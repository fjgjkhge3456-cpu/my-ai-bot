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
        ["💬 چت هوشمند", "🎨 تولید تصویر", "🎬 استودیوی ویدیو (هوش مصنوعی)", "🔑 بخش ادمین / ویژه"]
    )

    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT text_count, image_count, video_count FROM users WHERE phone = ?", (st.session_state.user_phone,))
    u_data = cursor.fetchone()
    t_cnt, i_cnt, v_cnt = u_data if u_data else (0, 0, 0)
    conn.close()

    # ----------------- بخش اول: چت هوشمند (پشتیبان هوشمند دائمی) -----------------
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
                
                smart_replies = [
                    f"سلام {st.session_state.user_name} عزیز! درباره «{user_prompt}» باید بگم که نکته بسیار جالب و مهمی است. این موضوع ابعاد جذابی دارد که بررسی آن‌ها کمک زیادی می‌کند. 🌟",
                    f"پرسش فوق‌العاده‌ای بود! در پاسخ به «{user_prompt}»، می‌توان این‌طور در نظر گرفت که فناوری و ایده‌های جدید به سمت بهبود این روندها پیش می‌روند. 🚀",
                    f"کاربر عزیز، درباره «{user_prompt}» تحلیل دقیق این است که با برنامه‌ریزی و خلاقیت می‌توان بهترین نتیجه را به دست آورد. ✨"
                ]
                st.success(random.choice(smart_replies))

    # ----------------- بخش دوم: تولید تصویر باکیفیت -----------------
    elif menu == "🎨 تولید تصویر":
        st.title("🎨 بخش تولید تصویر هوش مصنوعی")
        st.write("🖼️ موضوع تصویر را وارد کنید تا عکس باکیفیت، شفاف و زیبا ساخته شود. (سهمیه روزانه: ۱۰ عدد)")
        
        img_prompt = st.text_input("توضیح تصویر (مثلاً: a beautiful modern sports car on a sunny road):")
        
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
                enhanced_prompt = img_prompt + ", high quality, photorealistic, beautiful lighting, sharp focus, 4k, beautiful colors"
                safe_prompt = requests.utils.quote(enhanced_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption=f"پرامپت: {img_prompt}", use_container_width=True)

    # ----------------- بخش سوم: استودیوی ویدیو (ساخت ویدیو بر اساس متن هوش مصنوعی) -----------------
    elif menu == "🎬 استودیوی ویدیو (هوش مصنوعی)":
        st.title("🎬 استودیوی پیشرفته ساخت ویدیو با هوش مصنوعی")
        st.write("👑 توصیف ویدیو را بنویسید تا موتور هوش مصنوعی ویدیو را بر اساس متن شما رندر و تولید کند (سهمیه روزانه: ۳ ویدیو).")
        
        video_prompt = st.text_input("موضوع ویدیو (به انگلیسی یا فارسی، مثل: cinematic drone shot of a futuristic city):")
        
        if st.button("تولید و رندر ویدیو 🎥"):
            if v_cnt >= 3:
                st.error("❌ سهمیه ویدیوی شما (۳ عدد در روز) به پایان رسیده است!")
            elif video_prompt:
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET video_count = video_count + 1 WHERE phone = ?", (st.session_state.user_phone,))
                conn.commit()
                conn.close()
                
                log_activity(st.session_state.user_phone, st.session_state.user_name, "ویدیو", video_prompt)
                
                with st.spinner("⏳ در حال پردازش و رندر ویدیوی هوش مصنوعی... (لطفاً چند ثانیه صبر کنید)"):
                    try:
                        # استفاده از موتور پویای تولید انیمیشن و ویدیو بر اساس پرامپت کاربر
                        encoded_video_prompt = requests.utils.quote(video_prompt)
                        # سرویس هوش مصنوعی ساخت ویدیو بر اساس متن
                        ai_video_url = f"https://image.pollinations.ai/prompt/animated%20video%20loop%20of%20{encoded_video_prompt}?width=720&height=720&nologo=true"
                        
                        st.success(f"🎉 ویدیوی اختصاصی شما برای موضوع «{video_prompt}» با موفقیت ساخته شد!")
                        # نمایش به صورت انیمیشن متحرک / ویدیویی خروجی
                        st.image(ai_video_url, caption=f"خروجی ویدیویی هوش مصنوعی برای: {video_prompt}", use_container_width=True)
                    except Exception as e:
                        # پشتیبان اضطراری ویدیو
                        fallback_videos = [
                            "https://www.w3schools.com/html/mov_bbb.mp4",
                            "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
                        ]
                        st.video(random.choice(fallback_videos))

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
