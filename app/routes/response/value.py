from .base import Response
from app import logger, download_image
from app.utils import mm_wrapper
from flask import make_response
import re

REGEX_MESSAGE_PATTERN_ADD_VALUE = re.compile(r"value add \"[a-zA-Z0-9]*\" (http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png|jpeg)")

class Value(Response):

    def __init__(self, data):
        self.transObj = data

    def check_format(self):
        logger.debug("Checking format for value")
        if REGEX_MESSAGE_PATTERN_ADD_VALUE.match(self.transObj.text):
            return True
        return False

    @classmethod
    def help(self):
        help_str = "Format for adding a value is as follows\n" + \
                   "`/umatter value add \"value_name\" <image_url>`\n" + \
                       "Ensure no special characters other than dot(.), dash(-), underscore(-) are in the value name. Supported image urls should end in png, jpg, jpeg, gif.\n" + \
                           "For ex. `/umatter value add \"consistency\" http://<image_url>.png`"
        return help_str
    
    def add_value(self):
        logger.debug("In value addition")
        com_group = re.search('"(.+?)"', self.transObj.text)
        com_value = None
        if com_group:
            com_value = com_group.group(1)
        if com_value == "":
            logger.warning("No value name given. Invalidating request")
            return "Value name cannot be None. Please re-enter the command with a value name"

        image_url = None
        image_url_group = re.search('http(.+?).(png|jpg|gif|jpeg)', self.transObj.text)

        if image_url_group:
            image_url = image_url_group.group(0)

        if image_url is None:
            logger.warning("No image url given. Invalidating request")
            return "Image Url can't be None. Please re-enter the command with an image Url"

        flag, image_bytes = download_image(image_url)
        if not flag:
            logger.warning("Not able to download the image url")
            return "Not able to download the image. Please re-try with a different image"
        res = mm_wrapper.create_custom_emoji(com_value.lower(), bytes(image_bytes))
        
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
            return "Problem in the application server. Please contact system admin"

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
        if not mes:
            logger.warning("incorrect format for value. Invalidating the request")
            return self.help()
            # "Format incorrect for adding/listing company value. Ensure no special characters other than dot(.), dash(-), underscore(-) are in the value name. \n Follow example as follows: \n /umatter value add \"ownership\" <http image url with extension (jpg|gif|png|jpeg)"

        first_split = self.transObj.text.split(" ", 1)
        if first_split[1].startswith("add"):
            return self.add_value()
        else:
            return "Option not recognized. Available options - "
        # elif first_split[1].startswith("list"):
        #     return self.list_value()