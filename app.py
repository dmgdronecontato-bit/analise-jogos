import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Painel de Jogos", layout="wide")
st.title("🎲 Painel de Jogos e Odds - Estilo Betano")

API_KEY = st.secrets["FOOTBALL_API_KEY"]
headers = {"X-Auth-Token": API_KEY}

# Competitions
competitions = {
    "PL - Premier League": "PL",
    "SA - Serie A": "SA",
    "BSA - Campeonato Brasileiro Série A": "BSA",
    "CL - UEFA Champions League": "CL",
    "WC - FIFA World Cup": "WC"
}

champ = st.selectbox("Selecione a competição:", list(competitions.keys()))
comp_id = competitions[champ]

# Filtro por status
status_filter = st.selectbox("Filtrar por status:", ["Todos", "Em andamento", "Próximos", "Finalizados"])

# Buscar jogos
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
            "Rodada": m["matchday"],
            "CasaEscudo": m["homeTeam"].get("crest", ""),
            "ForaEscudo": m["awayTeam"].get("crest", "")
        } for m in matches])

        # Aplicar filtro de status
        if status_filter != "Todos":
            map_status = {"Em andamento":"LIVE", "Próximos":"SCHEDULED", "Finalizados":"FINISHED"}
            matches_df = matches_df[matches_df["Status"] == map_status[status_filter]]

        matches_df['DataHora'] = matches_df['Data'] + " " + matches_df['Hora']
        matches_df = matches_df.sort_values(['DataHora'])

        # Mostrar jogos
        for date, group in matches_df.groupby('Data'):
            st.markdown(f"## 📅 {date}")
            for _, row in group.iterrows():
                st.markdown(f"""
                <div style="border:1px solid #ccc; border-radius:10px; margin-bottom:10px; padding:10px; display:flex; align-items:center; background:#f0f2f6;">
                    <div style="width:90px; text-align:center; font-weight:bold;">
                        <img src="{row['CasaEscudo']}" width="50"><br>{row['Casa']}
                    </div>
                    <div style="width:30px; text-align:center; font-size:20px;"><strong>X</strong></div>
                    <div style="width:90px; text-align:center; font-weight:bold;">
                        <img src="{row['ForaEscudo']}" width="50"><br>{row['Fora']}
                    </div>
                    <div style="margin-left:20px; flex-grow:1;">
                        <strong>{row['Hora']}</strong> | Rodada: {row['Rodada']} | Status: {row['Status']}
                    </div>
                    <div style="display:flex; gap:5px;">
                        <div style="background:#1E90FF; color:white; padding:5px 10px; border-radius:5px;">1.75</div>
                        <div style="background:#808080; color:white; padding:5px 10px; border-radius:5px;">3.50</div>
                        <div style="background:#FF4500; color:white; padding:5px 10px; border-radius:5px;">3.20</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


