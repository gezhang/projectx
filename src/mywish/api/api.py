from tastypie.api import Api
from mywish.api.resources import TweetResource
from mywish.api.resources import WishResource

v1 = Api("v1")
v1.register(TweetResource())
v1.register(WishResource())

def determine_format(self, request): 
    return "application/json"