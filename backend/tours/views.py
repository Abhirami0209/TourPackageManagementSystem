import uuid
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Vendor, TourPackage, TourPackageImage, Booking

# — Home —
def index(request):
    return render(request, 'index.html')


# — Authentication —
def register_user(request):
    if request.method == 'POST':
        name, email, pwd = (
            request.POST['name'],
            request.POST['email'].lower(),
            request.POST['password']
        )

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register_user')

        # Create the user
        user = User.objects.create_user(username=email, email=email, password=pwd)
        user.first_name = name
        user.save()

        # Ensure profile is created without duplication
        profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'user'})

        messages.success(request, "Registered successfully! Please log in.")
        return redirect('login')

    return render(request, 'register_user.html')




def register_vendor(request):
    if request.method == 'POST':
        # 1) Collect form fields exactly matching the template names
        name        = request.POST.get('name', '').strip()
        email       = request.POST.get('email', '').lower().strip()
        password    = request.POST.get('password', '')
        company     = request.POST.get('company', '').strip()
        address     = request.POST.get('address', '').strip()
        reg_no      = request.POST.get('reg_no', '').strip()
        dob         = request.POST.get('dob', '')            
        phone       = request.POST.get('phone', '').strip()

        # 2) Prevent duplicate emails
        if User.objects.filter(username=email).exists():
            messages.error(request, "That email is already in use.")
            return redirect('register_vendor')

        # 3) Create the User
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        # 4) Create or update the Profile to 'vendor'
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = 'vendor'
        profile.save()

        # 5) Now create the Vendor record
        Vendor.objects.create(
            user=user,
            company_name    = company,
            contact_info    = address,
            contact_email   = email,
            business_reg_no = reg_no,
            date_of_birth   = dob,
            phone           = phone
        )

        messages.success(request, "Vendor registered! Please log in.")
        return redirect('login')

    # GET → just render the form
    return render(request, 'register_vendor.html')


def login_view(request):
    if request.method == 'POST':
        # using email as username
        email    = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            # redirect based on role
            if user.profile.role == 'vendor':
                return redirect('vendor_dashboard')
            return redirect('user_dashboard')

        messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('login')


# — User Dashboard —
@login_required
def user_dashboard(request):
    if request.user.profile.role != 'user':
        return redirect('vendor_dashboard')
    packages = TourPackage.objects.filter(status='approved')
    return render(request, 'user_dashboard.html', {'packages': packages})


# — Vendor Dashboard —
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Booking  # Make sure Booking is imported

@login_required
def vendor_dashboard(request):
    if request.user.profile.role != 'vendor':
        return redirect('user_dashboard')

    vendor = request.user.vendor
    current = vendor.packages.filter(status='approved')
    previous = vendor.packages.exclude(status='approved')

    # Get all bookings for the vendor's packages
    bookings = Booking.objects.filter(package__vendor=vendor)

    # Calculate total revenue from confirmed bookings
    confirmed_bookings = bookings.filter(status='confirmed')
    total_revenue = sum(b.number_of_people * b.package.price for b in confirmed_bookings)

    # Count total bookings
    total_bookings = confirmed_bookings.count()

    # Avoid division by zero
    total_packages = current.count()
    avg_earnings = total_revenue / total_packages if total_packages > 0 else 0

    return render(request, 'vendor_dashboard.html', {
        'vendor': vendor,
        'current_packages': current,
        'previous_packages': previous,
        'bookings': bookings,
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'avg_earnings': avg_earnings,
    })


# — Package CRUD (Vendor) —
@login_required
def add_package(request):
    if request.user.profile.role != 'vendor':
        return redirect('user_dashboard')
    if request.method == 'POST':
        pkg = TourPackage.objects.create(
            vendor=request.user.vendor,
            title=request.POST['title'],
            description=request.POST['description'],
            price=request.POST['price'],
            capacity=request.POST.get('capacity', 50)
        )
        for img in request.FILES.getlist('images'):
            TourPackageImage.objects.create(package=pkg, image=img)
        messages.success(request, "Package added successfully!")
        return redirect('vendor_dashboard')
    return render(request, 'add_package.html')


@login_required
def edit_package(request, pkg_id):
    pkg = get_object_or_404(TourPackage, id=pkg_id, vendor=request.user.vendor)
    if request.method == 'POST':
        pkg.title = request.POST['title']
        pkg.description = request.POST['description']
        pkg.price = request.POST['price']
        pkg.capacity = request.POST['capacity']
        if 'images' in request.FILES:
            pkg.images.all().delete()
            for img in request.FILES.getlist('images'):
                TourPackageImage.objects.create(package=pkg, image=img)
        pkg.save()
        messages.success(request, "Package updated!")
        return redirect('vendor_dashboard')
    return render(request, 'edit_package.html', {'pkg': pkg})


@login_required
def delete_package(request, pkg_id):
    pkg = get_object_or_404(TourPackage, id=pkg_id, vendor=request.user.vendor)
    if request.method == 'POST':
        pkg.delete()
        messages.success(request, "Package deleted.")
        return redirect('vendor_dashboard')
    return render(request, 'delete_package.html', {'pkg': pkg})


# — Vendor: All Bookings Across Their Packages —
from django.utils import timezone

@login_required
def view_bookings(request):
    if request.user.profile.role != 'vendor':
        return redirect('user_dashboard')

    bookings = Booking.objects.filter(package__vendor=request.user.vendor)

    # Get filter values
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('booked_at')

    # Apply filters
    if status_filter and status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    if date_filter:
        bookings = bookings.filter(booked_at__date=date_filter)

    bookings = bookings.select_related('user', 'package')

    return render(request, 'view_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter or 'all',
        'date_filter': date_filter or '',
    })


# — Vendor: Bookings for a Single Package —
@login_required
def view_bookings_for_pkg(request, pkg_id):
    if request.user.profile.role != 'vendor':
        return redirect('user_dashboard')
    pkg = get_object_or_404(TourPackage, id=pkg_id, vendor=request.user.vendor)
    bookings = Booking.objects.filter(package=pkg).select_related('user')
    return render(request, 'view_bookings_for_pkg.html', {
        'bookings': bookings,
        'package': pkg
    })


# — Shared Package Detail (View + Booking Form) —
@login_required
def view_package_details(request, package_id):
    # Fetch the package
    package = get_object_or_404(TourPackage, id=package_id, status='approved')

    # If vendor, show bookings inline
    if request.user.profile.role == 'vendor' and package.vendor.user == request.user:
        bookings = package.bookings.select_related('user').all()
        return render(request, 'view_package_details.html', {
            'package': package,
            'vendor': package.vendor,
            'bookings': bookings,
        })

    # If user, handle booking form POST
    if request.user.profile.role == 'user':
        if request.method == 'POST':
            num = int(request.POST.get('number_of_people', 1))
            Booking.objects.create(
                user=request.user,
                package=package,
                number_of_people=num,
                status='pending'
            )
            messages.success(request, "Booking successful!")
            return redirect('user_bookings')
        # GET: just show details + form
        return render(request, 'view_package_details.html', {
            'package': package,
            'vendor': package.vendor,
        })

    # Otherwise no permission
    messages.error(request, "No permission.")
    return redirect('index')

# — Vendor Profile & Settings —
@login_required
def vendor_profile(request):
    if request.user.profile.role != 'vendor':
        return redirect('user_dashboard')
    vendor = request.user.vendor
    if request.method == 'POST':
        vendor.company_name = request.POST['company_name']
        vendor.contact_info = request.POST['contact_info']
        vendor.contact_email = request.POST['contact_email']
        vendor.phone = request.POST['phone']
        vendor.save()
        messages.success(request, "Profile updated.")
        return redirect('vendor_profile')
    return render(request, 'vendor_profile.html', {'vendor': vendor})


@login_required
def vendor_settings(request):
    if request.user.profile.role != 'vendor':
        return redirect('user_dashboard')
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.email = request.POST.get('email', request.user.email).lower()
        request.user.save()
        messages.success(request, "Settings saved.")
        return redirect('vendor_settings')
    return render(request, 'vendor_settings.html')


# — User Profile & Settings —
@login_required
def user_profile(request):
    if request.user.profile.role != 'user':
        return redirect('vendor_dashboard')
    return render(request, 'user_profile.html', {'user': request.user})


@login_required
def user_settings(request):
    if request.user.profile.role != 'user':
        return redirect('vendor_dashboard')
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name  = request.POST.get('last_name', request.user.last_name)
        request.user.email      = request.POST.get('email', request.user.email).lower()
        request.user.save()
        messages.success(request, "Settings saved.")
        return redirect('user_settings')
    return render(request, 'user_settings.html')


# — User’s Bookings List —
@login_required
def user_bookings(request):
    if request.user.profile.role != 'user':
        return redirect('vendor_dashboard')
    bookings = Booking.objects.filter(user=request.user).select_related('package', 'package__vendor')
    return render(request, 'user_bookings.html', {'bookings': bookings})

def view_booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    package = booking.package
    vendor = package.vendor

    if request.method == 'POST':
        # Optional: handle additional booking logic
        number_of_people = request.POST.get('number_of_people')
        # Add logic if rebooking is allowed

    return render(request, 'view_bookings_for_pkg.html', {
        'booking': booking,
        'package': package,
        'vendor': vendor,
    })
    
@login_required
def book_package(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id)
    if request.method == 'POST':
        num_people = int(request.POST.get('number_of_people', 1))
        Booking.objects.create(user=request.user, package=package, number_of_people=num_people)
        return redirect('user_dashboard')  # or wherever you want to go after booking
    return render(request, 'tours/book_package.html', {'package': package})  