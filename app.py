import io
import json
import os
import tempfile
import time
from pathlib import Path
from PIL import Image
import streamlit as st
from streamlit_paste_button import paste_image_button
from model import analyze, get_backend_info

st.set_page_config(
    page_title="Circuit & Diagram Explainer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling & Keyframe Animations
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header hero */
    .hero-container {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.08) 50%, rgba(236, 72, 153, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }

    /* Upload Container */
    .upload-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 16px;
        padding: 2rem;
        max-width: 820px;
        margin: 0 auto;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
    }

    /* Scanning animation */
    .scanner-box {
        position: relative;
        overflow: hidden;
        border-radius: 12px;
        border: 2px solid #6366f1;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.3);
        margin: 1.5rem auto;
        max-width: 600px;
        text-align: center;
    }

    .laser-line {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, transparent, #ec4899, #a855f7, #6366f1, transparent);
        box-shadow: 0 0 15px #6366f1, 0 0 25px #ec4899;
        animation: scanline 2s ease-in-out infinite alternate;
        z-index: 10;
    }

    @keyframes scanline {
        0% { top: 0%; opacity: 0.8; }
        100% { top: 98%; opacity: 1; }
    }

    .pulse-glow {
        animation: pulseAnimation 2s infinite ease-in-out;
    }

    @keyframes pulseAnimation {
        0%, 100% { opacity: 0.7; transform: scale(0.99); }
        50% { opacity: 1; transform: scale(1.01); }
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        text-align: center;
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #6366f1;
    }
    .metric-lbl {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-top: 0.2rem;
    }
    
    /* Chip tags */
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin: 0.6rem 0 1rem 0;
    }
    .chip-symbol {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        font-size: 0.82rem;
        font-weight: 500;
        border-radius: 20px;
        background: rgba(99, 102, 241, 0.12);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.25);
    }
    .chip-label {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        font-size: 0.78rem;
        font-family: 'JetBrains Mono', monospace;
        border-radius: 6px;
        background: rgba(148, 163, 184, 0.1);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    /* Issue Cards */
    .issue-card {
        padding: 1.1rem 1.3rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border-left: 4px solid;
    }
    .issue-high {
        background: rgba(239, 68, 68, 0.08);
        border-left-color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    .issue-medium {
        background: rgba(245, 158, 11, 0.08);
        border-left-color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    .issue-low {
        background: rgba(59, 130, 246, 0.08);
        border-left-color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Configuration (Simplified without Quick Tips)
st.sidebar.markdown("### ⚙️ Engine Settings")

backend_choice = st.sidebar.radio(
    "Model Backend",
    ["gemini", "ollama"],
    format_func=lambda b: "☁️ Cloud (Gemini API)" if b == "gemini" else "💻 Local (Ollama)",
    help="Switch between cloud inference or local offline open-weights execution.",
)

backend_info = get_backend_info(backend_choice)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Provider:** `{backend_info['provider']}`")
st.sidebar.markdown(f"**Active Model:** `{backend_info['model']}`")
st.sidebar.markdown(f"**Architecture:** `{'Local Offline' if backend_info['offline'] else 'Cloud Hosted'}`")

# Header
st.markdown(
    """
    <div class="hero-container">
        <h1 class="hero-title">⚡ Circuit & Diagram Explainer</h1>
        <p class="hero-subtitle">Reverse-engineer schematics, detect flaws, and generate engineering practice problems powered by <b>Gemma 4</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "active_image" not in st.session_state:
    st.session_state["active_image"] = None
if "image_source" not in st.session_state:
    st.session_state["image_source"] = None
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "analysis_time" not in st.session_state:
    st.session_state["analysis_time"] = None
if "is_analyzing" not in st.session_state:
    st.session_state["is_analyzing"] = False

# ==========================================
# STAGE 1: UPLOAD / PROVIDE CIRCUIT DIAGRAM
# (Visible when no result is currently shown)
# ==========================================
if st.session_state["analysis_result"] is None:
    upload_col_left, upload_col_center, upload_col_right = st.columns([1, 4, 1])

    with upload_col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h3 style="margin-bottom: 0.3rem;">Upload or Paste Circuit Schematic</h3>
                <p style="color: #94a3b8; font-size: 0.95rem;">Provide an engineering diagram, PCB schematic, or handwritten circuit photo.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_paste, tab_upload, tab_sample = st.tabs(["📋 Paste from Clipboard", "📁 Upload File", "⚡ Sample Preset"])

        with tab_paste:
            st.markdown(
                "<p style='color:#94a3b8; font-size: 0.92rem; text-align: center; margin-top: 0.5rem;'>Copy any screenshot or image to your clipboard (`Cmd+Shift+4` or `Win+Shift+S`), then click:</p>",
                unsafe_allow_html=True,
            )
            p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
            with p_col2:
                paste_result = paste_image_button(
                    label="📋 Paste Image from Clipboard",
                    background_color="#6366f1",
                    hover_background_color="#4f46e5",
                    key="clipboard_paste_btn",
                )
            if paste_result.image_data is not None:
                st.session_state["active_image"] = paste_result.image_data
                st.session_state["image_source"] = "Pasted from Clipboard"
                st.toast("Image pasted from clipboard!", icon="📋")

        with tab_upload:
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=["jpg", "jpeg", "png", "webp"],
                help="Supports JPG, PNG, WEBP diagrams",
                key="uploader_input",
            )
            if uploaded_file is not None:
                try:
                    st.session_state["active_image"] = Image.open(uploaded_file)
                    st.session_state["image_source"] = f"Uploaded File: {uploaded_file.name}"
                except Exception as e:
                    st.error(f"Error loading image: {e}")

        with tab_sample:
            st.markdown(
                "<p style='color:#94a3b8; font-size: 0.92rem; text-align: center; margin-top: 0.5rem;'>Test the system immediately with our built-in transistor op-amp diagram:</p>",
                unsafe_allow_html=True,
            )
            sample_img_path = Path("test_images/circuit1.jpeg")
            s_col1, s_col2, s_col3 = st.columns([1, 2, 1])
            with s_col2:
                if sample_img_path.exists():
                    if st.button("🔌 Load 741 Op-Amp Schematic", use_container_width=True):
                        st.session_state["active_image"] = Image.open(sample_img_path)
                        st.session_state["image_source"] = "Built-in Sample: 741 Op-Amp"
                        st.toast("Loaded sample schematic!", icon="🔌")

        # Preview and Trigger Analysis
        if st.session_state["active_image"] is not None:
            active_img = st.session_state["active_image"]
            st.markdown("---")
            st.markdown(
                f"<div style='text-align: center; color: #818cf8; font-size: 0.9rem; font-weight: 500;'>Ready to analyze: {st.session_state['image_source']} ({active_img.width}×{active_img.height} px)</div>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            prev_left, prev_mid, prev_right = st.columns([1, 3, 1])
            with prev_mid:
                st.image(active_img, use_container_width=True)

            action_left, action_btn_col, action_clear_col, action_right = st.columns([1, 2.5, 1, 1])
            with action_btn_col:
                btn_text = f"🚀 Analyze Diagram ({backend_info['type']})"
                if st.button(btn_text, type="primary", use_container_width=True):
                    st.session_state["is_analyzing"] = True
                    st.rerun()
            with action_clear_col:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state["active_image"] = None
                    st.session_state["image_source"] = None
                    st.rerun()

# ==========================================
# STAGE 2: ANIMATED SCANNING & ANALYSIS
# ==========================================
if st.session_state.get("is_analyzing") and st.session_state.get("active_image") is not None:
    import base64
    active_img = st.session_state["active_image"]
    buffered = io.BytesIO()
    active_img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    anim_col1, anim_col2, anim_col3 = st.columns([1, 2.2, 1])
    with anim_col2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h3 style="color: #f8fafc; font-weight: 600;">⚡ Scanning & Analyzing Circuit Schematic</h3>
                <p style="color: #818cf8; font-size: 0.95rem;">Model: <b>{backend_info['provider']} ({backend_info['model']})</b></p>
            </div>
            <div class="scanner-box">
                <div class="laser-line"></div>
                <img src="data:image/png;base64,{img_b64}" style="width: 100%; max-height: 400px; object-fit: contain; opacity: 0.88; filter: contrast(1.1) brightness(0.95);" />
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.status("🧠 Deep-analyzing diagram topology...", expanded=True) as status_box:
            st.write("🔍 Identifying electrical symbols, junctions, and reference nodes...")
            time.sleep(0.5)
            st.write("⚡ Tracing differential pairs, feedback loops, and biasing rails...")
            
            # Save temporary image for analyzer
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                active_img.save(tmp.name, format="PNG")
                tmp_path = tmp.name

            start_t = time.time()
            result = analyze(tmp_path, backend_choice)
            elapsed = time.time() - start_t

            try:
                os.unlink(tmp_path)
            except Exception:
                pass

            st.write("📋 Checking design health, common pitfalls, and generating practice questions...")
            status_box.update(label="✅ Analysis complete!", state="complete", expanded=False)

        st.session_state["analysis_result"] = result
        st.session_state["analysis_time"] = elapsed
        st.session_state["is_analyzing"] = False
        st.rerun()

# ==========================================
# STAGE 3: COMPLETE ANALYSIS & TUTORING DASHBOARD
# (Appears only after analysis finishes)
# ==========================================
if st.session_state["analysis_result"] is not None:
    result = st.session_state["analysis_result"]
    elapsed = st.session_state.get("analysis_time", 0.0)
    active_img = st.session_state.get("active_image")

    # Top Control Bar
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: baseline; gap: 0.75rem;">
                <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">{result.get('diagram_type', 'Circuit Analysis')}</h2>
                <span style="background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 0.2rem 0.65rem; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                    {backend_info['provider']} · {elapsed:.2f}s
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_col2:
        if st.button("🔄 Analyze Another Diagram", use_container_width=True):
            st.session_state["analysis_result"] = None
            st.session_state["active_image"] = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Key Metrics Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{len(result.get('components', []))}</div>
                <div class="metric-lbl">Components Identified</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{len(result.get('visible_symbols', []))}</div>
                <div class="metric-lbl">Symbols Recognized</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val" style="color: {'#ef4444' if result.get('possible_issues') else '#22c55e'};">{len(result.get('possible_issues', []))}</div>
                <div class="metric-lbl">Design Risks / Issues</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val" style="color:#a855f7;">{elapsed:.2f}s</div>
                <div class="metric-lbl">Inference Latency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Collapsible Source Image Review
    if active_img is not None:
        with st.expander("🖼️ View Analyzed Diagram Reference", expanded=False):
            img_c1, img_c2, img_c3 = st.columns([1, 2, 1])
            with img_c2:
                st.image(active_img, caption="Analyzed Circuit Schematic", use_container_width=True)

    # Detected Symbols & Labels Chips
    symbols = result.get("visible_symbols", [])
    labels = result.get("visible_labels", [])
    if symbols or labels:
        with st.expander("🔍 Detected Symbols & Text Labels", expanded=True):
            if symbols:
                st.markdown("**Recognized Symbols:**")
                chip_html = "".join([f"<span class='chip-symbol'>{s}</span>" for s in symbols])
                st.markdown(f"<div class='chip-container'>{chip_html}</div>", unsafe_allow_html=True)
            if labels:
                st.markdown("**Recognized Text & Values:**")
                label_html = "".join([f"<span class='chip-label'>{lbl}</span>" for lbl in labels])
                st.markdown(f"<div class='chip-container'>{label_html}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Analysis Tabs
    tab_explain, tab_components, tab_issues, tab_practice, tab_export = st.tabs(
        [
            "📖 Circuit Architecture & Explanation",
            "🧩 Component Breakdown",
            "⚠️ Diagnostics & Flaw Detection",
            "🎓 Practice Quiz",
            "💾 Raw Data & Export",
        ]
    )

    with tab_explain:
        connections = result.get("connections", "")
        if connections:
            st.markdown(
                f"""
                <div style="background: rgba(99, 102, 241, 0.08); border-left: 4px solid #6366f1; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; font-size: 0.95rem;">
                    <div style="font-weight: 600; color: #818cf8; margin-bottom: 0.3rem;">Wiring & Node Connections:</div>
                    <div style="color: #f1f5f9; line-height: 1.5;">{connections}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("#### Functional Explanation")
        st.markdown(result.get("explanation", "No detailed explanation provided."))

    with tab_components:
        st.markdown("#### 🧩 Identified Components & Their Engineering Roles")
        components = result.get("components", [])
        if components:
            for comp in components:
                lbl = comp.get("label", "Component")
                role = comp.get("role", "No role defined")
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(148, 163, 184, 0.12); border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 0.6rem; display: flex; align-items: baseline;">
                        <span style="font-weight: 600; color: #818cf8; font-family: 'JetBrains Mono', monospace; min-width: 160px; font-size: 0.95rem;">{lbl}</span>
                        <span style="color: #cbd5e1; font-size: 0.92rem; flex: 1;">{role}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No individual components identified in this schematic.")

    with tab_issues:
        st.markdown("#### ⚠️ Flaw Detection & Diagnostic Warnings")
        issues = result.get("possible_issues", [])
        if not issues:
            st.success("✅ **Clean Schematic**: No ambiguous connections, missing rails, or design hazards detected.")
        else:
            for item in issues:
                issue_title = item.get("issue", "Issue")
                why = item.get("why", "")
                conf = (item.get("confidence") or "medium").lower()

                css_class = "issue-medium"
                badge_color = "#f59e0b"
                if "high" in conf:
                    css_class = "issue-high"
                    badge_color = "#ef4444"
                elif "low" in conf:
                    css_class = "issue-low"
                    badge_color = "#3b82f6"

                st.markdown(
                    f"""
                    <div class="issue-card {css_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                            <b style="font-size: 1rem; color: #f8fafc;">{issue_title}</b>
                            <span style="background: {badge_color}; color: #ffffff; font-size: 0.72rem; padding: 0.15rem 0.55rem; border-radius: 12px; font-weight: 600; text-transform: uppercase;">{conf} confidence</span>
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.92rem;">{why}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_practice:
        st.markdown("#### 🎓 Undergraduate Engineering Assessment Quiz")
        st.caption("3 questions customized to this exact schematic, progressing from conceptual to design-level.")
        questions = result.get("practice_questions", [])
        if not questions:
            st.info("No practice questions were generated for this diagram.")
        else:
            for n, q in enumerate(questions, 1):
                q_text = q.get("q", "")
                ans_text = q.get("answer", "")
                with st.container():
                    st.markdown(f"**Q{n}.** {q_text}")
                    with st.expander(f"💡 Reveal Solution & Worked Steps (Q{n})"):
                        st.markdown(
                            f"""
                            <div style="background: rgba(99, 102, 241, 0.05); border-left: 3px solid #818cf8; padding: 0.85rem 1.1rem; border-radius: 6px; font-size: 0.93rem; color: #f1f5f9;">
                                {ans_text}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    st.markdown("<hr style='margin: 0.9rem 0; opacity: 0.12;'>", unsafe_allow_html=True)

    with tab_export:
        st.markdown("#### 💾 Export Report")
        json_str = json.dumps(result, indent=2)

        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.download_button(
                label="📥 Download JSON Report",
                data=json_str,
                file_name="circuit_analysis.json",
                mime="application/json",
                use_container_width=True,
            )
        with dcol2:
            md_content = f"# Circuit Analysis: {result.get('diagram_type', '')}\n\n"
            md_content += f"**Model:** {backend_info['provider']} ({backend_info['model']})\n\n"
            md_content += f"## Connections\n{result.get('connections', '')}\n\n"
            md_content += f"## Explanation\n{result.get('explanation', '')}\n\n"
            md_content += "## Components\n"
            for c in result.get('components', []):
                md_content += f"- **{c.get('label', '')}**: {c.get('role', '')}\n"
            st.download_button(
                label="📄 Download Markdown Summary",
                data=md_content,
                file_name="circuit_analysis.md",
                mime="text/markdown",
                use_container_width=True,
            )

        st.markdown("##### Structured JSON Data")
        st.code(json_str, language="json")
