from django.conf import settings  
from django.conf.urls.static import static  
from django.contrib import admin  
from django.urls import path, include  
from django.contrib.auth import views as auth_views  


urlpatterns = [  
    # Handle custom admin payment URLs first
    path('admin/payments/', include('calligraphyApp.urls')),
    path('admin/payment/', include('calligraphyApp.urls')),
    # Then default Django admin
    path('admin/', admin.site.urls),  
    path('', include('calligraphyApp.urls')),  # Include the URLs from calligraphyApp  
    path('accounts/', include('django.contrib.auth.urls')),  # Add Django auth URLs  
]  


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  