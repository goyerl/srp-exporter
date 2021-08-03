import logging
import os
import time

from datetime import datetime, timedelta
from srpenergy.client import SrpEnergyClient
from prometheus_client import start_http_server
from prometheus_client.core import (
    GaugeMetricFamily, REGISTRY
)

logging.getLogger().setLevel(logging.INFO)
accountid = os.environ["SRP_ID"]
username = os.environ["SRP_USER"]
password = os.environ["SRP_PASS"]
client = SrpEnergyClient(accountid, username, password)


class CustomCollector(object):
    """
    Collect yesterday's metrics from SrpEnergyClient 
    """
    def __init__(self):
        pass

    # Get yesterday's details from SRP
    def get_yesterday(self):
        end_date = datetime.now()
        start_date = datetime.now() - timedelta(hours=30)
        usage = client.usage(start_date, end_date)
        return usage

    def collect(self):
        logging.info("collection_running")
        usage_gauge = GaugeMetricFamily("energy_usage", "Help text", labels=["account"])
        cost_gauge = GaugeMetricFamily("energy_cost", "Help Text", labels=["account"])
        metrics = self.get_yesterday()
        total_usage = 0
        total_cost = 0
        logging.info(metrics)
        for i in metrics:
            date, hour, isodate, kwh, cost = i
            total_cost += cost
            total_usage += kwh

        usage_gauge.add_metric([accountid], total_usage)
        cost_gauge.add_metric([accountid], total_cost)
        yield cost_gauge
        yield usage_gauge



if __name__ == "__main__":
    start_http_server(8000)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
