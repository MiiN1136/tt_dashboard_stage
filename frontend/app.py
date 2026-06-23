import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# CONFIGURATION & GLOBAL INITIALIZATION
# ==========================================
st.set_page_config(page_title="TT Healthcare Intelligence", layout="wide")
BASE_URL = "https://tt-backend-ieay.onrender.com"
yes_no = ["No", "Yes"]

def to_binary(x):
    return 1 if x == "Yes" else 0

# ==========================================
# SESSION STATE FOR CUSTOM NAVIGATION
# ==========================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "Enterprise Overview"

# ==========================================
# 🎨 CLEAN LIGHT-THEME SIDEBAR STYLING
# ==========================================
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
    # Brand / Logo
    st.markdown("""
    <div class="sidebar-brand">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
        <span>TT Health Intel</span>
    </div>
    """, unsafe_allow_html=True)
    pages = [
        ("Enterprise Overview", "🏢", "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"),  # building icon paths too complex; use simpler SVGs
    ]
        # Navigation icons (Unicode geometric – modern, no raw SVGs)
    nav_items = [
        {"label": "Enterprise Overview", "key": "Enterprise Overview", "icon": "⊞"},
        {"label": "Advanced Analytics",  "key": "Advanced Analytics",  "icon": "▤"},
        {"label": "Employee Registry",   "key": "Employee Registry",   "icon": "⛂"},
        {"label": "Neural Simulation",   "key": "Neural Simulation",   "icon": "◎"}
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
        "Risk Tier Filter",
        ["Low Risk", "Medium Risk", "High Risk"],
        default=["Low Risk", "Medium Risk", "High Risk"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # System status
    try:
        status = requests.get(f"{BASE_URL}/kpis", timeout=2).status_code
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
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.8rem; margin-bottom: 1rem;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
        </svg>
        <h1 style="font-size: 1.8rem; font-weight: 600; color: #0f172a; margin: 0;">Enterprise Health Overview</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Fetch KPI data (unchanged)
    try:
        kpi_data = requests.get(f"{BASE_URL}/kpis").json()
    except:
        kpi_data = {"total_predicted_cost": 0, "avg_cost": 0, "high_risk_count": 0, "total_employees": 0}

    # --- Animated floating KPI cards with custom SVG icons ---
    st.markdown("""
    <style>
        .kpi-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin: 1rem 0 1.5rem 0;
            justify-content: center;
        }
        .kpi-card {
            flex: 1 1 200px;
            min-width: 200px;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(8px);
            border-radius: 20px;
            padding: 1.5rem 1.2rem;
            text-align: center;
            border: 1px solid rgba(99, 102, 241, 0.15);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.02), 0 2px 6px rgba(0, 0, 0, 0.03);
            transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
        }
        .kpi-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 14px 28px rgba(99, 102, 241, 0.08), 0 6px 12px rgba(0, 0, 0, 0.04);
            border-color: rgba(99, 102, 241, 0.35);
        }
        .kpi-card .icon {
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .kpi-card .icon svg {
            width: 36px;
            height: 36px;
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
            font-size: 2.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }
        /* Staggered animation delays */
        .kpi-card:nth-child(1) { animation-delay: 0.05s; }
        .kpi-card:nth-child(2) { animation-delay: 0.15s; }
        .kpi-card:nth-child(3) { animation-delay: 0.25s; }
        .kpi-card:nth-child(4) { animation-delay: 0.35s; }

        @keyframes fadeInUp {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
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
            <div class="label">High Risk Employees</div>
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
        risk_data = requests.get(f"{BASE_URL}/risk-distribution").json()
        disease_data = requests.get(f"{BASE_URL}/cost-by-disease").json()
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
        "High Risk": "#1e3a8a"
    }

    disease_colors = {
        "asthme": "#60a5fa",
        "diabete": "#3b82f6",
        "hypertension": "#2563eb",
        "troubles musculosquelettiques": "#1d4ed8",
        "aucune": "#1e3a8a"
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
                hole=0.55,
                color="Risk_Level",
                color_discrete_map=risk_colors
            )
            fig_risk.update_traces(
                textinfo='percent+label',
                textfont_size=13,
                marker=dict(line=dict(color='white', width=2))
            )
            fig_risk.update_layout(
                height=400,
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
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
            cohorts_data = requests.get(f"{BASE_URL}/cohorts").json()
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
            drivers_data = requests.get(f"{BASE_URL}/cost-drivers").json()
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
    # --- Page header with icon ---
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.8rem; margin-bottom: 1rem;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
        <h1 style="font-size: 1.8rem; font-weight: 600; color: #0f172a; margin: 0;">Multi‑Axis Risk Intelligence</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # --- First row: Heatmap & 3D Matrix ---
    h_col1, h_col2 = st.columns(2)

    with h_col1:
        # Icon + title
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" />
            </svg>
            <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Age‑Stratified Risk Heatmap</span>
        </div>
        """, unsafe_allow_html=True)

        try:
            data = requests.get(f"{BASE_URL}/risk-heatmap-age").json()
            df = pd.DataFrame(data)
            risk_order = ["Low Risk", "Medium Risk", "High Risk"]
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
                height=380,
                xaxis_title="Age Brackets",
                yaxis_title="",
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#475569"),
                coloraxis_showscale=False
            )
            fig_heat.update_traces(
                xgap=1, ygap=1,
                hovertemplate='Age: %{x}<br>Risk: %{y}<br>Count: %{z}<extra></extra>'
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        except:
            st.error("Could not construct demographic matrix.")

    with h_col2:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3" />
                <circle cx="19" cy="5" r="2" />
                <circle cx="5" cy="19" r="2" />
                <line x1="16.5" y1="7.5" x2="7.5" y2="16.5" />
            </svg>
            <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">3‑Factor Cost Cube</span>
        </div>
        """, unsafe_allow_html=True)

        try:
            matrix_data = requests.get(f"{BASE_URL}/risk-matrix").json()
            df_matrix = pd.DataFrame(matrix_data)

            if not df_matrix.empty:
                df_matrix["Type_Prestation_Clinique"] = df_matrix["Type_Prestation_Clinique"].map(
                    {0: "No Clinic", 1: "Clinic Visited"}
                )
                risk_order = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
                disease_order = ["None", "Asthma", "Musculoskeletal", "Diabetes", "Hypertension"]

                df_matrix = df_matrix.dropna(subset=["Risk_Level", "Disease_Type"])

                fig_3d = px.scatter_3d(
                    df_matrix,
                    x="Disease_Type",
                    y="Type_Prestation_Clinique",
                    z="Risk_Level",
                    size="Count",
                    size_max=45,
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

                # Light‑theme cube without overlapping axis titles
                fig_3d.update_layout(
                    height=420,
                    margin=dict(l=0, r=0, b=0, t=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    scene=dict(
                        xaxis=dict(
                            title="",                     # no title to avoid overlap
                            showbackground=True,
                            backgroundcolor="rgba(255,255,255,0.85)",
                            gridcolor="#cbd5e1",
                            zeroline=False
                        ),
                        yaxis=dict(
                            title="",
                            showbackground=True,
                            backgroundcolor="rgba(255,255,255,0.85)",
                            gridcolor="#cbd5e1",
                            zeroline=False
                        ),
                        zaxis=dict(
                            title="",
                            showbackground=True,
                            backgroundcolor="rgba(255,255,255,0.85)",
                            gridcolor="#cbd5e1",
                            zeroline=False
                        ),
                        # Draw a subtle wireframe around the data boundaries to emphasize the "cube"
                        annotations=[
                            # We'll add invisible traces as a simple workaround; instead we can set
                            # the aspectmode and add a transparent outer box later. But for simplicity,
                            # we rely on the background planes – they already form a cube.
                        ],
                        camera=dict(eye=dict(x=1.6, y=1.6, z=1.2))
                    ),
                    coloraxis_colorbar=dict(
                        title="Avg Cost (TND)",
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=250,
                        yanchor="top", y=0.9, xanchor="left", x=1.05
                    )
                )

                # Add faint cube edges to reinforce the 3D structure
                # (corners of the categorical space)
                x_cats = disease_order
                y_cats = ["No Clinic", "Clinic Visited"]
                z_cats = risk_order
                # Draw lines along the outer edges
                for x in [x_cats[0], x_cats[-1]]:
                    for y in y_cats:
                        fig_3d.add_scatter3d(
                            x=[x, x], y=[y, y], z=[z_cats[0], z_cats[-1]],
                            mode='lines',
                            line=dict(color='#94a3b8', width=1),
                            showlegend=False,
                            hoverinfo='skip'
                        )
                for y in [y_cats[0], y_cats[-1]]:
                    for z in [z_cats[0], z_cats[-1]]:
                        fig_3d.add_scatter3d(
                            x=[x_cats[0], x_cats[-1]], y=[y, y], z=[z, z],
                            mode='lines',
                            line=dict(color='#94a3b8', width=1),
                            showlegend=False,
                            hoverinfo='skip'
                        )
                for z in [z_cats[0], z_cats[-1]]:
                    for x in [x_cats[0], x_cats[-1]]:
                        fig_3d.add_scatter3d(
                            x=[x, x], y=[y_cats[0], y_cats[-1]], z=[z, z],
                            mode='lines',
                            line=dict(color='#94a3b8', width=1),
                            showlegend=False,
                            hoverinfo='skip'
                        )

                fig_3d.update_traces(
                    marker=dict(
                        sizemin=6,
                        line=dict(width=1, color='white'),
                        opacity=0.9
                    ),
                    hovertemplate='<b>%{x}</b><br>Clinic: %{y}<br>Risk: %{z}<br>Count: %{marker.size}<br>Avg Cost: %{marker.color:,.2f} TND<extra></extra>',
                    selector=dict(type='scatter3d')
                )

                st.plotly_chart(fig_3d, use_container_width=True)

        except Exception as e:
            st.error(f"Could not cross‑reference usage matrices: {e}")

    st.markdown("---")

    # --- High Risk Registry ---
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <span style="font-weight:600; font-size:1.2rem; color:#1e293b;">Critical Priority Registry (High‑Risk Workers)</span>
    </div>
    """, unsafe_allow_html=True)

    try:
        response = requests.get(f"{BASE_URL}/high-risk")
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.info("No high‑risk individuals currently flagged.")
    except:
        st.error("Database connection dropped during directory scan.")


elif page == "Employee Registry":
    # --- Page header with icon ---
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.8rem; margin-bottom: 1rem;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 00-3-3.87" />
            <path d="M16 3.13a4 4 0 010 7.75" />
        </svg>
        <h1 style="font-size: 1.8rem; font-weight: 600; color: #0f172a; margin: 0;">Employee Health Registry</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # --- Employee Lookup ---
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Profile Deep‑Dive</span>
    </div>
    """, unsafe_allow_html=True)

    matricule_search = st.text_input("Scan Employee Matricule Number", placeholder="Enter ID...", label_visibility="collapsed")

    if matricule_search:
        try:
            emp_response = requests.get(f"{BASE_URL}/employee/{matricule_search}")
            if emp_response.status_code == 200:
                emp_data = emp_response.json()
                if "error" in emp_data:
                    st.warning(emp_data["error"])
                else:
                    # --- Employee KPI cards ---
                    col_age, col_cost, col_visits = st.columns(3)
                    with col_age:
                        st.markdown(f"""
                        <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
                            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="12" cy="12" r="10" />
                                    <polyline points="12 6 12 12 16 14" />
                                </svg>
                                <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Age</span>
                            </div>
                            <div style="font-size:2.3rem; font-weight:700; background: linear-gradient(135deg, #6366f1, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{emp_data['employee_age']}</div>
                            <div style="color:#475569; font-size:0.85rem; margin-top:0.3rem;">Years</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_cost:
                        st.markdown(f"""
                        <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
                            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
                                </svg>
                                <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Predicted Annual Cost</span>
                            </div>
                            <div style="font-size:2.3rem; font-weight:700; background: linear-gradient(135deg, #6366f1, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{emp_data['predicted_cost']:,.0f}</div>
                            <div style="color:#475569; font-size:0.85rem; margin-top:0.3rem;">TND</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_visits:
                        # Show visit features as a mini card with counts
                        features = emp_data.get("visit_features", {})
                        features_html = "".join([f"<span style='display: inline-block; background: #eef2ff; color: #4338ca; padding: 0.2rem 0.6rem; border-radius: 8px; margin: 0.2rem; font-size:0.8rem;'>{k}: {v}</span>" for k,v in features.items()])
                        st.markdown(f"""
                        <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
                            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                                    <polyline points="14 2 14 8 20 8" />
                                    <line x1="16" y1="13" x2="8" y2="13" />
                                    <line x1="16" y1="17" x2="8" y2="17" />
                                </svg>
                                <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600;">Used Services</span>
                            </div>
                            <div style="margin-top:0.8rem;">{features_html}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # --- Claims table ---
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:0.6rem; margin: 1.5rem 0 0.5rem 0;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                            <line x1="16" y1="2" x2="16" y2="6" />
                            <line x1="8" y1="2" x2="8" y2="6" />
                            <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                        <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Historical Claims Ledger</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(emp_data["profile"]), use_container_width=True, hide_index=True)
            else:
                st.error("Employee not found in registry.")
        except Exception as e:
            st.error(f"Registry processing failure: {e}")

    st.markdown("---")

    # --- Trend charts row ---
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
            <span style="font-weight:600; font-size:1rem; color:#1e293b;">Total Cost Evolution</span>
        </div>
        """, unsafe_allow_html=True)
        data = requests.get(f"{BASE_URL}/cost-trend").json()
        df = pd.DataFrame(data)
        if not df.empty:
            fig = px.line(df, x="Month", y="Total_Depense", markers=True)
            fig.update_traces(line_color="#6366f1", line_width=2.5, marker=dict(size=6, color="#6366f1"))
            fig.update_layout(height=350, margin=dict(t=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#475569"), xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0"))
            st.plotly_chart(fig, use_container_width=True)

    with col_t2:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
            <span style="font-weight:600; font-size:1rem; color:#1e293b;">Average Cost Trend</span>
        </div>
        """, unsafe_allow_html=True)
        data = requests.get(f"{BASE_URL}/avg-cost-trend").json()
        df = pd.DataFrame(data)
        if not df.empty:
            fig = px.line(df, x="Month", y="Total_Depense", markers=True)
            fig.update_traces(line_color="#f59e0b", line_width=2.5, marker=dict(size=6, color="#f59e0b"))
            fig.update_layout(height=350, margin=dict(t=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#475569"), xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0"))
            st.plotly_chart(fig, use_container_width=True)

        # --- Risk Evolution Over Time (absolute stacked area) ---
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.6rem; margin: 1.5rem 0 0.5rem 0;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Risk Evolution Over Time</span>
    </div>
    """, unsafe_allow_html=True)

    data = requests.get(f"{BASE_URL}/risk-trend").json()
    df = pd.DataFrame(data)

    if not df.empty:
        # Original logic: absolute counts, not percentages
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
                "High Risk": "#1e3a8a"
            }
        )

        fig_risk.update_traces(opacity=0.85)
        fig_risk.update_layout(
            height=350,
            margin=dict(t=15),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#475569"),
            yaxis_title="Number of Employees",
            xaxis=dict(gridcolor="#e2e8f0"),
            yaxis=dict(gridcolor="#e2e8f0")
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    # --- Clinic usage trend ---
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.6rem; margin: 1.5rem 0 0.5rem 0;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <line x1="3" y1="9" x2="21" y2="9" />
            <line x1="9" y1="21" x2="9" y2="9" />
        </svg>
        <span style="font-weight:600; font-size:1.15rem; color:#1e293b;">Service Line Utilization</span>
    </div>
    """, unsafe_allow_html=True)

    data = requests.get(f"{BASE_URL}/clinic-trend").json()
    df = pd.DataFrame(data)
    if not df.empty:
        fig_clinic = px.area(df, x="Month", y="Count", color="Type_Prestation",
                             color_discrete_sequence=["#93c5fd", "#6366f1", "#1e3a8a", "#312e81"])
        fig_clinic.update_traces(opacity=0.8)
        fig_clinic.update_layout(height=350, margin=dict(t=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                 font=dict(color="#475569"), xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0"))
        st.plotly_chart(fig_clinic, use_container_width=True)



# ==========================================
# PAGE 3: NEURAL SIMULATION
# ==========================================
elif page == "Neural Simulation":
    # --- Page header with icon ---
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.8rem; margin-bottom: 1rem;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="6" />
            <circle cx="12" cy="12" r="2" />
            <line x1="12" y1="2" x2="12" y2="6" />
            <line x1="12" y1="18" x2="12" y2="22" />
            <line x1="2" y1="12" x2="6" y2="12" />
            <line x1="18" y1="12" x2="22" y2="12" />
        </svg>
        <h1 style="font-size: 1.8rem; font-weight: 600; color: #0f172a; margin: 0;">What‑If Cost Simulator</h1>
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
            Chronic_musculo = st.radio("Musculoskeletal Anomalies", yes_no, horizontal=True)

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
        # Vector transformations (unchanged)
        asthme_bin = to_binary(Chronic_asthme)
        diabete_bin = to_binary(Chronic_diabete)
        hyper_bin = to_binary(Chronic_hypertension)
        musculo_bin = to_binary(Chronic_musculo)

        aucune_flag = 1 if sum([asthme_bin, diabete_bin, hyper_bin, musculo_bin]) == 0 else 0

        payload = {
            "Dependent_Age": Dependent_Age,
            "Chronic_Disease_asthme": asthme_bin,
            "Chronic_Disease_aucune": aucune_flag,
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
            res = requests.post(f"{BASE_URL}/what-if", json=payload).json()

            st.markdown("### 📌 What‑If Comparison")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
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
                <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
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
                <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
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
                <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
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
                <div style="background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2;">
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
                    icon_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>'
                    color = "#10b981"
                    bg = "rgba(16, 185, 129, 0.08)"
                elif risk_level == "Medium Risk":
                    icon_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>'
                    color = "#f59e0b"
                    bg = "rgba(245, 158, 11, 0.08)"
                else:
                    icon_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>'
                    color = "#ef4444"
                    bg = "rgba(239, 68, 68, 0.08)"

                st.markdown(f"""
                <div style="background: {bg}; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e9eef2; text-align: center;">
                    <div style="display:flex; align-items:center; justify-content:center; gap:0.5rem; margin-bottom:0.5rem;">
                        {icon_svg}
                        <span style="color:{color}; font-weight:600; font-size:0.9rem; text-transform:uppercase;">{risk_level}</span>
                    </div>
                    <div style="font-size:1.8rem; font-weight:700; color: {color};">{risk_level}</div>
                </div>
                """, unsafe_allow_html=True)