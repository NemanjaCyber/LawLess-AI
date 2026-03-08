import streamlit as st
import logic
import base64
import os
from pathlib import Path
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(page_title="LawLess AI", layout="wide", page_icon="⚖️")

# ── Load CSS ──────────────────────────────────────────────────────────────────
with open(Path(__file__).parent / "Style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚖ LawLess AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Profesionalna analiza pravnih dokumenata bez advokatskih troškova.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Kako koristiti:**")
    st.markdown("""
1. Otpremite PDF ugovor  
2. Kliknite *Pokreni Analizu*  
3. Pregledajte analizu, rizike i preporuke  
4. Preuzmite izveštaj
""")
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("v1.0 · Powered by Llama 3.3 70B")

# ── Header ────────────────────────────────────────────────────────────────────
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

        # 2. UZMI BAJTOVE DOKUMENTA
        bytes_data = uploaded_file.getvalue()

        # 3. PRIKAŽI PDF (Ovo menja sav onaj prethodni HTML/JS kod)
        # pdf_viewer će automatski prikazati sve stranice i omogućiti skrolovanje
        pdf_viewer(
            input=bytes_data,
            width=None,
            height=600,
        )

        # Logika za ekstrakciju teksta ostaje ista
        raw_text = logic.extract_text_from_pdf(uploaded_file)

    with col2:
        st.markdown('<div class="section-label">AI Analiza</div>', unsafe_allow_html=True)

        if st.button("Pokreni Analizu", key="glavno_dugme_analize"):

            # ── Validacija ────────────────────────────────────────────────
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

            # ── Analiza ───────────────────────────────────────────────────
            with st.spinner("Analiza klauzula u toku..."):
                try:
                    izvestaj, risk_score = logic.analyze_contract(raw_text)
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
            STOP_RECI = ["stroga pravila", "vazna napomena", "napomena:", "disclaimer", "ocena rizika"]

            sekcije = {k: [] for k in SEKCIJE_MAPA}
            current_section = None

            for line in izvestaj.split("\n"):
                clean_line = line.strip()
                if not clean_line:
                    continue
                lower_line = clean_line.lower()
                if any(stop in lower_line for stop in STOP_RECI):
                    break
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