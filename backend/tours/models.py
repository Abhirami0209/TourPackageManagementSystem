import uuid
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('vendor', 'Vendor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    contact_info = models.TextField()
    contact_email = models.EmailField()
    business_reg_no = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.company_name} ({self.user.username})"

class TourPackage(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='packages')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=50, help_text="Maximum number of people allowed")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    @property
    def booked_count(self):
        return sum(b.number_of_people for b in self.bookings.filter(status='confirmed'))

    @property
    def slots_remaining(self):
        rem = self.capacity - self.booked_count
        return rem if rem >= 0 else 0

    @property
    def is_available(self):
        return self.status == 'approved' and self.slots_remaining > 0

class TourPackageImage(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='package_images/')

    def __str__(self):
        return f"Image for {self.package.title}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='bookings')
    number_of_people = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         return f"{self.user.username} booked {self.package.title} ({self.get_status_display()})" 