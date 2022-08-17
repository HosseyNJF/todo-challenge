from todo.extensions import db


task_assignment = db.Table(
    "task_assignment",
    db.Model.metadata,
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("task_id", db.ForeignKey("task.id"), primary_key=True),
)
