import json
from flask import request
from . import main_service
from app.models import transaction
from .controller import Controller
    
@main_service.route('/', methods=["POST"])
@main_service.route('', methods=["POST"])
def index():
    return Controller.return_interface(transaction.Transaction(request.form))