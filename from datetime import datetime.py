from datetime import datetime
import geopandas as gpd
import matplotlib.pyplot as plt
from meteostat import Daily, Point
import numpy as np
from shapely.geometry import Polygon
import streamlit as st  # <-- Mudado de 'str' para 'st' para evitar conflitos

# Configuração da página do site
st.set_page_config(
    page_title="AgroTech Dashboard", page_icon="🌱", layout="wide"
)

st.title("🌱 Painel de Ferramentas Agronômicas")
st.markdown("Bem-vindo ao seu ambiente de análise agrícola digital.")

# Criando o menu de navegação por abas no site
aba1, aba2, aba3 = st.tabs(
    ["🌦️ Clima Histórico", "🗺️ Mapeamento de Talhão", "🛰️ Cálculo de NDVI"]
)

# -------------------------------------------------------------------------
# ABA 1: CLIMA HISTÓRICO
# ---------------------python3 -m streamlit run app.py----------------------------------------------------
with aba1:
    st.header("Análise Climática Local (Meteostat)")
    st.write("Monitore a temperatura e chuva de qualquer coordenada.")

    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input(
            "Latitude", value=-21.1775, format="%.4f", key="lat"
        )
    with col2:
        lon = st.number_input(
            "Longitude", value=-47.8103, format="%.4f", key="lon"
        )

    if st.button("Buscar Dados Climáticos"):
        with st.spinner("Coletando dados..."):
            localizacao = Point(lat, lon)
            inicio = datetime(2025, 1, 1)
            fim = datetime(2025, 12, 31)

            dados = Daily(localizacao, inicio, fim).fetch()

            if not dados.empty:
                fig, ax1 = plt.subplots(figsize=(10, 4))
                ax1.set_ylabel("Temperatura Média (°C)", color="red")
                ax1.plot(
                    dados.index, dados["tavg"], color="red", label="Temp. Média"
                )
                ax1.tick_params(axis="y", labelcolor="red")

                ax2 = ax1.twinx()
                ax2.set_ylabel("Precipitação (mm)", color="blue")
                ax2.bar(
                    dados.index,
                    dados["prcp"],
                    color="blue",
                    alpha=0.3,
                    label="Chuva",
                )
                ax2.tick_params(axis="y", labelcolor="blue")

                plt.title("Histórico de Clima (2025)")

                st.pyplot(fig)
                st.dataframe(
                    dados[["tavg", "prcp"]].rename(
                        columns={
                            "tavg": "Temp Média (°C)",
                            "prcp": "Chuva (mm)",
                        }
                    )
                )
            else:
                st.error(
                    "Não foram encontrados dados para as coordenadas informadas."
                )

# -------------------------------------------------------------------------
# ABA 2: MAPEAMENTO DE TALHÃO
# -------------------------------------------------------------------------
with aba2:
    st.header("Cálculo de Área e Desenho de Talhões")
    st.write(
        "Desenhe um polígono baseado em coordenadas GPS para medir a área em Hectares."
    )

    coordenadas_texto = st.text_area(
        "Insira as coordenadas dos vértices (Longitude, Latitude) separadas por linha:",
        value="-47.810, -21.175\n-47.805, -21.175\n-47.805, -21.180\n-47.810, -21.180",
    )

    if st.button("Calcular e Mapear"):
        try:
            linhas = coordenadas_texto.strip().split("\n")
            pontos = [tuple(map(float, l.split(","))) for l in linhas]

            if pontos[0] != pontos[-1]:
                pontos.append(pontos[0])

            poligono = Polygon(pontos)
            gdf = gpd.GeoDataFrame(
                index=[0], crs="EPSG:4326", geometry=[poligono]
            )

            gdf_metrico = gdf.to_crs(epsg=31982)
            area_ha = gdf_metrico.geometry.area.iloc[0] / 10000

            st.metric(label="Área Total do Talhão", value=f"{area_ha:.2f} ha")

            fig, ax = plt.subplots(figsize=(6, 4))
            gdf.plot(
                ax=ax, edgecolor="green", facecolor="green", alpha=0.3, lw=2
            )
            plt.title("Geometria do Talhão")
            plt.grid(True)
            st.pyplot(fig)

        except Exception as e:
            st.error(
                f"Erro ao processar as coordenadas. Formato correto: Longitude, Latitude. Erro: {e}"
            )

# -------------------------------------------------------------------------
# ABA 3: CÁLCULO DE NDVI (SIMULADO)
# -------------------------------------------------------------------------
with aba3:
    st.header("Análise de Índice de Vegetação (NDVI)")
    st.write("Simulação de matriz de dados de satélite para análise de vigor.")

    simular = st.checkbox(
        "Simular dados de satélite automaticamente para teste", value=True
    )

    if simular:
        np.random.seed(42)
        nir = np.random.uniform(0.2, 0.8, (100, 100))
        red = np.random.uniform(0.05, 0.3, (100, 100))

        ndvi = (nir - red) / (nir + red)

        fig, ax = plt.subplots(figsize=(7, 5))
        img = ax.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
        fig.colorbar(img, label="Saúde da Planta (NDVI)")
        plt.title("Mapa de Calor da Lavoura (Simulado)")

        st.pyplot(fig)
        st.info(
            "No NDVI, áreas verdes escuras representam plantas saudáveis. Áreas vermelhas indicam solo exposto ou estresse severo."
        )