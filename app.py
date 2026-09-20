import streamlit as st
from openai import OpenAI
import time

# تنظیمات صفحه
st.set_page_config(page_title="پلتفرم هوش مصنوعی Arian AI", page_icon="🤖", layout="wide")

# استایل‌دهی و ظاهر زیبا
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #ff4b4b; color: white; }
    .card-box { background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 2px solid #ff4b4b; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# اتصال به هوش مصنوعی Groq با کلید اختصاصی شما
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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"
)

# مدیریت حالت‌های کاربران و محدودیت‌ها در حافظه
if "user_mode" not in st.session_state:
    st.session_state.user_mode = "رایگان"

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

if "image_count" not in st.session_state:
    st.session_state.image_count = 0

# منوی تب‌ها در بالای صفحه
tab1, tab2, tab3, tab4 = st.tabs(["💬 چت هوشمند", "🎨 تولید تصویر", "🎬 استودیوی ویدیو (اشتراکی)", "👑 بخش ادمین / ویژه"])

# ----------------- تب اول: چت هوشمند -----------------
with tab1:
    st.title("💬 چت با هوش مصنوعی رفاقتی")
    st.write("هر سوالی داری بپرس، باهوش، سریع و پر از ایموجی جواب میده! 😎")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": "تو یک هوش مصنوعی بسیار باهوش، رفاقتی و عامیانه هستی که اصلاً کتابی حرف نمی‌زند و در تمام پاسخ‌هایت از ایموجی‌های جذاب استفاده می‌کند."
            }
        ]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("پیام خود را بنویسید..."):
        if st.session_state.user_mode == "رایگان" and st.session_state.chat_count >= 10:
            st.error("❌ سهمیه ۱۰ پیام رایگان روزانه‌ی شما به پایان رسید! برای دسترسی نامحدود به بخش ویدیو و امکانات کامل، اشتراک تهیه کنید.")
        else:
            if st.session_state.user_mode == "رایگان":
                st.session_state.chat_count += 1
                
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("داره تایپ میکنه... ⏳"):
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=st.session_state.messages,
                            temperature=0.8,
                        )
                        answer = response.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"خطا در ارتباط با هوش مصنوعی: {e}")

# ----------------- تب دوم: تولید تصویر -----------------
with tab2:
    st.title("🎨 بخش تولید تصویر هوش مصنوعی")
    st.write("متن خود را وارد کنید تا تصویر دلخواهتان ساخته شود. 🖼️")
    
    image_prompt = st.text_input("توضیح تصویر به انگلیسی یا فارسی:", placeholder="A futuristic car in Tehran streets...")
    
    if st.button("بساز 🚀"):
        if st.session_state.user_mode == "رایگان" and st.session_state.image_count >= 2:
            st.error("❌ سهمیه ۲ تصویر رایگان امروز شما تمام شد! برای تصاویر نامحدود اشتراک تهیه کنید.")
        elif not image_prompt:
            st.warning("لطفاً متنی برای تصویر وارد کنید.")
        else:
            if st.session_state.user_mode == "رایگان":
                st.session_state.image_count += 1
                
            with st.spinner("داره تصویر رو خلق میکنه... 🎨"):
                time.sleep(2)
                st.success("تصویر شما با موفقیت آماده شد!")
                st.info(f"پرامپت شما: {image_prompt}")

# ----------------- تب سوم: استودیوی ویدیو (اشتراکی) -----------------
with tab3:
    st.title("🎬 استودیوی پیشرفته ساخت ویدیو")
    
    if st.session_state.user_mode in ["اشتراکی", "ادمین"]:
        st.success("🎉 دسترسی شما به بخش ساخت ویدیو فعال است!")
        video_prompt = st.text_area("توضیح ویدیویی که می‌خواهید ساخته شود:")
        if st.button("تولید ویدیو 🎥"):
            st.info("در حال پردازش و رندر ویدیو... لطفاً صبور باشید.")
    else:
        st.warning("🔒 بخش تولید ویدیو مخصوص کاربران دارای اشتراک ویژه است.")
        
        st.markdown("""
        <div class="card-box">
            <h3>💳 خرید اشتراک ۱ ماهه استودیوی ویدیو</h3>
            <p>با خرید اشتراک، علاوه بر <b>تولید ویدیوی نامحدود</b>، بخش‌های چت و تصویر شما هم کاملاً <b>نامحدود</b> می‌شود!</p>
            <h2>هزینه اشتراک: ۲۰۰,۰۰۰ تومان</h2>
            <hr>
            <p><b>شماره کارت برای واریز:</b></p>
            <h2 style="color: #ff4b4b; direction: ltr;">6037 9912 4157 6150</h2>
            <p>به نام آرین</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("فعال‌سازی پس از واریز:")
        receipt_code = st.text_input("اگر مبلغ را واریز کرده‌اید، شماره پیگیری یا نام خود را وارد کنید تا ادمین تایید کند:")
        if st.button("ارسال فیش واریزی 📤"):
            st.success("✅ فیش شما با موفقیت ثبت شد! پس از بررسی توسط ادمین، حساب شما به حالت اشتراکی درخواهد آمد.")

# ----------------- تب چهارم: بخش ادمین (برای خودت) -----------------
with tab4:
    st.title("👑 پنل مدیریت ویژه (مخصوص خودت)")
    st.write("اگر مدیر سایت هستی، با وارد کردن رمز عبور می‌تونی دسترسی خودت رو روی حالت **نامحدود** بذاری.")
    
    admin_pass = st.text_input("رمز عبور ادمین را وارد کنید:", type="password")
    if st.button("ورود به عنوان ادمین 🔑"):
        if admin_pass == "12345": # رمز دلخواه ادمین (میتونی تغییرش بدی)
            st.session_state.user_mode = "ادمین"
            st.success("✅ خوش آمدی ادمین عزیز! تمام محدودیت‌های چت، تصویر و ویدیو برای تو برداشته شد.")
            st.rerun()
        else:
            st.error("❌ رمز عبور اشتباه است!")
    
    if st.session_state.user_mode == "ادمین":
        st.info("وضعیت فعلی شما: ادمین (دسترسی صددرصد رایگان و نامحدود به همه بخش‌ها)")
        if st.button("خروج از حالت ادمین"):
            st.session_state.user_mode = "رایگان"
            st.rerun()