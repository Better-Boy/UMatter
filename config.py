import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    APP_NAME = "u-matter rest service"
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "root"
    MYSQL_DB = "umatter"
    MYSQL_PORT = 3306
    DAILY_POINT_LIMIT = 10

class ProductionConfig(BaseConfig):
    """
    Production configurations
    """
    PORT = 80
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    """
    Development configurations
    """
    TOKEN_ID = ""
    PORT = 5000
    DEBUG = True
    MYSQL_HOST = "127.0.0.1"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DB = "umatter"
    MYSQL_PORT = 3306
    DAILY_POINT_LIMIT = 10
    PER_TRANSACTION_POINT_LIMIT = 5

class TestingConfig(BaseConfig):
    """
    Testing configurations
    """


app_config = {  
    # 'default': ProductionConfig,  
    'default': DevelopmentConfig,  
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}