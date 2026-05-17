// ─── GRADE CALCULATOR ──────────────────────────────────────────────────────────
function calcGrade(total) {
  if (total >= 90) return { grade: 'O',  gp: 10 };
  if (total >= 80) return { grade: 'A+', gp: 9 };
  if (total >= 70) return { grade: 'A',  gp: 8 };
  if (total >= 60) return { grade: 'B+', gp: 7 };
  if (total >= 50) return { grade: 'B',  gp: 6 };
  if (total >= 40) return { grade: 'C',  gp: 5 };
  return             { grade: 'F',  gp: 0 };
}

// ─── MARKS TABLE AUTO-CALC ─────────────────────────────────────────────────────
function initMarksTable() {
  const table = document.getElementById('marksTable');
  if (!table) return;

  function updateRow(row) {
    const intEl = row.querySelector('.inp-internal');
    const extEl = row.querySelector('.inp-external');
    const totEl = row.querySelector('.inp-total');
    const gradeEl = row.querySelector('.inp-grade');
    const gpEl    = row.querySelector('.inp-gp');

    if (!intEl || !extEl) return;
    const internal = parseFloat(intEl.value) || 0;
    const external = parseFloat(extEl.value) || 0;
    const total    = internal + external;

    if (totEl)   { totEl.value = total; }
    const { grade, gp } = calcGrade(total);
    if (gradeEl) { gradeEl.value = grade; gradeEl.className = `td-input inp-grade grade-color-${grade.replace('+','')} `;  }
    if (gpEl)    { gpEl.value = gp; }
  }

  table.addEventListener('input', e => {
    if (e.target.matches('.inp-internal, .inp-external')) {
      updateRow(e.target.closest('tr'));
    }
  });
}

// ─── SAVE MARKS (ADMIN) ────────────────────────────────────────────────────────
async function saveMarks() {
  const btn = document.getElementById('saveBtn');
  const studentId = document.getElementById('studentSelect')?.value;
  const year = document.getElementById('yearSelect')?.value;
  const semester = document.getElementById('semesterSelect')?.value;
  const msgEl = document.getElementById('saveMsg');

  if (!studentId) { showMsg(msgEl, 'error', 'Please select a student.'); return; }
  if (!year || !semester) { showMsg(msgEl, 'error', 'Please select year and semester.'); return; }

  const rows = [];
  document.querySelectorAll('#marksTable tbody tr').forEach(tr => {
    const code  = tr.querySelector('.inp-code')?.value?.trim();
    const name  = tr.querySelector('.inp-name')?.value?.trim();
    if (!code && !name) return;
    rows.push({
      subject_code:   code,
      subject_name:   name,
      credits:        parseInt(tr.querySelector('.inp-credits')?.value) || 3,
      internal_marks: parseFloat(tr.querySelector('.inp-internal')?.value) || 0,
      external_marks: parseFloat(tr.querySelector('.inp-external')?.value) || 0,
      total_marks:    parseFloat(tr.querySelector('.inp-total')?.value)    || 0,
      grade:          tr.querySelector('.inp-grade')?.value || 'F',
      grade_point:    parseFloat(tr.querySelector('.inp-gp')?.value) || 0,
      exam_date:      tr.querySelector('.inp-date')?.value || null
    });
  });

  if (!rows.length) { showMsg(msgEl, 'error', 'No rows to save.'); return; }

  btn.disabled = true; btn.textContent = 'Saving…';
  try {
    const res = await fetch('/admin/save_marks', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, year, semester, rows })
    });
    const data = await res.json();
    showMsg(msgEl, data.success ? 'success' : 'error', data.message);
  } catch (err) {
    showMsg(msgEl, 'error', 'Network error: ' + err.message);
  }
  btn.disabled = false; btn.textContent = 'Save Results';
}

// ─── ADD ROW ───────────────────────────────────────────────────────────────────
function addRow() {
  const tbody = document.querySelector('#marksTable tbody');
  const idx   = tbody.querySelectorAll('tr').length + 1;
  const tr    = document.createElement('tr');
  tr.innerHTML = `
    <td class="td-num">${idx}</td>
    <td><input class="td-input inp-code"     placeholder="CS301" /></td>
    <td><input class="td-input inp-name" style="width:140px" placeholder="Subject Name" /></td>
    <td><input class="td-input inp-credits"  type="number" value="3" min="1" max="5" style="width:55px"/></td>
    <td><input class="td-input inp-internal" type="number" placeholder="0" min="0" max="30" style="width:65px"/></td>
    <td><input class="td-input inp-external" type="number" placeholder="0" min="0" max="70" style="width:65px"/></td>
    <td><input class="td-input inp-total"    type="number" readonly style="width:65px"/></td>
    <td><input class="td-input inp-grade"    readonly style="width:55px"/></td>
    <td><input class="td-input inp-gp"       type="number" readonly style="width:50px"/></td>
    <td><input class="td-input inp-date"     type="date"/></td>
    <td><button class="btn btn-danger btn-sm" onclick="this.closest('tr').remove()">✕</button></td>
  `;
  tbody.appendChild(tr);
}

// ─── GENERATE PLAN ────────────────────────────────────────────────────────────
async function generatePlan() {
  const btn     = document.getElementById('generateBtn');
  const loading = document.getElementById('planLoading');
  const result  = document.getElementById('planResult');
  const msgEl   = document.getElementById('planMsg');

  const study_hours   = parseInt(document.getElementById('studyHours')?.value) || 4;
  const num_days      = parseInt(document.getElementById('numDays')?.value)    || 7;
  const preferred_time = document.getElementById('preferredTime')?.value      || 'morning';

  const backlogs = [];
  document.querySelectorAll('.backlog-check:checked').forEach(cb => {
    backlogs.push({
      subject_code: cb.dataset.code,
      subject_name: cb.dataset.name,
      marks:        parseInt(cb.dataset.marks) || 30
    });
  });

  if (!backlogs.length) {
    showMsg(msgEl, 'error', 'Please select at least one backlog subject.');
    return;
  }

  btn.disabled = true; btn.textContent = 'Generating…';
  loading.style.display = 'block';
  result.style.display  = 'none';

  try {
    const res  = await fetch('/student/generate_plan', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ backlogs, study_hours, num_days, preferred_time })
    });
    const data = await res.json();
    if (data.success) {
      renderPlan(data);
      result.style.display = 'block';
    } else {
      showMsg(msgEl, 'error', data.message);
    }
  } catch (err) {
    showMsg(msgEl, 'error', 'Error: ' + err.message);
  }
  btn.disabled = false; btn.textContent = '🤖 Generate Study Plan';
  loading.style.display = 'none';
}

function renderPlan(data) {
  // Motivation
  const motEl = document.getElementById('motivation');
  if (motEl && data.motivation) {
    motEl.textContent = data.motivation;
    motEl.parentElement.style.display = 'block';
  }

  // Timetable
  const ttEl = document.getElementById('timetableGrid');
  if (ttEl) {
    ttEl.innerHTML = data.timetable.map(day => `
      <div class="day-card">
        <div class="day-title">Day ${day.day} · ${day.date}</div>
        ${day.slots.map(s => `
          <div class="day-slot">
            <span class="slot-name">${s.subject}</span>
            <span class="slot-hrs">${s.hours}h</span>
          </div>
        `).join('')}
        <div style="font-size:.75rem;color:var(--muted);margin-top:8px;">☕ ${day.break_time}</div>
      </div>
    `).join('');
  }

  // Resources
  const resEl = document.getElementById('resourcesGrid');
  if (resEl) {
    resEl.innerHTML = Object.entries(data.resources).map(([subj, links]) => `
      <div class="resource-card">
        <h4>${subj}</h4>
        ${links.map(l => `
          <a href="${l.url}" target="_blank" class="resource-link">
            <span class="res-type">${l.type}</span>
            <span>${l.title}</span>
          </a>
        `).join('')}
      </div>
    `).join('');
  }

  // Priority table
  const priEl = document.getElementById('priorityTable');
  if (priEl) {
    priEl.innerHTML = `
      <table><thead><tr>
        <th>Subject</th><th>Marks</th><th>Hours Allocated</th><th>Priority</th>
      </tr></thead><tbody>
      ${data.backlogs.sort((a,b) => a.marks - b.marks).map((b, i) => `
        <tr>
          <td><strong>${b.subject_name}</strong></td>
          <td class="td-num">${b.marks}</td>
          <td class="td-num">${b.hours_allocated}h</td>
          <td>${i === 0 ? '<span class="priority-badge">🔴 HIGH</span>' :
               i === 1 ? '<span style="background:rgba(245,136,74,.15);color:var(--orange);padding:2px 8px;border-radius:6px;font-size:.72rem;font-weight:700;">🟡 MED</span>' :
               '<span style="background:rgba(79,142,247,.15);color:var(--accent);padding:2px 8px;border-radius:6px;font-size:.72rem;font-weight:700;">🔵 LOW</span>'}</td>
        </tr>
      `).join('')}
      </tbody></table>`;
  }
}

// ─── DOWNLOAD TIMETABLE ────────────────────────────────────────────────────────
function downloadTimetable() {
  window.print();
}

// ─── UTILS ────────────────────────────────────────────────────────────────────
function showMsg(el, type, msg) {
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 5000);
}

// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initMarksTable();

  // Active nav link
  const path = location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });

  // Auto-dismiss alerts
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
      a.style.transition = 'opacity .5s';
      a.style.opacity = '0';
      setTimeout(() => a.remove(), 500);
    });
  }, 4000);
});
