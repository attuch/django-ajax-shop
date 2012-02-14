from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'first.html'}),
	(r'^purchased/(?P<cartid>\d+)/$', 'e_commerce.views.purchased' ),
)
