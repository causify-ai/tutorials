#!/bin/bash
docker run -p 8888:8888 -v "$(pwd)":/app dataprep_project
