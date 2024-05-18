# Оптимізовані імпорти
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Course, Lesson, Grade, Profile, Enrollment
from parler.forms import TranslatableModelForm

# Форма для реєстрації учня або викладача
class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label=_("Ім'я"), max_length=30, required=True)
    last_name = forms.CharField(label=_("Прізвище"), max_length=30, required=True)
    email = forms.EmailField(label=_("Електронна пошта"), max_length=254, help_text=_("Обов'язкове поле."))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

# Форма для авторизації
class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_('Ім\'я користувача'), max_length=254, required=True)
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'password']

# Форма для створення/редагування курсу
class CourseForm(TranslatableModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

# Форма для створення/редагування заняття
class LessonForm(TranslatableModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'schedule']

# Форма для створення/редагування оцінки
class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['lesson', 'student', 'grade']
        widgets = {
            'lesson': forms.HiddenInput(),
            'student': forms.HiddenInput(),
        }

# Форма для додавання студента до курсу
class AddStudentForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Profile.objects.filter(role='student'))

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)
        
        if course_id:
            # Виключити студентів, які вже записані на цей курс
            enrolled_students = Enrollment.objects.filter(course_id=course_id).values_list('student_id', flat=True)
            self.fields['student'].queryset = Profile.objects.filter(role='student').exclude(id__in=enrolled_students)

# Форма для оновлення даних користувача
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

# Форма для зміни паролю користувача
class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(label=_("Старий пароль"), widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_("Новий пароль"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Підтвердження нового паролю"), widget=forms.PasswordInput)
