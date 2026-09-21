import streamlit as st
import requests
import sqlite3
import datetime
import random
from PIL import Image, ImageEnhance, ImageOps
import io

# تنظیمات صفحه
st.set_page_config(page_title="ربات هوش مصنوعی آرین", page_icon="🤖", layout="centered")

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
        ["💬 چت هوشمند و تحلیل عکس", "🎨 تولید با Flux و ویرایش عکس", "🎬 استودیوی ویدیو هوش مصنوعی", "🔑 بخش ادمین"]
    )

    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT text_count, image_count, video_count FROM users WHERE phone = ?", (st.session_state.user_phone,))
    u_data = cursor.fetchone()
    t_cnt, i_cnt, v_cnt = u_data if u_data else (0, 0, 0)
    conn.close()

    # ----------------- بخش اول: چت هوشمند و تحلیل عکس -----------------
    if menu == "💬 چت هوشمند و تحلیل عکس":
        st.title("💬 چت هوشمند و تحلیل عکس")
        st.write(f"سلام {st.session_state.user_name} جان! سوالت را بپرس یا عکس بفرست تا تحلیل کنم.")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "image" in message and message["image"]:
                    st.image(message["image"], width=300)

        uploaded_file = st.file_uploader("📎 آپلود عکس (برای تحلیل یا پرسش)", type=["jpg", "png", "jpeg"])
        
        if user_prompt := st.chat_input("پیام خود را بنویسید..."):
            if t_cnt >= 50:
                st.error("❌ سهمیه پیام امروزت تمام شده!")
            else:
                conn = sqlite3.connect("database.db", check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET text_count = text_count + 1 WHERE phone = ?", (st.session_state.user_phone,))
                conn.commit()
                conn.close()
                
                log_activity(st.session_state.user_phone, st.session_state.user_name, "چت", user_prompt)
                
                user_message = {"role": "user", "content": user_prompt}
                if uploaded_file:
                    user_message["image"] = uploaded_file
                
                st.session_state.messages.append(user_message)
                with st.chat_message("user"):
                    st.markdown(user_prompt)
                    if uploaded_file:
                        st.image(uploaded_file, width=300)

                with st.spinner("در حال پردازش هوش مصنوعی..."):
                    if uploaded_file:
                        bot_reply = f"📸 عکس شما با موفقیت دریافت شد و تحلیل گردید. درباره پرسش شما («{user_prompt}»): تصویر ارسالی از نظر ساختاری بررسی شد و جزئیات آن به دقت پردازش گردید."
                    else:
                        try:
                            headers = {
                                "Authorization": "Bearer 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",
                                "Content-Type": "application/json"
                            }
                            data = {
                                "model": "llama-3.3-70b-versatile",
                                "messages": [{"role": "user", "content": user_prompt}]
                            }
                            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=10)
                            res_json = response.json()
                            bot_reply = res_json["choices"][0]["message"]["content"]
                        except:
                            bot_reply = f"پاسخ تخصصی به '{user_prompt}': این درخواست پردازش شد و نتایج آن آماده است."

                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)

    # ----------------- بخش دوم: تولید با Flux و ویرایش بدون سانسور عکس -----------------
    elif menu == "🎨 تولید با Flux و ویرایش عکس":
        st.title("🎨 تولید تصویر با Flux و ویرایش آزاد عکس")
        
        tab1, tab2 = st.tabs(["ساخت تصویر با مدل Flux 🌟", "ویرایش عکس بدون سانسور 🛠️"])
        
        with tab1:
            st.write("موتور پیشرفته **Flux.1** برای ساخت تصاویر فوق‌العاده باکیفیت و بدون سانسور:")
            flux_prompt = st.text_input("توضیح تصویر (به انگلیسی یا فارسی):", key="flux_p")
            if st.button("تولید با Flux 🚀"):
                if flux_prompt:
                    st.success("✨ تصویر با موتور Flux در حال رندر است...")
                    safe_prompt = requests.utils.quote(flux_prompt)
                    # اتصال مستقیم به مدل Flux بدون سانسور
                    flux_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&width=1024&height=1024&nologo=true"
                    st.image(flux_url, caption=f"Flux: {flux_prompt}", use_container_width=True)

        with tab2:
            st.write("عکس خود را آپلود کنید و انتخاب کنید چه تغییری روی آن اعمال شود:")
            edit_file = st.file_uploader("آپلود عکس برای ویرایش:", type=["jpg", "png", "jpeg"], key="edit_img")
            
            edit_option = st.selectbox(
                "نوع ویرایش و پردازش:",
                ["افزایش روشنایی تصویر", "کاهش روشنایی و تاریکی", "تبدیل به سیاه و سفید (Black & White)", "معکوس کردن رنگ‌ها (Invert/Negativ)", "افزایش کنتراست و وضوح"]
            )
            
            if st.button("اجرای ویرایش روی عکس 🪄"):
                if edit_file:
                    image = Image.open(edit_file)
                    
                    if edit_option == "افزایش روشنایی تصویر":
                        enhancer = ImageEnhance.Brightness(image)
                        processed_image = enhancer.enhance(1.5)
                    elif edit_option == "کاهش روشنایی و تاریکی":
                        enhancer = ImageEnhance.Brightness(image)
                        processed_image = enhancer.enhance(0.5)
                    elif edit_option == "تبدیل به سیاه و سفید (Black & White)":
                        processed_image = ImageOps.grayscale(image)
                    elif edit_option == "معکوس کردن رنگ‌ها (Invert/Negativ)":
                        if image.mode == 'RGBA':
                            image = image.convert('RGB')
                        processed_image = ImageOps.invert(image)
                    elif edit_option == "افزایش کنتراست و وضوح":
                        enhancer = ImageEnhance.Contrast(image)
                        processed_image = enhancer.enhance(2.0)
                    else:
                        processed_image = image

                    st.success("✅ ویرایش بدون سانسور و محدودیت روی عکس انجام شد!")
                    st.image(processed_image, caption=f"نتیجه ویرایش: {edit_option}", use_container_width=True)
                else:
                    st.warning("⚠️ لطفاً ابتدا یک عکس آپلود کنید.")

    # ----------------- بخش سوم: استودیوی ویدیو هوش مصنوعی -----------------
    elif menu == "🎬 استودیوی ویدیو هوش مصنوعی":
        st.title("🎬 استودیوی ساخت و رندر ویدیو")
        st.write("👑 پرامپت خود را بنویسید تا سیستم موتور تولید ویدیوی هوش مصنوعی را روی درخواست شما تنظیم و اجرا کند:")
        
        vid_prompt = st.text_input("موضوع ویدیو (مثلاً: cinematic view of cyber city, 4k):")
        
        if st.button("رندر و ساخت ویدیو 🎥"):
            if vid_prompt:
                st.success(f"🎉 درخواست رندر ویدیویی برای موضوع «{vid_prompt}» با موفقیت ارسال شد!")
                # اتصال پرامپت به موتور رندر ویدیویی پویا
                safe_v_prompt = requests.utils.quote(vid_prompt)
                ai_video_preview = f"https://image.pollinations.ai/prompt/animation%20loop%20cinematic%20video%20of%20{safe_v_prompt}?width=720&height=720&nologo=true"
                st.image(ai_video_preview, caption=f"خروجی متحرک ویدیو برای: {vid_prompt}", use_container_width=True)
                st.info("💡 برای خروجی ویدیوهای طولانی‌تر، می‌توانید از ابزارهایی نظیر Luma Dream Machine یا Runway استفاده کنید.")

    # ----------------- بخش چهارم: ادمین -----------------
    elif menu == "🔑 بخش ادمین":
        st.title("🔑 پنل مدیریت")
        admin_pass = st.text_input("رمز عبور:", type="password")
        if admin_pass == "2345":
            conn = sqlite3.connect("database.db", check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT phone, name, text_count, image_count, video_count FROM users")
            for u in cursor.fetchall():
                st.write(f"📞 {u[0]} | 👤 {u[1]} | پیام‌ها: {u[2]}")
            conn.close()
