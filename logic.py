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
        text += page.extract_text()
    return text

def analyze_contract(text):
    prompt = f"""
    Ti si ekspertni pravni savetnik. Analiziraj ugovor i strogo se pridržavaj sledećeg formata:
    
    SAŽETAK: (Ovde napiši kratku suštinu ugovora u 2-3 rečenice)
    
    RIZICI (RED FLAGS): 
    - (Ovde listaj rizike koristeći bullet pointe)
    - (Svaki rizik treba da bude u novom redu)
    
    KLJUČNI PODACI:
    - (Strane u ugovoru, datumi, cifre)
    
    VAŽNA NAPOMENA: Odgovori isključivo na srpskom jeziku.

    STROGA PRAVILA:
    1. Odgovori ISKLJUČIVO na LATINICI. Zabranjena je upotreba ćirilice.
    2. Zabranjena je upotreba bilo kakvih EMOJIJA (ikona). Koristi samo čist tekst.
    3. Koristi profesionalni, ali razumljiv rečnik.
    
    Tekst ugovora:
    {text[:7000]} 
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.2, # Smanjujemo kreativnost da bi bio precizniji
    )
    return response.choices[0].message.content

def create_pdf_report(report_text):
    # Mapiranje svih mogućih problematičnih karaktera (Ćirilica -> Latinica)
    cyr_to_lat = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'dj', 'е': 'e', 'ж': 'z',
        'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n',
        'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'u': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Dj', 'Е': 'E', 'Ж': 'Z',
        'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'M': 'M', 'Н': 'N',
        'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'C', 'Џ': 'Dz', 'Š': 'S',
        # Naša latinična slova sa kvačicama (za svaki slučaj)
        'š': 's', 'ć': 'c', 'č': 'c', 'đ': 'dj', 'ž': 'z',
        'Š': 'S', 'Ć': 'C', 'Č': 'C', 'Đ': 'Dj', 'Ž': 'Z'
    }

    # 1. Prvo menjamo sve prepoznate karaktere
    for cyr, lat in cyr_to_lat.items():
        report_text = report_text.replace(cyr, lat)

    # 2. Finalno čišćenje: pretvaramo u ASCII i ignorišemo sve što je preostalo
    # Ovo osigurava da latin-1 codec u FPDF-u nikada ne vidi karaktere van opsega
    clean_text = report_text.encode('ascii', 'ignore').decode('ascii')

    pdf = FPDF()
    pdf.add_page()
    
    # Naslov
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="LawLess AI - Izvestaj Analize", ln=True, align="C")
    
    pdf.ln(10)
    
    # Sadržaj
    pdf.set_font("Arial", size=12)
    # multi_cell za automatski prelom redova
    pdf.multi_cell(0, 10, txt=clean_text)
    
    # Vraćamo PDF kao bajtove
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def get_risk_score(text):
    prompt = f"""
    Na osnovu teksta ugovora, oceni nivo pravnog rizika za potpisnika na skali od 1 do 10.
    Gde je 1 potpuno bezbedan ugovor, a 10 izuzetno opasan i nepovoljan.
    
    ODGOVORI SAMO JEDNIM BROJEM. Bez dodatnog teksta.
    
    Tekst:
    {text[:5000]}
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )
    
    # Izvlačimo samo broj iz odgovora
    score_str = response.choices[0].message.content.strip()
    try:
        return int(score_str)
    except:
        return 5 # Fallback ako AI nešto pobrljavi