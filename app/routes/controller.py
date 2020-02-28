from .response.appreciation import Appreciation
from .response.help import Help
from .response.value import Value
from .response.user import User
from .response.top import Top
from .response.rewards import Rewards
from app import logger

class Controller:
        
    @classmethod
    def return_interface(self, data):
        logger.debug("In controller interface")
        if data.text.startswith("help"):
            return Help(data).response()
        elif data.text.startswith("me"):
            return User(data).response()
        elif data.text.startswith("value"):
            return Value(data).response()
        elif data.text.startswith("top"):
            return Top(data).response()
        elif data.text.startswith("rewards"):
            return Rewards(data).response()
        elif data.text.startswith("@"):
            return Appreciation(data).response()

        unkown = Help(data).help()
        return f"Unknown Option Chosen. Here's help \n{unkown}"