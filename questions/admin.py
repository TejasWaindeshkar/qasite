# questions/admin.py
from django.contrib import admin
from .models import Question, Answer, Tag, Vote

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ['title', 'author', 'vote_score', 'answer_count', 'created_at']
    list_filter   = ['is_closed', 'tags']
    search_fields = ['title', 'body']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display  = ['author', 'question', 'is_accepted', 'vote_score', 'created_at']
    list_filter   = ['is_accepted']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'usage_count']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'value', 'content_type', 'object_id', 'created_at']