# questions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                                          views.question_list,  name='question_list'),
    path('ask/',                                      views.ask_question,   name='ask_question'),
    path('question/<int:pk>/',                        views.question_detail,name='question_detail'),
    path('question/<int:pk>/answer/',                 views.post_answer,    name='post_answer'),
    path('question/<int:pk>/accept/<int:answer_pk>/', views.accept_answer,  name='accept_answer'),
    path('vote/<str:content_type>/<int:object_id>/<int:value>/', views.vote, name='vote'),
    path('answer/<int:pk>/accept/', views.accept_answer, name='accept_answer'),
]