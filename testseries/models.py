from django.db import models

# Create your models here.
# testseries/models.py
from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Test(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tests')
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    total_marks = models.PositiveIntegerField(default=100)
    total_questions = models.PositiveIntegerField(default=10)
    
    # Negative Marking
    has_negative_marking = models.BooleanField(default=False)
    negative_marks_per_question = models.FloatField(default=0.0, help_text="e.g. 0.25 or 1.0")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category.name})"


class Question(models.Model):
    OPTION_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.question_text[:50]}... ({self.test.title})"


# testseries/models.py
from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Test(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tests')
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    total_marks = models.PositiveIntegerField(default=100)
    total_questions = models.PositiveIntegerField(default=10)
    has_negative_marking = models.BooleanField(default=False)
    negative_marks_per_question = models.FloatField(default=0.0, help_text="e.g. 0.25 or 1.0")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category.name})"


class Question(models.Model):
    OPTION_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.question_text[:50]}... ({self.test.title})"


# testseries/models.py
class TestResult(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score_obtained = models.FloatField()
    total_marks = models.PositiveIntegerField()
    correct_count = models.PositiveIntegerField(default=0)
    wrong_count = models.PositiveIntegerField(default=0)
    unattempted_count = models.PositiveIntegerField(default=0)
    # New Field: Stores dict of {question_id: selected_option}
    user_answers = models.JSONField(default=dict, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.test.title}"