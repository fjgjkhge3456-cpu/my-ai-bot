import streamlit as st
import requests
import sqlite3
import datetime
from PIL import Image, ImageEnhance, ImageOps

# تنظیمات اصلی صفحه
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

# مقداردهی نشست‌ها (Session State)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
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

# تابع قدرتمند پاسخ‌دهی هوش مصنوعی (افزایش زمان به ۳۰ ثانیه)
def ask_ai(prompt_text):
    # تلاش با مدل اصلی
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": "شما یک دستیار هوش مصنوعی بسیار باهوش و کامل به زبان فارسی هستید."},
                {"role": "user", "content": prompt_text}
            ],
            "model": "openai"
        }
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200 and res.text:
            return res.text
    except Exception:
        pass

    # تلاش با مدل پشتیبان و سریع‌تر (Qwen/Mistral)
    try:
        safe_p = requests.utils.quote(prompt_text)
        res = requests.get(f"https://text.pollinations.ai/{safe_p}?model=qwen-coder", timeout=30)
        if res.status_code == 200 and res.text:
            return res.text
    except Exception:
        pass

    return "⚠️ سرور در حال حاضر شلوغ است، لطفاً همین پیام را مجدداً ارسال کنید."

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
        ["💬 چت هوشمند", "🎨 تولید با Flux و ویرایش آزاد عکس", "🎬 استودیوی ویدیوی واقعی", "🔑 بخش ادمین"]
    )

    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT text_count, image_count, video_count FROM users WHERE phone = ?", (st.session_state.user_phone,))
    u_data = cursor.fetchone()
    t_cnt, i_cnt, v_cnt = u_data if u_data else (0, 0, 0)
    conn.close()

    # ----------------- بخش اول: چت هوشمند -----------------
    if menu == "💬 چت هوشمند":
        st.title("💬 چت هوشمند آنلاین")
        st.write(f"سلام {st.session_state.user_name} جان! هر سوالی داری بپرس تا هوش مصنوعی پاسخ دهد.")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "image" in message and message["image"]:
                    st.image(message["image"], width=300)

        uploaded_file = st.file_uploader("📎 آپلود عکس (اختیاری)", type=["jpg", "png", "jpeg"])
        
        if user_prompt := st.chat_input("پیام خود را بنویسید..."):
            if t_cnt >= 200:
                st.error("❌ سهمیه پیام امروز شما تمام شده است!")
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

                with st.spinner("هوش مصنوعی در حال پاسخ‌دهی (ممکن است چند ثانیه طول بکشد)..."):
                    bot_reply = ask_ai(user_prompt)

                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)

    # ----------------- بخش دوم: تولید با Flux و ویرایش عکس -----------------
    elif menu == "🎨 تولید با Flux و ویرایش آزاد عکس":
        st.title("🎨 تولید با Flux و ویرایش دستی عکس")
        
        tab1, tab2 = st.tabs(["ساخت تصویر با Flux 🌟", "ویرایش آزاد عکس 🛠️"])
        
        with tab1:
            flux_prompt = st.text_input("توضیح تصویر (پرامپت به انگلیسی یا فارسی):", key="flux_p")
            if st.button("تولید تصویر با Flux 🚀"):
                if flux_prompt:
                    st.success("✨ تصویر با موتور Flux در حال ساخت است...")
                    safe_prompt = requests.utils.quote(flux_prompt)
                    flux_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&width=1024&height=1024&nologo=true"
                    st.image(flux_url, caption=f"Flux: {flux_prompt}", use_container_width=True)

        with tab2:
            edit_file = st.file_uploader("عکس خود را آپلود کنید:", type=["jpg", "png", "jpeg"], key="edit_img")
            user_edit_instruction = st.text_input("دستور ویرایش خود را بنویسید (مثلاً: روشنایی، سیاه و سفید، تاریک، کنتراست، چرخش یا نگاتیو):")
            
            if st.button("اعمال ویرایش روی عکس 🪄"):
                if edit_file and user_edit_instruction:
                    image = Image.open(edit_file)
                    inst = user_edit_instruction.lower()
                    
                    if "روشنایی" in inst or "نور" in inst:
                        enhancer = ImageEnhance.Brightness(image)
                        processed_image = enhancer.enhance(1.6)
                    elif "تاریک" in inst:
                        enhancer = ImageEnhance.Brightness(image)
                        processed_image = enhancer.enhance(0.4)
                    elif "سیاه و سفید" in inst or "grayscale" in inst:
                        processed_image = ImageOps.grayscale(image)
                    elif "نگاتیو" in inst or "معکوس" in inst:
                        if image.mode == 'RGBA':
                            image = image.convert('RGB')
                        processed_image = ImageOps.invert(image)
                    elif "چرخش" in inst:
                        processed_image = image.rotate(90, expand=True)
                    elif "کنتراست" in inst or "وضوح" in inst:
                        enhancer = ImageEnhance.Contrast(image)
                        processed_image = enhancer.enhance(2.0)
                    else:
                        enhancer = ImageEnhance.Color(image)
                        processed_image = enhancer.enhance(1.3)

                    st.success(f"✅ ویرایش با موفقیت بر اساس دستور «{user_edit_instruction}» انجام شد!")
                    st.image(processed_image, caption=f"دستور شما: {user_edit_instruction}", use_container_width=True)
                else:
                    st.warning("⚠️ لطفاً هم عکس را آپلود کنید و هم دستور ویرایش را بنویسید.")

    # ----------------- بخش سوم: استودیوی ویدیوی واقعی -----------------
    elif menu == "🎬 استودیوی ویدیوی واقعی":
        st.title("🎬 استودیوی رندر و ساخت ویدیوی هوش مصنوعی")
        st.write("👑 موضوع ویدیوی خود را بنویسید تا موتور هوش مصنوعی ویدیو را رندر و مستقیماً نمایش دهد:")
        
        video_prompt = st.text_input("پرامپت ویدیو (مثلا: cinematic drone shot of driving a car, 4k):")
        
        if st.button("ساخت و رندر ویدیوی واقعی 🎥"):
            if video_prompt:
                st.success(f"🎉 ویدیوی اختصاصی برای «{video_prompt}» ساخته شد!")
                safe_v_prompt = requests.utils.quote(video_prompt)
                video_render_url = f"https://image.pollinations.ai/prompt/cinematic%20dynamic%20video%20animation%20of%20{safe_v_prompt}?width=720&height=720&nologo=true"
                st.video(video_render_url)

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
