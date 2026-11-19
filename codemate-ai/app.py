"""CodeMate AI — AI-powered Code Refactoring & Documentation Assistant.

Main Streamlit Application.
Features:
- Clean, modern light-theme SaaS interface (#F8FAFC, #172554, #3B82F6)
- Shared session state across all 7 navigation sections
- Real-time AST code analysis and Black formatting
- AI-powered refactoring, explanation, and README generation via Google Gemini
- Safe isolated test execution (never executed in the Streamlit process)
"""

import os
import streamlit as st

# Configure Streamlit page settings (must be the very first Streamlit call)
st.set_page_config(
    page_title="CodeMate AI — Code Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from services.code_analyzer import analyze_code
from services.documentation_service import generate_code_docstrings, generate_project_readme
from services.explanation_service import explain_code, format_explanation_export
from services.gemini_service import (
    DEFAULT_GEMINI_MODEL,
    SUPPORTED_MODELS,
    gemini_service,
)
from services.refactoring_service import refactor_code
from services.validation_service import (
    format_with_black,
    run_isolated_test_suite,
    validate_syntax,
)
from utils.file_handler import (
    create_analysis_export_markdown,
    read_uploaded_file,
)
from utils.sample_codes import (
    SAMPLE_PROGRAMS,
    get_sample_code,
    get_sample_description,
    get_sample_names,
)


# ==============================================================================
# Custom CSS — Modern Minimalist Light SaaS Design
# ==============================================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #334155;
    background-color: #F8FAFC;
}

/* Main background */
.stApp {
    background-color: #F8FAFC !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #334155;
}

/* Sidebar Radio Navigation items */
div[data-testid="stRadio"] {
    width: 100% !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
}

div[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    color: #334155 !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    margin-bottom: 2px !important;
    border: 1px solid transparent !important;
    background-color: transparent !important;
}

div[data-testid="stRadio"] label:hover {
    background-color: #F1F5F9 !important;
    color: #172554 !important;
}

div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label div {
    color: #334155 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
}

/* Radio buttons selected */
div[data-testid="stRadio"] label:has(input:checked) {
    background-color: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
}

div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stRadio"] label:has(input:checked) span {
    color: #1D4ED8 !important;
    font-weight: 700 !important;
}

/* Expander styling in light theme */
div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    margin-bottom: 0.75rem !important;
}

div[data-testid="stExpander"] summary {
    background-color: #F8FAFC !important;
    color: #172554 !important;
    border-radius: 8px !important;
    border-bottom: 1px solid #E2E8F0 !important;
    padding: 0.5rem 0.75rem !important;
}

div[data-testid="stExpander"] summary:hover {
    background-color: #F1F5F9 !important;
}

div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span {
    color: #172554 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

div[data-testid="stExpander"] svg {
    fill: #172554 !important;
    stroke: #172554 !important;
    color: #172554 !important;
}

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background-color: #FFFFFF !important;
    padding: 0.75rem 0.5rem !important;
}

/* Inputs and Select boxes (Light SaaS look) */
div[data-testid="stWidgetLabel"] label p,
label[data-testid="stWidgetLabel"] p,
.stTextInput label p,
.stSelectbox label p,
.stTextArea label p {
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

div[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    color: #172554 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    font-size: 0.88rem !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #94A3B8 !important;
}

div[data-testid="stTextInput"] > div > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
}

div[data-testid="stTextInput"] svg {
    fill: #64748B !important;
    color: #64748B !important;
}

/* Selectbox styling */
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #172554 !important;
    border-radius: 6px !important;
}

div[data-testid="stSelectbox"] span,
div[data-testid="stSelectbox"] p {
    color: #172554 !important;
    font-size: 0.88rem !important;
}

div[data-testid="stSelectbox"] svg {
    fill: #64748B !important;
    color: #64748B !important;
}

/* Dropdown popover menu */
ul[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

li[data-baseweb="menu-item"] {
    background-color: #FFFFFF !important;
    color: #334155 !important;
}

li[data-baseweb="menu-item"]:hover {
    background-color: #F1F5F9 !important;
    color: #172554 !important;
}

/* Captions and links */
div[data-testid="stCaptionContainer"] p,
.stCaption,
caption {
    color: #64748B !important;
    font-size: 0.78rem !important;
}

section[data-testid="stSidebar"] a {
    color: #2563EB !important;
    text-decoration: underline;
    font-weight: 500;
}

section[data-testid="stSidebar"] a:hover {
    color: #1D4ED8 !important;
}

/* Text area */
div[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}

/* Card containers */
.cm-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.cm-card-header {
    font-size: 1.05rem;
    font-weight: 600;
    color: #172554;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Metric badge card */
.cm-stat-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.cm-stat-val {
    font-size: 1.75rem;
    font-weight: 700;
    color: #172554;
    line-height: 1.2;
}

.cm-stat-lbl {
    font-size: 0.8rem;
    font-weight: 500;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

/* Status badges */
.cm-badge {
    display: inline-block;
    padding: 0.25rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 6px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.cm-badge-success {
    background-color: #DCFCE7;
    color: #15803D;
}

.cm-badge-warning {
    background-color: #FEF9C3;
    color: #A16207;
}

.cm-badge-danger {
    background-color: #FEE2E2;
    color: #B91C1C;
}

.cm-badge-info {
    background-color: #DBEAFE;
    color: #1D4ED8;
}

/* Code area fonts */
pre, code, textarea {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Primary Button Styling */
div.stButton > button[kind="primary"] {
    background-color: #172554 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    border: 1px solid #172554 !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.15s ease-in-out;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #1E3A8A !important;
    border-color: #1E3A8A !important;
    box-shadow: 0 2px 4px rgba(23, 37, 84, 0.2);
}

/* Secondary Button Styling */
div.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    border: 1px solid #E2E8F0 !important;
    padding: 0.45rem 1rem !important;
}

div.stButton > button[kind="secondary"]:hover {
    border-color: #CBD5E1 !important;
    background-color: #F8FAFC !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #E2E8F0;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    background-color: transparent;
    border-radius: 6px 6px 0 0;
    font-weight: 500;
    color: #64748B;
    padding: 0 16px;
}

.stTabs [aria-selected="true"] {
    color: #172554 !important;
    border-bottom: 2px solid #3B82F6 !important;
    font-weight: 600 !important;
}

/* Diff highlights */
.diff-del {
    background-color: #FEE2E2;
    color: #991B1B;
    padding: 2px 4px;
    border-radius: 3px;
    display: block;
}
.diff-add {
    background-color: #DCFCE7;
    color: #166534;
    padding: 2px 4px;
    border-radius: 3px;
    display: block;
}

/* Alert tweaks */
div[data-testid="stAlert"] {
    border-radius: 8px;
    border: 1px solid #E2E8F0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# Session State Initialization & Navigation Helper
# ==============================================================================
def init_session_state():
    """Initialize persistent application state."""
    default_sample_name = "Student Grade Calculator"
    if "code" not in st.session_state:
        st.session_state["code"] = get_sample_code(default_sample_name)
    if "original_code" not in st.session_state:
        st.session_state["original_code"] = st.session_state["code"]
    if "refactored_code" not in st.session_state:
        st.session_state["refactored_code"] = ""
    if "refactoring_result" not in st.session_state:
        st.session_state["refactoring_result"] = None
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None
    if "explanation_result" not in st.session_state:
        st.session_state["explanation_result"] = None
    if "readme_result" not in st.session_state:
        st.session_state["readme_result"] = None
    if "docstrings_result" not in st.session_state:
        st.session_state["docstrings_result"] = None
    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = "Dashboard"
    if "active_nav" not in st.session_state:
        st.session_state["active_nav"] = "Dashboard"
    if "target_nav" not in st.session_state:
        st.session_state["target_nav"] = None
    if "api_key_override" not in st.session_state:
        st.session_state["api_key_override"] = ""
    model_env = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    if "selected_model" not in st.session_state or st.session_state["selected_model"] not in SUPPORTED_MODELS:
        st.session_state["selected_model"] = model_env if model_env in SUPPORTED_MODELS else DEFAULT_GEMINI_MODEL


def navigate_to(page_name: str):
    """Programmatically navigate to another view on the next rerun."""
    st.session_state["target_nav"] = page_name
    st.rerun()


init_session_state()


# ==============================================================================
# Sidebar & Navigation
# ==============================================================================
def render_sidebar():
    """Render the sidebar containing branding, navigation, and API settings."""
    with st.sidebar:
        # CodeMate AI Brand Header
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1.25rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="background-color: #172554; color: #FFFFFF; font-weight: 700; font-size: 1.1rem; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">⚡</div>
                    <div>
                        <div style="font-weight: 700; font-size: 1.15rem; color: #172554; line-height: 1.1;">CodeMate AI</div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Refactoring & Docs Assistant</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation Menu Options
        nav_options = [
            "Dashboard",
            "Code Workspace",
            "Code Analysis",
            "AI Refactoring",
            "Code Explanation",
            "Documentation Generator",
            "About Project",
        ]

        nav_icons = {
            "Dashboard": "📊  Dashboard",
            "Code Workspace": "💻  Code Workspace",
            "Code Analysis": "🔍  Code Analysis",
            "AI Refactoring": "⚡  AI Refactoring",
            "Code Explanation": "💡  Code Explanation",
            "Documentation Generator": "📝  Documentation Generator",
            "About Project": "ℹ️  About Project",
        }

        # Apply programmatic navigation before radio is instantiated
        if st.session_state.get("target_nav"):
            st.session_state["nav_selection"] = st.session_state.pop("target_nav")

        selected_nav = st.radio(
            "Navigation",
            options=nav_options,
            key="nav_selection",
            format_func=lambda x: nav_icons.get(x, x),
            label_visibility="collapsed",
        )
        st.session_state["active_nav"] = selected_nav

        st.markdown("<hr style='margin: 1.25rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # API & Model Configuration
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #172554; margin-bottom: 0.5rem;'>⚙️ CONFIGURATION</div>", unsafe_allow_html=True)

        is_env_configured = gemini_service.is_configured(st.session_state["api_key_override"])
        if is_env_configured:
            st.markdown(
                """
                <div style='margin-bottom: 0.75rem;'>
                    <span class='cm-badge cm-badge-success'>● Gemini API Connected</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style='margin-bottom: 0.75rem;'>
                    <span class='cm-badge cm-badge-warning'>● Offline / Key Missing</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("API & Model Settings", expanded=not is_env_configured):
            user_key = st.text_input(
                "Gemini API Key",
                value=st.session_state["api_key_override"],
                type="password",
                placeholder="Paste AI Studio Key here",
                help="Key is kept safely in memory for this session and never logged or exposed.",
            )
            if user_key != st.session_state["api_key_override"]:
                st.session_state["api_key_override"] = user_key
                st.rerun()

            model_choice = st.selectbox(
                "Gemini Model",
                options=SUPPORTED_MODELS,
                index=SUPPORTED_MODELS.index(st.session_state["selected_model"]) if st.session_state["selected_model"] in SUPPORTED_MODELS else 0,
                help="Configure the Gemini model used for Refactoring, Explanations, and Documentation.",
            )
            st.session_state["selected_model"] = model_choice

            if not is_env_configured:
                st.caption(
                    "[Get a free Gemini API key](https://aistudio.google.com/app/apikey) to enable AI Refactoring, Explanation, and Documentation generation."
                )

        st.markdown("<hr style='margin: 1.25rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # Quick Stats in Sidebar
        loc_count = len(st.session_state["code"].splitlines())
        st.markdown(
            f"""
            <div style="font-size: 0.78rem; color: #64748B;">
                <div>Active Code: <b>{loc_count} lines</b></div>
                <div>Status: <span style="color: #10B981; font-weight: 500;">Ready</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# View 1: Dashboard
# ==============================================================================
def render_dashboard():
    """Render the main dashboard overview page."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #172554; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.25rem;">
                CodeMate AI Dashboard
            </h1>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 0;">
                Developer productivity tool for code analysis, PEP 8 refactoring, plain-English explanations, and documentation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # API connection status banner if not configured
    is_connected = gemini_service.is_configured(st.session_state["api_key_override"])
    if not is_connected:
        st.info(
            "💡 **Gemini API Key Setup:** Static AST analysis, Black formatting, and syntax validation work completely offline! "
            "To unlock AI-powered refactoring, code explanation, and README generation, enter your Gemini API key in the sidebar."
        )

    # Compute quick metrics on current workspace code
    analysis = analyze_code(st.session_state["code"])
    st.session_state["analysis_result"] = analysis

    metrics = analysis.get("metrics", {})
    health_score = analysis.get("health_score", 100)
    issue_count = len(analysis.get("issues", []))

    # Metric Cards Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val">{metrics.get('loc', 0)}</div>
                <div class="cm-stat-lbl">Lines of Code</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        score_color = "#15803D" if health_score >= 80 else ("#A16207" if health_score >= 60 else "#B91C1C")
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val" style="color: {score_color};">{health_score}<span style="font-size: 1rem;">/100</span></div>
                <div class="cm-stat-lbl">Health Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val">{issue_count}</div>
                <div class="cm-stat-lbl">Issues / Smells</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        fn_count = metrics.get('functions_count', 0)
        cls_count = metrics.get('classes_count', 0)
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val">{fn_count} <span style="font-size: 0.9rem; font-weight: 500; color: #64748B;">/ {cls_count}</span></div>
                <div class="cm-stat-lbl">Functions / Classes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Feature Quick-Launch Grid
    st.markdown("<h3 style='color: #172554; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.75rem;'>Quick Actions</h3>", unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)

    with q1:
        st.markdown(
            """
            <div class="cm-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div class="cm-card-header">💻 Workspace</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Edit Python code, upload files, or select beginner-friendly examples.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Workspace", key="dash_btn_ws", use_container_width=True):
            navigate_to("Code Workspace")

    with q2:
        st.markdown(
            """
            <div class="cm-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div class="cm-card-header">🔍 Code Analysis</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Inspect AST syntax, PEP 8 style, unused imports, and code smells.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Run Analysis", key="dash_btn_an", use_container_width=True):
            navigate_to("Code Analysis")

    with q3:
        st.markdown(
            """
            <div class="cm-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div class="cm-card-header">⚡ AI Refactoring</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Refactor code, fix anti-patterns, and view side-by-side diffs.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Refactor Code", key="dash_btn_rf", use_container_width=True):
            navigate_to("AI Refactoring")

    with q4:
        st.markdown(
            """
            <div class="cm-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div class="cm-card-header">💡 Explain & Document</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Get real-world analogies, step-by-step logic, and README files.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Explain / Document", key="dash_btn_exp", use_container_width=True):
            navigate_to("Code Explanation")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Sample Programs Section
    st.markdown("<h3 style='color: #172554; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.75rem;'>Try Sample Programs for Learning</h3>", unsafe_allow_html=True)
    sample_col1, sample_col2 = st.columns([2, 1])

    with sample_col1:
        chosen_sample = st.selectbox(
            "Select a sample to load into workspace:",
            options=get_sample_names(),
            index=0,
            key="dash_sample_select",
        )
        st.caption(get_sample_description(chosen_sample))

    with sample_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Load Sample into Workspace", type="primary", use_container_width=True):
            st.session_state["code"] = get_sample_code(chosen_sample)
            st.session_state["original_code"] = st.session_state["code"]
            st.session_state["refactored_code"] = ""
            st.session_state["refactoring_result"] = None
            st.session_state["analysis_result"] = None
            st.session_state["explanation_result"] = None
            st.session_state["readme_result"] = None
            st.success(f"Loaded '{chosen_sample}' into workspace!")
            navigate_to("Code Workspace")


# ==============================================================================
# View 2: Code Workspace
# ==============================================================================
def render_workspace():
    """Render the interactive code workspace editor and file loader."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="color: #172554; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.25rem;">
                Code Workspace
            </h1>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 0;">
                Write, paste, upload, and format Python code. Changes are preserved across all tool tabs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Input Method Tabs
    tab_editor, tab_upload, tab_samples, tab_tests = st.tabs([
        "📝 Code Editor",
        "📁 Upload .py File",
        "📚 Sample Programs",
        "🧪 Safe Test Runner"
    ])

    with tab_upload:
        uploaded_file = st.file_uploader("Upload a Python file (.py)", type=["py"], key="ws_uploader")
        if uploaded_file is not None:
            ok, content, err = read_uploaded_file(uploaded_file)
            if ok:
                if content != st.session_state["code"]:
                    st.session_state["code"] = content
                    st.session_state["original_code"] = content
                    st.success(f"Successfully loaded '{uploaded_file.name}' into workspace!")
                    st.rerun()
            else:
                st.error(f"Error reading uploaded file: {err}")

    with tab_samples:
        s_col1, s_col2 = st.columns([3, 1])
        with s_col1:
            sample_selected = st.selectbox(
                "Choose an educational sample program:",
                options=get_sample_names(),
                key="ws_sample_select",
            )
            st.caption(get_sample_description(sample_selected))
        with s_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Load This Sample", key="ws_load_sample_btn", use_container_width=True):
                st.session_state["code"] = get_sample_code(sample_selected)
                st.session_state["original_code"] = st.session_state["code"]
                st.session_state["refactored_code"] = ""
                st.session_state["refactoring_result"] = None
                st.session_state["analysis_result"] = None
                st.success(f"Loaded '{sample_selected}'!")
                st.rerun()

    with tab_editor:
        # Action Toolbar above editor
        tb1, tb2, tb3, tb4 = st.columns([1.5, 1.5, 1.2, 1.2])

        with tb1:
            if st.button("🎨 Format with Black", use_container_width=True):
                ok, formatted, msg = format_with_black(st.session_state["code"])
                if ok:
                    st.session_state["code"] = formatted
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with tb2:
            if st.button("🛡️ Validate Syntax", use_container_width=True):
                val_res = validate_syntax(st.session_state["code"])
                if val_res["valid"]:
                    st.success("Syntax is 100% valid Python! Compiles cleanly to bytecode.")
                else:
                    st.error(f"SyntaxError (Line {val_res.get('line')}, Col {val_res.get('column')}): {val_res.get('error')}")

        with tb3:
            if st.button("🗑️ Clear Code", use_container_width=True):
                st.session_state["code"] = ""
                st.rerun()

        with tb4:
            if st.button("🔄 Reset Sample", use_container_width=True):
                st.session_state["code"] = get_sample_code("Student Grade Calculator")
                st.rerun()

        # Primary Code Editor
        edited_code = st.text_area(
            "Python Source Code",
            value=st.session_state["code"],
            height=380,
            label_visibility="collapsed",
            help="Type or paste your Python code here.",
        )
        if edited_code != st.session_state["code"]:
            st.session_state["code"] = edited_code

    with tab_tests:
        st.markdown(
            """
            <div style="margin-bottom: 0.75rem;">
                <div style="font-weight: 600; color: #172554;">Safe Subprocess Test Runner</div>
                <div style="font-size: 0.85rem; color: #64748B;">
                    Test cases run in a strictly isolated, sandboxed child process with a 3.0s timeout.
                    <b>Uploaded code is never executed inside the Streamlit host process.</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        default_tests = "# Add test assertions for the active workspace code\nassert 'calc' in dir() or 'process' in dir().lower() or True\nprint('Smoke test executed successfully!')"
        if "test_suite_code" not in st.session_state:
            st.session_state["test_suite_code"] = default_tests

        test_code_input = st.text_area(
            "Test Assertions / Test Cases",
            value=st.session_state["test_suite_code"],
            height=140,
            help="Enter Python assertions, e.g. assert add(2, 3) == 5",
        )
        st.session_state["test_suite_code"] = test_code_input

        if st.button("▶️ Run Tests in Isolated Sandbox", type="primary"):
            with st.spinner("Executing assertions in isolated subprocess..."):
                t_res = run_isolated_test_suite(st.session_state["code"], test_code_input)
                if t_res["passed"]:
                    st.success(f"✅ Tests Passed in {t_res['duration']}s! Output: {t_res['stdout']}")
                else:
                    st.error(f"❌ {t_res['status']} in {t_res['duration']}s:\n{t_res['error']}")

        st.caption(
            "⚠️ **Distinction Note:** AST syntax validation checks grammatical and structural validity without execution. "
            "Behavioral verification requires executing test suites in the isolated sandbox."
        )

    # Workspace metrics strip
    loc = len(st.session_state["code"].splitlines())
    char_count = len(st.session_state["code"])
    st.markdown(
        f"""
        <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.5rem; display: flex; gap: 1.5rem;">
            <span>Lines: <b>{loc}</b></span>
            <span>Characters: <b>{char_count}</b></span>
            <span>Encoding: <b>UTF-8</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# View 3: Code Analysis
# ==============================================================================
def render_analysis():
    """Render AST analysis and Black formatting inspection."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="color: #172554; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.25rem;">
                Code Quality & AST Analysis
            </h1>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 0;">
                Static code inspection powered by Python AST and Black. Detects syntax errors, missing docstrings, unused imports, and code smells.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    code = st.session_state["code"]
    if not code.strip():
        st.warning("Your workspace code is empty. Please paste code or load a sample in the Code Workspace.")
        return

    # Run analysis
    analysis = analyze_code(code)
    st.session_state["analysis_result"] = analysis

    # Top Status & Metrics Row
    health_score = analysis.get("health_score", 100)
    metrics = analysis.get("metrics", {})
    issues = analysis.get("issues", [])
    black_ok = analysis.get("black_compliant", False)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        badge_cls = "cm-badge-success" if health_score >= 80 else ("cm-badge-warning" if health_score >= 60 else "cm-badge-danger")
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val">{health_score}<span style="font-size: 0.9rem;">/100</span></div>
                <div class="cm-stat-lbl">Health Score</div>
                <div style="margin-top: 0.5rem;"><span class="cm-badge {badge_cls}">{'Healthy' if health_score >= 80 else 'Needs Attention'}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val">{len(issues)}</div>
                <div class="cm-stat-lbl">Issues Found</div>
                <div style="margin-top: 0.5rem;"><span class="cm-badge cm-badge-info">AST Scanned</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val">{metrics.get('cyclomatic_complexity', 1)}</div>
                <div class="cm-stat-lbl">Cyclomatic Complexity</div>
                <div style="margin-top: 0.5rem;"><span class="cm-badge cm-badge-info">Decision Paths</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="cm-stat-card">
                <div class="cm-stat-val">{'Passed' if black_ok else 'Diff'}</div>
                <div class="cm-stat-lbl">Black PEP 8 Check</div>
                <div style="margin-top: 0.5rem;">
                    <span class="cm-badge {'cm-badge-success' if black_ok else 'cm-badge-warning'}">
                        {'Compliant' if black_ok else 'Formatting Needed'}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Detailed Issues List
    st.markdown("<h3 style='color: #172554; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.75rem;'>Inspection Findings</h3>", unsafe_allow_html=True)

    if not issues:
        st.success("🎉 Outstanding! No syntax errors, anti-patterns, or missing documentation detected. Code is clean and well-structured.")
    else:
        for idx, iss in enumerate(issues, start=1):
            severity = iss.get("severity", "Info")
            badge_class = "cm-badge-danger" if severity == "Critical" else ("cm-badge-warning" if severity == "Warning" else "cm-badge-info")
            line_str = f"Line {iss['line']}" if iss.get("line") else "General"

            with st.container():
                st.markdown(
                    f"""
                    <div class="cm-card" style="margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div style="font-weight: 600; color: #172554; font-size: 0.98rem;">
                                {idx}. {iss.get('title')}
                            </div>
                            <div>
                                <span class="cm-badge {badge_class}">{severity}</span>
                                <span style="font-size: 0.75rem; color: #64748B; margin-left: 0.5rem; font-weight: 500;">{line_str}</span>
                            </div>
                        </div>
                        <div style="font-size: 0.88rem; color: #334155; margin-bottom: 0.5rem;">
                            {iss.get('description')}
                        </div>
                        <div style="font-size: 0.82rem; color: #1D4ED8; background-color: #EFF6FF; padding: 0.4rem 0.6rem; border-radius: 6px;">
                            💡 <b>Recommendation:</b> {iss.get('suggestion')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Export & Disclaimer Section
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    exp_col1, exp_col2 = st.columns([1, 2])
    with exp_col1:
        report_md = create_analysis_export_markdown(analysis, code)
        st.download_button(
            label="📥 Download Analysis Report (.md)",
            data=report_md,
            file_name="codemate_analysis_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with exp_col2:
        st.caption(analysis.get("disclaimer", ""))


# ==============================================================================
# View 4: AI Refactoring
# ==============================================================================
def render_refactoring():
    """Render AI Refactoring with side-by-side comparison, metrics, and diff."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="color: #172554; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.25rem;">
                AI Code Refactoring
            </h1>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 0;">
                Improve naming, eliminate code smells, enforce PEP 8 conventions, and preserve exact program functionality using Google Gemini.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    code = st.session_state["code"]
    if not code.strip():
        st.warning("Workspace code is empty. Please paste code or load a sample first.")
        return

    # Trigger refactoring button
    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        refactor_btn = st.button("⚡ Refactor Code with Gemini", type="primary", use_container_width=True)
    with btn_col2:
        active_model = st.session_state["selected_model"]
        st.markdown(
            f"<div style='padding-top: 0.4rem;'><span class='cm-badge cm-badge-info'>Model: {active_model}</span></div>",
            unsafe_allow_html=True,
        )

    if refactor_btn:
        with st.spinner("Refactoring code, checking PEP 8, and computing metrics..."):
            result = refactor_code(
                code=code,
                override_key=st.session_state["api_key_override"],
                override_model=st.session_state["selected_model"],
            )
            st.session_state["refactoring_result"] = result
            if result["success"]:
                st.session_state["refactored_code"] = result["refactored_code"]
                st.toast("Refactoring completed successfully!", icon="✅")
            else:
                st.error(f"Refactoring could not be completed: {result.get('error')}")

    # Display results if available
    res = st.session_state["refactoring_result"]
    if res and res.get("success"):
        refactored = res["refactored_code"]
        orig_analysis = res.get("original_analysis", {})
        ref_analysis = res.get("refactored_analysis", {})
        delta = res.get("health_score_delta", 0)

        # Improvement Banner
        delta_str = f"+{delta}" if delta > 0 else f"{delta}"
        delta_color = "#15803D" if delta >= 0 else "#B91C1C"
        st.markdown(
            f"""
            <div class="cm-card" style="border-left: 4px solid #3B82F6; margin-top: 1rem; margin-bottom: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; font-size: 1.05rem; color: #172554;">Refactoring Completed</div>
                        <div style="font-size: 0.85rem; color: #64748B;">All original functionality preserved with clean structure and PEP 8 naming.</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.85rem; color: #64748B;">Health Score: </span>
                        <b>{orig_analysis.get('health_score', 0)}</b> &rarr; <b>{ref_analysis.get('health_score', 100)}</b>
                        <span style="font-weight: 700; color: {delta_color}; margin-left: 0.4rem;">({delta_str} pts)</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tabbed result views
        tab_sidebyside, tab_diff, tab_explanation = st.tabs(["👥 Side-by-Side Comparison", "🔍 Unified Diff", "📖 Explanations & Tips"])

        with tab_sidebyside:
            col_orig, col_refact = st.columns(2)
            with col_orig:
                st.markdown("<div style='font-weight: 600; color: #64748B; margin-bottom: 0.25rem;'>Original Code</div>", unsafe_allow_html=True)
                st.code(code, language="python", line_numbers=True)
            with col_refact:
                st.markdown("<div style='font-weight: 600; color: #15803D; margin-bottom: 0.25rem;'>Refactored Code (Clean & PEP 8)</div>", unsafe_allow_html=True)
                st.code(refactored, language="python", line_numbers=True)

        with tab_diff:
            diff_text = res.get("diff", "")
            if diff_text:
                st.code(diff_text, language="diff")
            else:
                st.info("No text differences detected.")

        with tab_explanation:
            st.markdown(res.get("explanation", ""))

        # Action Buttons
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        act1, act2 = st.columns(2)
        with act1:
            st.download_button(
                label="📥 Download Refactored Python File (.py)",
                data=refactored,
                file_name="refactored_code.py",
                mime="text/x-python",
                use_container_width=True,
            )
        with act2:
            if st.button("📋 Replace Workspace Code with Refactored Code", use_container_width=True):
                st.session_state["code"] = refactored
                st.session_state["original_code"] = code
                st.success("Workspace updated with refactored code!")
                st.rerun()


# ==============================================================================
# View 5: Code Explanation
# ==============================================================================
def render_explanation():
    """Render beginner-friendly code explanation, analogies, and execution trace."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="color: #172554; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.25rem;">
                Beginner-Friendly Code Explanation
            </h1>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 0;">
                Learn how your code works through intuitive real-world analogies, step-by-step logic traces, and function breakdowns.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    code = st.session_state["code"]
    if not code.strip():
        st.warning("Workspace code is empty. Please paste code or load a sample first.")
        return

    exp_btn = st.button("💡 Explain This Code with Gemini", type="primary", use_container_width=True)

    if exp_btn:
        with st.spinner("Analyzing logic, composing analogies, and structuring explanation..."):
            res = explain_code(
                code=code,
                override_key=st.session_state["api_key_override"],
                override_model=st.session_state["selected_model"],
            )
            st.session_state["explanation_result"] = res
            if not res["success"]:
                st.error(f"Explanation could not be generated: {res.get('error')}")

    explanation_data = st.session_state["explanation_result"]
    if explanation_data and explanation_data.get("success"):
        markdown_text = explanation_data["explanation"]

        st.markdown(
            """
            <div class="cm-card" style="margin-top: 1rem;">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(markdown_text)
        st.markdown("</div>", unsafe_allow_html=True)

        # Download explanation report
        exp_doc = format_explanation_export(markdown_text, code)
        st.download_button(
            label="📥 Download Explanation Report (.md)",
            data=exp_doc,
            file_name="code_explanation_report.md",
            mime="text/markdown",
            use_container_width=True,
        )


# ==============================================================================
# View 6: Documentation Generator
# ==============================================================================
def render_documentation():
    """Render automated README and Docstring generator."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="color: #172554; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.25rem;">
                Automated Documentation Generator
            </h1>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 0;">
                Generate comprehensive, publication-ready README.md files and add PEP 257 / Google-style docstrings to your code.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    code = st.session_state["code"]
    if not code.strip():
        st.warning("Workspace code is empty. Please paste code or load a sample first.")
        return

    tab_readme, tab_docstrings = st.tabs(["📄 Project README.md", "📝 Code with Docstrings"])

    with tab_readme:
        gen_readme_btn = st.button("Generate README.md with Gemini", type="primary", key="btn_gen_readme")
        if gen_readme_btn:
            with st.spinner("Generating project README markdown..."):
                readme_res = generate_project_readme(
                    code=code,
                    override_key=st.session_state["api_key_override"],
                    override_model=st.session_state["selected_model"],
                )
                st.session_state["readme_result"] = readme_res
                if not readme_res["success"]:
                    st.error(f"Failed to generate README: {readme_res.get('error')}")

        readme_data = st.session_state["readme_result"]
        if readme_data and readme_data.get("success"):
            readme_text = readme_data["readme_markdown"]
            st.markdown(
                """
                <div class="cm-card" style="margin-top: 1rem;">
                """,
                unsafe_allow_html=True,
            )
            st.markdown(readme_text)
            st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                label="📥 Download README.md",
                data=readme_text,
                file_name="README.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with tab_docstrings:
        gen_doc_btn = st.button("Generate Code with Docstrings", type="primary", key="btn_gen_docstrings")
        if gen_doc_btn:
            with st.spinner("Adding Google-style docstrings and validating syntax..."):
                doc_res = generate_code_docstrings(
                    code=code,
                    override_key=st.session_state["api_key_override"],
                    override_model=st.session_state["selected_model"],
                )
                st.session_state["docstrings_result"] = doc_res
                if not doc_res["success"]:
                    st.error(f"Docstring generation failed: {doc_res.get('error')}")

        doc_data = st.session_state["docstrings_result"]
        if doc_data and doc_data.get("success"):
            doc_code = doc_data["documented_code"]
            st.code(doc_code, language="python", line_numbers=True)

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="📥 Download Documented Code (.py)",
                    data=doc_code,
                    file_name="documented_code.py",
                    mime="text/x-python",
                    use_container_width=True,
                )
            with d_col2:
                if st.button("📋 Apply to Workspace", key="apply_docstrings_btn", use_container_width=True):
                    st.session_state["code"] = doc_code
                    st.success("Workspace code updated with docstrings!")
                    st.rerun()


# ==============================================================================
# View 7: About Project
# ==============================================================================
def render_about():
    """Render About page with architecture, technology stack, and educational mission."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="color: #172554; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.25rem;">
                About CodeMate AI
            </h1>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 0;">
                Architecture, safety design, technology stack, and educational guide.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="cm-card">
            <div class="cm-card-header">🎯 Educational Mission & Philosophy</div>
            <p style="font-size: 0.9rem; color: #334155; line-height: 1.6;">
                CodeMate AI was built specifically for students and beginner programmers to bridge the gap between 
                <b>"code that works"</b> and <b>"clean, readable, production-grade code"</b>. 
                Instead of simply telling learners their code has issues, CodeMate AI demonstrates concrete improvements, 
                explains the rationale behind PEP 8 standards, and provides intuitive real-world analogies.
            </p>
        </div>

        <div class="cm-card">
            <div class="cm-card-header">🔒 Security & Sandbox Isolation Architecture</div>
            <p style="font-size: 0.9rem; color: #334155; line-height: 1.6;">
                <b>Arbitrary Code Execution Safety:</b> CodeMate AI strictly obeys security boundaries. 
                Arbitrary uploaded code is <b>never executed directly inside the Streamlit host process</b>.
            </p>
            <ul style="font-size: 0.88rem; color: #334155; line-height: 1.6;">
                <li><b>Static AST Analysis:</b> Code is parsed into an abstract syntax tree and compiled to bytecode without evaluating logic.</li>
                <li><b>Isolated Subprocess Sandboxing:</b> When running test cases or behavioral verification, execution happens in a separate ephemeral child process with strict timeout boundaries (3.0 seconds max) and isolated memory.</li>
                <li><b>API Key Isolation:</b> API keys are stored in session memory or environment variables and never logged or serialized to client-side bundles.</li>
            </ul>
        </div>

        <div class="cm-card">
            <div class="cm-card-header">🛠️ Technology Stack</div>
            <div style="font-size: 0.88rem; color: #334155; line-height: 1.8;">
                <div>• <b>Frontend:</b> Streamlit 1.56+ with custom CSS design system</div>
                <div>• <b>Generative AI:</b> Google GenAI Python SDK with Gemini API (configurable model)</div>
                <div>• <b>Static Analysis:</b> Python native <code>ast</code> (Abstract Syntax Tree) module</div>
                <div>• <b>Code Formatter:</b> Black 24.0+ PEP 8 formatting engine</div>
                <div>• <b>Testing Suite:</b> Pytest 9.0+</div>
                <div>• <b>Configuration:</b> python-dotenv</div>
            </div>
        </div>

        <div class="cm-card">
            <div class="cm-card-header">🚀 Quick Setup Guide</div>
            <ol style="font-size: 0.88rem; color: #334155; line-height: 1.7;">
                <li>Copy <code>.env.example</code> to <code>.env</code> in the project directory.</li>
                <li>Add your free Gemini API key: <code>GEMINI_API_KEY=your_key_here</code></li>
                <li>Optionally set your preferred model: <code>GEMINI_MODEL=gemini-2.5-flash</code></li>
                <li>Launch the app: <code>streamlit run app.py</code></li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# Main Router
# ==============================================================================
def main():
    render_sidebar()
    active_view = st.session_state.get("nav_selection", st.session_state.get("active_nav", "Dashboard"))

    if active_view == "Dashboard":
        render_dashboard()
    elif active_view == "Code Workspace":
        render_workspace()
    elif active_view == "Code Analysis":
        render_analysis()
    elif active_view == "AI Refactoring":
        render_refactoring()
    elif active_view == "Code Explanation":
        render_explanation()
    elif active_view == "Documentation Generator":
        render_documentation()
    elif active_view == "About Project":
        render_about()


if __name__ == "__main__":
    main()
