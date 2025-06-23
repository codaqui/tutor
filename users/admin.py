from django.contrib import admin

from users.models import User
from django.contrib.auth.models import Group


class UsersAdminConfig(admin.ModelAdmin):
    pass


class GroupsAdminConfig(admin.ModelAdmin):
    pass


# Unregister the default Group model
admin.site.unregister(Group)

# Register the custom admin site for Users
admin.site.register(User, UsersAdminConfig)
admin.site.register(Group, GroupsAdminConfig)
