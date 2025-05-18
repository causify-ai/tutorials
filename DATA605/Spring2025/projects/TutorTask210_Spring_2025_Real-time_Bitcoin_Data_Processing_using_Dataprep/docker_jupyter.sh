#!/bin/bash
docker run -p 8890:8888 -v "$(pwd)":/app dataprep_project
