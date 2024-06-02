from rest_framework import serializers

from .models import Question, Answer


class QuestionListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="my_hasker:question:detail", lookup_url_kwarg="q_id"
    )

    class Meta:
        model = Question
        fields = '__all__'


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="username"
    )
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    question_text = serializers.CharField(max_length=800)
    title = serializers.CharField(max_length=200)
    question_date = serializers.DateTimeField("Дата создания")

    class Meta:
        model = Question
        fields = '__all__'

    def get_answers_count(self, question):
        return question.answers.count()


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="username"
    )
    answer_text = serializers.CharField(max_length=800)
    answer_date = serializers.DateTimeField("Дата создания")
    is_correct = serializers.BooleanField()

    class Meta:
        model = Answer
        fields = '__all__'
