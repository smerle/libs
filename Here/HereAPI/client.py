#
# Copyright 2015 Smerle Inc. All rights reserved
#

# __author__ = 'thomasr'

"""
Core client functionality, common across all API requests
"""

# import base64
from datetime import datetime
from datetime import timedelta
from pprint import pprint
# import hashlib
# import hmac
import requests
import random
import time

import HereAPI

try:  # Python 3
    from urllib.parse import urlencode
except ImportError:  # Python 2
    from urllib import urlencode

_RETRIABLE_STATUSES = set([500, 503])
_USER_AGENT = "HEREAPIClientPython/%s" % HereAPI.__version__
# _DEFAULT_BASE_URL = "https://maps.googleapis.com"


class Client(object):
    """Performs requests to the Google Maps API web services."""

    def __init__(self, client_id=None, client_secret=None,
                 timeout=None, connect_timeout=None, read_timeout=None,
                 retry_timeout=60):
        """
        :param timeout: Combined connect and read timeout for HTTP requests, in
            seconds. Specify "None" for no timeout.
        :type timeout: int

        :param connect_timeout: Connection timeout for HTTP requests, in
            seconds. You should specify read_timeout in addition to this option.
            Note that this requires requests >= 2.4.0.
        :type connect_timeout: int

        :param read_timeout: Read timeout for HTTP requests, in
            seconds. You should specify connect_timeout in addition to this
            option. Note that this requires requests >= 2.4.0.
        :type read_timeout: int

        :param retry_timeout: Timeout across multiple retriable requests, in
            seconds.
        :type retry_timeout: int

        :param client_id: (for Maps API for Work customers) Your client ID.
        :type client_id: string

        :param client_secret: (for Maps API for Work customers) Your client
            secret (base64 encoded).
        :type client_secret: string

        :raises ValueError: when either credentials are missing, incomplete
            or invalid.
        :raises NotImplementedError: if connect_timeout and read_timeout are
            used with a version of requests prior to 2.4.0.
        """
        if not (client_secret and client_id):
            raise ValueError("Must provide API key or enterprise credentials "
                             "when creating client.")

        # if key and not key.startswith("AIza"):
        #     raise ValueError("Invalid API key provided.")

        # self.key = key

        if timeout and (connect_timeout or read_timeout):
            raise ValueError("Specify either timeout, or connect_timeout " +
                             "and read_timeout")

        if connect_timeout and read_timeout:
            # Check that the version of requests is >= 2.4.0
            chunks = requests.__version__.split(".")
            if chunks[0] < 2 or (chunks[0] == 2 and chunks[1] < 4):
                raise NotImplementedError("Connect/Read timeouts require "
                                          "requests v2.4.0 or higher")
            self.timeout = (connect_timeout, read_timeout)
        else:
            self.timeout = timeout

        self.client_id = client_id
        self.client_secret = client_secret
        self.retry_timeout = timedelta(seconds=retry_timeout)

    def _get(self, url, params, first_request_time=None, retry_counter=0,
             accepts_clientid=True, extract_body=None):
        """Performs HTTP GET request with credentials, returning the body as
        JSON.

        :param url: URL path for the request. Should begin with a slash.
        :type url: string
        :param params: HTTP GET parameters.
        :type params: dict or list of key/value tuples
        :param first_request_time: The time of the first request (None if no retries
                have occurred).
        :type first_request_time: datetime.datetime
        :param retry_counter: The number of this retry, or zero for first attempt.
        :type retry_counter: int
        :param accepts_clientid: Whether this call supports the client/signature
                params. Some APIs require API keys (e.g. Roads).
        :type accepts_clientid: bool
        :param extract_body: A function that extracts the body from the request.
                If the request was not successful, the function should raise a
                HereAPI.HTTPError or HereAPI.ApiError as appropriate.
        :type extract_body: function

        :raises ApiError: when the API returns an error.
        :raises Timeout: if the request timed out.
        :raises TransportError: when something went wrong while trying to
                exceute a request.
        """

        if not first_request_time:
            first_request_time = datetime.now()

        elapsed = datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise HereAPI.exceptions.Timeout()

        if retry_counter > 0:
            # 0.5 * (1.5 ^ i) is an increased sleep time of 1.5x per iteration,
            # starting at 0.5s when retry_counter=0. The first retry will occur
            # at 1, so subtract that first.
            delay_seconds = 0.5 * 1.5 ** (retry_counter - 1)

            # Jitter this value by 50% and pause.
            time.sleep(delay_seconds * (random.random() + 0.5))

        authed_url = self._generate_auth_url(url, params, accepts_clientid)
        # print("authed_url = %s" % authed_url)

        try:
            resp = requests.get(authed_url,
                                headers={"User-Agent": _USER_AGENT},
                                timeout=self.timeout,
                                verify=True)  # NOTE(cbro): verify SSL certs.
        except requests.exceptions.Timeout:
            raise HereAPI.exceptions.Timeout()
        except Exception as e:
            raise HereAPI.exceptions.TransportError(e)

        if resp.status_code in _RETRIABLE_STATUSES:
            # Retry request.
            return self._get(url, params, first_request_time, retry_counter + 1,
                             extract_body)
        # pprint(resp)
        try:
            if extract_body:
                return extract_body(resp)
            return self._get_body(resp)
        except HereAPI.exceptions._RetriableRequest:
            # Retry request.
            return self._get(url, params, first_request_time, retry_counter + 1,
                             extract_body)

    def _get_body(self, resp):
        if resp.status_code != 200:
            raise HereAPI.exceptions.HTTPError(resp.status_code)

        body = resp.json()

        # api_status = body["status"]
        # if api_status == "OK" or api_status == "ZERO_RESULTS":
        #     return body
        return body
        # if api_status == "OVER_QUERY_LIMIT":
        #     raise HereAPI.exceptions._RetriableRequest()
        #
        # if "error_message" in body:
        #     raise HereAPI.exceptions.ApiError(api_status,
        #             body["error_message"])
        # else:
        #     raise HereAPI.exceptions.ApiError(api_status)

    def _generate_auth_url(self, path, params, accepts_clientid):
        """Returns the path and query string portion of the request URL, first
        adding any necessary parameters.
        :param path: The path portion of the URL.
        :type path: string
        :param params: URL parameters.
        :type params: dict or list of key/value tuples
        :rtype: string
        """
        # Deterministic ordering through sorting by key.
        # Useful for tests, and in the future, any caching.
        if type(params) is dict:
            params = sorted(params.items())

        if accepts_clientid and self.client_id and self.client_secret:
            params.append(("app_id", self.client_id))

            path = "?".join([path, urlencode_params(params)])
            # sig = sign_hmac(self.client_secret, path)
            sig = self.client_secret
            return path + "&app_code=" + sig

        # if self.key:
        #     params.append(("key", self.key))
        #     return path + "?" + urlencode_params(params)

        raise ValueError("Must provide API key for this API. It does not accept"
                         "enterprise credentials.")


from HereAPI.geocode import geocode
from HereAPI.routing import routing
from HereAPI.matrix import matrix

Client.geocode = geocode
Client.routing = routing
Client.matrix = matrix


def urlencode_params(params):
    """URL encodes the parameters.
    :param params: The parameters
    :type params: list of key/value tuples.
    """
    # urlencode does not handle unicode strings in Python 2.
    # First normalize the values so they get encoded correctly.
    params = [(key, normalize_for_urlencode(val)) for key, val in params]
    return urlencode(params)


try:
    unicode
    # NOTE(cbro): `unicode` was removed in Python 3. In Python 3, NameError is
    # raised here, and caught below.

    def normalize_for_urlencode(value):
        """(Python 2) Converts the value to a `str` (raw bytes)."""
        if isinstance(value, unicode):
            return value.encode('utf8')
        if isinstance(value, str):
            return value
        return normalize_for_urlencode(str(value))

except NameError:
    def normalize_for_urlencode(value):
        """(Python 3) No-op."""
        # urlencode in Python 3 handles all the types we are passing it.
        return value
