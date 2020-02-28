from flask import request
from . import main_service
from app.models import transaction
from app import SLASH_TOKEN, logger
from .controller import Controller

def check_token(token):
    logger.info("Authenticating Token")
    if token.split(" ")[1] == SLASH_TOKEN:
        return True
    return False

@main_service.route('/', methods=["POST"])
@main_service.route('', methods=["POST"])
def index():
    if not check_token(request.headers["Authorization"]):
        logger.error("Token Authentication Failed")
        return "Request Token Invalid. Please check the token wrt Slash Command Or Contact your System Admin"
    logger.debug("Incoming message data - %s", request.form)
    return Controller.return_interface(transaction.Transaction(request.form))