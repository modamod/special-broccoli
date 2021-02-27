#!/usr/bin/env python
''' Module with helper functions '''

import shelve
import time
from contextlib import contextmanager
from functools import partial, wraps
from tempfile import gettempdir
from typing import NoReturn, Sequence, Tuple, Generator

import boto3
import botocore
import sys
from invoke import context


def aws_session(*args: Sequence[str], **kwargs: Sequence[str]) -> boto3.session.Session:
    ''' Helper function to get boto3 session object '''
    return boto3.session.Session(*args, **kwargs)


def duration_to_hms(duration: float) -> Tuple:
    ''' Function that turns number of seconds into Number of hours, minutes and seconds'''
    hours = duration // 3600
    minutes = (duration - hours * 3600) // 60
    seconds = duration - hours * 3600 - minutes * 60
    return hours, minutes, seconds


@contextmanager
def timer(name: str = '') -> NoReturn:
    ''' Timer contextx manager/decorator '''
    sts = ets = diff = 0
    try:
        sts = time.time()
        yield
    finally:
        ets = time.time()
        diff = ets - sts
        hours, minutes, seconds = duration_to_hms(diff)
        print(f'{name} took: {hours:.0f}h:{minutes:.0f}m:{seconds:.2f}s')


def get_value_from_key(items, key):
    ''' Helper function to use with map
        Args:
            items: iteratable that we are going to get the value from
            key: the key used to get its value from the iteratable.
        Returns:
            Object
    '''
    for i in items:
        if i['Key'] == key:
            return i['Value']


def key_value_to_dict(items, key_name='Key', value_name='Value'):
    ''' Helper function to convert {'key_name': key, 'value_name': value} to {key: value} '''
    return {item[key_name]: item[value_name] for item in items}


def cache(func):
    ''' Function decorator to cache function result in disk

        Args:
            func: Callable that the decorator is going to cache its result in disk

        Returns:
            Callable
    '''

    shelf = shelve.open(f'{gettempdir()}/{func.__name__}')
    @wraps(func)
    def inner(*args, **kwargs):
        refresh = False
        if 'refresh' in kwargs:
            refresh = kwargs['refresh']
            del(kwargs['refresh'])
        if repr((args, kwargs)) not in shelf or refresh:
            result = func(*args, **kwargs)
            shelf[repr((args, kwargs))] = result
        else:
            result = shelf[repr((args, kwargs))]
        return result
    return inner


@cache
def get_ec2_instances(*args, **kwargs):
    ''' Helper function to get'''
    session = aws_session(
        profile_name=kwargs['profile_name'], region_name=kwargs['region_name'])
    client = session.client('ec2')
    try:
        paginator = client.get_paginator("describe_instances")
        instances = []
        for page in paginator.paginate(Filters=kwargs['Filters'], InstanceIds=kwargs['InstanceIds']):
            # reservations hold all the instances found with filter provided
            for reservation in page["Reservations"]:
                # each reservation returns an array of instances
                for instance in reservation["Instances"]:
                    instances.append(instance)
    except botocore.exceptions.ClientError as exp:
        print('This is an exception')
        print(exp.operation_name)
        sys.exit(1)
    return instances


def format_ec2_instances(instance):
    result = {
        'InstanceId': instance['InstanceId'],
        'Tags': key_value_to_dict(instance['Tags'])
    }
    return result


@timer(name='Main')
def main():
    time.sleep(1)


def accounts_regions_to_tuple(accounts: str, regions: str) -> Tuple:
    ''' Function to map accounts to regions passed through command line

        Args:
            accounts: comma delimited lists of aws profile names
                exmaple: --acounts stlb,stcs,sthybrid
            regions: semicolon delimited list of comma delimited list to define region for each specified account
                example: --regions "us-east-1;us-east-1,us-east-2-us-west-2;u-east-1,us-east-2,us-west-2;eu-central-1,ap-southeast-2"
    '''
    accounts_region_mapping = dict(zip(map(lambda acc: acc.strip(), accounts.split(
        ',')), map(lambda reg: reg.split(','), regions.split(';'))))
    for key, values in accounts_region_mapping.items():
        for item in values:
            yield (key, item)


def prep_args(contxt: context.Context, accounts: str,
              regions: str, filters: str, refresh: bool) -> Generator:
    ''' Function to perare the arguments for list_all_instances task
        Args:

            contxt: Invoke task context object, needed to invoke the list_instances task
            accounts: comma delimited lists of aws profile names
                exmaple: --acounts stlb,stcs,sthybrid
            regions: semicolon delimited list of comma delimited list to define region for each specified account
                example: --regions "us-east-1;us-east-1,us-east-2-us-west-2;u-east-1,us-east-2,us-west-2;eu-central-1,ap-southeast-2"
            filters: semicolon delimited list of Key=Values pair to define ec2 filters
                example: --filters tag:CostCenter=CloudSuite Corporate Enterprise Edition,CloudSuite HealthCare,CloudSuite Corporate Base;tag:machineLabel=INFORBCMG01
            refresh: Flag to refresh cached values

        Returns:
            Generator
    '''

    for account_region in accounts_regions_to_tuple(accounts, regions):
        yield (contxt, account_region[0], account_region[1], filters, refresh)


if __name__ == "__main__":
    main()
