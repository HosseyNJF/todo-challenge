from flask import request
from flask_jwt_extended import jwt_required, current_user
from flask_restful import Resource

from todo.api.schemas import TaskSchema
from todo.commons.pagination import paginate
from todo.extensions import db
from todo.models import Project, ProjectMembership, Task, User


def _check_project_access(project_id):
    project = Project.query.filter(Project.id == project_id).join(ProjectMembership).first()
    if not project or not current_user.get_membership_for_project(project):
        return False, project

    return True, project


class TaskResource(Resource):
    """Single task resource

    ---
    put:
      tags:
        - api
      summary: Update a task
      description: Update a single task by ID
      parameters:
        - in: path
          name: project_id
          schema:
            type: integer
        - in: path
          name: task_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              TaskSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  task: TaskSchema
        403:
          description: You do not have permission to edit this task
        404:
          description: Task does not exist
    delete:
      tags:
        - api
      summary: Delete a task
      description: Delete a single task by ID
      parameters:
        - in: path
          name: project_id
          schema:
            type: integer
        - in: path
          name: task_id
          schema:
            type: integer
      responses:
        204:
          description: Task successfully deleted
        403:
          description: You do not have permission to delete this task
        404:
          description: User does not exist
    """

    method_decorators = [jwt_required()]

    @staticmethod
    def _check_access_to_task(project_id, task_id):
        task = Task.query.filter(Task.id == task_id).join((User, Task.assignees)).first()

        if not task or task.project_id != project_id:
            return "This task doesn't belong to this project", None

        membership = current_user.get_membership_for_project(task.project)
        if membership.role != ProjectMembership.Role.MANAGER and current_user not in task.assignees:
            return "You don't have access to this task", None

        return None, task

    def put(self, project_id, task_id):
        error, task = self._check_access_to_task(project_id, task_id)

        if error:
            return {"msg": error}, 403

        schema = TaskSchema(partial=True)
        schema.load(request.json, instance=task)

        for user in task.assignees:
            if not user.get_membership_for_project(task.project):
                return {"msg": f"User {user.id} is not a member of this project"}

        db.session.commit()

        return {"task": schema.dump(task)}, 200

    def delete(self, project_id, task_id):
        error, task = self._check_access_to_task(project_id, task_id)

        if error:
            return {"msg": error}, 403

        db.session.delete(task)
        db.session.commit()

        return {}, 204


class TaskList(Resource):
    """List or create task

    ---
    get:
      tags:
        - api
      summary: Get a list of tasks
      description: Get a list of tasks for a project that the user have access to
      parameters:
        - in: path
          name: project_id
          schema:
            type: integer
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
                          $ref: '#/components/schemas/TaskSchema'
        403:
          description: You don't have access to this endpoint
    post:
      tags:
        - api
      summary: Create a task
      description: Creates a new task in the specified project
      parameters:
        - in: path
          name: project_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              TaskSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  task: TaskSchema
        403:
          description: You don't have access to this endpoint
    """

    method_decorators = [jwt_required()]

    def get(self, project_id):
        authorized, project = _check_project_access(project_id)

        if not authorized:
            return {"msg": "You do not have access to this project"}, 403

        schema = TaskSchema(many=True)

        query = Task.query.filter(Task.project == project)

        return paginate(query, schema)

    def post(self, project_id):
        authorized, project = _check_project_access(project_id)

        if not authorized:
            return {"msg": "You do not have access to this project"}, 403

        schema = TaskSchema()

        task = schema.load(request.json)

        for user in task.assignees:
            if not user.get_membership_for_project(project):
                return {"msg": f"User {user.id} is not a member of this project"}

        task.project = project
        task.assignees.append(current_user)

        db.session.add(task)
        db.session.commit()

        return {"task": schema.dump(task)}


class MyselfTaskList(Resource):
    """List tasks for myself

    ---
    get:
      tags:
        - api
      summary: Get a list of personal tasks
      description: Get a list of tasks assigned to the current user for a project
      parameters:
        - in: path
          name: project_id
          schema:
            type: integer
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
                          $ref: '#/components/schemas/TaskSchema'
        403:
          description: You don't have access to this endpoint
    """

    method_decorators = [jwt_required()]

    def get(self, project_id):
        authorized, project = _check_project_access(project_id)

        if not authorized:
            return {"msg": "You do not have access to this project"}, 403

        schema = TaskSchema(many=True)

        query = Task.query.filter(Task.project == project, Task.assignees.any(id=current_user.id))

        return paginate(query, schema)
