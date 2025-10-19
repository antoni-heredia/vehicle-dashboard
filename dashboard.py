import streamlit as st
import pandas as pd
import clickhouse_connect
import time

# --- Configuración ClickHouse ---
CH_HOST = "localhost"   # usa "localhost" si corres fuera de Docker
CH_PORT = 8123
CH_USER = "default"
CH_PASS = ""
CH_DB = "default"

client = clickhouse_connect.get_client(
    host=CH_HOST,
    port=CH_PORT,
    username=CH_USER,
    password=CH_PASS,
    database=CH_DB,
)

st.set_page_config(page_title="Mapa flota vehículos", layout="wide")
st.title("🚗 Mapa en tiempo real de vehículos")

# --- Panel lateral ---
limit = st.sidebar.slider("Número de registros recientes", 100, 10000, 1000)
refresh = st.sidebar.slider("Refresco (segundos)", 2, 30, 5)

def load_data():
    query = f"""
        SELECT
            vehicle_id,
            lat,
            lon,
            speed_kmh,
            rpm,
            oil_temp,
            fuel,
            timestamp
        FROM vehicle_data
        ORDER BY timestamp DESC
        LIMIT {limit}
    """
    df = client.query_df(query)
    return df

placeholder_map = st.empty()
placeholder_table = st.empty()

# --- Bucle de refresco ---
while True:
    df = load_data()
    if df.empty:
        st.warning("No hay datos disponibles en ClickHouse.")
    else:
        # Color por velocidad (gradiente simple)
        min_v, max_v = df["speed_kmh"].min(), df["speed_kmh"].max()
        df["color"] = df["speed_kmh"].apply(
            lambda v: f"#{int(255*(v-min_v)/(max_v-min_v+0.01)):02x}3030"
        )

        st.subheader(f"{len(df)} vehículos activos")

        # Mapa básico nativo
        placeholder_map.map(df, latitude="lat", longitude="lon")

        # Tabla con datos
        placeholder_table.dataframe(df[["vehicle_id", "speed_kmh", "fuel", "timestamp"]])

    time.sleep(refresh)
