#!/bin/bash
docker rm -f btc_pipeline_container redis-server
docker rmi btc_pipeline_image
