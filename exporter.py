import logging
import os
import time
import dateutil.parser as dp

from datetime import datetime, timedelta
from srpenergy.client import SrpEnergyClient
from prometheus_client import start_http_server, Summary
from prometheus_client import Gauge
from prometheus_client.core import (
    GaugeMetricFamily, Timestamp, REGISTRY
)

logging.getLogger().setLevel(logging.INFO)
accountid = os.environ['SRP_ID']
username = os.environ['SRP_USER']
password = os.environ['SRP_PASS']
client = SrpEnergyClient(accountid, username, password)

# Get yesterday's details from SRP
def get_yesterday():
    end_date = datetime.now()
    start_date = datetime.now() - timedelta(hours=30)
    usage = client.usage(start_date, end_date)
    return usage


class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        logging.info("collection_running")
        usage_gauge = GaugeMetricFamily("energy_usage", 'Help text', labels=["power"])
        cost_gauge = GaugeMetricFamily("energy_cost", "Help Text", labels=["cost"])
        metrics = get_yesterday()
        total_usage = 0
        total_cost = 0
        logging.info(metrics)
        for i in metrics:
            date, hour, isodate, kwh, cost = i
            total_cost += cost
            total_usage += kwh
            
        usage_gauge.add_metric(["kwh"], total_usage)
        cost_gauge.add_metric(["dollars"], total_cost)
        yield cost_gauge
        yield usage_gauge
        #g.add_metric(["kwh"], 20, Timestamp(1627538400, 0))
        #yield g

        #c = GaugeMetricFamily("HttpRequests", 'Help text', labels=['app'])
        #c.add_metric(["example"], 2000)
        #yield c


if __name__ == '__main__':
    start_http_server(8000)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
