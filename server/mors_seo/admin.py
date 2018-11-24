from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from server.mors_seo.forms import CustomUserCreationForm, CustomUserChangeForm
from server.mors_seo.models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'username']


admin.site.register(User, CustomUserAdmin)
