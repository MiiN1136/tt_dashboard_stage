import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import time

# ==========================================
# CONFIGURATION & GLOBAL INITIALIZATION
# ==========================================
st.set_page_config(page_title="TT Healthcare Intelligence", layout="wide")
BASE_URL = "https://tt-backend-ieay.onrender.com"
#BASE_URL = "http://localhost:8000"
yes_no = ["No", "Yes"]

def to_binary(x):
    return 1 if x == "Yes" else 0

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.matricule = None


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #f8fafc;
        --card-bg: rgba(255, 255, 255, 0.85);
        --border: rgba(99, 102, 241, 0.12);
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --accent: #6366f1;
        --accent-glow: rgba(99, 102, 241, 0.15);
        --cyan: #38bdf8;
        --green: #10b981;
        --amber: #f59e0b;
        --red: #ef4444;
        --radius: 20px;
        --shadow: 0 8px 30px rgba(15, 23, 42, 0.06), 0 2px 6px rgba(15, 23, 42, 0.03);
        --shadow-hover: 0 16px 40px rgba(99, 102, 241, 0.12), 0 6px 14px rgba(15, 23, 42, 0.05);
        --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stApp {
        background-color: var(--bg);
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
        animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ---------- CARDS / CONTAINERS ---------- */
    div[data-testid="stContainer"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.75rem !important;
        box-shadow: var(--shadow) !important;
        transition: var(--transition) !important;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(8px);
    }
    div[data-testid="stContainer"]:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-hover) !important;
        border-color: rgba(99, 102, 241, 0.25) !important;
    }

    /* ---------- HERO BANNER (light futuristic) ---------- */
    .hero-banner {
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        color: var(--text-primary);
        padding: 2.5rem 3rem;
        border-radius: var(--radius);
        box-shadow: 0 15px 35px -10px rgba(99, 102, 241, 0.15);
        margin-bottom: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
        position: relative;
        overflow: hidden;
        transition: var(--transition);
    }
    .hero-banner:hover {
        box-shadow: 0 20px 45px -10px rgba(99, 102, 241, 0.25);
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.12), transparent 50%);
        pointer-events: none;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        color: #475569;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    .hero-kicker {
        color: #6366f1;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.5rem;
    }

    /* ---------- METRICS (Streamlit native) ---------- */
    div[data-testid="stMetric"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        padding: 1.5rem 1.5rem !important;
        border-radius: 16px !important;
        box-shadow: var(--shadow) !important;
        transition: var(--transition) !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(99, 102, 241, 0.4) !important;
        box-shadow: var(--shadow-hover) !important;
        transform: translateY(-3px);
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ---------- ENTERPRISE TABLE (light header, sticky) ---------- */
    .enterprise-table-container {
        width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        margin-bottom: 0.5rem !important;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        box-shadow: var(--shadow);
        margin-top: 1rem;
    }
    .enterprise-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        color: #1e293b;
        text-align: left;
        margin-bottom: 0 !important;
    }
    .enterprise-table th {
        background: linear-gradient(180deg, #eef2ff 0%, #e0e7ff 100%);
        color: #1e293b;
        padding: 14px 20px;
        font-weight: 600;
        letter-spacing: 0.03em;
        border-bottom: 2px solid #c7d2fe;
        text-transform: uppercase;
        font-size: 0.75rem;
        white-space: nowrap;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .enterprise-table td {
        padding: 14px 20px;
        border-bottom: 1px solid #f1f5f9;
        transition: background 0.15s ease;
        white-space: nowrap;
    }
    .enterprise-table tr:hover td {
        background-color: #f8fafc;
    }
    .enterprise-table tr:nth-child(even) td {
        background-color: #fafbfc;
    }

    .stFormSubmitButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    color: white !important;
    }

    /* ---------- STATUS BADGES (pulse animation) ---------- */
    .badge-reimbursed, .badge-pending, .badge-rejected {
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .badge-reimbursed {
        background-color: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .badge-pending {
        background-color: #fffbeb;
        color: #d97706;
        border: 1px solid #fde68a;
    }
    .badge-rejected {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }
    
    .badge-reimbursed::before, .badge-pending::before, .badge-rejected::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
    .badge-reimbursed::before { background-color: #10b981; }
    .badge-pending::before { background-color: #f59e0b; }
    .badge-rejected::before { background-color: #ef4444; }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }

    /* ---------- SIDEBAR (light, minimal) ---------- */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 12px;
        transition: var(--transition);
        border: 1px solid #e2e8f0;
        background: #ffffff;
        color: #334155;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #eef2ff;
        border-color: #6366f1;
        color: #4338ca;
    }

    /* ---------- AI ACCENT (subtle floating orb) ---------- */
    .ai-orb {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #38bdf8);
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.6);
        animation: float 2.5s ease-in-out infinite;
        margin-right: 0.6rem;
    }
    @keyframes float {
        0% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
        100% { transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# AUTHENTICATION GATE (LOGIN / SIGN UP)
# ==========================================
# Initialize navigation state if missing
if "current_page" not in st.session_state:
    st.session_state.current_page = "Login"

if not st.session_state.authenticated:
    
    # ====================================================
    # SIGN-UP / SET PASSWORD PAGE
    # ====================================================
    if st.session_state.current_page == "Set Password":
        _, col_center, _ = st.columns([1, 1.1, 1])
        
        with col_center:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; padding: 0.75rem 0 1rem 0;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: #eff6ff; border-radius: 14px; margin-bottom: 0.75rem; color: #2563eb; font-size: 1.4rem; box-shadow: inset 0 2px 4px rgba(59, 130, 246, 0.1);">
                            ✨
                        </div>
                        <h2 style="color: #0f172a; margin: 0; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.025em;">Employee Sign-Up</h2>
                        <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.35rem; font-weight: 400;">Register your corporate ID and verify via email.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                default_matricule = st.session_state.get("temp_matricule", "")
                
                with st.form("signup_form"):
                    matricule_input = st.text_input("Employee Matricule / ID", value=default_matricule, placeholder="Your ID")
                    email_input = st.text_input("Corporate Email", placeholder="name@company.com")
                    new_pw = st.text_input("New Password", type="password", placeholder="••••••••")
                    confirm_pw = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                    
                    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                    submit_btn = st.form_submit_button("Send Verification Code", use_container_width=True, type="primary")
                    
                    if submit_btn:
                        if not matricule_input or not email_input or not new_pw:
                            st.error("⚠️ All fields are required.")
                        elif "@" not in email_input:
                            st.error("❌ Invalid email format.")
                        elif new_pw != confirm_pw:
                            st.error("❌ Passwords do not match.")
                        else:
                            try:
                                res = requests.post(f"{BASE_URL}/api/signup", json={
                                    "matricule": matricule_input,
                                    "email": email_input,
                                    "password": new_pw
                                })
                                if res.status_code == 200:
                                    st.session_state.temp_matricule = matricule_input
                                    st.session_state.current_page = "Verify OTP"
                                    st.success("Verification code dispatched to your email!")
                                    st.rerun()
                                else:
                                    st.error(f"⚠️ {res.json().get('detail', 'Registration failed.')}")
                            except Exception as e:
                                st.error(f"Connection Error: {e}")
                                
                st.markdown("<div style='margin: 0.75rem 0; border-top: 1px solid #f1f5f9;'></div>", unsafe_allow_html=True)
                if st.button("← Return to Login Portal", type="secondary", use_container_width=True, key="return_login_btn"):
                    st.session_state.current_page = "Login"
                    st.rerun()

    # ====================================================
    # FORGOT PASSWORD REQUEST PAGE
    # ====================================================
    elif st.session_state.current_page == "Forgot Password":
        _, col_center, _ = st.columns([1, 0.85, 1])
        
        with col_center:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; padding: 0.75rem 0 1rem 0;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: #eff6ff; border-radius: 14px; margin-bottom: 0.75rem; color: #2563eb; font-size: 1.4rem; box-shadow: inset 0 2px 4px rgba(59, 130, 246, 0.1);">
                            🔑
                        </div>
                        <h2 style="color: #0f172a; margin: 0; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.025em;">Reset Password</h2>
                        <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.35rem; font-weight: 400;">Enter your credentials to receive a password reset code.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                default_matricule = st.session_state.get("temp_matricule", "")
                
                with st.form("forgot_form"):
                    matricule_input = st.text_input("Employee Matricule / ID", value=default_matricule, placeholder="Your ID")
                    email_input = st.text_input("Corporate Email", placeholder="name@company.com")
                    
                    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                    submit_btn = st.form_submit_button("Send Reset Code", use_container_width=True, type="primary")
                    
                    if submit_btn:
                        if not matricule_input or not email_input:
                            st.error("⚠️ All fields are required.")
                        else:
                            try:
                                res = requests.post(f"{BASE_URL}/api/forgot-password", json={
                                    "matricule": matricule_input,
                                    "email": email_input
                                })
                                if res.status_code == 200:
                                    st.session_state.temp_matricule = matricule_input
                                    st.session_state.current_page = "Reset Password"
                                    st.success("Reset code dispatched to your email!")
                                    st.rerun()
                                else:
                                    st.error(f"⚠️ {res.json().get('detail', 'Request failed.')}")
                            except Exception as e:
                                st.error(f"Connection Error: {e}")
                                
                st.markdown("<div style='margin: 0.75rem 0; border-top: 1px solid #f1f5f9;'></div>", unsafe_allow_html=True)
                if st.button("← Return to Login Portal", type="secondary", use_container_width=True, key="return_login_from_forgot"):
                    st.session_state.current_page = "Login"
                    st.rerun()

    # ====================================================
    # RESET PASSWORD CONFIRMATION PAGE
    # ====================================================
    elif st.session_state.current_page == "Reset Password":
        _, col_center, _ = st.columns([1, 0.85, 1])
        
        with col_center:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; padding: 0.75rem 0 1rem 0;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: #eff6ff; border-radius: 14px; margin-bottom: 0.75rem; color: #2563eb; font-size: 1.4rem; box-shadow: inset 0 2px 4px rgba(59, 130, 246, 0.1);">
                            🛡️
                        </div>
                        <h2 style="color: #0f172a; margin: 0; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.025em;">Set New Password</h2>
                        <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.35rem; font-weight: 400;">Enter the 6-digit code sent to your email and your new password.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                target_matricule = st.session_state.get("temp_matricule", "")
                
                with st.form("reset_form"):
                    otp_input = st.text_input("6-Digit Verification Code", max_chars=6, placeholder="123456")
                    new_pw = st.text_input("New Password", type="password", placeholder="••••••••")
                    confirm_pw = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
                    
                    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                    reset_btn = st.form_submit_button("Update Password", use_container_width=True, type="primary")
                    
                    if reset_btn:
                        if not otp_input or len(otp_input) != 6 or not new_pw:
                            st.error("⚠️ Please fill out all fields properly.")
                        elif new_pw != confirm_pw:
                            st.error("❌ Passwords do not match.")
                        else:
                            try:
                                res = requests.post(f"{BASE_URL}/api/reset-password", json={
                                    "matricule": target_matricule,
                                    "otp": otp_input,
                                    "new_password": new_pw
                                })
                                if res.status_code == 200:
                                    st.success("Password updated successfully! Please log in.")
                                    if "temp_matricule" in st.session_state:
                                        del st.session_state.temp_matricule
                                    st.session_state.current_page = "Login"
                                    st.rerun()
                                else:
                                    st.error(f"⚠️ {res.json().get('detail', 'Reset failed.')}")
                            except Exception as e:
                                st.error(f"Connection Error: {e}")
                
                # --- Cooldown & Resend Logic (Placed outside form to avoid nested triggers) ---
                st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)
                
                # Calculate remaining cooldown time
                cooldown_period = 60 # seconds
                last_sent = st.session_state.get("last_resend_timestamp", 0)
                elapsed = time.time() - last_sent
                is_cooled_down = elapsed >= cooldown_period
                
                if not is_cooled_down:
                    remaining = int(cooldown_period - elapsed)
                    st.info(f"⏳ Please wait {remaining}s before requesting a new code.")
                
                if st.button("🔄 Resend Verification Code", use_container_width=True, type="secondary", disabled=not is_cooled_down):
                    try:
                        res = requests.post(f"{BASE_URL}/api/resend-otp", json={"matricule": target_matricule})
                        if res.status_code == 200:
                            st.session_state.last_resend_timestamp = time.time()
                            st.success("✨ A new verification code has been dispatched to your email!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ {res.json().get('detail', 'Failed to resend code.')}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

                st.markdown("<div style='margin: 0.75rem 0; border-top: 1px solid #f1f5f9;'></div>", unsafe_allow_html=True)
                if st.button("← Return to Login Portal", type="secondary", use_container_width=True, key="return_login_from_reset"):
                    st.session_state.current_page = "Login"
                    st.rerun()

    # ====================================================
    # OTP VERIFICATION PAGE
    # ====================================================
    elif st.session_state.current_page == "Verify OTP":
        _, col_center, _ = st.columns([1, 0.85, 1])
        
        with col_center:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; padding: 0.75rem 0 1rem 0;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: #eff6ff; border-radius: 14px; margin-bottom: 0.75rem; color: #2563eb; font-size: 1.4rem; box-shadow: inset 0 2px 4px rgba(59, 130, 246, 0.1);">
                            📩
                        </div>
                        <h2 style="color: #0f172a; margin: 0; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.025em;">Email Confirmation</h2>
                        <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.35rem; font-weight: 400;">Please enter the 6-digit OTP sent to your registered email address.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                target_matricule = st.session_state.get("temp_matricule", "")
                
                with st.form("otp_form"):
                    otp_input = st.text_input("6-Digit Verification Code", max_chars=6, placeholder="123456")
                    
                    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                    verify_btn = st.form_submit_button("Verify & Activate Account", use_container_width=True, type="primary")
                    
                    if verify_btn:
                        if not otp_input or len(otp_input) != 6:
                            st.error("⚠️ Please enter a valid 6-digit code.")
                        else:
                            try:
                                res = requests.post(f"{BASE_URL}/api/verify-otp", json={
                                    "matricule": target_matricule,
                                    "otp": otp_input
                                })
                                if res.status_code == 200:
                                    st.success("Account activated successfully! Please log in.")
                                    if "temp_matricule" in st.session_state:
                                        del st.session_state.temp_matricule
                                    st.session_state.current_page = "Login"
                                    st.rerun()
                                else:
                                    st.error(f"⚠️ {res.json().get('detail', 'Verification failed.')}")
                            except Exception as e:
                                st.error(f"Connection Error: {e}")

    # ----------------------------------------------------
    # ROUTE 2: MAIN LOGIN PORTAL
    # ----------------------------------------------------
    else:
        # High-end SaaS Custom CSS Overrides with 50/50 Balanced Tabs
        st.markdown("""
            <style>
                /* Smooth input styling */
                .stTextInput > div > div > input {
                    background-color: #f8fafc !important;
                    border: 1px solid #cbd5e1 !important;
                    border-radius: 10px !important;
                    padding: 0.6rem 1rem !important;
                    font-size: 0.95rem !important;
                    color: #0f172a !important;
                    transition: all 0.2s ease;
                }
                .stTextInput > div > div > input:focus {
                    background-color: #ffffff !important;
                    border-color: #3b82f6 !important;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
                }
                
                /* Premium button styling */
                .stButton > button {
                    border-radius: 10px !important;
                    font-weight: 600 !important;
                    padding: 0.6rem 1rem !important;
                    transition: all 0.2s ease;
                }
                .stButton > button[kind="primary"] {
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                    border: none !important;
                    color: white !important;
                    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
                }
                .stButton > button[kind="primary"]:hover {
                    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
                    transform: translateY(-1px);
                }
                .stButton > button[kind="secondary"] {
                    background: #ffffff !important;
                    border: 1px solid #cbd5e1 !important;
                    color: #475569 !important;
                }
                .stButton > button[kind="secondary"]:hover {
                    background: #f8fafc !important;
                    border-color: #94a3b8 !important;
                    color: #0f172a !important;
                }
                
                /* Perfectly Balanced 50/50 Modern Tabs */
                .stTabs [data-baseweb="tab-list"] {
                    display: flex !important;
                    width: 100% !important;
                    gap: 6px;
                    background-color: #f1f5f9;
                    padding: 4px;
                    border-radius: 12px;
                }
                .stTabs [data-baseweb="tab"] {
                    flex: 1 !important;
                    justify-content: center !important;
                    text-align: center !important;
                    border-radius: 8px !important;
                    height: 40px;
                    font-weight: 500;
                    color: #475569;
                }
                /* Centers text content inside the tab buttons */
                .stTabs [data-baseweb="tab"] div {
                    width: 100%;
                    text-align: center;
                }
            </style>
        """, unsafe_allow_html=True)

        _, col_center, _ = st.columns([1, 0.85, 1])
        
        with col_center:
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; padding: 0.75rem 0 1rem 0;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: #eff6ff; border-radius: 14px; margin-bottom: 0.75rem; color: #2563eb; font-size: 1.4rem; box-shadow: inset 0 2px 4px rgba(59, 130, 246, 0.1);">
                            🔐
                        </div>
                        <h2 style="color: #0f172a; margin: 0; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.025em;">TT Health Portal</h2>
                        <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.35rem; font-weight: 400;">Secure enterprise authentication for staff & administration</p>
                    </div>
                """, unsafe_allow_html=True)
                
                tab_employee, tab_admin = st.tabs(["👤 Employee Portal", "🛡️ Admin Dashboard"])
                
                with tab_employee:
                    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
                    matricule_input = st.text_input("Matricule ID", placeholder="Enter your ID", key="emp_matricule")
                    password_input = st.text_input("Password", type="password", placeholder="Enter your password", key="emp_password")
                    
                    st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)
                    
                    if st.button("Sign In to Portal", use_container_width=True, type="primary", key="emp_login_btn"):
                        try:
                            res = requests.post(f"{BASE_URL}/api/login", json={
                                "role": "employee", 
                                "matricule": matricule_input, 
                                "password": password_input
                            })
                            if res.status_code == 200:
                                data = res.json()
                                if data.get("status") == "first_time":
                                    st.session_state.temp_matricule = matricule_input
                                    st.session_state.current_page = "Set Password"
                                    st.rerun()
                                else:
                                    st.session_state.authenticated = True
                                    st.session_state.role = "employee"
                                    st.session_state.matricule = matricule_input
                                    st.rerun()
                            else:
                                st.error(res.json().get("detail", "Login failed."))
                        except Exception as e:
                            st.error(f"Backend connection error: {e}")
                    
                    if st.button("🔑 Forgot password?", use_container_width=True, type="secondary", key="goto_forgot_btn"):
                        if matricule_input:
                            st.session_state.temp_matricule = matricule_input
                        st.session_state.current_page = "Forgot Password"
                        st.rerun()

                    st.markdown("<div style='margin: 1rem 0; border-top: 1px solid #f1f5f9;'></div>", unsafe_allow_html=True)
                    if st.button("✨ First-time user? Set up password", use_container_width=True, type="secondary", key="emp_signup_btn"):
                        if matricule_input:
                            st.session_state.temp_matricule = matricule_input
                        st.session_state.current_page = "Set Password"
                        st.rerun()

                with tab_admin:
                    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
                    admin_pass = st.text_input("Admin Password", type="password", placeholder="Enter secure admin key...", key="admin_password_input")
                    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
                    
                    if st.button("Login as Admin", use_container_width=True, type="primary", key="admin_login_btn"):
                        try:
                            res = requests.post(f"{BASE_URL}/api/login", json={"role": "admin", "password": admin_pass})
                            if res.status_code == 200:
                                st.session_state.authenticated = True
                                st.session_state.role = "admin"
                                st.rerun()
                            else:
                                st.error("Invalid Admin Password")
                        except Exception as e:
                            st.error(f"Backend connection error: {e}")
                            
        st.stop() 
# ==========================================
# SESSION STATE FOR CUSTOM NAVIGATION
# ==========================================


elif st.session_state.role == "employee":
    st.markdown("""
        <style>
            .block-container {
                padding-top: 3rem !important;
                padding-bottom: 3rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    # ==========================================
    # SIDEBAR NAVIGATION
    # ==========================================
    with st.sidebar:
        st.markdown("""
            <style>
                .session-title {
                    color: #3b82f6;
                    font-size: 0.65rem;
                    text-transform: uppercase;
                    letter-spacing: 0.07em;
                    font-weight: 700;
                    margin: 0;
                }
                .session-value {
                    color: #1e3a8a;
                    font-size: 0.9rem;
                    font-weight: 700;
                    margin: 0.15rem 0 0 0;
                }
            </style>
        """, unsafe_allow_html=True)

        # Brand Header with Custom Icon Badge
        st.markdown("""
            <div style="padding: 1rem 0 0.5rem 0; text-align: center;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: #e0f2fe; border-radius: 12px; margin-bottom: 0.5rem; color: #0284c7; font-size: 1.2rem; box-shadow: inset 0 2px 4px rgba(2, 132, 199, 0.1);">
                    🏢
                </div>
                <h3 style="color: #0f172a; margin: 0; font-size: 1.05rem; font-weight: 700; letter-spacing: -0.025em;">TT HEALTHCARE</h3>
                <p style="color: #64748b; font-size: 0.75rem; margin-top: 0.15rem; font-weight: 500;">Secure Employee Terminal</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 0.5rem 0; border-top: 1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
        
        # Styled Active Session Card
        matricule_display = st.session_state.get('matricule', 'N/A')
        st.markdown(f"""
            <div class="session-card">
                <p class="session-title">Active Session</p>
                <p class="session-value">Matricule: {matricule_display}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('---')
        
        # Mini Section Header for Menu
        st.markdown("<p style='color: #94a3b8; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.07em; font-weight: 700; margin-bottom: 0.35rem; padding-left: 0.2rem;'>Main Navigation</p>", unsafe_allow_html=True)
        
        if "emp_current_page" not in st.session_state:
            st.session_state.emp_current_page = "Operations Ledger"

        emp_nav = [
            {"label": "Operations Ledger", "key": "Operations Ledger", "icon": "📋"},
            {"label": "Financial Breakdown", "key": "Financial Breakdown", "icon": "📊"},
            {"label": "Household & Dependents", "key": "Household & Dependents", "icon": "👨‍👩‍👧‍👦"}
        ]

        for item in emp_nav:
            is_active = st.session_state.emp_current_page == item["key"]
            label = f"{item['icon']}  {item['label']}"
            button_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"emp_nav_{item['key']}", use_container_width=True, type=button_type):
                st.session_state.emp_current_page = item["key"]
                st.rerun()
        
        # Dynamic spacing to push logout button to the lower section cleanly
        st.markdown("<div style='margin-top: 5rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin: 0.75rem 0; border-top: 1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
        
        if st.button("🚪 Terminate Session", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.matricule = None
            st.session_state.emp_current_page = None
            st.rerun()

    # ==========================================
    # DATA FETCHING WITH SPINNER
    # ==========================================
    # @st.cache_data(ttl=300)
    def load_employee_data(mat):
        try:
            res = requests.get(f"{BASE_URL}/api/employee/records/{mat}", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    with st.spinner("Querying enterprise database nodes..."):
        records_data = load_employee_data(st.session_state.matricule)

    if not records_data:
        st.error("Failed to connect to backend ledger or record not found.")
        st.stop()

    df_emp = pd.DataFrame(records_data)
    employee_name = df_emp["Adherent"].iloc[0] if "Adherent" in df_emp.columns and not df_emp.empty else "Employee"

    # ==========================================
    # SOPHISTICATED HERO HEADER BANNER
    # ==========================================
    st.markdown(f"""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="hero-kicker">
                <span class="ai-orb"></span> Employee Portal
            </div>
            <h1 class="hero-title">Welcome back, {employee_name}</h1>
            <p class="hero-subtitle">Household Medical Dossier & Real‑time Claims Processing Hub</p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.7); padding: 1rem 1.5rem; border-radius: 16px; border: 1px solid rgba(99,102,241,0.2); box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <span style="color: #475569; font-size: 0.75rem; display: block;">TOTAL DOSSIER CLAIMS</span>
            <span style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #6366f1, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{len(df_emp)} Records</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # total_spent = df_emp["Total_Depense"].sum() if "Total_Depense" in df_emp.columns else 0
    # total_reimbursed = df_emp["Total_Rembourse"].sum() if "Total_Rembourse" in df_emp.columns else 0
    # reimbursed_count = len(df_emp[df_emp["Etat"] == "REMBOURSE"]) if "Etat" in df_emp.columns else 0
    # pending_count = len(df_emp[df_emp["Etat"] == "EN_ATTENTE"]) if "Etat" in df_emp.columns else 0

    # k1, k2, k3, k4 = st.columns(4)
    # k1.metric("Processed Claims", f"{len(df_emp)}")
    # k2.metric("Cumulative Expenses", f"{total_spent:,.3f} TND")
    # k3.metric("Total Reimbursed", f"{total_reimbursed:,.3f} TND")
    # k4.metric("Pending Verification", f"{pending_count}", delta=f"{reimbursed_count} Cleared", delta_color="normal")
    
    st.markdown("<br>", unsafe_allow_html=True)

    current_page = st.session_state.get("emp_current_page", "Operations Ledger")

    # ==========================================
    # SECTION VIEWS (Card Enclosed)
    # ==========================================
    if current_page == "Operations Ledger":
        # Force equal height on metric cards via CSS
        st.markdown("""
        <style>
            [data-testid="stMetric"] {
                height: 130px !important;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
        </style>
    """, unsafe_allow_html=True)

        processed_count = len(df_emp)
        pending_count = len(df_emp[df_emp["Etat"].isin(["EN_ATTENTE", "Pending", "EN ATTENTE"])]) if "Etat" in df_emp.columns else 0
        reimbursed_count = len(df_emp[df_emp["Etat"] == "REMBOURSE"]) if "Etat" in df_emp.columns else 0
        
        # 2 Native Metric Cards with perfectly matched heights
        op_col1, op_col2 = st.columns(2)
        op_col1.metric("Processed Claims", f"{processed_count}")
        op_col2.metric("Pending Verification", f"{pending_count}", delta=f"{reimbursed_count} Cleared", delta_color="normal")
                
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### Complete Historical Operations Ledger")
            st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Detailed itemized log of all healthcare expenditures and reimbursement tracking.</p>", unsafe_allow_html=True)
            
            col_f1, col_f2 = st.columns([1, 4])
            with col_f1:
                status_filter = st.selectbox("Filter Status", ["All", "REMBOURSE", "EN_ATTENTE", "REJETÉ"])
            
            df_display = df_emp.copy()
            if status_filter != "All":
                df_display = df_display[df_display["Etat"] == status_filter]
            
            columns_to_drop = ["Categorie", "Employee_Age", "Couple_TT", "Matricule", "Adherent"]
            df_display = df_display.drop(columns=[col for col in columns_to_drop if col in df_display.columns], errors="ignore")
            
            df_html = df_display.copy()
            if "Total_Depense" in df_html.columns:
                df_html["Total_Depense"] = df_html["Total_Depense"].apply(lambda x: f"<span style='font-weight: 600; color: #0f172a;'>{x:,.3f} TND</span>" if pd.notnull(x) else "")
            if "Total_Rembourse" in df_html.columns:
                df_html["Total_Rembourse"] = df_html["Total_Rembourse"].apply(lambda x: f"<span style='font-weight: 600; color: #059669;'>{x:,.3f} TND</span>" if pd.notnull(x) else "")
            
            if "Etat" in df_html.columns:
                def style_status(val):
                    if val == "REMBOURSE":
                        return '<span class="badge-reimbursed">Reimbursed</span>'
                    elif val == "EN_ATTENTE":
                        return '<span class="badge-pending">Pending</span>'
                    elif val in ["REJETÉ", "REJETE"]:
                        return '<span class="badge-rejected">Rejected</span>'
                    return f'<span style="font-weight: 600;">{val}</span>'
                df_html["Etat"] = df_html["Etat"].apply(style_status)

            df_html = df_html.fillna("None")

            table_html = df_html.to_html(classes="enterprise-table", index=False, escape=False)
            st.markdown(f"""
            <div class="enterprise-table-container">
                {table_html}
            </div>
            """, unsafe_allow_html=True)

    elif current_page == "Financial Breakdown":
        total_spent = df_emp["Total_Depense"].sum() if "Total_Depense" in df_emp.columns else 0
        total_reimbursed = df_emp["Total_Rembourse"].sum() if "Total_Rembourse" in df_emp.columns else 0
        
        # 2 Native Metric Cards for Financial Tab
        fin_col1, fin_col2 = st.columns(2)
        fin_col1.metric("Cumulative Expenses", f"{total_spent:,.3f} TND")
        fin_col2.metric("Total Reimbursed", f"{total_reimbursed:,.3f} TND")
                
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 📊 Cost Burden & Prestation Analytics")
            st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1.5rem;'>Visual breakdown of medical resource distribution and temporal expenditure patterns.</p>", unsafe_allow_html=True)
            
            saas_palette = ['#2563eb', '#06b6d4', '#10b981', '#6366f1', '#f59e0b', '#ec4899']
            
            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                if "Type_Prestation" in df_emp.columns and "Total_Depense" in df_emp.columns:
                    fig_prest = px.pie(
                        df_emp, names="Type_Prestation", values="Total_Depense", 
                        title="Expenditure Distribution by Prestation Type", hole=0.55,
                        color_discrete_sequence=saas_palette
                    )
                    fig_prest.update_traces(marker=dict(line=dict(color='#ffffff', width=2)))
                    fig_prest.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                        margin=dict(t=40, b=20, l=20, r=20), 
                        font=dict(family="Inter", color="#1e293b", size=12),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_prest, use_container_width=True)
                    
            with c_chart2:
                if "Date_Sinistre" in df_emp.columns and "Total_Depense" in df_emp.columns:
                    fig_time = px.bar(
                        df_emp, x="Date_Sinistre", y="Total_Depense", color="Type_Prestation",
                        title="Timeline Analysis of Claims", color_discrete_sequence=saas_palette
                    )
                    fig_time.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                        margin=dict(t=40, b=20, l=20, r=20), 
                        font=dict(family="Inter", color="#1e293b", size=12),
                        xaxis=dict(showgrid=False, linecolor="#cbd5e1", title=""),
                        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1", title="Total Expense (TND)"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_time, use_container_width=True)

    elif current_page == "Household & Dependents":
        with st.container(border=True):
            st.markdown("### Household & Family Member Claims Breakdown")
            st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1.5rem;'>Aggregated financial footprint segmented by household relationship categories.</p>", unsafe_allow_html=True)
            
            if "Relationship" in df_emp.columns:
                rel_summary = df_emp.groupby("Relationship").agg(
                    Total_Claims=("Matricule", "count"),
                    Total_Spent=("Total_Depense", "sum"),
                    Total_Rembourse=("Total_Rembourse", "sum")
                ).reset_index()
                
                # Format numbers into elite HTML table representation
                rel_html = rel_summary.copy()
                if "Total_Spent" in rel_html.columns:
                    rel_html["Total_Spent"] = rel_html["Total_Spent"].apply(lambda x: f"<span style='font-weight: 600; color: #0f172a;'>{x:,.3f} TND</span>" if pd.notnull(x) else "")
                if "Total_Rembourse" in rel_html.columns:
                    rel_html["Total_Rembourse"] = rel_html["Total_Rembourse"].apply(lambda x: f"<span style='font-weight: 600; color: #059669;'>{x:,.3f} TND</span>" if pd.notnull(x) else "")
                
                # Clean up header names for presentation
                rel_html.columns = [col.replace("_", " ") for col in rel_html.columns]

                table_html = rel_html.to_html(classes="enterprise-table", index=False, escape=False)
                st.markdown(f"""
                <div class="enterprise-table-container">
                    {table_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Relationship classification data is not indexed for this dataset view.")

        st.markdown("</div>", unsafe_allow_html=True)


elif st.session_state.role == "admin":
    st.markdown("""
            <style>
                .block-container {
                    padding-top: 3rem !important;
                    padding-bottom: 3rem !important;
                }
            </style>
        """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        /* Sidebar background & typography */
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e2e8f0;
            padding: 1.5rem 1rem;
        }
        [data-testid="stSidebar"] .css-1d391kg {
            background: transparent;
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 2rem;
            padding-left: 0.3rem;
        }
        .sidebar-brand span {
            font-weight: 700;
            font-size: 1.15rem;
            color: #0f172a;
            letter-spacing: -0.01em;
        }

        /* Navigation buttons */
        .nav-btn {
            display: block;
            width: 100%;
            padding: 0.6rem 1rem;
            margin: 0.3rem 0;
            background: transparent;
            border: none;
            border-radius: 12px;
            color: #334155;
            text-align: left;
            font-weight: 500;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        .nav-btn:hover {
            background: #f1f5f9;
        }
        .nav-btn.active {
            background: #eef2ff;
            color: #4338ca;
        }
        .nav-btn svg {
            width: 20px;
            height: 20px;
            stroke: currentColor;
            stroke-width: 2;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* Filter section */
        .filter-section {
            margin-top: 2rem;
            padding: 0.3rem;
        }
        .filter-section .stMultiSelect [data-baseweb="input"] {
            border-radius: 10px;
        }

        /* System status */
        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-online {
            background: rgba(16, 185, 129, 0.08);
            color: #059669;
        }
        .status-offline {
            background: rgba(239, 68, 68, 0.08);
            color: #dc2626;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }
        .status-online .status-dot {
            background: #10b981;
        }
        .status-offline .status-dot {
            background: #ef4444;
        }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # SIDEBAR – BRAND, NAVIGATION, FILTERS, STATUS
    # ==========================================
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
            <span>TT Health Intel</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Role:** `{st.session_state.role}`") 
        pages = [
            ("Enterprise Overview", "🏢", "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"),  # building icon paths too complex; use simpler SVGs
        ]
            # Navigation icons (Unicode geometric – modern, no raw SVGs)
        nav_items = [
    {"label": "Enterprise Overview", "key": "Enterprise Overview", "icon": "⊞", "desc": "KPI & risk metrics"},
    {"label": "Advanced Analytics", "key": "Advanced Analytics", "icon": "▤", "desc": "Heatmaps & matrices"},
    {"label": "Employee Registry", "key": "Employee Registry", "icon": "⛂", "desc": "Deep profiles & trends"},
    {"label": "Neural Simulation", "key": "Neural Simulation", "icon": "◎", "desc": "What‑if simulator"}
]

        

        for item in nav_items:
            is_active = st.session_state.current_page == item["key"]
            label = f"{item['icon']}  {item['label']}"
            button_type = "primary" if is_active else "secondary"
            if st.button(label, key=item["key"], use_container_width=True, type=button_type):
                st.session_state.current_page = item["key"]
                st.rerun()

        st.markdown("---")

        # Filters
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        selected_risk = st.multiselect(
            "**Risk Tier Filter**",
            ["Low Risk", "Medium Risk", "High Risk", "Critical"],
            default=["Low Risk", "Medium Risk", "High Risk", "Critical"]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🚪 Terminate Session", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.matricule = None
            st.rerun()

        st.markdown("---")
        

        # System status
        try:
            status = requests.get(f"{BASE_URL}/kpis", timeout=5).status_code
            if status == 200:
                st.markdown("""
                <div class="status-badge status-online">
                    <div class="status-dot"></div>
                    Backend Online
                </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div class="status-badge status-offline">
                <div class="status-dot"></div>
                Backend Offline
            </div>
            """, unsafe_allow_html=True)

    # Now set the page variable from session state
    page = st.session_state.current_page

    # ==========================================
    # PAGE 1: ENTERPRISE OVERVIEW (header only)
    # ==========================================
    if page == "Enterprise Overview":
        # --- Sleek Light Theme Hero Banner CSS & HTML ---
        st.markdown("""
        <style>
            .hero-banner {
                background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: 20px;
                padding: 2rem 2.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 10px 25px rgba(99, 102, 241, 0.05);
            }
            .hero-kicker {
                color: #6366f1;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 0.5rem;
            }
            .hero-title {
                color: #0f172a;
                font-size: 2rem;
                font-weight: 700;
                margin: 0 0 0.5rem 0;
                letter-spacing: -0.02em;
            }
            .hero-desc {
                color: #475569;
                font-size: 0.95rem;
                margin: 0;
                line-height: 1.5;
            }
        </style>

        <div class="hero-banner">
            <div class="hero-kicker">
                <span class="ai-orb"></span> ENTERPRISE ANALYTICS
            </div>
            <div class="hero-title">Enterprise Health Overview</div>
            <div class="hero-desc">Comprehensive organizational risk metrics, financial cost burdens, and neural sensitivity indicators.</div>
        </div>
        """, unsafe_allow_html=True)

        # Fetch KPI data (unchanged)
        try:
            kpi_data = requests.get(f"{BASE_URL}/kpis", timeout=5).json()
        except:
            kpi_data = {"total_predicted_cost": 0, "avg_cost": 0, "high_risk_count": 0, "total_employees": 0}

        # --- Animated floating KPI cards with custom SVG icons ---
        st.markdown("""
        <style>
            /* Enhanced KPI Grid */
.kpi-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin: 1rem 0 1.5rem 0;
}
.kpi-card {
    flex: 1 1 200px;
    min-width: 200px;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 1.5rem 1.2rem;
    text-align: center;
    border: 1px solid rgba(99, 102, 241, 0.15);
    box-shadow: var(--shadow);
    transition: var(--transition);
    animation: fadeInUp 0.5s ease forwards;
    opacity: 0;
}
.kpi-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-hover);
    border-color: rgba(99, 102, 241, 0.35);
}
.kpi-card .icon { margin-bottom: 0.5rem; }
.kpi-card .icon svg {
    width: 34px;
    height: 34px;
    stroke: #6366f1;
    stroke-width: 2;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
}
.kpi-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 0.5rem;
    font-weight: 600;
}
.kpi-card .value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.kpi-card .trend {
    font-size: 0.75rem;
    color: #10b981;
    margin-top: 0.4rem;
    font-weight: 500;
}
@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}
.kpi-card:nth-child(1) { animation-delay: 0.05s; }
.kpi-card:nth-child(2) { animation-delay: 0.15s; }
.kpi-card:nth-child(3) { animation-delay: 0.25s; }
.kpi-card:nth-child(4) { animation-delay: 0.35s; }
        </style>
        """, unsafe_allow_html=True)

        # Build KPI cards with custom SVG icons
        kpi_html = f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="icon">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
                    </svg>
                </div>
                <div class="label">Total Predicted Cost</div>
                <div class="value">{kpi_data.get('total_predicted_cost', 0):,.0f} TND</div>
            </div>
            <div class="kpi-card">
                <div class="icon">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                    </svg>
                </div>
                <div class="label">Avg Predicted Cost</div>
                <div class="value">{kpi_data.get('avg_cost', 0):,.0f} TND</div>
            </div>
            <!-- High Risk Employees -->
            <div class="kpi-card">
                <div class="icon">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                        <line x1="12" y1="9" x2="12" y2="13" />
                        <line x1="12" y1="17" x2="12.01" y2="17" />
                    </svg>
                </div>
                <div class="label">Potential High Risk Employees</div>
                <div class="value">{kpi_data.get('high_risk_count', 0)}</div>
            </div>
            <!-- Total Employees -->
            <div class="kpi-card">
                <div class="icon">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 00-3-3.87" />
                        <path d="M16 3.13a4 4 0 010 7.75" />
                    </svg>
                </div>
                <div class="label">Total Employees</div>
                <div class="value">{kpi_data.get('total_employees', 0)}</div>
            </div>
        </div>
        """

        st.markdown(kpi_html, unsafe_allow_html=True)

        st.markdown("---")

        # Risk & Disease Charts row
        col_chart1, col_chart2 = st.columns(2)

        try:
            risk_data = requests.get(f"{BASE_URL}/risk-distribution", timeout=5).json()
            disease_data = requests.get(f"{BASE_URL}/cost-by-disease", timeout=5).json()
        except:
            risk_data, disease_data = [], []

        df_risk = pd.DataFrame(risk_data)
        if not df_risk.empty:
            df_risk.columns = ["Risk_Level", "Count"]
            df_risk = df_risk[df_risk["Risk_Level"].isin(selected_risk)]

        df_disease = pd.DataFrame(disease_data)

        # Unified blue palette
        risk_colors = {
            "Low Risk": "#93c5fd",
            "Medium Risk": "#6366f1",
            "High Risk": "#1e3a8a",
            "Critical": "#152551"
        }

        disease_colors = {
            "asthme": "#60a5fa",
            "diabete": "#3b82f6",
            "hypertension": "#2563eb",
            "troubles musculosquelettiques": "#1d4ed8",
            "cardiaque": "#1e40af",
            "cancer": "#1e3a8a",
            "aucune": "#172554"
        }

        with col_chart1:
            # --- Icon + title ---
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
                    <circle cx="19" cy="5" r="1" fill="#6366f1" stroke="none" />
                    <circle cx="12" cy="12" r="1" fill="#6366f1" stroke="none" />
                    <circle cx="8" cy="16" r="1" fill="#6366f1" stroke="none" />
                </svg>
                <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Risk Distribution</span>
            </div>
            """, unsafe_allow_html=True)

            if not df_risk.empty:
                fig_risk = px.pie(
                    df_risk,
                    names="Risk_Level",
                    values="Count",
                    hole=0.45,
                    color="Risk_Level",
                    color_discrete_map=risk_colors
                )
                fig_risk.update_traces(
                    textinfo='percent+label',
                    textfont_size=12,
                    marker=dict(line=dict(color='white', width=2))
                )
                fig_risk.update_layout(
                    height=400,
                    showlegend=False,
                    margin=dict(t=20, b=40, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#475569")
                )
                st.plotly_chart(fig_risk, use_container_width=True)

        with col_chart2:
            # --- Icon + title ---
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10" />
                    <line x1="12" y1="20" x2="12" y2="4" />
                    <line x1="6" y1="20" x2="6" y2="14" />
                </svg>
                <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Cost Burden by Disease</span>
            </div>
            """, unsafe_allow_html=True)

            if not df_disease.empty:
                df_disease = df_disease.sort_values(by="Total_Cost", ascending=True)

                fig_bar = px.bar(
                    df_disease,
                    y="Disease",
                    x="Total_Cost",
                    orientation='h',
                    color="Disease",
                    color_discrete_map=disease_colors,
                    text_auto='.2s'
                )

                fig_bar.update_traces(
                    textposition="outside",
                    marker_line_width=0,
                    opacity=0.9
                )

                fig_bar.update_layout(
                    height=400,
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#475569"),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor="#e2e8f0",
                        title="Total Cost (TND)"
                    ),
                    yaxis=dict(
                        showgrid=False,
                        title=""
                    )
                )

                st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # Cohorts, Cost Drivers row – perfectly balanced
        col_sub1, col_sub2 = st.columns(2)

        with col_sub1:
            # --- Icon + title ---
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
                <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Projected Cost Curve by Age Cohort</span>
            </div>
            """, unsafe_allow_html=True)

            try:
                cohorts_data = requests.get(f"{BASE_URL}/cohorts", timeout=5).json()
                df_cohorts = pd.DataFrame(cohorts_data)
                if not df_cohorts.empty:
                    fig_cohorts = px.area(
                        df_cohorts,
                        x="Age_Group",
                        y="Predicted_Cost",
                        line_shape='spline',
                        color_discrete_sequence=["#6366f1"]
                    )
                    fig_cohorts.update_traces(
                        line=dict(width=2.5),
                        fillcolor='rgba(99, 102, 241, 0.08)',
                        opacity=1
                    )
                    fig_cohorts.update_layout(
                        height=390,
                        margin=dict(l=40, r=20, t=20, b=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#475569"),
                        xaxis_title="Age Cohort",
                        yaxis_title="Avg Cost (TND)",
                        xaxis=dict(showgrid=False, tickangle=-30),
                        yaxis=dict(showgrid=True, gridcolor="#e2e8f0")
                    )
                    st.plotly_chart(fig_cohorts, use_container_width=True)
            except:
                st.error("Failed to compile age cohort curve.")

        with col_sub2:
            # --- Icon + title ---
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <circle cx="12" cy="12" r="6" />
                    <circle cx="12" cy="12" r="2" />
                    <line x1="12" y1="2" x2="12" y2="6" />
                    <line x1="12" y1="18" x2="12" y2="22" />
                    <line x1="2" y1="12" x2="6" y2="12" />
                    <line x1="18" y1="12" x2="22" y2="12" />
                </svg>
                <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Neural Feature Sensitivity</span>
            </div>
            """, unsafe_allow_html=True)

            try:
                drivers_data = requests.get(f"{BASE_URL}/cost-drivers", timeout=5).json()
                df_drivers = pd.DataFrame(drivers_data)

                if not df_drivers.empty:
                    df_drivers = df_drivers.sort_values("Importance", ascending=False).head(8)
                    avg_importance = df_drivers["Importance"].mean()

                    fig = px.bar_polar(
                        df_drivers,
                        r="Importance",
                        theta="Feature",
                        color="Importance",
                        color_continuous_scale=[
                            [0.0, "#93c5fd"],
                            [0.5, "#6366f1"],
                            [1.0, "#312e81"]
                        ],
                        template=None
                    )

                    fig.update_traces(
                        marker=dict(line=dict(color="white", width=1.5)),
                        width=0.8,
                        selector=dict(type="barpolar")
                    )

                    fig.add_shape(
                        type="circle",
                        xref="paper", yref="paper",
                        x0=0.5, y0=0.5,
                        x1=0.5, y1=0.5,
                        opacity=0.4,
                        fillcolor="rgba(99,102,241,0.06)",
                        line=dict(color="#6366f1", width=2, dash="solid"),
                    )

                    fig.update_layout(
                        height=380,
                        margin=dict(l=40, r=20, t=20, b=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#475569"),
                        polar=dict(
                            radialaxis=dict(visible=False),
                            angularaxis=dict(
                                rotation=145,
                                direction="clockwise",
                                tickfont=dict(size=11, color="#334155")
                            ),
                            bgcolor="rgba(255,255,255,0.5)"
                        ),
                        coloraxis_showscale=False
                    )

                    for trace in fig.data:
                        if trace.type == "barpolar":
                            trace.hovertemplate = '<b>%{theta}</b><br>Importance: %{r:.3f}<extra></extra>'
                            trace.marker.showscale = False

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error("Failed to compile neural sensitivity metrics.")

    # ==========================================
    # PAGE 2: EMPLOYEE DIRECTORY
    # ==========================================
    elif page == "Advanced Analytics":
        # ==========================================
        # SOPHISTICATED HERO HEADER BANNER
        # ==========================================
        st.markdown("""
    <style>
        .hero-banner {
            background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.05);
        }
        .hero-kicker {
            color: #6366f1;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.02em;
        }
        .hero-desc {
            color: #475569;
            font-size: 0.95rem;
            margin: 0;
            line-height: 1.5;
        }
    </style>

    <div class="hero-banner">
        <div class="hero-kicker">
            <span class="ai-orb"></span> ADVANCED ANALYTICS
        </div>
        <div class="hero-title">Multi-Axis Risk Intelligence</div>
        <div class="hero-desc">Advanced demographic heatmaps, multi‑factor cost matrices, and critical worker registries.</div>
    </div>
    """, unsafe_allow_html=True)

        # ==========================================
        # FIRST ROW: HEATMAP & 3D MATRIX CARDS
        # ==========================================
        h_col1, h_col2 = st.columns(2)

        with h_col1:
            with st.container(border=True):
                st.markdown("### 📊 Age‑Stratified Risk Heatmap")
                st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Demographic concentration of risk tiers mapped across age brackets.</p>", unsafe_allow_html=True)

                try:
                    data = requests.get(f"{BASE_URL}/risk-heatmap-age", timeout=5).json()
                    df = pd.DataFrame(data)
                    risk_order = ["Low Risk", "Medium Risk", "High Risk", "Critical"]
                    age_order = ["0-8", "9-16", "17-24", "25-32", "33-40", "41-48",
                                "49-55", "56-63", "64-71", "72-79", "80-87", "+88"]
                    df["Risk_Level"] = pd.Categorical(df["Risk_Level"], categories=risk_order, ordered=True)
                    df["Age_Bin"] = pd.Categorical(df["Age_Bin"], categories=age_order, ordered=True)
                    df = df.sort_values("Age_Bin")

                    fig_heat = px.density_heatmap(
                        df,
                        x="Age_Bin",
                        y="Risk_Level",
                        z="Count",
                        text_auto=True,
                        category_orders={"Age_Bin": age_order, "Risk_Level": risk_order},
                        color_continuous_scale=[
                            [0.0, "#dbeafe"],   # light blue
                            [0.5, "#6366f1"],   # indigo
                            [1.0, "#1e3a8a"]    # deep navy
                        ]
                    )
                    fig_heat.update_layout(
                        height=360,
                        xaxis_title="Age Brackets",
                        yaxis_title="",
                        margin=dict(l=30, r=10, t=10, b=30),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#475569", family="Inter"),
                        coloraxis_showscale=False
                    )
                    fig_heat.update_traces(
                        xgap=1, ygap=1,
                        hovertemplate='Age: %{x}<br>Risk: %{y}<br>Count: %{z}<extra></extra>'
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)
                except Exception:
                    st.error("Could not construct demographic matrix.")

        with h_col2:
            with st.container(border=True):
                st.markdown("### 🧊 3‑Factor Cost Cube Matrix")
                st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Multi-dimensional mapping of clinical visits, disease vectors, and average costs.</p>", unsafe_allow_html=True)

                try:
                    matrix_data = requests.get(f"{BASE_URL}/risk-matrix", timeout=5).json()
                    df_matrix = pd.DataFrame(matrix_data)

                    if not df_matrix.empty:
                        df_matrix["Type_Prestation_Clinique"] = df_matrix["Type_Prestation_Clinique"].map(
                            {0: "No Clinic", 1: "Clinic Visited"}
                        )
                        risk_order = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
                        disease_order = ["None", "Asthma", "Musculoskeletal", "Diabetes", "Hypertension", "Cardiaque", "Cancer"]

                        df_matrix = df_matrix.dropna(subset=["Risk_Level", "Disease_Type"])

                        fig_3d = px.scatter_3d(
                            df_matrix,
                            x="Disease_Type",
                            y="Type_Prestation_Clinique",
                            z="Risk_Level",
                            size="Count",
                            size_max=40,
                            color="Avg_Cost",
                            color_continuous_scale=[
                                [0.0, "#dbeafe"],
                                [0.5, "#6366f1"],
                                [1.0, "#1e3a8a"]
                            ],
                            category_orders={
                                "Disease_Type": disease_order,
                                "Risk_Level": risk_order,
                                "Type_Prestation_Clinique": ["No Clinic", "Clinic Visited"]
                            }
                        )

                        fig_3d.update_layout(
                            height=360,
                            margin=dict(l=0, r=0, b=0, t=0),
                            paper_bgcolor="rgba(0,0,0,0)",
                            scene=dict(
                                xaxis=dict(title="", showbackground=True, backgroundcolor="rgba(255,255,255,0.85)", gridcolor="#cbd5e1", zeroline=False),
                                yaxis=dict(title="", showbackground=True, backgroundcolor="rgba(255,255,255,0.85)", gridcolor="#cbd5e1", zeroline=False),
                                zaxis=dict(title="", showbackground=True, backgroundcolor="rgba(255,255,255,0.85)", gridcolor="#cbd5e1", zeroline=False),
                                camera=dict(eye=dict(x=1.6, y=1.6, z=1.2))
                            ),
                            coloraxis_colorbar=dict(
                                title="Avg Cost (TND)",
                                thicknessmode="pixels", thickness=12,
                                lenmode="pixels", len=200,
                                yanchor="top", y=0.9, xanchor="left", x=1.05
                            )
                        )

                        # Draw subtle wireframe edges for 3D structure
                        x_cats = disease_order
                        y_cats = ["No Clinic", "Clinic Visited"]
                        z_cats = risk_order
                        for x in [x_cats[0], x_cats[-1]]:
                            for y in y_cats:
                                fig_3d.add_scatter3d(
                                    x=[x, x], y=[y, y], z=[z_cats[0], z_cats[-1]],
                                    mode='lines', line=dict(color='#94a3b8', width=1), showlegend=False, hoverinfo='skip'
                                )
                        for y in [y_cats[0], y_cats[-1]]:
                            for z in [z_cats[0], z_cats[-1]]:
                                fig_3d.add_scatter3d(
                                    x=[x_cats[0], x_cats[-1]], y=[y, y], z=[z, z],
                                    mode='lines', line=dict(color='#94a3b8', width=1), showlegend=False, hoverinfo='skip'
                                )
                        for z in [z_cats[0], z_cats[-1]]:
                            for x in [x_cats[0], x_cats[-1]]:
                                fig_3d.add_scatter3d(
                                    x=[x, x], y=[y_cats[0], y_cats[-1]], z=[z, z],
                                    mode='lines', line=dict(color='#94a3b8', width=1), showlegend=False, hoverinfo='skip'
                                )

                        fig_3d.update_traces(
                            marker=dict(sizemin=5, line=dict(width=1, color='white'), opacity=0.9),
                            hovertemplate='<b>%{x}</b><br>Clinic: %{y}<br>Risk: %{z}<br>Count: %{marker.size}<br>Avg Cost: %{marker.color:,.2f} TND<extra></extra>',
                            selector=dict(type='scatter3d')
                        )

                        st.plotly_chart(fig_3d, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not cross‑reference usage matrices: {e}")

        # ==========================================
        # SECOND ROW: CRITICAL PRIORITY REGISTRY
        # ==========================================
        with st.container(border=True):
            st.markdown("""
            <style>
                .enterprise-table-container {
                    max-height: 450px;
                    overflow-y: auto;
                    overflow-x: auto;
                    scrollbar-width: none; /* Firefox */
                }
                .enterprise-table-container::-webkit-scrollbar {
                    display: none; /* Safari and Chrome */
                }

                .badge-critical, .badge-high-risk {
                    padding: 0.35rem 0.85rem;
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }
                .badge-critical {
                    background-color: #fee2e2;
                    color: #991b1b;
                    border: 1px solid #fca5a5;
                }
                .badge-high-risk {
                    background-color: #ffedd5;
                    color: #c2410c;
                    border: 1px solid #fed7aa;
                }
                
                .badge-critical::before, .badge-high-risk::before {
                    content: '';
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    display: inline-block;
                    animation: pulse 1.5s infinite;
                }
                .badge-critical::before { background-color: #ef4444; }
                .badge-high-risk::before { background-color: #f97316; }

                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.4; }
                    100% { opacity: 1; }
                }
            </style>
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.25rem;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                <h3 style="margin: 0; font-size: 1.15rem; color: #0f172a;">Critical Priority Registry (High‑Risk Workers)</h3>
            </div>
            <p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Real-time directory feed tracking workers classified within high-risk medical tiers.</p>
            """, unsafe_allow_html=True)

            try:
                response = requests.get(f"{BASE_URL}/high-risk", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        df_high_risk = pd.DataFrame(data)
                        
                        df_html = df_high_risk.copy()
                        
                        # Format predicted cost column if present
                        for cost_col in ["predicted_cost", "Predicted_Cost", "PREDICTED_COST"]:
                            if cost_col in df_html.columns:
                                df_html[cost_col] = df_html[cost_col].apply(lambda x: f"<span style='font-weight: 600; color: #0f172a;'>{float(x):,.3f} TND</span>" if pd.notnull(x) else "")

                        # Case-insensitive column lookup for Risk Level
                        risk_col = next((c for c in df_html.columns if c.lower() in ["risk_level", "risk level"]), None)

                        if risk_col:
                            def style_risk_row(val):
                                val_str = str(val).strip()
                                if val_str.lower() == "critical":
                                    return f'<span class="badge-critical">{val_str}</span>'
                                else:
                                    return f'<span class="badge-high-risk">{val_str}</span>'
                                    
                            df_html[risk_col] = df_html[risk_col].apply(style_risk_row)

                        df_html = df_html.fillna("None")
                        
                        # Clean up column headers for presentation
                        df_html.columns = [col.replace('_', ' ').upper() for col in df_html.columns]

                        table_html = df_html.to_html(classes="enterprise-table", index=False, escape=False)
                        st.markdown(f"""
                        <div class="enterprise-table-container">
                            {table_html}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No high‑risk individuals currently flagged.")
                else:
                    st.error("Failed to fetch high-risk registry data.")
            except Exception as e:
                st.error(f"Database connection dropped during directory scan: {e}")
    elif page == "Employee Registry":
        st.markdown("""
    <style>
        .hero-banner {
            background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.05);
        }
        .hero-kicker {
            color: #6366f1;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.02em;
        }
        .hero-desc {
            color: #475569;
            font-size: 0.95rem;
            margin: 0;
            line-height: 1.5;
        }
    </style>

    <div class="hero-banner">
        <div class="hero-kicker">
            <span class="ai-orb"></span> EMPLOYEE REGISTRY
        </div>
        <div class="hero-title">Employee Health Registry</div>
        <div class="hero-desc">Comprehensive directory tracking employee health profiles, medical tiers, and claims history.</div>
    </div>
    """, unsafe_allow_html=True)

        # --- Employee Lookup Section ---
        with st.container(border=True):
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.75rem;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <h3 style="margin: 0; font-size: 1.15rem; color: #0f172a;">Profile Deep‑Dive</h3>
            </div>
            <p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Scan or enter an employee matricule number to inspect individual metrics and historical records.</p>
            """, unsafe_allow_html=True)

            matricule_search = st.text_input("Scan Employee Matricule Number", placeholder="Enter ID...", label_visibility="collapsed")

            if matricule_search:
                try:
                    emp_response = requests.get(f"{BASE_URL}/employee/{matricule_search}", timeout=5)
                    if emp_response.status_code == 200:
                        emp_data = emp_response.json()
                        if "error" in emp_data:
                            st.warning(emp_data["error"])
                        else:
                            # --- Employee KPI cards ---
                            col_age, col_cost, col_visits = st.columns(3)
                            with col_age:
                                st.markdown(f"""
                                <div style="background: white; border-radius: 12px; padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
                                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <circle cx="12" cy="12" r="10" />
                                            <polyline points="12 6 12 12 16 14" />
                                        </svg>
                                        <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Age</span>
                                    </div>
                                    <div style="font-size:2.1rem; font-weight:700; background: linear-gradient(135deg, #6366f1, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{emp_data['employee_age']}</div>
                                    <div style="color:#475569; font-size:0.85rem; margin-top:0.2rem;">Years</div>
                                </div>
                                """, unsafe_allow_html=True)

                            with col_cost:
                                st.markdown(f"""
                                <div style="background: white; border-radius: 12px; padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
                                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
                                        </svg>
                                        <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Predicted Cost</span>
                                    </div>
                                    <div style="font-size:2.1rem; font-weight:700; background: linear-gradient(135deg, #6366f1, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{emp_data['predicted_cost']:,.0f}</div>
                                    <div style="color:#475569; font-size:0.85rem; margin-top:0.2rem;">TND</div>
                                </div>
                                """, unsafe_allow_html=True)

                            with col_visits:
                                features = emp_data.get("visit_features", {})
                                features_html = "".join([f"<span style='display: inline-block; background: #eef2ff; color: #4338ca; padding: 0.2rem 0.5rem; border-radius: 6px; margin: 0.15rem; font-size:0.75rem;'>{k}: {v}</span>" for k,v in features.items()])
                                st.markdown(f"""
                                <div style="background: white; border-radius: 12px; padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
                                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                                            <polyline points="14 2 14 8 20 8" />
                                            <line x1="16" y1="13" x2="8" y2="13" />
                                            <line x1="16" y1="17" x2="8" y2="17" />
                                        </svg>
                                        <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Used Services</span>
                                    </div>
                                    <div style="margin-top:0.4rem; max-height: 75px; overflow-y: auto;">{features_html}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            st.markdown("""
                                <style>
                                    /* Force equal height across the 3 KPI columns and their inner containers */
                                    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                                        display: flex;
                                        flex-direction: column;
                                    }
                                    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {
                                        flex: 1;
                                        display: flex;
                                        flex-direction: column;
                                    }
                                    /* Ensure custom card divs inside columns fill height */
                                    .kpi-card-wrapper {
                                        flex: 1;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: space-between;
                                        background: white;
                                        padding: 1.25rem;
                                        border-radius: 0.5rem;
                                        border: 1px solid #e2e8f0;
                                        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                                    }
                                </style>
                            """, unsafe_allow_html=True)

                            # --- Historical Claims---
                            st.markdown("""
                                <div style="display:flex; align-items:center; gap:0.5rem; margin: 1.25rem 0 0.5rem 0;">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                                        <line x1="16" y1="2" x2="16" y2="6" />
                                        <line x1="8" y1="2" x2="8" y2="6" />
                                        <line x1="3" y1="10" x2="21" y2="10" />
                                    </svg>
                                    <span style="font-weight:600; font-size:1.05rem; color:#1e293b;">Historical Claims Ledger</span>
                                </div>
                                """, unsafe_allow_html=True)

                            df_profile = pd.DataFrame(emp_data["profile"])
                            if not df_profile.empty:
                                html_table = """
                                <div style="max-height: 280px; overflow-y: auto; overflow-x: auto; border-radius: 8px; border: 1px solid #e2e8f0; background-color: white; margin-bottom: 0.5rem;">
                                    <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.85rem;">
                                        <thead>
                                            <tr style="position: sticky; top: 0; background-color: #eef2ff; color: #1e293b; text-align: left; z-index: 2;">
                                """
                                for col in df_profile.columns:
                                    clean_col_name = col.replace('_', ' ').upper()
                                    html_table += f"<th style='padding: 12px 14px; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; background-color: #eef2ff; color: #1e293b; border-bottom: 1px solid #e2e8f0;'>{clean_col_name}</th>"
                                html_table += "</tr></thead><tbody>"

                                for idx, row in df_profile.iterrows():
                                    row_bg = "#f8fafc" if idx % 2 == 1 else "white"
                                    html_table += f"<tr style='border-bottom: 1px solid #f1f5f9; background-color: {row_bg};'>"
                                    for col in df_profile.columns:
                                        val = row[col]
                                        if col.lower() in ["etat", "status", "risk_level", "tier"]:
                                            val_str = str(val)
                                            if val_str in ["Critical", "High Risk", "Rejected", "REJETÉ", "REJETE"]:
                                                pill_bg = "#fee2e2"
                                                pill_color = "#991b1b"
                                                dot_color = "#ef4444"
                                            elif val_str in ["Pending", "EN_ATTENTE", "EN ATTENTE"]:
                                                pill_bg = "#fef3c7"
                                                pill_color = "#92400e"
                                                dot_color = "#f59e0b"
                                            else:
                                                pill_bg = "#dcfce7"
                                                pill_color = "#166534"
                                                dot_color = "#22c55e"

                                            cell_content = f"""
                                            <span style='background-color: {pill_bg}; color: {pill_color}; padding: 3px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;'>
                                                <span style='width: 5px; height: 5px; background-color: {dot_color}; border-radius: 50%; display: inline-block;'></span>
                                                {val_str}
                                            </span>
                                            """
                                        else:
                                            cell_content = str(val) if pd.notna(val) else "-"

                                        html_table += f"<td style='padding: 12px 14px; color: #334155;'>{cell_content}</td>"
                                    html_table += "</tr>"

                                html_table += "</tbody></table></div>"
                                st.markdown(html_table, unsafe_allow_html=True)
                            else:
                                st.info("No historical claims available for this employee.")
                    else:
                        st.error("Employee not found in registry.")
                except Exception as e:
                    st.error(f"Registry processing failure: {e}")

        # --- Trend Charts Row Container ---
        with st.container(border=True):
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
                <h3 style="margin: 0; font-size: 1.15rem; color: #0f172a;">Cost Evolution Analytics</h3>
            </div>
            <p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Comparative breakdown of total expenditures and monthly averages.</p>
            """, unsafe_allow_html=True)

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("<p style='font-weight:600; font-size:0.95rem; color:#1e293b; margin-bottom:0.2rem;'>Total Cost Evolution</p>", unsafe_allow_html=True)
                data = requests.get(f"{BASE_URL}/cost-trend", timeout=5).json()
                df = pd.DataFrame(data)
                if not df.empty:
                    fig = px.line(df, x="Month", y="Total_Depense", markers=True)
                    fig.update_traces(line_color="#6366f1", line_width=2.5, marker=dict(size=6, color="#6366f1"))
                    fig.update_layout(height=320, margin=dict(t=15, l=10, r=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                    font=dict(color="#475569"), xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0"))
                    st.plotly_chart(fig, use_container_width=True)

            with col_t2:
                st.markdown("<p style='font-weight:600; font-size:0.95rem; color:#1e293b; margin-bottom:0.2rem;'>Average Cost Trend</p>", unsafe_allow_html=True)
                data = requests.get(f"{BASE_URL}/avg-cost-trend", timeout=5).json()
                df = pd.DataFrame(data)
                if not df.empty:
                    fig = px.line(df, x="Month", y="Total_Depense", markers=True)
                    fig.update_traces(line_color="#f59e0b", line_width=2.5, marker=dict(size=6, color="#f59e0b"))
                    fig.update_layout(height=320, margin=dict(t=15, l=10, r=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                    font=dict(color="#475569"), xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0"))
                    st.plotly_chart(fig, use_container_width=True)

        # --- Risk Evolution Container ---
        with st.container(border=True):
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                <h3 style="margin: 0; font-size: 1.15rem; color: #0f172a;">Risk Evolution Over Time</h3>
            </div>
            <p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Stacked distribution tracking workforce movement across medical risk tiers.</p>
            """, unsafe_allow_html=True)

            data = requests.get(f"{BASE_URL}/risk-trend", timeout=5).json()
            df = pd.DataFrame(data)

            if not df.empty:
                df = df.pivot(index="Month", columns="Risk_Level", values="Count").fillna(0).reset_index()
                df_melt = df.melt(id_vars="Month", var_name="Risk_Level", value_name="Count")

                fig_risk = px.area(
                    df_melt,
                    x="Month",
                    y="Count",
                    color="Risk_Level",
                    color_discrete_map={
                        "Low Risk": "#93c5fd",
                        "Medium Risk": "#6366f1",
                        "High Risk": "#1e3a8a",
                        "Critical": "#152551"
                    }
                )

                fig_risk.update_traces(opacity=0.85)
                fig_risk.update_layout(
                    height=340,
                    margin=dict(t=15, l=10, r=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#475569"),
                    yaxis_title="Number of Employees",
                    xaxis=dict(gridcolor="#e2e8f0"),
                    yaxis=dict(gridcolor="#e2e8f0")
                )
                st.plotly_chart(fig_risk, use_container_width=True)

        # --- Service Line Utilization Container ---
        with st.container(border=True):
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <line x1="3" y1="9" x2="21" y2="9" />
                    <line x1="9" y1="21" x2="9" y2="9" />
                </svg>
                <h3 style="margin: 0; font-size: 1.15rem; color: #0f172a;">Service Line Utilization</h3>
            </div>
            <p style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Volume trends across medical service categories and clinic branches.</p>
            """, unsafe_allow_html=True)

            data = requests.get(f"{BASE_URL}/clinic-trend", timeout=5).json()
            df = pd.DataFrame(data)
            if not df.empty:
                fig_clinic = px.area(df, x="Month", y="Count", color="Type_Prestation",
                                    color_discrete_sequence=["#93c5fd", "#6366f1", "#1e3a8a", "#312e81"])
                fig_clinic.update_traces(opacity=0.8)
                fig_clinic.update_layout(
                    height=340,
                    margin=dict(t=15, l=10, r=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#475569"),
                    xaxis=dict(gridcolor="#e2e8f0"),
                    yaxis=dict(gridcolor="#e2e8f0")
                )
                st.plotly_chart(fig_clinic, use_container_width=True)
        

    # ==========================================
    # PAGE 3: NEURAL SIMULATION
    # ==========================================
    elif page == "Neural Simulation":
        st.markdown("""
    <style>
        .hero-banner {
            background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.05);
        }
        .hero-kicker {
            color: #6366f1;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.02em;
        }
        .hero-desc {
            color: #475569;
            font-size: 0.95rem;
            margin: 0;
            line-height: 1.5;
        }
    </style>

    <div class="hero-banner">
        <div class="hero-kicker">
            <span class="ai-orb"></span> NEURAL SIMULATION
        </div>
        <div class="hero-title">What-If Cost Simulator</div>
        <div class="hero-desc">Predict individual health costs and test intervention scenarios using the neural engine.</div>
    </div>
    """, unsafe_allow_html=True)
        st.markdown("---")

        with st.form("predict_form"):
            col1, col2 = st.columns(2)

            with col1:
                # --- Demographics section ---
                st.markdown("""
                <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <polyline points="12 6 12 12 16 14" />
                    </svg>
                    <span style="font-weight:600; font-size:1.1rem; color:#1e293b;">Subject Demographics</span>
                </div>
                """, unsafe_allow_html=True)

                Dependent_Age = st.number_input("Baseline Age", 0, 100, 35)
                Chronic_asthme = st.radio("Asthma", yes_no, horizontal=True)
                Chronic_diabete = st.radio("Diabetes", yes_no, horizontal=True)

            with col2:
                # Spacer for alignment
                st.markdown("<br>", unsafe_allow_html=True)
                Chronic_hypertension = st.radio("Hypertension", yes_no, horizontal=True)
                Chronic_musculo = st.radio("Musculoskeletal Anomalies", yes_no, horizontal=True),
                cancer = st.radio("Cancer", yes_no, horizontal=True),
                cardiaque = st.radio("Maladie Cardiaque", yes_no, horizontal=True)

            # --- Expected Clinical Touchpoints ---
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin: 1.5rem 0 0.8rem 0;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <line x1="3" y1="9" x2="21" y2="9" />
                    <line x1="9" y1="21" x2="9" y2="9" />
                </svg>
                <span style="font-weight:600; font-size:1.1rem; color:#1e293b;">Expected Service Utilization</span>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                Clinique = st.radio("Hospital/Clinic Stay", yes_no, horizontal=True)
                Consultation = st.radio("General Consultation", yes_no, horizontal=True)
            with c2:
                Laboratoire = st.radio("Laboratory Assays", yes_no, horizontal=True)
                Pharmacie = st.radio("Pharmacy Dispense", yes_no, horizontal=True)
            with c3:
                Radio = st.radio("Radiology Imaging", yes_no, horizontal=True)

            st.markdown("---")

            # --- Intervention Setup ---
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
                </svg>
                <span style="font-weight:600; font-size:1.1rem; color:#1e293b;">Intervention Scenario</span>
            </div>
            """, unsafe_allow_html=True)

            reduce_clinic = st.checkbox("Apply Preventive Program (Force Clinic Admission to Zero)")

            submit = st.form_submit_button("Run Neural Engine")

        if submit:
            st.markdown('<div id="results-anchor"></div>', unsafe_allow_html=True)

            cardiaque_bin = to_binary(cardiaque)
            cancer_bin = to_binary(cancer)
            asthme_bin = to_binary(Chronic_asthme)
            diabete_bin = to_binary(Chronic_diabete)
            hyper_bin = to_binary(Chronic_hypertension)
            musculo_bin = to_binary(Chronic_musculo)

            aucune_flag = 1 if sum([asthme_bin, diabete_bin, hyper_bin, musculo_bin, cancer_bin, cardiaque_bin]) == 0 else 0

            payload = {
                "Dependent_Age": Dependent_Age,
                "Chronic_Disease_asthme": asthme_bin,
                "Chronic_Disease_aucune": aucune_flag,
                "Chronic_Disease_cancer": cancer_bin,
                "Chronic_Disease_cardiaque": cardiaque_bin,
                "Chronic_Disease_diabete": diabete_bin,
                "Chronic_Disease_hypertension": hyper_bin,
                "Chronic_Disease_troubles musculosquelettiques": musculo_bin,
                "Type_Prestation_Clinique": to_binary(Clinique),
                "Type_Prestation_Consultation": to_binary(Consultation),
                "Type_Prestation_Laboratoire": to_binary(Laboratoire),
                "Type_Prestation_Pharmacie": to_binary(Pharmacie),
                "Type_Prestation_Radio": to_binary(Radio),
                "reduce_clinic": reduce_clinic
            }

            if reduce_clinic:
                payload["reduce_clinic"] = True
                try:
                    res = requests.post(f"{BASE_URL}/what-if", json=payload)
                    if res.status_code != 200:
                        st.error(f"Backend error: {res.text}")
                        st.stop()
                    res = res.json()
                except Exception as e:
                    st.error(f"What‑if simulation failed: {e}")
                    st.stop()

                st.markdown("### 📌 What‑If Comparison")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2; height: 100%;">
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
                            </svg>
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Baseline Liability</span>
                        </div>
                        <div style="font-size:2rem; font-weight:700; color:#4f46e5;">{res['base_cost']:,.0f}</div>
                        <div style="color:#475569; font-size:0.85rem;">TND</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2; height: 100%;">
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                            </svg>
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Optimized Cost</span>
                        </div>
                        <div style="font-size:2rem; font-weight:700; color:#059669;">{res['scenario_cost']:,.0f}</div>
                        <div style="color:#475569; font-size:0.85rem;">TND</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2; height: 100%;">
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                            </svg>
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Cost Avoidance</span>
                        </div>
                        <div style="font-size:2rem; font-weight:700; color:#dc2626;">{res['savings']:,.0f}</div>
                        <div style="color:#10b981; font-size:0.85rem; font-weight:500;">↑ Positive ROI</div>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                try:
                    response = requests.post(f"{BASE_URL}/predict", json=payload)
                    if response.status_code != 200:
                        st.error(f"Backend error: {response.text}")
                        st.stop()
                    res = response.json()
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {str(e)}")
                    st.stop()
                except ValueError:
                    st.error("Backend did not return valid JSON")
                    st.stop()

                st.markdown("### 📌 Single‑Life Projection")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2; height: 100%;">
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
                            </svg>
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Projected Cost</span>
                        </div>
                        <div style="font-size:2rem; font-weight:700; color:#4f46e5;">{res['predicted_cost']:,.0f}</div>
                        <div style="color:#475569; font-size:0.85rem;">TND</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2; height: 100%;">
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                                <line x1="12" y1="9" x2="12" y2="13" />
                                <line x1="12" y1="17" x2="12.01" y2="17" />
                            </svg>
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Risk Severity Score</span>
                        </div>
                        <div style="font-size:2rem; font-weight:700; color:#d97706;">{res['risk_score']}/100</div>
                        <div style="color:#475569; font-size:0.85rem;">out of 100</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    risk_level = res['risk_level']
                    if risk_level == "Low Risk":
                        icon_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>'
                        color = "#10b981"
                        bg = "rgba(16, 185, 129, 0.08)"
                    elif risk_level == "Medium Risk":
                        icon_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>'
                        color = "#f59e0b"
                        bg = "rgba(245, 158, 11, 0.08)"
                    else:
                        icon_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>'
                        color = "#ef4444"
                        bg = "rgba(239, 68, 68, 0.08)"

                    st.markdown(f"""
                    <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2; height: 100%;">
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            {icon_svg}
                            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Risk Level</span>
                        </div>
                        <div style="font-size:2rem; font-weight:700; color: {color};">{risk_level}</div>
                        <div style="color:#475569; font-size:0.85rem;">Classification</div>
                    </div>
                    """, unsafe_allow_html=True)

            #Auto-scroll script
            st.components.v1.html("""
            <script>
                document.getElementById('results-anchor').scrollIntoView({ behavior: 'smooth' });
            </script>
            """, height=0)