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

import binascii
import re
from collections import namedtuple
from platform import python_version

from six import ensure_binary, ensure_str

from ._version import __version__

# Sentinel value used to highlight default values
# when 'None' has special meaning (like request_timeout)
# The only supported operation on this value is identity ('is DEFAULT')
DEFAULT = namedtuple("DEFAULT", ())()


def create_user_agent(name, version):
    """Creates the 'User-Agent' header given the library name and version"""
    return "%s/%s (Python/%s; elastic-transport/%s)" % (
        name,
        version,
        python_version(),
        __version__,
    )


def client_meta_version(ver):
    """Converts a Python package version to a meta version.
    Meta version simply adds a 'p' suffix for all pre-releases
    """
    ver, ver_is_pre = re.match(r"^([0-9][0-9.]*[0-9]|[0-9])(.*)$", ver).groups()
    if ver_is_pre:
        ver += "p"
    return ver


def normalize_headers(headers):
    """Normalizes HTTP headers to be lowercase to ensure
    there are no case-collisions deeper within the stack.
    """
    if not headers:
        return {}
    return {
        k.lower(): v
        for k, v in (headers.items() if hasattr(headers, "items") else headers)
    }


CloudID = namedtuple(
    "CloudID", ["cluster_name", "es_host", "es_port", "kibana_host", "kibana_port"]
)


def parse_cloud_id(cloud_id):
    """Parses a Cloud ID into its components"""
    try:
        cloud_id = ensure_str(cloud_id)
        cluster_name, _, cloud_id = cloud_id.partition(":")
        parts = ensure_str(
            binascii.a2b_base64(ensure_binary(cloud_id, "ascii")), "ascii"
        ).split("$")
        parent_dn = parts[0]
        if not parent_dn:
            raise ValueError()  # Caught and re-raised properly below
        try:
            es_uuid = parts[1]
        except IndexError:
            es_uuid = None
        try:
            kibana_uuid = parts[2] or None
        except IndexError:
            kibana_uuid = None
        port = None
        if ":" in parent_dn:
            parent_dn, _, parent_port = parent_dn.rpartition(":")
            if parent_port != "443":
                port = int(parent_port)
    except (ValueError, IndexError, UnicodeError):
        raise ValueError("Cloud ID is not properly formatted")

    es_host = "%s.%s" % (es_uuid, parent_dn) if es_uuid else None
    kibana_host = "%s.%s" % (kibana_uuid, parent_dn) if kibana_uuid else None

    return CloudID(
        cluster_name=cluster_name,
        es_host=es_host,
        es_port=port,
        kibana_host=kibana_host,
        kibana_port=port,
    )
