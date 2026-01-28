import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="UFC Biomedical Dashboard",
    page_icon="🥊",
    layout="wide"
)

# --- 1. CONEXIÓN Y CARGA DE DATOS (Cacheada) ---
# Usamos @st.cache_data para que no recargue la SQL cada vez que mueves un filtro
@st.cache_data
def load_data():
    DB_STR = "postgresql://postgres:ufc123@127.0.0.1:5433/ufc_data"
    engine = create_engine(DB_STR)
    
    query = """
    SELECT 
        "Name", 
        "Height_cms", 
        "Reach_cms", 
        "Weight_kgs",
        ("Reach_cms" - "Height_cms") as "Ape_Index"
    FROM clean_fighters 
    WHERE "Height_cms" IS NOT NULL 
      AND "Reach_cms" IS NOT NULL
    ;
    """
    df = pd.read_sql(query, engine)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error conectando a la base de datos: {e}")
    st.stop()

# --- 2. BARRA LATERAL (FILTROS) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/UFC_Logo.svg/2560px-UFC_Logo.svg.png", width=150)
st.sidebar.header("🎛️ Filtros Biomédicos")

# Filtro de Peso (Slider doble)
min_w, max_w = int(df["Weight_kgs"].min()), int(df["Weight_kgs"].max())
weight_range = st.sidebar.slider(
    "Rango de Peso (kg)",
    min_value=min_w,
    max_value=max_w,
    value=(50, 130) # Valor por defecto
)

# Filtro de Ape Index
ape_filter = st.sidebar.radio(
    "Tipo de Morfología",
    ["Todos", "Ventaja (Brazos Largos)", "Desventaja (Brazos Cortos)"]
)

# --- APLICAR FILTROS ---
df_filtered = df[
    (df["Weight_kgs"] >= weight_range[0]) & 
    (df["Weight_kgs"] <= weight_range[1])
]

if ape_filter == "Ventaja (Brazos Largos)":
    df_filtered = df_filtered[df_filtered["Ape_Index"] > 0]
elif ape_filter == "Desventaja (Brazos Cortos)":
    df_filtered = df_filtered[df_filtered["Ape_Index"] <= 0]

# --- 3. DASHBOARD PRINCIPAL ---
st.title("🥊 Análisis Biomecánico de la UFC")
st.markdown("Explorando la ventaja evolutiva del **'Ape Index'** en atletas de alto rendimiento.")

# METRICAS (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Atletas Analizados", len(df_filtered))
col2.metric("Altura Promedio", f"{df_filtered['Height_cms'].mean():.1f} cm")
col3.metric("Alcance Promedio", f"{df_filtered['Reach_cms'].mean():.1f} cm")
col4.metric("Ape Index Promedio", f"+{df_filtered['Ape_Index'].mean():.1f} cm", delta_color="normal")

st.markdown("---")

# --- GRÁFICA 1: SCATTER PLOT INTERACTIVO ---
st.subheader("🧬 Mapa de Ventaja Genética")

# Configuración visual (Tu estilo "Pro")
plt.rcParams['font.family'] = 'sans-serif'
sns.set_theme(style="whitegrid", context="talk")

fig1, ax1 = plt.figure(figsize=(12, 8)), plt.gca()

# Lógica de color
cmap = sns.color_palette("blend:crimson,gold,seagreen", as_cmap=True)
norm = plt.Normalize(vmin=df['Ape_Index'].min(), vmax=df['Ape_Index'].max())

scatter = sns.scatterplot(
    data=df_filtered, 
    x="Height_cms", y="Reach_cms", 
    hue="Ape_Index", size="Weight_kgs",
    sizes=(50, 400), palette=cmap, hue_norm=norm,
    alpha=0.85, edgecolor="white", linewidth=1, legend=False, ax=ax1
)

# Línea 1:1
min_val = min(df_filtered["Height_cms"].min(), df_filtered["Reach_cms"].min())
max_val = max(df_filtered["Height_cms"].max(), df_filtered["Reach_cms"].max())
ax1.plot([min_val, max_val], [min_val, max_val], color='#333333', linestyle='--', linewidth=2)
ax1.text(max_val, max_val-1, "Humano Promedio (1:1)", ha='right', va='top', fontsize=10, color='gray')

ax1.set_xlabel("Altura (cm)", fontweight='bold')
ax1.set_ylabel("Envergadura (cm)", fontweight='bold')
ax1.set_title("Relación Altura vs. Alcance", fontweight='bold')

# Mostramos en Streamlit
st.pyplot(fig1)

# --- GRÁFICA 2: HISTOGRAMA ---
st.subheader("📊 Distribución de la Ventaja")

fig2, ax2 = plt.figure(figsize=(12, 6)), plt.gca()
sns.histplot(df_filtered["Ape_Index"], kde=True, bins=25, color="seagreen", ax=ax2)
ax2.axvline(0, color='black', linestyle='--', linewidth=2)
ax2.axvline(df_filtered["Ape_Index"].mean(), color='blue', linewidth=3)

ax2.set_xlabel("Diferencia (Alcance - Altura)", fontweight='bold')
ax2.set_ylabel("Cantidad de Atletas", fontweight='bold')

col_graph1, col_graph2 = st.columns([3, 1])
with col_graph1:
    st.pyplot(fig2)
with col_graph2:
    st.info(f"""
    **Interpretación:**
    
    La línea azul indica el promedio del grupo seleccionado.
    
    Actualmente es de **+{df_filtered['Ape_Index'].mean():.1f} cm**.
    
    Esto confirma que en este rango de peso, la morfología favorece brazos largos.
    """)

# --- TABLA DE DATOS ---
with st.expander("🔎 Ver Datos Crudos"):
    st.dataframe(df_filtered.sort_values("Ape_Index", ascending=False))