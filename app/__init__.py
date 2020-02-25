from flask import Flask
import logging
import pymysql
import os
import matplotlib
from config import app_config
from .utils.mattermostdriver import Driver

config_name = os.getenv('FLASK_CONFIG', 'default')

app = Flask(__name__)

color_list = set()
for name, hex in matplotlib.colors.cnames.items():
    if name.startswith("light"): color_list.add(hex)

app.config.from_object(app_config[config_name])
mysql = pymysql.connect(host=app_config[config_name].MYSQL_HOST,
						port=app_config[config_name].MYSQL_PORT,
                        user=app_config[config_name].MYSQL_USER,
                        password=app_config[config_name].MYSQL_PASSWORD,
                        db=app_config[config_name].MYSQL_DB,
                        cursorclass=pymysql.cursors.DictCursor)

default_options = {
	'scheme': 'http',
	'url': 'localhost',
	'port': 8065,
	'basepath': '/api/v4',
	'verify': True,
	'timeout': 30,
	'request_timeout': None,
	'login_id': None,
	'password': None,
	'token': "itreywtggb8ityz9dft1rz4k7r",
	'mfa_token': None,
	'auth': None,
	'debug': False
}

mm_client = Driver(default_options)
mm_client.login()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DAILY_POINT_LIMIT = app_config[config_name].DAILY_POINT_LIMIT
PER_TRANSACTION_POINT_LIMIT = app_config[config_name].PER_TRANSACTION_POINT_LIMIT

INSERT_QUERY_STRING = "insert into transaction(channel_id, channel_name, from_user_id, from_user_name, points, to_user_id, to_user_name, post_id, insertionTime, message) values (\"%s\", \"%s\", \"%s\", \"%s\", %d, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
WEEKLY_THRESHOLD = 5

from .utils.helpers import *

# REGISTER BLUEPRINTS
from app.routes.index import main_service
app.register_blueprint(main_service, url_prefix='/v1/index')