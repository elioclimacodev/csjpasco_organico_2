from django.urls import path

from .views import index, signup

app_name = 'main'
urlpatterns = [
    path('', index, name='index'),
    path('signup/', signup, name='signup'),
]
