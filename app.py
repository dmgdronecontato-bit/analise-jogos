import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Painel de Jogos", layout="wide")
st.title("🎲 Painel de Jogos e Odds - TheOddsAPI")

# =========================
# Configuração das API Keys
# =========================
THEODDS_API_KEY = st.secrets["THEODDS_API_KEY"]

# =========================
# Competitions (exemplo)
# =========================
competitions = {
    "Premier League": "soccer_epl",
    "Serie A": "soccer_italy_serie_a",
    "Campeonato Brasileiro": "soccer_brazil_campeonato_brasileiro",
    "UEFA Champions League": "soccer_uefa_champs_league",
    "FIFA World Cup": "soccer_fifa_world_cup"
}

# Dropdown de campeonato
champ = st.selectbox("Selecione a competição:", list(competitions.keys()))
sport_key = competitions[champ]

# Dropdown de filtro de status
status_filter = st.selectbox(
    "Filtrar jogos por status:",
    ["Todos", "Somente Hoje", "Em andamento", "Próximos", "Finalizados"]
)

# =========================
# Buscar jogos da TheOddsAPI
# =========================
url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
params = {
    "apiKey": THEODDS_API_KEY,
    "regions": "eu,us",  # Europa e EUA
    "markets": "h2h",    # 1X2
    "oddsFormat": "decimal"
}

response = requests.get(url, params=params)

if response.status_code != 200:
    st.error(f"Erro ao buscar dados da API. Status code: {response.status_code}")
    st.stop()

data = response.json()
tz_brasil = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(tz_brasil)

# =========================
# Processar jogos
# =========================
jogos_filtrados = []

for match in data:
    # Data do jogo
    dt_utc = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
    dt_brasil = dt_utc.astimezone(tz_brasil)
    
    # Status do jogo
    if match.get("status") in ["inprogress", "live"]:
        status = "Em andamento"
    elif dt_brasil.date() < hoje.date():
        status = "Finalizados"
    else:
        status = "Próximos"
    
    # Filtro
    if status_filter != "Todos":
        if status_filter == "Somente Hoje" and dt_brasil.date() != hoje.date():
            continue
        elif status_filter not in ["Todos", "Somente Hoje"] and status != status_filter:
            continue

    # Times
    home_team = match["home_team"]
    away_team = match["away_team"]
    
    # Odds (primeira casa de apostas disponível)
    odds_home = odds_draw = odds_away = "N/A"
    if match.get("bookmakers"):
        first_bookmaker = match["bookmakers"][0]
        for market in first_bookmaker["markets"]:
            if market["key"] == "h2h":
                odds_list = market["outcomes"]
                if len(odds_list) == 2:  # apenas dois outcomes (home/away)
                    odds_home = odds_list[0]["price"]
                    odds_away = odds_list[1]["price"]
                    odds_draw = "-"
                elif len(odds_list) == 3:  # 1X2
                    odds_home = odds_list[0]["price"]
                    odds_draw = odds_list[1]["price"]
                    odds_away = odds_list[2]["price"]

    # Escudos fictícios (pode substituir por API real ou imagens locais)
    escudo_home = f"https://logo.clearbit.com/{home_team.replace(' ', '').lower()}.com"
    escudo_away = f"https://logo.clearbit.com/{away_team.replace(' ', '').lower()}.com"

    jogos_filtrados.append({
        "data": dt_brasil.strftime("%d/%m/%Y"),
        "hora": dt_brasil.strftime("%H:%M"),
        "casa": home_team,
        "fora": away_team,
        "status": status,
        "casa_escudo": escudo_home,
        "fora_escudo": escudo_away,
        "odds": {"home": odds_home, "draw": odds_draw, "away": odds_away}
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
                    <strong>{row['hora']}</strong> | Status: {row['status']}
                </div>
                <div style="display:flex; gap:5px;">
                    <div style="background:#1E90FF; color:white; padding:5px 10px; border-radius:5px;">{row['odds']['home']}</div>
                    <div style="background:#808080; color:white; padding:5px 10px; border-radius:5px;">{row['odds']['draw']}</div>
                    <div style="background:#FF4500; color:white; padding:5px 10px; border-radius:5px;">{row['odds']['away']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

