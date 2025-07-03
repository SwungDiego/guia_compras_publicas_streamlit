import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Página de Contrato", layout="wide")
st.title("Página de Contrato")
st.markdown("## Datos de Contratación Pública en Ecuador 2025")

# Sidebar con filtros
st.sidebar.title("Filtros")
st.sidebar.markdown("### Fuente de datos")
st.sidebar.markdown("[Link del sitio de los datos oficiales](https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/procedimientos?local=1&year=2025&page=1)")

# Opciones para los filtros
años = [str(a) for a in range(2015, 2026)]
provincias = ["Todos", "AZUAY", "BOLÍVAR", "CAÑAR", "CARCHI", "CHIMBORAZO", "COTOPAXI", "EL ORO",
    "ESMERALDAS", "GALÁPAGOS", "GUAYAS", "IMBABURA", "LOJA", "LOS RÍOS",
    "MANABÍ", "MORONA SANTIAGO", "NAPO", "ORELLANA", "PASTAZA", "PICHINCHA",
    "SANTA ELENA", "SANTO DOMINGO DE LOS TSÁCHILAS", "SUCUMBÍOS", "TUNGURAHUA",
    "ZAMORA CHINCHIPE"]

tipos_contratacion = [
    "Todos", "Subasta Inversa Electrónica", "Menor Cuantía", "Cotización",
    "Contratacion directa", "Licitación", "Catálogo electrónico", "Bienes y Servicios únicos"
]

anio_seleccionado = st.sidebar.selectbox("Seleccione el año", años, index=años.index("2025"))
provincia_seleccionada = st.sidebar.selectbox("Seleccione la provincia", provincias)
tipo_contratacion_seleccionado = st.sidebar.selectbox("Seleccione el tipo de contratación", tipos_contratacion)

# Carga de los datos actuales
url = "https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/get_analysis"
params = {
    "local": 1,
    "year": anio_seleccionado,
    "province": provincia_seleccionada if provincia_seleccionada != "Todos" else "",
    "type": tipo_contratacion_seleccionado if tipo_contratacion_seleccionado != "Todos" else "",
}
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    df_filtrado = pd.DataFrame(data)

    if df_filtrado.empty:
        st.warning("No hay datos para los filtros seleccionados.")
    else:
        st.dataframe(df_filtrado.head())
        st.success("Datos cargados automáticamente.")

        # Conteo por mes y gráfico de barras 
        st.markdown("### Procedimientos por Mes")
        df_mes = df_filtrado["month"].value_counts().sort_index()
        fig_mes = px.bar(x=df_mes.index, y=df_mes.values,
                         labels={'x': 'Mes', 'y': 'Cantidad'},
                         title="Gráfico de Barras - Procedimientos por Mes")
        st.plotly_chart(fig_mes)

        # Conteo por tipo de contratación
        if "type" in df_filtrado.columns:
            st.markdown("### Procedimientos por Tipo de Contratación")
            df_tipo = df_filtrado["type"].value_counts().sort_values(ascending=False)
            fig_tipo = px.pie(names=df_tipo.index, values=df_tipo.values,
                              title="Gráfico de Pastel - Tipos de Contratación")
            st.plotly_chart(fig_tipo)

        # Conteo por estado (si existe)
        if "state" in df_filtrado.columns:
            st.markdown("### Procedimientos por Estado")
            df_estado = df_filtrado["state"].value_counts()
            fig_estado = px.bar(x=df_estado.index, y=df_estado.values,
                                labels={"x": "Estado", "y": "Cantidad"},
                                title="Gráfico de Barras - Estados de Contratos")
            st.plotly_chart(fig_estado)

        # Gráfica anual automática
        st.markdown("### Procedimientos por Año")
        data_anual = []
        for year in range(2015, 2026):
            url_anual = f"https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/get_analysis?local=1&year={year}"
            try:
                resp = requests.get(url_anual)
                if resp.status_code == 200:
                    datos = resp.json()
                    if isinstance(datos, list):
                        for item in datos:
                            item["year"] = year
                            data_anual.append(item)
            except Exception as e:
                st.warning(f"Error al obtener datos del año {year}: {e}")

        if data_anual:
            df_anual = pd.DataFrame(data_anual)
            df_cuenta = df_anual["year"].value_counts().sort_index().reset_index()
            df_cuenta.columns = ["Año", "Cantidad"]

            fig_anual = px.line(
                df_cuenta,
                x="Año",
                y="Cantidad",
                markers=True,
                title="Número de Procedimientos por Año (2015–2025)"
            )
            st.plotly_chart(fig_anual)
        else:
            st.error("No se pudieron obtener datos históricos.")
else:
    st.error("Error al cargar los datos desde la API.")
