#!/bin/bash
rm -f output/*.tar
docker build -f Dockerfile -t invest-ai:latest .
docker image save -o output/invest_ai_$(date +%Y%m%d).tar invest-ai:latest