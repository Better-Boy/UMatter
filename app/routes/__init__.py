from flask import Blueprint

main_service = Blueprint('index_service', __name__)

from . import index

