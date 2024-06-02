from django.db import models


class User(models.Model):
    nickname = models.CharField("Никнейм", max_length=200, unique=True)
    password = models.CharField("Пароль", max_length=200)
    email = models.CharField("Мэйл", max_length=200)
    avatar = models.ImageField("Аватар", upload_to=None,
                               height_field=None, width_field=None, max_length=100,
                               null=True, blank=True)
    reg_date = models.DateTimeField("Дата регистрации")
    USERNAME_FIELD = 'admin'

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


VOTE_UP = 1
VOTE_DOWN = -1
VOTE_CHOICES = ((VOTE_UP, 'Vote Up'), (VOTE_DOWN, 'Vote Down'))


class AnswerVote(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    to = models.ForeignKey(Answer, on_delete=models.CASCADE, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    value = models.ImageField(choices=VOTE_CHOICES)

    class Meta:
        verbose_name = 'Голосование: ответ'
        verbose_name_plural = 'Голосование: ответы'

    def __str__(self):
        return f"{self.user.nickname} {self.value:+d}"


class QuestionVote(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    to = models.ForeignKey(Question, on_delete=models.CASCADE, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    value = models.ImageField(choices=VOTE_CHOICES)

    class Meta:
        verbose_name = 'Голосование: вопрос'
        verbose_name_plural = 'Голосование: вопросы'

    def __str__(self):
        return f"{self.user.nickname} {self.value:+d}"
