# file: code/repo.py

from dagster import job, op, repository

@op
def hello_op():
    return "Hello, Dagster!"

@job
def hello_job():
    hello_op()

@repository
def my_repo():
    return [hello_job]
