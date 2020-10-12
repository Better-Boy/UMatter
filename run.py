from app import app, logger

if __name__ == '__main__':
    logger.info("Starting the application")
    logger.debug("Application Configuration Options - %s", app.config)
    app.run(host=app.config["APP_HOST"])