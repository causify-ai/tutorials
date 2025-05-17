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

import time
import warnings

import six
import urllib3
from urllib3.exceptions import ConnectTimeoutError, ReadTimeoutError
from urllib3.util.retry import Retry

from ..exceptions import ConnectionError, ConnectionTimeout
from ..utils import DEFAULT, client_meta_version, normalize_headers
from .base import Connection

CA_CERTS = None

try:
    import certifi

    CA_CERTS = certifi.where()
except ImportError:  # pragma: nocover
    pass


class Urllib3HttpConnection(Connection):
    """
    Default connection class using the `urllib3` library and the http protocol.

    :arg host: hostname of the node (default: localhost)
    :arg port: port to use (integer)
    :arg url_prefix: optional url prefix
    :arg timeout: default timeout in seconds (float, default: 10)
    :arg use_ssl: use ssl for the connection if `True`
    :arg verify_certs: whether to verify SSL certificates
    :arg ssl_show_warn: show warning when verify certs is disabled
    :arg ca_certs: optional path to CA bundle.
        See https://urllib3.readthedocs.io/en/latest/security.html#using-certifi-with-urllib3
        for instructions how to get default set
    :arg client_cert: path to the file containing the private key and the
        certificate, or cert only if using client_key
    :arg client_key: path to the file containing the private key if using
        separate cert and key files (client_cert will contain only the cert)
    :arg ssl_version: version of the SSL protocol to use. Choices are:
        SSLv23 (default) SSLv2 SSLv3 TLSv1 (see ``PROTOCOL_*`` constants in the
        ``ssl`` module for exact options for your environment).
    :arg ssl_assert_hostname: use hostname verification if not `False`
    :arg ssl_assert_fingerprint: verify the supplied certificate fingerprint if not `None`
    :arg connections_per_host: the number of connections which will be kept open to this
        host. See https://urllib3.readthedocs.io/en/latest/reference/urllib3.connectionpool.html
        for more information.
    :arg headers: any custom http headers to be add to requests
    :arg http_compress: Use gzip compression
    :arg opaque_id: Send this value in the 'X-Opaque-Id' HTTP header
        For tracing all requests made by this transport.
    """

    HTTP_CLIENT_META = ("ur", client_meta_version(urllib3.__version__))

    def __init__(
        self,
        host="localhost",
        port=None,
        use_ssl=False,
        verify_certs=DEFAULT,
        ssl_show_warn=DEFAULT,
        ca_certs=None,
        client_cert=None,
        client_key=None,
        ssl_version=None,
        ssl_assert_hostname=None,
        ssl_assert_fingerprint=None,
        connections_per_host=10,
        headers=None,
        ssl_context=None,
        http_compress=None,
        opaque_id=None,
        **kwargs
    ):
        # Initialize headers before calling super().__init__().
        self.headers = urllib3.make_headers(keep_alive=True)

        super(Urllib3HttpConnection, self).__init__(
            host=host,
            port=port,
            use_ssl=use_ssl,
            headers=headers,
            http_compress=http_compress,
            opaque_id=opaque_id,
            **kwargs
        )
        pool_class = urllib3.HTTPConnectionPool
        kw = {}

        # if providing an SSL context, raise error if any other SSL related flag is used
        if ssl_context and (
            (verify_certs is not DEFAULT)
            or (ssl_show_warn is not DEFAULT)
            or ca_certs
            or client_cert
            or client_key
            or ssl_version
        ):
            warnings.warn(
                "When using `ssl_context`, all other SSL related kwargs are ignored"
            )

        # if ssl_context provided use SSL by default
        if ssl_context and self.use_ssl:
            pool_class = urllib3.HTTPSConnectionPool
            kw.update(
                {
                    "assert_fingerprint": ssl_assert_fingerprint,
                    "ssl_context": ssl_context,
                }
            )

        elif self.use_ssl:
            pool_class = urllib3.HTTPSConnectionPool
            kw.update(
                {
                    "ssl_version": ssl_version,
                    "assert_hostname": ssl_assert_hostname,
                    "assert_fingerprint": ssl_assert_fingerprint,
                }
            )

            # Convert all sentinel values to their actual default
            # values if not using an SSLContext.
            if verify_certs is DEFAULT:
                verify_certs = True
            if ssl_show_warn is DEFAULT:
                ssl_show_warn = True

            ca_certs = CA_CERTS if ca_certs is None else ca_certs
            if verify_certs:
                if not ca_certs:
                    raise ValueError(
                        "Root certificates are missing for certificate "
                        "validation. Either pass them in using the ca_certs parameter or "
                        "install certifi to use it automatically."
                    )

                kw.update(
                    {
                        "cert_reqs": "CERT_REQUIRED",
                        "ca_certs": ca_certs,
                        "cert_file": client_cert,
                        "key_file": client_key,
                    }
                )
            else:
                kw["cert_reqs"] = "CERT_NONE"
                if ssl_show_warn:
                    warnings.warn(
                        "Connecting to %r using SSL with verify_certs=False is insecure"
                        % self.base_url
                    )
                else:
                    urllib3.disable_warnings()

        self.pool = pool_class(
            self.host,
            port=self.port,
            timeout=self.request_timeout,
            maxsize=connections_per_host,
            block=True,
            **kw
        )

    def perform_request(
        self,
        method,
        target,
        body=None,
        request_timeout=DEFAULT,
        ignore_status=(),
        headers=None,
    ):
        url = self.base_url + self.url_prefix + target

        start = time.time()
        orig_body = body
        try:
            kw = {}
            if request_timeout is not DEFAULT:
                kw["timeout"] = request_timeout

            # in python2 we need to make sure the url and method are not
            # unicode. Otherwise the body will be decoded into unicode too
            target = six.ensure_str(target, "utf-8")
            method = six.ensure_str(method, "ascii")

            request_headers = self.headers.copy()
            request_headers.update(headers or ())
            request_headers = normalize_headers(request_headers)

            if self.http_compress and body:
                body = self._gzip_compress(body)
                request_headers["content-encoding"] = "gzip"

            response = self.pool.urlopen(
                method,
                target,
                body,
                retries=Retry(False),
                headers=request_headers,
                **kw
            )
            response_headers = dict(response.headers)
            duration = time.time() - start
            raw_data = response.data.decode("utf-8", "surrogatepass")
        except Exception as e:
            self.log_request_fail(
                method=method,
                url=url,
                body=orig_body,
                duration=time.time() - start,
                exception=e,
            )
            if isinstance(e, (ConnectTimeoutError, ReadTimeoutError)):
                raise ConnectionTimeout(
                    "Connection timed out during request", errors=(e,)
                )
            raise ConnectionError(str(e), errors=(e,))

        # raise errors based on http status codes, let the client handle those if needed
        if not (200 <= response.status < 300) and response.status not in ignore_status:
            self.log_request_fail(
                method=method,
                url=url,
                body=orig_body,
                duration=duration,
                status=response.status,
                response=raw_data,
            )
            self._raise_error(
                status=response.status, headers=response_headers, raw_data=raw_data
            )

        self.log_request_success(
            method=method,
            url=url,
            body=orig_body,
            status=response.status,
            response=raw_data,
            duration=duration,
        )

        return response.status, response_headers, raw_data

    def close(self):
        """
        Explicitly closes connection
        """
        self.pool.close()
