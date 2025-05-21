from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Vendor, TourPackage, Booking

# unregister default User to attach Profile inline
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'email', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'contact_email')
    search_fields = ('company_name', 'user__username', 'contact_email')

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor', 'price', 'status', 'capacity', 'booked_count')
    list_filter = ('status',)
    search_fields = ('title', 'vendor__company_name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'number_of_people', 'status', 'booking_date')
    list_filter = ('status',)
