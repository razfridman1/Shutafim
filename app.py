import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime

# =========================
# APP CONFIG
# =========================
st.set_page_config(page_title="שותפים - מציאת שותפים לדירה", layout="wide")

# =========================
# SESSION STATE
# =========================
if "users" not in st.session_state:
    st.session_state.users = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "listings" not in st.session_state:
    st.session_state.listings = []

# =========================
# HELPERS
# =========================
def match_score(u1, u2):

    score = 0

    # budget similarity
    score += max(0, 100 - abs(u1["budget"] - u2["budget"]) / 100)

    # city match
    if u1["city"] == u2["city"]:
        score += 50

    # lifestyle overlap
    score += len(set(u1["lifestyle"]).intersection(set(u2["lifestyle"]))) * 25

    return round(score, 2)

# =========================
# SIDEBAR MENU
# =========================
st.sidebar.title("🏠 שותפים")

menu = st.sidebar.radio("ניווט", [
    "דשבורד",
    "יצירת פרופיל",
    "התאמות",
    "לוח דירות",
    "צ'אט"
])

# =========================
# DASHBOARD
# =========================
if menu == "דשבורד":

    st.title("🏠 שותפים - מערכת מציאת שותפים")

    col1, col2, col3 = st.columns(3)

    col1.metric("משתמשים", len(st.session_state.users))
    col2.metric("הודעות", len(st.session_state.messages))
    col3.metric("דירות", len(st.session_state.listings))

    st.subheader("👥 משתמשים רשומים")

    if st.session_state.users:
        st.dataframe(pd.DataFrame(st.session_state.users))
    else:
        st.info("אין משתמשים עדיין")

# =========================
# CREATE USER (FINAL FIXED VERSION)
# =========================
elif menu == "יצירת פרופיל":

    st.title("👤 יצירת פרופיל משתמש")

    with st.form("user_form"):

        name = st.text_input("שם מלא")

        age = st.number_input("גיל", 18, 100, 25)

        city = st.selectbox(
            "עיר מגורים",
            ["תל אביב", "ירושלים", "חיפה", "באר שבע", "רמת גן", "הרצליה"]
        )

        budget = st.number_input("תקציב חודשי (₪)", 1000, 30000, 5000)

        lifestyle = st.multiselect(
            "סגנון חיים",
            ["שקט", "חברתי", "נקי", "מעשן", "חיות מחמד", "עובד מהבית", "לילות מאוחרים"]
        )

        submitted = st.form_submit_button("➕ צור פרופיל")

    if submitted:

        if not name:
            st.error("חובה להזין שם")
        else:

            user = {
                "id": str(uuid.uuid4()),
                "name": name,
                "age": age,
                "city": city,
                "budget": budget,
                "lifestyle": lifestyle
            }

            st.session_state.users.append(user)

            st.success(f"✅ משתמש {name} נוצר בהצלחה!")

            st.json(user)

# =========================
# MATCHING ENGINE
# =========================
elif menu == "התאמות":

    st.title("🤝 התאמות חכמות לשותפים")

    if len(st.session_state.users) < 2:
        st.warning("צריך לפחות 2 משתמשים כדי לבצע התאמות")
    else:

        for user in st.session_state.users:

            st.subheader(f"👤 התאמות עבור: {user['name']}")

            matches = []

            for other in st.session_state.users:

                if other["id"] != user["id"]:

                    score = match_score(user, other)

                    matches.append({
                        "שם": other["name"],
                        "עיר": other["city"],
                        "תקציב": other["budget"],
                        "התאמה (%)": score
                    })

            matches = sorted(matches, key=lambda x: x["התאמה (%)"], reverse=True)

            st.dataframe(pd.DataFrame(matches))

# =========================
# LISTINGS
# =========================
elif menu == "לוח דירות":

    st.title("🏢 לוח דירות ושותפים")

    st.subheader("➕ הוסף דירה")

    owner = st.text_input("שם בעל הדירה")

    city = st.selectbox(
        "עיר",
        ["תל אביב", "ירושלים", "חיפה", "באר שבע"]
    )

    price = st.number_input("מחיר (₪)", 1000, 30000, 5000)

    desc = st.text_area("תיאור הדירה")

    if st.button("פרסם דירה"):

        if owner:

            st.session_state.listings.append({
                "owner": owner,
                "city": city,
                "price": price,
                "desc": desc
            })

            st.success("הדירה פורסמה!")
        else:
            st.error("חובה להזין שם בעל הדירה")

    st.subheader("📌 דירות זמינות")

    if st.session_state.listings:
        st.dataframe(pd.DataFrame(st.session_state.listings))
    else:
        st.info("אין דירות עדיין")

# =========================
# CHAT SYSTEM
# =========================
elif menu == "צ'אט":

    st.title("💬 צ'אט פנימי")

    if len(st.session_state.users) < 2:
        st.warning("צריך לפחות 2 משתמשים")
    else:

        names = [u["name"] for u in st.session_state.users]

        sender = st.selectbox("שולח", names)
        receiver = st.selectbox("מקבל", names)

        msg = st.text_input("הודעה")

        if st.button("שלח הודעה"):

            if msg:

                st.session_state.messages.append({
                    "from": sender,
                    "to": receiver,
                    "msg": msg,
                    "time": datetime.now().strftime("%H:%M:%S")
                })

                st.success("הודעה נשלחה!")

        st.subheader("📨 הודעות")

        for m in reversed(st.session_state.messages):

            st.write(f"""
**{m['from']} → {m['to']}**  
{m['msg']}  
⏱ {m['time']}
""")
