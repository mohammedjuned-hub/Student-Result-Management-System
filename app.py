"""
Student Result Management System
──────────────────────────────────
Database : SQLite  →  srms.db   (auto-created next to app.py on first run)
Run      : python app.py
Open     : http://127.0.0.1:5000

NO MySQL · NO XAMPP · NO setup · Just run.
"""

import os, sqlite3, random, datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = 'srms_secret_key_2024'

# ── Path to the SQLite database file ─────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'srms.db')


# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE BOOTSTRAP  – runs once when app.py starts
# ══════════════════════════════════════════════════════════════════════════════
def _bootstrap():
    """Create all tables + seed sample data if the DB file doesn't exist yet."""
    is_new = not os.path.exists(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    cur = con.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            hallticket  TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            password    TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id  TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            password    TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS faculty_subjects (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id   TEXT,
            subject_code TEXT,
            subject_name TEXT,
            year         INTEGER,
            semester     INTEGER,
            UNIQUE(subject_code, semester)
        );
        CREATE TABLE IF NOT EXISTS semester_results (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id     TEXT,
            subject_code   TEXT,
            subject_name   TEXT,
            credits        INTEGER DEFAULT 3,
            internal_marks REAL    DEFAULT 0,
            external_marks REAL    DEFAULT 0,
            total_marks    REAL    DEFAULT 0,
            grade          TEXT,
            grade_point    REAL    DEFAULT 0,
            year           INTEGER,
            semester       INTEGER,
            exam_date      TEXT,
            UNIQUE(student_id, subject_code, year, semester)
        );
        CREATE TABLE IF NOT EXISTS internal_marks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      TEXT,
            subject_code    TEXT,
            mid1_exam       REAL DEFAULT 0,
            mid1_assignment REAL DEFAULT 0,
            mid1_ppt        REAL DEFAULT 0,
            mid2_exam       REAL DEFAULT 0,
            mid2_assignment REAL DEFAULT 0,
            mid2_ppt        REAL DEFAULT 0,
            UNIQUE(student_id, subject_code)
        );
    """)

    if is_new:   # only insert sample rows once
        cur.executemany("INSERT OR IGNORE INTO students VALUES(?,?,?)", [
            ('22BD1A0501', 'Alice Johnson', '22BD1A0501'),
            ('22BD1A0502', 'Bob Smith',     '22BD1A0502'),
            ('22BD1A0503', 'Carol Davis',   '22BD1A0503'),
            ('22BD1A0504', 'David Wilson',  '22BD1A0504'),
            ('22BD1A0505', 'Eva Martinez',  '22BD1A0505'),
        ])
        cur.executemany("INSERT OR IGNORE INTO faculty VALUES(?,?,?)", [
            ('F001', 'Dr. Ramesh Kumar', 'F001'),
            ('F002', 'Prof. Sunita Rao', 'F002'),
            ('F003', 'Dr. Arjun Mehta',  'F003'),
        ])
        cur.executemany(
            "INSERT OR IGNORE INTO faculty_subjects"
            "(faculty_id,subject_code,subject_name,year,semester) VALUES(?,?,?,?,?)", [
            ('F001','CS301','Data Structures',            3,1),
            ('F001','CS302','Algorithms',                 3,1),
            ('F002','CS303','Database Management Systems',3,1),
            ('F002','CS304','Operating Systems',          3,1),
            ('F003','CS305','Computer Networks',          3,1),
        ])
        # Alice has 2 Fs  ← good for testing AI backlog assistant
        cur.executemany(
            "INSERT OR IGNORE INTO semester_results"
            "(student_id,subject_code,subject_name,credits,"
            " internal_marks,external_marks,total_marks,"
            " grade,grade_point,year,semester,exam_date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", [
            ('22BD1A0501','CS301','Data Structures',4,            25,62,87,'A+',9, 3,1,'2024-11-20'),
            ('22BD1A0501','CS302','Algorithms',4,                  22,45,67,'A', 8, 3,1,'2024-11-22'),
            ('22BD1A0501','CS303','Database Management Systems',3, 18,20,38,'F', 0, 3,1,'2024-11-24'),
            ('22BD1A0501','CS304','Operating Systems',3,           20,55,75,'B+',7, 3,1,'2024-11-26'),
            ('22BD1A0501','CS305','Computer Networks',3,           15,22,37,'F', 0, 3,1,'2024-11-28'),
            ('22BD1A0502','CS301','Data Structures',4,            28,65,93,'O', 10,3,1,'2024-11-20'),
            ('22BD1A0502','CS302','Algorithms',4,                  26,60,86,'A+',9, 3,1,'2024-11-22'),
            ('22BD1A0502','CS303','Database Management Systems',3, 24,58,82,'A+',9, 3,1,'2024-11-24'),
            ('22BD1A0502','CS304','Operating Systems',3,           22,52,74,'B+',7, 3,1,'2024-11-26'),
            ('22BD1A0502','CS305','Computer Networks',3,           25,55,80,'A+',9, 3,1,'2024-11-28'),
        ])
        cur.executemany(
            "INSERT OR IGNORE INTO internal_marks"
            "(student_id,subject_code,"
            " mid1_exam,mid1_assignment,mid1_ppt,"
            " mid2_exam,mid2_assignment,mid2_ppt) VALUES(?,?,?,?,?,?,?,?)", [
            ('22BD1A0501','CS301', 20,4,4, 22,4,5),
            ('22BD1A0501','CS302', 18,3,3, 20,4,4),
            ('22BD1A0501','CS303', 12,3,2, 14,3,3),
            ('22BD1A0502','CS301', 24,5,5, 25,5,5),
            ('22BD1A0502','CS302', 22,5,4, 23,5,5),
        ])

    con.commit()
    con.close()


# ══════════════════════════════════════════════════════════════════════════════
#  CONNECTION HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row   # rows behave like dicts
    con.execute("PRAGMA foreign_keys = ON")
    return con

def _all(cur, sql, params=()):
    return [dict(r) for r in cur.execute(sql, params).fetchall()]

def _one(cur, sql, params=()):
    r = cur.execute(sql, params).fetchone()
    return dict(r) if r else None

def _scalar(cur, sql, params=()):
    return cur.execute(sql, params).fetchone()[0]


# ══════════════════════════════════════════════════════════════════════════════
#  UPSERT HELPERS  (SQLite uses ON CONFLICT … DO UPDATE instead of ON DUPLICATE KEY)
# ══════════════════════════════════════════════════════════════════════════════
def _upsert_mid1(cur, ht, code, exam, assign, ppt):
    cur.execute("""
        INSERT INTO internal_marks(student_id,subject_code,mid1_exam,mid1_assignment,mid1_ppt)
        VALUES(?,?,?,?,?)
        ON CONFLICT(student_id,subject_code) DO UPDATE SET
            mid1_exam=excluded.mid1_exam,
            mid1_assignment=excluded.mid1_assignment,
            mid1_ppt=excluded.mid1_ppt
    """, (ht, code, exam, assign, ppt))

def _upsert_mid2(cur, ht, code, exam, assign, ppt):
    cur.execute("""
        INSERT INTO internal_marks(student_id,subject_code,mid2_exam,mid2_assignment,mid2_ppt)
        VALUES(?,?,?,?,?)
        ON CONFLICT(student_id,subject_code) DO UPDATE SET
            mid2_exam=excluded.mid2_exam,
            mid2_assignment=excluded.mid2_assignment,
            mid2_ppt=excluded.mid2_ppt
    """, (ht, code, exam, assign, ppt))

def _upsert_result(cur, sid, code, name, credits, intm, extm, total, grade, gp, yr, sem, dt):
    cur.execute("""
        INSERT INTO semester_results
            (student_id,subject_code,subject_name,credits,
             internal_marks,external_marks,total_marks,grade,grade_point,
             year,semester,exam_date)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(student_id,subject_code,year,semester) DO UPDATE SET
            subject_name=excluded.subject_name,
            credits=excluded.credits,
            internal_marks=excluded.internal_marks,
            external_marks=excluded.external_marks,
            total_marks=excluded.total_marks,
            grade=excluded.grade,
            grade_point=excluded.grade_point,
            exam_date=excluded.exam_date
    """, (sid, code, name, credits, intm, extm, total, grade, gp, yr, sem, dt))


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH DECORATORS
# ══════════════════════════════════════════════════════════════════════════════
def admin_required(f):
    @wraps(f)
    def d(*a, **kw):
        if session.get('role') != 'admin': return redirect(url_for('admin_login'))
        return f(*a, **kw)
    return d

def faculty_required(f):
    @wraps(f)
    def d(*a, **kw):
        if session.get('role') != 'faculty': return redirect(url_for('faculty_login'))
        return f(*a, **kw)
    return d

def student_required(f):
    @wraps(f)
    def d(*a, **kw):
        if session.get('role') != 'student': return redirect(url_for('student_login'))
        return f(*a, **kw)
    return d


# ══════════════════════════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/')
def index():
    return render_template('index.html')


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN PORTAL
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == 'admin':
            session['role'] = 'admin'; session['user'] = 'Admin'
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid password'
    return render_template('admin_login.html', error=error)


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    con = get_db(); cur = con.cursor()
    s   = _scalar(cur, "SELECT COUNT(*) FROM students")
    f   = _scalar(cur, "SELECT COUNT(*) FROM faculty")
    r   = _scalar(cur, "SELECT COUNT(*) FROM semester_results")
    sub = _scalar(cur, "SELECT COUNT(*) FROM faculty_subjects")
    con.close()
    return render_template('admin.html',
        student_count=s, faculty_count=f, result_count=r, subject_count=sub)


@app.route('/admin/assign_subjects', methods=['GET','POST'])
@admin_required
def assign_subjects():
    con = get_db(); cur = con.cursor()
    msg = None
    if request.method == 'POST':
        d = request.form
        try:
            cur.execute(
                "INSERT INTO faculty_subjects(faculty_id,subject_code,subject_name,year,semester)"
                " VALUES(?,?,?,?,?)",
                (d['faculty_id'], d['subject_code'], d['subject_name'], d['year'], d['semester']))
            con.commit(); msg = ('success', 'Subject assigned successfully!')
        except sqlite3.IntegrityError:
            msg = ('error', 'This subject code already exists for that semester.')
        except Exception as e:
            msg = ('error', str(e))

    faculty     = _all(cur, "SELECT faculty_id,name FROM faculty ORDER BY name")
    assignments = _all(cur,
        "SELECT fs.*,f.name AS faculty_name FROM faculty_subjects fs"
        " JOIN faculty f ON fs.faculty_id=f.faculty_id ORDER BY fs.id DESC")
    con.close()
    return render_template('assign_subjects.html',
        faculty=faculty, assignments=assignments, msg=msg)


@app.route('/admin/enter_marks', methods=['GET','POST'])
@admin_required
def enter_marks():
    con = get_db(); cur = con.cursor()
    students = _all(cur, "SELECT hallticket,name FROM students ORDER BY name")
    con.close()
    return render_template('enter_marks.html', students=students)


@app.route('/admin/save_marks', methods=['POST'])
@admin_required
def save_marks():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data received'})
    con = get_db(); cur = con.cursor()
    try:
        for row in data['rows']:
            _upsert_result(cur,
                data['student_id'], row['subject_code'], row['subject_name'],
                row['credits'], row['internal_marks'], row['external_marks'],
                row['total_marks'], row['grade'], row['grade_point'],
                data['year'], data['semester'], row.get('exam_date'))
        con.commit()
        return jsonify({'success': True,
                        'message': f"{len(data['rows'])} records saved successfully!"})
    except Exception as e:
        con.rollback(); return jsonify({'success': False, 'message': str(e)})
    finally:
        con.close()


@app.route('/admin/manage_students', methods=['GET','POST'])
@admin_required
def manage_students():
    con = get_db(); cur = con.cursor()
    msg = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            try:
                ht = request.form['hallticket']
                cur.execute("INSERT INTO students(hallticket,name,password) VALUES(?,?,?)",
                            (ht, request.form['name'], ht))
                con.commit(); msg = ('success', 'Student added!')
            except sqlite3.IntegrityError:
                msg = ('error', 'Hall ticket number already exists.')
            except Exception as e:
                msg = ('error', str(e))
        elif action == 'delete':
            cur.execute("DELETE FROM students WHERE hallticket=?", (request.form['hallticket'],))
            con.commit(); msg = ('success', 'Student deleted!')
    students = _all(cur, "SELECT * FROM students ORDER BY name")
    con.close()
    return render_template('manage_students.html', students=students, msg=msg)


@app.route('/admin/manage_faculty', methods=['GET','POST'])
@admin_required
def manage_faculty():
    con = get_db(); cur = con.cursor()
    msg = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            try:
                fid = request.form['faculty_id']
                cur.execute("INSERT INTO faculty(faculty_id,name,password) VALUES(?,?,?)",
                            (fid, request.form['name'], fid))
                con.commit(); msg = ('success', 'Faculty added!')
            except sqlite3.IntegrityError:
                msg = ('error', 'Faculty ID already exists.')
            except Exception as e:
                msg = ('error', str(e))
        elif action == 'delete':
            cur.execute("DELETE FROM faculty WHERE faculty_id=?", (request.form['faculty_id'],))
            con.commit(); msg = ('success', 'Faculty deleted!')
    faculty = _all(cur, "SELECT * FROM faculty ORDER BY name")
    con.close()
    return render_template('manage_faculty.html', faculty=faculty, msg=msg)


@app.route('/admin/change_password', methods=['GET','POST'])
@admin_required
def admin_change_password():
    msg = None
    if request.method == 'POST':
        if request.form.get('old_password') == 'admin':
            msg = ('success', 'Password updated!')
        else:
            msg = ('error', 'Current password is incorrect.')
    return render_template('admin_change_password.html', msg=msg)


# ══════════════════════════════════════════════════════════════════════════════
#  FACULTY PORTAL
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/faculty/login', methods=['GET','POST'])
def faculty_login():
    error = None
    if request.method == 'POST':
        con = get_db(); cur = con.cursor()
        f = _one(cur, "SELECT * FROM faculty WHERE faculty_id=? AND password=?",
                 (request.form['faculty_id'], request.form['password']))
        con.close()
        if f:
            session['role']       = 'faculty'
            session['user']       = f['name']
            session['faculty_id'] = f['faculty_id']
            return redirect(url_for('faculty_dashboard'))
        error = 'Invalid credentials'
    return render_template('faculty_login.html', error=error)


@app.route('/faculty/dashboard')
@faculty_required
def faculty_dashboard():
    con = get_db(); cur = con.cursor()
    subjects = _all(cur, """
        SELECT fs.*, COUNT(DISTINCT sr.student_id) AS student_count
        FROM   faculty_subjects fs
        LEFT JOIN semester_results sr
               ON fs.subject_code=sr.subject_code AND fs.semester=sr.semester
        WHERE  fs.faculty_id=?
        GROUP  BY fs.id
    """, (session['faculty_id'],))
    con.close()
    return render_template('faculty.html', subjects=subjects)


@app.route('/faculty/enter_internal', methods=['GET','POST'])
@faculty_required
def enter_internal():
    con = get_db(); cur = con.cursor()
    msg          = None
    subject_code = request.args.get('subject_code', '')
    mid          = request.args.get('mid', '1')

    subject   = _one(cur,
        "SELECT * FROM faculty_subjects WHERE faculty_id=? AND subject_code=?",
        (session['faculty_id'], subject_code))
    students  = _all(cur, "SELECT hallticket,name FROM students ORDER BY name")
    marks_map = {}
    if subject_code:
        for m in _all(cur, "SELECT * FROM internal_marks WHERE subject_code=?", (subject_code,)):
            marks_map[m['student_id']] = m

    if request.method == 'POST':
        try:
            for s in students:
                ht = s['hallticket']
                _f = lambda k: float(request.form.get(k, 0) or 0)
                if mid == '1':
                    _upsert_mid1(cur, ht, subject_code,
                        _f(f'mid1_exam_{ht}'), _f(f'mid1_assign_{ht}'), _f(f'mid1_ppt_{ht}'))
                else:
                    _upsert_mid2(cur, ht, subject_code,
                        _f(f'mid2_exam_{ht}'), _f(f'mid2_assign_{ht}'), _f(f'mid2_ppt_{ht}'))
            con.commit()
            msg = ('success', f'MID-{mid} marks saved successfully!')
        except Exception as e:
            con.rollback(); msg = ('error', str(e))

    con.close()
    return render_template('enter_internal.html',
        students=students, subject=subject,
        subject_code=subject_code, mid=mid,
        marks_map=marks_map, msg=msg)


@app.route('/faculty/change_password', methods=['GET','POST'])
@faculty_required
def faculty_change_password():
    msg = None
    if request.method == 'POST':
        con = get_db(); cur = con.cursor()
        old, new = request.form.get('old_password'), request.form.get('new_password')
        row = cur.execute("SELECT password FROM faculty WHERE faculty_id=?",
                          (session['faculty_id'],)).fetchone()
        if row and row[0] == old:
            cur.execute("UPDATE faculty SET password=? WHERE faculty_id=?",
                        (new, session['faculty_id']))
            con.commit(); msg = ('success', 'Password changed successfully!')
        else:
            msg = ('error', 'Current password is incorrect.')
        con.close()
    return render_template('faculty_change_password.html', msg=msg)


# ══════════════════════════════════════════════════════════════════════════════
#  STUDENT PORTAL
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/student/login', methods=['GET','POST'])
def student_login():
    error = None
    if request.method == 'POST':
        con = get_db(); cur = con.cursor()
        s = _one(cur, "SELECT * FROM students WHERE hallticket=? AND password=?",
                 (request.form['hallticket'], request.form['password']))
        con.close()
        if s:
            session['role']       = 'student'
            session['user']       = s['name']
            session['hallticket'] = s['hallticket']
            return redirect(url_for('student_dashboard'))
        error = 'Invalid Hall Ticket or Password'
    return render_template('student_login.html', error=error)


@app.route('/student/dashboard')
@student_required
def student_dashboard():
    ht  = session['hallticket']
    con = get_db(); cur = con.cursor()
    all_results = _all(cur,
        "SELECT * FROM semester_results WHERE student_id=? ORDER BY year,semester", (ht,))
    con.close()

    semesters = {}
    for r in all_results:
        semesters.setdefault((r['year'], r['semester']), []).append(r)

    sgpa_data = {}
    for key, rows in semesters.items():
        gp = sum(r['grade_point']*r['credits'] for r in rows)
        cr = sum(r['credits'] for r in rows)
        sgpa_data[key] = round(gp/cr, 2) if cr else 0

    all_gp = sum(r['grade_point']*r['credits'] for r in all_results)
    all_cr = sum(r['credits'] for r in all_results)
    cgpa   = round(all_gp/all_cr, 2) if all_cr else 0

    latest_key     = max(semesters.keys()) if semesters else None
    latest_rows    = semesters.get(latest_key, [])
    sgpa           = sgpa_data.get(latest_key, 0)
    total_credits  = sum(r['credits'] for r in latest_rows)
    gained_credits = sum(r['credits'] for r in latest_rows if r['grade'] != 'F')
    total_marks    = sum(r['total_marks'] for r in latest_rows)
    backlogs       = [r for r in all_results if r['grade'] == 'F']

    return render_template('student_dashboard.html',
        all_results=all_results, semesters=semesters, sgpa_data=sgpa_data,
        cgpa=cgpa, sgpa=sgpa, total_credits=total_credits,
        gained_credits=gained_credits, total_marks=total_marks,
        backlogs=backlogs, latest_key=latest_key)


@app.route('/student/mid_marks')
@student_required
def student_mid_marks():
    con = get_db(); cur = con.cursor()
    marks = _all(cur, """
        SELECT im.*, COALESCE(fs.subject_name, im.subject_code) AS subject_name
        FROM   internal_marks im
        LEFT JOIN faculty_subjects fs ON im.subject_code=fs.subject_code
        WHERE  im.student_id=?
    """, (session['hallticket'],))
    con.close()
    return render_template('student_mid_marks.html', marks=marks)


@app.route('/student/results')
@student_required
def student_results():
    con = get_db(); cur = con.cursor()
    results = _all(cur,
        "SELECT * FROM semester_results WHERE student_id=?"
        " ORDER BY year,semester,subject_code", (session['hallticket'],))
    con.close()
    semesters = {}
    for r in results:
        semesters.setdefault(f"Year {r['year']} - Sem {r['semester']}", []).append(r)
    return render_template('student_results.html', semesters=semesters)


@app.route('/student/backlogs')
@student_required
def student_backlogs():
    con = get_db(); cur = con.cursor()
    backlogs = _all(cur,
        "SELECT * FROM semester_results WHERE student_id=? AND grade='F'",
        (session['hallticket'],))
    con.close()
    return render_template('student_backlogs.html', backlogs=backlogs)


@app.route('/student/ranking')
@student_required
def student_ranking():
    con = get_db(); cur = con.cursor()
    rows = _all(cur, """
        SELECT s.hallticket, s.name, sr.grade_point, sr.credits
        FROM   students s
        LEFT JOIN semester_results sr ON s.hallticket=sr.student_id
    """)
    con.close()

    gpa_map = {}
    for r in rows:
        ht = r['hallticket']
        gpa_map.setdefault(ht, {'name': r['name'], 'gp_sum': 0.0, 'cr_sum': 0})
        if r['grade_point'] and r['credits']:
            gpa_map[ht]['gp_sum'] += r['grade_point'] * r['credits']
            gpa_map[ht]['cr_sum'] += r['credits']

    leaderboard = []
    for ht, d in gpa_map.items():
        cgpa = round(d['gp_sum']/d['cr_sum'], 2) if d['cr_sum'] else 0
        leaderboard.append({'hallticket': ht, 'name': d['name'], 'cgpa': cgpa})
    leaderboard.sort(key=lambda x: x['cgpa'], reverse=True)
    for i, r in enumerate(leaderboard):
        r['rank'] = i + 1

    return render_template('student_ranking.html',
        leaderboard=leaderboard, my_ht=session['hallticket'])


@app.route('/student/change_password', methods=['GET','POST'])
@student_required
def student_change_password():
    msg = None
    if request.method == 'POST':
        con = get_db(); cur = con.cursor()
        old, new = request.form.get('old_password'), request.form.get('new_password')
        row = cur.execute("SELECT password FROM students WHERE hallticket=?",
                          (session['hallticket'],)).fetchone()
        if row and row[0] == old:
            cur.execute("UPDATE students SET password=? WHERE hallticket=?",
                        (new, session['hallticket']))
            con.commit(); msg = ('success', 'Password changed successfully!')
        else:
            msg = ('error', 'Current password is incorrect.')
        con.close()
    return render_template('student_change_password.html', msg=msg)


@app.route('/student/backlog_assistant')
@student_required
def backlog_assistant():
    con = get_db(); cur = con.cursor()
    backlogs = _all(cur,
        "SELECT * FROM semester_results WHERE student_id=? AND grade='F'",
        (session['hallticket'],))
    con.close()
    return render_template('backlog_assistant.html', backlogs=backlogs)


@app.route('/student/generate_plan', methods=['POST'])
@student_required
def generate_plan():
    data           = request.get_json()
    backlogs       = data.get('backlogs', [])
    study_hours    = max(1, int(data.get('study_hours', 4)))
    num_days       = max(1, int(data.get('num_days',    7)))
    preferred_time = data.get('preferred_time', 'morning')

    if not backlogs:
        return jsonify({'success': False, 'message': 'No backlogs found'})

    # Priority weighting  (lower score → needs more time)
    total_weight = sum(100 - float(b.get('marks', 50)) for b in backlogs) or 1
    for b in backlogs:
        w = 100 - float(b.get('marks', 50))
        b['hours_allocated'] = round((w/total_weight)*study_hours*num_days, 1)

    today = datetime.date.today()
    idx   = 0
    timetable = []
    for day in range(num_days):
        date      = today + datetime.timedelta(days=day)
        remaining = study_hours
        slots     = []
        while remaining > 0 and backlogs:
            s      = backlogs[idx % len(backlogs)]
            slot_h = min(2, remaining)
            slots.append({'subject': s['subject_name'], 'hours': slot_h})
            remaining -= slot_h
            idx       += 1
        timetable.append({'day': day+1, 'date': date.strftime('%a, %d %b'),
                          'slots': slots, 'break_time': '30 min after each 2 hrs'})

    resources = {}
    for b in backlogs:
        name  = b['subject_name']
        q     = name.replace(' ', '+')
        resources[name] = [
            {'type': 'YouTube',
             'title': f'{name} Lectures',
             'url':   f'https://www.youtube.com/results?search_query={q}+full+course'},
            {'type': 'PDF Notes',
             'title': f'{name} Study Material',
             'url':   f'https://www.google.com/search?q={q}+notes+pdf'},
            {'type': 'NPTEL',
             'title': f'{name} Free Course',
             'url':   f'https://nptel.ac.in/search?query={q}'},
            {'type': 'Practice',
             'title': f'{name} Practice Problems',
             'url':   f'https://www.google.com/search?q={q}+previous+year+questions+with+solutions'},
        ]

    return jsonify({
        'success':    True,
        'timetable':  timetable,
        'resources':  resources,
        'backlogs':   backlogs,
        'motivation': random.choice([
            "Every expert was once a beginner. Keep going! 💪",
            "Success is the sum of small efforts repeated day in and day out. 🌟",
            "Believe you can and you're halfway there! 🚀",
            "Hard work beats talent when talent doesn't work hard! 🔥",
            "The only way to do great work is to love what you do! ❤️",
            "Push yourself — no one else is going to do it for you! ⚡",
        ]),
    })


# ── Logout ────────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ── /init_db  — wipe & re-seed (handy reset button) ──────────────────────────
@app.route('/init_db')
def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    _bootstrap()
    return ("<h2 style='font-family:sans-serif'>✅ Database reset with sample data!</h2>"
            "<a href='/'>← Go Home</a>")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    _bootstrap()   # creates srms.db + sample data on very first run

    print()
    print("=" * 56)
    print("  SRMS  →  http://127.0.0.1:5000")
    print()
    print("  Admin login    password        :  admin")
    print("  Faculty login  F001 or F002    :  F001 / F002")
    print("  Student login  22BD1A0501      :  22BD1A0501")
    print("  (Alice has 2 backlogs — good for testing AI assistant)")
    print("=" * 56)
    print()

    app.run(debug=True, port=5000)
