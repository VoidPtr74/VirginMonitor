from prometheus_client import start_http_server, Gauge
import random
import time
import urllib.request
import json
import sys
import datetime
import time
import math

ROUTER_STATUS_URL = "http://192.168.0.1/getRouterStatus"

UPSTREAM_CHANNEL_ID_PREFIX = "1.3.6.1.2.1.10.127.1.1.2.1.1."
UPSTREAM_CHANNEL_FREQUENCY_PREFIX = "1.3.6.1.2.1.10.127.1.1.2.1.2."
UPSTREAM_CHANNEL_POWER_10X_PREFIX = "1.3.6.1.4.1.4491.2.1.20.1.2.1.1."

DOWNSTREAM_CHANNEL_ID_PREFIX = "1.3.6.1.2.1.10.127.1.1.1.1.1."
DOWNSTREAM_CHANNEL_FREQUENCY_PREFIX = "1.3.6.1.2.1.10.127.1.1.1.1.2."
DOWNSTREAM_CHANNEL_POWER_10X_PREFIX = "1.3.6.1.2.1.10.127.1.1.1.1.6."
DOWNSTREAM_CHANNEL_SNR_PREFIX = "1.3.6.1.2.1.10.127.1.1.4.1.5."

gauge_downstream_channel_count = Gauge('channel_downstream_count', 'How many downstream channels are active?')
gauge_downstream_channel_count.set(math.nan)
gauge_upstream_channel_count = Gauge('channel_upstream_count', 'How many upstream channels are active?')
gauge_upstream_channel_count.set(math.nan)
gauge_total_downstream_power = Gauge('total_downstream_power_dbmv', 'Total downstream power (dBmV (10log10))')
gauge_total_downstream_power.set(math.nan)
gauge_total_upstream_power = Gauge('total_upstream_power_dbmv', 'Total upstream power (dBmV (10log10))')
gauge_total_upstream_power.set(math.nan)

gauges_channel_upstream_power = dict()
gauges_channel_upstream_frequency = dict()
gauges_channel_downstream_power = dict()
gauges_channel_downstream_snr = dict()
gauges_channel_downstream_frequency = dict()


def loop():
    contents = urllib.request.urlopen(ROUTER_STATUS_URL).read()
    loaded_json = json.loads(contents)
    upstream_key_ids, upstream_channel_ids = get_prefix_ids(loaded_json, UPSTREAM_CHANNEL_ID_PREFIX)
    upstream_channel_count = len(upstream_channel_ids)
    upstream_frequency_per_channel = get_data_from_json(loaded_json, UPSTREAM_CHANNEL_FREQUENCY_PREFIX, upstream_key_ids, int)

    upstream_power_per_channel_x10 = \
        get_data_from_json(loaded_json, UPSTREAM_CHANNEL_POWER_10X_PREFIX, upstream_key_ids, float)
    upstream_power_per_channel = list(map(lambda x: x / 10.0, upstream_power_per_channel_x10))
    total_upstream_power = math.log10(sum(map(lambda x: 10 ** x, upstream_power_per_channel))) * 10

    downstream_key_ids, downstream_channel_ids = get_prefix_ids(loaded_json, DOWNSTREAM_CHANNEL_ID_PREFIX)
    downstream_channel_count = len(downstream_channel_ids)
    downstream_frequency_per_channel = \
        get_data_from_json(loaded_json, DOWNSTREAM_CHANNEL_FREQUENCY_PREFIX, downstream_key_ids, int)

    downstream_power_per_channel_x10 = \
        get_data_from_json(loaded_json, DOWNSTREAM_CHANNEL_POWER_10X_PREFIX, downstream_key_ids, float)
    downstream_power_per_channel = list(map(lambda x: x / 10.0, downstream_power_per_channel_x10))
    total_downstream_power = math.log10(sum(map(lambda x: 10 ** x, downstream_power_per_channel))) * 10

    downstream_snr_per_channel_x10 = \
        get_data_from_json(loaded_json, DOWNSTREAM_CHANNEL_SNR_PREFIX, downstream_key_ids, float)
    downstream_snr_per_channel = list(map(lambda x: x / 10.0, downstream_snr_per_channel_x10))

    gauge_downstream_channel_count.set(downstream_channel_count)
    gauge_upstream_channel_count.set(upstream_channel_count)
    gauge_total_downstream_power.set(total_downstream_power)
    gauge_total_upstream_power.set(total_upstream_power)

    init_multiple_gauges(gauges_channel_upstream_power, upstream_channel_ids)
    init_multiple_gauges(gauges_channel_upstream_frequency, upstream_channel_ids)
    init_multiple_gauges(gauges_channel_downstream_power, downstream_channel_ids)
    init_multiple_gauges(gauges_channel_downstream_snr, downstream_channel_ids)
    init_multiple_gauges(gauges_channel_downstream_frequency, downstream_channel_ids)

    for i in range(len(upstream_channel_ids)):
        set_gauge_value(upstream_channel_ids[i], upstream_power_per_channel[i], gauges_channel_upstream_power,
                        "channel_upstream_power_dbmv_", "Power for upstream channel ")
        set_gauge_value(upstream_channel_ids[i], upstream_frequency_per_channel[i], gauges_channel_upstream_frequency,
                        "channel_upstream_frequency_hz_", "Frequency for upstream channel ")
    for i in range(len(downstream_channel_ids)):
        # DS power
        set_gauge_value(downstream_channel_ids[i], downstream_power_per_channel[i], gauges_channel_downstream_power,
                        "channel_downstream_power_dbmv_", "Power for downstream channel ")
        # SNR
        set_gauge_value(downstream_channel_ids[i], downstream_snr_per_channel[i], gauges_channel_downstream_snr,
                        "channel_downstream_snr_db_", "SNR for downstream channel ")
        # Frequency
        set_gauge_value(downstream_channel_ids[i], downstream_frequency_per_channel[i], gauges_channel_downstream_frequency,
                        "channel_downstream_frequency_hz_", "Frequency for downstream channel ")


def set_gauge_value(channel_id, value, gauges, name_prefix, desc_prefix):
    if channel_id not in gauges:
        gauges[channel_id] = Gauge(name_prefix + str(channel_id), desc_prefix + str(channel_id))

    gauges[channel_id].set(value)


def init_multiple_gauges(gauges, known_ids):
    for id in gauges:
        if id not in known_ids:
            gauges[id].set(math.nan)


def get_data_from_json(loaded_json, prefix, key_ids, target_type):
    keys = map(lambda x: prefix + x, key_ids)
    data = map(lambda x: loaded_json[x], keys)
    return list(map(lambda x: target_type(x), data))


def get_prefix_ids(loaded_json, prefix):
    id_keys = list(filter(lambda x: x.startswith(prefix), loaded_json.keys()))
    return list(map(lambda x: x.split('.')[-1], id_keys)), list(map(lambda x: int(loaded_json[x]), id_keys))


def main():
    start_http_server(8000)
    start = datetime.datetime.utcnow()
    interval = datetime.timedelta(seconds=15)
    target = start

    while True:
        try:
            start = target
            target = start + interval
            loop()
        except Exception:
            e = sys.exc_info()[0]
            time_now = datetime.datetime.utcnow()
            print(str(time_now) + (" - ERROR: %s" % e))
        remaining_time = (target - datetime.datetime.utcnow()).total_seconds()
        if remaining_time > 0:
            print("waiting for " + str(remaining_time) + "s")
            time.sleep(remaining_time)
        else:
            print("not pausing..")

if __name__ == '__main__':
    main()
