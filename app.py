import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Painel de Jogos", layout="wide")
st.title("🎲 Painel de Jogos e Odds - Estilo Betano")

# API_KEY do Streamlit Secrets
API_KEY = st.secrets["FOOTBALL_API_KEY"]
headers = {"X-Auth-Token": API_KEY}

# Dropdown para selecionar campeonato
competitions = {
    "Premier League": "2021",
    "La Liga": "2014",
    "Serie A": "2019",
    "Bundesliga": "2002"
}

champ = st.selectbox("Selecione o campeonato:", list(competitions.keys()))
comp_id = competitions[champ]

# Pegar os jogos
url = f"https://api.football-data.org/v4/competitions/{comp_id}/matches"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    st.error("Erro ao buscar dados da API. Verifique sua chave e conexão.")
else:
    data = response.json()
    matches = data.get("matches", [])

    if not matches:
        st.info("Nenhum jogo encontrado.")
    else:
        # Organizar por data e horário
        matches_df = pd.DataFrame([{
            "Casa": m["homeTeam"]["name"],
            "Fora": m["awayTeam"]["name"],
            "Data": m["utcDate"][:10],
            "Hora": m["utcDate"][11:16],
            "Status": m["status"],
            "Rodada": m["matchday"]
        } for m in matches])

        matches_df['DataHora'] = matches_df['Data'] + " " + matches_df['Hora']
        matches_df = matches_df.sort_values(['DataHora'])

        # Agrupar por data
        for date, group in matches_df.groupby('Data'):
            st.markdown(f"## 📅 {date}")
            for _, row in group.iterrows():
                st.markdown(f"""
                <div style="border:1px solid #ccc; padding:10px; border-radius:8px; margin-bottom:10px; background:#f9f9f9">
                    <strong>{row['Hora']}</strong> - {row['Casa']} 🆚 {row['Fora']} <br>
                    Rodada: {row['Rodada']} | Status: {row['Status']} <br>
                    Odds Vitória Casa: 1.75 | Odds Empate: 3.50 | Odds Vitória Fora: 3.20
                </div>
                """, unsafe_allow_html=True)

