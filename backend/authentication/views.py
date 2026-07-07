from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .models import User
from core.models import Profile, Setting, History, ActivityLog


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(user, action, request):
    ActivityLog.objects.create(
        user=user,
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        username_val = request.POST.get('username', '').strip().lower()
        password_val = request.POST.get('password', '')
        next_url = request.GET.get('next', '').strip() or request.POST.get('next', '').strip()

        if next_url and not next_url.startswith('/'):
            next_url = ''

        if not username_val or not password_val:
            return JsonResponse({'success': False, 'message': 'Missing fields. Please enter both username/email and password.'}, status=400)

        # 1. Search database & Check user existence
        try:
            if '@' in username_val:
                user_obj = User.objects.get(email=username_val)
            else:
                user_obj = User.objects.get(username=username_val)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User does not exist.'}, status=404)

        # 2. Check disabled account
        if not user_obj.is_active:
            return JsonResponse({'success': False, 'message': 'Your account has been disabled.'}, status=400)

        # 3. Verify password
        user = authenticate(request, username=user_obj.username, password=password_val)
        if user is None:
            return JsonResponse({'success': False, 'message': 'Incorrect password.'}, status=400)

        # 4. Login successful
        auth_login(request, user)
        log_action(user, "User logged in", request)

        try:
            setting = Setting.objects.get(user=user)
            request.session['theme'] = setting.theme
        except Setting.DoesNotExist:
            Setting.objects.create(user=user)
            request.session['theme'] = 'dark'

        if next_url:
            redirect_url = next_url
        elif user.role == 'admin':
            redirect_url = '/erp/admin-dashboard/'
        else:
            redirect_url = '/erp/dashboard/'

        return JsonResponse({'success': True, 'redirect': redirect_url})

    return render(request, 'login.html')


@csrf_protect
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip().lower()
        fullname = request.POST.get('fullname', '').strip()
        track = request.POST.get('track', '')
        academic = request.POST.get('academic', '').strip()
        bio = request.POST.get('bio', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not fullname or not password:
            return JsonResponse({'success': False, 'message': 'Missing fields. Required fields must be completed.'}, status=400)

        if confirm_password and password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match.'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists.'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email address already registered.'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password, role='user')

        Profile.objects.create(
            user=user,
            full_name=fullname,
            track=track,
            academic_background=academic,
            bio=bio,
            status='pending'
        )
        Setting.objects.create(user=user, theme='dark')

        History.objects.create(
            user=user,
            milestone_name="Application Submitted",
            description="Your internship request has been successfully filed in the recruitment panel."
        )

        log_action(user, "User signed up", request)

        return JsonResponse({
            'success': True,
            'message': 'Registration successful! Please log in.',
            'redirect': '/auth/login/'
        })

    return render(request, 'signup.html')


def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, "User logged out", request)
    auth_logout(request)
    return redirect('login')


@csrf_protect
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            return JsonResponse({'success': False, 'message': 'Please enter your email address.'}, status=400)

        try:
            user = User.objects.get(email=email)
            request.session['reset_email'] = email
            return JsonResponse({
                'success': True,
                'message': 'Account verified. Redirecting to reset your password...',
                'redirect': '/auth/reset-password/'
            })
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Email address not found in system.'}, status=400)

    return render(request, 'forgot-password.html')


@csrf_protect
def reset_password_view(request):
    reset_email = request.session.get('reset_email')
    if not reset_email:
        messages.error(request, "Please verify your email address first.")
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not password or not confirm_password:
            return JsonResponse({'success': False, 'message': 'Please fill out both password fields.'}, status=400)

        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match.'}, status=400)

        if len(password) < 6:
            return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters.'}, status=400)

        try:
            user = User.objects.get(email=reset_email)
            user.set_password(password)
            user.save()

            # Clear recovery session context
            request.session.pop('reset_email', None)

            return JsonResponse({
                'success': True,
                'message': 'Password updated successfully! Redirecting to login...',
                'redirect': '/auth/login/'
            })
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User profile resolution error.'}, status=400)

    return render(request, 'reset-password.html')


@login_required
@csrf_protect
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        email = user.email
        
        # Delete user (cascades to Profile, Setting, History, UploadedFile, Attendance, GeneratedResume, etc.)
        user.delete()
        
        # Delete any associated internship application records to clear credentials
        from core.models import InternshipApplication
        InternshipApplication.objects.filter(email=email).delete()
        
        # Log out to clear session
        auth_logout(request)
        
        return JsonResponse({'success': True, 'message': 'Account deleted successfully.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

