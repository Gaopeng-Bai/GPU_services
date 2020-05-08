#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:**********************************************
# @Time    : 5/8/2020 11:26 AM
# @Author  : Gaopeng.Bai
# @File    : Alibaba_services.py
# @User    : gaop
# @Software: PyCharm
# @Description:
# Reference:**********************************************

import json
import logging
import time
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526.CreateInstanceRequest import CreateInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest

# configuration the log output formatter, if you want to save the output to file,
# append ",filename='ecs_invoke.log'" after datefmt.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S')

clt = client.AcsClient(
    "LTAIxK1dvmGDFYJW",
    "mNiK40Ax5I6A2jK3wF1KO2dExtE8v0",
    "eu-central-1")
IMAGE_ID = 'centos_7_7_x64_20G_alibase_20200329.vhd'
INSTANCE_TYPE = 'ecs.ic5.large'  # 2c2g generation 1
SECURITY_GROUP_ID = 'sg-gw8bx81hi315bdl62nj9'
vswitchid = 'vsw-gw8bq3e90fho9fooo9z5o'
INSTANCE_RUNNING = 'Running'


'''
This part provide functions to create instance of ECS services.
Required parameters. Original api in:
https://www.alibabacloud.com/help/doc-detail/92990.htm?spm=a2c63.p38356.b99.815.1af1498c1ptEPn
'''


def create_instance_action():
    instance_id = create_after_pay_instance(
        image_id=IMAGE_ID,
        instance_type=INSTANCE_TYPE,
        security_group_id=SECURITY_GROUP_ID)
    check_instance_running(instance_id=instance_id)


def create_prepay_instance_action():
    instance_id = create_prepay_instance(
        image_id=IMAGE_ID,
        instance_type=INSTANCE_TYPE,
        security_group_id=SECURITY_GROUP_ID,
        vswitchid=vswitchid)
    check_instance_running(instance_id=instance_id)
    return instance_id


# create one after pay ecs instance.


def create_after_pay_instance(image_id, instance_type, security_group_id, vswitchid):
    """
    :param image_id:      You can use public images or custom images. Image specify a OS and related software packages.
    :param instance_type: The option “one-core 2GiB n1.small” indicates that the input parameter is
                           ecs.n1.small.
    :param security_group_id: Security group ID. A security group is similar to a firewall and uses security group rules
                              to control network access requests of instances.We recommend that you configure access rules
                              only according to the actual needs.
    :return: a instance id.
    """
    request = CreateInstanceRequest()
    request.set_ImageId(image_id)
    request.set_SecurityGroupId(security_group_id)
    request.set_InstanceType(instance_type)
    request.set_IoOptimized('optimized')
    request.set_VSwitchId(vswitchid)
    response = _send_request(request)
    instance_id = response.get('InstanceId')
    logging.info(
        "instance %s created task submit successfully.",
        instance_id)
    return instance_id


# create one prepay ecs instance.


def create_prepay_instance(image_id, instance_type, security_group_id):
    """
        :param image_id:      You can use public images or custom images. Image specify a OS and related software packages.
        :param instance_type: The option “one-core 2GiB n1.small” indicates that the input parameter is
                               ecs.n1.small.
        :param security_group_id: Security group ID. A security group is similar to a firewall and uses security group rules
                                  to control network access requests of instances.We recommend that you configure access rules
                                  only according to the actual needs.
        :return: a instance id.
        """
    request = CreateInstanceRequest()
    request.set_ImageId(image_id)
    request.set_SecurityGroupId(security_group_id)
    request.set_InstanceType(instance_type)
    request.set_IoOptimized('optimized')
    request.set_VSwitchId('vsw-vswitchid')
    request.set_SystemDiskCategory('cloud_ssd')
    request.set_Period(1)
    request.set_InstanceChargeType('PrePaid')
    response = _send_request(request)
    instance_id = response.get('InstanceId')
    logging.info(
        "instance %s created task submit successfully.",
        instance_id)
    return instance_id


def check_instance_running(instance_id):
    """
    The ECS start and stop operations are asynchronous. You can use scripts to create an ECS instance, check its status,
    and perform the required operations. Specifically, the following code:

           1. Checks whether the specified instance is in the Stopped status after obtaining an instance ID.
           2. Calls StartInstance if it is in the Stopped status.
           3. Waits for the instance to change to the Running status.
    :param instance_id:
    :return:
    """
    detail = get_instance_detail_by_id(
        instance_id=instance_id,
        status=INSTANCE_RUNNING)
    index = 0
    while detail is None and index < 60:
        detail = get_instance_detail_by_id(instance_id=instance_id)
        time.sleep(10)
    if detail and detail.get('Status') == 'Stopped':
        logging.info("instance %s is stopped now.")
        start_instance(instance_id=instance_id)
        logging.info("start instance %s job submit.")
    detail = get_instance_detail_by_id(
        instance_id=instance_id,
        status=INSTANCE_RUNNING)
    while detail is None and index < 60:
        detail = get_instance_detail_by_id(
            instance_id=instance_id, status=INSTANCE_RUNNING)
        time.sleep(10)
    logging.info("instance %s is running now.", instance_id)
    return instance_id


def start_instance(instance_id):
    request = StartInstanceRequest()
    request.set_InstanceId(instance_id)
    _send_request(request)


# output the instance owned in current region.


def get_instance_detail_by_id(instance_id, status='Stopped'):
    logging.info("Check instance %s status is %s", instance_id, status)
    request = DescribeInstancesRequest()
    request.set_InstanceIds(json.dumps([instance_id]))
    response = _send_request(request)
    instance_detail = None
    if response is not None:
        instance_list = response.get('Instances').get('Instance')
        for item in instance_list:
            if item.get('Status') == status:
                instance_detail = item
                break
        return instance_detail


'''
Release a instance api, For more details:
https://www.alibabacloud.com/help/doc-detail/93110.htm?spm=a2c63.p38356.b99.817.69981493e2gwCF
'''


def stop_instance(instance_id, force_stop=False):
    """
    stop one ecs instance.
    :param instance_id: instance id of the ecs instance, like 'i-***'.
    :param force_stop: if force stop is true, it will force stop the server and not ensure the data
    write to disk correctly.
    :return:
    """
    request = StopInstanceRequest()
    request.set_InstanceId(instance_id)
    request.set_ForceStop(force_stop)
    logging.info("Stop %s command submit successfully.", instance_id)
    _send_request(request)


def describe_instance_detail(instance_id):
    """
    describe instance detail
    :param instance_id: instance id of the ecs instance, like 'i-***'.
    :return:
    """
    request = DescribeInstancesRequest()
    request.set_InstanceIds(json.dumps([instance_id]))
    response = _send_request(request)
    if response is not None:
        instance_list = response.get('Instances').get('Instance')
        if len(instance_list) > 0:
            return instance_list[0]


def check_auto_release_time_ready(instance_id):
    detail = describe_instance_detail(instance_id=instance_id)
    if detail is not None:
        release_time = detail.get('AutoReleaseTime')
        return release_time


def release_instance(instance_id, force=False):
    """
    delete instance according instance id, only support after pay instance.
    :param instance_id: instance id of the ecs instance, like 'i-***'.
    :param force:
    if force is false, you need to make the ecs instance stopped, you can
    execute the delete action.
    If force is true, you can delete the instance even the instance is running.
    :return:
    """
    request = DeleteInstanceRequest()
    request.set_InstanceId(instance_id)
    request.set_Force(force)
    _send_request(request)


def set_instance_auto_release_time(instance_id, time_to_release=None):
    """
    setting instance auto delete time
    :param instance_id: instance id of the ecs instance, like 'i-***'.
    :param time_to_release: if the property is setting, such as '2017-01-30T00:00:00Z'
    it means setting the instance to be release at that time.
    if the property is None, it means cancel the auto delete time.
    :return:
    """
    request = ModifyInstanceAutoReleaseTimeRequest()
    request.set_InstanceId(instance_id)
    if time_to_release is not None:
        request.set_AutoReleaseTime(time_to_release)
    _send_request(request)
    release_time = check_auto_release_time_ready(instance_id)
    logging.info(
        "Check instance %s auto release time setting is %s. ",
        instance_id,
        release_time)

# send open api request


def _send_request(request):
    request.set_accept_format('json')
    try:
        response_str = clt.do_action(request)
        logging.info(response_str)
        response_detail = json.loads(response_str)
        return response_detail
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    logging.info("Create ECS by OpenApi!")
    # create_instance_action()
    instance_id = create_prepay_instance_action()
    stop_instance(instance_id)
    release_instance(instance_id)
