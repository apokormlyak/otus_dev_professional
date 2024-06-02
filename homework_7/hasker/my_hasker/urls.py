from django.urls import path

from .views import views, user_views

urlpatterns = [
    path("add/", views.add_tag, name="add"),
    path(
            "",
            views.QuestionList.as_view(
                sort_by_date=True, title="Главная"
            ),
            name="home"
        ),
    path(
        "search/",
        views.QuestionList.as_view(),
        name="search_results"
    ),
    path("<str:name>/", views.QuestionList.as_view(), name="detail"),
    path("ask/", views.QuestionAddView.as_view(), name="add"),
    path("login/", user_views.HaskerLoginView.as_view(), name="login"),
    path("signup/", user_views.HaskerSignupView.as_view(), name="signup"),
    path("settings/", user_views.HaskerUserEditView.as_view(), name="edit"),

]