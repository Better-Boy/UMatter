from .base import Response
from app.utils import mm_wrapper
from flask import make_response
from app import select_feed_channel, generate_md_table, logger, WEEKLY_THRESHOLD
import re, datetime

REGEX_TOP_POINTS = re.compile(r"top peers ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])) ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")

class Top(Response):

    def __init__(self, data):
        self.transObj = data

    def check_format(self):
        logger.debug("Checking format for top peers")
        res_top = REGEX_TOP_POINTS.match(self.transObj.text)
        if self.transObj.text == "top points threshold": return True
        if res_top and res_top.span()[1] == len(self.transObj.text): return True
        return False

    @classmethod
    def help(self):
        help_str = "The format for getting top peers is as follows \n"  + \
                   "`/umatter top peers start_date end_date`\n" + \
                    "start_date and end_date to be in `yyyy-mm-dd` format. \n" + \
                    "For ex. `/umatter top peers 2020-02-12 2020-02-24`"
        return help_str

    def check_private_chat(self):
        logger.debug("Checking private chat for top peers")
        channel_type = mm_wrapper.get_channel_type(self.transObj.channel_id)
        if channel_type == "D":
            return True
        return False

    def response(self):
        if not self.check_format():
            logger.warning("Invalid format. Invalidating request")
            return "Invalid Format \n" + self.help()

        if self.check_private_chat():
            logger.warning("Request from a private chat. Invalidating request")
            return "> Please issue the command in private or public channels"
        split_text = self.transObj.text.split(" ")
        str_date2, str_date1 = split_text[-1], split_text[-2]
        date1 = datetime.datetime.strptime(str_date1, "%Y-%m-%d")
        date2 = datetime.datetime.strptime(str_date2, "%Y-%m-%d")
        if date1 >= date2:
            logger.warning("From Date greater than To Date")
            return "> To Date should be greater than From Date \n" + \
                   "For help, issue `/umatter help`"
        flag = False
        if (date2 - date1).days == 7:
            logger.debug("Date range of 7 days chosen")
            flag = True
            query = select_feed_channel(self.transObj.channel_id, date1, date2, is_week=True)
        else:
            query = select_feed_channel(self.transObj.channel_id, date1, date2)
        
        res_flag, res = self.transObj.execute_user_feed(query)
        if not res_flag:
            return "Internal Server Error. Please contact System admin"
            
        res_list = []
        for index, i in enumerate(res):
            if index == 0:
                res_list.append((":1st_place_medal:",i["to_user_name"], i["sum_total"]))
            elif index == 1:
                res_list.append((":2nd_place_medal:",i["to_user_name"], i["sum_total"]))
            elif index == 2:
                res_list.append((":3rd_place_medal:",i["to_user_name"], i["sum_total"]))
            elif flag:
                res_list.append((":star:",i["to_user_name"], i["sum_total"]))

        table = generate_md_table(res_list, ["Medal", "Peer Name", "Points Total"])
        if flag:
            text_msg = f"Top Peers Distribution for the channel **{self.transObj.channel_name}** who have cumulative sum of points greater than **{WEEKLY_THRESHOLD}** (weekly threshold), from **{str_date1}** to **{str_date2}** is as follows \n\n {table}"
        else:
            text_msg = f"Top Peers Distribution for the channel **{self.transObj.channel_name}** from **{str_date1}** to **{str_date2}** is as follows \n\n {table}"

        result = {
            "attachments":[{
                "text": text_msg
            }]
        }
        final_res = make_response(result)
        final_res.headers["Content-Type"] = "application/json"
        return final_res
