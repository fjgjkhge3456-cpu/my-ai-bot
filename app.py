import streamlit as st
import requests
import random
import sqlite3
import datetime

# تنظیمات صفحه
st.set_page_config(page_title="ربات هوش مصنوعی من", page_icon="🤖", layout="centered")

# راه‌اندازی دیتابیس محلی برای ذخیره کاربران، پیام‌ها و تصاویر
def init_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    # جدول کاربران
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            name TEXT,
            text_count INT,
            image_count INT,
            video_count INT,
            last_login TEXT
        )
    """)
    # جدول تاریخچه فعالیت‌ها و چت‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            name TEXT,
            action_type TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# مدیریت نشست‌ها در استریم‌لیت
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "verification_code" not in st.session_state:
    st.session_state.verification_code = ""
if "code_sent" not in st.session_state:
    st.session_state.code_sent = False
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# تابع کمکی برای ثبت لاگ در دیتابیس
def log_activity(phone, name, action_type, content):
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_logs (phone, name, action_type, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (phone, name, action_type, content, str(datetime.datetime.now()))
    )
    conn.commit()
    conn.close()

# تابع کمکی برای بررسی و بروزرسانی سهمیه کاربر
def get_or_create_user(phone, name):
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users (phone, name, text_count, image_count, video_count, last_login) VALUES (?, ?, 0, 0, 0, ?)",
            (phone, name, str(datetime.datetime.now()))
        )
        conn.commit()
        user = (phone, name, 0, 0, 0, str(datetime.datetime.now()))
    conn.close()
    return user

# ----------------- سیستم ورود و ثبت‌نام اولیه -----------------
if not st.session_state.authenticated:
    st.title("🔐 ورود به ربات هوش مصنوعی")
    st.write("لطفاً نام و شماره تلفن خود را وارد کنید تا کد تأیید برای شما ارسال شود.")
    
    name_input = st.text_input("نام و نام خانوادگی:")
    phone_input = st.text_input("شماره تلفن همراه (مثلا 09123456789):")
    
    if not st.session_state.code_sent:
        if st.button("ارسال کد تأیید 📩"):
            if name_input and phone_input:
                generated_code = str(random.randint(1000, 9999))
                st.session_state.verification_code = generated_code
                st.session_state.user_name = name_input
                st.session_state.user_phone = phone_input
                st.session_state.code_sent = True
                st.success(f"✅ کد تأیید خودکار ارسال شد! (کد تست شما: {generated_code})")
                st.rerun()
            else:
                st.error("❌ لطفاً هم نام و هم شماره تلفن را وارد کنید.")
    else:
        st.info(f"کد تأیید به شماره {st.session_state.user_phone} ارسال شد.")
        entered_code = st.text_input("کد تأیید ۴ رقمی را وارد کنید:")
        
        if st.button("تایید و ورود 🚀"):
            if entered_code == st.session_state.verification_code:
                st.session_state.authenticated = True
                get_or_create_user(st.session_state.user_phone, st.session_state.user_name)
                log_activity(st.session_state.user_phone, st.session_state.user_name, "ورود", "کاربر وارد سامانه شد")
                st.success(f"🎉 خوش آمدی {st.session_state.user_name} عزیز!")
                st.rerun()
            else:
                st.error("❌ کد وارد شده اشتباه است.")

else:
    # ----------------- محیط اصلی سایت بعد از ورود -----------------
    st.sidebar.success(f"👤 کاربر: {st.session_state.user_name}")
    if st.sidebar.button("خروج از حساب 🚪"):
        st.session_state.authenticated = False
        st.session_state.code_sent = False
        st.rerun()

    menu = st.selectbox(
        "منوی اصلی سایت 👇",
        ["💬 چت هوشمند", "🎨 تولید تصویر", "🎬 استودیوی ویدیو (اشتراکی)", "🔑 بخش ادمین / ویژه"]
    )

    # اتصال برای خواندن اطلاعات کاربر جاری
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT text_count, image_count, video_count FROM users WHERE phone = ?", (st.session_state.user_phone,))
    u_data = cursor.fetchone()
    t_cnt, i_cnt, v_cnt = u_data if u_data else (0, 0, 0)
    conn.close()

    # ----------------- بخش اول: چت هوشمند -----------------
    if menu == "💬 چت هوشمند":
        st.title("💬 چت با هوش مصنوعی رفاقتی")
        st.write(f"سلام {st.session_state.user_name} جان! هر سوالی داری بپرس.")
        
        user_prompt = st.text_input("پیام خود را بنویسید...")
        
        if st.button("ارسال پیام 🚀"):
            if t_cnt >= 40:
                st.error("❌ سهمیه متن رایگان امروزت (سقف ۴۰ عدد) تموم شده!")
            elif user_prompt:
                # افزایش سهمیه در دیتابیس
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET text_count = text_count + 1 WHERE phone = ?", (st.session_state.user_phone,))
                conn.commit()
                conn.close()
                
                log_activity(st.session_state.user_phone, st.session_state.user_name, "چت", user_prompt)
                
                try:
                    headers = {
                        "Authorization": "Bearer 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",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": "llama-3.1-70b-versatile",
                        "messages": [{"role": "user", "content": user_prompt + " (لطفا با لحن خودمانی و کلی ایموجی پاسخ بده)"}]
                    }
                    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
                    res_json = response.json()
                    if "choices" in res_json:
                        bot_reply = res_json["choices"][0]["message"]["content"]
                        st.success(bot_reply)
                    else:
                        st.error("خطا در پاسخ‌دهی هوش مصنوعی.")
                except Exception as e:
                    st.error(f"خطا در ارتباط با سرور: {e}")

    # ----------------- بخش دوم: تولید تصویر -----------------
    elif menu == "🎨 تولید تصویر":
        st.title("🎨 بخش تولید تصویر هوش مصنوعی")
        st.write("🖼️ متن خود را وارد کنید تا تصویر دلخواهتان ساخته شود. (سهمیه روزانه: ۱۰ عدد)")
        
        img_prompt = st.text_input("توضیح تصویر به انگلیسی یا فارسی:")
        
        if st.button("بساز 🎨"):
            if i_cnt >= 10:
                st.error("❌ سهمیه تصویر رایگان امروزت تموم شده (سقف ۱۰ عدد)!")
            elif img_prompt:
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET image_count = image_count + 1 WHERE phone = ?", (st.session_state.user_phone,))
                conn.commit()
                conn.close()
                
                log_activity(st.session_state.user_phone, st.session_state.user_name, "تصویر", img_prompt)
                
                st.success("✨ تصویر شما با موفقیت آماده شد!")
                safe_prompt = requests.utils.quote(img_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}"
                st.image(image_url, caption=f"پرامپت شما: {img_prompt}")

    # ----------------- بخش سوم: استودیوی ویدیو -----------------
    elif menu == "🎬 استودیوی ویدیو (اشتراکی)":
        st.title("🎬 استودیوی پیشرفته تولید ویدیو")
        st.write("👑 این بخش مخصوص کاربران ویژه است (سهمیه روزانه: ۳ ویدیو).")
        
        video_prompt = st.text_input("موضوع ویدیو را وارد کنید:")
        
        if st.button("تولید ویدیو 🎥"):
            if v_cnt >= 3:
                st.error("❌ سهمیه ویدیوی شما (۳ عدد در روز) به پایان رسیده است!")
            elif video_prompt:
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET video_count = video_count + 1 WHERE phone = ?", (st.session_state.user_phone,))
                conn.commit()
                conn.close()
                
                log_activity(st.session_state.user_phone, st.session_state.user_name, "ویدیو", video_prompt)
                st.info("⏳ درخواست ویدیوی شما ثبت شد و در صف پردازش قرار گرفت!")

    # ----------------- بخش چهارم: ادمین و مدیریت کامل -----------------
    elif menu == "🔑 بخش ادمین / ویژه":
        st.title("🔑 ورود به پنل مدیریت و نظارت")
        
        admin_pass = st.text_input("رمز عبور ادمین را وارد کنید:", type="password")
        if st.button("ورود به پنل مدیریت 🔐"):
            if admin_pass == "2345":
                st.session_state.admin_logged = True
                st.success("✅ با موفقیت وارد پنل ادمین شدی!")
            else:
                st.error("❌ رمز عبور اشتباه است!")
                
        if st.session_state.admin_logged:
            st.subheader("📊 پنل نظارت بر کاربران و فعالیت‌ها:")
            
            # خواندن تمام کاربران از دیتابیس
            conn = sqlite3.connect("database.db", check_same_thread=False)
            cursor = conn.cursor()
            
            st.markdown("### 👤 لیست کاربران ثبت‌نام شده:")
            cursor.execute("SELECT phone, name, text_count, image_count, video_count, last_login FROM users")
            users_list = cursor.fetchall()
            for u in users_list:
                st.write(f"📞 شماره: **{u[0]}** | نام: **{u[1]}** | متن‌ها: {u[2]} | تصاویر: {u[3]} | ویدیوها: {u[4]}")
            
            st.markdown("---")
            st.markdown("### 📝 تاریخچه کامل پیام‌ها، تصاویر و درخواست‌های کاربران:")
            cursor.execute("SELECT phone, name, action_type, content, timestamp FROM activity_logs ORDER BY id DESC")
            logs_list = cursor.fetchall()
            for log in logs_list:
                st.info(f"زمان: {log[4]} | کاربر: {log[1]} ({log[0]}) | نوع: **{log[2]}**\n\nمتن/موضوع: `{log[3]}`")
                
            conn.close()
            
            if st.button("پاکسازی و ریست کردن دیتابیس 🗑️"):
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users")
                cursor.execute("DELETE FROM activity_logs")
                conn.commit()
                conn.close()
                st.success("دیتابیس با موفقیت پاکسازی شد!")
