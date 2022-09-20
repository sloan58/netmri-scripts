import datetime
import os
import sys
from pprint import pprint

import requests
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from infoblox_netmri import InfobloxNetMRI

load_dotenv()

# Begin time for chart data (default: today)
start = datetime.datetime.today()
chart_start_time = start.strftime("%Y-%m-%d")

# End time for chart data (default: tomorrow)
end = start + datetime.timedelta(days=1)
chart_end_time = end.strftime("%Y-%m-%d")

# Chart data to collect
chart_names = [
    'basic_configuration',
    'load_average',
    'load_per_comp',
    'mem_consumption',
    'swap_consumption',
    'mem_per_comp',
    'total_iowait',
    'read_write',
    'partition_cap',
]

try:
    net_mri_client = InfobloxNetMRI(
        host=os.getenv('NETMRI_HOST'),
        username=os.getenv('NETMRI_USER'),
        password=os.getenv('NETMRI_PASSWORD')
    )
except requests.exceptions.ConnectionError as e:
    print('Could not connect to NetMRI')
    sys.exit()

"""
Docs:
    DataSourceBroker: /netmri/share/api/pythondoc/v3_8_0.DataSourceBroker.html
    DataSource Object Model: /api/3.8/data_sources/model
"""
data_source_broker = net_mri_client.get_broker('DataSource')

"""
Docs:
    PerformanceDataBroker: /netmri/share/api/pythondoc/v3_8_0.PerformanceDataBroker.html
"""
performance_broker = net_mri_client.get_broker('PerformanceData')

# You can generate an API token from the "API Tokens Tab" in the UI
token = os.getenv('INFLUXDB_TOKEN')
org = os.getenv('INFLUXDB_ORG')
bucket = os.getenv('INFLUXDB_BUCKET')

with InfluxDBClient(url=f"http://{os.getenv('INFLUXDB_HOST')}:8086", token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for source in data_source_broker.index():
        for chart_name in chart_names:
            chart = {
                'chart': chart_name,
                'starttime': chart_start_time,
                'endtime': chart_end_time,
                'unit_id': source.DataSourceID
            }
            data = performance_broker.get_chart_data(**chart)
            pprint('##### Collecting ' + chart_name + ' #####')
            for data_point in data:
                point = Point(chart_name)\
                    .tag(chart_name, os.getenv('NETMRI_HOST'))\
                    .field(data_point['metric_name'], float(data_point['metric_value']))\
                    .time(data_point['timestamp'], WritePrecision.S)
                write_api.write(bucket, org, point)
    client.close()
