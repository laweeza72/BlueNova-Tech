from django.db import models
from django.conf import settings


THEME_CHOICES = [
    ('classic', 'Classic'),
    ('ember', 'Ember'),
    ('engineeringclassic', 'Engineering Classic'),
    ('engineeringresumes', 'Engineering Resumes'),
    ('harvard', 'Harvard'),
    ('ink', 'Ink'),
    ('moderncv', 'Modern CV'),
    ('opal', 'Opal'),
    ('sb2nov', 'SB2Nov'),
]

SOCIAL_NETWORK_CHOICES = [
    ('LinkedIn', 'LinkedIn'),
    ('GitHub', 'GitHub'),
    ('GitLab', 'GitLab'),
    ('Instagram', 'Instagram'),
    ('ORCID', 'ORCID'),
    ('ResearchGate', 'ResearchGate'),
    ('Twitter', 'Twitter'),
    ('Mastodon', 'Mastodon'),
    ('StackOverflow', 'StackOverflow'),
    ('YouTube', 'YouTube'),
    ('Telegram', 'Telegram'),
    ('WhatsApp', 'WhatsApp'),
    ('WeChat', 'WeChat'),
    ('LINE', 'LINE'),
    ('Medium', 'Medium'),
    ('Substack', 'Substack'),
    ('HackerNews', 'HackerNews'),
    ('Reddit', 'Reddit'),
]


class ResumeProfile(models.Model):
    """
    Stores the header / personal info section of a user's resume.
    Maps 1:1 to RenderCV's `cv` top-level block.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume_profile'
    )
    full_name = models.CharField(max_length=200, blank=True)
    headline = models.CharField(max_length=300, blank=True, help_text='e.g. Software Engineer | PhD Candidate')
    location = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True, help_text='E.164 format, e.g. +1-234-567-8900')
    website = models.URLField(blank=True)
    photo = models.ImageField(upload_to='resume_photos/', blank=True, null=True,
                              help_text='Optional profile photo — only included in themes that support it')
    selected_theme = models.CharField(max_length=50, choices=THEME_CHOICES, default='classic')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — Resume Profile"


class SocialNetwork(models.Model):
    """LinkedIn, GitHub, etc. connections shown in the resume header."""
    profile = models.ForeignKey(ResumeProfile, on_delete=models.CASCADE, related_name='social_networks')
    network = models.CharField(max_length=50, choices=SOCIAL_NETWORK_CHOICES)
    username = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.network}: {self.username}"


class ResumeSection(models.Model):
    """
    A named section of the resume (Education, Experience, Projects, etc.).
    Each section contains entries of a single entry type.
    """
    ENTRY_TYPE_CHOICES = [
        ('education', 'Education'),
        ('experience', 'Experience'),
        ('project', 'Project'),
        ('publication', 'Publication'),
        ('skill', 'Skill'),
        ('bullet', 'Bullet (Honors / Awards / Talks)'),
        ('normal', 'Normal Text'),
        ('one_line', 'One-Line'),
    ]
    profile = models.ForeignKey(ResumeProfile, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, help_text='Display title, e.g. "Work Experience"')
    entry_type = models.CharField(max_length=30, choices=ENTRY_TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.profile.user.username} → {self.title}"


class EducationEntry(models.Model):
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='education_entries')
    institution = models.CharField(max_length=300)
    area = models.CharField(max_length=200, blank=True, help_text='e.g. Computer Science')
    degree = models.CharField(max_length=100, blank=True, help_text='e.g. BS, MS, PhD')
    location = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=20, blank=True, help_text='YYYY-MM or YYYY')
    end_date = models.CharField(max_length=20, blank=True, help_text='YYYY-MM, YYYY, or "present"')
    single_date = models.CharField(max_length=20, blank=True, help_text='For a fixed date instead of range')
    summary = models.TextField(blank=True)
    gpa = models.CharField(max_length=100, blank=True, help_text='e.g. GPA: 3.8/4.0 or 85%')
    highlights = models.JSONField(default=list, help_text='List of bullet-point strings')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.institution} — {self.degree}"


class ExperienceEntry(models.Model):
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='experience_entries')
    company = models.CharField(max_length=300)
    position = models.CharField(max_length=300)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=20, blank=True)
    end_date = models.CharField(max_length=20, blank=True, help_text='"present" or YYYY-MM')
    single_date = models.CharField(max_length=20, blank=True)
    summary = models.TextField(blank=True)
    highlights = models.JSONField(default=list)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.company} — {self.position}"


class ProjectEntry(models.Model):
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='project_entries')
    name = models.CharField(max_length=300)
    url = models.URLField(blank=True, help_text='Optional project URL — will be hyperlinked in PDF')
    location = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=20, blank=True)
    end_date = models.CharField(max_length=20, blank=True)
    single_date = models.CharField(max_length=20, blank=True)
    summary = models.TextField(blank=True)
    highlights = models.JSONField(default=list)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class PublicationEntry(models.Model):
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='publication_entries')
    title = models.CharField(max_length=500)
    authors = models.JSONField(default=list, help_text='List of author name strings. Wrap your name in *asterisks*.')
    journal = models.CharField(max_length=300, blank=True)
    doi = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)
    date = models.CharField(max_length=20, blank=True, help_text='YYYY-MM or YYYY')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class SkillEntry(models.Model):
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='skill_entries')
    label = models.CharField(max_length=200, help_text='e.g. "Programming Languages"')
    details = models.CharField(max_length=500, help_text='e.g. "Python, C++, Rust"')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.details}"


class BulletEntry(models.Model):
    """Generic bullet item — used for honors, awards, patents, talks, etc."""
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='bullet_entries')
    bullet = models.TextField(help_text='Bullet text (Markdown supported)')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.bullet[:80]


class NormalEntry(models.Model):
    """A normal (title + optional details) entry."""
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='normal_entries')
    name = models.CharField(max_length=300)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=20, blank=True)
    end_date = models.CharField(max_length=20, blank=True)
    single_date = models.CharField(max_length=20, blank=True)
    summary = models.TextField(blank=True)
    highlights = models.JSONField(default=list)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class GeneratedResume(models.Model):
    """Stores a generated PDF resume file."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_resumes'
    )
    pdf_file = models.FileField(upload_to='resumes/generated/', blank=True, null=True)
    preview_image = models.ImageField(upload_to='resumes/previews/', blank=True, null=True)
    theme = models.CharField(max_length=50, choices=THEME_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    resume_name = models.CharField(max_length=200, blank=True, help_text='Display name for this generated PDF')
    resume_data = models.JSONField(blank=True, null=True, help_text='JSON snapshot of the resume data at generation time')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.theme} — {self.created_at.strftime('%Y-%m-%d %H:%M')}"
