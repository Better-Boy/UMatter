from .base import Response

REGEX_MESSAGE_PATTERN = "help"

class Help(Response):

    def __init__(self, data):
        self.transObj = data

    def check_format(self):
        if self.transObj.text.strip() != REGEX_MESSAGE_PATTERN:
            return False
        return True

    def response(self):
        if not self.check_format():
            return "Format incorrect for help. \n Example - /umatter help"
        return "HELP STRING TO BE HERE"