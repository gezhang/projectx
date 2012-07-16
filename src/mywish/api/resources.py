from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

from mywish.models import Tweet
from mywish.models import Wish

class TweetResource(ModelResource):
    class Meta:
        queryset = Tweet.objects.all()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get']
        always_return_data = True
        
class WishResource(ModelResource):
    class Meta:
        queryset = Wish.objects.all()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get']
        always_return_data = True