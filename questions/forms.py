# questions/forms.py
from django import forms
from .models import Question, Answer, Tag


class QuestionForm(forms.ModelForm):
    # custom tag input — user types comma separated tags
    tags = forms.CharField(
        max_length=200,
        required=False,
        help_text='Enter tags separated by commas. e.g. python, django, mysql',
        widget=forms.TextInput(attrs={'placeholder': 'python, django, mysql'})
    )

    class Meta:
        model  = Question
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'What is your question? Be specific.'
            }),
            'body': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Describe your problem in detail...'
            }),
        }

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()
            # handle tags
            tag_names = self.cleaned_data.get('tags', '')
            if tag_names:
                question.tags.clear()
                for name in tag_names.split(','):
                    name = name.strip().lower()
                    if name:
                        tag, created = Tag.objects.get_or_create(name=name)
                        if created:
                            tag.slug = name.replace(' ', '-')
                            tag.save()
                        tag.usage_count += 1
                        tag.save()
                        question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model  = Answer
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write your answer here...'
            })
        }
        labels = {
            'body': 'Your Answer'
        }