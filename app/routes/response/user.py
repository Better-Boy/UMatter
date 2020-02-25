from .base import Response
from app import select_feed_user_query, make_plot, generate_md_table, select_feed_user_timebound
from app.utils import mm_wrapper
import re, datetime
from flask import make_response
from collections import defaultdict

REGEX_MESSAGE_PATTERN_FEED = re.compile(r"me feed \"[a-zA-Z0-9!\"#$%&\'\(\)\*\+,-./:;<=>?@\[\]\^_`{|}~ ]*\"")
REGEX_MESSAGE_PATTERN_POINTS = re.compile(r"me points ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])) ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")

class User(Response):

    def __init__(self, data):
        self.transObj = data
    
    def check_format(self):
        if self.transObj.text == "me stats":
            return True
        res_feed = REGEX_MESSAGE_PATTERN_FEED.match(self.transObj.text)
        if res_feed and res_feed.span()[1] == len(self.transObj.text): return True
        res_points = REGEX_MESSAGE_PATTERN_POINTS.match(self.transObj.text)
        if res_points and res_points.span()[1] == len(self.transObj.text): return True
        return False

    def user_stats(self):
        query = select_feed_user_query(self.transObj.from_user_id)
        res = self.transObj.execute_user_feed(query)
        total_points_rvd = 0
        total_points_gvn = 0
        appr_posts_from_count = 0
        appr_posts_to_count = 0
        channel_points = defaultdict(int)
        post_id_list = []
        total_appr_post_count = len(res)
        for i in res:
            channel_points[i["channel_name"]]+=1
            if i["from_user_name"] == self.transObj.from_user_name:
                appr_posts_from_count += 1
                total_points_gvn += i["points"]
            if i["to_user_name"] == self.transObj.from_user_name:
                appr_posts_to_count += 1
                total_points_rvd += i["points"]
            post_id_list.append(i["post_id"])

        mm_status, mm_res = mm_wrapper.get_reaction_bulk(post_id_list)
        if not mm_status:
            return mm_res
        
        emoji_dist = defaultdict(int)
        for k,v in mm_res.items():
            for i in v:
                k = i["emoji_name"]
                emoji_dist[f":{k}: {k}"] += 1
        
        # cp_plot_byte = make_plot(list(channel_points.keys()), list(channel_points.values()), "Points Channel Distribution")
        # file_id_channel = mm_wrapper.upload_file(self.transObj.channel_id, cp_plot_byte)
        # ed_plot_byte = make_plot(list(emoji_dist.keys()), list(emoji_dist.values()), "Emoji Count Distribution")
        # file_id_emoji = mm_wrapper.upload_file(self.transObj.channel_id, ed_plot_byte)

        cp_table = generate_md_table(channel_points.items(), ["Channel Name", "Points"])
        ed_table = generate_md_table(emoji_dist.items(), ["Emoji Name", "Frequency Tagged"])
        res = {
            "attachments":[{
                "text": f"### **Channel Points** \n\n {cp_table} \n\n ### **Emoji Distribution** \n\n {ed_table}",
                "fields":[{
                    "short":True,
                    "title":"User Name",
                    "value": self.transObj.from_user_name
                },{
                    "short":True,
                    "title":"Total Appreciation Posts",
                    "value": str(total_appr_post_count)
                },
                {
                    "short":True,
                    "title":"Total Points Received from Peers",
                    "value": str(total_points_rvd)
                },{
                    "short":True,
                    "title":"Total Points Given to Peers",
                    "value": str(total_points_gvn)
                },{
                    "short":True,
                    "title":"Total Appreciation by you",
                    "value": str(appr_posts_from_count)
                },{
                    "short":True,
                    "title":"Total Appreciation to you",
                    "value": str(appr_posts_to_count)
                }]
            }]
        }
        final_res = make_response(res)
        final_res.headers["Content-Type"] = "application/json"
        return final_res

    def user_feed(self):
        channel_name_grp = re.search('"(.+?)"', self.transObj.text)
        channel_name = None
        if channel_name_grp:
            channel_name = channel_name_grp.group(1)
        query = select_feed_user_query(self.transObj.from_user_id, channel_name, 10, True)
        res = self.transObj.execute_user_feed(query)
        res_list = []
        for i in res:
            res_list.append((i["from_user_name"], i["to_user_name"], i["points"], i["channel_name"], i["message"]))
        table = generate_md_table(res_list, ["From User", "To User", "Points", "Channel Name", "Appreciation Message"])
        result = {
            "attachments":[{
                "text": f"Your latest appreciation feed for the channel **{self.transObj.channel_name}** \n\n\n {table}"
            }]
        }
        final_res = make_response(result)
        final_res.headers["Content-Type"] = "application/json"
        return final_res

    def user_points(self):
        split_text = self.transObj.text.split(" ")
        str_date2, str_date1 = split_text[-1], split_text[-2]
        date1 = datetime.datetime.strptime(str_date1, "%Y-%m-%d")
        date2 = datetime.datetime.strptime(str_date2, "%Y-%m-%d")
        if date1 >= date2:
            return "To Date should be greater than From Date"
        query = select_feed_user_timebound(self.transObj.from_user_id, date1, date2)
        res = self.transObj.execute_user_feed(query)
        res_list = []
        for i in res:
            res_list.append((i["channel_name"], i["points"], i["from_user_name"], i["insertionTime"]))
        table = generate_md_table(res_list, ["Channel Name", "Points", "From Peer", "Timestamp"])
        result = {
            "attachments":[{
                "text": f"Your Points Distribution from {date1} to {date2} is as follows \n\n {table}"
            }]
        }
        final_res = make_response(result)
        final_res.headers["Content-Type"] = "application/json"
        return final_res

    def response(self):
        if not self.check_format(): 
            return "Format Incorrect for viewing about yourself. Follow the examples below: \n *hello*"
        first_split = self.transObj.text.split(" ")
        if first_split[1] == "stats":
            return self.user_stats()

        if first_split[1] == "feed":
            return self.user_feed()

        if first_split[1] == "points":
            return self.user_points()