"""
rendercv_service.py
-------------------
Service layer that bridges the Django ORM with RenderCV's Python API.

Requirements (must be installed in venv):
    pip install rendercv rendercv-fonts typst
    # or:
    pip install "rendercv[full]"

Usage:
    from resume.rendercv_service import build_and_generate_resume
    pdf_path = build_and_generate_resume(resume_profile, output_dir)
"""

import atexit
import pathlib
import re
import shutil
import tempfile


# ---------------------------------------------------------------------------
# Themes that embed a photo in the header
# ---------------------------------------------------------------------------
PHOTO_SUPPORTED_THEMES = {'moderncv'}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _get_highlights(highlights_json):
    """Return a list of strings from a JSON field (already a list)."""
    if isinstance(highlights_json, list) and highlights_json:
        return highlights_json
    return None


def _date_range(entry):
    """Return (start_date, end_date, single_date) from an ORM entry."""
    return (
        entry.start_date or None,
        entry.end_date or None,
        getattr(entry, 'single_date', None) or None,
    )


def _safe_filename(name: str) -> str:
    """Convert a display name to a filesystem-safe string."""
    safe = re.sub(r'[^\w\s-]', '', name).strip()
    return re.sub(r'[\s-]+', '_', safe) or 'resume'


def _sanitize_phone(phone: str) -> str | None:
    """
    Normalize a phone number to E.164 format for RenderCV.

    RenderCV's Pydantic model requires international format: +<country><number>
    e.g.  +1-234-567-8900  or  +44 20 1234 5678  or  +91-9876543210

    Rules applied:
      - Already starts with '+' → pass through as-is
      - Starts with '00' → replace prefix with '+'
      - 10-digit number (India/US style) → prepend '+91' (common default)
      - Anything else that doesn't look international → return None (skip field)

    The user can always correct it in the form; we never crash on bad input.
    """
    if not phone:
        return None

    # Strip spaces, dashes for analysis (keep them in output for readability)
    stripped = re.sub(r'[\s\-\(\)\.]+', '', phone)

    if phone.strip().startswith('+'):
        # Already E.164 — return as-is
        return phone.strip()

    if stripped.startswith('00') and len(stripped) >= 10:
        # 0044... → +44...
        return '+' + stripped[2:]

    if stripped.isdigit() and len(stripped) == 10:
        # 10-digit number without country code → assume +91 (India)
        # Users should ideally enter the full number; this is a best-effort fallback
        return f'+91-{stripped[:5]}-{stripped[5:]}'

    if stripped.isdigit() and len(stripped) == 11 and stripped.startswith('0'):
        # 011234567890 → +1...
        return '+' + stripped[1:]

    # Unrecognised format — skip to avoid validation crash
    return None


# ---------------------------------------------------------------------------
# Build RenderCV dict from ORM
# ---------------------------------------------------------------------------

def build_rendercv_dict(profile) -> dict:
    """
    Convert a ResumeProfile ORM object into the RenderCV YAML-equivalent dict.

    The dict structure mirrors the rendercv YAML spec exactly so it can be
    fed directly into RenderCVModel.model_validate().
    """
    theme = profile.selected_theme
    cv_dict: dict = {}

    if profile.full_name:
        cv_dict['name'] = profile.full_name
    if profile.headline:
        cv_dict['headline'] = profile.headline
    if profile.location:
        cv_dict['location'] = profile.location
    if profile.email:
        cv_dict['email'] = profile.email
    if profile.phone:
        phone = _sanitize_phone(profile.phone)
        if phone:
            cv_dict['phone'] = phone
    if profile.website:
        cv_dict['website'] = profile.website

    # Photo — only for themes that support it
    if profile.photo and theme in PHOTO_SUPPORTED_THEMES:
        cv_dict['photo'] = str(profile.photo.path)

    # Social networks
    social_nets = profile.social_networks.all()
    if social_nets.exists():
        cv_dict['social_networks'] = [
            {'network': sn.network, 'username': sn.username}
            for sn in social_nets
        ]

    # Sections
    sections: dict = {}
    for section in profile.sections.all():
        entries = []
        etype = section.entry_type

        if etype == 'education':
            for e in section.education_entries.all():
                start, end, single = _date_range(e)
                entry = {'institution': e.institution}
                if e.area:
                    entry['area'] = e.area
                if e.degree:
                    entry['degree'] = e.degree
                if e.location:
                    entry['location'] = e.location
                if single:
                    entry['date'] = single
                else:
                    entry['date'] = None
                    entry['start_date'] = start
                    entry['end_date'] = end
                if e.summary:
                    entry['summary'] = e.summary
                
                # Retrieve highlights or start empty
                highlights = _get_highlights(e.highlights) or []
                
                # Check for GPA/marks
                gpa_val = getattr(e, 'gpa', '').strip() if hasattr(e, 'gpa') else ''
                if gpa_val:
                    # Intelligently check if user already wrote GPA / Marks
                    lower_gpa = gpa_val.lower()
                    if any(kw in lower_gpa for kw in ['gpa', 'marks', 'percentage', 'grade', 'cgpa', 'percent']):
                        formatted_gpa = gpa_val
                    else:
                        formatted_gpa = f"GPA/Marks: {gpa_val}"
                    # Insert at the beginning of highlights list for prominent visibility
                    highlights.insert(0, formatted_gpa)

                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)


        elif etype == 'experience':
            for e in section.experience_entries.all():
                start, end, single = _date_range(e)
                entry = {'company': e.company, 'position': e.position}
                if e.location:
                    entry['location'] = e.location
                if single:
                    entry['date'] = single
                else:
                    entry['date'] = None
                    entry['start_date'] = start
                    entry['end_date'] = end
                if e.summary:
                    entry['summary'] = e.summary
                highlights = _get_highlights(e.highlights)
                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)

        elif etype == 'project':
            for e in section.project_entries.all():
                start, end, single = _date_range(e)
                name = f"[{e.name}]({e.url})" if e.url else e.name
                entry = {'name': name}
                if e.location:
                    entry['location'] = e.location
                if single:
                    entry['date'] = single
                else:
                    entry['date'] = None
                    entry['start_date'] = start
                    entry['end_date'] = end
                if e.summary:
                    entry['summary'] = e.summary
                highlights = _get_highlights(e.highlights)
                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)

        elif etype == 'publication':
            for e in section.publication_entries.all():
                entry = {'title': e.title}
                if e.authors:
                    entry['authors'] = e.authors
                if e.journal:
                    entry['journal'] = e.journal
                if e.doi:
                    entry['doi'] = e.doi
                if e.url:
                    entry['url'] = e.url
                if e.date:
                    entry['date'] = e.date
                entries.append(entry)

        elif etype == 'skill':
            for e in section.skill_entries.all():
                entries.append({'label': e.label, 'details': e.details})

        elif etype == 'bullet':
            for e in section.bullet_entries.all():
                entries.append({'bullet': e.bullet})

        elif etype == 'normal':
            for e in section.normal_entries.all():
                start, end, single = _date_range(e)
                entry = {'name': e.name}
                if e.location:
                    entry['location'] = e.location
                if single:
                    entry['date'] = single
                else:
                    entry['date'] = None
                    entry['start_date'] = start
                    entry['end_date'] = end
                if e.summary:
                    entry['summary'] = e.summary
                highlights = _get_highlights(e.highlights)
                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)

        if entries:
            sections[section.title] = entries

    if sections:
        cv_dict['sections'] = sections

    return {
        'cv': cv_dict,
        'design': {
            'theme': theme,
            'page': {
                'show_footer': False,
                'show_top_note': False
            }
        }
    }


# ---------------------------------------------------------------------------
# Typst compiler — delegate to rendercv's own implementation
# ---------------------------------------------------------------------------

def _get_typst_compiler(root: pathlib.Path) -> 'typst.Compiler':
    """
    Create a Typst compiler using rendercv's bundled font + package setup.
    Delegates entirely to rendercv.renderer.pdf_png.get_typst_compiler()
    so we always stay in sync with whatever version of rendercv is installed.
    """
    from rendercv.renderer.pdf_png import get_typst_compiler
    # input_file_path=None → fonts folder defaults to cwd/fonts (fine for us)
    return get_typst_compiler(None, root)


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def build_rendercv_dict_from_json(profile_data: dict) -> dict:
    """
    Convert a serialized ResumeProfile JSON snapshot (from _profile_to_dict)
    into the RenderCV YAML-equivalent dict.
    """
    theme = profile_data.get('selected_theme', 'sb2nov')
    cv_dict: dict = {}

    if profile_data.get('full_name'):
        cv_dict['name'] = profile_data['full_name']
    if profile_data.get('headline'):
        cv_dict['headline'] = profile_data['headline']
    if profile_data.get('location'):
        cv_dict['location'] = profile_data['location']
    if profile_data.get('email'):
        cv_dict['email'] = profile_data['email']
    if profile_data.get('phone'):
        phone = _sanitize_phone(profile_data['phone'])
        if phone:
            cv_dict['phone'] = phone
    if profile_data.get('website'):
        cv_dict['website'] = profile_data['website']

    # Social networks
    social_nets = profile_data.get('social_networks', [])
    if social_nets:
        cv_dict['social_networks'] = [
            {'network': sn['network'], 'username': sn['username']}
            for sn in social_nets if sn.get('network') and sn.get('username')
        ]

    # Sections
    sections: dict = {}
    for section in profile_data.get('sections', []):
        entries = []
        etype = section.get('entry_type')

        for e in section.get('entries', []):
            if etype == 'education':
                entry = {'institution': e.get('institution', '')}
                if e.get('area'):
                    entry['area'] = e['area']
                if e.get('degree'):
                    entry['degree'] = e['degree']
                if e.get('location'):
                    entry['location'] = e['location']
                if e.get('single_date'):
                    entry['date'] = e['single_date']
                else:
                    entry['date'] = None
                    entry['start_date'] = e.get('start_date') or None
                    entry['end_date'] = e.get('end_date') or None
                if e.get('summary'):
                    entry['summary'] = e['summary']
                
                highlights = e.get('highlights') or []
                gpa_val = e.get('gpa', '').strip() if e.get('gpa') else ''
                if gpa_val:
                    lower_gpa = gpa_val.lower()
                    if any(kw in lower_gpa for kw in ['gpa', 'marks', 'percentage', 'grade', 'cgpa', 'percent']):
                        formatted_gpa = gpa_val
                    else:
                        formatted_gpa = f"GPA/Marks: {gpa_val}"
                    highlights = list(highlights)
                    highlights.insert(0, formatted_gpa)

                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)

            elif etype == 'experience':
                entry = {'company': e.get('company', ''), 'position': e.get('position', '')}
                if e.get('location'):
                    entry['location'] = e['location']
                if e.get('single_date'):
                    entry['date'] = e['single_date']
                else:
                    entry['date'] = None
                    entry['start_date'] = e.get('start_date') or None
                    entry['end_date'] = e.get('end_date') or None
                if e.get('summary'):
                    entry['summary'] = e['summary']
                highlights = _get_highlights(e.get('highlights'))
                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)

            elif etype == 'project':
                url = e.get('url', '')
                name = f"[{e.get('name', '')}]({url})" if url else e.get('name', '')
                entry = {'name': name}
                if e.get('location'):
                    entry['location'] = e['location']
                if e.get('single_date'):
                    entry['date'] = e['single_date']
                else:
                    entry['date'] = None
                    entry['start_date'] = e.get('start_date') or None
                    entry['end_date'] = e.get('end_date') or None
                if e.get('summary'):
                    entry['summary'] = e['summary']
                highlights = _get_highlights(e.get('highlights'))
                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)

            elif etype == 'publication':
                entry = {'title': e.get('title', '')}
                if e.get('authors'):
                    entry['authors'] = e['authors']
                if e.get('journal'):
                    entry['journal'] = e['journal']
                if e.get('doi'):
                    entry['doi'] = e['doi']
                if e.get('url'):
                    entry['url'] = e['url']
                if e.get('date'):
                    entry['date'] = e['date']
                entries.append(entry)

            elif etype == 'skill':
                entries.append({'label': e.get('label', ''), 'details': e.get('details', '')})

            elif etype == 'bullet':
                entries.append({'bullet': e.get('bullet', '')})

            elif etype == 'normal':
                entry = {'name': e.get('name', '')}
                if e.get('location'):
                    entry['location'] = e['location']
                if e.get('single_date'):
                    entry['date'] = e['single_date']
                else:
                    entry['date'] = None
                    entry['start_date'] = e.get('start_date') or None
                    entry['end_date'] = e.get('end_date') or None
                if e.get('summary'):
                    entry['summary'] = e['summary']
                highlights = _get_highlights(e.get('highlights'))
                if highlights:
                    entry['highlights'] = highlights
                entries.append(entry)

        if entries:
            sections[section.get('title', 'Section')] = entries

    if sections:
        cv_dict['sections'] = sections

    return {
        'cv': cv_dict,
        'design': {
            'theme': theme,
            'page': {
                'show_footer': False,
                'show_top_note': False
            }
        }
    }


# ---------------------------------------------------------------------------
# Typst compiler — delegate to rendercv's own implementation
# ---------------------------------------------------------------------------

def _get_typst_compiler(root: pathlib.Path) -> 'typst.Compiler':
    """
    Create a Typst compiler using rendercv's bundled font + package setup.
    Delegates entirely to rendercv.renderer.pdf_png.get_typst_compiler()
    so we always stay in sync with whatever version of rendercv is installed.
    """
    from rendercv.renderer.pdf_png import get_typst_compiler
    # input_file_path=None → fonts folder defaults to cwd/fonts (fine for us)
    return get_typst_compiler(None, root)


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def build_and_generate_resume(profile_or_json, output_dir: pathlib.Path) -> pathlib.Path:
    """
    Build a PDF resume from a ResumeProfile or dict snapshot using RenderCV's Python API.
    """
    from rendercv.schema.models.rendercv_model import RenderCVModel
    from rendercv.renderer.templater.templater import render_full_template

    # 1. Build the dict
    if isinstance(profile_or_json, dict):
        data = build_rendercv_dict_from_json(profile_or_json)
        theme = profile_or_json.get('selected_theme', 'sb2nov')
        name_str = profile_or_json.get('full_name', 'resume')
    else:
        data = build_rendercv_dict(profile_or_json)
        theme = profile_or_json.selected_theme
        name_str = profile_or_json.full_name or profile_or_json.user.username

    # 2. Validate with Pydantic
    rendercv_model = RenderCVModel.model_validate(data)

    # 3. Render Typst source
    typst_source = render_full_template(rendercv_model, 'typst')

    # 4. Write .typ to a temp directory and compile
    with tempfile.TemporaryDirectory(prefix='bluenova_resume_') as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)

        # Copy photo if needed
        cv = rendercv_model.cv
        if cv.photo and isinstance(cv.photo, pathlib.Path) and cv.photo.exists():
            shutil.copy(cv.photo, tmpdir_path / cv.photo.name)

        typ_file = tmpdir_path / 'resume.typ'
        typ_file.write_text(typst_source, encoding='utf-8')

        # 5. Compile to PDF
        pdf_path = tmpdir_path / 'resume.pdf'
        compiler = _get_typst_compiler(tmpdir_path)
        compiler.compile(input=typ_file, format='pdf', output=pdf_path)

        # 6. Copy to persistent output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _safe_filename(name_str)
        pdf_dest = output_dir / f"{safe_name}_{theme}.pdf"
        shutil.copy2(pdf_path, pdf_dest)

    return pdf_dest


def generate_preview_png(profile_or_json, output_dir: pathlib.Path) -> list:
    """
    Generate PNG preview images for the current resume data (profile or json).
    Returns list of Path objects for saved PNG files.
    """
    try:
        from rendercv.schema.models.rendercv_model import RenderCVModel
        from rendercv.renderer.templater.templater import render_full_template

        if isinstance(profile_or_json, dict):
            data = build_rendercv_dict_from_json(profile_or_json)
            name_str = profile_or_json.get('full_name', 'resume')
        else:
            data = build_rendercv_dict(profile_or_json)
            name_str = profile_or_json.full_name or profile_or_json.user.username

        rendercv_model = RenderCVModel.model_validate(data)
        typst_source = render_full_template(rendercv_model, 'typst')

        with tempfile.TemporaryDirectory(prefix='bluenova_png_') as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)
            typ_file = tmpdir_path / 'resume.typ'
            typ_file.write_text(typst_source, encoding='utf-8')

            compiler = _get_typst_compiler(tmpdir_path)
            png_results = compiler.compile(input=typ_file, format='png')

            if not isinstance(png_results, list):
                png_results = [png_results]

            output_dir.mkdir(parents=True, exist_ok=True)
            safe_name = _safe_filename(name_str)
            paths = []
            for i, png_bytes in enumerate(png_results):
                if png_bytes:
                    dest = output_dir / f"{safe_name}_preview_{i + 1}.png"
                    dest.write_bytes(png_bytes)
                    paths.append(dest)
            return paths
    except Exception:
        import traceback
        traceback.print_exc()
        return []

