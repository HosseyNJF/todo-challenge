from marshmallow_enum import EnumField

from todo.extensions import ma, db
from todo.models import ProjectMembership


class ProjectMembershipSchema(ma.SQLAlchemyAutoSchema):
    role = EnumField(ProjectMembership.Role)

    class Meta:
        model = ProjectMembership
        sqla_session = db.session
        load_instance = True
        include_fk = True
        exclude = ('project_id',)
