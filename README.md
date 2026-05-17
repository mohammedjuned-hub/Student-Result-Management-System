# Student Result Management System (SRMS)

A full-stack web application built with **Python Flask**, **MySQL**, and **vanilla HTML/CSS/JS**.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- MySQL 5.7+ or MariaDB
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
Edit `app.py` and update `DB_CONFIG` with your MySQL credentials:
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'your_password',   # ← change this
    'database': 'srms_db'
}
```

### 4. Initialize the Database

**Option A — MySQL CLI:**
```bash
mysql -u root -p < setup.sql
```

**Option B — Via the app:**
```bash
python app.py
```
Then open: http://localhost:5000/init_db

### 5. Run the App
```bash
python app.py
```
Visit: **http://localhost:5000**

---

## 🔐 Login Credentials

| Portal  | Username            | Password        |
|---------|---------------------|-----------------|
| Admin   | —                   | `admin`         |
| Faculty | `F001`              | `F001`          |
| Faculty | `F002`              | `F002`          |
| Student | `22BD1A0501` (Alice)| `22BD1A0501`    |
| Student | `22BD1A0502` (Bob)  | `22BD1A0502`    |

> Alice has 2 backlogs — great for testing the AI Assistant!

---

## 📁 File Structure

```
project/
├── app.py                      # Flask backend (all routes)
├── requirements.txt
├── setup.sql                   # Database schema + sample data
├── README.md
├── templates/
│   ├── base.html               # Base layout
│   ├── index.html              # Landing page
│   ├── admin_login.html
│   ├── faculty_login.html
│   ├── student_login.html
│   ├── admin.html              # Admin dashboard
│   ├── enter_marks.html        # Semester marks entry
│   ├── assign_subjects.html
│   ├── manage_students.html
│   ├── manage_faculty.html
│   ├── admin_change_password.html
│   ├── faculty.html            # Faculty dashboard
│   ├── enter_internal.html     # MID marks entry
│   ├── faculty_change_password.html
│   ├── student_dashboard.html  # Student home
│   ├── student_mid_marks.html
│   ├── student_results.html
│   ├── student_backlogs.html
│   ├── student_ranking.html
│   ├── student_change_password.html
│   └── backlog_assistant.html  # AI Study Plan Generator
└── static/
    ├── css/style.css           # All styles (dark theme, responsive)
    └── js/main.js              # Auto-calc, fetch API, plan renderer
```

---

## ✨ Features

### Admin Portal
- Dashboard with system stats
- Enter semester marks (auto grade + GP calculation via JS)
- Assign subjects to faculty
- Add/delete students and faculty

### Faculty Portal
- View assigned subjects
- Enter MID-1 and MID-2 marks (exam + assignment + PPT)

### Student Portal
- Dashboard with SGPA, CGPA, credits summary
- View MID marks
- Full semester results with grade table
- Backlogs section
- Class leaderboard / ranking
- Change password

### 🤖 AI Backlog Assistant
- Detects backlog subjects automatically
- Configurable: study hours/day, number of days, preferred time
- Generates day-wise timetable with subject distribution
- Priority analysis (weak subjects get more time)
- Learning resources per subject (YouTube, PDF, Practice)
- Progress tracker with checkboxes
- Motivational messages
- Print/Download as PDF

---

## 🎨 Design
- Dark theme with CSS variables
- Sora + JetBrains Mono fonts
- Fully responsive (mobile + desktop)
- Animations and smooth transitions
- Grade color badges

---

## 📊 Grade Scale

| Marks | Grade | Grade Point |
|-------|-------|-------------|
| ≥ 90  | O     | 10          |
| ≥ 80  | A+    | 9           |
| ≥ 70  | A     | 8           |
| ≥ 60  | B+    | 7           |
| ≥ 50  | B     | 6           |
| ≥ 40  | C     | 5           |
| < 40  | F     | 0           |

---

## 🧮 GPA Formulas

**SGPA** = Σ(Grade Point × Credits) / Σ Credits (per semester)

**CGPA** = Σ(Grade Point × Credits) / Σ Credits (all semesters)
