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

"""Transport classes and utilities shared among Python Elastic client libraries"""

import sys
import warnings

from ._version import __version__  # noqa
from .connection import Connection, RequestsHttpConnection, Urllib3HttpConnection
from .connection_pool import (
    ConnectionPool,
    ConnectionSelector,
    DummyConnectionPool,
    EmptyConnectionPool,
    RandomSelector,
    RoundRobinSelector,
)
from .exceptions import (
    APIError,
    BadGatewayError,
    BadRequestError,
    ConflictError,
    ConnectionError,
    ConnectionTimeout,
    ForbiddenError,
    GatewayTimeoutError,
    InternalServerError,
    MethodNotImplementedError,
    NotFoundError,
    PayloadTooLargeError,
    PaymentRequiredError,
    SerializationError,
    ServiceUnavailableError,
    TransportError,
    UnauthorizedError,
    UnprocessableEntityError,
)
from .models import QueryParams
from .serializer import Deserializer, JSONSerializer, Serializer, TextSerializer
from .transport import Transport

__all__ = [
    "APIError",
    "BadGatewayError",
    "BadRequestError",
    "ConflictError",
    "Connection",
    "ConnectionError",
    "ConnectionPool",
    "ConnectionSelector",
    "ConnectionTimeout",
    "Deserializer",
    "DummyConnectionPool",
    "EmptyConnectionPool",
    "ForbiddenError",
    "GatewayTimeoutError",
    "InternalServerError",
    "JSONSerializer",
    "MethodNotImplementedError",
    "NotFoundError",
    "PayloadTooLargeError",
    "PaymentRequiredError",
    "QueryParams",
    "RandomSelector",
    "RequestsHttpConnection",
    "RoundRobinSelector",
    "SerializationError",
    "Serializer",
    "ServiceUnavailableError",
    "TextSerializer",
    "Transport",
    "TransportError",
    "UnauthorizedError",
    "UnprocessableEntityError",
    "Urllib3HttpConnection",
]

# Python earlier than 3.6 is deprecated and will be removed in 8.0.0
if sys.version_info < (3, 6):
    warnings.warn(
        "Support for Python 3.5 and earlier is deprecated and will be removed "
        "in v8.0.0 (current instance is Python %d.%d)" % sys.version_info[:2],
        category=DeprecationWarning,
        stacklevel=2,
    )
