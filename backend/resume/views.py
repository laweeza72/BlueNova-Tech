"""
Resume Builder Views
--------------------
All views for the /erp/resume/ section of the BlueNova ERP.
"""

import json
import pathlib
import traceback
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.core.files.base import ContentFile

from .models import (
    ResumeProfile, SocialNetwork, ResumeSection,
    EducationEntry, ExperienceEntry, ProjectEntry,
    PublicationEntry, SkillEntry, BulletEntry, NormalEntry,
    GeneratedResume, THEME_CHOICES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_profile(user) -> ResumeProfile:
    profile, _ = ResumeProfile.objects.get_or_create(user=user)
    return profile


def _profile_to_dict(profile: ResumeProfile) -> dict:
    """Serialize a full ResumeProfile into a JSON-safe dict for the frontend."""
    sections_data = []
    for section in profile.sections.all():
        s_data = {
            'id': section.id,
            'title': section.title,
            'entry_type': section.entry_type,
            'order': section.order,
            'entries': [],
        }
        etype = section.entry_type

        if etype == 'education':
            for e in section.education_entries.all():
                s_data['entries'].append({
                    'id': e.id, 'institution': e.institution, 'area': e.area,
                    'degree': e.degree, 'location': e.location,
                    'start_date': e.start_date, 'end_date': e.end_date,
                    'single_date': e.single_date, 'summary': e.summary,
                    'gpa': getattr(e, 'gpa', ''),
                    'highlights': e.highlights, 'order': e.order,
                })
        elif etype == 'experience':
            for e in section.experience_entries.all():
                s_data['entries'].append({
                    'id': e.id, 'company': e.company, 'position': e.position,
                    'location': e.location, 'start_date': e.start_date,
                    'end_date': e.end_date, 'single_date': e.single_date,
                    'summary': e.summary, 'highlights': e.highlights, 'order': e.order,
                })
        elif etype == 'project':
            for e in section.project_entries.all():
                s_data['entries'].append({
                    'id': e.id, 'name': e.name, 'url': e.url,
                    'location': e.location, 'start_date': e.start_date,
                    'end_date': e.end_date, 'single_date': e.single_date,
                    'summary': e.summary, 'highlights': e.highlights, 'order': e.order,
                })
        elif etype == 'publication':
            for e in section.publication_entries.all():
                s_data['entries'].append({
                    'id': e.id, 'title': e.title, 'authors': e.authors,
                    'journal': e.journal, 'doi': e.doi, 'url': e.url,
                    'date': e.date, 'order': e.order,
                })
        elif etype == 'skill':
            for e in section.skill_entries.all():
                s_data['entries'].append({
                    'id': e.id, 'label': e.label, 'details': e.details, 'order': e.order,
                })
        elif etype == 'bullet':
            for e in section.bullet_entries.all():
                s_data['entries'].append({
                    'id': e.id, 'bullet': e.bullet, 'order': e.order,
                })
        elif etype == 'normal':
            for e in section.normal_entries.all():
                s_data['entries'].append({
                    'id': e.id, 'name': e.name, 'location': e.location,
                    'start_date': e.start_date, 'end_date': e.end_date,
                    'single_date': e.single_date, 'summary': e.summary,
                    'highlights': e.highlights, 'order': e.order,
                })

        sections_data.append(s_data)

    return {
        'full_name': profile.full_name,
        'headline': profile.headline,
        'location': profile.location,
        'email': profile.email,
        'phone': profile.phone,
        'website': profile.website,
        'selected_theme': profile.selected_theme,
        'has_photo': bool(profile.photo),
        'photo_url': profile.photo.url if profile.photo else None,
        'social_networks': [
            {'id': sn.id, 'network': sn.network, 'username': sn.username, 'order': sn.order}
            for sn in profile.social_networks.all()
        ],
        'sections': sections_data,
    }


# ---------------------------------------------------------------------------
# Main Page
# ---------------------------------------------------------------------------

@login_required
def resume_builder(request):
    """Render the multi-step resume builder page."""
    profile = _get_or_create_profile(request.user)
    profile_data = _profile_to_dict(profile)
    generated_resumes = GeneratedResume.objects.filter(user=request.user)[:10]

    context = {
        'profile_data_json': json.dumps(profile_data),
        'theme_choices': THEME_CHOICES,
        'generated_resumes': generated_resumes,
        # ERP context injected by the caller if needed
    }
    return render(request, 'resume-builder.html', context)


# ---------------------------------------------------------------------------
# Save Personal Info
# ---------------------------------------------------------------------------

@login_required
@require_POST
def resume_save_personal(request):
    """Save personal info + social networks (Step 1 & 2)."""
    try:
        data = json.loads(request.body)
        profile = _get_or_create_profile(request.user)

        profile.full_name = data.get('full_name', '')
        profile.headline = data.get('headline', '')
        profile.location = data.get('location', '')
        profile.email = data.get('email', '')
        profile.phone = data.get('phone', '')
        profile.website = data.get('website', '')
        if 'selected_theme' in data:
            profile.selected_theme = data['selected_theme']
        profile.save()

        # Social networks — replace all
        if 'social_networks' in data:
            profile.social_networks.all().delete()
            for i, sn in enumerate(data['social_networks']):
                if sn.get('network') and sn.get('username'):
                    SocialNetwork.objects.create(
                        profile=profile,
                        network=sn['network'],
                        username=sn['username'],
                        order=i,
                    )

        return JsonResponse({'success': True, 'message': 'Personal info saved.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Photo Upload
# ---------------------------------------------------------------------------

@login_required
@require_POST
def resume_upload_photo(request):
    """Upload a profile photo for the resume (used only by photo-supporting themes)."""
    try:
        profile = _get_or_create_profile(request.user)
        if 'photo' in request.FILES:
            if profile.photo:
                # Remove old photo
                try:
                    os.remove(profile.photo.path)
                except OSError:
                    pass
            profile.photo = request.FILES['photo']
            profile.save()
            return JsonResponse({'success': True, 'photo_url': profile.photo.url})
        return JsonResponse({'success': False, 'error': 'No file uploaded.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Save / Delete Section
# ---------------------------------------------------------------------------

@login_required
@require_POST
def resume_save_section(request):
    """Create or update a resume section and its entries."""
    try:
        data = json.loads(request.body)
        profile = _get_or_create_profile(request.user)

        section_id = data.get('section_id')
        if section_id:
            section = get_object_or_404(ResumeSection, id=section_id, profile=profile)
            section.title = data.get('title', section.title)
            section.order = data.get('order', section.order)
            section.save()
        else:
            section = ResumeSection.objects.create(
                profile=profile,
                title=data.get('title', 'New Section'),
                entry_type=data.get('entry_type', 'bullet'),
                order=data.get('order', 0),
            )

        # Replace entries
        etype = section.entry_type
        _clear_section_entries(section)

        entries = data.get('entries', [])
        _save_entries(section, etype, entries)

        return JsonResponse({'success': True, 'section_id': section.id})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def _clear_section_entries(section: ResumeSection):
    section.education_entries.all().delete()
    section.experience_entries.all().delete()
    section.project_entries.all().delete()
    section.publication_entries.all().delete()
    section.skill_entries.all().delete()
    section.bullet_entries.all().delete()
    section.normal_entries.all().delete()


def _save_entries(section: ResumeSection, etype: str, entries: list):
    for i, e in enumerate(entries):
        if etype == 'education':
            EducationEntry.objects.create(
                section=section,
                institution=e.get('institution', ''),
                area=e.get('area', ''),
                degree=e.get('degree', ''),
                location=e.get('location', ''),
                start_date=e.get('start_date', ''),
                end_date=e.get('end_date', ''),
                single_date=e.get('single_date', ''),
                summary=e.get('summary', ''),
                gpa=e.get('gpa', ''),
                highlights=e.get('highlights', []),
                order=i,
            )
        elif etype == 'experience':
            ExperienceEntry.objects.create(
                section=section,
                company=e.get('company', ''),
                position=e.get('position', ''),
                location=e.get('location', ''),
                start_date=e.get('start_date', ''),
                end_date=e.get('end_date', ''),
                single_date=e.get('single_date', ''),
                summary=e.get('summary', ''),
                highlights=e.get('highlights', []),
                order=i,
            )
        elif etype == 'project':
            ProjectEntry.objects.create(
                section=section,
                name=e.get('name', ''),
                url=e.get('url', ''),
                location=e.get('location', ''),
                start_date=e.get('start_date', ''),
                end_date=e.get('end_date', ''),
                single_date=e.get('single_date', ''),
                summary=e.get('summary', ''),
                highlights=e.get('highlights', []),
                order=i,
            )
        elif etype == 'publication':
            PublicationEntry.objects.create(
                section=section,
                title=e.get('title', ''),
                authors=e.get('authors', []),
                journal=e.get('journal', ''),
                doi=e.get('doi', ''),
                url=e.get('url', ''),
                date=e.get('date', ''),
                order=i,
            )
        elif etype == 'skill':
            SkillEntry.objects.create(
                section=section,
                label=e.get('label', ''),
                details=e.get('details', ''),
                order=i,
            )
        elif etype == 'bullet':
            BulletEntry.objects.create(
                section=section,
                bullet=e.get('bullet', ''),
                order=i,
            )
        elif etype == 'normal':
            NormalEntry.objects.create(
                section=section,
                name=e.get('name', ''),
                location=e.get('location', ''),
                start_date=e.get('start_date', ''),
                end_date=e.get('end_date', ''),
                single_date=e.get('single_date', ''),
                summary=e.get('summary', ''),
                highlights=e.get('highlights', []),
                order=i,
            )


@login_required
@require_POST
def resume_delete_section(request, section_id):
    """Delete a section and all its entries."""
    profile = _get_or_create_profile(request.user)
    section = get_object_or_404(ResumeSection, id=section_id, profile=profile)
    section.delete()
    return JsonResponse({'success': True})


# ---------------------------------------------------------------------------
# Generate PDF
# ---------------------------------------------------------------------------

@login_required
@require_POST
def resume_generate(request):
    """Generate a PDF resume and store it as a GeneratedResume record."""
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'classic')

        profile = _get_or_create_profile(request.user)
        profile.selected_theme = theme
        profile.save()

        from .rendercv_service import build_and_generate_resume

        output_dir = pathlib.Path(settings.MEDIA_ROOT) / 'resumes' / 'generated'
        pdf_path = build_and_generate_resume(profile, output_dir)

        # Relative path for FileField
        relative = pdf_path.relative_to(pathlib.Path(settings.MEDIA_ROOT))

        profile_snapshot = _profile_to_dict(profile)

        gen = GeneratedResume.objects.create(
            user=request.user,
            theme=theme,
            resume_name=f"{profile.full_name or request.user.username} — {theme}",
            resume_data=profile_snapshot,
        )
        gen.pdf_file.name = str(relative).replace('\\', '/')
        gen.save()

        # Log action to ActivityLog
        try:
            from authentication.views import log_action
            log_action(request.user, f"Generated Resume PDF ({theme} theme)", request)
        except Exception:
            pass

        # Cache preview PNGs right at compile time to history
        try:
            from .rendercv_service import generate_preview_png
            preview_dir = pathlib.Path(settings.MEDIA_ROOT) / 'resumes' / 'previews' / str(gen.id)
            generate_preview_png(profile_snapshot, preview_dir)
        except Exception:
            pass

        return JsonResponse({
            'success': True,
            'resume_id': gen.id,
            'download_url': f'/erp/resume/download/{gen.id}/',
            'preview_url': f'/erp/resume/preview/{gen.id}/',
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ---------------------------------------------------------------------------
# Download PDF
# ---------------------------------------------------------------------------

@login_required
def resume_download(request, resume_id):
    """Stream the PDF file to the browser."""
    gen = get_object_or_404(GeneratedResume, id=resume_id, user=request.user)
    if not gen.pdf_file:
        raise Http404("PDF not found.")
    pdf_path = pathlib.Path(settings.MEDIA_ROOT) / gen.pdf_file.name
    if not pdf_path.exists():
        raise Http404("PDF file missing from disk.")
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    safe = gen.resume_name.replace(' ', '_').replace('—', '-').replace(' ', '')
    response['Content-Disposition'] = f'attachment; filename="{safe}.pdf"'
    return response


# ---------------------------------------------------------------------------
# Preview (PNG)
# ---------------------------------------------------------------------------

@login_required
def resume_preview(request, resume_id):
    """
    Generate and return PNG previews for a specific GeneratedResume.

    Returns JSON: { success, pages: [base64_png, ...] }
    Each entry in `pages` is a data-URL-ready base64 string for one PDF page.
    """
    import base64

    gen = get_object_or_404(GeneratedResume, id=resume_id, user=request.user)

    # Check if cached preview PNGs already exist on disk
    preview_dir = pathlib.Path(settings.MEDIA_ROOT) / 'resumes' / 'previews' / str(resume_id)
    cached = sorted(preview_dir.glob('*_preview_*.png')) if preview_dir.exists() else []

    if cached:
        pages = []
        for p in cached:
            with open(p, 'rb') as f:
                pages.append(base64.b64encode(f.read()).decode())
        return JsonResponse({'success': True, 'pages': pages})

    # Generate fresh PNGs from saved snapshot data if available, else current profile
    try:
        from .rendercv_service import generate_preview_png

        if gen.resume_data:
            png_paths = generate_preview_png(gen.resume_data, preview_dir)
        else:
            profile = _get_or_create_profile(request.user)
            profile.selected_theme = gen.theme   # Match the theme of this generated resume
            png_paths = generate_preview_png(profile, preview_dir)

        if not png_paths:
            return JsonResponse({
                'success': False,
                'error': 'Preview generation failed. Download the PDF to view.'
            })

        pages = []
        for p in sorted(png_paths):
            with open(p, 'rb') as f:
                pages.append(base64.b64encode(f.read()).decode())

        return JsonResponse({'success': True, 'pages': pages})

    except Exception:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Preview error. Download the PDF to view.'
        })


# ---------------------------------------------------------------------------
# Restore / Clear Resume Profile
# ---------------------------------------------------------------------------

@login_required
@require_POST
def resume_restore(request, resume_id):
    """Restore a past generated resume snapshot back to the active ResumeProfile."""
    try:
        gen = get_object_or_404(GeneratedResume, id=resume_id, user=request.user)
        if not gen.resume_data:
            return JsonResponse({'success': False, 'error': 'This resume does not have a data snapshot to restore.'}, status=400)

        profile = _get_or_create_profile(request.user)
        data = gen.resume_data

        # Restore personal info
        profile.full_name = data.get('full_name', '')
        profile.headline = data.get('headline', '')
        profile.location = data.get('location', '')
        profile.email = data.get('email', '')
        profile.phone = data.get('phone', '')
        profile.website = data.get('website', '')
        profile.selected_theme = data.get('selected_theme', 'sb2nov')
        profile.save()

        # Restore social networks
        profile.social_networks.all().delete()
        for i, sn in enumerate(data.get('social_networks', [])):
            if sn.get('network') and sn.get('username'):
                SocialNetwork.objects.create(
                    profile=profile,
                    network=sn['network'],
                    username=sn['username'],
                    order=i
                )

        # Restore sections & entries
        profile.sections.all().delete()
        for sec in data.get('sections', []):
            section = ResumeSection.objects.create(
                profile=profile,
                title=sec.get('title', 'New Section'),
                entry_type=sec.get('entry_type', 'bullet'),
                order=sec.get('order', 0)
            )
            etype = section.entry_type
            entries = sec.get('entries', [])
            _save_entries(section, etype, entries)

        # Log action to ActivityLog
        try:
            from authentication.views import log_action
            log_action(request.user, f"Restored Resume version (Export: {gen.resume_name})", request)
        except Exception:
            pass

        return JsonResponse({'success': True, 'message': 'Resume version restored successfully!'})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def resume_clear(request):
    """Clear all entries in the user's active ResumeProfile to start a fresh resume."""
    try:
        profile = _get_or_create_profile(request.user)
        profile.full_name = ''
        profile.headline = ''
        profile.location = ''
        profile.email = ''
        profile.phone = ''
        profile.website = ''
        profile.selected_theme = 'sb2nov'
        profile.save()

        profile.social_networks.all().delete()
        profile.sections.all().delete()

        # Log action to ActivityLog
        try:
            from authentication.views import log_action
            log_action(request.user, "Cleared active resume builder profile data", request)
        except Exception:
            pass

        return JsonResponse({'success': True, 'message': 'Builder form cleared.'})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ---------------------------------------------------------------------------

@login_required
@require_GET
def resume_list(request):
    """Return JSON list of user's generated resumes."""
    resumes = GeneratedResume.objects.filter(user=request.user).values(
        'id', 'theme', 'resume_name', 'created_at'
    )
    data = []
    for r in resumes:
        data.append({
            'id': r['id'],
            'theme': r['theme'],
            'name': r['resume_name'],
            'created_at': r['created_at'].strftime('%Y-%m-%d %H:%M'),
            'download_url': f'/erp/resume/download/{r["id"]}/',
        })
    return JsonResponse({'success': True, 'resumes': data})


@login_required
@require_POST
def resume_delete_generated(request, resume_id):
    """Delete a generated resume record and its PDF file."""
    gen = get_object_or_404(GeneratedResume, id=resume_id, user=request.user)
    if gen.pdf_file:
        try:
            pdf_path = pathlib.Path(settings.MEDIA_ROOT) / gen.pdf_file.name
            if pdf_path.exists():
                pdf_path.unlink()
        except Exception:
            pass
    # Also delete cached preview PNGs
    try:
        preview_dir = pathlib.Path(settings.MEDIA_ROOT) / 'resumes' / 'previews' / str(resume_id)
        if preview_dir.exists():
            shutil.rmtree(preview_dir)
    except Exception:
        pass
    gen.delete()
    return JsonResponse({'success': True})


# ---------------------------------------------------------------------------
# Get current profile data (for autofill / reload)
# ---------------------------------------------------------------------------

@login_required
@require_GET
def resume_get_profile(request):
    """Return the user's full resume profile as JSON."""
    profile = _get_or_create_profile(request.user)
    return JsonResponse({'success': True, 'data': _profile_to_dict(profile)})


# ---------------------------------------------------------------------------
# Live On-The-Fly Preview (PNG)
# ---------------------------------------------------------------------------

@login_required
@require_POST
def resume_live_preview(request):
    """
    Generate and return live PNG previews of the current user's profile state
    without saving a permanent history record.
    
    If the user has selected a theme in their request body, we temporarily apply 
    and save it so they see it instantly in the preview.
    """
    import base64
    import tempfile
    import shutil
    
    try:
        profile = _get_or_create_profile(request.user)
        
        # Check if the user is changing the theme in real-time
        try:
            body_data = json.loads(request.body) if request.body else {}
            if 'theme' in body_data:
                profile.selected_theme = body_data['theme']
                profile.save()
        except Exception:
            pass

        from .rendercv_service import generate_preview_png

        # Render inside a temporary folder
        with tempfile.TemporaryDirectory(prefix='bluenova_live_') as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)
            png_paths = generate_preview_png(profile, tmpdir_path)

            if not png_paths:
                return JsonResponse({
                    'success': False,
                    'error': 'Live preview generation failed. Fill in more sections first.'
                })

            pages = []
            for p in sorted(png_paths):
                with open(p, 'rb') as f:
                    pages.append(base64.b64encode(f.read()).decode())

            return JsonResponse({'success': True, 'pages': pages})
            
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ---------------------------------------------------------------------------
# Dedicated Export History Page
# ---------------------------------------------------------------------------

@login_required
def resume_history(request):
    """Render the resume history page listing all compiled exports."""
    generated_resumes = GeneratedResume.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'resume-history.html', {
        'generated_resumes': generated_resumes,
    })


