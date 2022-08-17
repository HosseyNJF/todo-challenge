import enum

from todo.extensions import db


class ProjectMembership(db.Model):
    class Role(enum.Enum):
        DEVELOPER = enum.auto()
        MANAGER = enum.auto()

    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    project_id = db.Column(db.ForeignKey("project.id"), primary_key=True)
    role = db.Column(db.Enum(Role), nullable=False)

    project = db.relationship("Project", back_populates="memberships")
    user = db.relationship("User", back_populates="memberships")
