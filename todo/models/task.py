from todo.extensions import db


class Task(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    project_id = db.Column(db.BigInteger, db.ForeignKey("project.id"), nullable=False)

    project = db.relationship("Project", back_populates="tasks")
    assignees = db.relationship("User", secondary="task_assignment")

    def __repr__(self):
        return "<Task %s>" % self.title
