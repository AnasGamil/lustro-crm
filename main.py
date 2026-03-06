from flask import Flask, request, jsonify, render_template_string, make_response
from flask_cors import CORS
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────────
# IN-MEMORY DATABASE
# Matches REAL Dentak CRM field names exactly (PascalCase)
# ─────────────────────────────────────────────────────────────

patients = [
    {
        "FileNo": "7855",
        "ArabicName": "الهام عيشه التبيتي",
        "EnglishName": "الهام عيشه التبيتي",
        "Mobile": "0503519928",
        "IDCard": "1030514028"
    },
    {
        "FileNo": "12316",
        "ArabicName": "انس جميل محمد احمد",
        "EnglishName": "AnasGamin mohamed احمد",
        "Mobile": "0512345678",
        "IDCard": "2134567892"
    }
]

next_patient_id = 30000
next_appointment_id = 50000

appointments = [
    {
        "AppointmentId": 48504,
        "PatientId": "12316",
        "PatientName": "انس جميل محمد احمد",
        "PatientMobile": "0512345678",
        "DoctorId": 113,
        "DoctorName": "د. أنوار حكمي",
        "AppointmentDate": "2026/03/06",
        "StartTime": "05:30 pm",
        "EndTime": "06:30 pm",
        "Status": "Waiting"
    }
]

notes = []
activity_log = []

specialties = [
    {"Id": 1,  "NameArabic": "الطب النفسي",                    "NameEnglish": "Psychiatry"},
    {"Id": 2,  "NameArabic": "انف أذن وحنجرة",                 "NameEnglish": "Ear, Nose and Throat"},
    {"Id": 3,  "NameArabic": "أمراض القلب والأوعية الدموية",    "NameEnglish": "Cardiology and Vascular Disease"},
    {"Id": 4,  "NameArabic": "السمعيات",                        "NameEnglish": "Audiology"},
    {"Id": 5,  "NameArabic": "العلاج الطبيعي",                  "NameEnglish": "Physiotherapy"},
    {"Id": 6,  "NameArabic": "الطب الباطني",                    "NameEnglish": "Internal Medicine"},
    {"Id": 7,  "NameArabic": "طب الأطفال",                      "NameEnglish": "Pediatrics"},
    {"Id": 8,  "NameArabic": "النساء والولادة",                  "NameEnglish": "Obstetrics and Gynecology"},
    {"Id": 9,  "NameArabic": "الجلدية",                         "NameEnglish": "Dermatology"},
    {"Id": 10, "NameArabic": "الأسنان والتقويم",                "NameEnglish": "Dental and Orthodontics"},
    {"Id": 11, "NameArabic": "جراحة العظام",                    "NameEnglish": "Orthopedic Surgery"},
    {"Id": 12, "NameArabic": "المسالك البولية",                 "NameEnglish": "Urology"},
    {"Id": 13, "NameArabic": "العيون",                          "NameEnglish": "Ophthalmology"},
    {"Id": 14, "NameArabic": "الجراحة العامة",                  "NameEnglish": "General Surgery"},
    {"Id": 15, "NameArabic": "التغذية",                         "NameEnglish": "Nutrition"}
]

doctors = [
    {"Id": 5,   "Code": "1",  "ArabicName": "د. عبدالرحمن قنوت",  "EnglishName": "Dr. Abdulrahman Kannout", "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 6,   "Code": "2",  "ArabicName": "د. نعمت العاقل",     "EnglishName": "Dr. Nimat",               "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 7,   "Code": "3",  "ArabicName": "د. هنادي الحارثي",   "EnglishName": "Dr. Hanadi Alharthi",     "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 108, "Code": "15", "ArabicName": "د. فهد الطاسان",     "EnglishName": "Dr. Fahad Altasan",       "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 113, "Code": "20", "ArabicName": "د. أنوار حكمي",      "EnglishName": "Dr. Anwar Hakmi",         "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 50,  "Code": "8",  "ArabicName": "د. سارة المالكي",    "EnglishName": "Dr. Sarah Almalki",       "SpecialtyId": 7,  "SpecialtyName": "طب الأطفال"},
    {"Id": 60,  "Code": "10", "ArabicName": "د. محمد العتيبي",    "EnglishName": "Dr. Mohammed Alotaibi",   "SpecialtyId": 6,  "SpecialtyName": "الطب الباطني"},
    {"Id": 70,  "Code": "12", "ArabicName": "د. نورة الشهري",     "EnglishName": "Dr. Noura Alshahri",      "SpecialtyId": 9,  "SpecialtyName": "الجلدية"},
]

# Doctor schedules (keyed by doctor Id)
schedules = {
    5: [
        {"DoctorId": 5, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
    ],
    108: [
        {"DoctorId": 108, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "02:00 pm", "EndTime": "02:00 pm", "SlotMinutes": 15},
        {"DoctorId": 108, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "09:00 pm", "EndTime": "09:00 pm", "SlotMinutes": 15},
    ],
    113: [
        {"DoctorId": 113, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 113, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
        {"DoctorId": 113, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 113, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
}

# Default schedule for doctors without specific schedule
default_schedule = [
    {"DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    {"DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
    {"DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    {"DayOfWeek": 3, "DayName": "Monday",    "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
    {"DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
    {"DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "04:00 pm", "EndTime": "04:00 pm", "SlotMinutes": 15},
]


def log(message):
    entry = {"time": datetime.now().strftime("%I:%M:%S %p"), "message": message}
    activity_log.insert(0, entry)
    if len(activity_log) > 50:
        activity_log.pop()


def find_patient(file_no):
    """Find patient by FileNo."""
    return next((p for p in patients if str(p["FileNo"]) == str(file_no)), None)


def find_patient_by_mobile(mobile):
    """Find patient by mobile number."""
    return next((p for p in patients if p["Mobile"] == mobile), None)


def find_doctor(did):
    """Find doctor by Id."""
    return next((d for d in doctors if d["Id"] == int(did)), None)


def find_appointment(aid):
    """Find appointment by AppointmentId."""
    return next((a for a in appointments if a["AppointmentId"] == int(aid)), None)


def generate_slots(doctor_id, slot_date):
    """Generate realistic available time slots for a doctor on a given date."""
    did = str(doctor_id)
    slots = []
    base_times = [
        ("09:00 am", "09:15 am"), ("09:15 am", "09:30 am"), ("09:30 am", "09:45 am"),
        ("10:00 am", "10:15 am"), ("10:15 am", "10:30 am"), ("10:30 am", "10:45 am"),
        ("11:00 am", "11:15 am"), ("11:30 am", "11:45 am"),
        ("02:00 pm", "02:15 pm"), ("02:15 pm", "02:30 pm"), ("02:30 pm", "02:45 pm"),
        ("03:00 pm", "03:15 pm"), ("03:30 pm", "03:45 pm"),
        ("05:00 pm", "05:15 pm"), ("05:15 pm", "05:30 pm"), ("05:30 pm", "05:45 pm"),
    ]
    for start, end in base_times:
        slots.append({
            "DocotorID": did,  # NOTE: Real API has this typo — must match exactly
            "SlotDate": slot_date,
            "StartTime": start,
            "EndTime": end
        })
    return slots


# ─────────────────────────────────────────────────────────────
# DASHBOARD HTML
# ─────────────────────────────────────────────────────────────

DASHBOARD_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lustro CRM — Mock</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'Segoe UI',Tahoma,sans-serif; background:#0f172a; color:#e2e8f0; min-height:100vh; }
    header {
      background:linear-gradient(135deg,#1e293b,#0f172a);
      padding:18px 30px; border-bottom:2px solid #6366f1;
      display:flex; align-items:center; gap:14px;
    }
    header h1 { font-size:20px; color:#a5b4fc; }
    header p  { font-size:12px; color:#64748b; margin-top:2px; }
    .live-dot { width:10px; height:10px; background:#22c55e; border-radius:50%; animation:pulse 1.5s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .badge-live { background:#22c55e22; color:#22c55e; border:1px solid #22c55e44; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
    .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:15px; padding:20px; }
    .stat { background:#1e293b; border-radius:12px; padding:18px 22px; border:1px solid #334155; transition:transform .2s; }
    .stat:hover { transform:translateY(-2px); }
    .stat-num { font-size:30px; font-weight:700; color:#6366f1; }
    .stat-label { font-size:12px; color:#64748b; margin-top:4px; }
    .toolbar { padding:0 20px 15px; display:flex; align-items:center; gap:10px; }
    .btn { background:#6366f1; color:white; border:none; padding:8px 20px; border-radius:8px; cursor:pointer; font-size:13px; transition:background .2s; }
    .btn:hover { background:#4f46e5; }
    .btn-danger { background:#dc2626; }
    .btn-danger:hover { background:#b91c1c; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; padding:0 20px 30px; }
    .card { background:#1e293b; border-radius:12px; padding:20px; border:1px solid #334155; }
    .card.full { grid-column:1/-1; }
    .card h2 { font-size:14px; color:#94a3b8; margin-bottom:15px; display:flex; align-items:center; gap:8px; }
    table { width:100%; border-collapse:collapse; font-size:13px; }
    th { background:#0f172a; color:#64748b; padding:10px 12px; text-align:right; font-weight:600; }
    td { padding:10px 12px; border-bottom:1px solid #0f172a; }
    tr:last-child td { border-bottom:none; }
    tr:hover td { background:#1e3a5f18; }
    .badge { padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; display:inline-block; }
    .Confirmed  { background:#16a34a22; color:#22c55e; border:1px solid #22c55e44; }
    .Waiting    { background:#d9770622; color:#f97316; border:1px solid #f9731644; }
    .Canceled   { background:#dc262622; color:#f87171; border:1px solid #f8717144; }
    .Rescheduled{ background:#7c3aed22; color:#a78bfa; border:1px solid #a78bfa44; }
    .held       { background:#0369a122; color:#38bdf8; border:1px solid #38bdf844; }
    .log-entry { padding:9px 12px; border-bottom:1px solid #0f172a; font-size:12px; display:flex; gap:12px; }
    .log-entry:last-child { border-bottom:none; }
    .log-time { color:#6366f1; min-width:90px; font-weight:600; }
    .log-msg { color:#cbd5e1; }
    .log-box { max-height:300px; overflow-y:auto; }
    .empty { color:#475569; font-size:13px; padding:15px 0; text-align:center; }
    .counter { font-size:11px; color:#475569; margin-right:auto; }
    .mock-tag { background:#f59e0b22; color:#f59e0b; border:1px solid #f59e0b44; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; margin-right:10px; }
  </style>
</head>
<body>
<header>
  <div class="live-dot"></div>
  <div>
    <h1>🦷 Lustro CRM — لوحة التحكم</h1>
    <p>عيادات لوسترو — حي المروة، جدة | تتحدث تلقائياً كل 5 ثوانٍ</p>
  </div>
  <span class="mock-tag">⚠️ MOCK — يطابق CRM الحقيقي</span>
  <span class="badge-live" style="margin-right:auto">● LIVE</span>
</header>

<div class="stats" id="stats"></div>

<div class="toolbar">
  <button class="btn" onclick="load()">🔄 تحديث الآن</button>
  <button class="btn btn-danger" onclick="resetData()">🗑️ مسح البيانات</button>
  <span class="counter" id="last-update"></span>
</div>

<div class="grid">
  <div class="card full">
    <h2>📅 المواعيد</h2>
    <table>
      <thead><tr><th>رقم الموعد</th><th>المريض</th><th>الطبيب</th><th>التاريخ</th><th>الوقت</th><th>الحالة</th></tr></thead>
      <tbody id="appt-body"><tr><td colspan="6" class="empty">جاري التحميل...</td></tr></tbody>
    </table>
  </div>
  <div class="card">
    <h2>👤 المرضى المسجلون</h2>
    <table>
      <thead><tr><th>رقم الملف</th><th>الاسم</th><th>الجوال</th></tr></thead>
      <tbody id="pat-body"><tr><td colspan="3" class="empty">جاري التحميل...</td></tr></tbody>
    </table>
  </div>
  <div class="card">
    <h2>⚡ سجل النشاط المباشر</h2>
    <div class="log-box" id="log-body"><div class="empty">لا يوجد نشاط بعد</div></div>
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
    document.getElementById('stats').innerHTML =
      stat(pats.length, 'إجمالي المرضى') +
      stat(appts.filter(a => a.Status === 'Confirmed').length, 'مواعيد مؤكدة') +
      stat(appts.filter(a => a.Status === 'Canceled').length, 'مواعيد ملغاة') +
      stat(appts.filter(a => a.Status === 'Waiting').length, 'بانتظار التأكيد')
    document.getElementById('appt-body').innerHTML = appts.length
      ? appts.map(a => '<tr>' +
          '<td><strong>#' + a.AppointmentId + '</strong></td>' +
          '<td>' + (a.PatientName || '—') + '</td>' +
          '<td>' + (a.DoctorName || '—') + '</td>' +
          '<td>' + (a.AppointmentDate || '—') + '</td>' +
          '<td>' + (a.StartTime || '—') + ' → ' + (a.EndTime || '—') + '</td>' +
          '<td><span class="badge ' + a.Status + '">' + a.Status + '</span></td>' +
        '</tr>').join('')
      : '<tr><td colspan="6" class="empty">لا توجد مواعيد بعد</td></tr>'
    document.getElementById('pat-body').innerHTML = pats.length
      ? pats.map(p => '<tr>' +
          '<td>#' + p.FileNo + '</td>' +
          '<td>' + (p.ArabicName || p.EnglishName || '—') + '</td>' +
          '<td>' + (p.Mobile || '—') + '</td>' +
        '</tr>').join('')
      : '<tr><td colspan="3" class="empty">لا يوجد مرضى بعد</td></tr>'
    document.getElementById('log-body').innerHTML = logs.length
      ? logs.map(l => '<div class="log-entry"><span class="log-time">' + l.time + '</span><span class="log-msg">' + l.message + '</span></div>').join('')
      : '<div class="empty">لا يوجد نشاط بعد</div>'
    document.getElementById('notes-body').innerHTML = nts.length
      ? nts.map(n => '<tr><td>' + (n.patient_name || '#' + n.patient_id) + '</td><td>' + n.notes + '</td><td>' + n.time + '</td></tr>').join('')
      : '<tr><td colspan="3" class="empty">لا توجد ملاحظات بعد</td></tr>'
    document.getElementById('last-update').textContent = 'آخر تحديث: ' + new Date().toLocaleTimeString('ar-SA')
  } catch(e) { console.error('Load error:', e) }
}
function stat(num, label) {
  return '<div class="stat"><div class="stat-num">' + num + '</div><div class="stat-label">' + label + '</div></div>'
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
# INTERNAL DATA APIs (used by the dashboard only)
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

@app.route('/api/debug')
def api_debug():
    return jsonify(activity_log[:20])


# ═════════════════════════════════════════════════════════════
# DENTAK CRM API ENDPOINTS
# Responses match the REAL Dentak CRM exactly
# ═════════════════════════════════════════════════════════════


# ── 1. FIND PATIENT BY PHONE ─────────────────────────────────
# Real response: ARRAY of patient objects with PascalCase fields
@app.route('/MyCallAi/patients/search')
def search_patient():
    phone = request.args.get('phone', '')
    patient = find_patient_by_mobile(phone)
    if patient:
        log(f"🔍 تم إيجاد المريض: {patient['ArabicName']} ({phone})")
        return jsonify([patient])  # Real API returns ARRAY
    else:
        log(f"🔍 لم يتم إيجاد المريض بالرقم: {phone}")
        return jsonify([])  # Empty array when not found


# ── 2. GET PATIENT DETAILS ───────────────────────────────────
# Real response: single object with PascalCase fields
@app.route('/MyCallAi/patients/<pid>', methods=['GET'])
def get_patient(pid):
    patient = find_patient(pid)
    if patient:
        log(f"👤 تم جلب بيانات المريض #{pid}")
        return jsonify(patient)
    return jsonify({"message": "Not found"}), 404


# ── 3. CREATE NEW PATIENT ────────────────────────────────────
# Real request body: lowercase (arabicname, englishname, mobile, idcard, bithdate)
# Real response: {"Status": "SUCCESS", "id": "12316"}
@app.route('/MyCallAi/patients', methods=['POST'])
def create_patient():
    global next_patient_id
    data = request.get_json() or {}
    new_id = str(next_patient_id)
    next_patient_id += 1

    new_patient = {
        "FileNo": new_id,
        "ArabicName": data.get('arabicname', ''),
        "EnglishName": data.get('englishname', ''),
        "Mobile": data.get('mobile', ''),
        "IDCard": data.get('idcard', ''),
    }
    patients.append(new_patient)
    name = new_patient['ArabicName'] or new_patient['EnglishName'] or 'غير محدد'
    log(f"✅ تم تسجيل مريض جديد: {name} (ملف #{new_id})")
    return jsonify({"Status": "SUCCESS", "id": new_id})


# ── 4. UPDATE PATIENT BASIC DATA ─────────────────────────────
# Real response: "SUCCESS" (plain string)
@app.route('/MyCallAi/patients/<pid>', methods=['POST'])
def update_patient(pid):
    data = request.get_json() or {}
    patient = find_patient(pid)
    if patient:
        if 'arabicname' in data:  patient['ArabicName'] = data['arabicname']
        if 'englishname' in data: patient['EnglishName'] = data['englishname']
        if 'mobile' in data:      patient['Mobile'] = data['mobile']
        if 'idcard' in data:      patient['IDCard'] = data['idcard']
        log(f"✏️ تم تحديث بيانات المريض #{pid}")
    return make_response(json.dumps("SUCCESS"), 200, {'Content-Type': 'application/json'})


# ── 5. GET PATIENT INSURANCE DETAILS ─────────────────────────
# Real response: {patientId, count, data: [{InsuranceCompany, PolicyNumber, ...}]}
@app.route('/MyCallAi/patients/<pid>/insurance')
def patient_insurance(pid):
    log(f"🏥 تم جلب بيانات التأمين للمريض #{pid}")
    return jsonify({
        "patientId": int(pid),
        "count": 1,
        "data": [
            {
                "InsuranceCompany": "",
                "PolicyNumber": "46493329",
                "MemberId": "123456",
                "ClassName": "b+",
                "PatientDeductable": "20 %",
                "PatientDeductableMax": "0 S.R.",
                "StartDate": "2025/07/01",
                "EndDate": "2026/06/30"
            }
        ]
    })


# ── 6. CHECK INSURANCE ELIGIBILITY ───────────────────────────
# Real response: "Eligibile" (plain string, with their typo)
@app.route('/MyCallAi/patients/<pid>/insurance/eligibility')
def insurance_eligibility(pid):
    log(f"🏥 تم التحقق من أهلية التأمين للمريض #{pid}")
    return make_response(json.dumps("Eligibile"), 200, {'Content-Type': 'application/json'})


# ── 7. GET SPECIALTIES LIST ──────────────────────────────────
# Real response: {count, data: [{Id, NameArabic, NameEnglish}]}
@app.route('/MyCallAi/specialties')
def get_specialties():
    log("📋 تم جلب قائمة التخصصات")
    return jsonify({
        "count": len(specialties),
        "data": specialties
    })


# ── 8. GET DOCTORS BY SPECIALTY ──────────────────────────────
# Real response: {specialtyId, count, data: [{Id, Code, ArabicName, EnglishName, SpecialtyId, SpecialtyName}]}
@app.route('/MyCallAi/doctors')
def get_doctors():
    specialty_id = request.args.get('specialty_id')
    if specialty_id:
        result = [d for d in doctors if str(d['SpecialtyId']) == str(specialty_id)]
    else:
        result = doctors
    log(f"👨‍⚕️ تم جلب قائمة الأطباء (التخصص: {specialty_id or 'الكل'})")
    return jsonify({
        "specialtyId": int(specialty_id) if specialty_id else None,
        "count": len(result),
        "data": result
    })


# ── 9. GET DOCTOR SCHEDULE ───────────────────────────────────
# Real response: {doctorId, count, data: [{DoctorId, DayOfWeek, DayName, StartTime, EndTime, SlotMinutes}]}
@app.route('/MyCallAi/doctors/<int:did>/schedule')
def get_schedule(did):
    doctor = find_doctor(did)
    doc_schedule = schedules.get(did, [{"DoctorId": did, **s} for s in default_schedule])
    log(f"🗓️ تم جلب جدول الطبيب: {doctor['ArabicName'] if doctor else f'#{did}'}")
    return jsonify({
        "doctorId": did,
        "count": len(doc_schedule),
        "data": doc_schedule
    })


# ── 10. GET AVAILABLE SLOTS ──────────────────────────────────
# Real request: GET with body {app_dt_fmt: 20260311, doctorid: 108, day_id: 5}
# Real response: [{DocotorID, SlotDate, StartTime, EndTime}]  (NOTE: DocotorID typo is real)
@app.route('/MyCallAi/appointments/available', methods=['GET', 'POST'])
def get_available():
    data = request.get_json(silent=True) or {}
    app_dt_fmt = request.args.get('app_dt_fmt') or data.get('app_dt_fmt')
    doctorid = request.args.get('doctorid') or data.get('doctorid')
    day_id = request.args.get('day_id') or data.get('day_id')

    # Convert app_dt_fmt (20260311) to date format (2026/03/11)
    slot_date = "2026/03/15"  # default
    if app_dt_fmt:
        s = str(app_dt_fmt)
        if len(s) == 8:
            slot_date = f"{s[:4]}/{s[4:6]}/{s[6:]}"

    slots = generate_slots(doctorid or "0", slot_date)
    log(f"🕐 تم جلب المواعيد المتاحة | التاريخ: {slot_date} | الطبيب: {doctorid} | اليوم: {day_id}")
    return jsonify(slots)


# ── 11. HOLD APPOINTMENT SLOT ────────────────────────────────
# Real request: {patientid, doctorid, fromtime, endtime, appointmentdate}
# Real response: {"Status": "SUCCESS", "id": "48504"}
@app.route('/MyCallAi/appointments/hold', methods=['POST'])
def hold_appointment():
    global next_appointment_id
    data = request.get_json() or {}

    pid = data.get('patientid', '')
    did = data.get('doctorid', '')
    patient = find_patient(pid)
    doctor = find_doctor(did) if did else None

    new_id = next_appointment_id
    next_appointment_id += 1

    appt = {
        "AppointmentId": new_id,
        "PatientId": str(pid),
        "PatientName": patient['ArabicName'] if patient else 'غير محدد',
        "PatientMobile": patient['Mobile'] if patient else '',
        "DoctorId": int(did) if did else 0,
        "DoctorName": doctor['ArabicName'] if doctor else 'غير محدد',
        "AppointmentDate": data.get('appointmentdate', ''),
        "StartTime": data.get('fromtime', ''),
        "EndTime": data.get('endtime', ''),
        "Status": "Waiting"
    }
    appointments.append(appt)
    log(f"⏳ تم حجز موعد مؤقت لـ {appt['PatientName']} مع {appt['DoctorName']}")
    return jsonify({"Status": "SUCCESS", "id": str(new_id)})


# ── 12. CONFIRM APPOINTMENT ──────────────────────────────────
# Real response: "Appointment is Confirmed" (plain string)
@app.route('/MyCallAi/appointments/<int:aid>/confirm', methods=['POST'])
def confirm_appointment(aid):
    global appointments
    appt = find_appointment(aid)
    appointments = [dict(a, Status='Confirmed') if a['AppointmentId'] == aid else a for a in appointments]
    name = appt['PatientName'] if appt else f"#{aid}"
    log(f"✅ تم تأكيد الموعد لـ {name}")
    return make_response(json.dumps("Appointment is Confirmed"), 200, {'Content-Type': 'application/json'})


# ── 13. BOOK APPOINTMENT (DIRECT) ────────────────────────────
# Real response: {"Status": "SUCCESS", "id": "48504"}
@app.route('/MyCallAi/appointments', methods=['POST'])
def create_appointment():
    global next_appointment_id
    data = request.get_json() or {}

    pid = data.get('patientid', '')
    did = data.get('doctorid', '')
    patient = find_patient(pid)
    doctor = find_doctor(did) if did else None

    new_id = next_appointment_id
    next_appointment_id += 1

    appt = {
        "AppointmentId": new_id,
        "PatientId": str(pid),
        "PatientName": patient['ArabicName'] if patient else 'غير محدد',
        "PatientMobile": patient['Mobile'] if patient else '',
        "DoctorId": int(did) if did else 0,
        "DoctorName": doctor['ArabicName'] if doctor else 'غير محدد',
        "AppointmentDate": data.get('appointmentdate', ''),
        "StartTime": data.get('fromtime', ''),
        "EndTime": data.get('endtime', ''),
        "Status": "Waiting"
    }
    appointments.append(appt)
    log(f"📌 تم حجز موعد لـ {appt['PatientName']} مع {appt['DoctorName']}")
    return jsonify({"Status": "SUCCESS", "id": str(new_id)})


# ── 14. RESCHEDULE APPOINTMENT ───────────────────────────────
# Real response: "Appointment is Rescheduled" (plain string, no body needed)
@app.route('/MyCallAi/appointments/<int:aid>/reschedule', methods=['POST'])
def reschedule_appointment(aid):
    global appointments
    appt = find_appointment(aid)
    appointments = [dict(a, Status='Rescheduled') if a['AppointmentId'] == aid else a for a in appointments]
    name = appt['PatientName'] if appt else f"#{aid}"
    log(f"🔄 تم تعديل الموعد لـ {name}")
    return make_response(json.dumps("Appointment is Rescheduled"), 200, {'Content-Type': 'application/json'})


# ── 15. CANCEL APPOINTMENT ───────────────────────────────────
# Real response: "Appointment is Canceled" (plain string, no body needed)
@app.route('/MyCallAi/appointments/<int:aid>/cancel', methods=['POST'])
def cancel_appointment(aid):
    global appointments
    appt = find_appointment(aid)
    appointments = [dict(a, Status='Canceled') if a['AppointmentId'] == aid else a for a in appointments]
    name = appt['PatientName'] if appt else f"#{aid}"
    log(f"❌ تم إلغاء الموعد لـ {name}")
    return make_response(json.dumps("Appointment is Canceled"), 200, {'Content-Type': 'application/json'})


# ── 16. GET APPOINTMENT DETAILS ──────────────────────────────
# Real response: {AppointmentId, PatientId, PatientName, PatientMobile, DoctorId, DoctorName, AppointmentDate, StartTime, EndTime, Status}
@app.route('/MyCallAi/appointments/<int:aid>', methods=['GET'])
def get_appointment(aid):
    appt = find_appointment(aid)
    if appt:
        log(f"📋 تم جلب تفاصيل الموعد #{aid}")
        return jsonify(appt)
    return jsonify({"message": "Not found"}), 404


# ── 17. ADD PATIENT NOTE / CALL SUMMARY ──────────────────────
# Real response: "SUCCESS" (plain string)
@app.route('/MyCallAi/patients/<pid>/notes', methods=['POST'])
def add_note(pid):
    data = request.get_json() or {}
    patient = find_patient(pid)
    note = {
        "patient_id": pid,
        "patient_name": patient['ArabicName'] if patient else f"#{pid}",
        "notes": data.get('notes', ''),
        "time": datetime.now().strftime("%I:%M %p")
    }
    notes.insert(0, note)
    log(f"📝 تم حفظ ملاحظة للمريض #{pid}")
    return make_response(json.dumps("SUCCESS"), 200, {'Content-Type': 'application/json'})


# ── DATE HELPER (for agent to get correct date) ──────────────
@app.route('/MyCallAi/today')
def get_today():
    from datetime import date, timedelta
    today = date.today()
    days_ar = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    return jsonify({
        "today": today.strftime("%Y/%m/%d"),
        "tomorrow": (today + timedelta(days=1)).strftime("%Y/%m/%d"),
        "day_after": (today + timedelta(days=2)).strftime("%Y/%m/%d"),
        "today_day_name": days_ar[today.isoweekday() % 7],
        "today_day_id": today.isoweekday() % 7 + 1
    })


# ── MESSAGING ENDPOINTS (still mock — not in real CRM yet) ───
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

@app.route('/MyCallAi/patients/<pid>/consent', methods=['GET'])
def get_consent(pid):
    log(f"✅ تم التحقق من موافقة المريض #{pid}")
    return jsonify({"patient_id": pid, "whatsapp_consent": True})

@app.route('/MyCallAi/patients/<pid>/consent', methods=['POST'])
def save_consent(pid):
    log(f"✅ تم حفظ موافقة المريض #{pid}")
    return jsonify({"status": "saved"})


# ─────────────────────────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
