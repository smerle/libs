#
# Copyright 2015 Smerle Inc. All rights reserved
#


"""
Defines exceptions that are thrown by HERE Maps API
"""


class ApiError(Exception):
    """ Represents an exception returned by the remote API. """
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return self.status
        else:
            return "%s (%s)" % (self.status, self.message)


class TransportError(Exception):
    """ Error in executing the request. """

    def __init__(self, base_exception=None):
        self.base_exception = base_exception

    def __str__(self):
        if self.base_exception:
            return str(self.base_exception)
        return "An unknown error occurred."


class HTTPError(TransportError):
    """ HTTP error handler"""
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return "HTTP Error: %d" % self.status_code


class Timeout(Exception):
    """ Request timed out"""
    pass


class _RetriableRequest(Exception):
    """ Cannot retry request """
    pass
