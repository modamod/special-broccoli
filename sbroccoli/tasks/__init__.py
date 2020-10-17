from invoke import Collection
from . import utils, aws

ns = Collection()
ns.add_collection(ns.from_module(utils))
ns.add_collection(ns.from_module(aws))
