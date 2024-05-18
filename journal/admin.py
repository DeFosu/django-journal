from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Course, Profile, Enrollment, Lesson, Grade
from django.utils.translation import gettext_lazy as _

# Клас CourseAdmin наслідується від TranslatableAdmin і визначає властивості адміністратора курсів.
class CourseAdmin(TranslatableAdmin):
    list_display = ['title', 'teacher']  # Властивість list_display визначає, які поля відображаються у списку курсів у панелі адміністратора.
    search_fields = ['title', 'teacher__user__username']  # Поля для пошуку в списку курсів у панелі адміністратора.

# Клас ProfileAdmin визначає властивості адміністратора профілів.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']  # Властивість list_display визначає, які поля відображаються у списку профілів у панелі адміністратора.
    search_fields = ['user__username', 'role']  # Поля для пошуку в списку профілів у панелі адміністратора.

# Клас EnrollmentAdmin визначає властивості адміністратора записів на курси.
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'student']  # Властивість list_display визначає, які поля відображаються у списку записів на курси у панелі адміністратора.
    search_fields = ['course__title', 'student__user__username']  # Поля для пошуку в списку записів на курси у панелі адміністратора.

# Клас LessonAdmin наслідується від TranslatableAdmin і визначає властивості адміністратора занять.
class LessonAdmin(TranslatableAdmin):
    list_display = ['title', 'course', 'schedule']  # Властивість list_display визначає, які поля відображаються у списку занять у панелі адміністратора.
    search_fields = ['title', 'course__title']  # Поля для пошуку в списку занять у панелі адміністратора.
    date_hierarchy = 'schedule'  # Поля для фільтрації занять за датою у панелі адміністратора.

# Клас GradeAdmin визначає властивості адміністратора оцінок.
class GradeAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'student', 'grade']  # Властивість list_display визначає, які поля відображаються у списку оцінок у панелі адміністратора.
    search_fields = ['lesson__title', 'student__user__username']  # Поля для пошуку в списку оцінок у панелі адміністратора.

# Реєстрація моделей та їх властивостей адміністратора в панелі адміністратора Django.
admin.site.register(Course, CourseAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Grade, GradeAdmin)
