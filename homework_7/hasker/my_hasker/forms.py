from .models import User, Question, Answer
from django.forms import ModelForm, SlugField
from django.urls import reverse_lazy

import re
from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
)


class LogInForm(AuthenticationForm):
    pass


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("nickname", "email", "password", "avatar")


class EditForm(ModelForm):
    username = SlugField(disabled=True)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_action = reverse_lazy("edit")
    helper.add_input(
        Submit('edit', 'Изменить', css_class='btn-primary')
    )


class SettingsForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "avatar")


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("answer_text",)


class AskForm(forms.ModelForm):
    tags = forms.CharField(max_length=512, required=False)

    class Meta:
        model = Question
        fields = ("question_text", "title")

    def clean_tags(self):
        raw_tags = self.cleaned_data["tags"]
        raw_tags, _ = re.subn(r"\s+", " ", raw_tags)

        tags = (tag.strip().lower() for tag in raw_tags.split(","))
        tags = set(filter(bool, tags))

        if len(tags) > settings.QUESTIONS_MAX_NUMBER_OF_TAGS:
            n = settings.QUESTIONS_MAX_NUMBER_OF_TAGS
            raise forms.ValidationError(f"The maximum number of tags is {n}.")

        if any(len(tag) > settings.QUESTIONS_MAX_TAG_LEN for tag in tags):
            raise forms.ValidationError(
                "Ensure each tag has at most 128 characters."
            )

        return sorted(tags)