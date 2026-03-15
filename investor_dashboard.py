import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURAZIONI STREAMLIT ---
st.set_page_config(page_title="Multiverse Quant Dashboard", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

# Token inserito tramite i "Secrets" di Streamlit Cloud (o variabili d'ambiente in test locale)
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"] if "GITHUB_TOKEN" in st.secrets else os.getenv("GITHUB_TOKEN")
GIST_ID = st.secrets["GIST_ID"] if "GIST_ID" in st.secrets else os.getenv("GIST_ID")

@st.cache_data(ttl=60) # Aggiorna i dati ogni 60 secondi senza fondere le API di GitHub
def fetch_risk_data():
    """Scarica il JSON dal Gist Segreto"""
    if not GITHUB_TOKEN or not GIST_ID:
        return None
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        if res.status_code == 200:
            content = res.json()["files"]["risk_config.json"]["content"]
            import json
            return json.loads(content)
    except Exception as e:
        st.error(f"Errore di connessione al Cloud: {e}")
    return None

# --- UI PRINCIPALE ---
st.title("🏦 Quant Trading Ecosystem | Chief Risk Officer Dashboard")
st.markdown("Monitoraggio in tempo reale dei regimi algoritmici e dell'esposizione al rischio globale.")

data = fetch_risk_data()

if data:
    # Metriche Globali
    total_bots = len(data)
    hot_bots = sum(1 for bot in data.values() if "HOT" in bot["status"])
    defensive_bots = sum(1 for bot in data.values() if "DEFENSIVE" in bot["status"])
    total_risk = sum(float(bot["current_risk"]) for bot in data.values())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Motori Attivi", total_bots)
    col2.metric("Regime HOT 🔥", hot_bots)
    col3.metric("Regime DEFENSIVE 🛡️", defensive_bots)
    col4.metric("Esposizione Max Globale", f"{total_risk:.2f}%")

    st.divider()

    # Creiamo un DataFrame per i grafici
    df_list = []
    for magic, info in data.items():
        # Pulizia della stringa del Win Rate per il grafico (es: "67%" -> 67)
        wr_clean = int(info["recent_winrate"].replace('%', '')) if info["recent_winrate"] != "N/A" else 0
        df_list.append({
            "Magic": magic,
            "Strategia": info["strategy"],
            "Stato": info["status"],
            "Rischio (%)": float(info["current_risk"]),
            "Win Rate Recente (%)": wr_clean
        })
    df = pd.DataFrame(df_list)

    # Layout a colonne per Grafici e Tabelle
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("📊 Win Rate per Strategia")
        # Grafico a barre
        fig = px.bar(df, x="Strategia", y="Win Rate Recente (%)", color="Stato", 
                     color_discrete_map={"🔥 HOT": "#ff4b4b", "🛡️ DEFENSIVE": "#456987", "⚪ NEUTRAL (No recent data)": "#555555"},
                     text="Win Rate Recente (%)")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("⚙️ Allocazione Rischio")
        # Grafico a torta
        fig_pie = px.pie(df, values='Rischio (%)', names='Strategia', hole=0.4)
        fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                              legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📋 Dettaglio Motori Quantitativi")
    # Tabella dati formattata
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.warning("In attesa dei dati dalla Virtual Machine o Token Mancante. Assicurati che l'Orchestratore sia online e che i Secrets siano impostati correttamente su Streamlit Cloud.")