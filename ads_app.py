import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard ADS - Demo Portafolio", layout="wide")

# --- 2. CONFIGURACIÓN DE ASSETS (Rutas del Original) ---
dir_actual = os.path.dirname(__file__)
# Usamos 'assets' para mantener la estructura de tu carpeta de producción
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

# --- 3. FUNCIONES DE APOYO Y SIMULACIÓN ---
def fmt_moneda(valor):
    """Formato de moneda estilo contable Argentina"""
    return f"${valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def generar_datos_ficticios(lista_campanas, solo_google=False):
    """Genera un DataFrame con datos aleatorios para la demo"""
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

# --- 4. COMPONENTES DE INTERFAZ ---
def mostrar_encabezado_principal():
    st.write("")
    c1, c2, c3 = st.columns(3)
    principales = [("Facebook", c1), ("Google", c2), ("Gout", c3)]
    for nombre, col in principales:
        with col:
            ruta = logos.get(nombre)
            if ruta and os.path.exists(ruta):
                st.image(ruta, width=180)
            else:
                st.subheader(nombre)
    st.write("")

def renderizar_bloque_marca_demo(nombre_marca, logo_key, campanas, ocultar_fb=False):
    """Renderiza la estructura completa: Logo/Título -> KPIs -> Tabla -> Gráficos"""
    
    # Header de Sección
    col_l, col_t = st.columns([0.07, 0.93])
    with col_l:
        ruta_logo = logos.get(logo_key)
        if ruta_logo and os.path.exists(ruta_logo):
            st.image(ruta_logo, width=65)
    with col_t:
        st.markdown(f"## {nombre_marca}")

    # Datos Aleatorios
    df = generar_datos_ficticios(campanas, solo_google=ocultar_fb)
    
    # Métricas (KPIs)
    inv_t = df["Inversión Total"].sum()
    vnt_t = df["Total Ventas"].sum()
    cpv_a = inv_t / vnt_t if vnt_t > 0 else 0

    k1, k2, k3 = st.columns(3)
    k1.metric("Inversión Total", fmt_moneda(inv_t), delta=f"Proy: {fmt_moneda(inv_t * 1.15)}")
    k2.metric("Ventas Total", f"{int(vnt_t)}", delta=f"Proy: {int(vnt_t * 1.15)}")
    k3.metric("CPV Acumulado", fmt_moneda(cpv_a))
    
    # Tabla de Detalle (Estilo Producción)
    st.write("📋 **Detalle de Campañas**")
    st.dataframe(df.style.background_gradient(cmap='RdYlGn_r', subset=['CPV Acumulado', 'Inversión Total']).format({
        'Inversión Google': '${:,.2f}', 'Inversión Facebook': '${:,.2f}', 
        'Inversión Total': '${:,.2f}', 'Total Ventas': '{:,.0f}', 'CPV Acumulado': '${:,.2f}'
    }, decimal=',', thousands='.'), use_container_width=True, hide_index=True)

    # Gráficos (Estructura: 1 Arriba, 2 Abajo)
    st.write("📊 **Rendimiento Visual**")
    
    # 1. Gráfico de Inversión (Ancho total)
    y_graf = ['Inversión Google'] if ocultar_fb else ['Inversión Google', 'Inversión Facebook']
    fig_inv = px.bar(df, x='Campaña', y=y_graf, title="Distribución de Inversión", 
                     barmode='stack', template="plotly_dark", height=400)
    fig_inv.update_layout(separators=',.', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_inv, use_container_width=True)

    # 2. Fila inferior de gráficos
    g1, g2 = st.columns(2)
    with g1:
        fig_v = px.bar(df, x='Campaña', y='Total Ventas', title="Ventas por Campaña", text='Total Ventas', template="plotly_dark")
        fig_v.update_traces(textposition='outside', textfont=FONT_LABEL)
        st.plotly_chart(fig_v, use_container_width=True)

    with g2:
        fig_c = px.bar(df, x='Campaña', y='CPV Acumulado', title="CPV por Campaña", text='CPV Acumulado', template="plotly_dark", color_discrete_sequence=['#d62728'])
        fig_c.update_traces(texttemplate='$%{text:,.2f}', textposition='outside', textfont=FONT_LABEL)
        st.plotly_chart(fig_c, use_container_width=True)
    
    st.markdown("<hr style='border: 1.2px solid #555; margin: 25px 0;'>", unsafe_allow_html=True)

# --- 5. EJECUCIÓN PRINCIPAL ---
mostrar_encabezado_principal()

tab1, tab2 = st.tabs(["📊 Consolidado General", "🎯 Detalle por Cuenta"])

with tab1:
    # Simulación de las secciones del original
    renderizar_bloque_marca_demo(
        "Directv", "DirectTV", 
        ["AR_Search_Broad", "AR_Performance_Max", "UY_Search_Brand", "CL_Generic_Video", "CO_Display_Remessaging"]
    )
    
    renderizar_bloque_marca_demo(
        "Prosegur", "Prosegur", 
        ["AR_Alarmas_Pyme", "AR_Alarmas_Residencial", "UY_Alarmas_Smart"], 
        ocultar_fb=True
    )
    
    renderizar_bloque_marca_demo(
        "Claro", "Claro", 
        ["UY_Portabilidad_Google", "UY_Fibra_Optica_Google"], 
        ocultar_fb=True
    )

with tab2:
    st.sidebar.title("Configuración Demo")
    cuenta_mock = st.sidebar.selectbox("Seleccione Cuenta (Simulación)", [
        "Google_Directv_Ar", "Facebook_Directv_Ar", "Google_Prosegur_Arg", "Google_Claro_Uru"
    ])
    
    st.title(f"🎯 Rendimiento: {cuenta_mock}")
    
    # Simulación de datos diarios (30 días)
    dias = [f"Día {i}" for i in range(1, 31)]
    df_diario = pd.DataFrame({
        'Día': dias,
        'Coste': np.random.uniform(5000, 15000, 30),
        'Total Ventas': np.random.randint(1, 10, 30),
        'Total Leeds': np.random.randint(10, 50, 30)
    })
    df_diario['CPV'] = df_diario['Coste'] / df_diario['Total Ventas']
    
    st.subheader("📅 Detalle Diario Simulado")
    st.dataframe(df_diario.style.format({
        'Coste': '${:,.2f}', 'CPV': '${:,.2f}'
    }, decimal=',', thousands='.'), use_container_width=True, hide_index=True)
    
    fig_diario = px.line(df_diario, x='Día', y='Coste', title="Evolución de Gasto Diario", markers=True, template="plotly_dark")
    st.plotly_chart(fig_diario, use_container_width=True)
