from django.contrib import admin  
from .models import (
    Course, Part, Video, Payment, SiteSetting, 
    SupportTicket, TicketResponse, OrderItem, Order,
    UserProfile, CourseEnrollment
)

class VideoInline(admin.TabularInline):  
    model = Video  
    extra = 1  # Number of empty forms to display  

class PartInline(admin.TabularInline):  
    model = Part  
    extra = 1  # Number of empty forms to display  

@admin.register(Course)  
class CourseAdmin(admin.ModelAdmin):  
    list_display = ('title', 'created_at')  
    search_fields = ('title', 'description')  
    inlines = [PartInline]  # Allows editing of parts directly in the course admin  

@admin.register(Part)  
class PartAdmin(admin.ModelAdmin):  
    list_display = ('title', 'course', 'order')  
    list_filter = ('course',)  
    search_fields = ('title',)  

@admin.register(Video)  
class VideoAdmin(admin.ModelAdmin):  
    list_display = ('title', 'part', 'duration', 'order')  
    list_filter = ('part__course', 'part')  
    search_fields = ('title', 'description')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'card_number')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__username')

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ticket__subject', 'user__username')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'course', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__user__username', 'course__title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'level')
    search_fields = ('user__username', 'phone')

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_paid', 'enrolled_at')
    list_filter = ('is_paid', 'enrolled_at')
    search_fields = ('user__username', 'course__title')