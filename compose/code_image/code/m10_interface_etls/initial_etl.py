from dagster import job, op, repository

@op
def hello_op():
    return "Hello, Dagster!"

@job
def m10_hello_job():
    hello_op()
