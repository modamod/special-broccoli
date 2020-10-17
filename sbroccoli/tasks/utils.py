from invoke import task, Collection
from tempfile import gettempdir
import os
import zipfile
from pathlib import Path

@task
def print_strings(c, strings):
    for string in strings:
        print(string)


@task
def zipdir(c, path, destination, compresslevel=1, override=True):
    ''' Zips path and save it to destination zipfile'''
    mode = 'w' if not zipfile.is_zipfile(destination) or override else 'a'
    ziph = zipfile.ZipFile(destination, mode, zipfile.ZIP_DEFLATED, compresslevel=compresslevel)
    for root, _, files in os.walk(path):
        for file_ in files:
            print(root)
            ziph.write(os.path.join(root, file_))
    ziph.close()


@task
def build_lambda_zip(c, lambda_name, code_path, zip_path):
    ''' Task to zip lambda code and its dependencies '''
    with c.cd(code_path):

        c.run(f'pip install -r requirements.txt --target ./package')
        with c.cd(f'./package'):
            c.run(f'zip -r9 /tmp/function.zip .')
