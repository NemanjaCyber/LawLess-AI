import streamlit as st
import logic
import base64

st.set_page_config(page_title="LawLess AI", layout="wide")

st.sidebar.title("⚖️ LawLess ⚖️")
st.sidebar.info("Alat za analizu ugovora bez advokatskih troškova.")

st.title("Pravna analiza u realnom vremenu")

uploaded_file = st.file_uploader("Otpremite PDF ugovor", type="pdf")

if uploaded_file:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Pregled dokumenta")

        bytes_data = uploaded_file.getvalue()
        base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'

        st.markdown("""
            <style>
            iframe { border-radius: 10px; border: 1px solid #4A4A4A; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(pdf_display, unsafe_allow_html=True)
        raw_text = logic.extract_text_from_pdf(uploaded_file)

    with col2:
        st.subheader("AI Analiza")
        if st.button("Pokreni Analizu", key="glavno_dugme_analize"):
            with st.spinner("Llama 3 analizira klauzule..."):

                try:
                    izvestaj = logic.analyze_contract(raw_text)
                    risk_score = logic.get_risk_score(raw_text)
                except Exception as e:
                    st.error(f"Greška pri komunikaciji sa AI: {e}")
                    st.stop()

                # --- Risk score prikaz ---
                st.markdown("---")
                st.subheader("📊 Ukupna ocena rizika")

                if risk_score <= 3:
                    color = "green"
                    label = "NIZAK RIZIK - Ugovor deluje standardno."
                elif risk_score <= 7:
                    color = "orange"
                    label = "SREDNJI RIZIK - Obratite pažnju na detalje."
                else:
                    color = "red"
                    label = "VISOK RIZIK - Ne potpisujte bez stručne pomoći!"

                st.progress(risk_score * 10)
                st.markdown(f"### Nivo: :{color}[{risk_score}/10] - {label}")

                # --- Parser sekcija ---
                # Mapa: kljucne reci -> naziv slota
                SEKCIJE_MAPA = {
                    "sazetak":     ["sazetak", "sažetak"],
                    "rizici":      ["rizici", "red flags", "opasnost"],
                    "preporuke":   ["preporuke"],
                    "podaci":      ["kljucni podaci", "ključni podaci"],
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
                            # Tekst posle ":" u istom redu
                            if ":" in clean_line:
                                content = clean_line.split(":", 1)[1].strip()
                                if content:
                                    sekcije[slot].append(content)
                            matched = True
                            break

                    if not matched and current_section:
                        sekcije[current_section].append(clean_line)

                # --- Prikaz rezultata ---
                st.markdown("---")
                st.header("🔍 Rezultati Analize")

                if sekcije["sazetak"]:
                    with st.expander("📝 SAŽETAK UGOVORA", expanded=True):
                        st.info("\n".join(sekcije["sazetak"]))
                else:
                    st.warning("Sažetak nije pronađen u odgovoru.")

                if sekcije["rizici"]:
                    with st.expander("⚠️ IDENTIFIKOVANI RIZICI", expanded=True):
                        st.error("\n".join(sekcije["rizici"]))

                if sekcije["preporuke"]:
                    with st.expander("💡 PREPORUKE ZA POPUNJAVANJE", expanded=True):
                        st.warning("\n".join(sekcije["preporuke"]))

                if sekcije["podaci"]:
                    with st.expander("📊 KLJUČNI PODACI", expanded=True):
                        st.success("\n".join(sekcije["podaci"]))

                # Ako nijedna sekcija nije parsirana, prikazi raw odgovor
                if not any(sekcije.values()):
                    st.markdown("---")
                    st.subheader("Sirovi odgovor AI-ja")
                    st.text(izvestaj)

                # --- Export ---
                st.markdown("### 📥 Preuzmite izveštaj")
                pdf_data = logic.create_pdf_report(izvestaj)
                st.download_button(
                    label="Preuzmi PDF Izveštaj",
                    data=pdf_data,
                    file_name="LawLess_Izvestaj.pdf",
                    mime="application/pdf",
                    key="download_pdf_btn"
                )