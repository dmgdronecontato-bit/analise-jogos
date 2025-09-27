import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Painel de Jogos e Odds", layout="wide")
st.title("🎲 Painel de Jogos, Escudos e Odds - API-Football")

# =========================
# API Key
# =========================
API_FOOTBALL_KEY = st.secrets["API_FOOTBALL_KEY"]
headers = {"x-apisports-key": API_FOOTBALL_KEY}

# =========================
# Campeonatos disponíveis
# =========================
competitions = {
    "Campeonato Brasileiro Série A": 71,
    "Premier League": 39,
    "Serie A (Itália)": 135,
    "UEFA Champions League": 2,
    "FIFA World Cup": 1
}

# =========================
# Sidebar - filtros
# =========================
st.sidebar.header("Filtros")
champ = st.sidebar.selectbox("Selecione o campeonato:", list(competitions.keys()))
status_filter = st.sidebar.selectbox(
    "Filtrar jogos por status:",
    ["Todos", "Somente Hoje", "Em andamento", "Próximos", "Finalizados"]
)

league_id = competitions[champ]

# =========================
# Buscar jogos da API-Football
# =========================
tz_brasil = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(tz_brasil)

# Pegando os próximos 50 jogos da liga
url = "https://v3.football.api-sports.io/fixtures"
params = {
    "league": league_id,
    "season": 2025,  # temporada
    "next": 50
}
response = requests.get(url, headers=headers, params=params)
if response.status_code != 200:
    st.error(f"Erro ao buscar dados da API. Status code: {response.status_code}")
    st.stop()

data = response.json()["response"]

# =========================
# Processar jogos
# =========================
jogos_filtrados = []

for item in data:
    fixture = item["fixture"]
    teams = item["teams"]
    goals = item["goals"]

    dt_utc = datetime.fromisoformat(fixture["date"].replace("Z", "+00:00"))
    dt_brasil = dt_utc.astimezone(tz_brasil)

    # Status do jogo
    status_api = fixture["status"]["short"]
    if status_api in ["1H", "2H", "LIVE"]:
        status = "Em andamento"
    elif dt_brasil.date() < hoje.date():
        status = "Finalizados"
    else:
        status = "Próximos"

    # Filtrar
    if status_filter != "Todos":
        if status_filter == "Somente Hoje" and dt_brasil.date() != hoje.date():
            continue
        elif status_filter not in ["Todos", "Somente Hoje"] and status != status_filter:
            continue

    # Odds 1X2 (quando disponível)
    odds_data = item.get("odds", [])
    # API gratuita geralmente não retorna odds detalhadas
    # Para testes, podemos simular odds aleatórias se não houver
    if odds_data:
        # Pega primeiro bookmaker e as odds de 1X2
        bookmaker = odds_data[0]
        try:
            odds_1x2 = bookmaker["bets"][0]["values"]  # valores 1X2
            odd_home = odds_1x2[0]["odd"]
            odd_draw = odds_1x2[1]["odd"]
            odd_away = odds_1x2[2]["odd"]
        except:
            odd_home, odd_draw, odd_away = "-", "-", "-"
    else:
        odd_home, odd_draw, odd_away = "-", "-", "-"

    jogos_filtrados.append({
        "data": dt_brasil.strftime("%d/%m/%Y"),
        "hora": dt_brasil.strftime("%H:%M"),
        "home": teams["home"]["name"],
        "away": teams["away"]["name"],
        "home_escudo": teams["home"]["logo"],
        "away_escudo": teams["away"]["logo"],
        "status": status,
        "goals_home": goals["home"],
        "goals_away": goals["away"],
        "odd_home": odd_home,
        "odd_draw": odd_draw,
        "odd_away": odd_away
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
                    <img src="{row['home_escudo']}" width="50"><br>{row['home']}
                </div>
                <div style="width:30px; text-align:center; font-size:20px;"><strong>X</strong></div>
                <div style="width:90px; text-align:center; font-weight:bold;">
                    <img src="{row['away_escudo']}" width="50"><br>{row['away']}
                </div>
                <div style="margin-left:20px; flex-grow:1;">
                    <strong>{row['hora']}</strong> | Status: {row['status']}
                </div>
                <div style="display:flex; gap:5px;">
                    <div style="background:#1E90FF; color:white; padding:5px 10px; border-radius:5px;">{row['odd_home']}</div>
                    <div style="background:#808080; color:white; padding:5px 10px; border-radius:5px;">{row['odd_draw']}</div>
                    <div style="background:#FF4500; color:white; padding:5px 10px; border-radius:5px;">{row['odd_away']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

