import streamlit as st
import logic
import base64

st.set_page_config(page_title="LawLess AI", layout="wide")

# Sidebar za navigaciju
st.sidebar.title("⚖️ LawLess AI")
st.sidebar.info("Vaš alat za analizu ugovora bez advokatskih troškova.")

st.title("Pravna Analiza u Realnom Vremenu")

uploaded_file = st.file_uploader("Otpremite PDF ugovor", type="pdf")

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Pregled dokumenta")
        
        # Čitamo fajl za prikaz u iframe-u
        bytes_data = uploaded_file.getvalue()
        base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
        
        # Generišemo HTML za ugradnju PDF-a
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        
        st.markdown("""
            <style>
            iframe {
                border-radius: 10px;
                border: 1px solid #4A4A4A;
            }
            </style>
            """, unsafe_allow_html=True)

        # Prikazujemo PDF
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # Izvlačimo tekst za AI (ovo ostaje u pozadini, ne vidi se)
        raw_text = logic.extract_text_from_pdf(uploaded_file)

    with col2:
        st.subheader("🤖 AI Analiza")
        if st.button("Pokreni Analizu", key="glavno_dugme_analize"):
            with st.spinner("Llama 3 analizira klauzule..."):
                izvestaj = logic.analyze_contract(raw_text)
                
                # 1. Priprema "fioka" za tekst
                sekcije = {
                    "sazetak": [],
                    "rizici": [],
                    "podaci": []
                }
                
                current_section = None
                lines = izvestaj.split("\n")
                
                # 2. Razvrstavanje teksta
                for line in lines:
                    clean_line = line.strip()
                    if not clean_line: continue
                    
                    lower_line = clean_line.lower()
                    
                    # Provera naslova sekcija
                    if any(x in lower_line for x in ["sažetak", "sazetak"]):
                        current_section = "sazetak"
                        # Ako u istom redu ima još teksta posle dve tačke, uzmi ga
                        if ":" in clean_line:
                            content = clean_line.split(":", 1)[1].strip()
                            if content: sekcije["sazetak"].append(content)
                        continue 
                        
                    elif any(x in lower_line for x in ["rizici", "red flags", "opasnost"]):
                        current_section = "rizici"
                        if ":" in clean_line:
                            content = clean_line.split(":", 1)[1].strip()
                            if content: sekcije["rizici"].append(content)
                        continue
                        
                    elif any(x in lower_line for x in ["ključni podaci", "kljucni podaci"]):
                        current_section = "podaci"
                        if ":" in clean_line:
                            content = clean_line.split(":", 1)[1].strip()
                            if content: sekcije["podaci"].append(content)
                        continue
                    
                    # Ako nije naslov, dodaj tekst u trenutno aktivnu sekciju
                    if current_section:
                        sekcije[current_section].append(clean_line)

                # 3. PRIKAZ (Sada su boje zagarantovane)
                st.markdown("---")
                st.header("🔍 Rezultati Analize")

                if sekcije["sazetak"]:
                    with st.expander("📝 SAŽETAK UGOVORA", expanded=True):
                        st.info("\n".join(sekcije["sazetak"]))

                if sekcije["rizici"]:
                    with st.expander("⚠️ IDENTIFIKOVANI RIZICI (RED FLAGS)", expanded=True):
                        # Sve u ovoj sekciji će biti CRVENO
                        for r in sekcije["rizici"]:
                            st.error(r)

                if sekcije["podaci"]:
                    with st.expander("📊 KLJUČNI PODACI I STRANE", expanded=True):
                        st.success("\n".join(sekcije["podaci"]))

                # 4. EXPORT (ostaje isto)
                st.markdown("### 📥 Preuzmite izveštaj")
                pdf_data = logic.create_pdf_report(izvestaj)
                st.download_button(
                    label="Preuzmi PDF Izveštaj",
                    data=pdf_data,
                    file_name="LawLess_Izvestaj.pdf",
                    mime="application/pdf",
                    key="download_pdf_btn"
                )