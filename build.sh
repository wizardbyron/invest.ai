#!/bin/bash

docker build -t invest-ai:$(date +%Y%m%d) -f Dockerfile .
docker image save -o output/invest-ai.$(date +%Y%m%d).tar invest-ai:$(date +%Y%m%d)