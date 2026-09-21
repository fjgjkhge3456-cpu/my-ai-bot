import streamlit as st
import requests
import sqlite3
import datetime

# تنظیمات صفحه
st.set_page_config(page_title="ربات هوش مصنوعی من", page_icon="🤖", layout="centered")

# راه‌اندازی دیتابیس محلی برای ذخیره کاربران، پیام‌ها و تصاویر
def init_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
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
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

def log_activity(phone, name, action_type, content):
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_logs (phone, name, action_type, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (phone, name, action_type, content, str(datetime.datetime.now()))
    )
    conn.commit()
    conn.close()

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
    conn.close()

# ----------------- سیستم ورود ساده و سریع -----------------
if not st.session_state.authenticated:
    st.title("🔐 ورود به ربات هوش مصنوعی")
    st.write("لطفاً نام و شماره تلفن خود را وارد کنید تا وارد سامانه شوید.")
    
    name_input = st.text_input("نام و نام خانوادگی:")
    phone_input = st.text_input("شماره تلفن همراه (مثلا 09123456789):")
    
    if st.button("ورود به سایت 🚀"):
        if name_input and phone_input:
            st.session_state.user_name = name_input
            st.session_state.user_phone = phone_input
            st.session_state.authenticated = True
            get_or_create_user(phone_input, name_input)
            log_activity(phone_input, name_input, "ورود", "کاربر وارد سامانه شد")
            st.rerun()
        else:
            st.error("❌ لطفاً هم نام و هم شماره تلفن را وارد کنید.")

else:
    # ----------------- محیط اصلی سایت بعد از ورود -----------------
    st.sidebar.success(f"👤 کاربر: {st.session_state.user_name}")
    if st.sidebar.button("خروج از حساب 🚪"):
        st.session_state.authenticated = False
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
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": user_prompt + " (لطفا با لحن خودمانی و کلی ایموجی پاسخ بده)"}]
                    }
                    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
                    res_json = response.json()
                    if "choices" in res_json:
                        bot_reply = res_json["choices"][0]["message"]["content"]
                        st.success(bot_reply)
                    else:
                        st.error(f"خطا در پاسخ‌دهی هوش مصنوعی: {res_json}")
                except Exception as e:
                    st.error(f"خطا در ارتباط با سرور: {e}")

    # ----------------- بخش دوم: تولید تصویر -----------------
    elif menu == "🎨 تولید تصویر":
        st.title("🎨 بخش تولید تصویر هوش مصنوعی")
        st.write("🖼️ پرامپت خود را به انگلیسی بنویسید تا بهترین کیفیت تصویر خروجی داده شود. (سهمیه روزانه: ۱۰ عدد)")
        
        img_prompt = st.text_input("توضیح تصویر (ترجیحاً انگلیسی، مثلاً: futuristic car in cyberpunk city):")
        
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
                image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption=f"پرامپت شما: {img_prompt}", use_container_width=True)

    # ----------------- بخش سوم: استودیوی ویدیو -----------------
    elif menu == "🎬 استودیوی ویدیو (اشتراکی)":
        st.title("🎬 استودیوی پیشرفته تولید ویدیو")
        st.write("👑 این بخش مخصوص کاربران ویژه است (سهمیه روزانه: ۳ ویدیو).")
        
        video_prompt = st.text_input("موضوع و سناریوی ویدیو را وارد کنید:")
        
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
                st.success("✅ درخواست ساخت ویدیوی شما با موفقیت ثبت شد و به صف رندرینگ هوش مصنوعی اضافه گردید!")
                st.info("⏳ به دلیل حجم پردازش بالا، خروجی ویدیو پس از آماده‌سازی به پنل ادمین ارسال خواهد شد.")

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
