import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="שותפים - מציאת שותפים", layout="wide")

# =========================
# STATE DB
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
def create_user(name, age, city, budget, lifestyle):
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "age": age,
        "city": city,
        "budget": budget,
        "lifestyle": lifestyle
    }

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
# SIDEBAR
# =========================
st.sidebar.title("🏠 שותפים")
menu = st.sidebar.radio("תפריט", [
    "דשבורד",
    "פרופיל חדש",
    "התאמות",
    "לוח דירות",
    "צ'אט"
])

# =========================
# DASHBOARD
# =========================
if menu == "דשבורד":

    st.title("🏠 שותפים - מערכת התאמת שותפים בישראל")

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
# CREATE USER
# =========================
elif menu == "פרופיל חדש":

    st.title("👤 יצירת פרופיל")

    name = st.text_input("שם")
    age = st.number_input("גיל", 18, 100, 25)

    city = st.selectbox("עיר", ["תל אביב", "ירושלים", "חיפה", "באר שבע"])

    budget = st.number_input("תקציב (₪)", 1000, 20000, 4000)

    lifestyle = st.multiselect("סגנון חיים", [
        "שקט",
        "חברתי",
        "נקי",
        "מעשן",
        "חיות מחמד",
        "לילות מאוחרים"
    ])

    if st.button("צור פרופיל"):

        user = create_user(name, age, city, budget, lifestyle)
        st.session_state.users.append(user)

        st.success("הפרופיל נוצר!")

# =========================
# MATCHING
# =========================
elif menu == "התאמות":

    st.title("🤝 התאמות חכמות")

    if len(st.session_state.users) < 2:
        st.warning("צריך לפחות 2 משתמשים")
    else:

        for user in st.session_state.users:

            st.subheader(f"👤 התאמות עבור {user['name']}")

            matches = []

            for other in st.session_state.users:

                if other["id"] != user["id"]:

                    score = match_score(user, other)

                    matches.append({
                        "שם": other["name"],
                        "עיר": other["city"],
                        "תקציב": other["budget"],
                        "התאמה": score
                    })

            matches = sorted(matches, key=lambda x: x["התאמה"], reverse=True)

            st.dataframe(pd.DataFrame(matches))

# =========================
# LISTINGS
# =========================
elif menu == "לוח דירות":

    st.title("🏢 לוח דירות")

    st.subheader("הוסף דירה")

    owner = st.text_input("שם בעל הדירה")
    city = st.selectbox("עיר", ["תל אביב", "ירושלים", "חיפה", "באר שבע"])
    price = st.number_input("מחיר", 1000, 30000, 5000)
    desc = st.text_area("תיאור")

    if st.button("פרסם דירה"):

        st.session_state.listings.append({
            "owner": owner,
            "city": city,
            "price": price,
            "desc": desc
        })

    st.subheader("דירות זמינות")

    if st.session_state.listings:
        st.dataframe(pd.DataFrame(st.session_state.listings))
    else:
        st.info("אין דירות עדיין")

# =========================
# CHAT
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

        if st.button("שלח"):

            st.session_state.messages.append({
                "from": sender,
                "to": receiver,
                "msg": msg,
                "time": datetime.now().strftime("%H:%M:%S")
            })

        st.subheader("הודעות")

        for m in reversed(st.session_state.messages):

            st.write(f"""
**{m['from']} → {m['to']}**  
{m['msg']}  
⏱ {m['time']}
""")
