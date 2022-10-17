import sys

import requests
from infoblox_netmri.client import InfobloxNetMRI

try:
    net_mri_client = InfobloxNetMRI(host="",
                                        username="",
                                        password="",
                                        use_ssl=False)
except requests.exceptions.ConnectionError as e:
    print(e)
    sys.exit()

try:
    response = net_mri_client.api_request('scripts/index', {})
except requests.exceptions.HTTPError as e:
    sys.exit()

for script in response['scripts']:
    print(script)
