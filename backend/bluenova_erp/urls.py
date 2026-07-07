from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from core.views import page_404, get_erp_context, course_detail_view, apply_view, apply_success_view

def public_view(template_name):
    def view_func(request):
        context = {}
        if request.user.is_authenticated:
            context.update(get_erp_context(request))
        return render(request, template_name, context)
    return view_func

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # Public Pages
    path('', public_view('index.html'), name='home'),
    path('about/', public_view('about.html'), name='about'),
    path('contact/', public_view('contact.html'), name='contact'),
    path('courses/apply/success/', apply_success_view, name='apply_success'),
    path('courses/apply/', apply_view, name='apply'),
    path('courses/<slug:course_slug>/', course_detail_view, name='course_detail'),
    path('services/', public_view('services.html'), name='services'),
    path('internships/', public_view('internships.html'), name='internships'),
    path('training/', public_view('training.html'), name='training'),
    path('portfolio/', public_view('portfolio.html'), name='portfolio'),
    path('gallery/', public_view('gallery.html'), name='gallery'),
    path('pricing/', public_view('pricing.html'), name='pricing'),
    path('careers/', public_view('careers.html'), name='careers'),
    path('certificates/', public_view('certificates.html'), name='certificates'),
    path('placements/', public_view('placements.html'), name='placements'),
    path('success-stories/', public_view('success-stories.html'), name='success_stories'),
    path('testimonials/', public_view('testimonials.html'), name='testimonials'),
    path('technologies/', public_view('technologies.html'), name='technologies'),
    path('team/', public_view('team.html'), name='team'),
    path('events/', public_view('events.html'), name='events'),
    path('blog/', public_view('blog.html'), name='blog'),
    path('faq/', public_view('faq.html'), name='faq'),
    path('privacy/', public_view('privacy.html'), name='privacy'),
    path('terms/', public_view('terms.html'), name='terms'),
    path('refund-policy/', public_view('refund-policy.html'), name='refund_policy'),
    path('help-center-public/', public_view('help-center-public.html'), name='help_center_public'),
    path('sitemap/', public_view('sitemap.html'), name='sitemap'),
    
    # Authentications
    path('auth/', include('authentication.urls')),
    
    # Primary ERP System
    path('erp/', include('core.urls')),
    path('erp/', include('resume.urls')),
    path('404/', page_404, name='page_404'),

]

# Custom 404 handler
handler404 = page_404

# Serve Media/Static files in Dev environment
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
