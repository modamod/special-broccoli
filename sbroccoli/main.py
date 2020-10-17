from invoke import Collection, Program
from sbroccoli.tasks import aws,utils


ns = Collection()
ns.add_collection(ns.from_module(utils), name='util')
ns.add_collection(ns.from_module(aws), name='aws')

program = Program(namespace=ns, version='0.1.0')
