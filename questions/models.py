# questions/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# ─────────────────────────────────────────
# TAG MODEL
# ─────────────────────────────────────────
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # auto-generate slug from name (e.g. "Python 3" → "python-3")
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ─────────────────────────────────────────
# QUESTION MODEL
# ─────────────────────────────────────────
class Question(models.Model):
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title       = models.CharField(max_length=255)
    body        = models.TextField()
    tags        = models.ManyToManyField(Tag, blank=True, related_name='questions')
    vote_score  = models.IntegerField(default=0)
    answer_count= models.PositiveIntegerField(default=0)
    is_closed   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']   # newest first by default


# ─────────────────────────────────────────
# ANSWER MODEL
# ─────────────────────────────────────────
class Answer(models.Model):
    question    = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    body        = models.TextField()
    is_accepted = models.BooleanField(default=False)
    vote_score  = models.IntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Answer by {self.author.username} on '{self.question.title}'"

    class Meta:
        ordering = ['-is_accepted', '-vote_score', 'created_at']
        # accepted answer first, then highest voted, then oldest


# ─────────────────────────────────────────
# VOTE MODEL  (works for both Q and A)
# ─────────────────────────────────────────
class Vote(models.Model):
    UPVOTE   = 1
    DOWNVOTE = -1
    VOTE_CHOICES = [(UPVOTE, 'Upvote'), (DOWNVOTE, 'Downvote')]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    value        = models.SmallIntegerField(choices=VOTE_CHOICES)

    # Generic FK — can point to Question OR Answer
    content_type = models.CharField(max_length=20, choices=[('question','Question'),('answer','Answer')])
    object_id    = models.PositiveIntegerField()

    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {'↑' if self.value == 1 else '↓'} {self.content_type} #{self.object_id}"

    class Meta:
        # one vote per user per object — no duplicate votes!
        unique_together = ['user', 'content_type', 'object_id']