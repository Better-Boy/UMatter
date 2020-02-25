import abc

class Response(abc.ABC):

    @abc.abstractclassmethod
    def response(self):
        pass

    @abc.abstractclassmethod
    def check_format(self):
        pass