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

from six import add_metaclass, python_2_unicode_compatible

from .response import Headers

HTTP_EXCEPTIONS = {}


class TransportErrorMeta(type):
    def __new__(meta_cls, *args, **kwargs):
        cls = type.__new__(meta_cls, *args, **kwargs)
        status = getattr(cls, "status", None)
        if status is not None:
            HTTP_EXCEPTIONS[status] = cls
        return cls


@python_2_unicode_compatible
@add_metaclass(TransportErrorMeta)
class TransportError(Exception):
    """Generic exception for the 'elastic-transport' package.

    For the 'errors' attribute, errors are ordered from
    most recently raised (index=0) to least recently raised (index=N)

    If an HTTP status code is available with the error it
    will be stored under 'status'. If HTTP headers are available
    they are stored under 'headers'.
    """

    status = None

    def __init__(self, message, errors=(), status=None, headers=None):
        super(TransportError, self).__init__(message)
        self.errors = tuple(errors)
        self.message = message
        if status is not None:
            self.status = status
        if headers is not None:
            self.headers = Headers(headers)
        else:
            self.headers = None

    def __repr__(self):
        parts = [repr(self.message)]
        if self.status is not None:
            parts.append("status=%r" % self.status)
        if self.errors:
            parts.append("errors=%r" % (self.errors,))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(parts))

    def __str__(self):
        if self.status:
            return "[%s] %s" % (self.status, self.message)
        return str(self.message)


class SerializationError(TransportError):
    """Error that occurred during the serialization or
    deserialization of an HTTP message body
    """


class ConnectionError(TransportError):
    """Error raised by the HTTP connection"""


class ConnectionTimeout(TransportError):
    """Connection timed out during an operation"""


class APIError(TransportError):
    """Error that is raised from the service via HTTP status codes"""


class BadRequestError(APIError):
    """Error for HTTP status 400 'Bad Request'"""

    status = 400


class UnauthorizedError(APIError):
    """Error for HTTP status 401 'Unauthorized'"""

    status = 401


class PaymentRequiredError(APIError):
    """Error for HTTP status 402 'Payment Required'
    Usually signals that your instance doesn't have
    a proper license active for the operation
    """

    status = 402


class ForbiddenError(APIError):
    """Error for HTTP status 403 'Forbidden'"""

    status = 403


class NotFoundError(APIError):
    """Error for HTTP status 404 'Not Found'"""

    status = 404


class ConflictError(APIError):
    """Error for HTTP status 409 'Conflict'"""

    status = 409


class PayloadTooLargeError(APIError):
    """Error for HTTP status 413 'Payload Too Large'"""

    status = 413


class UnprocessableEntityError(APIError):
    """Error for HTTP status 422 'Unprocessable Entity'"""

    status = 422


class InternalServerError(APIError):
    """Error for HTTP status 500 'Internal Server Error'"""

    status = 500


class MethodNotImplementedError(APIError):
    """Error for HTTP status 501 'Method Not Allowed'"""

    status = 501


class BadGatewayError(APIError):
    """Error for HTTP status 502 'Bad Gateway'"""

    status = 502


class ServiceUnavailableError(APIError):
    """Error for HTTP status 503 'Service Unavailable'"""

    status = 503


class GatewayTimeoutError(APIError):
    """Error for HTTP status 504 'Gateway Timeout'"""

    status = 504
