🇮🇷 فارسی

## 🩺 MediSync v1.0.0 — اولین انتشار عمومی

**یک دستیار سلامت هوشمند برای تشخیص اولیه‌ی بیماری‌ها به زبان فارسی، با قابلیت‌های:**

- ✨ **تشخیص هوشمند** از روی جملات محاوره‌ای فارسی (NLP)
- 🎙️ **ورودی صوتی** با Web Speech API (فارسی)
- 💻 **ترمینال CMD** برای پزشکان (دستورات check, diagnose, add, delete, ask, translate)
- 👤 **فرم بیمار** با طراحی واکنش‌گرا
- 🧠 **اتصال به DeepSeek** برای مشاوره‌ی پزشکی هوشمند
- 🌐 **ترجمه‌ی چندزبانه** (انگلیسی، کره‌ای، فرانسوی، عربی و...)
- 📥 **بارگذاری گروهی** بیماری‌ها (Bulk import)
- 🔐 **سیستم احراز هویت** با نقش‌های Admin، Doctor و Patient
- 👤 **پروفایل کاربری** (سوابق پزشکی، داروها و...)
- 📡 **چند کاربره و شبکه‌ای** (قابل استفاده از چند دستگاه هم‌زمان)
- 🍓 **بهینه برای سخت‌افزار ضعیف** (Raspberry Pi)

### 🛠️ نصب و اجرا
```bash
git clone <repo-url>
cd medisync
pip install -r requirements.txt
python database.py   # راه‌اندازی دیتابیس
python app.py        # اجرا روی http://localhost:5000
```

🔑 حساب‌های پیش‌فرض
ادمین: admin / admin123

پزشک: doctor / doctor123

📄 مجوز
این پروژه تحت MIT License منتشر می‌شود.

🙏 قدردانی
این پروژه با عشق و اشتیاق به پزشکی و فناوری، در تنهاییِ شب‌های یک دانش‌آموز ساخته شد.
از تمام آموزگارانی که چراغ دانش را در دلم روشن کردند، از خانواده‌ام که با صبوری و حمایت بستری برای رؤیاپردازی‌ام فراهم نمودند، و از همه‌ی پزشکان و مهندسانی که بی‌وقفه برای سلامت انسان‌ها تلاش می‌کنند، سپاسگزارم.

امیدوارم MediSync روزی بتواند حتی به اندازهٔ یک مشاور ساده، یاری‌گر کسانی باشد که به مراقبت‌های پزشکی دسترسی آسان ندارند.

با آرزوی آینده‌ای سالم‌تر برای همه.
— سازندهٔ پروژه، ایمان پاینده 🩺✨
🇬🇧 English

## 🩺 MediSync v1.0.0 — First Public Release

**A smart health assistant for preliminary disease diagnosis in Persian, featuring:**

- ✨ **Smart Diagnosis** from conversational Persian sentences (NLP)
- 🎙️ **Voice Input** via Web Speech API (Persian)
- 💻 **CMD Terminal** for physicians (commands: check, diagnose, add, delete, ask, translate)
- 👤 **Patient Form** with responsive design
- 🧠 **DeepSeek Integration** for intelligent medical consultation
- 🌐 **Multilingual Translation** (English, Korean, French, Arabic, etc.)
- 📥 **Bulk Disease Import** (bulk add)
- 🔐 **Authentication System** with Admin, Doctor, and Patient roles
- 👤 **User Profile** (medical history, medications, etc.)
- 📡 **Multi-user & Network-ready** (accessible from multiple devices simultaneously)
- 🍓 **Optimized for Low-end Hardware** (Raspberry Pi)

### 🛠️ Installation & Run
```bash
git clone <repo-url>
cd medisync
pip install -r requirements.txt
python database.py   # Set up the database
python app.py        # Run on http://localhost:5000
```
🔑 Default Accounts
Admin: admin / admin123

Doctor: doctor / doctor123

📄 License
This project is released under the MIT License.

🙏 Acknowledgments
This project was built with love and passion for medicine and technology, during the quiet nights of a student's life.
I am deeply grateful to all the teachers who lit the flame of knowledge in my heart, to my family whose patience and support gave me a safe space to dream, and to all the physicians and engineers who tirelessly work for the well-being of humanity.

I hope MediSync can one day serve as even a humble assistant to those who lack easy access to medical care.

Wishing everyone a healthier future.
— The creator, iman payande🩺✨

