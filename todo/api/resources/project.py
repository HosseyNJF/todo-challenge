from flask import request
from flask_jwt_extended import jwt_required, current_user
from flask_restful import Resource

from todo.api.schemas import ProjectSchema, ProjectMembershipSchema
from todo.commons.pagination import paginate
from todo.extensions import db
from todo.models import Project, ProjectMembership, User


def _check_project_manager_access(project_id):
    project = Project.query.filter(Project.id == project_id).join(ProjectMembership).first()
    if (
            not project
            or not (m := current_user.get_membership_for_project(project))
            or m.role != ProjectMembership.Role.MANAGER
    ):
        return False, project

    return True, project


class ProjectMembershipResource(Resource):
    """Single membership resource

    ---
    delete:
      tags:
        - api
      summary: Remove a user
      description: Remove a single user from the project by ID
      parameters:
        - in: path
          name: project_id
          schema:
            type: integer
        - in: path
          name: user_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: User removed from project
        404:
          description: User is not a member in the project
    """

    method_decorators = [jwt_required()]

    def delete(self, project_id, user_id):
        authorized, project = _check_project_manager_access(project_id)

        if not authorized:
            return {"msg": "You do not have access to change this project's memberships"}, 403

        membership = ProjectMembership.query.filter(
            ProjectMembership.project_id == project_id,
            ProjectMembership.user_id == user_id,
        ).first()

        if not membership:
            return {"msg": "The specified user is not a member of this project"}

        db.session.delete(membership)
        db.session.commit()

        return {"msg": "User removed from project"}


class ProjectMembershipList(Resource):
    """Manage memberships

    ---
    post:
      tags:
        - api
      summary: Create a membership
      description: Create a membership, which adds a user to this project
      parameters:
        - in: path
          name: project_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              ProjectMembershipSchema
      responses:
        200:
          description: User added successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  membership: ProjectMembershipSchema
        400:
          description: The specified user is already a member of this project
        403:
          description: You don't have access to this endpoint
        404:
          description: User does not exist
    """

    method_decorators = [jwt_required()]

    def post(self, project_id):
        authorized, project = _check_project_manager_access(project_id)

        if not authorized:
            return {"msg": "You do not have access to change this project's memberships"}, 403

        schema = ProjectMembershipSchema()
        membership = schema.load(request.json)

        user = User.query.filter(User.id == membership.user_id).first()

        if not user:
            return {"msg": "The specified user does not exist"}, 404

        if user.get_membership_for_project(project):
            return {"msg": "The specified user is already a member of this project"}, 400

        membership.project = project

        db.session.add(membership)
        db.session.commit()

        return {"membership": schema.dump(membership)}


class ProjectList(Resource):
    """List or create project

    ---
    get:
      tags:
        - api
      summary: Get a list of projects
      description: Get a list of projects that the user have access to
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/ProjectSchema'
    post:
      tags:
        - api
      summary: Create a project
      description: Creates a new project and adds you as a manager
      requestBody:
        content:
          application/json:
            schema:
              ProjectSchema
      responses:
        200:
          content:
            application/json:
              schema:
                ProjectSchema
    """

    method_decorators = [jwt_required()]

    def get(self):
        schema = ProjectSchema(many=True)

        query = Project.query.filter(Project.memberships.any(user=current_user))

        return paginate(query, schema)

    def post(self):
        schema = ProjectSchema()

        project = schema.load(request.json)
        membership = ProjectMembership(
            role=ProjectMembership.Role.MANAGER,
            user=current_user,
        )

        db.session.add(project)
        project.memberships.append(membership)
        db.session.commit()

        return {"project": schema.dump(project)}
