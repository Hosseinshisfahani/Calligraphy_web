from django.contrib import admin  
from .models import Course, Part, Video  

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