# questions/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Question, Answer, Tag, Vote
from .forms import QuestionForm, AnswerForm
from django.core.mail import send_mail
from django.conf import settings as django_settings

# ─────────────────────────────────────────
# QUESTION LIST — homepage
# ─────────────────────────────────────────
def question_list(request):
    questions = Question.objects.select_related('author').prefetch_related('tags')

    # search
    query = request.GET.get('q', '')
    if query:
        questions = questions.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )

    # tag filter
    tag_slug   = request.GET.get('tag', '')
    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        questions  = questions.filter(tags=active_tag)

    # ordering
    order = request.GET.get('order', 'newest')
    if order == 'votes':
        questions = questions.order_by('-vote_score', '-created_at')
    elif order == 'unanswered':
        questions = questions.filter(answer_count=0).order_by('-created_at')
    else:
        questions = questions.order_by('-created_at')

    # ✅ pagination — 10 questions per page
    paginator = Paginator(questions, 10)
    page      = request.GET.get('page', 1)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    popular_tags = Tag.objects.order_by('-usage_count')[:15]

    return render(request, 'questions/list.html', {
        'questions'   : questions,
        'query'       : query,
        'active_tag'  : active_tag,
        'order'       : order,
        'popular_tags': popular_tags,
        'paginator'   : paginator,
    })

# ─────────────────────────────────────────
# QUESTION DETAIL
# ─────────────────────────────────────────
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers  = question.answers.select_related('author').order_by('-is_accepted', '-vote_score', 'created_at')
    form     = AnswerForm()

    # get user's existing votes
    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(
            user=request.user,
            content_type__in=['question', 'answer']
        )
        for v in votes:
            user_votes[f"{v.content_type}_{v.object_id}"] = v.value

    return render(request, 'questions/detail.html', {
        'question'  : question,
        'answers'   : answers,
        'form'      : form,
        'user_votes': user_votes,
    })


# ─────────────────────────────────────────
# ASK QUESTION
# ─────────────────────────────────────────
@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            messages.success(request, "Question posted successfully!")
            return redirect('question_detail', pk=question.pk)
    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'form': form})


# ─────────────────────────────────────────
# POST ANSWER
# ─────────────────────────────────────────

@login_required
def post_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer          = form.save(commit=False)
            answer.author   = request.user
            answer.question = question
            answer.save()

            # update answer count
            question.answer_count = question.answers.count()
            question.save()

            # ✅ email notification to question author
            if question.author.email and question.author != request.user:
                try:
                    send_mail(
                        subject=f'New answer on: {question.title}',
                        message=f'Hi {question.author.username},\n\n'
                                f'{request.user.username} answered your question:\n'
                                f'"{question.title}"\n\n'
                                f'View it here: http://127.0.0.1:8000/question/{question.pk}/\n\n'
                                f'— QASite',
                        from_email='noreply@qasite.com',
                        recipient_list=[question.author.email],
                        fail_silently=True,   # don't crash if email fails
                    )
                except Exception:
                    pass

            messages.success(request, "Answer posted!")
            return redirect('question_detail', pk=pk)

    return redirect('question_detail', pk=pk)


# ─────────────────────────────────────────
# VOTE — AJAX
# ─────────────────────────────────────────
@login_required
def vote(request, content_type, object_id, value):
    if content_type not in ['question', 'answer']:
        return JsonResponse({'error': 'Invalid type'}, status=400)

    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid value'}, status=400)

    if content_type == 'question':
        obj = get_object_or_404(Question, pk=object_id)
    else:
        obj = get_object_or_404(Answer, pk=object_id)

    # can't vote on your own post
    if obj.author == request.user:
        return JsonResponse({'error': "Can't vote on your own post"}, status=403)

    existing = Vote.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=object_id
    ).first()

    rep_change = 0

    if existing:
        if existing.value == value:
            # remove vote
            existing.delete()
            obj.vote_score -= value
            rep_change      = -5 if value == 1 else 5
        else:
            # change vote direction
            obj.vote_score -= existing.value
            rep_change      = 10 if value == 1 else -10
            existing.value  = value
            existing.save()
            obj.vote_score += value
    else:
        Vote.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            value=value
        )
        obj.vote_score += value
        rep_change      = 5 if value == 1 else -2

    obj.save()

    # ✅ update author reputation
    if rep_change != 0:
        try:
            profile = obj.author.profile
            profile.reputation = max(0, profile.reputation + rep_change)
            profile.save()
        except Exception:
            pass

    return JsonResponse({'vote_score': obj.vote_score})


# ─────────────────────────────────────────
# ACCEPT ANSWER
# ─────────────────────────────────────────
@login_required
def accept_answer(request, pk):
    answer   = get_object_or_404(Answer, pk=pk)
    question = answer.question

    # only question author can accept
    if request.user != question.author:
        messages.error(request, "Only the question author can accept an answer.")
        return redirect('question_detail', pk=question.pk)

    # toggle — if already accepted, unaccept
    if answer.is_accepted:
        answer.is_accepted = False
        answer.save()
    else:
        # unaccept all other answers first
        question.answers.update(is_accepted=False)
        answer.is_accepted = True
        answer.save()

        # give reputation to answer author
        if answer.author != request.user:
            profile = answer.author.profile
            profile.reputation += 15
            profile.save()

    return redirect('question_detail', pk=question.pk)