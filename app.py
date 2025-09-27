import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("📊 Sistema de Análise de Jogos")

API_KEY = "e50f1ce938e544f29d2a914189d13bd4"
headers = {"X-Auth-Token": API_KEY}

# Exemplo: Premier League (competição 2021)
url = "https://api.football-data.org/v4/competitions/2021/matches"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    st.error("Erro ao buscar dados da API. Verifique sua chave e conexão.")
else:
    data = response.json()
    today = datetime.today().strftime("%Y-%m-%d")
    matches_today = [m for m in data.get("matches", []) if m["utcDate"].startswith(today)]

    if matches_today:
        df = pd.DataFrame([{
            "Casa": m["homeTeam"]["name"],
            "Fora": m["awayTeam"]["name"],
            "Rodada": m["matchday"],
            "Data": m["utcDate"][:10],
            "Status": m["status"]
        } for m in matches_today])
        st.subheader("Jogos de hoje")
        st.dataframe(df)
    else:
        st.info("Nenhum jogo hoje na competição selecionada.")

