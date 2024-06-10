from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('student_form/', views.student_data_form_view, name='student_form'),
]
