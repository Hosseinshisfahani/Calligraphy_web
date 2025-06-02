from django.conf import settings  
from django.conf.urls.static import static  
from django.contrib import admin  
from django.urls import path, include  
from django.contrib.auth import views as auth_views  


urlpatterns = [  
    # Django admin should come before our app URLs to avoid interference
    path('admin/', admin.site.urls),  
    # Then include app URLs
    path('', include('calligraphyApp.urls')),  # Include the URLs from calligraphyApp  
    path('accounts/', include('django.contrib.auth.urls')),  # Add Django auth URLs  
]  


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  