import os
import django
from django.conf import settings
from django.utils import translation
# Налаштування Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth.models import User
from journal.models import Course, Profile, Enrollment, Lesson, Grade
import os
import django
from django.utils import timezone
import os
import django
from django.utils import translation
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from datetime import datetime

# Створення користувачів
def create_user(username, first_name, last_name, email, role):
    user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password='password123')
    profile = Profile.objects.create(user=user, role=role)
    return profile

# Створення курсів
def create_course(title_en, title_uk, title_de, description_en, description_uk, description_de, teacher):
    course = Course.objects.create(teacher=teacher)
    with translation.override('en'):
        course.set_current_language('en')
        course.title = title_en
        course.description = description_en
        course.save()

    with translation.override('uk'):
        course.set_current_language('uk')
        course.title = title_uk
        course.description = description_uk
        course.save()

    with translation.override('de'):
        course.set_current_language('de')
        course.title = title_de
        course.description = description_de
        course.save()

    return course

# Створення занять
def create_lesson(course, title_en, title_uk, title_de, description_en, description_uk, description_de, schedule):
    lesson = Lesson.objects.create(course=course, schedule=make_aware(schedule))
    with translation.override('en'):
        lesson.set_current_language('en')
        lesson.title = title_en
        lesson.description = description_en
        lesson.save()

    with translation.override('uk'):
        lesson.set_current_language('uk')
        lesson.title = title_uk
        lesson.description = description_uk
        lesson.save()

    with translation.override('de'):
        lesson.set_current_language('de')
        lesson.title = title_de
        lesson.description = description_de
        lesson.save()

    return lesson

# Створення запису на курс
def create_enrollment(course, student):
    return Enrollment.objects.create(course=course, student=student)

# Створення оцінки
def create_grade(lesson, student, grade):
    return Grade.objects.create(lesson=lesson, student=student, grade=grade)

def populate():
    # Створення профілів викладачів та студентів
    teacher1 = create_user('teacher1', 'John', 'Doe', 'john.doe@example.com', 'teacher')
    student1 = create_user('student1', 'Jane', 'Smith', 'jane.smith@example.com', 'student')
    student2 = create_user('student2', 'Max', 'Mustermann', 'max.mustermann@example.com', 'student')

    # Створення курсів
    course1 = create_course(
        title_en='Math 101', title_uk='Математика 101', title_de='Mathematik 101',
        description_en='Basic mathematics', description_uk='Основи математики', description_de='Grundlagen der Mathematik',
        teacher=teacher1
    )

    # Створення занять
    lesson1 = create_lesson(
        course=course1,
        title_en='Algebra', title_uk='Алгебра', title_de='Algebra',
        description_en='Introduction to Algebra', description_uk='Вступ до Алгебри', description_de='Einführung in die Algebra',
        schedule=datetime(2024, 5, 18, 10, 0, 0)
    )

    # Створення записів на курс
    enrollment1 = create_enrollment(course=course1, student=student1)
    enrollment2 = create_enrollment(course=course1, student=student2)

    # Створення оцінок
    grade1 = create_grade(lesson1, student1, 85)
    grade2 = create_grade(lesson1, student2, 90)

if __name__ == '__main__':
    populate()