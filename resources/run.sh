#!/bin/bash

./prometheus/prometheus --config.file=prometheus.yml &
python query.py

