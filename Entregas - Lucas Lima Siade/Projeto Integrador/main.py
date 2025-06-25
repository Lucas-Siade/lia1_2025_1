from flask import Flask, render_template_string, request

import os
import google.generativeai as genai
import feedparser
from dotenv import load_dotenv
from datetime import datetime
import urllib.parse

# ============ CONFIGURAÇÃO ============
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

perfil_jornalista = (
    "Você é um jornalista brasileiro especialista em resumir notícias. "
    "Seu trabalho é ler a notícia e criar um resumo abordando as principais informações dela."
)

# ============ FUNÇÕES ============
def buscar_noticias(assunto):
    assunto_url = urllib.parse.quote(assunto)
    rss_url = f"https://news.google.com/rss/search?q={assunto_url}&ceid=BR:pt-419"
    feed = feedparser.parse(rss_url)
    noticias = []
    for entrada in feed.entries[:4]:
        noticias.append({
            "titulo": entrada.title,
            "conteudo": entrada.summary,
            "link": entrada.link
        })
    return noticias

def resumir_noticias(noticias):
    chat_jornalista = model.start_chat(history=[])
    resumos = []
    for noticia in noticias:
        resposta = chat_jornalista.send_message(f"{perfil_jornalista}\n\n{noticia['conteudo']}")
        resumos.append({
            "titulo": noticia["titulo"],
            "resumo": resposta.text,
            "link": noticia["link"]
        })
    return resumos

# ============ FLASK APP ============

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    assunto = request.form.get("assunto") if request.method == "POST" else None
    resumos = []
    if assunto:
        noticias = buscar_noticias(assunto)
        resumos = resumir_noticias(noticias)
    data = datetime.now().strftime("%d/%m/%Y")

    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Capivara News</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f0f0;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
            }
            form {
                text-align: center;
                margin: 20px 0 40px;
            }
            input[type="text"] {
                width: 60%;
                padding: 8px;
                font-size: 16px;
            }
            input[type="submit"] {
                padding: 8px 16px;
                font-size: 16px;
                margin-left: 10px;
            }
            .grid {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            .card {
                background: #fafafa;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 16px;
                width: 45%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            .card h2 {
                font-size: 18px;
                margin-bottom: 10px;
            }
            .card p {
                font-size: 14px;
                color: #333;
            }
            .card a {
                display: inline-block;
                margin-top: 10px;
                color: #007BFF;
                text-decoration: none;
                font-size: 13px;
            }
            .nenhuma {
                text-align: center;
                color: red;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 Capivara News</h1>
            <p style="text-align: center;">{{ data }}</p>
            <form method="post">
                <input type="text" name="assunto" placeholder="Digite o tema da notícia..." required value="{{ assunto or '' }}">
                <input type="submit" value="Buscar Notícias">
            </form>
            {% if resumos %}
                <div class="grid">
                    {% for noticia in resumos %}
                        <div class="card">
                            <h2>{{ loop.index }}. {{ noticia.titulo }}</h2>
                            <p>{{ noticia.resumo }}</p>
                            <a href="{{ noticia.link }}" target="_blank">Ler notícia completa</a>
                        </div>
                    {% endfor %}
                </div>
            {% elif assunto %}
                <p class="nenhuma">❌ Nenhuma notícia encontrada para "{{ assunto }}"</p>
            {% endif %}
        </div>
    </body>
    </html>
    """

    return render_template_string(html, resumos=resumos, assunto=assunto, data=data)

# ============ EXECUTAR ============
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
