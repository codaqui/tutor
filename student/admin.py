from django.contrib import admin
from student.models import Student
from wallet.models import Wallet

# Register your custom students functionality here

@admin.action(description="Active a student and create a wallet")
def activate_students(modeladmin, request, queryset):
    students = queryset
    students.update(is_active=True)
    for student in students:
        wallet = Wallet.objects.create(user=student.user)
        wallet.save()


# Register your custom students modelsAdmin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'telephone', 'is_active', 'get_age')
    actions = (activate_students,)

    def get_age(self, obj):
        return obj.get_age()

    # Custom Name
    get_age.short_description = 'Age'

# Register your models here.
admin.site.register(Student, StudentAdmin)