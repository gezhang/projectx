from django.conf.urls.defaults import patterns, include, url
import settings
from mywish.api.api import v1
from .views import IndexView, DetailView

urlpatterns = patterns('',
    (r'^accounts/', include('mywish.accounts.urls')),
)

urlpatterns += patterns('',
    url(r'^$',
        IndexView.as_view(),
        name='home'),

    url(r'^(?P<pk>\d+)/$',
        DetailView.as_view(),
        name="detail"),

    url(r'^api/', include(v1.urls)),

    url(r'^test1$', 'mywish.views.test1', name='home'),
    url(r'^test$', 'mywish.views.test'),
)

#if settings.DEBUG:
urlpatterns += patterns('',
    (r'^mymedia/(?P<path>.*)$', 'django.views.static.serve',  
     {'document_root': settings.MEDIA_ROOT}),
    (r'^mystatic/(?P<path>.*)$', 'django.views.static.serve',  
     {'document_root': settings.STATIC_ROOT}),
)