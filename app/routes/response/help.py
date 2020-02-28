from .base import Response
from app import logger
from .appreciation import Appreciation
from .top import Top
from .user import User
from .value import Value

REGEX_MESSAGE_PATTERN = "help"

class Help(Response):

    def __init__(self, data):
        self.transObj = data
    
    def help(self):
        help_str =  "Welcome to umatter. Here's the list of available slash commands.\n"
        help_str += "**Giving Appreciation** \n" + Appreciation.help() + "\n"
        help_str += "**Top Peers in the channel** \n" + Top.help() + "\n"
        help_str += "**Statistics about yourself** \n" + User.help() + "\n\n"
        help_str += "**Adding a company value** \n" + Value.help() + "\n"
        return help_str

    def check_format(self):
        logger.debug("checking format for help")
        if self.transObj.text.strip() != REGEX_MESSAGE_PATTERN:
            return False
        return True

    def response(self):
        if not self.check_format():
            logger.warning("Format incorrect for help")
            return "Format incorrect for help. \n Example - /umatter help"
        return self.help()