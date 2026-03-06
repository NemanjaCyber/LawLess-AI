import os
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def validate_document(text):
    """
    Proverava da li dokument ima ikakve veze sa ugovorom ili pravnim tekstom.
    Namerno je permisivan - odbija samo ocigledne ne-ugovore (slike, CV, fakture...).
    """
    prompt = f"""
Proceni sledeci dokument. Da li je ovo BILO KOJI od sledecih tipova dokumenta:
- Ugovor (potpisan ili nepotpisan)
- Template ili obrazac ugovora
- Pravni dokument sa klauzulama
- Sporazum, aneks, addendum
- Dokument koji sadrzi pravne odredbe ili obaveze

Odgovori SAMO sa "DA" ako spada u bilo koju od ovih kategorija.
Odgovori SAMO sa "NE" ako je to nesto potpuno drugo (npr. CV, faktura, clanak, slika, prezentacija).

Tekst dokumenta:
{text[:2000]}
"""
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )

    odgovor = response.choices[0].message.content.strip().upper()
    return "DA" in odgovor

def analyze_contract(text):
    prompt = f"""
Ti si ekspertni pravni savetnik koji analizira TEMPLATE ugovore (prazne obrasce bez popunjenih podataka).
Tvoj zadatak je da analiziras STRUKTURU i KLAUZULE ugovora, a ne konkretne strane ili iznose.

Strogo se pridrzavaj TACNO ovog formata (ne menjaj nazive sekcija):

SAZETAK:
(2-3 recenice: koja je VRSTA ugovora, cemu sluzi, ko su tipicno strane koje ga potpisuju)

RIZICI:
- (Analiziraj svaku klauzulu koja moze biti nepovoljna za potpisnika)
- (Ukazi na nejasne formulacije, jednostrane odredbe, skrivene obaveze)
- (Ukazi na ono sto NEDOSTAJE - vazne zastitne klauzule kojih nema u templateu)

PREPORUKE:
- (Sta treba pazljivo popuniti pre potpisivanja)
- (Na koje stavke obratiti posebnu paznju prilikom unosa podataka)

KLJUCNI PODACI:
- (Tip ugovora, nadleznost ako je navedena, trajanje, uslovi raskida)

STROGA PRAVILA:
1. Odgovori ISKLJUCIVO na srpskom jeziku i LATINICI. Zabranjena je cirilica.
2. Bez emojija, samo cist tekst.
3. Nikad ne izmisljaj konkretne podatke - ugovor je template.
4. Ako klauzula nedostaje a trebalo bi da postoji, eksplicitno to napomeni.
5. Koristi TACNO iste nazive sekcija kao sto je zadato gore.

Tekst ugovora:
{text[:7000]}
"""
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )
    return response.choices[0].message.content

def get_risk_score(text):
    prompt = f"""
Analiziras PRAZAN TEMPLATE ugovora (bez popunjenih podataka).
Oceni koliko su KLAUZULE I STRUKTURA ovog templatea potencijalno rizicne za osobu koja ga potpise, na skali 1 do 10.

Kriterijumi:
- Da li su klauzule jednostrane?
- Da li postoje nejasne ili manipulativne formulacije?
- Da li nedostaju vazne zastitne klauzule?
- Koliko prostora template ostavlja za zloupotrebu pri popunjavanju?

ODGOVORI SAMO JEDNIM BROJEM OD 1 DO 10. Bez ikakvog dodatnog teksta.

Tekst:
{text[:5000]}
"""
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )
    score_str = response.choices[0].message.content.strip()
    for char in score_str:
        if char.isdigit():
            val = int(char)
            if 1 <= val <= 10:
                return val
    return 5

def create_pdf_report(report_text):
    cyr_to_lat = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'dj', 'е': 'e', 'ж': 'z',
        'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n',
        'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c',
        'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Dj', 'Е': 'E', 'Ж': 'Z',
        'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'Н': 'N',
        'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'C', 'Џ': 'Dz',
        'š': 's', 'ć': 'c', 'č': 'c', 'đ': 'dj', 'ž': 'z',
        'Š': 'S', 'Ć': 'C', 'Č': 'C', 'Đ': 'Dj', 'Ž': 'Z'
    }
    for cyr, lat in cyr_to_lat.items():
        report_text = report_text.replace(cyr, lat)
    clean_text = report_text.encode('ascii', 'ignore').decode('ascii')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="LawLess AI - Izvestaj Analize", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1', 'ignore')