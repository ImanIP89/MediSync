from flask import Flask, render_template, jsonify, request, session
import sqlite3
import openai

app = Flask(__name__)
app.secret_key = 'medisync-secret-key-change-in-production'

# ---------- پیکربندی DeepSeek ----------
DEEPSEEK_API_KEY = "sk-215d3b60ca584440ac081399b905f462"  # 🔑 کلید خود را جایگزین کن

# ---------- توابع کمکی ----------
def get_db():
    """اتصال به دیتابیس SQLite با پشتیبانی از دسترسی هم‌زمان چند کاربر"""
    conn = sqlite3.connect('medisync.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def ask_deepseek(question):
    """ارسال سوال به DeepSeek و دریافت پاسخ"""
    openai.api_key = DEEPSEEK_API_KEY
    openai.api_base = "https://api.deepseek.com/v1"
    prompt = f"""تو یک دستیار پزشکی هوشمند و مهربان هستی که به زبان فارسی و روان صحبت می‌کنی.
با توجه به اطلاعات زیر، به سوال بیمار پاسخ بده و توضیح بده که چه اقدامی باید انجام دهد.
همیشه یادآوری کن که این یک نظر اولیه است و باید به پزشک مراجعه کند.

سوال بیمار: {question}

پاسخ تو:"""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "شما یک دستیار پزشک هستید و به فارسی جواب می‌دهید."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ خطا در ارتباط با DeepSeek: {str(e)}"

def translate_text(text, target_lang='English'):
    """ترجمه متن با DeepSeek"""
    prompt = f"""Translate the following Persian medical text to {target_lang}.
If the text is not medical, still translate it accurately and naturally.
Text: {text}
Translation:"""
    try:
        openai.api_key = DEEPSEEK_API_KEY
        openai.api_base = "https://api.deepseek.com/v1"
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful medical translator. Always reply in the target language."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Translation error: {str(e)}"

def get_disease_symptoms(disease_id):
    """برگرداندن لیست علائم یک بیماری مشخص"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT s.name FROM disease_symptoms ds JOIN symptoms s ON ds.symptom_id = s.id WHERE ds.disease_id = ?', (disease_id,))
    syms = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return syms

# ---------- مسیرهای صفحات ----------
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')

@app.route('/patient')
def patient_form():
    return render_template('patient.html')

@app.route('/translate')
def translate_page():
    return render_template('translate.html')

@app.route('/bulk')
def bulk_page():
    return render_template('bulk.html')

# ---------- API: دریافت لیست بیماری‌ها ----------
@app.route('/api/diseases')
def api_diseases():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.name, d.description, d.treatment, d.urgency,
               GROUP_CONCAT(s.name, ', ') as symptoms
        FROM diseases d
        JOIN disease_symptoms ds ON d.id = ds.disease_id
        JOIN symptoms s ON ds.symptom_id = s.id
        GROUP BY d.id
    ''')
    rows = cursor.fetchall()
    conn.close()
    diseases = []
    for row in rows:
        diseases.append({
            "name": row["name"],
            "description": row["description"],
            "treatment": row["treatment"],
            "urgency": row["urgency"],
            "symptoms": row["symptoms"]
        })
    return jsonify(diseases)

# ---------- API: اجرای دستورات ترمینال ----------
@app.route('/api/command', methods=['POST'])
def api_command():
    data = request.get_json()
    cmd = data.get('cmd', '').strip()
    cmd_lower = cmd.lower()
    response = {"output": ""}

    if cmd_lower == 'check' or cmd_lower == 'show':
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.name, d.urgency, GROUP_CONCAT(s.name, ', ') as symptoms
            FROM diseases d
            JOIN disease_symptoms ds ON d.id = ds.disease_id
            JOIN symptoms s ON ds.symptom_id = s.id
            GROUP BY d.id
        ''')
        rows = cursor.fetchall()
        conn.close()
        if rows:
            output = "🏥 بیماری‌های موجود در دیتابیس:\n"
            for r in rows:
                output += f"🔹 {r['name']} (اورژانس: {r['urgency']})\n   علائم: {r['symptoms']}\n"
        else:
            output = "❌ دیتابیس خالی است."
        response["output"] = output

    elif cmd_lower.startswith('diagnose'):
        parts = cmd.split(' ', 1)
        if len(parts) < 2:
            response["output"] = "❌ نحوه استفاده: diagnose <علائم با کاما> یا diagnose <جمله فارسی>"
        else:
            raw_text = parts[1].strip()
            if ',' in raw_text:
                symptoms_list = [s.strip() for s in raw_text.split(',') if s.strip()]
            else:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM symptoms')
                all_symptoms = [row['name'] for row in cursor.fetchall()]
                conn.close()
                symptoms_list = [sym for sym in all_symptoms if sym in raw_text]

            if not symptoms_list:
                response["output"] = "❌ هیچ علامت قابل تشخیصی در جمله پیدا نشد."
            else:
                conn = get_db()
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(symptoms_list))
                query = f'''
                    SELECT d.name, d.description, d.treatment, d.urgency, COUNT() as matched_count
                    FROM diseases d
                    JOIN disease_symptoms ds ON d.id = ds.disease_id
                    JOIN symptoms s ON ds.symptom_id = s.id
                    WHERE s.name IN ({placeholders})
                    GROUP BY d.id
                    ORDER BY matched_count DESC
                    LIMIT 1
                '''
                cursor.execute(query, symptoms_list)
                row = cursor.fetchone()
                conn.close()
                if row:
                    output = f"🩺 تشخیص احتمالی: {row['name']} (تطابق: {row['matched_count']} علامت)\n"
                    output += f"   شرح: {row['description']}\n"
                    output += f"   درمان اولیه: {row['treatment']}\n"
                    output += f"   سطح اورژانس: {row['urgency']}"
                else:
                    output = "❌ هیچ بیماری با این علائم پیدا نشد."
            response["output"] = output

    elif cmd_lower.startswith('add'):
        fields = {'name': '', 'urgency': 'کم', 'desc': '', 'treat': '', 'sym': ''}
        params = cmd[3:].strip()
        parts = params.split()
        for part in parts:
            if ':' in part:
                key, val = part.split(

':', 1)
                key = key.lower()
                if key in fields:
                    fields[key] = val.strip()
        if not fields['name'] or not fields['sym']:
            response["output"] = "❌ حداقل name و sym الزامی است.\nفرمت: add name:نام_بیماری sym:علامت۱,علامت۲ urgency:کم/متوسط/بالا desc:توضیح treat:درمان"
        else:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO diseases (name, description, treatment, urgency) VALUES (?, ?, ?, ?)',
                           (fields['name'], fields['desc'], fields['treat'], fields['urgency']))
            disease_id = cursor.lastrowid
            symptom_names = [s.strip() for s in fields['sym'].split(',') if s.strip()]
            for sym in symptom_names:
                cursor.execute('INSERT OR IGNORE INTO symptoms (name) VALUES (?)', (sym,))
                cursor.execute('SELECT id FROM symptoms WHERE name = ?', (sym,))
                sym_id = cursor.fetchone()[0]
                cursor.execute('INSERT OR IGNORE INTO disease_symptoms (disease_id, symptom_id) VALUES (?, ?)',
                               (disease_id, sym_id))
            conn.commit()
            conn.close()
            response["output"] = f"✅ بیماری «{fields['name']}» با موفقیت به دیتابیس اضافه شد.\nعلائم: {fields['sym']}"

    elif cmd_lower.startswith('ask'):
        parts = cmd.split(' ', 1)
        if len(parts) < 2:
            response["output"] = "❌ نحوه استفاده: ask سوال خود را بنویسید"
        else:
            question = parts[1].strip()
            answer = ask_deepseek(question)
            response["output"] = f"🤖 پاسخ DeepSeek:\n{answer}"

    elif cmd_lower.startswith('translate'):
        parts = cmd.split(' ', 1)
        if len(parts) < 2:
            response["output"] = "❌ نحوه استفاده: translate <متن> یا translate to <زبان>: <متن>"
        else:
            text_part = parts[1].strip()
            target = 'English'
            if text_part.lower().startswith('to '):
                colon_idx = text_part.find(':')
                if colon_idx == -1:
                    response["output"] = "❌ فرمت: translate to French: Bonjour"
                else:
                    target = text_part[3:colon_idx].strip()
                    text = text_part[colon_idx+1:].strip()
                    if not text:
                        response["output"] = "❌ متنی برای ترجمه وارد نشده."
                    else:
                        translation = translate_text(text, target)
                        response["output"] = f"🌐 ترجمه به {target}:\n{translation}"
            else:
                translation = translate_text(text_part, 'English')
                response["output"] = f"🌐 ترجمه به انگلیسی:\n{translation}"

    elif cmd_lower.startswith('guided'):
        response["output"] = "⚡ تشخیص گام‌به‌گام فقط از طریق فرم بیمار (Patient Form) در دسترس است. لطفاً از آنجا استفاده کنید."

    else:
        response["output"] = "❌ دستور نامعتبر. دستورات: check, diagnose, add, ask, translate, guided"

    return jsonify(response)

# ---------- API: تشخیص بیمار (فرم) ----------
@app.route('/api/patient_diagnose', methods=['POST'])
def patient_diagnose():
    data = request.get_json()
    raw_text = data.get('symptoms', '').strip()
    if not raw_text:
        return jsonify({"error": "لطفاً علائم خود را وارد کنید."})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM symptoms')
    all_symptoms = [row['name'] for row in cursor.fetchall()]
    conn.close()

    found_symptoms = [sym for sym in all_symptoms if sym in raw_text]
    if not found_symptoms:
        return jsonify({"error": "متأسفانه هیچ علامتی در متن شما پیدا نشد. لطفاً واضح‌تر توضیح دهید."})

    conn = get_db()
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(found_symptoms))
    query = f'''
        SELECT d.name, d.description, d.treatment, d.urgency, COUNT() as matched_count
        FROM diseases d
        JOIN disease_symptoms ds ON d.id = ds.disease_id
        JOIN symptoms s ON ds.symptom_id = s.id
        WHERE s.name IN ({placeholders})
        GROUP BY d.id
        ORDER BY matched_count DESC
        LIMIT 1
    '''
    cursor.execute(query, found_symptoms)
    row = cursor.fetchone()
    conn.close()

    if row:
        result = {
            "name": row["name"],
            "description": row["description"],
            "treatment": row["treatment"],
            "urgency": row["urgency"],
            "matched": row["matched_count"],
            "symptoms_found": found_symptoms
        }
        return jsonify(result)
    else:
        return jsonify({"error": "بیماری منطبق با علائم شما یافت نشد. لطفاً با پزشک مشورت کنید."})

# ---------- API: افزودن گروهی بیماری‌ها ----------
@app.route('/api/bulk_add', methods=['POST'])
def api_bulk_add():
    data = request.get_json()
    diseases = data.get('diseases', [])
    if not diseases:
        return jsonify({"message": "❌ هیچ داده‌ای ارسال نشد."})
    conn = get_db()
    cursor = conn.cursor()
    added = 0
    for d in diseases:
        name = d.get('name','').strip()
        urgency = d.get('urgency','کم').strip()
        desc = d.get('description','').strip()
        treat = d.get('treatment','').strip()
        symptoms_str = d.get('symptoms','').strip()
        if not name or not symptoms_str:
            continue
        cursor.execute('INSERT INTO diseases (name, description, treatment, urgency) VALUES (?,?,?,?)',
                       (name, desc, treat, urgency))
        disease_id = cursor.lastrowid
        symptom_names = [s.strip() for s in symptoms_str.split(',') if s.strip()]
        for sym in symptom_names:
            cursor.execute('INSERT OR IGNORE INTO symptoms (name) VALUES (?)', (sym,))
            cursor.execute('SELECT id FROM symptoms WHERE name = ?', (sym,))
            sym_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO disease_symptoms (disease_id, symptom_id) VALUES (?,?)',
                           (disease_id, sym_id))
        added += 1
    conn.commit()
    conn.close()
    return jsonify({"message": f"✅ {added} بیماری با موفقیت به دیتابیس اضافه شد."})

# ---------- API: ترجمه ----------
@app.route('/api/translate', methods=['POST'])
def api_translate():
    data = request.get_json()
    text = data.get('text', '').strip()
    target = data.get('target', 'English').strip()
    if not text:
        return jsonify({"error": "No text provided."})
    translation = translate_text(text, target)
    return jsonify({"translation": translation})

# ---------- API: پرسش از هوش مصنوعی (در صورت نیاز جداگانه) ----------
@app.route('/api/ai_ask', methods=['POST'])
def ai_ask():
    data = request.get_json()
    question = data.get('question', '').strip()
    if not question:
        return jsonify({"error": "لطفاً سوال خود را بنویسید."})
    answer = ask_deepseek(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    # host='0.0.0.0' باعث می‌شود همه‌ی دستگاه‌های شبکه بتوانند متصل شوند
    # threaded=True برای پشتیبانی از چند کاربر هم‌زمان ضروری است
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
