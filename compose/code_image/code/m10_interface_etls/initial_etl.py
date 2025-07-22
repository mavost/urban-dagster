from dagster import job, op, repository

@op
def hello_op():
    return "Hello, Dagster!"

@job(name="hello_job", tags={"module": "m10_interface_etls"})
def hello_job():
    hello_op()
