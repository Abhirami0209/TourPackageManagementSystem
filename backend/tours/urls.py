from django.urls import path
from . import views

urlpatterns = [
    # Home & Auth
    path('',                       views.index,               name='index'),
    path('login/',                 views.login_view,          name='login'),
    path('logout/',                views.logout_view,         name='logout'),

    # Registration
    path('register/user/',         views.register_user,       name='register_user'),
    path('register/vendor/',       views.register_vendor,     name='register_vendor'),

    # Dashboards
    path('dashboard/user/',        views.user_dashboard,      name='user_dashboard'),
    path('dashboard/vendor/',      views.vendor_dashboard,    name='vendor_dashboard'),

    # Package CRUD (vendor)
    path('dashboard/vendor/add/',               views.add_package,      name='add_package'),
    path('dashboard/vendor/edit/<int:pkg_id>/', views.edit_package,     name='edit_package'),
    path('dashboard/vendor/delete/<int:pkg_id>/', views.delete_package, name='delete_package'),

    # Vendor bookings
    path('dashboard/vendor/bookings/',               views.view_bookings,             name='view_bookings'),
    path('dashboard/vendor/bookings/<uuid:pkg_id>/', views.view_bookings_for_pkg,   name='view_bookings_for_pkg'),

    # Shared package detail + booking form
    path('dashboard/package/<uuid:package_id>/',     views.view_package_details,     name='view_package_details'),

    # Vendor profile/settings
    path('dashboard/vendor/profile/',   views.vendor_profile,   name='vendor_profile'),
    path('dashboard/vendor/settings/',  views.vendor_settings,  name='vendor_settings'),

    # User profile/settings/bookings
    path('dashboard/user/profile/',  views.user_profile,   name='user_profile'),
    path('dashboard/user/settings/', views.user_settings,  name='user_settings'),
    path('dashboard/user/bookings/', views.user_bookings, name='user_bookings'),
    path('dashboard/user/bookings/<int:booking_id>/view/', views.view_booking_details, name='view_booking_details'),
    path('book/<uuid:package_id>/', views.book_package, name='book_package'),

]     