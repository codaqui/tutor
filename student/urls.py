from django.urls import path
from student import views 
from student.apps import StudentConfig

app_name = StudentConfig.name

urlpatterns = [
    path('student_form/', views.student_data_form_view, name='student_form'),
]
