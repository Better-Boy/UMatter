from .base import Response


class Rewards(Response):

    def __init__(self, data):
        self.transObj = data

    def check_format(self):
        return ""

    def response(self):
        return ""