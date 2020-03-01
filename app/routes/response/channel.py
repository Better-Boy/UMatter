from .base import Response
from app import logger, select_feed_channel_stats, make_plot
from app.utils import mm_wrapper
from flask import make_response
import re, datetime
from collections import defaultdict

REGEX_CHANNEL_STATS = re.compile(r"channel stats ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])) ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")

class Channel(Response):

    def __init__(self, data):
        self.transObj = data

    def check_format(self):
        logger.debug("Checking format for top peers")
        res_stats = REGEX_CHANNEL_STATS.match(self.transObj.text)
        if res_stats and res_stats.span()[1] == len(self.transObj.text): return True
        return False

    @classmethod
    def help(self):
        help_str = "The format for getting channel statistics is as follows \n"  + \
                   "`/umatter channel stats start_date end_date`\n" + \
                    "start_date and end_date to be in `yyyy-mm-dd` format. \n" + \
                    "For ex. `/umatter channel stats 2020-02-12 2020-02-24`"
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
        
        query = select_feed_channel_stats(self.transObj.channel_id, date1, date2)

        flag, res = self.transObj.execute_user_feed(query)

        if not flag:
            return "Internal Server Error. Please contact System admin"

        post_id_list = [i["post_id"] for i in res]

        mm_status, mm_res = mm_wrapper.get_reaction_bulk(post_id_list)

        if not mm_status:
            return "Internal Server Error has been detected. Please contact system admin"
        
        emoji_dist = defaultdict(int)
        
        for k,v in mm_res.items():
            for i in v:
                k = i["emoji_name"]
                emoji_dist[f":{k}: {k}"] += 1

        message = f"Channel Statistics from **{str_date1}** to **{str_date2}** for the channel **{self.transObj.channel_name}** \n "
        message += f"Total Appreciation Post Count - {len(res)}\n"

        if emoji_dist:
            ed_plot_byte = make_plot(list(emoji_dist.keys()), list(emoji_dist.values()), "Emoji Count Distribution")
            flag, file_id_emoji = mm_wrapper.upload_file(self.transObj.channel_id, ed_plot_byte)
            if not flag:
                return "Looks like there is a server problem. Please contact system admin. Sorry for the inconvience"
        else:
            file_id_emoji = ""
            message += "No emojis are tagged to the appreciation posts. Please start tagging emojis to the appreciation posts"
        
        flag, _, _ = mm_wrapper.create_post(message, file_id_emoji, self.transObj.channel_id)

        if not flag:
            return "Looks like there is a server problem. Please contact system admin. Sorry for the inconvience"
        
        return ""
