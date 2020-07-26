from invoke import task, Collection


@task
def list_instances(c, aws_profile, region, filters=[]):
    print(aws_profile, region)

