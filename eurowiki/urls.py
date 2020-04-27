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
from django.conf.urls import url
from eurowiki import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.list_namespaces, name='homepage'),

    url(r'^named_graph/(?P<namespace_id>[\d-]+)/$', views.view_named_graph, name='named_graph'),
    url(r'^named_graph/new/$', views.editNamedGraph.as_view(), name='named_graph_new'),
    url(r'^named_graph/(?P<named_graph_id>[\d-]+)/edit/$', views.editNamedGraph.as_view(), name='named_graph_edit'),

    url(r'^namespaces/$', views.list_namespaces, name='list_namespaces'),
    url(r'^namespace/(?P<namespace_id>[\d-]+)/$', views.view_namespace_model, name='namespace_model'),
    url(r'^namespace/new/$', views.editNamespaceModel.as_view(), name='namespace_model_new'),
    url(r'^namespace/(?P<namespace_id>[\d-]+)/edit/$', views.editNamespaceModel.as_view(), name='namespace_model_edit'),

    url(r'^uri_statement/(?P<statement_id>[\d-]+)/$', views.view_uri_statement, name='uri_statement'),
    url(r'^uri_statement/new/$', views.editURIStatement.as_view(), name='uri_statement_new'),
    url(r'^uri_statement/(?P<statement_id>[\d-]+)/edit/$', views.editURIStatement.as_view(), name='uri_statement_edit'),

    url(r'^literal_statement/(?P<statement_id>[\d-]+)/$', views.view_literal_statement, name='literal_statement'),
    url(r'^literal_statement/new/$', views.editLiteralStatement.as_view(), name='literal_statement_new'),
    url(r'^literal_statement/(?P<statement_id>[\d-]+)/edit/$', views.editLiteralStatement.as_view(), name='literal_statement_edit'),
]
