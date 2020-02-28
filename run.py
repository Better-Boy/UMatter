from app import app, logger
from waitress import serve

if __name__ == '__main__':
    logger.info("Starting the application")
    logger.debug("Application Configuration Options - %s", app.config)
    # app.run(host=app.config["APP_HOST"], port=app.config['APP_PORT'], debug=app.config['DEBUG'])
    serve(app, host=app.config["APP_HOST"], port=app.config['APP_PORT'])