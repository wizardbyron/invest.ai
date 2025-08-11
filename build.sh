#!/bin/bash

docker build Dockerfile .
docker image save -o output/invest-ai.$(date +%Y%m%d).tar invest-ai:latest