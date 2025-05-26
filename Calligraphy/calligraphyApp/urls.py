# urls.py  
from django.conf import settings  
from django.conf.urls.static import static  
from django.urls import path  
from .views import * 
from django.contrib.auth import views as auth_views  
from . import views
from .forms import LoginForm

app_name = 'calligraphyApp'

urlpatterns = [
    # Admin-related URLs - placed first for higher priority
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/payments/', views.admin_payment_list, name='admin_payment_list'),
    path('admin/payments/<int:payment_id>/', views.admin_payment_detail, name='admin_payment_detail'),
    path('admin/payment/update/<int:payment_id>/', views.update_payment_status, name='update_payment_status'),
    path('admin/payment/debug/', views.payment_debug, name='payment_debug'),

    # Direct manual access paths for payments by ID (no conflicting patterns)
    path('payments/detail/<int:payment_id>/', views.admin_payment_detail, name='direct_payment_detail'),
    
    # Regular user URLs
    path('', views.course_list, name='home'),  # This will serve as both home and course_list
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),  
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    # My Courses URL (temporary)
    path('my-courses/', views.course_list, name='my_courses'),  
    
    # Orders URL (temporary)
    path('orders/', views.profile_view, name='orders'),
    
    # Teacher Profile URL
    path('teacher/profile/', views.teacher_profile, name='teacher_profile'),

    # Shopping Cart URLs
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/apply-discount/', views.apply_discount, name='apply_discount'),
    path('cart/remove-discount/', views.remove_discount, name='remove_discount'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('payment/process/<int:course_id>/', views.payment_process, name='payment_process'),
    path('payment/list/', views.payment_list, name='payment_list'),

    # Protected Video URL
    path('video/<int:video_id>/', views.protected_video_view, name='protected_video'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='calligraphyApp/registration/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', views.log_out, name='logout'),

    # Password Change
    path('password-change/', 
        auth_views.PasswordChangeView.as_view(
            template_name='calligraphyApp/registration/password_change_form.html',
            success_url='done'
        ), name='password_change'),
    path('password-change/done/', 
        auth_views.PasswordChangeDoneView.as_view(
            template_name='calligraphyApp/registration/password_change_done.html'
        ), name='password_change_done'),

    # Password Reset
    path('password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='calligraphyApp/registration/password_reset_form.html',
            success_url='done',
            email_template_name='calligraphyApp/registration/password_reset_email.html'
        ), name='password_reset'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='calligraphyApp/registration/password_reset_done.html'
        ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='calligraphyApp/registration/password_reset_confirm.html',
            success_url='/calligraphyApp/password-reset/complete/'
        ), name='password_reset_confirm'),
    path('password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='calligraphyApp/registration/password_reset_complete.html'
        ), name='password_reset_complete'),

    # User Management
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),  # User profile view  
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Support Tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # Course Related URLs
    path('course/<int:course_id>/part/<int:part_id>/', views.part_detail, name='part_detail'),
    path('course/<int:course_id>/part/<int:part_id>/video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('users/', user_list, name='user_list'),
]  

if settings.DEBUG:  # Serve media files in development  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  