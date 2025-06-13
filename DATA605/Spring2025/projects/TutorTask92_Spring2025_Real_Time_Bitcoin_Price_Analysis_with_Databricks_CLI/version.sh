#!/bin/bash
#
# Print the version of the tools inside a container.
#

set -e

VERSION=$(python3 --version)
echo "# Python3: $VERSION"

VERSION=$(pip3 --version)
echo "# pip3: $VERSION"

if which jupyter >/dev/null 2>&1; then
    VERSION=$(jupyter --version)
else
    VERSION="-"
fi
echo "# jupyter: $VERSION"

if which mongod >/dev/null 2>&1; then
    VERSION=$(mongod --version)
else
    VERSION="-"
fi
echo "# mongo: $VERSION"

echo "# Python packages"
pip3 list
