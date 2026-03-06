import streamlit as st
import logic
import base64

st.set_page_config(page_title="LawLess AI", layout="wide", page_icon="⚖️")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

/* Reset & base */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0f0f0f;
    color: #e8e2d9;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 1400px !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #141414;
    border-right: 1px solid #2a2a2a;
}
section[data-testid="stSidebar"] * {
    color: #e8e2d9 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.sidebar-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #c9a84c !important;
    letter-spacing: 0.05em;
    padding: 1rem 0 0.25rem 0;
    border-bottom: 1px solid #2a2a2a;
    margin-bottom: 1rem;
}
.sidebar-tagline {
    font-size: 0.78rem;
    color: #888 !important;
    line-height: 1.5;
    font-weight: 300;
}

/* ── Header ── */
.app-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #2a2a2a;
}
.app-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #e8e2d9;
    letter-spacing: -0.01em;
    margin: 0;
}
.app-title span { color: #c9a84c; }
.app-subtitle {
    font-size: 0.85rem;
    color: #666;
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
    padding: 0.5rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #c9a84c !important;
}
[data-testid="stFileUploader"] label {
    color: #888 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── Section headings ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #2a2a2a;
}

/* ── Analyze button ── */
.stButton > button {
    background: #c9a84c !important;
    color: #0f0f0f !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #e0be6a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.25) !important;
}

/* ── Risk score card ── */
.risk-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}
.risk-number {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
}
.risk-label {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.25rem;
    font-weight: 400;
}
.risk-low  { color: #4a9d6f; }
.risk-mid  { color: #d4843a; }
.risk-high { color: #c94a4a; }

/* ── Progress bar ── */
.stProgress > div > div {
    background: #2a2a2a !important;
    border-radius: 2px !important;
    height: 4px !important;
}
.stProgress > div > div > div {
    border-radius: 2px !important;
}

/* ── Result panels ── */
.result-panel {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #c9a84c;
    border-radius: 2px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #d0c9be;
}
.result-panel.danger  { border-left-color: #c94a4a; }
.result-panel.warning { border-left-color: #d4843a; }
.result-panel.success { border-left-color: #4a9d6f; }

.panel-title {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    color: #888;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 2px !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #888 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
[data-testid="stExpander"] summary:hover { color: #c9a84c !important; }

/* Override Streamlit alert colors */
.stAlert {
    background: #141414 !important;
    border-radius: 2px !important;
    border: 1px solid #2a2a2a !important;
    font-size: 0.88rem !important;
    line-height: 1.7 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #c9a84c !important;
    border: 1px solid #c9a84c !important;
    border-radius: 2px !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #c9a84c !important;
    color: #0f0f0f !important;
}

/* ── Divider ── */
hr { border-color: #2a2a2a !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #c9a84c !important; }

/* ── Column border ── */
.pdf-col {
    border-right: 1px solid #2a2a2a;
    padding-right: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚖ LawLess AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Profesionalna analiza pravnih dokumenata bez advokatskih troškova.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Kako koristiti:**", unsafe_allow_html=False)
    st.markdown("""
1. Otpremite PDF ugovor  
2. Kliknite *Pokreni Analizu*  
3. Pregledajte rizike i preporuke  
4. Preuzmite izveštaj
""")
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("v1.0 · Powered by Llama 3.3 70B")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1 class="app-title">Law<span>Less</span></h1>
    <span class="app-subtitle">Analiza pravnih dokumenata</span>
</div>
""", unsafe_allow_html=True)

# ── File uploader ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Otpremite PDF ugovor", type="pdf", label_visibility="collapsed")

if not uploaded_file:
    st.markdown("""
    <div style="
        background:#141414;
        border:1px dashed #2a2a2a;
        border-radius:4px;
        padding:3rem 2rem;
        text-align:center;
        margin-top:1rem;
    ">
        <div style="font-size:2rem;margin-bottom:1rem;">⚖️</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:#e8e2d9;margin-bottom:0.5rem;">
            Otpremite ugovor za analizu
        </div>
        <div style="font-size:0.8rem;color:#555;letter-spacing:0.06em;">
            Podržani format: PDF · Template ili popunjen ugovor
        </div>
    </div>
    """, unsafe_allow_html=True)

if uploaded_file:
    col1, col2 = st.columns([1.1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-label">Pregled dokumenta</div>', unsafe_allow_html=True)

        bytes_data = uploaded_file.getvalue()
        base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
        pdf_display = f'''
            <iframe
                src="data:application/pdf;base64,{base64_pdf}"
                width="100%"
                height="600px"
                style="border-radius:4px; border:1px solid #2a2a2a; background:#141414;">
            </iframe>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)
        raw_text = logic.extract_text_from_pdf(uploaded_file)

    with col2:
        st.markdown('<div class="section-label">AI Analiza</div>', unsafe_allow_html=True)

        if st.button("Pokreni Analizu", key="glavno_dugme_analize"):

            with st.spinner("Verifikacija dokumenta..."):
                try:
                    je_validan = logic.validate_document(raw_text)
                except Exception as e:
                    st.error(f"Greška pri validaciji: {e}")
                    st.stop()

            if not je_validan:
                st.markdown("""
                <div class="result-panel danger">
                    <div class="panel-title">⚠ Nevažeći dokument</div>
                    Otpremljeni dokument ne prepoznajemo kao pravni ugovor.
                    Molimo otpremite ugovor ili template ugovora u PDF formatu.
                </div>
                """, unsafe_allow_html=True)
                st.stop()

            with st.spinner("Analiza klauzula u toku..."):
                try:
                    izvestaj = logic.analyze_contract(raw_text)
                    risk_score = logic.get_risk_score(raw_text)
                except Exception as e:
                    st.error(f"Greška pri analizi: {e}")
                    st.stop()

            # ── Risk score ────────────────────────────────────────────────
            st.markdown('<div class="section-label" style="margin-top:1.5rem;">Ocena rizika</div>', unsafe_allow_html=True)

            if risk_score <= 3:
                risk_class = "risk-low"
                risk_label = "Nizak rizik"
                risk_desc  = "Ugovor deluje standardno."
            elif risk_score <= 7:
                risk_class = "risk-mid"
                risk_label = "Srednji rizik"
                risk_desc  = "Obratite pažnju na detalje."
            else:
                risk_class = "risk-high"
                risk_label = "Visok rizik"
                risk_desc  = "Ne potpisujte bez stručne pomoći."

            st.markdown(f"""
            <div class="risk-card">
                <div style="display:flex;align-items:flex-end;gap:16px;">
                    <div class="risk-number {risk_class}">{risk_score}<span style="font-size:1.2rem;color:#444">/10</span></div>
                    <div>
                        <div class="risk-label {risk_class}">{risk_label}</div>
                        <div style="font-size:0.78rem;color:#555;margin-top:2px;">{risk_desc}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(risk_score * 10)

            # ── Parser ────────────────────────────────────────────────────
            SEKCIJE_MAPA = {
                "sazetak":   ["sazetak", "sažetak"],
                "rizici":    ["rizici", "red flags", "opasnost"],
                "preporuke": ["preporuke"],
                "podaci":    ["kljucni podaci", "ključni podaci"],
            }
            sekcije = {k: [] for k in SEKCIJE_MAPA}
            current_section = None

            for line in izvestaj.split("\n"):
                clean_line = line.strip()
                if not clean_line:
                    continue
                lower_line = clean_line.lower()
                matched = False
                for slot, kljucne_reci in SEKCIJE_MAPA.items():
                    if any(kw in lower_line for kw in kljucne_reci):
                        current_section = slot
                        if ":" in clean_line:
                            content = clean_line.split(":", 1)[1].strip()
                            if content:
                                sekcije[slot].append(content)
                        matched = True
                        break
                if not matched and current_section:
                    sekcije[current_section].append(clean_line)

            # ── Rezultati ─────────────────────────────────────────────────
            st.markdown('<div class="section-label" style="margin-top:1.5rem;">Rezultati analize</div>', unsafe_allow_html=True)

            if sekcije["sazetak"]:
                with st.expander("📋  Sažetak ugovora", expanded=True):
                    st.info("\n".join(sekcije["sazetak"]))

            if sekcije["rizici"]:
                with st.expander("⚠  Identifikovani rizici", expanded=True):
                    st.error("\n".join(sekcije["rizici"]))

            if sekcije["preporuke"]:
                with st.expander("💡  Preporuke za popunjavanje", expanded=True):
                    st.warning("\n".join(sekcije["preporuke"]))

            if sekcije["podaci"]:
                with st.expander("📊  Ključni podaci", expanded=True):
                    st.success("\n".join(sekcije["podaci"]))

            if not any(sekcije.values()):
                st.text(izvestaj)

            # ── Export ────────────────────────────────────────────────────
            st.markdown('<div class="section-label" style="margin-top:1.5rem;">Izvoz</div>', unsafe_allow_html=True)
            pdf_data = logic.create_pdf_report(izvestaj)
            st.download_button(
                label="↓  Preuzmi PDF izveštaj",
                data=pdf_data,
                file_name="LawLess_Izvestaj.pdf",
                mime="application/pdf",
                key="download_pdf_btn"
            )