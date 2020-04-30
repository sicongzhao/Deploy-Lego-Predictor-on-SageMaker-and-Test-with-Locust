from locust import HttpLocust, TaskSet, between

def index(l):
    l.client.get("https://q8fq0393vf.execute-api.us-east-2.amazonaws.com/test1/whichbrick")

class UserBehavior(TaskSet):
    tasks = {index: 1}

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
