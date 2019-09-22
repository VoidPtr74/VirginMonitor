FROM python:latest

RUN mkdir /prometheus
ADD prometheus /prometheus
ADD resources /
RUN chmod 555 run.sh
RUN pip install --no-cache-dir prometheus_client

CMD ["./run.sh"]
