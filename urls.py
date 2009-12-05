from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^bajar_de_peso/', include('bajar_de_peso.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^$', 'bajarpeso.views.main'),
    #(r'^home/$', 'django.views.generic.simple.direct_to_template', {'template': 'homepage.html'}),
    (r'^settings/$', 'bajarpeso.views.edit_settings'),
    (r'^get_chart_data/$', 'bajarpeso.views.get_chart_data'),
)
