from django.db import models  

class Course(models.Model):  
    title = models.CharField(max_length=255)  
    description = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    
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
    video_file = models.FileField(upload_to='videos', null=True)   
    duration = models.DurationField()  
    
    def __str__(self):  
        return self.title