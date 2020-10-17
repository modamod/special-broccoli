#!/usr/bin/env python
''' Module with helper functions '''

import shelve
import time
from contextlib import ContextDecorator
from functools import partial, wraps
from tempfile import gettempdir

import boto3
import botocore


def aws_session(*args, **kwargs):
    return boto3.session.Session(*args, **kwargs)


class Timer(ContextDecorator):
    ''' Context decorator to compute how much it took to execute a function '''
    def __init__(self, func):
        ''' Initializing Timer object '''
        self.name = 'name'
        self.start_time = 0
        self.duration = 0
        self.func = func
    def __enter__(self):
        ''' Overriding context manger enter method '''
        print(f'Starting {self.name}')
        self.start_time = time.time()
        return self
    def __exit__(self, *exp):
        ''' Overriding context manager exit function '''
        self.duration = time.time() - self.start_time
        hours, minutes, seconds = self.duration_to_hms()
        print(f'{self.name} took: {hours:.0f}h:{minutes:.0f}m:{seconds:.2f}s'.strip())
        return False

    def duration_to_hms(self):
        ''' Function that turns number of seconds into Number of hours, minutes and seconds'''
        hours = self.duration // 3600 if self.duration else 0
        minutes = (self.duration - hours * 3600) // 60 if self.duration else 0
        seconds = self.duration - hours * 3600 - minutes * 60 if self.duration else 0
        return hours, minutes, seconds


def get_value_from_key(items, key):
    ''' Helper function to use with map '''
    for i in items:
        if i['Key'] == key:
            return i['Value']


def key_value_to_dict(items, key_name='Key', value_name='Value'):
    ''' Helper function to convert {'key_name': key, 'value_name': value} to {key: value} '''
    return {item[key_name]: item[value_name] for item in items}


def cache(func):
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
    session = aws_session(profile_name=kwargs['profile_name'], region_name=kwargs['region_name'])
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
    except botocore.exceptions.ClientError as e:
        print('This is an exception')
        print(e.operation_name)
        exit(1)
    return instances

def format_ec2_instances(instance):
    result = {
        'InstanceId': instance['InstanceId'],
        'Tags': key_value_to_dict(instance['Tags'])
    }
    return result

@Timer
def main():
    time.sleep(1)


if __name__ == "__main__":
    main()
