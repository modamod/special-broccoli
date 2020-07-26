from invoke import task, Collection


@task
def print_strings(c, strings):
    for string in strings:
        print(string)
