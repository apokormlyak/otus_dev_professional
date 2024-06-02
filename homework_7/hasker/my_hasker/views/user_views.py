from django.core.exceptions import PermissionDenied

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView

from django.shortcuts import redirect
from django.urls import reverse_lazy

from ..forms import LogInForm, SignUpForm, EditForm


# Create your views here.
class NotLoggedInMixin(UserPassesTestMixin):
    request = None

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect("question:home")


class HaskerLoginView(NotLoggedInMixin, LoginView):
    form_class = LogInForm
    next = "home_page"
    template_name = "user/login.html"


class HaskerLogoutView(LoginRequiredMixin, LogoutView):
    next = reverse_lazy("question:home")


class HaskerSignupView(NotLoggedInMixin, CreateView):
    form_class = SignUpForm
    template_name = "user/signup.html"
    success_url = reverse_lazy("user:signup")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация"
        return context


class HaskerUserEditView(LoginRequiredMixin, UpdateView):
    form_class = EditForm
    template_name = "user/signup.html"
    success_url = reverse_lazy("edit")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Настройки"
        return context
