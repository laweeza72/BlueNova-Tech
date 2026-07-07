from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Profile, Setting
import json
import html

User = get_user_model()

class ERPTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin user
        self.admin = User.objects.create_superuser(
            username='admin_test',
            email='admin_test@bluenova.com',
            password='testpassword',
            role='admin'
        )
        Profile.objects.create(user=self.admin, full_name='Admin Test', track='Software Engineering', status='approved')
        Setting.objects.create(user=self.admin, theme='dark')
        
        # Create standard Intern user
        self.intern = User.objects.create_user(
            username='intern_test',
            email='intern_test@bluenova.com',
            password='testpassword',
            role='user'
        )
        Profile.objects.create(user=self.intern, full_name='Intern Test', track='Software Engineering', status='pending')
        Setting.objects.create(user=self.intern, theme='dark')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'intern_test',
            'password': 'testpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_login_fail(self):
        response = self.client.post(reverse('login'), {
            'username': 'intern_test',
            'password': 'wrongpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Incorrect password.')

    def test_login_deleted_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'deleted_user',
            'password': 'somepassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'User does not exist.')

    def test_login_disabled_user(self):
        # Create disabled user
        disabled_user = User.objects.create_user(
            username='disabled_test',
            email='disabled_test@bluenova.com',
            password='testpassword',
            role='user',
            is_active=False
        )
        response = self.client.post(reverse('login'), {
            'username': 'disabled_test',
            'password': 'testpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('disabled', response.json()['message'])


    def test_admin_only_view_denied_to_intern(self):
        # Log in as Intern
        self.client.login(username='intern_test', password='testpassword')
        response = self.client.get(reverse('admin_dashboard'))
        # Should redirect to 404 page (or dashboard depending on decorator logic)
        self.assertEqual(response.status_code, 302)

    def test_admin_view_allowed_to_admin(self):
        # Log in as Admin
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_course_detail_resolves_valid_slug(self):
        response = self.client.get(reverse('course_detail', args=['python-development']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Development')

    def test_course_detail_404_invalid_slug(self):
        response = self.client.get(reverse('course_detail', args=['non-existent-course-slug']))
        self.assertEqual(response.status_code, 404)

    def test_internship_application_form_get(self):
        response = self.client.get(reverse('apply') + '?course=django-development')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Development')

    def test_internship_application_form_submit(self):
        # Create a mock resume file
        import io
        mock_file = io.BytesIO(b"dummy resume PDF content")
        mock_file.name = "john_doe_resume.pdf"

        # Submit POST application
        response = self.client.post(reverse('apply'), {
            'full_name': 'John Applicant',
            'email': 'new_applicant@example.com',
            'phone': '1234567890',
            'college': 'Harvard University',
            'branch': 'Computer Science',
            'semester': '6',
            'city': 'Boston',
            'course': 'Python Development',
            'batch': 'July 2026 Cohort',
            'mode': 'Hybrid',
            'resume': mock_file
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify model object creation in SQLite database
        from core.models import InternshipApplication
        self.assertTrue(InternshipApplication.objects.filter(email='new_applicant@example.com').exists())

    def test_admin_applications_auth_required(self):
        # Anonymous user gets redirected to login
        response = self.client.get(reverse('admin_applications'))
        self.assertEqual(response.status_code, 302)

    def test_course_detail_page_loads(self):
        response = self.client.get(reverse('course_detail', args=['python-development']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Development')

    def test_course_detail_page_404(self):
        response = self.client.get(reverse('course_detail', args=['invalid-course-slug']))
        self.assertEqual(response.status_code, 404)

    def test_apply_page_autofills_program(self):
        response = self.client.get(reverse('apply') + '?course=python-development')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['prefilled_course'], 'Python Development')

    def test_apply_success_page_loads(self):
        response = self.client.get(reverse('apply_success') + '?course=Python%20Development')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Development')

    def test_login_via_email(self):
        response = self.client.post(reverse('login'), {
            'username': 'intern_test@bluenova.com',
            'password': 'testpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_login_next_parameter_redirect(self):
        response = self.client.post(reverse('login') + '?next=/courses/python-development/', {
            'username': 'intern_test',
            'password': 'testpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['redirect'], '/courses/python-development/')

    def test_forgot_password_and_reset_password_workflow(self):
        # 1. Forgot password lookup
        response = self.client.post(reverse('forgot_password'), {
            'email': 'intern_test@bluenova.com'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify session stores the email
        session = self.client.session
        self.assertEqual(session.get('reset_email'), 'intern_test@bluenova.com')

        # 2. Reset password
        response = self.client.post(reverse('reset_password'), {
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # 3. Test that old password fails
        login_fail = self.client.post(reverse('login'), {
            'username': 'intern_test',
            'password': 'testpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(login_fail.status_code, 400)

        # 4. Test that new password succeeds
        login_success = self.client.post(reverse('login'), {
            'username': 'intern_test',
            'password': 'newpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(login_success.status_code, 200)
        self.assertTrue(login_success.json()['success'])

    def test_attendance_admin_only_access(self):
        # Intern login
        self.client.login(username='intern_test', password='testpassword')
        response = self.client.get(reverse('attendance_dashboard'))
        self.assertEqual(response.status_code, 302)  # redirects (denied)

        # Admin login
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.get(reverse('attendance_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_attendance_marking_and_duplicate_prevention(self):
        self.client.login(username='admin_test', password='testpassword')
        
        # Mark attendance via POST
        post_data = {
            'date': '2026-07-10',
            'track': 'Software Engineering',
            f'status_{self.intern.id}': 'present',
            f'remarks_{self.intern.id}': 'Excellent work today'
        }
        response = self.client.post(reverse('attendance_mark'), post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Verify record exists in DB
        from core.models import Attendance
        att = Attendance.objects.get(student=self.intern, date='2026-07-10')
        self.assertEqual(att.status, 'present')
        self.assertEqual(att.remarks, 'Excellent work today')

        # Try marking again for same student and date (duplicate prevention / editing)
        post_data_edit = {
            'date': '2026-07-10',
            'track': 'Software Engineering',
            f'status_{self.intern.id}': 'late',
            f'remarks_{self.intern.id}': 'Late by 10 minutes'
        }
        response = self.client.post(reverse('attendance_mark'), post_data_edit, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Verify updated record and no duplication
        att_updated = Attendance.objects.filter(student=self.intern, date='2026-07-10')
        self.assertEqual(att_updated.count(), 1)
        self.assertEqual(att_updated.first().status, 'late')
        self.assertEqual(att_updated.first().remarks, 'Late by 10 minutes')

    def test_user_reports_only_shows_own_attendance(self):
        # Create attendance records for intern
        from core.models import Attendance
        Attendance.objects.create(
            student=self.intern,
            date='2026-06-10',
            status='present',
            internship_track='Software Engineering',
            marked_by=self.admin
        )
        
        # Log in as intern
        self.client.login(username='intern_test', password='testpassword')
        response = self.client.get(reverse('attendance_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Attendance Report')
        self.assertContains(response, 'Present')

        # Admin report check (admin redirect to admin attendance dashboard)
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.get(reverse('attendance_report'))
        self.assertEqual(response.status_code, 302)  # Redirects to admin attendance dashboard


