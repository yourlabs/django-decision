class BaseException(Exception):
    """ Base class for exceptions of this app. """
    pass


class CantVoteAfterEndDate(BaseException):
    pass


class ChoiceMustExist(BaseException):
    pass
