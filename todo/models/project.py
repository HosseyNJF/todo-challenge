from todo.extensions import db


class Project(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    tasks = db.relationship("Task", back_populates="project")
    memberships = db.relationship("ProjectMembership", back_populates="project")

    def __repr__(self):
        return "<Project %s>" % self.name
