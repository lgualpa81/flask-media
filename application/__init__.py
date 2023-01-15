from flask import Flask, make_response, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
import os, time

db = SQLAlchemy()

def register_handler_exceptions(app):
    @app.before_request
    def start_timer():            
        g.start = time.time()
        

    @app.errorhandler(404)
    def page_not_found(error):
        message = [str(x) for x in error.args]
        return make_response(jsonify({'code': 404, 'message': "Ups not found!!"}), 404)

    @app.errorhandler(405)
    def method_not_allowed(error):
        message = [str(x) for x in error.args]
        return make_response(jsonify({'code': 405, 'message': "Method not allowed"}), 405)
'''
    @app.errorhandler(500)
    def server_error(e):
        message = [str(x) for x in e.args]
        app.logger.error(message)
        return make_response(jsonify({'code': 500, 'message': "An internal error occurred. " + str(e.code)}), 500)

    @app.errorhandler(Exception)
    def exceptions(e):
        """ Logging after every Exception. """
        message = [str(x) for x in e.args]
        
        return make_response(
            jsonify({'code': 500, 'message': "An internal error occurred."}), 500)
'''

def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        # Create a directory in a known location to save files to.
        for folder in ['audio', 'video', 'image']:
            path_folder = os.path.join(app.root_path, 'static', folder)
            os.makedirs(path_folder, 0o777, True)                

        register_handler_exceptions(app)

        from . import routes  # Import routes

        return app
