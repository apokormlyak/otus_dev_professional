from django.db import models


class User(models.Model):
    nickname = models.CharField("Никнейм", max_length=200, unique=True)
    password = models.CharField("Пароль", max_length=200)
    email = models.CharField("Мэйл", max_length=200)
    avatar = models.ImageField("Аватар", upload_to=None,
                               height_field=None, width_field=None, max_length=100,
                               null=True, blank=True)
    reg_date = models.DateTimeField("Дата регистрации")

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=800)
    title = models.CharField("Содержание", max_length=200)
    question_date = models.DateTimeField("Дата создания")
    tags = models.JSONField("Теги", null=True, blank=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=800)
    answer_date = models.DateTimeField("Дата создания")
    is_correct = models.BooleanField("Флаг правильного ответа", null=True, blank=True)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class Tags(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
