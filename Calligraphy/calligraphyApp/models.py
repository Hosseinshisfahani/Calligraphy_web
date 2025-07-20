from django.db import models  
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    LEVEL_CHOICES = [
        ('مقدماتی و متوسط', 'مقدماتی و متوسط'),
        ('خوش', 'خوش'),
        ('عالی و ممتاز', 'عالی و ممتاز'),
        ('فوق ممتاز', 'فوق ممتاز')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone = models.CharField(max_length=15, verbose_name='شماره تلفن', default='09123456789')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name='سطح', default='مقدماتی و متوسط')
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'پروفایل {self.user.username}'

    def clean(self):
        # Validate phone number format (Iranian mobile numbers)
        if self.phone:
            if not self.phone.startswith('09') or len(self.phone) != 11:
                raise ValidationError('شماره تلفن باید با ۰۹ شروع شود و ۱۱ رقم باشد.')

class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پاسخ'),
        ('in_progress', 'در حال بررسی'),
        ('resolved', 'پاسخ داده شده'),
        ('closed', 'بسته شده'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.subject} - {self.user.username}'

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'پاسخ به {self.ticket.subject}'

class Course(models.Model):  
    title = models.CharField(max_length=200)  
    description = models.TextField()  
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def has_free_videos(self):
        return self.parts.filter(videos__is_free=True).exists()
    
    def get_free_videos(self):
        return Video.objects.filter(part__course=self, is_free=True)
    
    def ensure_one_free_video(self):
        """Ensure exactly one free video per course (first video of first part)"""
        # First, mark all videos as not free
        Video.objects.filter(part__course=self).update(is_free=False)
        
        # Find the first part (by order)
        first_part = self.parts.order_by('order').first()
        if first_part:
            # Find the first video in the first part (by order)
            first_video = first_part.videos.order_by('order').first()
            if first_video:
                first_video.is_free = True
                first_video.save()
                return first_video
        return None
    
    def get_first_free_video(self):
        """Get the first free video for this course"""
        first_part = self.parts.order_by('order').first()
        if first_part:
            return first_part.videos.filter(is_free=True).order_by('order').first()
        return None
    
    def __str__(self):  
        return self.title  


class Part(models.Model):  
    course = models.ForeignKey(Course, related_name='parts', on_delete=models.CASCADE)  
    title = models.CharField(max_length=255)  
    order = models.PositiveIntegerField(default=0)  
    
    class Meta:  
        ordering = ['order']  
    
    def __str__(self):  
        return self.title  


class Video(models.Model):  
    part = models.ForeignKey(Part, related_name='videos', on_delete=models.CASCADE)  
    title = models.CharField(max_length=255)  
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos', null=True)   
    duration = models.DurationField()
    order = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(upload_to='video_thumbnails', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_free = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):  
        return self.title

    def is_accessible_by(self, user):
        if self.is_free:
            return True
        if not user.is_authenticated:
            return False
        return CourseEnrollment.objects.filter(
            user=user,
            course=self.part.course,
            is_paid=True
        ).exists()

# Add Order and OrderItem models for shopping cart
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'ناموفق'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"سفارش {self.id} - {self.user.username}"

    def calculate_total(self):
        return sum(item.course.price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.order.user.username}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'در انتظار تایید'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    receipt = models.ImageField(upload_to='payment_receipts/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.amount} تومان"

class SiteSetting(models.Model):
    card_number = models.CharField(max_length=32, blank=True, default='', verbose_name='شماره کارت بانکی')

    def __str__(self):
        return 'Site Settings'

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'