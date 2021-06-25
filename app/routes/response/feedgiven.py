from os import write
from .base import Response
from app.utils import mm_wrapper
from flask import make_response
from app import select_feed_given, logger, WEEKLY_THRESHOLD
import re, datetime
import csv

REGEX_TOP_POINTS = re.compile(r"given all ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])) ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")

class FeedGiven(Response):

    def __init__(self, data):
        self.transObj = data

    def check_format(self):
        logger.debug("Checking format for given all")
        res_top = REGEX_TOP_POINTS.match(self.transObj.text)
        if self.transObj.text == "top points threshold": return True
        if res_top and res_top.span()[1] == len(self.transObj.text): return True
        return False

    @classmethod
    def help(self):
        help_str = "The format for getting given appreciation is as follows \n"  + \
                   "`/umatter given all start_date end_date`\n" + \
                    "start_date and end_date to be in `yyyy-mm-dd` format. \n" + \
                    "For ex. `/umatter given all 2020-02-12 2020-02-24`"
        return help_str

    def response(self):
        if not self.check_format():
            logger.warning("Invalid format. Invalidating request")
            return "Invalid Format \n" + self.help()

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
            query = select_feed_given(date1, date2, is_week=True)
        else:
            query = select_feed_given(date1, date2)
        
        res_flag, res = self.transObj.execute_user_feed(query)
        if not res_flag:
            return "Internal Server Error. Please contact System admin"
            
        res_list = []
        csv_res_list = []
        for index, i in enumerate(res):
            if index == 0:
                res_list.append((":1st_place_medal:",i["from_user_name"], i["sum_total"], i["given_count"]))
            elif index == 1:
                res_list.append((":2nd_place_medal:",i["from_user_name"], i["sum_total"], i["given_count"]))
            elif index == 2:
                res_list.append((":3rd_place_medal:",i["from_user_name"], i["sum_total"], i["given_count"]))
            elif flag:
                res_list.append((":star:",i["from_user_name"], i["sum_total"], i["given_count"]))

            csv_res_list.append([index + 1, i["from_user_name"], i["sum_total"], i["given_count"]])
        
        file_name = f'/tmp/PostsGivenData_{str_date1}_{str_date2}.csv'
        with open(file_name, 'w') as csv_file:
            fieldnames = ['Username', 'Total Points Given', 'Number of Posts Given']
            writer = csv.writer(csv_file)
            writer.writerow(fieldnames)
            writer.writerows(csv_res_list)

        if flag:
            text_msg = f"Data consisting of number of posts given by people for **{WEEKLY_THRESHOLD}** (weekly threshold), from **{str_date1}** to **{str_date2}** is:"
        else:
            text_msg = f"Data consisting of number of posts given by people, from **{str_date1}** to **{str_date2}** is:"

        flag, file_id = mm_wrapper.upload_csv(self.transObj.channel_id, file_name)
        flag, _, _ = mm_wrapper.create_post(text_msg, file_id, self.transObj.channel_id)

        return ""