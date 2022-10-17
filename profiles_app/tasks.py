from celery import shared_task


@shared_task
def profiles_hello_world():
    print('Hello, Profiles!')
