import os
import sys
from pprint import pprint

import requests
from dotenv import load_dotenv
from infoblox_netmri import InfobloxNetMRI

load_dotenv()

chart_start_time = '2022-09-07'  # Begin time for chart data
chart_end_time = '2022-09-08'    # Begin time for chart data

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

for source in data_source_broker.index():
    for chart_name in chart_names:
        chart = {
            'chart': chart_name,
            'starttime': chart_start_time,
            'endtime': chart_end_time,
            'unit_id': source.DataSourceID
        }
        data = performance_broker.get_chart_data(**chart)
        pprint('##### ' + chart_name + ' #####')
        pprint(data)
