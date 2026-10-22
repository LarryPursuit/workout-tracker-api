from flask import Flask

from config import Config
from errors import register_error_handlers
from extensions import db, migrate
from routes import register_blueprints


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.sort_keys = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Importing the package registers every model on db.metadata for migrations.
    import models  # noqa: F401

    register_blueprints(app)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
