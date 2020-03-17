#!/usr/bin/env bash
docker build -f ./docker/Dockfile -t movie-crawler .
docker run -td --name movie-crawler-app movie-crawler