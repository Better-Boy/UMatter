from app.models import transaction
from app import generate_blob, DAILY_POINT_LIMIT, PER_TRANSACTION_POINT_LIMIT, logger
from app.utils import mm_wrapper
from .base import Response
import re

REGEX_MESSAGE_PATTERN = re.compile(r"^@[a-zA-Z0-9_.-]* ([0-9]{1,2})?\+\+ ?.*")

class Appreciation(Response):

    def __init__(self, data):
        self.transObj = data

    def check_self_appr(self, to_user_name):
        logger.debug("Checking for self appreciation")
        if self.transObj.from_user_name == to_user_name:
            return True
        return False

    def check_private_chat(self):
        logger.debug("Checking if the request is from private chat")
        channel_type = mm_wrapper.get_channel_type(self.transObj.channel_id)
        if channel_type == "D":
            return True
        return False

    @classmethod
    def help(self):
        help_str = "In order to appreciate your peer, please follow the following format \n\n" + \
                   "1. `/umatter @username ++ for helping me out` ---> one point appreciation \n" + \
                   "2. `/umatter @username 3++ for writing the test suite` ---> more points appreciation"
        return help_str

    def check_format(self):
        logger.debug("In checking format for appreciation")
        if REGEX_MESSAGE_PATTERN.match(self.transObj.text):
            return True
        return False

    def response(self):
        if not self.check_format():
            logger.info("Slash command format not proper. Invalidating request and sending in help")
            return self.help()

        if self.check_private_chat():
            logger.info("Private Chat/Channel detected. Invalidating request")
            return "> Please give the appreciation in a public/private channel"
        
        first_split = self.transObj.text.strip().split(" ", 1)
        to_user_name = first_split[0].strip()[1:]

        if self.check_self_appr(to_user_name):
            logger.info("Self Appreciation Detected. Invalidating request")
            return "> Can't give points to yourself"
        
        flag, to_user_id = mm_wrapper.get_user_id(to_user_name)
        
        if not flag:
            return "Thank you for the appreciation. Unfortunately, it looks like the user is not existing in the system. Please contact system admin"

        second_split = first_split[1].strip().split(" ", 1)
        points = second_split[0]
        if len(second_split) == 2: message = second_split[1]
        else: message = ""

        if points == "++": points = 1
        else: points = int(points.replace("++", ""))

        if points > PER_TRANSACTION_POINT_LIMIT:
            logger.info("More than %s points given. Invalidating request", PER_TRANSACTION_POINT_LIMIT)
            return "You can give max {} points at a time".format(PER_TRANSACTION_POINT_LIMIT)

        flag, curr_points = self.transObj.execute_select_check_sum("select sum(points) as day_total from transaction where from_user_id=\""+self.transObj.from_user_id + "\" and date(insertionTime)=CURDATE();")

        if not flag:
            return "Problem in the application server. Please contact system admin"

        if curr_points is None: curr_points = 0
        if curr_points + points > DAILY_POINT_LIMIT:
            logger.info("Daily Limit of %s crossed", DAILY_POINT_LIMIT)
            return "Sorry!! You have exceeded your quota of points for today. Your Remaining points for today - {}".format(DAILY_POINT_LIMIT - curr_points)
        
        appr_post = generate_blob(f"{to_user_name} awarded {points} points")

        flag, file_id = mm_wrapper.upload_file(self.transObj.channel_id, appr_post)
        if not flag:
            return "Looks like there is a server problem. Please contact system admin. Sorry for the inconvience"
        
        flag, post_id, ts_created = mm_wrapper.create_post(f"@{to_user_name} awarded {points} points by @{self.transObj.from_user_name} \n {'**Message**: '+message if message else ''}", file_id, self.transObj.channel_id)

        if not flag:
            return "Looks like there is a server problem. Please contact system admin. Sorry for the inconvience"
        
        query_data = {
            "channel_id": self.transObj.channel_id,
            "channel_name": self.transObj.channel_name,
            "from_user_id": self.transObj.from_user_id,
            "from_user_name": self.transObj.from_user_name,
            "points": points,
            "to_user_id": to_user_id,
            "to_user_name": to_user_name,
            "post_id": post_id,
            "insertionTime": ts_created,
            "user_id": self.transObj.from_user_id,
            "message": message
        }
        flag = self.transObj.insert(query_data)

        if not flag:
            return "Looks like there is a server problem. Please contact system admin. Sorry for the inconvience"
        return ""