# forms.py  
from django import forms  
from django.contrib.auth.models import User  
from django.contrib.auth.forms import (
    AuthenticationForm, 
    PasswordChangeForm, 
    PasswordResetForm, 
    SetPasswordForm
)
from .models import UserProfile, SupportTicket, TicketResponse, Payment


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور خود را وارد کنید'
        })
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور را مجددا وارد کنید'
        })
    )
    phone = forms.CharField(
        label='شماره تلفن',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره تلفن خود را وارد کنید'
        })
    )
    level = forms.ChoiceField(
        label='انتخاب سطح',
        choices=[
            ('مقدماتی و متوسط', 'مقدماتی و متوسط'),
            ('خوش', 'خوش'),
            ('عالی و ممتاز', 'عالی و ممتاز'),
            ('فوق ممتاز', 'فوق ممتاز')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام کاربری'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل'
            }),
        }
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل'
        }
        help_texts = {
            'username': None,
            'email': None
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('رمز عبور و تکرار آن مطابقت ندارند!')
        return cd['password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('09') or len(phone) != 11:
            raise forms.ValidationError('شماره تلفن باید با ۰۹ شروع شود و ۱۱ رقم باشد.')
        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username exists (case-insensitive)
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError('این نام کاربری قبلا ثبت شده است.')
        return username.lower()  # Convert to lowercase

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام کاربری'
        }),
        label='نام کاربری'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور'
        }),
        label='رمز عبور'
    )

    error_messages = {
        'invalid_login': 'لطفا نام کاربری و رمز عبور صحیح را وارد کنید. توجه داشته باشید که هر دو فیلد به حروف بزرگ و کوچک حساس نیستند.',
        'inactive': 'این حساب کاربری غیرفعال است.'
    }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.lower()
        return username

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'پسورد فعلی'
        }),
        label='پسورد فعلی'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'پسورد جدید'
        }),
        label='پسورد جدید'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'تکرار پسورد جدید'
        }),
        label='تکرار پسورد جدید'
    )

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ایمیل خود را وارد کنید'
        }),
        label='ایمیل'
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'پسورد جدید'
        }),
        label='پسورد جدید'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'تکرار پسورد جدید'
        }),
        label='تکرار پسورد جدید'
    )

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل'
            }),
        }
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل'
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'phone', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره تماس'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'درباره من',
                'rows': 3
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'profile_image': 'تصویر پروفایل',
            'phone': 'شماره تماس',
            'bio': 'درباره من'
        }

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message', 'priority']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'پیام خود را بنویسید',
                'rows': 4
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'subject': 'موضوع',
            'message': 'پیام',
            'priority': 'اولویت'
        }

class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'پاسخ خود را بنویسید',
                'rows': 3
            })
        }
        labels = {
            'message': 'پاسخ'
        }

class PaymentForm(forms.ModelForm):
    receipt = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='تصویر رسید پرداخت'
    )

    class Meta:
        model = Payment
        fields = ['receipt']
        exclude = ['user', 'course', 'amount', 'status', 'admin_notes']
