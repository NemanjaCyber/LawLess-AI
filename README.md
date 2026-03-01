# ⚖️ LawLess AI: Digitalni Advokat za Svakoga

**LawLess** je AI MVP projekat dizajniran da demistifikuje pravne dokumente i zaštiti korisnike od štetnih klauzula koristeći najsavremenije LLM modele.

## Problem
Pravni žargon je barijera koja prosečnog čoveka ostavlja nezaštićenim. Većina ljudi potpisuje ugovore o radu, zakupu ili saradnji bez potpunog razumevanja rizika jer su advokatske konsultacije skupe i spore.

## Ciljna grupa
* **Freelanceri:** Analiza ugovora sa stranim klijentima.
* **Podstanari:** Brza provera ugovora o zakupu stana.
* **Mali preduzetnici:** Razumevanje obaveza prema dobavljačima.

## Glavne Funkcionalnosti
1. **Automatsko Sumiranje:** Pretvara 20 strana teksta u 3 ključne tačke.
2. **Red Flag Detektor:** Identifikacija penala, skrivenih troškova i nepovoljnih rokova.
3. **Pravni Prevodilac:** Objašnjavanje komplikovanih termina na svakodnevnom jeziku.

## Tehnološki Stack
* **Frontend:** Streamlit (Python)
* **AI Model:** llama-3.3-70b-versatile (via Groq Cloud API)
* **Infrastruktura:** GitHub Codespaces (Cloud-based development)
* **Obrada dokumenata:** PyPDF2 za ekstrakciju teksta