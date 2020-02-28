import os, pymysql, logging, matplotlib, sys
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import app_config
from .utils.mattermostdriver import Driver

config_name = os.getenv('FLASK_CONFIG', 'development')

app = Flask(__name__)

# load the color list from the matplotlib
color_list = set()
for name, hex in matplotlib.colors.cnames.items():
    if name.startswith("light"): color_list.add(hex)

# inherit the configuration object from the config file
app.config.from_object(app_config[config_name])

app_config = app_config[config_name]

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler(app_config.LOG_FILE_PATH, maxBytes=10000000, backupCount=5)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

try:
	mysql = pymysql.connect(host=app_config.MYSQL_HOST,
							port=app_config.MYSQL_PORT,
							user=app_config.MYSQL_USER,
							password=app_config.MYSQL_PASSWORD,
							db=app_config.MYSQL_DB,
							cursorclass=pymysql.cursors.DictCursor)
except Exception as e:
	logger.critical("Not able to connect to MySQL Server. Can't proceed further. Shutting down gracefully", exc_info=True)
	sys.exit()

default_options = {
	'scheme': app_config.MM_SCHEME,
	'url': app_config.MM_URL,
	'port': app_config.MM_PORT,
	'basepath': '/api/v4',
	'verify': True,
	'timeout': 30,
	'request_timeout': None,
	'login_id': None,
	'password': None,
	'token': app_config.MM_BOT_TOKEN,
	'mfa_token': None,
	'auth': None,
	'debug': False
}

SLASH_TOKEN = app_config.MM_SLASH_TOKEN

mm_client = Driver(default_options)

try:
	mm_client.login()
except Exception as e:
	logger.critical("Not able to connect to MatterSQL Server. Can't proceed further. \
	Shutting down gracefully", exc_info=True)
	sys.exit()

DAILY_POINT_LIMIT = app_config.DAILY_POINT_LIMIT
PER_TRANSACTION_POINT_LIMIT = app_config.PER_TRANSACTION_POINT_LIMIT

INSERT_QUERY_STRING = "insert into transaction(channel_id, channel_name, from_user_id, from_user_name, points, to_user_id, to_user_name, post_id, insertionTime, message) values (\"%s\", \"%s\", \"%s\", \"%s\", %d, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
WEEKLY_THRESHOLD = app_config.WEEKLY_THRESHOLD

from .utils.helpers import *

# REGISTER BLUEPRINTS
from app.routes.index import main_service
app.register_blueprint(main_service, url_prefix='/v1/index')