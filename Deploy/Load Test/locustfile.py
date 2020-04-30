from locust import HttpLocust, TaskSet, between

def index(l):
    l.client.get("https://q8fq0393vf.execute-api.us-east-2.amazonaws.com/test1/whichbrick")

class UserBehavior(TaskSet):
    tasks = {index: 1}

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
    
# Multihosts example, but not working with multihosts    
# import os

# from locust import HttpUser, TaskSet, task, between
# from locust.clients import HttpSession

# host1 = 'https://q8fq0393vf.execute-api.us-east-2.amazonaws.com/test1/whichbrick'
# host2 = 'https://q8fq0393vf.execute-api.us-east-2.amazonaws.com/test1/secondapi'

# class MultipleHostsUser(HttpUser):
#     abstract = True
    
#     def __init__(self, *args, **kwargs):
#         super(MultipleHostsUser, self).__init__(*args, **kwargs)
#         self.api_client = HttpSession(base_url=os.environ["API_HOST"])
    

# class UserTasks(TaskSet):
#     # but it might be convenient to use the @task decorator
#     @task
#     def index(self):
#         self.user.client.get(host1)
    
#     @task
#     def index_other_host(self):
#         self.user.api_client.get(host2)
    
# class WebsiteUser(MultipleHostsUser):
#     """
#     User class that does requests to the locust web server running on localhost
#     """
#     host = "http://127.0.0.1:8089"
#     wait_time = between(2, 5)
#     tasks = [UserTasks]