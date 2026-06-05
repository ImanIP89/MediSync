import sqlite3

# اتصال به دیتابیس (اگر وجود نداشته باشه، ساخته میشه)
conn = sqlite3.connect('medisync.db')
cursor = conn.cursor()

# ایجاد جدول‌ها
cursor.executescript('''
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    treatment TEXT,
    urgency TEXT
);

CREATE TABLE IF NOT EXISTS symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS disease_symptoms (
    disease_id INTEGER,
    symptom_id INTEGER,
    PRIMARY KEY (disease_id, symptom_id),
    FOREIGN KEY (disease_id) REFERENCES diseases (id),
    FOREIGN KEY (symptom_id) REFERENCES symptoms (id)
);
''')

# وارد کردن داده‌های نمونه (اول بیماری‌ها، بعد علائم، بعد رابطه‌ها)
# بیماری‌های نمونه
diseases_data = [
    ('سرماخوردگی', 'عفونت ویروسی دستگاه تنفسی فوقانی', 'استراحت، مایعات گرم، مصرف مسکن ساده', 'کم'),
    ('میگرن', 'سردرد شدید ضربان‌دار که معمولاً یک طرف سر را درگیر می‌کند', 'استراحت در محیط تاریک و ساکت، داروهای ضد میگرن مانند ایبوپروفن', 'متوسط'),
    ('گاستروانتریت (التهاب معده و روده)', 'التهاب معده و روده که باعث اسهال و استفراغ می‌شود', 'جبران آب از دست رفته (ORS)، استراحت، پرهیز از غذای سنگین', 'متوسط')
]

cursor.executemany('INSERT INTO diseases (name, description, treatment, urgency) VALUES (?, ?, ?, ?)', diseases_data)

# علائم نمونه (لیست یکتا)
symptoms_list = ['تب', 'آبریزش بینی', 'عطسه', 'سردرد', 'تهوع', 'استفراغ', 'اسهال', 'درد شکم', 'حساسیت به نور', 'خستگی']
for s in symptoms_list:
    cursor.execute('INSERT OR IGNORE INTO symptoms (name) VALUES (?)', (s,))

# ذخیره کردن تا IDها آماده بشن
conn.commit()

# حالا رابطه بیماری-علامت رو تعریف می‌کنیم
# اول ID بیماری‌ها و علائم رو می‌گیریم
cursor.execute("SELECT id, name FROM diseases")
disease_ids = {name: i for i, name in cursor.fetchall()}

cursor.execute("SELECT id, name FROM symptoms")
symptom_ids = {name: i for i, name in cursor.fetchall()}

# رابطه‌ها (تاپل‌های (disease_id, symptom_id))
relations = [
    # سرماخوردگی: تب، آبریزش بینی، عطسه، خستگی
    (disease_ids['سرماخوردگی'], symptom_ids['تب']),
    (disease_ids['سرماخوردگی'], symptom_ids['آبریزش بینی']),
    (disease_ids['سرماخوردگی'], symptom_ids['عطسه']),
    (disease_ids['سرماخوردگی'], symptom_ids['خستگی']),
    # میگرن: سردرد، تهوع، حساسیت به نور، خستگی
    (disease_ids['میگرن'], symptom_ids['سردرد']),
    (disease_ids['میگرن'], symptom_ids['تهوع']),
    (disease_ids['میگرن'], symptom_ids['حساسیت به نور']),
    (disease_ids['میگرن'], symptom_ids['خستگی']),
    # گاستروانتریت: تهوع، استفراغ، اسهال، درد شکم، تب
    (disease_ids['گاستروانتریت (التهاب معده و روده)'], symptom_ids['تهوع']),
    (disease_ids['گاستروانتریت (التهاب معده و روده)'], symptom_ids['استفراغ']),
    (disease_ids['گاستروانتریت (التهاب معده و روده)'], symptom_ids['اسهال']),
    (disease_ids['گاستروانتریت (التهاب معده و روده)'], symptom_ids['درد شکم']),
    (disease_ids['گاستروانتریت (التهاب معده و روده)'], symptom_ids['تب'])
]

cursor.executemany('INSERT OR IGNORE INTO disease_symptoms (disease_id, symptom_id) VALUES (?, ?)', relations)

conn.commit()
conn.close()
print("✅ دیتابیس با موفقیت ساخته شد و داده‌های نمونه وارد شد.")