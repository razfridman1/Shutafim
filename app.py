import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import urllib.parse

st.set_page_config(page_title="הבית שלנו", layout="wide")

# =========================
# STYLE (APPLE-LIKE UI)
# =========================
st.markdown("""
<style>
.main {
    background-color: #F5F5F7;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}
.big-number {
    font-size: 28px;
    font-weight: bold;
    color: #007AFF;
}
</style>
""", unsafe_allow_html=True)

# =========================
# STATE
# =========================
if "users" not in st.session_state:
    st.session_state.users = []

if "fixed" not in st.session_state:
    st.session_state.fixed = []

if "var" not in st.session_state:
    st.session_state.var = []

# =========================
# HELPERS
# =========================
def total_fixed():
    return sum(x["amount"] for x in st.session_state.fixed)

def total_var():
    return sum(x["amount"] for x in st.session_state.var)

def calculate_balances():
    balances = {u["name"]: 0 for u in st.session_state.users}

    if not balances:
        return balances

    # fixed split
    per = total_fixed() / len(balances)
    for k in balances:
        balances[k] -= per

    # variable
    for e in st.session_state.var:
        split = e["amount"] / len(e["participants"])
        for p in e["participants"]:
            balances[p] -= split
        balances[e["paid_by"]] += e["amount"]

    return balances

def debts_table(balances):
    creditors = []
    debtors = []

    for name, val in balances.items():
        if val > 0:
            creditors.append([name, val])
        elif val < 0:
            debtors.append([name, -val])

    result = []

    for d_name, d_val in debtors:
        for c in creditors:
            if d_val == 0:
                break
            c_name, c_val = c
            pay = min(d_val, c_val)
            if pay > 0:
                result.append({
                    "חייב": d_name,
                    "למי": c_name,
                    "סכום": round(pay,2)
                })
                d_val -= pay
                c[1] -= pay

    return pd.DataFrame(result)

def whatsapp_link(text):
    encoded = urllib.parse.quote(text)
    return f"https://wa.me/?text={encoded}"

# =========================
# MENU
# =========================
st.sidebar.title("🏠 הבית שלנו")

menu = st.sidebar.radio("ניווט", [
    "📊 דשבורד",
    "👥 שותפים",
    "🧾 הוצאות קבועות",
    "🔄 הוצאות משתנות"
])

# =========================
# DASHBOARD
# =========================
if menu == "📊 דשבורד":

    st.title("📊 מצב הדירה")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<div class='card'><div>שותפים</div><div class='big-number'>{len(st.session_state.users)}</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='card'><div>קבוע</div><div class='big-number'>{total_fixed()}</div></div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<div class='card'><div>משתנה</div><div class='big-number'>{total_var()}</div></div>", unsafe_allow_html=True)

    st.divider()

    balances = calculate_balances()

    st.subheader("💰 יתרות")

    df = pd.DataFrame([
        {"שותף": k, "יתרה": round(v,2)}
        for k,v in balances.items()
    ])

    st.dataframe(df)

    st.subheader("⚖️ מי חייב למי")

    debt_df = debts_table(balances)

    if not debt_df.empty:
        st.dataframe(debt_df)

        # WhatsApp share
        text = "חובות בדירה:\n"
        for _, row in debt_df.iterrows():
            text += f"{row['חייב']} חייב ל{row['למי']} {row['סכום']}₪\n"

        link = whatsapp_link(text)

        st.markdown(f"[📲 שתף ב-WhatsApp]({link})")

    else:
        st.success("אין חובות 🎉")

# =========================
# USERS
# =========================
elif menu == "👥 שותפים":

    st.title("👥 ניהול שותפים")

    with st.form("add"):
        name = st.text_input("שם")
        add = st.form_submit_button("➕ הוסף")

    if add and name:
        st.session_state.users.append({"id": str(uuid.uuid4()), "name": name})

    st.subheader("רשימה")

    for i, u in enumerate(st.session_state.users):
        col1, col2 = st.columns([3,1])

        new = col1.text_input("שם", value=u["name"], key=u["id"])

        if col2.button("🗑", key="d"+u["id"]):
            st.session_state.users.pop(i)
            st.rerun()

        u["name"] = new

# =========================
# FIXED
# =========================
elif menu == "🧾 הוצאות קבועות":

    st.title("🧾 הוצאות קבועות")

    with st.form("fixed"):
        name = st.text_input("שם")
        amount = st.number_input("סכום", 0, 50000, 5000)
        add = st.form_submit_button("הוסף")

    if add:
        st.session_state.fixed.append({"name": name, "amount": amount})

    st.dataframe(pd.DataFrame(st.session_state.fixed))

# =========================
# VARIABLE
# =========================
elif menu == "🔄 הוצאות משתנות":

    st.title("🔄 הוצאות משתנות")

    names = [u["name"] for u in st.session_state.users]

    if not names:
        st.warning("אין שותפים")
    else:

        with st.form("var"):
            desc = st.text_input("תיאור")
            amount = st.number_input("סכום", 0, 20000, 100)
            payer = st.selectbox("מי שילם", names)
            parts = st.multiselect("משתתפים", names, default=names)
            add = st.form_submit_button("הוסף")

        if add:
            st.session_state.var.append({
                "desc": desc,
                "amount": amount,
                "paid_by": payer,
                "participants": parts,
                "date": datetime.now()
            })

    st.dataframe(pd.DataFrame(st.session_state.var))
