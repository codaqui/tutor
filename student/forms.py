from django import forms
from student.models import Student


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'birth_year', 'email', 'telephone']
