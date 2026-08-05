from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Address

class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('email',)
    list_display = ('email', 'role', 'is_staff', 'is_active')
    list_filter = ('email', 'role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')

admin.site.register(User, CustomUserAdmin)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__email',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'city', 'country', 'is_default')
    list_filter = ('is_default', 'country', 'city')
    search_fields = ('user__email', 'title', 'street_address')
