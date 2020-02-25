from app.models import transaction
from app import generate_blob, DAILY_POINT_LIMIT, PER_TRANSACTION_POINT_LIMIT
from app.utils import mm_wrapper
from .base import Response
import re

REGEX_MESSAGE_PATTERN = re.compile(r"^@[a-zA-Z0-9_.-]* ([0-9]{1,2})?\+\+ ?.*")

class Appreciation(Response):

    def __init__(self, data):
        self.transObj = data

    def check_self_appr(self, to_user_name):
        if self.transObj.from_user_name == to_user_name:
            return True
        return False

    def check_private_chat(self):
        channel_type = mm_wrapper.get_channel_type(self.transObj.channel_id)
        if channel_type == "D":
            return True
        return False

    def check_format(self):
        if REGEX_MESSAGE_PATTERN.match(self.transObj.text):
            return True
        return False

    def response(self):
        if not self.check_format():
            return "Please write the appreciation in a correct format. \n Example - /umatter @userm 5++ fast delivery of project"

        if self.check_private_chat():
            return "Please give the appreciation in a public/private channel"
        
        first_split = self.transObj.text.strip().split(" ", 1)
        to_user_name = first_split[0].strip()[1:]

        if self.check_self_appr(to_user_name):
            return "Can't give points to yourself"
        
        to_user_id = mm_wrapper.get_user_id(to_user_name)
        second_split = first_split[1].strip().split(" ", 1)
        points = second_split[0]
        if len(second_split) == 2: message = second_split[1]
        else: message = ""
        if points == "++": points = 1
        else: points = int(points.replace("++", ""))
        if points > 5:
            return "You can give max {} points at a time".format(5)

        curr_points = self.transObj.execute_select_check_sum("select sum(points) as day_total from transaction where from_user_id=\""+self.transObj.from_user_id + "\" and date(insertionTime)=CURDATE();")
        if curr_points is None: curr_points = 0
        if curr_points + points > DAILY_POINT_LIMIT:
            return "Sorry!! You have exceeded your quota of points for today. Your Remaining points for today- {}".format(DAILY_POINT_LIMIT - curr_points)
        
        appr_post = generate_blob(f"{to_user_name} awarded {points} points")
        file_id = mm_wrapper.upload_file(self.transObj.channel_id, appr_post)
        post_id, ts_created = mm_wrapper.create_post(f"@{to_user_name} awarded {points} points by @{self.transObj.from_user_name} \n {'**Message**: '+message if message else ''}", file_id, self.transObj.channel_id)
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
        self.transObj.insert(query_data)
        return ""