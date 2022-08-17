from todo.models import Task
from todo.extensions import ma, db


class TaskSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    class Meta:
        model = Task
        sqla_session = db.session
        load_instance = True
        include_relationships = True
        include_pk = True
