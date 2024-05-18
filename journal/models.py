# Оптимізовані імпорти
from django.db import models
from django.contrib.auth.models import User
from parler.models import TranslatableModel, TranslatedFields
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

# Модель курсу
class Course(TranslatableModel):
    """
    Модель курсу, що підтримує переклади.
    """
    translations = TranslatedFields(
        title=models.CharField(_('Name of the course'), max_length=100),  # Назва курсу
        description=models.TextField(_('Description of the course'))  # Опис курсу
    )
    teacher = models.ForeignKey(
        'Profile',
        verbose_name=_('Teacher'),  # Викладач
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'}  # Обмеження на вибір тільки викладачів
    )

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

    def __str__(self):
        return self.title  # Повертає назву курсу як рядок

# Модель профілю користувача
class Profile(models.Model):
    """
    Модель профілю користувача, що розширює стандартну модель користувача.
    """
    ROLE_CHOICES = (
        ('student', _('Student')),
        ('teacher', _('Teacher')),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(_('User role'), max_length=10, choices=ROLE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return self.user.username  # Повертає ім'я користувача як рядок

# Модель запису на курс
class Enrollment(models.Model):
    """
    Модель запису на курс для студентів.
    """
    course = models.ForeignKey(Course, verbose_name=_('Course'), on_delete=models.CASCADE)
    student = models.ForeignKey('Profile', verbose_name=_('Student'), on_delete=models.CASCADE, limit_choices_to={'role': 'student'})

    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = [['course', 'student']]  # Заборонити дублювання комбінацій курсу і студента

    def __str__(self):
        return f"{self.student.user.username} - {self.course}"  # Повертає ім'я студента та курс як рядок

# Модель заняття
class Lesson(TranslatableModel):
    """
    Модель заняття, що підтримує переклади.
    """
    translations = TranslatedFields(
        title=models.CharField(_('Lesson title'), max_length=100),  # Назва заняття
        description=models.TextField(_('Lesson description'), blank=True, null=True)  # Опис заняття
    )
    course = models.ForeignKey(Course, verbose_name=_('Course'), on_delete=models.CASCADE)  # Курс
    schedule = models.DateTimeField(_('Scheduled time'))  # Час проведення

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')

    def __str__(self):
        return f"{self.course} - {self.title}"  # Повертає назву курсу та назву заняття як рядок

# Модель оцінки
class Grade(models.Model):
    """
    Модель оцінки студента за заняття.
    """
    lesson = models.ForeignKey(Lesson, verbose_name=_('Lesson'), on_delete=models.CASCADE)  # Заняття
    student = models.ForeignKey('Profile', verbose_name=_('Student'), on_delete=models.CASCADE, limit_choices_to={'role': 'student'})  # Студент
    grade = models.PositiveSmallIntegerField(
        _('Grade'), default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # Оцінка

    class Meta:
        verbose_name = _('Grade')
        verbose_name_plural = _('Grades')

    def __str__(self):
        return f"{self.student.user.username} - {self.lesson}"  # Повертає ім'я студента та назву заняття як рядок
