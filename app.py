{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fswiss\fcharset0 Helvetica-Light;}
{\colortbl;\red255\green255\blue255;\red25\green28\blue31;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c12941\c14510\c16078;\cssrgb\c0\c0\c0\c5098;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import requests\
import pandas as pd\
from datetime import datetime\
\
st.title("\uc0\u55357 \u56522  Sistema de An\'e1lise de Jogos")\
\
API_KEY = "
\f1 \cf2 \cb3 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 e50f1ce938e544f29d2a914189d13bd4
\f0 \cf0 \cb1 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 "\
headers = \{"X-Auth-Token": API_KEY\}\
\
# Exemplo: Premier League (competi\'e7\'e3o 2021)\
url = "https://api.football-data.org/v4/competitions/2021/matches"\
response = requests.get(url, headers=headers)\
\
if response.status_code != 200:\
    st.error("Erro ao buscar dados da API. Verifique sua chave e conex\'e3o.")\
else:\
    data = response.json()\
    today = datetime.today().strftime("%Y-%m-%d")\
    matches_today = [m for m in data.get("matches", []) if m["utcDate"].startswith(today)]\
\
    if matches_today:\
        df = pd.DataFrame([\{\
            "Casa": m["homeTeam"]["name"],\
            "Fora": m["awayTeam"]["name"],\
            "Rodada": m["matchday"],\
            "Data": m["utcDate"][:10],\
            "Status": m["status"]\
        \} for m in matches_today])\
        st.subheader("Jogos de hoje")\
        st.dataframe(df)\
    else:\
        st.info("Nenhum jogo hoje na competi\'e7\'e3o selecionada.")\
}