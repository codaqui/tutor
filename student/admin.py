from django.contrib import admin
from student.models import Student

# Register your custom students functionality here

@admin.action(description="Active a student and create a wallet")
def activate_students(modeladmin, request, queryset):
    students = queryset
    for student in students:
        student.active_user()

@admin.action(description="Invite student to GitHub Team")
def invite_students(modeladmin, request, queryset):
    students = queryset
    for student in students:
        student.invite_to_github_team()


# Register your custom students modelsAdmin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'telephone', 'is_active', 'get_age', 'get_membership')
    actions = (activate_students, invite_students)

    def get_age(self, obj):
        return obj.get_age()
    
    def get_membership(self, obj):
        return obj.verify_github_team_membership()

    # Custom Name
    get_age.short_description = 'Age'
    get_membership.short_description = 'GitHub Team Intranet Membership'

# Register your models here.
admin.site.register(Student, StudentAdmin)