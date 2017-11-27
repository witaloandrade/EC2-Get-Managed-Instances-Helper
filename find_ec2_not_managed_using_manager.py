"""
Find EC2 instances not using ssm (used for EC2 systems manager helper)

An alternative to this script, is to use AWS CLI commands:

- Gets all running instances
    - `aws ec2 describe-instances -query 'Reservations[*].Instances[*].[Placement.AvailabilityZone, State.Name, InstanceId]' --output json
    `
- Gets ssm managed instances
    - `aws ssm describe-instance-information --output json --query "InstanceInformationList[*]`

Then compare the instance ID's returned.

Setup:
    This .py script assumes the users AWS credentials have been setup and
    the virtualenv has boto3 installed.

Assumptions:
    This script assumes ec2 instances managed by ssm are controlled by the
    EC2 systems manager


Usage:  python3 find_ec2_not_managed_using_manager.py
Author: Carl Kenny
"""

import boto3
from pprint import pprint


def get_all_ec2_instances_list():
    """
    :return: list of all ec2 instances connected to account
    """
    print("++ get_all_ec2_instances_list")

    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()

    all_reservations = response["Reservations"]
    all_instance_ids = []

    for reserveration in all_reservations:
        instances = reserveration["Instances"]
        for instance in instances:
            all_instance_ids.append(instance["InstanceId"])

    print("-- get_all_ec2_instances_list")
    return all_instance_ids


def get_managed_by_ssm_instances_list():
    """
    Here we assume ec2 instances managed by ssm are controlled by the
    EC2 systems manager
    :return: list of ec2 instances managed by ssm
    """
    print("++ get_managed_by_ssm_instances_list")

    # find only instances with ssm enabled (managed)
    ssm = boto3.client('ssm')
    ssm_managed = ssm.describe_instance_information()
    ssm_managed_list = ssm_managed["InstanceInformationList"]

    ssm_managed_instance_ids = []

    for instance in ssm_managed_list:
        ssm_managed_instance_ids.append(instance["InstanceId"])

    print("-- get_managed_by_ssm_instances_list")
    return ssm_managed_instance_ids


def get_unmanaged_ec2_instances():
    """
    Using boto3 API, find ec2 instances not managed
    """
    all_instance_ids = get_all_ec2_instances_list()
    print("All instance Id's: {}".format(all_instance_ids))

    ssm_managed_instance_ids = get_managed_by_ssm_instances_list()
    print("SSM managed instances: {}".format(ssm_managed_instance_ids))

    instances_not_managed = list(set(all_instance_ids).difference(ssm_managed_instance_ids))
    print("Instances not managed by ssm: {}".format(instances_not_managed))


if __name__ == "__main__":
    get_unmanaged_ec2_instances()
