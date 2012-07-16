from django.shortcuts import render_to_response
# import the logging library
from django.views.generic.base import TemplateView
from django.http import Http404

from mywish.api.api import v1
from .models import Wish
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    template_name = 'base2.html'

class DetailView(TemplateView):
    template_name = 'base2.html'

    def get_detail(self, pk):
        tr = v1.canonical_resource_for('wish')

        try:
            wish = tr.cached_obj_get(pk=pk)
        except Wish.DoesNotExist:
            raise Http404

        bundle = tr.full_dehydrate(tr.build_bundle(obj=wish))
        data = bundle.data
        return data

    def get_context_data(self, **kwargs):
        base = super(DetailView, self).get_context_data(**kwargs)
        base['data'] = self.get_detail(base['params']['pk'])
        return base


def home(request):
    return render_to_response('base2.html')

def test1(request):
    return render_to_response('1.html')

def test(request):
    return render_to_response('test.html')