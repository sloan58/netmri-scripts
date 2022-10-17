import sys

import requests
from infoblox_netmri.client import InfobloxNetMRI

try:
    # Source NetMRI System
    net_mri_client_src = InfobloxNetMRI(host="",
                                        username="",
                                        password="",
                                        use_ssl=False)

    # Destination NetMRI System
    net_mri_client_dst = InfobloxNetMRI(host="",
                                        username="",
                                        password="",
                                        use_ssl=False)
except requests.exceptions.ConnectionError as e:
    print(e)
    sys.exit()

try:
    scr_scripts = net_mri_client_src.api_request('scripts/index', {})
except requests.exceptions.HTTPError as e:
    sys.exit()

try:
    dst_scripts = net_mri_client_dst.api_request('scripts/index', {})
except requests.exceptions.HTTPError as e:
    sys.exit()


src_names = list(map(lambda script_item: script_item['name'], scr_scripts['scripts']))
dst_names = list(map(lambda script_item: script_item['name'], dst_scripts['scripts']))

for script in src_names:
    if script not in dst_names:
        print(f'{script} not found in destination')

