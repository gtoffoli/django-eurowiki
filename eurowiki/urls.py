"""eurowiki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from . import views # search_indexes

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^tinymce/', include('tinymce.urls')),
    # url(r'^navigation_autocomplete$', search_indexes.navigation_autocomplete, name='navigation_autocomplete'),
    url(r'^$', views.homepage, name='homepage'),
    url(r'^search/$', views.search, name='search'),
    
    url(r'^statements/$', views.list_statements, name='list_statements'),
    url(r'^uri_statements/$', views.list_uri_statements, name='list_uri_statements'),
    url(r'^uri_statement/(?P<statement_id>[\d-]+)/$', views.view_uri_statement, name='uri_statement'),
    url(r'^literal_statements/$', views.list_literal_statements, name='list_literal_statements'),
    url(r'^literal_statement/(?P<statement_id>[\d-]+)/$', views.view_literal_statement, name='literal_statement'),

     url(r'^country/(?P<item_code>\w[\d]+)/$', views.view_country, name='view_country'),
     #url(r'^countries/compare/$', views.compare_countries, name='compare_countries'),
     url(r'^countries/view/$', views.view_countries, name='view_countries'),
     url(r'^item/(?P<item_code>[\w\d]+)/$', views.view_item, name='view_item'),
     url(r'^item/(?P<item_code>[\w\d]+)/edit/$', views.edit_item, name='edit_item'),

    url(r'^statement/(?P<subject_id>[\w\d]+)/new/$', views.editStatement.as_view(), name='statement_new'),
    url(r'^statement/(?P<statement_id>[\d-]+)/edit/$', views.editStatement.as_view(), name='statement_edit'),
]
