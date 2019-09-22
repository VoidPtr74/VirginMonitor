wget https://github.com/prometheus/prometheus/releases/download/v2.12.0/prometheus-2.12.0.linux-armv7.tar.gz 

tar xvfz prometheus-*.tar.gz
rm prometheus-*.tar.gz 

for name in prometheus-*; do
  mv "$name" "prometheus"
done

./build_and_run.sh
