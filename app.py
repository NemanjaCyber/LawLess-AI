import streamlit as st
import logic
import base64

st.set_page_config(page_title="LawLess AI", layout="wide")

# Sidebar za navigaciju
st.sidebar.title("⚖️ LawLess ⚖️")
st.sidebar.info("Alat za analizu ugovora bez advokatskih troškova.")

st.title("Pravna analiza u realnom vremenu")

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
        st.subheader("AI Analiza")
        if st.button("Pokreni Analizu", key="glavno_dugme_analize"):
            with st.spinner("Llama 3 analizira klauzule..."):
                izvestaj = logic.analyze_contract(raw_text)
        
                risk_score = logic.get_risk_score(raw_text)
                
                st.markdown("---")
                st.subheader("📊 Ukupna ocena rizika")
                
                # Određivanje boje i opisa na osnovu rezultata
                if risk_score <= 3:
                    color = "green"
                    label = "NIZAK RIZIK - Ugovor deluje standardno."
                elif risk_score <= 7:
                    color = "orange"
                    label = "SREDNJI RIZIK - Obratite pažnju na detalje."
                else:
                    color = "red"
                    label = "VISOK RIZIK - Ne potpisujte bez stručne pomoći!"

                # Vizuelni progress bar
                st.progress(risk_score * 10) # Streamlit progress ide od 0 do 100
                st.markdown(f"### Nivo: :{color}[{risk_score}/10] - {label}")

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
                    with st.expander("⚠️ IDENTIFIKOVANI RIZICI", expanded=True):
                        # Sve u ovoj sekciji će biti CRVENO
                        st.error("\n".join(sekcije["rizici"]))

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