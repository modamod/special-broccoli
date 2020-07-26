from invoke import Collection, Program
from sbroccoli import tasks


program = Program(namespace=Collection.from_module(tasks), version='0.1.0')