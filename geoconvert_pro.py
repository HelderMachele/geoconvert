import pandas as pd
import pyproj
import streamlit as st
from openpyxl import load_workbook
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import simplekml

# Configuração da página
st.set_page_config(
    page_title="GeoConvert Pro | Por Hélder Machele",
    layout="centered",
    page_icon="🌍"
)

# Cores profissionais
primary_color = "#2A5C8D"
secondary_color = "#4E8BBF"
accent_color = "#49505a"
background_color = "#8a7e74"
text_color = "#000000"

# CSS personalizado
st.markdown(f"""
<style>
    .stApp {{
        background-color: {background_color};
    }}
    .result-container {{
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid {accent_color};
    }}
    .result-title {{
        color: {primary_color};
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
    }}
    .result-value {{
        color: {text_color};
        font-weight: bold;
        font-size: 1.1rem;
        margin-left: 10px;
    }}
    .stButton>button {{
        background-color: {primary_color} !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header">
    <h1 style="margin-bottom: 0;">🌍 GeoConvert</h1>
    <p style="color: {text_color}; margin-top: 10px;">Conversor de Coordenadas Geográficas de Decimal  ↔  UTM com Visualização em Mapa</p>
</div>
""", unsafe_allow_html=True)

# Funções auxiliares
def calcular_distancia(ponto1, ponto2):
    return geodesic(ponto1, ponto2).meters

def criar_kml(coordenadas, nome_arquivo="pontos.kml"):
    kml = simplekml.Kml()
    for i, (lat, lon) in enumerate(coordenadas, 1):
        kml.newpoint(name=f"Ponto {i}", coords=[(lon, lat)])
    return kml.kml()

def converter_decimal_para_utm(lat, lon):
    zona = int((lon + 180)/6) + 1
    proj_utm = pyproj.Proj(proj='utm', zone=zona, ellps='WGS84', south=(lat < 0))
    easting, northing = proj_utm(lon, lat)
    return zona, easting, northing

def converter_utm_para_decimal(zona, easting, northing, hemisferio='S'):
    proj_utm = pyproj.Proj(proj='utm', zone=zona, ellps='WGS84', south=(hemisferio == 'S'))
    lon, lat = proj_utm(easting, northing, inverse=True)
    return lat, lon

def criar_mapa(lat, lon, zoom=15):
    mapa = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        attr='OpenStreetMap'
    )
    folium.Marker(
        [lat, lon],
        popup=f"Lat: {lat:.6f}<br>Lon: {lon:.6f}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(mapa)
    folium.Circle(
        radius=50,
        location=[lat, lon],
        color=primary_color,
        fill=True,
        fill_color=accent_color
    ).add_to(mapa)
    return mapa

# Interface principal
tab1, tab2 = st.tabs(["🔢 Conversão Manual", "📁 Conversão por Ficheiro"])

with tab1:
    modo = st.radio("Tipo de conversão:", ("Decimal → UTM", "UTM → Decimal"), horizontal=True)

    if modo == "Decimal → UTM":
        lat = st.number_input("Latitude (decimal)", value=-25.0143, format="%.8f")
        lon = st.number_input("Longitude (decimal)", value=32.5833, format="%.8f")
        if st.button("Converter para UTM"):
            try:
                zona, easting, northing = converter_decimal_para_utm(lat, lon)
                st.markdown(f"""
                <div class=\"result-container\">
                    <div class=\"result-title\">📌 Resultado UTM</div>
                    <p><strong>Zona:</strong> <span class=\"result-value\">{zona}</span></p>
                    <p><strong>Easting:</strong> <span class=\"result-value\">{easting:.3f}</span></p>
                    <p><strong>Northing:</strong> <span class=\"result-value\">{northing:.3f}</span></p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <div class=\"result-container\">
                    <div class=\"result-title\">🗺️ Visualização no Mapa</div>
                </div>
                """, unsafe_allow_html=True)
                mapa = criar_mapa(lat, lon)
                folium_static(mapa, width=700, height=500)
            except Exception as e:
                st.error(f"Erro na conversão: {str(e)}")

    else:
        zona = st.number_input("Zona UTM", min_value=1, max_value=60, value=36)
        easting = st.number_input("Easting", value=754128.00)
        northing = st.number_input("Northing", value=6947467.00)
        hemisferio = st.radio("Hemisfério", ['Norte', 'Sul'], index=1, horizontal=True)
        if st.button("Converter para Decimal"):
            try:
                lat, lon = converter_utm_para_decimal(zona, easting, northing, hemisferio[0])
                st.markdown(f"""
                <div class=\"result-container\">
                    <div class=\"result-title\">📌 Resultado Decimal</div>
                    <p><strong>Latitude:</strong> <span class=\"result-value\">{lat:.8f}</span></p>
                    <p><strong>Longitude:</strong> <span class=\"result-value\">{lon:.8f}</span></p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <div class=\"result-container\">
                    <div class=\"result-title\">🗺️ Visualização no Mapa</div>
                </div>
                """, unsafe_allow_html=True)
                mapa = criar_mapa(lat, lon)
                folium_static(mapa, width=700, height=500)
            except Exception as e:
                st.error(f"Erro na conversão: {str(e)}")
# (continuação do código)

with tab2:
    modo_arquivo = st.radio("Tipo de conversão:", ("Decimal → UTM", "UTM → Decimal"), key='file_mode', horizontal=True)
    uploaded_file = st.file_uploader("Carregue o ficheiro (CSV ou Excel)", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl') if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
            st.markdown("""
            <div class=\"result-container\">
                <div class=\"result-title\">📋 Pré-visualização dos Dados</div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df.head())

            if modo_arquivo == "Decimal → UTM":
                colunas = df.columns.tolist()
                col1, col2 = st.columns(2)
                with col1:
                    lat_col = st.selectbox("Coluna Latitude", colunas)
                with col2:
                    lon_col = st.selectbox("Coluna Longitude", colunas)

                if st.button("Processar Conversão"):
                    resultados = []
                    coordenadas_validas = []
                    for _, row in df.iterrows():
                        try:
                            lat = float(row[lat_col])
                            lon = float(row[lon_col])
                            zona, e, n = converter_decimal_para_utm(lat, lon)
                            resultados.append((zona, e, n))
                            coordenadas_validas.append((lat, lon))
                        except:
                            resultados.append(("Erro", "Erro", "Erro"))

                    df['Zona'] = [r[0] for r in resultados]
                    df['Easting'] = [r[1] for r in resultados]
                    df['Northing'] = [r[2] for r in resultados]

                    st.success("Conversão concluída com sucesso!")

                    if coordenadas_validas:
                        mapa = folium.Map(location=coordenadas_validas[0], zoom_start=10)
                        for lat, lon in coordenadas_validas:
                            folium.Marker([lat, lon], popup=f"Lat: {lat:.6f}, Lon: {lon:.6f}").add_to(mapa)
                        st.markdown("""
                        <div class=\"result-container\">
                            <div class=\"result-title\">🗺️ Mapa com Todos os Pontos</div>
                        </div>
                        """, unsafe_allow_html=True)
                        folium_static(mapa, width=700, height=500)

                    kml = criar_kml(coordenadas_validas)
                    st.download_button("⬇️ Baixar KML", data=kml, file_name="resultado.kml", mime="application/vnd.google-earth.kml+xml")
                    st.download_button("⬇️ Baixar CSV", data=df.to_csv(index=False, sep=';'), file_name="resultado_utm.csv", mime="text/csv")

            else:
                colunas = df.columns.tolist()
                col1, col2, col3 = st.columns(3)
                with col1:
                    zona_col = st.selectbox("Coluna Zona", colunas)
                with col2:
                    easting_col = st.selectbox("Coluna Easting", colunas)
                with col3:
                    northing_col = st.selectbox("Coluna Northing", colunas)
                hemisferio = st.radio("Hemisfério", ['Norte', 'Sul'], index=1, key='hemisferio_file', horizontal=True)

                if st.button("Processar Conversão"):
                    resultados_latlon = []
                    coordenadas_validas = []
                    for _, row in df.iterrows():
                        try:
                            lat, lon = converter_utm_para_decimal(int(row[zona_col]), float(row[easting_col]), float(row[northing_col]), hemisferio[0])
                            resultados_latlon.append((lat, lon))
                            coordenadas_validas.append((lat, lon))
                        except:
                            resultados_latlon.append(("Erro", "Erro"))

                    df['Latitude'] = [r[0] for r in resultados_latlon]
                    df['Longitude'] = [r[1] for r in resultados_latlon]

                    st.success("Conversão concluída com sucesso!")

                    if coordenadas_validas:
                        mapa = folium.Map(location=coordenadas_validas[0], zoom_start=10)
                        for lat, lon in coordenadas_validas:
                            folium.Marker([lat, lon], popup=f"Lat: {lat:.6f}, Lon: {lon:.6f}").add_to(mapa)
                        st.markdown("""
                        <div class=\"result-container\">
                            <div class=\"result-title\">🗺️ Mapa com Todos os Pontos</div>
                        </div>
                        """, unsafe_allow_html=True)
                        folium_static(mapa, width=700, height=500)

                    kml = criar_kml(coordenadas_validas)
                    st.download_button("⬇️ Baixar KML", data=kml, file_name="resultado.kml", mime="application/vnd.google-earth.kml+xml")
                    st.download_button("⬇️ Baixar CSV", data=df.to_csv(index=False, sep=';'), file_name="resultado_decimal.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Erro ao processar o ficheiro: {str(e)}")

# Rodapé
st.markdown(f"""
<div style="text-align: center; margin-top: 40px; color: {primary_color};">
    <p>© 2025 GeoConvert | Desenvolvido por Hélder Machele</p>
    <p>
        <a href="https://www.linkedin.com/in/h%C3%A9lder-victor-tom%C3%A1s-machele-5229bb343/" target="_blank" style="color: {primary_color}; text-decoration: none;">
           👨‍💻 Conecte-se no LinkedIn
        </a>
    </p>
</div>
""", unsafe_allow_html=True)
