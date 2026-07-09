<div align="center">

# 🔷 BlueNova Tech ERP

**A full-featured internship & learning management platform built with Django**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 📖 Overview

**BlueNova Tech ERP** is a comprehensive Enterprise Resource Planning system tailored for tech internship programs and training institutes. It handles everything from student onboarding and attendance tracking to AI-powered weekly assessments and professional resume generation — all within a single, cohesive platform.

---

## ✨ Features

### 🔐 Authentication & Security
- Custom role-based user model (`admin` / `intern`)
- Rate-limited login with **5-attempt lockout** (15-minute cooldown)
- Password reset via secure token links
- Session security with CSRF protection, `HttpOnly` & `SameSite` cookies
- Full activity audit log (IP address, user agent, timestamp)

### 🎛️ Dashboards
| Role | Dashboard |
|------|-----------|
| **Intern** | Personal stats, profile completion, upcoming tasks, recent activity |
| **Admin** | Platform-wide analytics, user management, internship applications |

### 👤 Profile & User Management
- Rich intern profiles (photo, bio, skills, track, academic background)
- Profile completion tracker
- Admin can activate, deactivate, reset passwords, and delete users
- File upload workspace (PDF, ZIP, documents)

### 📅 Attendance Management
- Mark attendance per intern per day (Present / Absent / Late / Leave)
- Per-intern attendance detail with date-wise breakdown
- Attendance dashboard with charts and analytics
- Export reports as **CSV** or **PDF**

### 📝 Assessments & Weekly Tests
- Auto-generated weekly tests per course/track
- 20-question MCQ format with configurable time limits
- Instant auto-grading with pass/fail status
- Admin override scoring & manual feedback
- Intern progress report with history

### 📄 Resume Builder
Powered by **RenderCV** — generates professional PDF resumes directly in the browser.

- 9 professional themes: `Classic`, `Ember`, `Harvard`, `Modern CV`, `Ink`, `Opal`, and more
- Structured sections: Education, Experience, Projects, Publications, Skills, Awards
- Social network links (LinkedIn, GitHub, ORCID, ResearchGate, and 15+ more)
- Resume history — view, re-download, or delete previously generated PDFs

### 💬 Messaging
- Direct intern-to-intern and intern-to-admin messaging
- Group broadcast messages
- Unread count badge with read receipts

### 🔔 Notifications
- System-level alerts (info / success / warning / error)
- Per-user notification inbox with read/delete support

### 📊 Analytics & Reports
- Platform-wide analytics view
- Export user & attendance data as CSV or PDF
- Activity logs for full audit trail
- Global search across users, courses, and content

### 🌐 Public Website
Full public-facing website included:
- Landing page, About, Services, Training, Internships
- Careers, Blog, FAQ, Team, Events, Gallery
- Pricing plans, Testimonials, Success Stories
- Legal pages (Privacy Policy, Terms, Refund Policy)
- Internship application form with resume upload

---

## 🗂️ Project Structure

```
erp/
├── backend/                        # Django project root
│   ├── authentication/             # Custom user model, login, signup, password reset
│   ├── core/                       # Main ERP app (dashboard, attendance, assessments, etc.)
│   │   ├── models.py               # Profile, Attendance, Message, Notification, WeeklyTest...
│   │   ├── views.py                # All ERP views
│   │   ├── questions_db.py         # Question bank for auto-generated assessments
│   │   └── management/commands/    # seed_db management command
│   ├── resume/                     # Resume builder app
│   │   ├── models.py               # ResumeProfile, sections, entries, GeneratedResume
│   │   ├── rendercv_service.py     # PDF generation via RenderCV
│   │   └── views.py                # Resume CRUD and PDF generation endpoints
│   ├── bluenova_erp/               # Django settings & URL config
│   ├── templates/                  # 64 HTML templates
│   │   └── includes/               # Shared partials (sidebar, navbar, etc.)
│   ├── static/                     # CSS, JS, images
│   │   ├── css/style.css
│   │   └── js/app.js
│   ├── media/                      # User uploads (gitignored)
│   ├── manage.py
│   └── .env                        # Secret config (gitignored — see .env.example)
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/laweeza786/BlueNova-Tech.git
cd BlueNova-Tech
```

### 2. Create & Activate a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note:** If there is no `requirements.txt` yet, install manually:
> ```bash
> pip install django python-dotenv pillow
> ```

### 4. Configure Environment Variables
```bash
cd backend
cp .env.example .env
```

Open `.env` and fill in your values:
```env
SECRET_KEY=your-generated-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate a fresh secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Seed the Database *(optional)*
```bash
python manage.py seed_db
```

### 7. Create a Superuser
```bash
python manage.py createsuperuser
```

### 8. Run the Development Server
```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** 🎉

---

## 🔑 Default Routes

| URL | Description |
|-----|-------------|
| `/` | Public landing page |
| `/auth/login/` | Intern / Admin login |
| `/auth/signup/` | New intern registration |
| `/erp/dashboard/` | Intern dashboard *(login required)* |
| `/erp/admin-dashboard/` | Admin dashboard *(admin only)* |
| `/erp/attendance/dashboard/` | Attendance management |
| `/erp/assessments/` | Weekly tests |
| `/erp/resume/builder/` | Resume builder |
| `/erp/messages/` | Messaging |
| `/erp/reports/` | Reports & exports |
| `/django-admin/` | Django admin panel |

---

## 🛡️ Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ Yes | — | Django cryptographic signing key |
| `DEBUG` | ✅ Yes | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | ✅ Yes | `localhost` | Comma-separated allowed hostnames |

---

## 🗃️ Data Models Summary

```
User (custom)
 └── Profile            — internship track, skills, status, photo
 └── Setting            — theme (dark/light), notification prefs
 └── Attendance         — daily status per intern per track
 └── WeeklyTestAttempt  — generated MCQ tests with auto-grading
 └── Message            — direct & group messaging
 └── Notification       — system alerts inbox
 └── ActivityLog        — audit trail (IP, action, timestamp)
 └── Feedback           — star-rated feedback submissions
 └── UploadedFile       — personal file workspace
 └── History            — milestone tracking
 └── InternshipApplication — public application form submissions
 └── ResumeProfile      — resume builder data
      └── ResumeSection → EducationEntry / ExperienceEntry
                        / ProjectEntry / SkillEntry / BulletEntry...
      └── GeneratedResume — stored PDF history
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**.

---

<div align="center">

Built with ❤️ by **BlueNova Tech**

</div>
