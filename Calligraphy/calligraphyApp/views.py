from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse, FileResponse, StreamingHttpResponse
from .models import *
from .forms import *
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout  
import logging  
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied
import os
from wsgiref.util import FileWrapper
import mimetypes
from django.db.transaction import atomic
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from django.db.models import Sum
from django.utils import timezone

# Set up logger
logger = logging.getLogger(__name__)

#
#def login(request):  
#    if request.method == 'POST':  
#        form = AuthenticationForm(data=request.POST)  
#        if form.is_valid():  
#            username = form.cleaned_data.get('username')  
#            password = form.cleaned_data.get('password')  
#            user = authenticate(username=username, password=password)  
#            if user is not None:  
#                auth_login(request, user)  
#                return redirect('home')  
#            else:  
#                messages.error(request, "Invalid username or password.")    
#        else:  
#            messages.error(request, "There was a problem with your submission.")  
#    else:  
#        form = AuthenticationForm()  
#    return render(request, 'calligraphyApp/registration/login.html', {'form': form})  
#
def user_login(request):
    if request.method == "POST":  
        form = LoginForm(request.POST)  
        if form.is_valid():  
            cd = form.cleaned_data  
            user = authenticate(username=cd['username'], password=cd['password'])  
            if user is not None:  
                if user.is_active:  
                    login(request, user)  # Log the user in  
                    messages.success(request, "خوش آمدید!")  # Welcome message
                    return redirect('calligraphyApp:home')  # Redirect to home with namespace  
                else: 
                    logger.warning(f"User {cd['username']} tried to log in but is inactive.")  
                    messages.error(request, "حساب کاربری شما غیرفعال است.")  
            else:
                logger.warning(f"Failed login attempt for {cd['username']}.")  
                messages.error(request, "نام کاربری یا رمز عبور نامعتبر است.")  
    else:  
        form = LoginForm()  
    
    return render(request, 'calligraphyApp/registration/login.html', {'form': form})  


#def register(request):  
#    if request.method == 'POST':  
#        form = UserRegistrationForm(request.POST)  
#        if form.is_valid():  
#            form.save()  # Save the new user  
#            username = form.cleaned_data.get('username')  
#            messages.success(request, f'Your account has been created! You can now log in.')  
#            return redirect('login')  # Redirect to the login page after successful registration  
#    else:  
#        form = UserRegistrationForm()  
#    return render(request, 'calligraphyApp/registration/register.html', {'form': form})  


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                level=form.cleaned_data['level']
            )
            messages.success(request, "ثبت نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.")
            return redirect('calligraphyApp:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'calligraphyApp/registration/register.html', {'form': form})

def log_out(request):
    logout(request)
    messages.success(request, "با موفقیت خارج شدید.")
    return redirect('calligraphyApp:home')

@login_required
def profile_view(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's enrolled courses
    enrolled_courses = CourseEnrollment.objects.filter(user=request.user).select_related('course')
    
    # Get user's support tickets
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'enrolled_courses': enrolled_courses,
        'tickets': tickets,
    }
    return render(request, 'calligraphyApp/profile.html', context)

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "پروفایل شما با موفقیت به‌روزرسانی شد.")
            return redirect('calligraphyApp:profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)
    
    return render(request, 'calligraphyApp/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "تیکت شما با موفقیت ثبت شد.")
            return redirect('calligraphyApp:ticket_detail', ticket_id=ticket.id)
    else:
        form = SupportTicketForm()
    
    return render(request, 'calligraphyApp/create_ticket.html', {'form': form})

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    responses = ticket.responses.all().order_by('created_at')
    
    if request.method == 'POST':
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.user = request.user
            response.save()
            messages.success(request, "پاسخ شما با موفقیت ثبت شد.")
            return redirect('calligraphyApp:ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketResponseForm()
    
    return render(request, 'calligraphyApp/ticket_detail.html', {
        'ticket': ticket,
        'responses': responses,
        'form': form
    })

@login_required
def ticket_list(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'calligraphyApp/ticket_list.html', {'tickets': tickets})

def course_list(request):
    courses = Course.objects.filter(is_active=True).prefetch_related('parts__videos')
    
    # Prepare course data with free video information
    courses_data = []
    for course in courses:
        free_videos_count = sum(
            1 for part in course.parts.all()
            for video in part.videos.all()
            if video.is_free
        )
        
        courses_data.append({
            'course': course,
            'free_videos_count': free_videos_count,
        })
    
    return render(request, 'calligraphyApp/course_list.html', {
        'courses_data': courses_data,
        'user_authenticated': request.user.is_authenticated
    })

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = False
    has_purchased = False
    
    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
        has_purchased = CourseEnrollment.objects.filter(user=request.user, course=course, is_paid=True).exists()
    
    # Get all parts with their videos
    parts = course.parts.prefetch_related('videos').all()
    
    # For each part, mark first two videos as free if they're in part 1 or 2
    for part in parts:
        if part.order <= 2:  # Only for first two parts
            videos = list(part.videos.all())
            if len(videos) >= 1:
                videos[0].is_free = True
                videos[0].save()
            if len(videos) >= 2:
                videos[1].is_free = True
                videos[1].save()
    
    context = {
        'course': course,
        'parts': parts,
        'is_enrolled': is_enrolled,
        'has_purchased': has_purchased,
        'user_authenticated': request.user.is_authenticated
    }
    return render(request, 'calligraphyApp/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        CourseEnrollment.objects.create(user=request.user, course=course)
        messages.success(request, f"شما با موفقیت در دوره {course.title} ثبت‌نام شدید.")
    return redirect('calligraphyApp:course_detail', course_id=course.id)

@login_required
def part_detail(request, course_id, part_id):
    part = get_object_or_404(Part, id=part_id, course_id=course_id)
    videos = part.videos.all()
    return render(request, 'calligraphyApp/part_detail.html', {
        'part': part,
        'videos': videos
    })

@login_required
def video_detail(request, course_id, part_id, video_id):
    video = get_object_or_404(Video, id=video_id, part_id=part_id)
    return render(request, 'calligraphyApp/video_detail.html', {'video': video})

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'calligraphyApp/user_list.html', {'users': users})

@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user already purchased the course
    if CourseEnrollment.objects.filter(user=request.user, course=course, is_paid=True).exists():
        messages.warning(request, "شما قبلاً این دوره را خریداری کرده‌اید.")
        return redirect('calligraphyApp:course_detail', course_id=course.id)
    
    # Get or create pending order
    order, created = Order.objects.get_or_create(
        user=request.user,
        status='pending'
    )
    
    # Check if course already in cart
    if not OrderItem.objects.filter(order=order, course=course).exists():
        OrderItem.objects.create(
            order=order,
            course=course,
            price=course.price
        )
        order.total_amount = order.calculate_total()
        order.save()
        messages.success(request, "دوره به سبد خرید اضافه شد.")
    else:
        messages.info(request, "این دوره قبلاً به سبد خرید اضافه شده است.")
    
    return redirect('calligraphyApp:cart')

@login_required
def cart(request):
    order = Order.objects.filter(
        user=request.user,
        status='pending'
    ).first()
    
    context = {
        'order': order,
        'cart_items': [],
        'total_price': 0,
        'final_price': 0,
        'has_discount': False,
        'discount_code': None,
        'discount_amount': 0
    }
    
    if order:
        # Prepare cart items with video counts
        cart_items = []
        total_price = 0
        
        for item in order.items.all():
            videos_count = sum(1 for part in item.course.parts.all() for _ in part.videos.all())
            cart_items.append({
                'course': item.course,
                'price': item.price,
                'videos_count': videos_count,
                'id': item.id
            })
            total_price += item.price
        
        # Check for discount in session
        discount_code = request.session.get('discount_code')
        discount_amount = request.session.get('discount_amount', 0)
        
        context.update({
            'cart_items': cart_items,
            'total_price': total_price,
            'final_price': max(0, total_price - discount_amount),
            'has_discount': bool(discount_code),
            'discount_code': discount_code,
            'discount_amount': discount_amount
        })
    
    return render(request, 'calligraphyApp/cart.html', context)

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    order = item.order
    item.delete()
    
    if order.items.count() == 0:
        order.delete()
        return redirect('calligraphyApp:course_list')
    
    order.total_amount = order.calculate_total()
    order.save()
    messages.success(request, "آیتم از سبد خرید حذف شد.")
    return redirect('calligraphyApp:cart')

@login_required
def checkout(request):
    order = get_object_or_404(Order, user=request.user, status='pending')
    
    # Here you would integrate with your payment gateway
    # For now, we'll simulate a successful payment
    try:
        with atomic():
            order.status = 'paid'
            order.save()
            
            # Create enrollments for purchased courses
            for item in order.items.all():
                CourseEnrollment.objects.create(
                    user=request.user,
                    course=item.course,
                    is_paid=True,
                    order=order
                )
            
            messages.success(request, "پرداخت با موفقیت انجام شد. اکنون می‌توانید به دوره‌های خریداری شده دسترسی داشته باشید.")
            return redirect('calligraphyApp:profile')
    except Exception as e:
        messages.error(request, "خطا در پردازش پرداخت. لطفاً دوباره تلاش کنید.")
        return redirect('calligraphyApp:cart')

@login_required
def apply_discount(request):
    """
    Apply a discount code to the user's current order.
    """
    if request.method == 'POST':
        discount_code = request.POST.get('discount_code')
        
        # Get the pending order
        order = Order.objects.filter(
            user=request.user,
            status='pending'
        ).first()
        
        if not order:
            messages.error(request, "سبد خرید شما خالی است.")
            return redirect('calligraphyApp:cart')
        
        # Here you would check if the discount code is valid
        # For now, we'll apply a simple 10% discount for any code
        if discount_code:
            # Store the discount code in the session for now
            request.session['discount_code'] = discount_code
            request.session['discount_amount'] = int(order.total_amount * 0.1)  # 10% discount
            
            messages.success(request, f"کد تخفیف '{discount_code}' با موفقیت اعمال شد.")
        else:
            messages.error(request, "لطفاً کد تخفیف را وارد کنید.")
        
        return redirect('calligraphyApp:cart')
    
    return redirect('calligraphyApp:cart')

@login_required
def remove_discount(request):
    """
    Remove the applied discount code from the user's current order.
    """
    if 'discount_code' in request.session:
        del request.session['discount_code']
    
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    
    messages.success(request, "کد تخفیف با موفقیت حذف شد.")
    return redirect('calligraphyApp:cart')

@login_required
def clear_cart(request):
    """
    Clear all items from the user's shopping cart.
    """
    order = Order.objects.filter(
        user=request.user,
        status='pending'
    ).first()
    
    if order:
        order.delete()
        messages.success(request, "سبد خرید شما با موفقیت خالی شد.")
    
    return redirect('calligraphyApp:cart')

def ranged(file, start=0, end=None, block_size=8192):
    consumed = 0
    file.seek(start)
    while True:
        remaining_bytes = end - start - consumed if end else block_size
        data = file.read(min(remaining_bytes, block_size) if end else block_size)
        if not data:
            break
        consumed += len(data)
        yield data
        if end and consumed >= end - start:
            break

@login_required(login_url=None)
def protected_video_view(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    quality = request.GET.get('quality', 'high')  # Default to high quality if not specified
    
    # Check if user has access to this video
    if not video.is_free:
        enrollment = CourseEnrollment.objects.filter(
            user=request.user,
            course=video.part.course,
            is_paid=True
        ).exists()
        if not enrollment:
            raise PermissionDenied("شما به این ویدیو دسترسی ندارید.")

    try:
        # First try the original path (video_file.path)
        path = video.video_file.path
        
        # If the file doesn't exist at the original path, try to find it in alphabet_videos
        if not os.path.exists(path):
            logger.warning(f"Video file not found at {path}. Attempting to find in alphabet_videos.")
            
            # Extract filename from the original path
            filename = os.path.basename(path)
            
            # Try to find the video in alphabet_videos directory
            # Check if the path contains a folder structure like "New folder/نقطه/(1)نقطه.mp4"
            if "New folder" in path and "/" in path:
                # Extract the subfolder name
                parts = path.split('/')
                for i, part in enumerate(parts):
                    if part == "New folder" and i+1 < len(parts):
                        subfolder = parts[i+1]
                        # Construct a new path to check
                        new_path = os.path.join(settings.MEDIA_ROOT, 'alphabet_videos', subfolder, filename)
                        if os.path.exists(new_path):
                            logger.info(f"Video file found at alternative location: {new_path}")
                            path = new_path
                            break
        
        # If the file still doesn't exist after all our attempts
        if not os.path.exists(path):
            messages.error(request, "فایل ویدیویی مورد نظر یافت نشد. لطفا با پشتیبانی تماس بگیرید.")
            logger.error(f"Video file not found for video_id={video_id}. Attempted paths include: {path}")
            return redirect('calligraphyApp:course_detail', course_id=video.part.course.id)
            
        # Define our response headers to prevent download and caching on client side
        response_headers = {
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
        
        # Add Content-Disposition header for better browser handling - forcing inline display
        filename = os.path.basename(path)
        response_headers['Content-Disposition'] = f'inline; filename="{filename}"'
            
        size = os.path.getsize(path)
        content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'

        # Handle range request
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        
        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte)
            last_byte = int(last_byte) if last_byte else size - 1
            if last_byte >= size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            
            resp = StreamingHttpResponse(
                ranged(open(path, 'rb'), start=first_byte, end=last_byte + 1),
                status=206,
                content_type=content_type
            )
            
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
        else:
            resp = StreamingHttpResponse(
                ranged(open(path, 'rb')),
                content_type=content_type
            )
            resp['Content-Length'] = str(size)
        
        # Apply all security headers
        for header, value in response_headers.items():
            resp[header] = value
        
        return resp
        
    except Exception as e:
        logger.exception(f"Error serving video_id={video_id}: {str(e)}")
        messages.error(request, "خطا در پخش ویدیو. لطفا با پشتیبانی تماس بگیرید.")
        return redirect('calligraphyApp:course_detail', course_id=video.part.course.id)

def teacher_profile(request):
    """
    View function for displaying the teacher (Hamidreza Tavakoli) profile page.
    """
    # You can add any data you want to pass to the template here
    context = {
        'teacher_name': 'حمیدرضا توکلی',
        'teacher_title': 'استاد خوشنویسی',
        'teacher_bio': 'استاد حمیدرضا توکلی، یکی از برجسته‌ترین خوشنویسان معاصر ایران با بیش از 20 سال تجربه در زمینه آموزش و اجرای هنر خوشنویسی فارسی می‌باشد. ایشان دارای مدرک درجه یک هنری از انجمن خوشنویسان ایران هستند و افتخارات متعددی را در این زمینه کسب کرده‌اند.',
        'teacher_about': 'استاد توکلی تحصیلات خود را در رشته هنرهای تجسمی با تمرکز بر خوشنویسی به پایان رسانده و از محضر استادان بزرگی چون استاد امیرخانی و استاد فلاح بهره‌مند شده‌اند. ایشان با تلفیق شیوه‌های سنتی و نوین، روش آموزشی منحصر به فردی را ارائه می‌دهند که به هنرجویان امکان پیشرفت سریع و اصولی را می‌دهد. علاوه بر خوشنویسی، ایشان در زمینه تذهیب و نقاشی ایرانی نیز فعالیت دارند و آثار ایشان در نمایشگاه‌های متعددی به نمایش درآمده است.',
        'specialties': [
            'خط نستعلیق',
            'خط شکسته نستعلیق',
            'خط ثلث',
            'خط نسخ',
            'خط کوفی',
            'تذهیب'
        ],
        'awards': [
            'نشان درجه یک هنری از انجمن خوشنویسان ایران (1395)',
            'برگزیده جشنواره بین‌المللی خوشنویسی استانبول (1392)',
            'مقام اول مسابقات کشوری خوشنویسی (1390)',
            'استاد برگزیده دانشگاه هنر تهران (1388)'
        ],
        'experience': [
            {
                'title': 'مدرس ارشد',
                'organization': 'انجمن خوشنویسان ایران',
                'period': '1390 تا کنون'
            },
            {
                'title': 'مدیر هنری',
                'organization': 'مرکز هنرهای تجسمی حوزه هنری',
                'period': '1387-1392'
            },
            {
                'title': 'مدرس',
                'organization': 'دانشگاه هنر تهران',
                'period': '1388 تا کنون'
            },
        ],
        'education': [
            {
                'degree': 'دکترای هنرهای تجسمی',
                'school': 'دانشگاه هنر تهران',
                'year': '1385'
            },
            {
                'degree': 'کارشناسی ارشد خوشنویسی',
                'school': 'دانشگاه تربیت مدرس',
                'year': '1380'
            },
        ],
        'courses_count': 12,
        'students_count': 1500,
        'avg_rating': 4.8,
        # Add more data as needed
    }
    return render(request, 'calligraphyApp/teacher_profile.html', context)

@login_required
def payment_process(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Get the global card number
    site_setting, _ = SiteSetting.objects.get_or_create(id=1)
    card_number = site_setting.card_number
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.course = course
            payment.amount = course.price
            payment.save()
            
            messages.success(request, 'پرداخت شما با موفقیت ثبت شد و در انتظار تایید است.')
            return redirect('calligraphyApp:payment_list')
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'course': course,
        'amount': course.price,
        'card_number': card_number,
    }
    return render(request, 'calligraphyApp/payment_process.html', context)

@login_required
def payment_list(request):
    payments = Payment.objects.filter(user=request.user).select_related('course')
    return render(request, 'calligraphyApp/payment_list.html', {'payments': payments})

@login_required
def admin_payment_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    
    payments = Payment.objects.all().select_related('user', 'course')
    return render(request, 'calligraphyApp/admin_payment_list.html', {'payments': payments})

@login_required
def admin_payment_detail(request, payment_id):
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        # Log the attempt to access payment detail
        logger.info(f"Admin user {request.user.username} is accessing payment ID {payment_id}")
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'approve':
                payment.status = 'approved'
                
                # Create or update CourseEnrollment when payment is approved
                enrollment, created = CourseEnrollment.objects.get_or_create(
                    user=payment.user,
                    course=payment.course,
                    defaults={'is_paid': True}
                )
                
                # If enrollment already existed but wasn't paid, update it
                if not created and not enrollment.is_paid:
                    enrollment.is_paid = True
                    enrollment.save()
                    
                messages.success(request, 'پرداخت با موفقیت تایید شد و دسترسی کاربر به دوره فعال شد.')
            elif action == 'reject':
                payment.status = 'rejected'
                messages.warning(request, 'پرداخت رد شد.')
            
            payment.admin_notes = request.POST.get('admin_notes', '')
            payment.save()
            return redirect('calligraphyApp:admin_payment_list')
        
        return render(request, 'calligraphyApp/admin_payment_detail.html', {'payment': payment})
    except Http404:
        logger.error(f"Payment with ID {payment_id} was not found when accessed by {request.user.username}")
        messages.error(request, f"پرداخت با شناسه {payment_id} یافت نشد.")
        return redirect('calligraphyApp:admin_payment_list')
    except Exception as e:
        logger.error(f"Error accessing payment ID {payment_id}: {str(e)}")
        messages.error(request, "خطایی در بازیابی اطلاعات پرداخت رخ داد.")
        return redirect('calligraphyApp:admin_payment_list')

@login_required
def update_payment_status(request, payment_id):
    if not request.user.is_staff:
        raise PermissionDenied
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [choice[0] for choice in Payment.PAYMENT_STATUS]:
            payment.status = status
            payment.save()
            
            # If payment is approved, create or update course enrollment
            if status == 'approved':
                # Create or update CourseEnrollment when payment is approved
                enrollment, created = CourseEnrollment.objects.get_or_create(
                    user=payment.user,
                    course=payment.course,
                    defaults={'is_paid': True}
                )
                
                # If enrollment already existed but wasn't paid, update it
                if not created and not enrollment.is_paid:
                    enrollment.is_paid = True
                    enrollment.save()
                
                messages.success(request, f'وضعیت پرداخت به {payment.get_status_display()} تغییر یافت و دسترسی کاربر به دوره فعال شد.')
            else:
                messages.success(request, f'وضعیت پرداخت به {payment.get_status_display()} تغییر یافت.')
        else:
            messages.error(request, 'وضعیت نامعتبر.')
    
    return redirect('calligraphyApp:admin_dashboard')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
        return redirect('calligraphyApp:home')

    # Get or create the global site setting
    site_setting, _ = SiteSetting.objects.get_or_create(id=1)

    # Handle card number update
    if request.method == 'POST' and 'card_number' in request.POST:
        card_number = request.POST.get('card_number', '').strip()
        site_setting.card_number = card_number
        site_setting.save()
        messages.success(request, 'شماره کارت با موفقیت ذخیره شد.')

    # Get statistics
    total_users = User.objects.count()
    active_courses = Course.objects.filter(is_active=True).count()
    monthly_income = Payment.objects.filter(
        created_at__month=timezone.now().month,
        status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0
    open_tickets = SupportTicket.objects.filter(status='open').count()

    # Get recent activities
    recent_activities = []
    recent_payments = Payment.objects.select_related('user', 'course').order_by('-created_at')[:5]
    for payment in recent_payments:
        recent_activities.append({
            'icon': 'fa-credit-card',
            'text': f'پرداخت جدید از {payment.user.username} برای دوره {payment.course.title}',
            'time': payment.created_at
        })

    # Get payments for the payments section
    payments = Payment.objects.select_related('user', 'course').order_by('-created_at')

    # Get courses for the courses section
    courses = Course.objects.all()

    # Get users for the users section
    users = User.objects.all()

    # Get tickets for the support section
    tickets = SupportTicket.objects.select_related('user').order_by('-created_at')

    context = {
        'total_users': total_users,
        'active_courses': active_courses,
        'monthly_income': monthly_income,
        'open_tickets': open_tickets,
        'recent_activities': recent_activities,
        'payments': payments,
        'courses': courses,
        'users': users,
        'tickets': tickets,
        'card_number': site_setting.card_number,
    }

    return render(request, 'calligraphyApp/admin_dashboard.html', context)

@login_required
def payment_debug(request):
    if not request.user.is_staff:
        raise PermissionDenied
    
    payments = Payment.objects.all().order_by('id')
    payment_info = [
        {
            'id': p.id,
            'user': p.user.username,
            'course': p.course.title,
            'amount': p.amount,
            'status': p.get_status_display(),
            'created_at': p.created_at
        }
        for p in payments
    ]
    
    return render(request, 'calligraphyApp/payment_debug.html', {'payments': payment_info})