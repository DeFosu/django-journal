from django.urls import path,include
from . import views
from django.views.i18n import set_language

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('course/<int:course_id>/remove_student/<int:enrollment_id>/', views.remove_student, name='remove_student'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/add_lesson/', views.add_lesson, name='add_lesson'),
    path('course/<int:lesson_id>/edit_lesson/', views.edit_lesson, name='edit_lesson'),
    path('course/<int:lesson_id>/delete_lesson/', views.delete_lesson, name='delete_lesson'),
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('course/<int:course_id>/add_student/', views.add_student, name='add_student'),
    path('course/<int:course_id>/remove_student/<int:enrollment_id>/', views.remove_student, name='remove_student'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('profile/<int:user_id>/update/', views.update_profile, name='update_profile'),
    path('profile/<int:user_id>/change_password/', views.change_password, name='change_password'),

]

