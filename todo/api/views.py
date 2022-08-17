from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError

from todo.extensions import apispec
from todo.api.resources import ProjectList, ProjectMembershipList, ProjectMembershipResource, TaskList, MyselfTaskList, TaskResource
from todo.api.schemas import TaskSchema, ProjectSchema, ProjectMembershipSchema

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)

api.add_resource(ProjectList, "/projects", endpoint="projects")
api.add_resource(ProjectMembershipList, "/projects/<int:project_id>/memberships", endpoint="project_memberships")
api.add_resource(ProjectMembershipResource, "/projects/<int:project_id>/memberships/<int:user_id>", endpoint="project_user_membership")
api.add_resource(TaskList, "/projects/<int:project_id>/tasks", endpoint="tasks_for_project")
api.add_resource(MyselfTaskList, "/projects/<int:project_id>/tasks/myself", endpoint="myself_tasks_for_project")
api.add_resource(TaskResource, "/projects/<int:project_id>/tasks/<int:task_id>", endpoint="task_resource")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("TaskSchema", schema=TaskSchema)
    apispec.spec.components.schema("ProjectSchema", schema=ProjectSchema)
    apispec.spec.components.schema("ProjectMembershipSchema", schema=ProjectMembershipSchema)
    apispec.spec.path(view=ProjectList, app=current_app)
    apispec.spec.path(view=ProjectMembershipList, app=current_app)
    apispec.spec.path(view=ProjectMembershipResource, app=current_app)
    apispec.spec.path(view=TaskList, app=current_app)
    apispec.spec.path(view=MyselfTaskList, app=current_app)
    apispec.spec.path(view=TaskResource, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
