#!/bin/bash
docker run -it --entrypoint /bin/bash -v "$(pwd)":/app dataprep_project
