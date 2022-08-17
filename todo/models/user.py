import typing
from typing import Any

from sqlalchemy.ext.hybrid import hybrid_property

from todo.extensions import db, pwd_context

if typing.TYPE_CHECKING:
    from todo.models import Project, ProjectMembershipList


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=False)

    memberships = db.relationship("ProjectMembership", back_populates="user")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = pwd_context.hash(value)

    def get_membership_for_project(self, project: 'Project') -> typing.Optional['ProjectMembershipList']:
        memberships = [m for m in project.memberships if m.user_id == self.id]
        if not memberships:
            return None
        return memberships[0]

    def __repr__(self):
        return "<User %s>" % self.username
