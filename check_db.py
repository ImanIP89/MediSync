import sqlite3

conn = sqlite3.connect('medisync.db')
cursor = conn.cursor()

# نمایش همه بیماری‌ها با علائمشان
cursor.execute('''
    SELECT d.name, d.urgency, GROUP_CONCAT(s.name, ', ') as symptoms
    FROM diseases d
    JOIN disease_symptoms ds ON d.id = ds.disease_id
    JOIN symptoms s ON ds.symptom_id = s.id
    GROUP BY d.id
''')

print("🏥 بیماری‌های موجود در دیتابیس:\n")
for row in cursor.fetchall():
    name, urgency, symp = row
    print(f"🔹 {name} (اورژانسی: {urgency})")
    print(f"   علائم: {symp}\n")

conn.close()