from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────────
# IN-MEMORY DATABASE
# This acts as your temporary database while testing.
# All data lives here and updates in real time.
# ─────────────────────────────────────────────────────────────

patients = [
    {"id": 11763, "arabicname": "أحمد محمد", "englishname": "Ahmed Mohamed", "mobile": "0538892874"}
]

appointments = [
    {"id": 46577, "patient_id": 11763, "patient_name": "أحمد محمد", "doctor_id": 113,
     "doctor_name": "د. فهد الطاسان", "date": "2026/03/10",
     "fromtime": "10:00 AM", "endtime": "10:30 AM", "status": "confirmed"}
]

notes = []
activity_log = []

specialties = [
    {"id": 1, "name": "تقويم الأسنان"},
    {"id": 2, "name": "زراعة الأسنان"},
    {"id": 3, "name": "طب أسنان الأطفال"},
    {"id": 4, "name": "علاج عصب الأسنان"},
    {"id": 5, "name": "تجميل الأسنان"}
]

doctors = [
    {"id": 113, "name": "د. فهد الطاسان",      "specialty_id": 5},
    {"id": 114, "name": "د. أنس جان",           "specialty_id": 2},
    {"id": 115, "name": "د. ماهر كشكول",        "specialty_id": 1},
    {"id": 116, "name": "د. عبدالعزيز البارقي", "specialty_id": 3},
    {"id": 117, "name": "د. نايف المطيري",      "specialty_id": 4}
]


def log(message):
    """Add a new entry to the live activity log."""
    entry = {"time": datetime.now().strftime("%I:%M:%S %p"), "message": message}
    activity_log.insert(0, entry)
    if len(activity_log) > 50:
        activity_log.pop()


def find_patient(pid):
    return next((p for p in patients if p["id"] == int(pid)), None)


def find_doctor(did):
    return next((d for d in doctors if d["id"] == int(did)), None)


# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────

DASHBOARD_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lustro CRM</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'Segoe UI',Tahoma,sans-serif; background:#0f172a; color:#e2e8f0; min-height:100vh; }

    header {
      background:linear-gradient(135deg,#1e293b,#0f172a);
      padding:18px 30px;
      border-bottom:2px solid #6366f1;
      display:flex; align-items:center; gap:14px;
    }
    header h1 { font-size:20px; color:#a5b4fc; }
    header p  { font-size:12px; color:#64748b; margin-top:2px; }
    .live-dot {
      width:10px; height:10px; background:#22c55e;
      border-radius:50%; animation:pulse 1.5s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .badge-live {
      background:#22c55e22; color:#22c55e;
      border:1px solid #22c55e44;
      padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600;
    }

    .stats {
      display:grid; grid-template-columns:repeat(4,1fr);
      gap:15px; padding:20px;
    }
    .stat {
      background:#1e293b; border-radius:12px;
      padding:18px 22px; border:1px solid #334155;
      transition:transform .2s;
    }
    .stat:hover { transform:translateY(-2px); }
    .stat-num   { font-size:30px; font-weight:700; color:#6366f1; }
    .stat-label { font-size:12px; color:#64748b; margin-top:4px; }

    .toolbar { padding:0 20px 15px; display:flex; align-items:center; gap:10px; }
    .btn {
      background:#6366f1; color:white; border:none;
      padding:8px 20px; border-radius:8px; cursor:pointer;
      font-size:13px; transition:background .2s;
    }
    .btn:hover { background:#4f46e5; }
    .btn-danger { background:#dc2626; }
    .btn-danger:hover { background:#b91c1c; }

    .grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; padding:0 20px 30px; }
    .card {
      background:#1e293b; border-radius:12px;
      padding:20px; border:1px solid #334155;
    }
    .card.full { grid-column:1/-1; }
    .card h2   { font-size:14px; color:#94a3b8; margin-bottom:15px; display:flex; align-items:center; gap:8px; }

    table { width:100%; border-collapse:collapse; font-size:13px; }
    th {
      background:#0f172a; color:#64748b;
      padding:10px 12px; text-align:right; font-weight:600;
    }
    td { padding:10px 12px; border-bottom:1px solid #0f172a; }
    tr:last-child td { border-bottom:none; }
    tr:hover td { background:#1e3a5f18; }

    .badge {
      padding:3px 10px; border-radius:20px;
      font-size:11px; font-weight:600; display:inline-block;
    }
    .confirmed  { background:#16a34a22; color:#22c55e;  border:1px solid #22c55e44; }
    .held       { background:#d9770622; color:#f97316;  border:1px solid #f9731644; }
    .cancelled  { background:#dc262622; color:#f87171;  border:1px solid #f8717144; }
    .rescheduled{ background:#7c3aed22; color:#a78bfa;  border:1px solid #a78bfa44; }
    .booked     { background:#0369a122; color:#38bdf8;  border:1px solid #38bdf844; }
    .active     { background:#16a34a22; color:#22c55e;  border:1px solid #22c55e44; }

    .log-entry  { padding:9px 12px; border-bottom:1px solid #0f172a; font-size:12px; display:flex; gap:12px; }
    .log-entry:last-child { border-bottom:none; }
    .log-time   { color:#6366f1; min-width:90px; font-weight:600; }
    .log-msg    { color:#cbd5e1; }
    .log-box    { max-height:300px; overflow-y:auto; }

    .empty { color:#475569; font-size:13px; padding:15px 0; text-align:center; }
    .counter { font-size:11px; color:#475569; margin-right:auto; }
  </style>
</head>
<body>

<header>
  <div class="live-dot"></div>
  <div>
    <h1>🦷 Lustro CRM — لوحة التحكم</h1>
    <p>عيادات لوسترو — حي المروة، جدة | تتحدث تلقائياً كل 5 ثوانٍ</p>
  </div>
  <span class="badge-live" style="margin-right:auto">● LIVE</span>
</header>

<div class="stats" id="stats">
  <div class="stat"><div class="stat-num">—</div><div class="stat-label">إجمالي المرضى</div></div>
  <div class="stat"><div class="stat-num">—</div><div class="stat-label">مواعيد مؤكدة</div></div>
  <div class="stat"><div class="stat-num">—</div><div class="stat-label">مواعيد ملغاة</div></div>
  <div class="stat"><div class="stat-num">—</div><div class="stat-label">محجوزة مؤقتاً</div></div>
</div>

<div class="toolbar">
  <button class="btn" onclick="load()">🔄 تحديث الآن</button>
  <button class="btn btn-danger" onclick="resetData()">🗑️ مسح البيانات</button>
  <span class="counter" id="last-update"></span>
</div>

<div class="grid">

  <div class="card full">
    <h2>📅 المواعيد</h2>
    <table>
      <thead><tr>
        <th>رقم الموعد</th><th>المريض</th><th>الطبيب</th>
        <th>التاريخ</th><th>الوقت</th><th>الحالة</th>
      </tr></thead>
      <tbody id="appt-body"><tr><td colspan="6" class="empty">جاري التحميل...</td></tr></tbody>
    </table>
  </div>

  <div class="card">
    <h2>👤 المرضى المسجلون</h2>
    <table>
      <thead><tr><th>رقم</th><th>الاسم</th><th>الجوال</th></tr></thead>
      <tbody id="pat-body"><tr><td colspan="3" class="empty">جاري التحميل...</td></tr></tbody>
    </table>
  </div>

  <div class="card">
    <h2>⚡ سجل النشاط المباشر</h2>
    <div class="log-box" id="log-body">
      <div class="empty">لا يوجد نشاط بعد</div>
    </div>
  </div>

  <div class="card full">
    <h2>📝 ملاحظات المكالمات</h2>
    <table>
      <thead><tr><th>المريض</th><th>الملاحظة</th><th>الوقت</th></tr></thead>
      <tbody id="notes-body"><tr><td colspan="3" class="empty">لا توجد ملاحظات بعد</td></tr></tbody>
    </table>
  </div>

</div>

<script>
async function load() {
  try {
    const [appts, pats, logs, nts] = await Promise.all([
      fetch('/api/appointments').then(r => r.json()),
      fetch('/api/patients').then(r => r.json()),
      fetch('/api/log').then(r => r.json()),
      fetch('/api/notes').then(r => r.json())
    ])

    // Stats
    document.getElementById('stats').innerHTML =
      stat(pats.length, 'إجمالي المرضى') +
      stat(appts.filter(a => a.status === 'confirmed').length, 'مواعيد مؤكدة') +
      stat(appts.filter(a => a.status === 'cancelled').length, 'مواعيد ملغاة') +
      stat(appts.filter(a => a.status === 'held').length, 'محجوزة مؤقتاً')

    // Appointments
    document.getElementById('appt-body').innerHTML = appts.length
      ? appts.map(a => `<tr>
          <td><strong>#${a.id}</strong></td>
          <td>${a.patient_name || '—'}</td>
          <td>${a.doctor_name || '—'}</td>
          <td>${a.date || '—'}</td>
          <td>${a.fromtime || '—'} → ${a.endtime || '—'}</td>
          <td><span class="badge ${a.status}">${a.status}</span></td>
        </tr>`).join('')
      : '<tr><td colspan="6" class="empty">لا توجد مواعيد بعد</td></tr>'

    // Patients
    document.getElementById('pat-body').innerHTML = pats.length
      ? pats.map(p => `<tr>
          <td>#${p.id}</td>
          <td>${p.arabicname || p.englishname || '—'}</td>
          <td>${p.mobile || '—'}</td>
        </tr>`).join('')
      : '<tr><td colspan="3" class="empty">لا يوجد مرضى بعد</td></tr>'

    // Activity Log
    document.getElementById('log-body').innerHTML = logs.length
      ? logs.map(l => `<div class="log-entry">
          <span class="log-time">${l.time}</span>
          <span class="log-msg">${l.message}</span>
        </div>`).join('')
      : '<div class="empty">لا يوجد نشاط بعد</div>'

    // Notes
    document.getElementById('notes-body').innerHTML = nts.length
      ? nts.map(n => `<tr>
          <td>${n.patient_name || '#' + n.patient_id}</td>
          <td>${n.notes}</td>
          <td>${n.time}</td>
        </tr>`).join('')
      : '<tr><td colspan="3" class="empty">لا توجد ملاحظات بعد</td></tr>'

    document.getElementById('last-update').textContent =
      'آخر تحديث: ' + new Date().toLocaleTimeString('ar-SA')

  } catch(e) {
    console.error('Load error:', e)
  }
}

function stat(num, label) {
  return `<div class="stat"><div class="stat-num">${num}</div><div class="stat-label">${label}</div></div>`
}

async function resetData() {
  if (!confirm('هل أنت متأكد من مسح جميع البيانات؟')) return
  await fetch('/api/reset', { method: 'POST' })
  load()
}

load()
setInterval(load, 5000)
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────
# DASHBOARD ROUTE
# ─────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


# ─────────────────────────────────────────────────────────────
# INTERNAL DATA APIs (used by the dashboard)
# ─────────────────────────────────────────────────────────────

@app.route('/api/appointments')
def api_appointments():
    return jsonify(appointments)

@app.route('/api/patients')
def api_patients():
    return jsonify(patients)

@app.route('/api/log')
def api_log():
    return jsonify(activity_log)

@app.route('/api/notes')
def api_notes():
    return jsonify(notes)

@app.route('/api/reset', methods=['POST'])
def api_reset():
    appointments.clear()
    notes.clear()
    activity_log.clear()
    log('🔄 تم مسح جميع البيانات')
    return jsonify({"status": "reset"})


# ─────────────────────────────────────────────────────────────
# PATIENT ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.route('/MyCallAi/patients/search')
def search_patient():
    phone = request.args.get('phone', '')
    patient = next((p for p in patients if p['mobile'] == phone), None)
    if patient:
        log(f"🔍 تم إيجاد المريض: {patient.get('arabicname') or patient.get('englishname')} ({phone})")
        return jsonify(patient)
    else:
        log(f"🔍 لم يتم إيجاد المريض بالرقم: {phone}")
        return jsonify({"message": "Patient not found"}), 404


@app.route('/MyCallAi/patients/<int:pid>/insurance/eligibility')
@app.route('/MyCallAi/insurance/eligibility')
def get_eligibility(pid=None):
    pid = pid or request.args.get('patient_id')
    log(f"🏥 تم التحقق من أهلية التأمين للمريض #{pid}")
    return jsonify({"patient_id": pid, "eligible": True, "message": "التأمين ساري وفعّال"})


@app.route('/MyCallAi/patients/<int:pid>/insurance')
def patient_insurance(pid):
    log(f"🏥 تم جلب بيانات التأمين للمريض #{pid}")
    return jsonify({"patient_id": pid, "provider": "Allianz", "policy_number": "ALZ-2024-9987", "status": "active"})


@app.route('/MyCallAi/patients/<int:pid>/notes', methods=['POST'])
def add_note(pid):
    data = request.get_json() or {}
    patient = find_patient(pid)
    note = {
        "patient_id": pid,
        "patient_name": patient.get('arabicname') or patient.get('englishname') if patient else f"#{pid}",
        "notes": data.get('notes', ''),
        "time": datetime.now().strftime("%I:%M %p")
    }
    notes.insert(0, note)
    log(f"📝 تم حفظ ملاحظة للمريض #{pid}")
    return jsonify({"status": "saved", "message": "تم حفظ الملاحظة بنجاح"})


@app.route('/MyCallAi/patients/<int:pid>/consent', methods=['GET'])
def get_consent(pid):
    log(f"✅ تم التحقق من موافقة المريض #{pid}")
    return jsonify({"patient_id": pid, "whatsapp_consent": True})


@app.route('/MyCallAi/patients/<int:pid>/consent', methods=['POST', 'PUT'])
def save_consent(pid):
    log(f"✅ تم حفظ موافقة المريض #{pid}")
    return jsonify({"status": "saved"})


@app.route('/MyCallAi/patients/<int:pid>', methods=['GET'])
def get_patient(pid):
    patient = find_patient(pid)
    if patient:
        return jsonify(patient)
    return jsonify({"message": "Not found"}), 404


@app.route('/MyCallAi/patients/<int:pid>', methods=['POST', 'PUT'])
def update_patient(pid):
    global patients
    data = request.get_json() or {}
    patients = [dict(p, **data) if p['id'] == pid else p for p in patients]
    log(f"✏️ تم تحديث بيانات المريض #{pid}")
    return jsonify({"status": "updated"})


@app.route('/MyCallAi/patients', methods=['POST'])
def create_patient():
    data = request.get_json() or {}
# Normalize bithdate/birthdate — client uses "bithdate" (their typo, must match)
    if 'birthdate' in data:
        data['bithdate'] = data.pop('birthdate')
    new_patient = {"id": int(datetime.now().timestamp()), **data}
    patients.append(new_patient)
    name = new_patient.get('arabicname') or new_patient.get('englishname') or 'غير محدد'
    log(f"✅ تم تسجيل مريض جديد: {name}")
    return jsonify(new_patient), 201


# ─────────────────────────────────────────────────────────────
# SPECIALTIES & DOCTORS
# ─────────────────────────────────────────────────────────────

@app.route('/MyCallAi/specialties')
def get_specialties():
    log("📋 تم جلب قائمة التخصصات")
    return jsonify(specialties)


@app.route('/MyCallAi/doctors')
def get_doctors():
    specialty_id = request.args.get('specialty_id')
    result = [d for d in doctors if str(d['specialty_id']) == str(specialty_id)] if specialty_id else doctors
    log("👨‍⚕️ تم جلب قائمة الأطباء")
    return jsonify(result)


@app.route('/MyCallAi/doctors/<int:did>/schedule')
def get_schedule(did):
    doctor = find_doctor(did)
    log(f"🗓️ تم جلب جدول الطبيب: {doctor['name'] if doctor else f'#{did}'}")
    return jsonify({
        "doctor_id": did,
        "working_days": [
            {"day_id": 1, "day": "الأحد",    "from": "09:00 AM", "to": "06:00 PM"},
            {"day_id": 2, "day": "الاثنين",  "from": "09:00 AM", "to": "06:00 PM"},
            {"day_id": 3, "day": "الثلاثاء", "from": "09:00 AM", "to": "03:00 PM"},
            {"day_id": 4, "day": "الأربعاء", "from": "10:00 AM", "to": "05:00 PM"},
            {"day_id": 5, "day": "الخميس",   "from": "09:00 AM", "to": "02:00 PM"}
        ]
    })


# ─────────────────────────────────────────────────────────────
# APPOINTMENT ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.route('/MyCallAi/appointments/available', methods=['GET', 'POST'])
def get_available():
    # Accept parameters from query string OR body — both work
    data         = request.get_json(silent=True) or {}
    app_dt_fmt   = request.args.get('app_dt_fmt')   or data.get('app_dt_fmt')
    doctorid     = request.args.get('doctorid')      or data.get('doctorid')
    day_id       = request.args.get('day_id')        or data.get('day_id')

    log(f"🕐 تم جلب المواعيد المتاحة | التاريخ: {app_dt_fmt} | الطبيب: {doctorid} | اليوم: {day_id}")
    return jsonify([
        {"fromtime": "09:00 AM", "endtime": "09:30 AM"},
        {"fromtime": "10:00 AM", "endtime": "10:30 AM"},
        {"fromtime": "11:00 AM", "endtime": "11:30 AM"},
        {"fromtime": "01:00 PM", "endtime": "01:30 PM"},
        {"fromtime": "03:00 PM", "endtime": "03:30 PM"},
        {"fromtime": "05:00 PM", "endtime": "05:30 PM"}
    ])


@app.route('/MyCallAi/appointments/hold', methods=['POST'])
def hold_appointment():
    data = request.get_json() or {}
    patient = find_patient(data.get('patientid', 0))
    doctor  = find_doctor(data.get('doctorid', 0))
    appt = {
        "id": int(datetime.now().timestamp()),
        "patient_id":   data.get('patientid'),
        "patient_name": patient.get('arabicname') or patient.get('englishname') if patient else 'غير محدد',
        "doctor_id":    data.get('doctorid'),
        "doctor_name":  doctor['name'] if doctor else 'غير محدد',
        "date":         data.get('appointmentdate'),
        "fromtime":     data.get('fromtime'),
        "endtime":      data.get('endtime'),
        "status":       "held"
    }
    appointments.append(appt)
    log(f"⏳ تم حجز موعد مؤقت لـ {appt['patient_name']} مع {appt['doctor_name']}")
    return jsonify({"appointment_id": appt['id'], "status": "held", "message": "تم حجز الموعد مؤقتاً"})


@app.route('/MyCallAi/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json() or {}
    patient = find_patient(data.get('patientid', 0))
    doctor  = find_doctor(data.get('doctorid', 0))
    appt = {
        "id": int(datetime.now().timestamp()),
        "patient_id":   data.get('patientid'),
        "patient_name": patient.get('arabicname') or patient.get('englishname') if patient else 'غير محدد',
        "doctor_id":    data.get('doctorid'),
        "doctor_name":  doctor['name'] if doctor else 'غير محدد',
        "date":         data.get('appointmentdate'),
        "fromtime":     data.get('fromtime'),
        "endtime":      data.get('endtime'),
        "status":       "booked"
    }
    appointments.append(appt)
    log(f"📌 تم حجز موعد لـ {appt['patient_name']} مع {appt['doctor_name']}")
    return jsonify(appt), 201


@app.route('/MyCallAi/appointments/<int:aid>')
def get_appointment(aid):
    appt = next((a for a in appointments if a['id'] == aid), None)
    if appt:
        return jsonify(appt)
    return jsonify({"message": "Not found"}), 404


@app.route('/MyCallAi/appointments/<int:aid>/confirm', methods=['POST'])
def confirm_appointment(aid):
    global appointments
    appt = next((a for a in appointments if a['id'] == aid), None)
    appointments = [dict(a, status='confirmed') if a['id'] == aid else a for a in appointments]
    name = appt['patient_name'] if appt else f"#{aid}"
    log(f"✅ تم تأكيد الموعد لـ {name}")
    return jsonify({"appointment_id": aid, "status": "confirmed", "message": "تم تأكيد الموعد بنجاح"})

@app.route('/MyCallAi/appointments/confirm', methods=['POST'])
def confirm_appointment_by_body():
    global appointments
    data = request.get_json() or {}
    aid = data.get('hold_id') or data.get('appointment_id')
    appt = next((a for a in appointments if str(a['id']) == str(aid)), None)
    appointments = [dict(a, status='confirmed') if str(a['id']) == str(aid) else a for a in appointments]
    name = appt['patient_name'] if appt else f"#{aid}"
    log(f"✅ تم تأكيد الموعد لـ {name}")
    return jsonify({"appointment_id": aid, "status": "confirmed", "message": "تم تأكيد الموعد بنجاح"})


@app.route('/MyCallAi/appointments/<int:aid>/cancel', methods=['POST', 'PUT'])
def cancel_appointment(aid):
    global appointments
    appt = next((a for a in appointments if a['id'] == aid), None)
    appointments = [dict(a, status='cancelled') if a['id'] == aid else a for a in appointments]
    name = appt['patient_name'] if appt else f"#{aid}"
    log(f"❌ تم إلغاء الموعد لـ {name}")
    return jsonify({"appointment_id": aid, "status": "cancelled", "message": "تم إلغاء الموعد بنجاح"})


@app.route('/MyCallAi/appointments/<int:aid>/reschedule', methods=['POST', 'PUT'])
def reschedule_appointment(aid):
    global appointments
    data = request.get_json() or {}
    appt = next((a for a in appointments if a['id'] == aid), None)
    appointments = [dict(a, **data, status='rescheduled') if a['id'] == aid else a for a in appointments]
    name = appt['patient_name'] if appt else f"#{aid}"
    log(f"🔄 تم تعديل الموعد لـ {name}")
    return jsonify({"appointment_id": aid, "status": "rescheduled", "message": "تم تعديل الموعد بنجاح"})


# ─────────────────────────────────────────────────────────────
# MESSAGING ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.route('/MyCallAi/messages/send', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    log(f"💬 تم إرسال رسالة إلى {data.get('to', 'غير محدد')}")
    return jsonify({"message_id": int(datetime.now().timestamp()), "status": "sent"})


@app.route('/MyCallAi/messages/status/<mid>')
def message_status(mid):
    return jsonify({"message_id": mid, "status": "delivered"})


@app.route('/MyCallAi/webhooks/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.get_json() or {}
    log(f"📲 رسالة واردة على واتساب من {data.get('from', 'غير محدد')}")
    return jsonify({"status": "received"})


# ─────────────────────────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
