import streamlit as st
import requests

# تنظیمات صفحه
st.set_page_config(page_title="ربات هوش مصنوعی من", page_icon="🤖", layout="centered")

# مدیریت وضعیت سهمیه‌ها و نشست‌ها
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "text_count" not in st.session_state:
    st.session_state.text_count = 0
if "image_count" not in st.session_state:
    st.session_state.image_count = 0
if "video_count" not in st.session_state:
    st.session_state.video_count = 0

# منوی ناوبری با ایموجی و اصطلاحات خودمانی
menu = st.selectbox(
    "منوی اصلی سایت 👇",
    ["💬 چت هوشمند", "🎨 تولید تصویر", "🎬 استودیوی ویدیو (اشتراکی)", "🔑 بخش ادمین / ویژه"]
)

# ----------------- بخش اول: چت هوشمند -----------------
if menu == "💬 چت هوشمند":
    st.title("💬 چت با هوش مصنوعی رفاقتی")
    st.write("😎 هر سوالی داری بپرس، باهوش، سریع و پر از ایموجی جواب میده!")
    
    user_prompt = st.text_input("پیام خود را بنویسید...")
    
    if st.button("ارسال پیام 🚀"):
        if st.session_state.text_count >= 40:
            st.error("❌ سهمیه متن رایگان امروزت تموم شده! برای استفاده بیشتر به بخش اشتراک مراجعه کن.")
        elif user_prompt:
            st.session_state.text_count += 1
            st.write(f"سالم: {user_prompt}")
            try:
                # استفاده از مدل پایدار و صحیح گروک
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
                    st.error("خطا در پاسخ‌دهی هوش مصنوعی. لطفاً دوباره تلاش کن.")
            except Exception as e:
                st.error(f"خطا در ارتباط با سرور: {e}")

# ----------------- بخش دوم: تولید تصویر -----------------
elif menu == "🎨 تولید تصویر":
    st.title("🎨 بخش تولید تصویر هوش مصنوعی")
    st.write("🖼️ متن خود را وارد کنید تا تصویر دلخواهتان ساخته شود.")
    
    img_prompt = st.text_input("توضیح تصویر به انگلیسی یا فارسی:")
    
    if st.button("بساز 🎨"):
        if st.session_state.image_count >= 10:
            st.error("❌ سهمیه تصویر رایگان امروزت تموم شده (سقف ۱۰ عدد)!")
        elif img_prompt:
            st.session_state.image_count += 1
            st.success("✨ تصویر شما با موفقیت آماده شد!")
            # استفاده از سرویس رایگان و پایدار تولید تصویر بر اساس پرامپت
            safe_prompt = requests.utils.quote(img_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}"
            st.image(image_url, caption=f"پرامپت شما: {img_prompt}")

# ----------------- بخش سوم: استودیوی ویدیو -----------------
elif menu == "🎬 استودیوی ویدیو (اشتراکی)":
    st.title("🎬 استودیوی پیشرفته تولید ویدیو")
    st.write("👑 این بخش مخصوص کاربران ویژه است (سهمیه روزانه: ۳ ویدیو).")
    
    video_prompt = st.text_input("موضوع ویدیو را وارد کنید:")
    
    if st.button("تولید ویدیو 🎥"):
        if st.session_state.video_count >= 3:
            st.error("❌ سهمیه ویدیوی شما (۳ عدد در روز) به پایان رسیده است!")
        elif video_prompt:
            st.session_state.video_count += 1
            st.info("⏳ درخواست ویدیوی شما ثبت شد و در صف پردازش قرار گرفت!")

# ----------------- بخش چهارم: ادمین و خرید اشتراک -----------------
elif menu == "🔑 بخش ادمین / ویژه":
    st.title("🔑 ورود به بخش مدیریت و خرید اشتراک")
    
    tab1, tab2 = st.tabs(["مدیریت (ادمین)", "خرید اشتراک (کارت به کارت)"])
    
    with tab1:
        admin_pass = st.text_input("رمز عبور ادمین را وارد کنید:", type="password")
        if st.button("ورود به پنل مدیریت 🔐"):
            if admin_pass == "2345":
                st.session_state.admin_logged = True
                st.success("✅ با موفقیت وارد پنل ادمین شدی!")
            else:
                st.error("❌ رمز عبور اشتباه است!")
                
        if st.session_state.admin_logged:
            st.subheader("📊 آمار مصرف کاربران:")
            st.write(f"تعداد درخواست‌های متن امروز: {st.session_state.text_count} از ۴۰")
            st.write(f"تعداد درخواست‌های تصویر امروز: {st.session_state.image_count} از ۱۰")
            st.write(f"تعداد درخواست‌های ویدیو امروز: {st.session_state.video_count} از ۳")
            
            if st.button("ریست کردن سهمیه‌ها 🔄"):
                st.session_state.text_count = 0
                st.session_state.image_count = 0
                st.session_state.video_count = 0
                st.success("سهمیه‌ها با موفقیت ریست شدند!")

    with tab2:
        st.subheader("💳 ارتقای حساب کاربری")
        st.write("برای خرید اشتراک و دسترسی نامحدود، مبلغ را به شماره کارت زیر واریز کنید:")
        st.code("6037991241576150", language="text")
        st.write("پس از واریز، فیش واریزی را به پشتیبانی بفرستید تا اکانت شما ویژه شود.")
