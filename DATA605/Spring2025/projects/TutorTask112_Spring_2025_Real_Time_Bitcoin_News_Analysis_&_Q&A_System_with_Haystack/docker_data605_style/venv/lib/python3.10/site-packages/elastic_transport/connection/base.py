#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import gzip
import io
import logging

import six

from ..exceptions import HTTP_EXCEPTIONS, APIError
from ..utils import DEFAULT, normalize_headers

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger("elastic_transport.connection")


class Connection(object):
    """
    Class responsible for maintaining a connection to an Enterprise Search node. It
    holds persistent connection pool to it and it's main interface
    (`perform_request`) is thread-safe.

    Also responsible for logging.

    :arg host: hostname of the node (default: localhost)
    :arg port: port to use (integer, default: 9200)
    :arg use_ssl: use ssl for the connection if `True`
    :arg path_prefix: optional url prefix for Enterprise Search
    :arg timeout: default timeout in seconds (float, default: 10)
    :arg http_compress: Use gzip compression
    :arg opaque_id: Send this value in the 'X-Opaque-Id' HTTP header
        For tracing all requests made by this transport.
    :arg user_agent: 'User-Agent' HTTP header for the given service.
    """

    HTTP_CLIENT_META = None

    def __init__(
        self,
        host="localhost",
        port=None,
        use_ssl=False,
        url_prefix="",
        request_timeout=10,
        headers=None,
        http_compress=None,
        opaque_id=None,
        user_agent=None,
        **kwargs
    ):
        # Work-around if the implementing class doesn't
        # define the headers property before calling super().__init__()
        if not hasattr(self, "headers"):
            self.headers = {}

        self.headers.update(normalize_headers(headers))
        if opaque_id:
            self.headers["x-opaque-id"] = opaque_id
        if user_agent:
            self.headers.setdefault("user-agent", user_agent)

        self.headers.setdefault("content-type", "application/json")
        if http_compress:
            self.headers["accept-encoding"] = "gzip"

        scheme = kwargs.get("scheme", "http")
        if use_ssl or scheme == "https":
            scheme = "https"
            use_ssl = True
        self.use_ssl = use_ssl
        self.http_compress = http_compress or False

        self.scheme = scheme
        self.port = port
        self.host = host
        if url_prefix:
            url_prefix = "/" + url_prefix.strip("/")
        self.url_prefix = url_prefix
        self.request_timeout = request_timeout

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.base_url)

    def __eq__(self, other):
        if not isinstance(other, Connection):
            raise TypeError("Unsupported equality check for %s and %s" % (self, other))
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return id(self)

    @property
    def base_url(self):
        return "".join(
            [
                self.scheme,
                "://",
                # IPv6 must be wrapped by [...]
                "[%s]" % self.host if ":" in self.host else self.host,
                ":%s" % self.port if self.port is not None else "",
                self.url_prefix,
            ]
        )

    def perform_request(
        self,
        method,
        target,
        body=None,
        request_timeout=DEFAULT,
        ignore_status=(),
        headers=None,
    ):  # pragma: nocover
        raise NotImplementedError()

    def log_request_success(self, method, url, body, status, response, duration):
        """Log a successful API call"""
        # body has already been serialized to utf-8, deserialize it for logging
        # TODO: find a better way to avoid (de)encoding the body back and forth
        if body:
            try:
                body = body.decode("utf-8", "ignore")
            except AttributeError:
                pass

        logger.info("%s %s [status:%s request:%.3fs]", method, url, status, duration)
        logger.debug("> %s", body)
        logger.debug("< %s", response)

    def log_request_fail(
        self,
        method,
        url,
        body,
        duration,
        status=None,
        response=None,
        exception=None,
    ):
        """Log an unsuccessful API call"""
        # do not log 404s on HEAD requests
        if method == "HEAD" and status == 404:
            return
        logger.warning(
            "%s %s [status:%s request:%.3fs]",
            method,
            url,
            status or "N/A",
            duration,
            exc_info=exception is not None,
        )

        # body has already been serialized to utf-8, deserialize it for logging
        # TODO: find a better way to avoid (de)encoding the body back and forth
        if body:
            try:
                body = body.decode("utf-8", "ignore")
            except AttributeError:
                pass

        logger.debug("> %s", body)

        if response is not None:
            logger.debug("< %s", response)

    def _raise_error(self, status, headers, raw_data):
        """Locate appropriate exception and raise it. Attempts
        to decode the raw data as JSON for better usability.
        """
        try:
            raw_data = json.loads(six.ensure_str(raw_data, "utf-8", "ignore"))
        except Exception:
            pass
        raise HTTP_EXCEPTIONS.get(status, APIError)(
            message=raw_data, status=status, headers=headers
        )

    def _gzip_compress(self, body):
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as f:
            f.write(body)
        return buf.getvalue()
