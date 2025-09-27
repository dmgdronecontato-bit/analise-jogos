import pytz
from datetime import datetime
import streamlit as st

# Timezone Brasil
tz_brasil = pytz.timezone("America/Sao_Paulo")

# Mapeamento dos status
status_map = {
    "SCHEDULED": "Próximos",
    "LIVE": "Em andamento",
    "IN_PLAY": "Em andamento",
    "PAUSED": "Em andamento",
    "FINISHED": "Finalizados",
    "POSTPONED": "Adiado",
    "CANCELED": "Cancelado"
}

# Dropdown extra
filtro_status = st.selectbox(
    "Filtrar jogos por status:",
    ["Todos", "Somente Hoje", "Em andamento", "Próximos", "Finalizados"]
)

jogos_filtrados = []
for match in data["matches"]:
    # Converte data para Brasil
    dt_utc = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
    dt_brasil = dt_utc.astimezone(tz_brasil)

    status = status_map.get(match["status"], match["status"])

    # Filtro de status
    if filtro_status != "Todos":
        if filtro_status == "Somente Hoje":
            if dt_brasil.date() != datetime.now(tz_brasil).date():
                continue
        elif status != filtro_status:
            continue

    jogos_filtrados.append({
        "data": dt_brasil.strftime("%d/%m/%Y"),
        "hora": dt_brasil.strftime("%H:%M"),
        "casa": match["homeTeam"]["name"],
        "fora": match["awayTeam"]["name"],
        "status": status
    })

# Ordenar por data/hora
jogos_filtrados = sorted(jogos_filtrados, key=lambda x: (x["data"], x["hora"]))

# Exibir jogos
for jogo in jogos_filtrados:
    st.markdown(
        f"**{jogo['data']} {jogo['hora']}** — "
        f"{jogo['casa']} 🆚 {jogo['fora']} "
        f"({jogo['status']})"
    )

