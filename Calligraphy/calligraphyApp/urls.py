# urls.py  
from django.conf import settings  
from django.conf.urls.static import static  
from django.urls import path  
from .views import * 
from django.contrib.auth import views as auth_views  


urlpatterns = [  
    path('', home, name='home'),  
    path('login/', user_login, name='login'), 
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  
    path('register/', register, name='register'),  
    path('part/<int:part_id>/', part_detail, name='part_detail'),
    path('users/', user_list, name='user_list'),
    path('profile/', profile_view, name='profile'),  # User profile view  
   
  
]  

if settings.DEBUG:  # Serve media files in development  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  