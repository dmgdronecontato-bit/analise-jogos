import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

st.set_page_config(page_title="Painel de Jogos", layout="wide")
st.title("🎲 Painel de Jogos e Odds - Estilo Betano")

# =========================
# Configuração da API
# =========================
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

# Dropdown de campeonato
champ = st.selectbox("Selecione a competição:", list(competitions.keys()))
comp_id = competitions[champ]

# Dropdown de filtro de status
status_filter = st.selectbox(
    "Filtrar jogos por status:",
    ["Todos", "Somente Hoje", "Em andamento", "Próximos", "Finalizados"]
)

# =========================
# Buscar jogos da API
# =========================
url = f"https://api.football-data.org/v4/competitions/{comp_id}/matches"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    st.error("Erro ao buscar dados da API. Verifique sua chave e conexão.")
    data = {"matches": []}
else:
    data = response.json()

# =========================
# Configuração de timezone e mapeamento status
# =========================
tz_brasil = pytz.timezone("America/Sao_Paulo")
status_map = {
    "SCHEDULED": "Próximos",
    "LIVE": "Em andamento",
    "IN_PLAY": "Em andamento",
    "PAUSED": "Em andamento",
    "FINISHED": "Finalizados",
    "POSTPONED": "Adiado",
    "CANCELED": "Cancelado"
}

# =========================
# Processar jogos
# =========================
jogos_filtrados = []

for match in data.get("matches", []):
    # Converte data para Brasil
    dt_utc = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
    dt_brasil = dt_utc.astimezone(tz_brasil)
    status = status_map.get(match["status"], match["status"])

    # Filtro de status
    if status_filter != "Todos":
        if status_filter == "Somente Hoje":
            if dt_brasil.date() != datetime.now(tz_brasil).date():
                continue
        elif status != status_filter:
            continue

    # Escudos (se disponíveis)
    casa_escudo = match["homeTeam"].get("crest", "")
    fora_escudo = match["awayTeam"].get("crest", "")

    jogos_filtrados.append({
        "data": dt_brasil.strftime("%d/%m/%Y"),
        "hora": dt_brasil.strftime("%H:%M"),
        "casa": match["homeTeam"]["name"],
        "fora": match["awayTeam"]["name"],
        "status": status,
        "rodada": match.get("matchday", ""),
        "casa_escudo": casa_escudo,
        "fora_escudo": fora_escudo
    })

# Ordenar por data e hora
jogos_filtrados = sorted(jogos_filtrados, key=lambda x: (x["data"], x["hora"]))

# =========================
# Exibir jogos
# =========================
if not jogos_filtrados:
    st.info("Nenhum jogo encontrado com os filtros selecionados.")
else:
    for date, group in pd.DataFrame(jogos_filtrados).groupby("data"):
        st.markdown(f"## 📅 {date}")
        for _, row in group.iterrows():
            st.markdown(f"""
            <div style="border:1px solid #ccc; border-radius:10px; margin-bottom:10px; padding:10px; display:flex; align-items:center; background:#f0f2f6;">
                <div style="width:90px; text-align:center; font-weight:bold;">
                    <img src="{row['casa_escudo']}" width="50"><br>{row['casa']}
                </div>
                <div style="width:30px; text-align:center; font-size:20px;"><strong>X</strong></div>
                <div style="width:90px; text-align:center; font-weight:bold;">
                    <img src="{row['fora_escudo']}" width="50"><br>{row['fora']}
                </div>
                <div style="margin-left:20px; flex-grow:1;">
                    <strong>{row['hora']}</strong> | Rodada: {row['rodada']} | Status: {row['status']}
                </div>
                <div style="display:flex; gap:5px;">
                    <div style="background:#1E90FF; color:white; padding:5px 10px; border-radius:5px;">1.75</div>
                    <div style="background:#808080; color:white; padding:5px 10px; border-radius:5px;">3.50</div>
                    <div style="background:#FF4500; color:white; padding:5px 10px; border-radius:5px;">3.20</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

