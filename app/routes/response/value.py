from .base import Response
from app import download_image
from app.utils import mm_wrapper
from flask import make_response
import re

REGEX_MESSAGE_PATTERN_ADD_VALUE = re.compile(r"value add \"[a-zA-Z0-9]*\" (http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png|jpeg)")

class Value(Response):

    def __init__(self, data):
        self.transObj = data

    def check_format(self):
        if not REGEX_MESSAGE_PATTERN_ADD_VALUE.match(self.transObj.text):
            return "Format incorrect for adding/listing company value. Ensure no special characters other than dot(.), dash(-), underscore(-) are in the value name. \n Follow example as follows: \n /umatter value add \"ownership\" <http image url with extension (jpg|gif|png|jpeg)"
        return None

    def add_value(self):
        com_group = re.search('"(.+?)"', self.transObj.text)
        com_value = None
        if com_group:
            com_value = com_group.group(1)
        if com_value == "":
            return "Company Value name cannot be None. Please re-enter the command with a company value"
        image_url = None
        image_url_group = re.search('http(.+?).(png|jpg|gif|jpeg)', self.transObj.text)
        if image_url_group:
            image_url = image_url_group.group(0)
        if image_url is None:
            return "Image Url can't be None"
        imageBytes = download_image(image_url)
        res, mes = mm_wrapper.create_custom_emoji(com_value.lower(), bytes(imageBytes))
        if res:
            value_add_res = {
                "response_type": "in_channel",
                "attachments": [{
                    "color": "#00FF00",
                    "title": "New Company Value [{}] Added successfully. You can start tagging the posts with the [{}] emoji\n".format(com_value, com_value),
                    "text": "\n\n",
                    "image_url": image_url
                }]
            }
            value_res = make_response(value_add_res)
            value_res.headers["Content-Type"] = "application/json"
            return value_res
        else:
            return mes

    # def list_value(self):
    #     res_status, value_list = mm_wrapper.get_list_of_custom_emoji()
    #     if not res_status:
    #         return value_list
    #     fields = []
    #     for i in value_list:
    #         fields.append({"short":True, "title":i["name"], "value":":{}:".format(i["name"])})
    #     res = {
    #         "attachments": [{
    #                 "title": "Here's the list of the company values that are added\n",
    #                 "color": "#00FF00",
    #                 "fields":fields
    #         }]
    #     }
    #     return res

    def response(self):
        mes = self.check_format()
        if mes:
            return mes
        first_split = self.transObj.text.split(" ", 1)
        if first_split[1].startswith("add"):
            return self.add_value()
        elif first_split[1].startswith("list"):
            return self.list_value()