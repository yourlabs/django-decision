class BaseException(Exception):
    """ Base class for exceptions of this app. """
    pass


class PollClosed(BaseException):
    pass


class InvalidChoice(BaseException):
    pass


class SelfDelegation(BaseException):
    pass


class UnauthorizedDelegatedVote(BaseException):
    pass


class DirectVoteOverrideAttempt(BaseException):
    pass
