#!/usr/bin/env bash

echo "start at" `date`
cd /
python -m app.read_movie
echo "finished at" `date`