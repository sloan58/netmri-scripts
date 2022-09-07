# BEGIN-SCRIPT-BLOCK
#
# Script-Filter:
#     true
#
# Script-Timeout: 600
# END-SCRIPT-BLOCK

from infoblox_netmri.easy import NetMRIEasy

defaults = {
    "api_url": api_url,
    "http_username": http_username,
    "http_password": http_password,
    "job_id": job_id,
    "device_id": device_id,
    "batch_id": batch_id,
    "script_login": "false"
}


with NetMRIEasy(**defaults) as easy:
    
    log = {
        'message': '',
        'id': easy.batch_id,
        'jobdetailid': easy.job_id,
        'severity': 'INFO' 
    }

    broker = easy.client.get_broker('DataSource')
    discovery = easy.client.get_broker('DiscoveryStatuses')
    collectors = broker.index()
    
    headers = [
        'Collector',
        'Network Devices',
        'Num Identified',
        'Num Reached',
        'Num Classified',
        'Num Reached Not Classified',
        'Num Processed,Licensed'
    ]

    log.update({'message': ','.join(str(val) for val in headers)})
    easy.broker('Job').log_custom_message(**log)

    for collector in collectors:
        if collector.DataSourceID not in ['0']:
            params = {'UnitID': collector.DataSourceID}
            details = discovery.summary(**params)
            output = [
                collector.DataSourceName,
                details['Networked'],
                details['NumIdentified'],
                details['NumReached'],
                details['NumClassified'],
                details['NumReachedNotClassified'],
                details['NumProcessed'],
                details['Licensed']
            ]
            log.update({'message': ','.join(str(val) for val in output)})
            easy.broker('Job').log_custom_message(**log)
