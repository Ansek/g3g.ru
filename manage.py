#!/usr/bin/env python
from flask.cli import FlaskGroup
from flask_migrate import Migrate

from app import create_app
from app.database import db

app = create_app()
cli = FlaskGroup(app)
migrate = Migrate()
migrate.init_app(app, db)

if __name__ == '__main__':
    cli()