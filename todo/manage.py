import click
from flask.cli import with_appcontext


@click.command("init")
@with_appcontext
def init():
    """Create a new admin user"""
    from todo.extensions import db
    from todo.models import User

    user = User(username="admin", email="hosseynjf@icloud.com", password="admin")
    db.session.add(user)
    db.session.commit()
    click.echo("Created user 'admin'")
