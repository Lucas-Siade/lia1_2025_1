import os
import google.generativeai as genai
import feedparser
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

RSS_URL = "https://news.google.com/rss/search?q=inteligencia+artificial&ceid=BR:pt-419"

chat_jornalista = model.start_chat(history=[])

perfil_jornalista = (
    "Você é um jornalista brasileiro especialista em Inteligência Artificial. "
    "Seu trabalho é ler a notícia e criar um resumo abordando as principais informações dela."
)

def buscar_noticias(rss_url):
    feed = feedparser.parse(rss_url)
    noticias = []
    for entrada in feed.entries:
        noticias.append({
            "titulo": entrada.title,
            "conteudo": entrada.summary,
            "link": entrada.link
        })
    return noticias

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        img_width = 30
        x_centered = (self.w - img_width) / 2
        self.image("Capivara Jornalista.jpg", x=x_centered, y=10, w=img_width)
        self.ln(30)
        self.cell(0, 10, "Capivara News", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, datetime.now().strftime("%d/%m/%Y"), ln=True, align="C")
        self.ln(5)

    def chapter_title(self, num, title):
        self.set_font("Arial", "B", 12)
        self.multi_cell(0, 10, f"{num}. {title}")

    def chapter_body(self, body):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 8, body)
        self.ln()

    def add_noticia(self, num, titulo, resumo, link):
        self.chapter_title(num, titulo)
        self.chapter_body(resumo)
        self.set_text_color(0, 0, 255)
        self.set_font("Arial", "U", 9)
        self.cell(0, 10, "Saiba mais na notícia completa", ln=True, link=link)
        self.set_text_color(0, 0, 0)
        self.ln(5)



noticias = buscar_noticias(RSS_URL)
pdf = PDF()
pdf.add_page()

for i, noticia in enumerate(noticias[:5]):
    resposta = chat_jornalista.send_message(f"{perfil_jornalista}\n\n{noticia['conteudo']}")
    pdf.add_noticia(i + 1, noticia["titulo"], resposta.text, noticia["link"])

output = f"Capivara News - {datetime.now().strftime('%d-%m-%Y')}.pdf"
pdf.output(output)

print(f"\n✅ PDF gerado: {output}")