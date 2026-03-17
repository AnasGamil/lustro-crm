from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────────
# IN-MEMORY DATABASE — Matches REAL Dentak CRM structure exactly
# ─────────────────────────────────────────────────────────────

patients = [
    {"FileNo": "11763", "ArabicName": "أحمد محمد السالم",        "EnglishName": "Ahmed Mohamed AlSalem",    "Mobile": "0538892874", "IDCard": "1098765432"},
    {"FileNo": "7855",  "ArabicName": "فاطمة عبدالله الزهراني",  "EnglishName": "Fatima Abdullah AlZahrani", "Mobile": "0501234567", "IDCard": "2087654321"},
    {"FileNo": "9240",  "ArabicName": "محمد علي الغامدي",        "EnglishName": "Mohammed Ali AlGhamdi",     "Mobile": "0556789012", "IDCard": "1076543210"},
    {"FileNo": "12316", "ArabicName": "أنس محمد احمد",           "EnglishName": "Anas Mohamed Ahmed",        "Mobile": "0512345678", "IDCard": "2134567892"},
]

specialties = [
    {"Id": 1,  "NameArabic": "الطب النفسي",                        "NameEnglish": "Psychiatry"},
    {"Id": 2,  "NameArabic": "انف أذن وحنجرة",                     "NameEnglish": "Ear, Nose and Throat"},
    {"Id": 3,  "NameArabic": "أمراض القلب والأوعية الدموية",        "NameEnglish": "Cardiology and Vascular Disease"},
    {"Id": 4,  "NameArabic": "السمعيات",                            "NameEnglish": "Audiology"},
    {"Id": 5,  "NameArabic": "جراحة عامة",                          "NameEnglish": "General Surgery"},
    {"Id": 6,  "NameArabic": "الباطنة",                             "NameEnglish": "Internal Medicine"},
    {"Id": 7,  "NameArabic": "العيون",                              "NameEnglish": "Ophtalmology"},
    {"Id": 8,  "NameArabic": "مسالك بولية",                         "NameEnglish": "Urologist"},
    {"Id": 9,  "NameArabic": "الجلدية والتجميل",                    "NameEnglish": "Dermatology and cosmetology"},
    {"Id": 10, "NameArabic": "الأسنان والتقويم",                    "NameEnglish": "Dental and Orthodontics"},
    {"Id": 12, "NameArabic": "أطفال وحديثي الولادة",                "NameEnglish": "Children and newborns"},
    {"Id": 13, "NameArabic": "مخ وأعصاب",                           "NameEnglish": "Neurologists"},
    {"Id": 14, "NameArabic": "عظام",                                "NameEnglish": "Bones"},
    {"Id": 15, "NameArabic": "نساء وتوليد",                         "NameEnglish": "Obstetrics and Gynecology"},
    {"Id": 16, "NameArabic": "جراحة وتجميل",                        "NameEnglish": "Plastic Surgery"},
    {"Id": 17, "NameArabic": "أورام",                               "NameEnglish": "Tumors"},
    {"Id": 18, "NameArabic": "تخسيس وتغذية",                        "NameEnglish": "Slimming and Nutrition"},
    {"Id": 19, "NameArabic": "صدر وجهاز تنفسي",                    "NameEnglish": "Chest and respiratory system"},
    {"Id": 20, "NameArabic": "سكر وغدد صماء",                       "NameEnglish": "Sugar and endocrine glands"},
    {"Id": 21, "NameArabic": "أشعة",                                "NameEnglish": "XRay"},
    {"Id": 22, "NameArabic": "مختبر",                               "NameEnglish": "Laboratory"},
]

doctors = [
    {"Id": 5,  "Code": "1", "ArabicName": "د. عبدالرحمن قنوت",     "EnglishName": "Dr. Abdulrahman Kannout",  "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 6,  "Code": "2", "ArabicName": "د. نعمت العاقل",         "EnglishName": "Dr. Nimat",                "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 7,  "Code": "3", "ArabicName": "د. هنادي الحارثي",       "EnglishName": "Dr. Hanadi Alharthi",      "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 8,  "Code": "4", "ArabicName": "د. مصطفى الحبال",        "EnglishName": "Dr. Moustafa ALhabbal",    "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 9,  "Code": "5", "ArabicName": "د. ولاء عبداللطيف",      "EnglishName": "Dr. Walaa Abdlatif",       "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 10, "Code": "6", "ArabicName": "د. عبدالعزيز البارقي",   "EnglishName": "Dr. Abdelaziz Al barqi",   "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 76, "Code": "7", "ArabicName": "Dr. Ebtesam",             "EnglishName": "Dr. Ebtesam",              "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 77, "Code": "8", "ArabicName": "Dr. Ahmed ElSayed",       "EnglishName": "Dr. Ahmed ElSayed",        "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 78, "Code": "9", "ArabicName": "د. ماهر كشكول",           "EnglishName": "Dr. Maher Kashkoul",       "SpecialtyId": 10, "SpecialtyName": "الأسنان والتقويم"},
    {"Id": 20, "Code": "20", "ArabicName": "د. سارة الشمري",         "EnglishName": "Dr. Sara AlShammari",      "SpecialtyId": 9,  "SpecialtyName": "الجلدية والتجميل"},
    {"Id": 21, "Code": "21", "ArabicName": "د. خالد العتيبي",         "EnglishName": "Dr. Khaled AlOtaibi",      "SpecialtyId": 9,  "SpecialtyName": "الجلدية والتجميل"},
    {"Id": 30, "Code": "30", "ArabicName": "د. ريم الدوسري",          "EnglishName": "Dr. Reem AlDossari",       "SpecialtyId": 15, "SpecialtyName": "نساء وتوليد"},
    {"Id": 31, "Code": "31", "ArabicName": "د. منى الزهراني",         "EnglishName": "Dr. Mona AlZahrani",       "SpecialtyId": 15, "SpecialtyName": "نساء وتوليد"},
    {"Id": 40, "Code": "40", "ArabicName": "د. فيصل الغامدي",         "EnglishName": "Dr. Faisal AlGhamdi",      "SpecialtyId": 14, "SpecialtyName": "عظام"},
    {"Id": 50, "Code": "50", "ArabicName": "د. نايف المطيري",          "EnglishName": "Dr. Nayef AlMutairi",      "SpecialtyId": 12, "SpecialtyName": "أطفال وحديثي الولادة"},
    {"Id": 51, "Code": "51", "ArabicName": "د. لمياء القحطاني",        "EnglishName": "Dr. Lamia AlQahtani",      "SpecialtyId": 12, "SpecialtyName": "أطفال وحديثي الولادة"},
    {"Id": 60, "Code": "60", "ArabicName": "د. عمر السبيعي",           "EnglishName": "Dr. Omar AlSubaie",        "SpecialtyId": 3,  "SpecialtyName": "أمراض القلب والأوعية الدموية"},
    {"Id": 70, "Code": "70", "ArabicName": "د. أحمد الحربي",           "EnglishName": "Dr. Ahmad AlHarbi",        "SpecialtyId": 6,  "SpecialtyName": "الباطنة"},
    {"Id": 80, "Code": "80", "ArabicName": "د. هند العمري",             "EnglishName": "Dr. Hind AlOmari",         "SpecialtyId": 18, "SpecialtyName": "تخسيس وتغذية"},
]

doctor_schedules = {
    5: [
        {"DoctorId": 5, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
        {"DoctorId": 5, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
    ],
    6: [
        {"DoctorId": 6, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 6, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
        {"DoctorId": 6, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 6, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 6, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
    ],
    7: [
        {"DoctorId": 7, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 7, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 7, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 7, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
        {"DoctorId": 7, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
    ],
    8: [
        {"DoctorId": 8, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "11:00 am", "EndTime": "11:00 am", "SlotMinutes": 15},
        {"DoctorId": 8, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "11:00 am", "EndTime": "11:00 am", "SlotMinutes": 15},
        {"DoctorId": 8, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
        {"DoctorId": 8, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "11:00 am", "EndTime": "11:00 am", "SlotMinutes": 15},
        {"DoctorId": 8, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "11:00 am", "EndTime": "11:00 am", "SlotMinutes": 15},
    ],
    9: [
        {"DoctorId": 9, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 9, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "04:00 pm", "EndTime": "04:00 pm", "SlotMinutes": 15},
        {"DoctorId": 9, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 9, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 9, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "04:00 pm", "EndTime": "04:00 pm", "SlotMinutes": 15},
    ],
    10: [
        {"DoctorId": 10, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 10, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
        {"DoctorId": 10, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 10, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 10, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "06:00 pm", "EndTime": "06:00 pm", "SlotMinutes": 15},
    ],
    76: [
        {"DoctorId": 76, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 76, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 76, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
    ],
    77: [
        {"DoctorId": 77, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 77, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 77, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
        {"DoctorId": 77, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
    78: [
        {"DoctorId": 78, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 78, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
        {"DoctorId": 78, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 78, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 78, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
    ],
    20: [
        {"DoctorId": 20, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 20, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 20, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "02:00 pm", "EndTime": "02:00 pm", "SlotMinutes": 15},
    ],
    21: [
        {"DoctorId": 21, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 21, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 21, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
    30: [
        {"DoctorId": 30, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 30, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 30, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
    31: [
        {"DoctorId": 31, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 31, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 31, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
    ],
    40: [
        {"DoctorId": 40, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 40, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 40, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
    50: [
        {"DoctorId": 50, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 50, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "05:00 pm", "EndTime": "05:00 pm", "SlotMinutes": 15},
        {"DoctorId": 50, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 50, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 50, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
    51: [
        {"DoctorId": 51, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 51, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 51, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
    ],
    60: [
        {"DoctorId": 60, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 60, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 60, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
    70: [
        {"DoctorId": 70, "DayOfWeek": 1, "DayName": "Saturday",  "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 70, "DayOfWeek": 3, "DayName": "Monday",    "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
        {"DoctorId": 70, "DayOfWeek": 5, "DayName": "Wednesday", "StartTime": "09:00 am", "EndTime": "09:00 am", "SlotMinutes": 15},
    ],
    80: [
        {"DoctorId": 80, "DayOfWeek": 2, "DayName": "Sunday",    "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 80, "DayOfWeek": 4, "DayName": "Tuesday",   "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
        {"DoctorId": 80, "DayOfWeek": 6, "DayName": "Thursday",  "StartTime": "10:00 am", "EndTime": "10:00 am", "SlotMinutes": 15},
    ],
}

insurance_data = {
    "11763": [{"InsuranceCompany": "Allianz Care", "PolicyNumber": "ALZ-2024-9987", "MemberId": "ALZ11763", "ClassName": "Class A", "PatientDeductable": "10%", "PatientDeductableMax": "500",  "StartDate": "01/01/2026", "EndDate": "31/12/2026"}],
    "7855":  [{"InsuranceCompany": "Tawuniya",     "PolicyNumber": "TWN-2025-4421", "MemberId": "TWN7855",  "ClassName": "Class B", "PatientDeductable": "20%", "PatientDeductableMax": "1000", "StartDate": "01/03/2026", "EndDate": "28/02/2027"}],
    "9240":  [{"InsuranceCompany": "Bupa Arabia",  "PolicyNumber": "BUP-2024-7710", "MemberId": "BUP9240",  "ClassName": "VIP",     "PatientDeductable": "0%",  "PatientDeductableMax": "0",    "StartDate": "15/06/2025", "EndDate": "14/06/2026"}],
    "12316": []
}

appointments = [
    {
        "_internal_id": 46577,
        "AppointmentId": 46577,
        "PatientId": "11763",
        "PatientName": "أحمد محمد السالم",
        "PatientMobile": "0538892874",
        "DoctorId": 5,
        "DoctorName": "د. عبدالرحمن قنوت",
        "AppointmentDate": "2026/03/10",
        "StartTime": "10:00 am",
        "EndTime": "10:00 am",
        "Status": "Confirmed"
    }
]

notes = []
activity_log = []


def log(message):
    entry = {"time": datetime.now().strftime("%I:%M:%S %p"), "message": message}
    activity_log.insert(0, entry)
    if len(activity_log) > 100:
        activity_log.pop()


def find_patient_by_fileno(fileno):
    return next((p for p in patients if str(p["FileNo"]) == str(fileno)), None)


def find_patient_by_mobile(mobile):
    return next((p for p in patients if p["Mobile"] == mobile), None)


def find_doctor(did):
    return next((d for d in doctors if d["Id"] == int(did)), None)


def generate_slots(doctor_id, date_str, schedule_entries):
    """
    Generate slots matching real CRM format: [{DocotorID, SlotDate, StartTime, EndTime}]
    StartTime = EndTime (both = slot start time — real CRM quirk)
    15-minute intervals for 2 hours from each session start
    """
    from datetime import datetime as dt, timedelta as td
    all_slots = []
    booked_times = set()
    for a in appointments:
        if str(a.get("DoctorId")) == str(doctor_id) and a.get("AppointmentDate") == date_str:
            if a.get("Status") not in ["Cancelled", "Rescheduled"]:
                booked_times.add(a.get("StartTime", "").lower().strip())
    for entry in schedule_entries:
        session_start_str = entry.get("StartTime", "")
        slot_minutes = entry.get("SlotMinutes", 15)
        try:
            session_start = dt.strptime(session_start_str.strip(), "%I:%M %p")
        except ValueError:
            continue
        session_end = session_start + td(hours=2)
        current = session_start
        while current < session_end:
            time_str_padded = current.strftime("%I:%M %p").lower()
            if time_str_padded not in booked_times:
                all_slots.append({
                    "DocotorID": str(doctor_id),
                    "SlotDate":  date_str,
                    "StartTime": time_str_padded,
                    "EndTime":   time_str_padded
                })
            current += td(minutes=slot_minutes)
    return all_slots


# ─────────────────────────────────────────────────────────────
# DASHBOARD HTML
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
    header { background:linear-gradient(135deg,#1e293b,#0f172a); padding:18px 30px; border-bottom:2px solid #6366f1; display:flex; align-items:center; gap:14px; }
    header h1 { font-size:20px; color:#a5b4fc; }
    header p  { font-size:12px; color:#64748b; margin-top:2px; }
    .live-dot { width:10px; height:10px; background:#22c55e; border-radius:50%; animation:pulse 1.5s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .badge-live { background:#22c55e22; color:#22c55e; border:1px solid #22c55e44; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
    .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:15px; padding:20px; }
    .stat { background:#1e293b; border-radius:12px; padding:18px 22px; border:1px solid #334155; }
    .stat-num { font-size:30px; font-weight:700; color:#6366f1; }
    .stat-label { font-size:12px; color:#64748b; margin-top:4px; }
    .toolbar { padding:0 20px 15px; display:flex; align-items:center; gap:10px; }
    .btn { background:#6366f1; color:white; border:none; padding:8px 20px; border-radius:8px; cursor:pointer; font-size:13px; }
    .btn-danger { background:#dc2626; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; padding:0 20px 30px; }
    .card { background:#1e293b; border-radius:12px; padding:20px; border:1px solid #334155; }
    .card.full { grid-column:1/-1; }
    .card h2 { font-size:14px; color:#94a3b8; margin-bottom:15px; }
    table { width:100%; border-collapse:collapse; font-size:13px; }
    th { background:#0f172a; color:#64748b; padding:10px 12px; text-align:right; font-weight:600; }
    td { padding:10px 12px; border-bottom:1px solid #0f172a; }
    tr:last-child td { border-bottom:none; }
    .badge { padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; display:inline-block; }
    .Confirmed,.confirmed { background:#16a34a22; color:#22c55e; border:1px solid #22c55e44; }
    .Held,.held { background:#d9770622; color:#f97316; border:1px solid #f9731644; }
    .Cancelled,.cancelled,.Canceled { background:#dc262622; color:#f87171; border:1px solid #f8717144; }
    .Rescheduled,.rescheduled { background:#7c3aed22; color:#a78bfa; border:1px solid #a78bfa44; }
    .Waiting,.waiting { background:#0369a122; color:#38bdf8; border:1px solid #38bdf844; }
    .log-entry { padding:9px 12px; border-bottom:1px solid #0f172a; font-size:12px; display:flex; gap:12px; }
    .log-time { color:#6366f1; min-width:90px; font-weight:600; }
    .log-msg { color:#cbd5e1; }
    .log-box { max-height:300px; overflow-y:auto; }
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
  <button class="btn btn-danger" onclick="resetData()">🗑️ مسح المواعيد والملاحظات</button>
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
      <thead><tr><th>FileNo</th><th>الاسم</th><th>الجوال</th><th>التأمين</th></tr></thead>
      <tbody id="pat-body"><tr><td colspan="4" class="empty">جاري التحميل...</td></tr></tbody>
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
      stat(appts.filter(a => (a.Status||'').toLowerCase() === 'confirmed').length, 'مواعيد مؤكدة') +
      stat(appts.filter(a => ['cancelled','canceled'].includes((a.Status||'').toLowerCase())).length, 'مواعيد ملغاة') +
      stat(appts.filter(a => (a.Status||'').toLowerCase() === 'held').length, 'محجوزة مؤقتاً')
    document.getElementById('appt-body').innerHTML = appts.length
      ? appts.map(a => `<tr>
          <td><strong>#${a.AppointmentId}</strong></td>
          <td>${a.PatientName||'—'}</td><td>${a.DoctorName||'—'}</td>
          <td>${a.AppointmentDate||'—'}</td>
          <td>${a.StartTime||'—'} → ${a.EndTime||'—'}</td>
          <td><span class="badge ${a.Status}">${a.Status}</span></td>
        </tr>`).join('')
      : '<tr><td colspan="6" class="empty">لا توجد مواعيد بعد</td></tr>'
    document.getElementById('pat-body').innerHTML = pats.length
      ? pats.map(p => `<tr>
          <td>#${p.FileNo}</td>
          <td>${p.ArabicName||p.EnglishName||'—'}</td>
          <td>${p.Mobile||'—'}</td>
          <td>${p._hasInsurance ? '✅' : '—'}</td>
        </tr>`).join('')
      : '<tr><td colspan="4" class="empty">لا يوجد مرضى</td></tr>'
    document.getElementById('log-body').innerHTML = logs.length
      ? logs.map(l => `<div class="log-entry"><span class="log-time">${l.time}</span><span class="log-msg">${l.message}</span></div>`).join('')
      : '<div class="empty">لا يوجد نشاط بعد</div>'
    document.getElementById('notes-body').innerHTML = nts.length
      ? nts.map(n => `<tr><td>${n.patient_name||'#'+n.patient_id}</td><td>${n.notes}</td><td>${n.time}</td></tr>`).join('')
      : '<tr><td colspan="3" class="empty">لا توجد ملاحظات بعد</td></tr>'
    document.getElementById('last-update').textContent = 'آخر تحديث: ' + new Date().toLocaleTimeString('ar-SA')
  } catch(e) { console.error(e) }
}
function stat(num, label) {
  return `<div class="stat"><div class="stat-num">${num}</div><div class="stat-label">${label}</div></div>`
}
async function resetData() {
  if (!confirm('مسح المواعيد والملاحظات؟')) return
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
# DASHBOARD & INTERNAL APIS
# ─────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/appointments')
def api_appointments():
    return jsonify(appointments)

@app.route('/api/patients')
def api_patients():
    result = []
    for p in patients:
        row = dict(p)
        row['_hasInsurance'] = len(insurance_data.get(str(p['FileNo']), [])) > 0
        result.append(row)
    return jsonify(result)

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
    log('🔄 تم مسح المواعيد والملاحظات')
    return jsonify({"status": "reset"})


# ─────────────────────────────────────────────────────────────
# PATIENT ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.route('/MyCallAi/patients/search')
def search_patient():
    """
    find_patient_by_phone — returns ARRAY. Empty array = not found.
    """
    phone = request.args.get('phone', '').strip()
    patient = find_patient_by_mobile(phone)
    if patient:
        log(f"🔍 تم إيجاد المريض: {patient.get('ArabicName')} ({phone})")
        return jsonify([patient])
    log(f"🔍 لم يتم إيجاد المريض بالرقم: {phone}")
    return jsonify([])


@app.route('/MyCallAi/patients/searchbyname')
def search_patient_by_name():
    """
    find_patient_by_name — URL: /patients/searchbyname?name=...
    Real CRM: returns ARRAY same fields as find_patient_by_phone.
    Partial name search supported.
    """
    name = request.args.get('name', '').strip()
    results = []
    for p in patients:
        arabic = p.get('ArabicName', '')
        english = p.get('EnglishName', '')
        if name and (name in arabic or name in english or
                     name.lower() in arabic.lower() or name.lower() in english.lower()):
            results.append(p)
    log(f"🔍 بحث بالاسم: '{name}' — نتائج: {len(results)}")
    return jsonify(results)


@app.route('/MyCallAi/patients/<pid>')
def get_patient(pid):
    patient = find_patient_by_fileno(pid)
    if patient:
        return jsonify(patient)
    return jsonify({"message": "Patient not found"}), 404


@app.route('/MyCallAi/patients/<pid>', methods=['POST'])
def update_patient(pid):
    """Update patient data. Maps lowercase keys to PascalCase stored keys."""
    global patients
    data = request.get_json() or {}
    field_map = {
        'arabicname':  'ArabicName',
        'englishname': 'EnglishName',
        'mobile':      'Mobile',
        'idcard':      'IDCard',
        'bithdate':    'BirthDate',
        'gender':      'Gender'
    }
    mapped_data = {field_map.get(k.lower(), k): v for k, v in data.items()}
    found = False
    for i, p in enumerate(patients):
        if str(p['FileNo']) == str(pid):
            patients[i] = {**p, **mapped_data}
            found = True
            break
    if found:
        log(f"✏️ تم تحديث بيانات المريض #{pid}")
        return "SUCCESS", 200, {'Content-Type': 'text/plain'}
    return jsonify({"message": "Patient not found"}), 404


@app.route('/MyCallAi/patients', methods=['POST'])
def create_patient():
    """
    Real CRM returns: {"Status": "SUCCESS", "id": "12316"}
    """
    data = request.get_json() or {}
    new_id = str(int(datetime.now().timestamp()))[-5:]
    new_patient = {
        "FileNo":      new_id,
        "ArabicName":  data.get('arabicname', ''),
        "EnglishName": data.get('englishname', ''),
        "Mobile":      data.get('mobile', ''),
        "IDCard":      data.get('idcard', ''),
        "BirthDate":   data.get('bithdate', ''),
        "Gender":      data.get('gender', ''),
        "Status":      "Active"
    }
    patients.append(new_patient)
    name = new_patient.get('ArabicName') or new_patient.get('EnglishName') or 'غير محدد'
    log(f"✅ تم تسجيل مريض جديد: {name} (FileNo: {new_id})")
    return jsonify({"Status": "SUCCESS", "id": new_id})


@app.route('/MyCallAi/patients/<pid>/insurance')
def patient_insurance(pid):
    data = insurance_data.get(str(pid), [])
    log(f"🏥 تم جلب بيانات التأمين للمريض #{pid}")
    return jsonify({"patientId": str(pid), "count": len(data), "data": data})


@app.route('/MyCallAi/patients/<pid>/insurance/eligibility')
def insurance_eligibility(pid):
    """Real CRM returns plain text 'Eligibile' (their typo)."""
    has_insurance = len(insurance_data.get(str(pid), [])) > 0
    log(f"🏥 تم التحقق من أهلية التأمين للمريض #{pid}")
    if has_insurance:
        return "Eligibile", 200, {'Content-Type': 'text/plain'}
    return "Not Eligible", 200, {'Content-Type': 'text/plain'}


@app.route('/MyCallAi/patients/checkinsurance', methods=['GET'])
def check_insurance_nphies():
    """
    Nphies insurance check.
    Input body: {"id_card": "2566891509", "tp": "1"}
    Real CRM returns complex object. Agent only needs:
      - elegibility.elgibile  ("eligible" = valid)
      - insurance.Insurance[0].InsuranceCompanyAR (Arabic insurance company name)
    Note: "elegibility" and "elgibile" are the real CRM's intentional typos.
    """
    data = request.get_json(silent=True) or {}
    id_card = data.get('id_card', '')
    # Find patient by IDCard
    patient = next((p for p in patients if p.get('IDCard') == id_card), None)
    has_insurance = False
    insurance_company_ar = ''
    insurance_company_en = ''
    expiry_date = ''
    if patient:
        pid = patient['FileNo']
        ins_list = insurance_data.get(str(pid), [])
        if ins_list:
            has_insurance = True
            insurance_company_ar = ins_list[0].get('InsuranceCompany', '') + ' للتأمين'
            insurance_company_en = ins_list[0].get('InsuranceCompany', '')
            expiry_date = ins_list[0].get('EndDate', '2027-12-31')
    log(f"🏥 Nphies فحص تأمين بالهوية: {id_card} — نتيجة: {'مؤهل' if has_insurance else 'غير مؤهل'}")
    # Return in real CRM format — only the fields the agent needs
    return jsonify({
        "elegibility": {
            "elgibile": "eligible" if has_insurance else "not eligible",
            "outcomeoperation": "Complete",
            "inforce": "True" if has_insurance else "False",
            "disposition": "Coverage is in-force" if has_insurance else "Coverage not found"
        },
        "insurance": {
            "ApiStatus": "Success",
            "Insurance": [
                {
                    "InsuranceCompanyAR": insurance_company_ar,
                    "InsuranceCompanyEN": insurance_company_en,
                    "ExpiryDate": expiry_date,
                    "DeductibleRate": "20"
                }
            ] if has_insurance else []
        }
    })


@app.route('/MyCallAi/patients/<pid>/appointments')
def get_patient_appointments(pid):
    """
    Returns all appointments for a patient by FileNo.
    Real CRM returns: direct ARRAY (NOT wrapped in count/data).
    AppointmentId is integer. Status values: Confirmed, Rescheduled, Waiting, Canceled.
    """
    result = []
    for a in appointments:
        if str(a.get('PatientId')) == str(pid):
            result.append({
                "AppointmentId":   int(a.get('_internal_id', a.get('AppointmentId', 0))),
                "PatientId":       str(a.get('PatientId', '')),
                "PatientName":     a.get('PatientName', ''),
                "PatientMobile":   a.get('PatientMobile', ''),
                "DoctorId":        int(a.get('DoctorId', 0)),
                "DoctorName":      a.get('DoctorName', ''),
                "AppointmentDate": a.get('AppointmentDate', ''),
                "StartTime":       a.get('StartTime', ''),
                "EndTime":         a.get('EndTime', ''),
                "Status":          a.get('Status', '')
            })
    log(f"📋 مواعيد المريض #{pid} — عدد: {len(result)}")
    return jsonify(result)  # ← direct ARRAY, real CRM format


@app.route('/MyCallAi/patients/<pid>/notes', methods=['POST'])
def add_note(pid):
    data = request.get_json() or {}
    patient = find_patient_by_fileno(pid)
    note = {
        "patient_id":   pid,
        "patient_name": patient.get('ArabicName') or patient.get('EnglishName') if patient else f"#{pid}",
        "notes":        data.get('notes', ''),
        "time":         datetime.now().strftime("%I:%M %p")
    }
    notes.insert(0, note)
    log(f"📝 تم حفظ ملاحظة للمريض #{pid}")
    return "SUCCESS", 200, {'Content-Type': 'text/plain'}


# ─────────────────────────────────────────────────────────────
# SPECIALTIES & DOCTORS
# ─────────────────────────────────────────────────────────────

@app.route('/MyCallAi/specialties')
def get_specialties():
    log("📋 تم جلب قائمة التخصصات")
    return jsonify({"count": len(specialties), "data": specialties})


@app.route('/MyCallAi/doctors')
def get_doctors():
    specialty_id = request.args.get('specialty_id')
    if specialty_id:
        result = [d for d in doctors if str(d['SpecialtyId']) == str(specialty_id)]
    else:
        result = doctors
    log(f"👨‍⚕️ تم جلب الأطباء (تخصص: {specialty_id or 'الكل'})")
    return jsonify({"specialtyId": specialty_id or "all", "count": len(result), "data": result})


@app.route('/MyCallAi/doctors/<int:did>/schedule')
def get_schedule(did):
    doctor = find_doctor(did)
    schedule = doctor_schedules.get(did, [])
    log(f"🗓️ جدول: {doctor['ArabicName'] if doctor else f'#{did}'} — {len(schedule)} جلسة")
    return jsonify({"doctorId": did, "count": len(schedule), "data": schedule})


# ─────────────────────────────────────────────────────────────
# APPOINTMENT ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.route('/MyCallAi/appointments/available', methods=['GET', 'POST'])
def get_available():
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()
        data.update(request.get_json(silent=True) or {})
    doctor_id = data.get('doctorid') or data.get('doctor_id')
    date_fmt  = data.get('app_dt_fmt')
    day_id    = data.get('day_id')
    date_str  = None
    if date_fmt:
        ds = str(date_fmt)
        if len(ds) == 8:
            date_str = f"{ds[0:4]}/{ds[4:6]}/{ds[6:8]}"
    slots = []
    if doctor_id and day_id:
        sched = doctor_schedules.get(int(doctor_id), [])
        day_entries = [e for e in sched if str(e.get('DayOfWeek')) == str(day_id)]
        if day_entries:
            slots = generate_slots(doctor_id, date_str, day_entries)
    log(f"🕐 مواعيد متاحة — طبيب {doctor_id}, يوم {day_id} → {len(slots)} موعد")
    return jsonify(slots)


@app.route('/MyCallAi/appointments/reminder')
def appointments_reminder():
    """
    Upcoming 24-hour appointments for outbound agent.
    URL: /appointments/reminder
    Real CRM returns: direct ARRAY.
    Fields include PatientMobile (critical for outbound calling).
    Status values seen: Waiting, Confirmed, Canceled, Rescheduled.
    """
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")
    today = datetime.now().strftime("%Y/%m/%d")
    upcoming = []
    for a in appointments:
        appt_date = a.get('AppointmentDate', '')
        if appt_date in [today, tomorrow]:
            upcoming.append({
                "AppointmentId":   int(a.get('_internal_id', a.get('AppointmentId', 0))),
                "PatientId":       str(a.get('PatientId', '')),
                "PatientName":     a.get('PatientName', ''),
                "PatientMobile":   a.get('PatientMobile', ''),
                "DoctorId":        int(a.get('DoctorId', 0)),
                "DoctorName":      a.get('DoctorName', ''),
                "AppointmentDate": a.get('AppointmentDate', ''),
                "StartTime":       a.get('StartTime', ''),
                "EndTime":         a.get('EndTime', ''),
                "Status":          a.get('Status', '')
            })
    log(f"📅 مواعيد الـ 24 ساعة القادمة: {len(upcoming)} موعد")
    return jsonify(upcoming)  # ← direct ARRAY, real CRM format


@app.route('/MyCallAi/appointments/hold', methods=['POST'])
def hold_appointment():
    """Real CRM returns: {"Status": "SUCCESS", "id": "48504"}"""
    data = request.get_json() or {}
    patient = find_patient_by_fileno(data.get('patientid', ''))
    doctor  = find_doctor(data.get('doctorid', 0)) if data.get('doctorid') else None
    new_id  = int(datetime.now().timestamp())
    appt = {
        "_internal_id":  new_id,
        "AppointmentId": new_id,
        "PatientId":     str(data.get('patientid', '')),
        "PatientName":   patient.get('ArabicName') or patient.get('EnglishName') if patient else 'غير محدد',
        "PatientMobile": patient.get('Mobile', '') if patient else '',
        "DoctorId":      int(data.get('doctorid', 0)) if data.get('doctorid') else 0,
        "DoctorName":    doctor['ArabicName'] if doctor else 'غير محدد',
        "AppointmentDate": data.get('appointmentdate', ''),
        "StartTime":     data.get('fromtime', ''),
        "EndTime":       data.get('endtime', ''),
        "Status":        "Held"
    }
    appointments.append(appt)
    log(f"⏳ موعد مؤقت: {appt['PatientName']} مع {appt['DoctorName']} — {appt['AppointmentDate']} {appt['StartTime']}")
    return jsonify({"Status": "SUCCESS", "id": str(new_id)})


@app.route('/MyCallAi/appointments', methods=['POST'])
def create_appointment():
    """Direct book. Real CRM returns: {"Status": "SUCCESS", "id": "48504"}"""
    data = request.get_json() or {}
    patient = find_patient_by_fileno(data.get('patientid', ''))
    doctor  = find_doctor(data.get('doctorid', 0)) if data.get('doctorid') else None
    new_id  = int(datetime.now().timestamp())
    appt = {
        "_internal_id":  new_id,
        "AppointmentId": new_id,
        "PatientId":     str(data.get('patientid', '')),
        "PatientName":   patient.get('ArabicName') or patient.get('EnglishName') if patient else 'غير محدد',
        "PatientMobile": patient.get('Mobile', '') if patient else '',
        "DoctorId":      int(data.get('doctorid', 0)) if data.get('doctorid') else 0,
        "DoctorName":    doctor['ArabicName'] if doctor else 'غير محدد',
        "AppointmentDate": data.get('appointmentdate', ''),
        "StartTime":     data.get('fromtime', ''),
        "EndTime":       data.get('endtime', ''),
        "Status":        "Confirmed"
    }
    appointments.append(appt)
    log(f"📌 موعد مباشر: {appt['PatientName']} مع {appt['DoctorName']}")
    return jsonify({"Status": "SUCCESS", "id": str(new_id)})


@app.route('/MyCallAi/appointments/update', methods=['POST'])
def update_appointment():
    """
    Update appointment details.
    URL: POST /appointments/update  (all params in body — NOT in path)
    Body: appointmentid, patientid, doctorid, fromtime, endtime, appointmentdate (all optional except appointmentid)
    Real CRM returns: {"Status": "SUCCESS", "id": "47195"}
    """
    global appointments
    data = request.get_json() or {}
    aid = str(data.get('appointmentid', ''))
    if not aid:
        return jsonify({"message": "appointmentid is required"}), 400
    found = False
    for i, a in enumerate(appointments):
        if str(a.get('AppointmentId')) == aid or str(a.get('_internal_id')) == aid:
            if data.get('appointmentdate'):
                appointments[i]['AppointmentDate'] = data['appointmentdate']
            if data.get('fromtime'):
                appointments[i]['StartTime'] = data['fromtime']
            if data.get('endtime'):
                appointments[i]['EndTime'] = data['endtime']
            if data.get('doctorid'):
                doctor = find_doctor(data['doctorid'])
                appointments[i]['DoctorId'] = int(data['doctorid'])
                appointments[i]['DoctorName'] = doctor['ArabicName'] if doctor else appointments[i]['DoctorName']
            appointments[i]['Status'] = 'Confirmed'
            log(f"✏️ تم تعديل الموعد #{aid} — {a.get('PatientName', '')}")
            found = True
            break
    if not found:
        log(f"⚠️ محاولة تعديل موعد غير موجود: #{aid}")
    return jsonify({"Status": "SUCCESS", "id": aid})


@app.route('/MyCallAi/appointments/<aid>')
def get_appointment(aid):
    appt = next((a for a in appointments if str(a.get('AppointmentId')) == str(aid) or str(a.get('_internal_id')) == str(aid)), None)
    if appt:
        return jsonify(appt)
    return jsonify({"message": "Appointment not found"}), 404


@app.route('/MyCallAi/appointments/<aid>/confirm', methods=['POST'])
def confirm_appointment(aid):
    """Real CRM returns: plain text 'Appointment is Confirmed'"""
    global appointments
    for i, a in enumerate(appointments):
        if str(a.get('AppointmentId')) == str(aid) or str(a.get('_internal_id')) == str(aid):
            appointments[i]['Status'] = 'Confirmed'
            log(f"✅ تم تأكيد الموعد #{aid} — {a.get('PatientName', '')}")
            break
    return "Appointment is Confirmed", 200, {'Content-Type': 'text/plain'}


@app.route('/MyCallAi/appointments/<aid>/cancel', methods=['POST'])
def cancel_appointment(aid):
    """Real CRM returns: plain text 'Appointment is Canceled'"""
    global appointments
    for i, a in enumerate(appointments):
        if str(a.get('AppointmentId')) == str(aid) or str(a.get('_internal_id')) == str(aid):
            appointments[i]['Status'] = 'Cancelled'
            log(f"❌ تم إلغاء الموعد #{aid} — {a.get('PatientName', '')}")
            break
    return "Appointment is Canceled", 200, {'Content-Type': 'text/plain'}


@app.route('/MyCallAi/appointments/<aid>/reschedule', methods=['POST'])
def reschedule_appointment(aid):
    """Real CRM returns: plain text 'Appointment is Rescheduled'"""
    global appointments
    data = request.get_json() or {}
    for i, a in enumerate(appointments):
        if str(a.get('AppointmentId')) == str(aid) or str(a.get('_internal_id')) == str(aid):
            appointments[i]['Status'] = 'Rescheduled'
            if data.get('appointmentdate'):
                appointments[i]['AppointmentDate'] = data['appointmentdate']
            if data.get('fromtime'):
                appointments[i]['StartTime'] = data['fromtime']
            if data.get('endtime'):
                appointments[i]['EndTime'] = data['endtime']
            log(f"🔄 تم تعديل الموعد #{aid} — {a.get('PatientName', '')}")
            break
    return "Appointment is Rescheduled", 200, {'Content-Type': 'text/plain'}


# ─────────────────────────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


# ─────────────────────────────────────────────────────────────
# REAL CRM PROXY — Forwards requests to Dentak
# Solves 2 problems:
#   1. SSL bypass (Dentak has invalid certificate)
#   2. GET+body support (needed for checkinsurance & get_available_slots)
# ─────────────────────────────────────────────────────────────

import requests as req_lib
import urllib3
urllib3.disable_warnings()  # suppress SSL warnings in logs

REAL_DENTAK_BASE = "https://lustro.dentech.site/DentechEtabibi/MyCallAi"

@app.route('/real/<path:endpoint>', methods=['GET', 'POST'])
def proxy_to_real_crm(endpoint):
    """
    Universal proxy to real Dentak CRM.
    - Accepts any method from ElevenLabs
    - Forwards to Dentak with SSL verification disabled
    - Supports GET+body (unlike Cloudflare Workers)
    - Returns Dentak's response exactly as-is
    """
    target_url = f"{REAL_DENTAK_BASE}/{endpoint}"

    # Get JSON body if present
    body = request.get_json(silent=True)

    # Get query params if present
    params = request.args.to_dict() if request.args else None

    try:
        resp = req_lib.request(
            method='GET' if 'checkinsurance' in endpoint or 'appointments/available' in endpoint else request.method,
            url=target_url,
            json=body if body else None,
            params=params,
            verify=False,   # SSL bypass — Dentak has invalid cert
            timeout=20      # 20 second timeout — enough for Nphies (6s)
        )

        # Try to return as JSON, fall back to plain text
        try:
            return jsonify(resp.json()), resp.status_code
        except Exception:
            return resp.text, resp.status_code, {'Content-Type': 'text/plain'}

    except Exception as e:
        log(f"⚠️ Proxy error for /{endpoint}: {str(e)}")
        return jsonify({"error": str(e)}), 500
