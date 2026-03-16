import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard ADS - Demo Portafolio", layout="wide")

# --- 2. CONFIGURACIÓN DE ASSETS ---
dir_actual = os.path.dirname(__file__)
PATH_ASSETS = os.path.join(dir_actual, "assets")

logos = {
    "DirectTV": os.path.join(PATH_ASSETS, "1-DirectTV-logo.png"),
    "Prosegur": os.path.join(PATH_ASSETS, "2-Prosegur_new_company_logo.png"),
    "Claro": os.path.join(PATH_ASSETS, "3-Claro.svg.png"),
    "Facebook": os.path.join(PATH_ASSETS, "4-facebook-ads-logo.png"),
    "Google": os.path.join(PATH_ASSETS, "5-Google_Ads_logo.svg.png"),
    "Gout": os.path.join(PATH_ASSETS, "6-Logo_Header.png")
}

FONT_LABEL = dict(size=11, family="Arial")

# --- 3. FUNCIONES DE APOYO (DATOS ALEATORIOS) ---
def fmt_moneda(valor):
    return f"${valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def generar_datos_ficticios(lista_campanas, solo_google=False):
    data = []
    for camp in lista_campanas:
        inv_g = np.random.uniform(80000, 250000)
        inv_f = 0.0 if solo_google else np.random.uniform(40000, 180000)
        ventas = np.random.randint(15, 120)
        total_inv = inv_g + inv_f
        data.append({
            "Campaña": camp,
            "Inversión Google": inv_g,
            "Inversión Facebook": inv_f,
            "Inversión Total": total_inv,
            "Total Ventas": ventas,
            "CPV Acumulado": total_inv / ventas if ventas > 0 else 0
        })
    return pd.DataFrame(data)

# --- 4. COMPONENTES VISUALES ---
def mostrar_encabezado_principal():
    st.write("")
    c1, c2, c3 = st.columns(3)
    principales = [("Facebook", c1), ("Google", c2), ("Gout", c3)]
    for nombre, col in principales:
        with col:
            ruta = logos.get(nombre)
            if ruta and os.path.exists(ruta):
                try: st.image(ruta, width=180)
                except: st.subheader(nombre)
            else: st.subheader(nombre)
    st.write("")

def renderizar_bloque_marca_demo(nombre_marca, logo_key, campanas, ocultar_fb=False):
    # Header: Logo + Título
    col_l, col_t = st.columns([0.07, 0.93])
    with col_l:
        ruta_logo = logos.get(logo_key)
        if ruta_logo and os.path.exists(ruta_logo):
            st.image(ruta_logo, width=65)
    with col_t:
        st.markdown(f"## {nombre_marca}")

    df = generar_datos_ficticios(campanas, solo_google=ocultar_fb)
    
    # KPIs
    inv_t = df["Inversión Total"].sum()
    vnt_t = df["Total Ventas"].sum()
    cpv_a = inv_t / vnt_t if vnt_t > 0 else 0

    k1, k2, k3 = st.columns(3)
    k1.metric("Inversión Total", fmt_moneda(inv_t), delta="Proy: +15%")
    k2.metric("Ventas Total", f"{int(vnt_t)}", delta="Proy: +8%")
    k3.metric("CPV Acumulado", fmt_moneda(cpv_a))
    
    # Tabla Detalle
    st.write("📋 **Detalle de Campañas**")
    st.dataframe(df.style.background_gradient(cmap='RdYlGn_r', subset=['CPV Acumulado']).format({
        'Inversión Google': '${:,.2f}', 'Inversión Facebook': '${:,.2f}', 
        'Inversión Total': '${:,.2f}', 'Total Ventas': '{:,.0f}', 'CPV Acumulado': '${:,.2f}'
    }, decimal=',', thousands='.'), use_container_width=True, hide_index=True)

    # Bloque de 3 Gráficos (1 arriba, 2 abajo)
    st.write("📊 **Rendimiento Visual**")
    
    # Gráfico 1: Inversión (Ancho total)
    y_graf = ['Inversión Google'] if ocultar_fb else ['Inversión Google', 'Inversión Facebook']
    fig_inv = px.bar(df, x='Campaña', y=y_graf, title="Distribución de Inversión", 
                     barmode='stack', template="plotly_dark", height=350)
    fig_inv.update_layout(separators=',.', legend=dict(orientation="h", y=1.1, x=1, xanchor="right"))
    st.plotly_chart(fig_inv, use_container_width=True)

    # Gráficos 2 y 3: Ventas y CPV (Lado a lado)
    g1, g2 = st.columns(2)
    with g1:
        fig_v = px.bar(df, x='Campaña', y='Total Ventas', title="Ventas por Campaña", text='Total Ventas', template="plotly_dark")
        fig_v.update_traces(textposition='outside', textfont=FONT_LABEL)
        st.plotly_chart(fig_v, use_container_width=True)
    with g2:
        fig_c = px.bar(df, x='Campaña', y='CPV Acumulado', title="CPV por Campaña", text='CPV Acumulado', template="plotly_dark", color_discrete_sequence=['#d62728'])
        fig_c.update_traces(texttemplate='$%{text:,.2f}', textposition='outside', textfont=FONT_LABEL)
        st.plotly_chart(fig_c, use_container_width=True)
    
    st.markdown("<hr style='border: 1px solid #444; margin: 30px 0;'>", unsafe_allow_html=True)

# --- 5. RENDERIZADO ---
mostrar_encabezado_principal()

tab1, tab2 = st.tabs(["📊 Consolidado General", "🎯 Detalle por Cuenta"])

with tab1:
    # Secciones con datos aleatorios
    renderizar_bloque_marca_demo("Directv", "DirectTV", ["AR_Search", "AR_PMax", "UY_Search", "CL_Generic"])
    renderizar_bloque_marca_demo("Prosegur", "Prosegur", ["Alarmas_Residencial", "Alarmas_Pyme"], ocultar_fb=True)
    renderizar_bloque_marca_demo("Claro", "Claro", ["Portabilidad_UY", "Fibra_UY"], ocultar_fb=True)

with tab2:
    st.title("🎯 Detalle Específico")
    st.info("Seleccione una cuenta en la barra lateral para simular el análisis.")
    
    # Sidebar para la pestaña 2
    cuenta_sel = st.sidebar.selectbox("Cuenta Demo", ["Google_Directv_Ar", "Facebook_Directv_Ar", "Google_Prosegur_Arg"])
    
    st.subheader(f"Análisis para: {cuenta_sel}")
    
    # Simulación simple de tabla diaria
    dias = pd.date_range(start='2024-01-01', periods=10).strftime('%d/%m/%Y')
    df_mini = pd.DataFrame({
        'Fecha': dias,
        'Gasto': np.random.uniform(5000, 15000, 10),
        'Ventas': np.random.randint(1, 10, 10)
    })
    st.table(df_mini) # Una tabla simple para la pestaña 2
