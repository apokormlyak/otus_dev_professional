from django.shortcuts import redirect, get_object_or_404
from rest_framework import generics
from .. import serializers
from django.db.models import Q, F, Count
from django.urls import resolve
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

from ..models import User, Question, Answer, Tags
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import AskForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseForbidden
)

import logging

logger = logging.getLogger(__name__)

PAGINATE_ANSWERS = 30
PAGINATE_QUESTIONS = 20


def add_tag(request):
    tag_val = request.GET.get('tag', None)
    tag_val = tag_val.lower()
    new_tag = Tags.objects.get_or_create(name=tag_val)
    return HttpResponse(new_tag[0].name)


def choose_correct_answer(request, a_id):
    try:
        answer = Answer.objects.get(pk=a_id)
    except (ObjectDoesNotExist,):
        return HttpResponseBadRequest()

    answer.question.correct_answer = answer
    answer.question.save()

    return redirect(answer.question.url)


class IndexQuestionListView(generics.ListAPIView):
    serializer_class = serializers.QuestionListSerializer
    queryset = Question.objects.all()


class QuestionList(ListView):
    context_object_name = 'questions'
    template_name = "question/list.html"

    title = ""
    search_phrase = ""
    tag_name = ""
    sort_by_date = False
    paginate_by = PAGINATE_QUESTIONS

    def get_queryset(self):
        return Question.objects.all()


class QuestionAddView(LoginRequiredMixin, CreateView):
    form_class = AskForm

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить вопрос"
        return context