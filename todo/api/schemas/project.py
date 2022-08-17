from todo.models import Project
from todo.extensions import ma, db


class ProjectSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)
    memberships = ma.Nested("ProjectMembershipSchema", many=True, dump_only=True)

    class Meta:
        model = Project
        sqla_session = db.session
        load_instance = True
