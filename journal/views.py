from django.contrib.auth import authenticate, login as user_login, logout as user_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages

from .forms import (
    AddStudentForm,
    CourseForm,
    GradeForm,
    LessonForm,
    UserUpdateForm,
    UserRegistrationForm,
)
from .models import Course, Profile, Lesson, Grade, Enrollment

@login_required
def view_profile(request, user_id):
    """Відображення профілю користувача."""
    user = get_object_or_404(User, pk=user_id)
    profile = user.profile
    is_teacher = request.user.profile.role == 'teacher'
    
    # Отримання курсів в залежності від ролі користувача
    if is_teacher:
        courses = Course.objects.filter(teacher=request.user.profile).distinct()
    else:
        courses = Course.objects.filter(enrollment__student=profile)

    course_details = {}
    for course in courses:
        lessons = course.lesson_set.all()
        course_grades = {}
        for lesson in lessons:
            # Викладач не повинен мати оцінок зі свого ж курсу
            if is_teacher and course.teacher == profile:
                continue

            try:
                grade = Grade.objects.filter(lesson=lesson, student=profile).latest('id')
                course_grades[lesson] = grade.grade
            except Grade.DoesNotExist:
                course_grades[lesson] = None
            except MultipleObjectsReturned:
                grades = Grade.objects.filter(lesson=lesson, student=profile)
                grade = grades.latest('id')
                course_grades[lesson] = grade.grade

        if not (is_teacher and course.teacher == profile):  # Додаткова перевірка, щоб викладач не бачив свої оцінки
            course_details[course] = {
                'lessons': lessons,
                'grades': course_grades
            }

        if request.method == 'POST' and is_teacher:
            grade_form = GradeForm(request.POST)
            if grade_form.is_valid():
                lesson = grade_form.cleaned_data['lesson']
                student = grade_form.cleaned_data['student']
                grade, created = Grade.objects.get_or_create(lesson=lesson, student=student)
                grade.grade = grade_form.cleaned_data['grade']
                grade.save()
                return HttpResponseRedirect(reverse('view_profile', args=[user_id]))
        else:
            grade_form = GradeForm()

    user_form = None
    if request.user == user:
        user_form = UserUpdateForm(instance=user)
        if request.method == 'POST' and not is_teacher:
            user_form = UserUpdateForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                return redirect('view_profile', user_id=user_id)
    
    return render(request, 'profile.html', {
        'userStudent': user,
        'profile': profile,
        'course_details': course_details,
        'user_form': user_form,
        'grade_form': grade_form,
        'is_teacher': is_teacher,
    })

@login_required
def update_profile(request, user_id):
    """Оновлення профілю користувача."""
    if request.user.id != user_id:
        return redirect('view_profile', user_id=request.user.id)
    
    user = get_object_or_404(User, pk=user_id)
    user_form = UserUpdateForm(instance=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('view_profile', user_id=user_id)

    return render(request, 'profile_update.html', {'user_form': user_form})

@login_required
def change_password(request, user_id):
    """Зміна паролю користувача."""
    if request.user.id != user_id:
        return redirect('view_profile', user_id=request.user.id)
    
    user = get_object_or_404(User, pk=user_id)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('view_profile', user_id=user_id)

    return render(request, 'password_change.html', {'password_form': password_form})

@login_required
def course_detail(request, course_id):
    """Деталі курсу."""
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('schedule')
    is_teacher = request.user.profile.role == 'teacher'

    if is_teacher:
        if course.teacher != request.user.profile:
            return HttpResponseForbidden(_("You are not the teacher of this course."))

        enrollments = Enrollment.objects.filter(course=course)
        if request.method == 'POST':
            lesson_id = request.POST.get('lesson_id')
            student_id = request.POST.get('student_id')
            grade_value = request.POST.get('grade')

            if lesson_id and student_id and grade_value is not None:
                grades = Grade.objects.filter(lesson_id=lesson_id, student_id=student_id)
                if grades.exists():
                    grade = grades.latest('id')
                else:
                    grade = Grade(lesson_id=lesson_id, student_id=student_id)
                
                grade.grade = grade_value
                grade.save()
                return HttpResponseRedirect(reverse('course_detail', args=[course_id]))

        grades = {
            enrollment.student.id: {
                lesson.id: Grade.objects.filter(lesson=lesson, student=enrollment.student).first()
                for lesson in lessons
            }
            for enrollment in enrollments
        }

        context = {
            'course': course,
            'lessons': lessons,
            'is_teacher': True,
            'enrollments': enrollments,
            'grades': grades,
        }
    else:
        enrollment, created = Enrollment.objects.get_or_create(course=course, student=request.user.profile)
        students = Profile.objects.filter(enrollment__course=course)
        grades = {
            student.id: {
                lesson.id: Grade.objects.filter(lesson=lesson, student=student).first()
                for lesson in lessons
            }
            for student in students
        }

        context = {
            'course': course,
            'lessons': lessons,
            'is_teacher': False,
            'grades': grades,
            'enrollment': enrollment,
            'students': students
        }

    return render(request, 'course_detail.html', context)

@login_required
def remove_student(request, course_id, enrollment_id):
    """Видалення студента з курсу за допомогою enrollment_id."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.delete()
    return redirect('course_detail', course_id=course_id)

@login_required
def home(request):
    """Домашня сторінка з курсами користувача."""
    profile = request.user.profile
    
    if profile.role == 'teacher':
        courses = Course.objects.filter(teacher=profile)
    else:  # роль 'student'
        enrollments = Enrollment.objects.filter(student=profile)
        courses = [enrollment.course for enrollment in enrollments]
    
    return render(request, 'home.html', {'courses': courses})

@login_required
def add_lesson(request, course_id):
    """Додавання уроку до курсу."""
    course = get_object_or_404(Course, id=course_id)
    if request.user.profile.role != 'teacher' or course.teacher != request.user.profile:
        return HttpResponseForbidden(_("Only the teacher of this course can add lessons."))
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm()
    return render(request, 'add_lesson.html', {'form': form, 'course': course})

@login_required
def edit_course(request, course_id):
    """Редагування курсу."""
    course = get_object_or_404(Course, id=course_id)
    if request.user.profile.role != 'teacher' or course.teacher != request.user.profile:
        return HttpResponseForbidden(_("Only the teacher of this course can edit it."))

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'edit_course.html', {'form': form, 'course': course})

@login_required
def add_student(request, course_id):
    """Додавання студента до курсу."""
    course = get_object_or_404(Course, id=course_id)
    
    # Перевірка чи користувач є викладачем курсу
    if request.user.profile.role != 'teacher' or course.teacher != request.user.profile:
        return HttpResponseForbidden(_("Only the teacher of this course can add students."))
    
    if request.method == 'POST':
        form = AddStudentForm(request.POST, course_id=course_id)
        if form.is_valid():
            student_profile = form.cleaned_data['student']
            Enrollment.objects.create(course=course, student=student_profile)
            return redirect('course_detail', course_id=course.id)
    else:
        form = AddStudentForm(course_id=course_id)
    
    return render(request, 'add_student.html', {'form': form, 'course': course})

@login_required
def edit_lesson(request, lesson_id):
    """Редагування уроку."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user.profile.role != 'teacher' or lesson.course.teacher != request.user.profile:
        return HttpResponseForbidden(_("Only the teacher of this lesson can edit it."))
    
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)
    
    return render(request, 'edit_lesson.html', {'form': form, 'lesson': lesson})

@login_required
def delete_lesson(request, lesson_id):
    """Видалення уроку."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user.profile.role != 'teacher' or lesson.course.teacher != request.user.profile:
        return HttpResponseForbidden(_("Only the teacher of this lesson can delete it."))
    
    course_id = lesson.course.id
    lesson.delete()
    return redirect('course_detail', course_id=course_id)

@login_required    
def logout(request):
    """Вихід з облікового запису."""
    user_logout(request)
    return redirect('login')

def register(request):
    """Реєстрація нового користувача."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Створення профілю без ролі
            Profile.objects.create(user=user)
            
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    """Вхід до облікового запису."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                user_login(request, user)  
                return redirect('home') 
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
