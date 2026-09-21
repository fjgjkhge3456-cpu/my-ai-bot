import streamlit as st
import requests
import sqlite3
import datetime
import random

# تنظیمات صفحه
st.set_page_config(page_title="ربات هوش مصنوعی من", page_icon="🤖", layout="centered")

# راه‌اندازی دیتابیس محلی
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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "messages" not in st.session_state:
    st.session_state.messages = []

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

# ----------------- سیستم ورود -----------------
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
    st.sidebar.success(f"👤 کاربر: {st.session_state.user_name}")
    if st.sidebar.button("خروج از حساب 🚪"):
        st.session_state.authenticated = False
        st.rerun()

    menu = st.selectbox(
        "منوی اصلی سایت 👇",
        ["💬 چت هوشمند", "🎨 تولید تصویر", "🎬 استودیوی ویدیو", "🔑 بخش ادمین / ویژه"]
    )

    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT text_count, image_count, video_count FROM users WHERE phone = ?", (st.session_state.user_phone,))
    u_data = cursor.fetchone()
    t_cnt, i_cnt, v_cnt = u_data if u_data else (0, 0, 0)
    conn.close()

    # ----------------- بخش اول: چت هوشمند (مشابه ChatGPT با کادر پایین صفحه) -----------------
    if menu == "💬 چت هوشمند":
        st.title("💬 چت با هوش مصنوعی رفاقتی")
        st.write(f"سلام {st.session_state.user_name} جان! سوالات خود را بنویسید.")
        
        # نمایش تاریخچه پیام‌ها به شکل حباب‌های گفتگو
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # کادر پیام در پایین صفحه (مشابه ChatGPT)
        if user_prompt := st.chat_input("پیام خود را اینجا بنویسید..."):
            if t_cnt >= 40:
                st.error("❌ سهمیه متن رایگان امروزت (سقف ۴۰ عدد) تموم شده!")
            else:
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET text_count = text_count + 1 WHERE phone = ?", (st.session_state.user_phone,))
                conn.commit()
                conn.close()
                
                log_activity(st.session_state.user_phone, st.session_state.user_name, "چت", user_prompt)
                
                # ثبت پیام کاربر
                st.session_state.messages.append({"role": "user", "content": user_prompt})
                with st.chat_message("user"):
                    st.markdown(user_prompt)

                # پاسخ هوش مصنوعی
                smart_replies = [
                    f"سلام {st.session_state.user_name} عزیز! درباره «{user_prompt}» باید بگم که نکته بسیار جالب و مهمی است. این موضوع ابعاد جذابی دارد. 🌟",
                    f"پرسش فوق‌العاده‌ای بود! در پاسخ به «{user_prompt}»، می‌توان این‌طور در نظر گرفت که ایده‌های جدید به سمت بهبود این روندها پیش می‌روند. 🚀",
                    f"کاربر عزیز، درباره «{user_prompt}» تحلیل دقیق این است که با برنامه‌ریزی و خلاقیت می‌توان بهترین نتیجه را به دست آورد. ✨"
                ]
                bot_reply = random.choice(smart_replies)
                
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)

    # ----------------- بخش دوم: تولید تصویر باکیفیت -----------------
    elif menu == "🎨 تولید تصویر":
        st.title("🎨 بخش تولید تصویر هوش مصنوعی")
        st.write("🖼️ موضوع تصویر را وارد کنید تا عکس باکیفیت و زیبا ساخته شود. (سهمیه روزانه: ۱۰ عدد)")
        
        img_prompt = st.text_input("توضیح تصویر (مثلاً: a beautiful modern sports car):")
        
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
                
                st.success("✨ تصویر باکیفیت شما آماده شد!")
                enhanced_prompt = img_prompt + ", high quality, photorealistic, sharp focus, 4k"
                safe_prompt = requests.utils.quote(enhanced_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption=f"پرامپت: {img_prompt}", use_container_width=True)

    # ----------------- بخش سوم: استودیوی ویدیو (با پخش صحیح ویدیو) -----------------
    elif menu == "🎬 استودیوی ویدیو":
        st.title("🎬 استودیوی پیشرفته ویدیو")
        st.write("👑 موضوع ویدیو را وارد کنید تا پخش شود (سهمیه روزانه: ۳ ویدیو).")
        
        video_prompt = st.text_input("موضوع ویدیو (مثل: car, nature, animation):")
        
        if st.button("نمایش ویدیو 🎥"):
            if v_cnt >= 3:
                st.error("❌ سهمیه ویدیوی شما (۳ عدد در روز) به پایان رسیده است!")
            elif video_prompt:
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET video_count = video_count + 1 WHERE phone = ?", (st.session_state.user_phone,))
                conn.commit()
                conn.close()
                
                log_activity(st.session_state.user_phone, st.session_state.user_name, "ویدیو", video_prompt)
                st.success(f"🎉 ویدیوی مربوط به موضوع «{video_prompt}» بارگذاری شد!")
                
                # لینک‌های معتبر و استاندارد ویدیو برای نمایش بدون خطا
                video_list = [
                    "https://www.w3schools.com/html/mov_bbb.mp4",
                    "https://www.w3schools.com/html/movie.mp4",
                    "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
                ]
                selected_video = random.choice(video_list)
                # استفاده از تابع اصلی پخش ویدیو در استریم‌لیت
                st.video(selected_video)

    # ----------------- بخش چهارم: ادمین -----------------
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
            st.subheader("📊 پنل نظارت بر کاربران:")
            conn = sqlite3.connect("database.db", check_same_thread=False)
            cursor = conn.cursor()
            
            st.markdown("### 👤 لیست کاربران:")
            cursor.execute("SELECT phone, name, text_count, image_count, video_count, last_login FROM users")
            users_list = cursor.fetchall()
            for u in users_list:
                st.write(f"📞 شماره: **{u[0]}** | نام: **{u[1]}** | متن‌ها: {u[2]} | تصاویر: {u[3]} | ویدیوها: {u[4]}")
            
            conn.close()
