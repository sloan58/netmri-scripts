# BEGIN-SCRIPT-BLOCK
#
# Script-Filter:
#     $ipaddress == <OC_IP>
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
    "batch_id": batch_id
}

oc_commands = [
    'show disk',
    'show io',
    'show memory',
    'show virtual'
]

with NetMRIEasy(**defaults) as easy:

    logger = easy.broker('Job')

    log_meta = {
        'id': easy.batch_id,
        'jobdetailid': easy.job_id,
        'severity': 'INFO'
    }

    for oc_command in oc_commands:
        logger.log_custom_message(
            **log_meta,
            message=f'######## Begin {device_devicename}: {oc_command} ########\n'
        )
        output = easy.send_command(oc_command)
        logger.log_custom_message(**log_meta, message=output)

        logger.log_custom_message(
            **log_meta,
            message=f'\n######## End {device_devicename}: {oc_command} ########\n'
        )
