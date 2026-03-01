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

def create_pdf_report(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="LawLess AI - Analiza ugovora", ln=True, align='C')
    pdf.ln(10)
    # Dekodiramo tekst za PDF (fpdf ima problema sa našim čćž, koristimo latin-1)
    pdf.multi_cell(0, 10, txt=content.encode('latin-1', 'replace').decode('latin-1'))
    
    output_path = "izvestaj_analize.pdf"
    pdf.output(output_path)
    return output_path