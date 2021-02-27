#!/usr/bin/env python
''' AWS invoke tasks module '''

from invoke import task, Collection
from sbroccoli.helper import get_ec2_instances, format_ec2_instances, timer, prep_args
from tempfile import gettempdir
import yaml
from pprint import pprint
from pathlib import Path
from multiprocessing import Manager, Pool


@task(help={
    'aws_profile': 'AWS Profile name used in aws config file',
    'region': 'AWS region name',
    'filters': 'AWS compatible filter list of dicts'
}
)
def list_instances(c, aws_profile, region, filters=[], instance_ids=[], write_to_file=False, refresh=False):
    ''' Invoke task to list all instances in account and region with filters '''
    @timer(name='Getting EC2 instances')
    def inner():
        result = get_ec2_instances(profile_name=aws_profile, region_name=region,
                                   Filters=filters, InstanceIds=instance_ids, refresh=refresh)
        if write_to_file:
            output_file_path = Path(f'{gettempdir()}/{aws_profile}/{region}/instances.yaml')
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            output_file = open(output_file_path, 'w')
            yaml.dump(result, output_file)
            print(f'output file: {output_file.name}')
        else:
            pprint(list(map(format_ec2_instances, result)))
        return result
    inner()


@task(help={
    'accounts': 'comma delimited lists of aws profile names\
                exmaple: --acounts stlb,stcs,sthybrid',
    'regions': 'semicolon delimited list of comma delimited list to define region for each specified account\
                example: --regions "us-east-1;us-east-1,us-east-2-us-west-2;u-east-1,us-east-2,us-west-2;eu-central-1,ap-southeast-2"',
    'filters': 'semicolon delimited list of Key=Values pair to define ec2 filters\
                example: --filters tag:CostCenter=CloudSuite Corporate Enterprise Edition,CloudSuite HealthCare,CloudSuite Corporate Base;tag:machineLabel=INFORBCMG01',
    'refresh': 'Flag to refresh cached values'
}
)
def list_all_instances(c, accounts, regions, filters=[], refresh=False):
    ''' List all instances in specified account/regions mapping '''
    print(tuple(prep_args(c, accounts, regions, filters, refresh)))
