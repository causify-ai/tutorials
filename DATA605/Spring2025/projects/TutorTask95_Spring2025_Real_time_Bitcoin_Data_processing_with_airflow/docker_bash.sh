#!/bin/bash
docker exec -it $(docker ps --filter name=airflow-webserver --format "{{.ID}}") /bin/bash
