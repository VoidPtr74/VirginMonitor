sudo docker build -t virginmonitor .
sudo docker run -d -p 9090:9090 --name virginmonitor virginmonitor 
