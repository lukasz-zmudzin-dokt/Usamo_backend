from django.urls import path, re_path
from .views import *

app_name = 'chat'
urlpatterns = [
    path("", InboxView.as_view()),
    path("contacts/", ContactListView.as_view()),
    re_path(r"^(?P<username>\S+)/$", ThreadView.as_view())
]