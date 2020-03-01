import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    # Flask Settings
    APP_NAME = "u-matter rest service"
    APP_PORT = 5000
    APP_HOST = "0.0.0.0"
    DEBUG = True

    # Mysql Settings 
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DB = ""
    MYSQL_PORT = 3306

    # Mattermost settings
    DAILY_POINT_LIMIT = 10
    PER_TRANSACTION_POINT_LIMIT = 5
    WEEKLY_THRESHOLD = 40
    MM_SCHEME = "http"
    MM_URL = "localhost"
    MM_PORT = 8065
    MM_BOT_TOKEN = ""
    MM_SLASH_TOKEN = ""

    # LOG FILE PATH
    LOG_FILE_PATH = "event_logs.log"

class ProductionConfig(BaseConfig):
    """
    Production configurations
    """
    APP_PORT = 5000
    APP_HOST = "0.0.0.0"
    DEBUG = False

    MYSQL_HOST = "db"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "root"
    MYSQL_DB = "umatter"
    MYSQL_PORT = 3306
    
    MM_SCHEME = "http"
    MM_URL = "host.docker.internal"
    MM_PORT = 8065
    MM_BOT_TOKEN = "wwgqj7p89t8zbqwsmd6nfg4srw"
    MM_SLASH_TOKEN = "aax8t67esirpjmegijtqx1puae"
    WEEKLY_THRESHOLD = 40

class DevelopmentConfig(BaseConfig):
    """
    Development configurations
    """
    APP_PORT = 5000
    DEBUG = True

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "root"
    MYSQL_DB = "umatter"
    MYSQL_PORT = 3306
    
    MM_SCHEME = "http"
    MM_URL = "localhost"
    MM_PORT = 8065
    MM_BOT_TOKEN = "wwgqj7p89t8zbqwsmd6nfg4srw"
    MM_SLASH_TOKEN = "aax8t67esirpjmegijtqx1puae"
    WEEKLY_THRESHOLD = 5

class TestingConfig(BaseConfig):
    """
    Testing configurations
    """


app_config = {  
    'default': ProductionConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}