# Virgin Super Hub 3.0 Monitor

## Overview 

Simple status monitor Docker image that will periodically query basic information from Virgin Media's Super Hub 3.0 and store it in Prometheus metrics. 

The Prometheus web interface is exposed via port 9090 inside (and by default also on the host of) the docker image.

As a basic default, this assumes that the router is available from the Docker image at address 192.168.0.1 (configurable in the Python code).

## Building and Running

From a completely fresh checkout, run 

`get_prometheus_build_and_run.sh`

This will retrieve an ARMv7 build of Prometheus 2.12 and extract it to a "prometheus" subdirectory before building the docker image and running it. 

Having run the "get_prometheus..." script once, you should be able to run 

`build_and_run.sh`

without having to redownload prometheus all over again.

## Configuration

All of the scripts and configuration (including the python script for querying the router web api and the Prometheus configuration) are stored in the `resources` directory.