#!/bin/bash
docker run -it --rm \
  -v "$PWD":/home/jovyan/work \
  txtai_project \
  bash

