#!/bin/bash

# Script to start the pequebot container

docker compose down
docker compose build
rm -f logs/peque_bot.log
docker compose up -d
docker logs -f pequebot