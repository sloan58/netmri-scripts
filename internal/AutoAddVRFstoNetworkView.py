# BEGIN-SCRIPT-BLOCK
#
# Script-Filter:
#     true
#
# Script-Timeout: 600
# Script-Variables:
#     $netmri_username string "NetMRI UserName"
#     $netmri_password password "NetMRI Password"
# END-SCRIPT-BLOCK

from infoblox_netmri.easy import NetMRIEasy
import json
import requests
requests.packages.urllib3.disable_warnings()

# This values will be provided by NetMRI before execution
defaults = {
    "api_url": api_url,
    "http_username": http_username,
    "http_password": http_password,
    "job_id": job_id,
    "device_id": device_id,
    "batch_id": batch_id,
    "script_login" : "false"
}

url = "https://<host>/api/3.8/virtual_networks/current_assigned_virtual_network_members.json?sort=VirtualNetworkMemberName&dir=ASC&VirtualNetworkID=0&VirtualNetworkMemberArtificialInd=false&start=0&limit=100"

response = requests.request("GET", url, auth=(netmri_username, netmri_password), verify=False)

items = json.loads(response.text)

vnm_id = []

# Create NetMRI context manager. It will close session after execution
with NetMRIEasy(**defaults) as easy:
         vnet_broker = easy.broker('VirtualNetwork')
         add_network = vnet_broker.assign_members
         if 'virtual_network_members' in items:
             for item in items['virtual_network_members']:
                 if 'VirtualNetworkMemberID' in item:
                    vnm_id.append(item['VirtualNetworkMemberID'])
                    clean_vnm_id = ",".join(vnm_id)
                    params = {
                        'VirtualNetworkID': 1,
                        'VirtualNetworkMemberID': clean_vnm_id
                    }
                    results = add_network(**params)
