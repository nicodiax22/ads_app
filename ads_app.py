import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard ADS - Demo Portafolio", layout="wide")

# --- 2. CONFIGURACIÓN DE RUTAS Y LOGOS ---
dir_actual = os.path.dirname(__file__)
PATH_LOGOS = os.path.join(dir_actual, "Logos")

logos = {
    "DirectTV": os.path.join(PATH_LOGOS, "1-DirectTV-logo.png"),
    "Prosegur": os.path.join(PATH_LOGOS, "2-Prosegur_new_company_logo.png"),
    "Claro": os.path.join(PATH_LOGOS, "3-Claro.svg.png"),
    "Facebook": os.path.join(PATH_LOGOS, "4-facebook-ads-logo.png"),
    "Google": os.path.join(PATH_LOGOS, "5-Google_Ads_logo.svg.png"),
    "Gout": os.path.join(PATH_LOGOS, "6-Logo_Header.png")
}

def mostrar_encabezado_principal():
    st.write("")
    c1, c2, c3 = st.columns(3)
    principales = [("Facebook", c1), ("Google", c2), ("Gout", c3)]
    for nombre, col in principales:
        with col:
            ruta = logos.get(nombre)
            if ruta and os.path.exists(ruta):
                try: st.image(ruta, width=180)
                except: st.write(f"**{nombre}**")
    st.write("")

mostrar_encabezado_principal()

# --- 3. FUNCIONES DE APOYO ---
def fmt_moneda(valor):
    return f"${valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

FONT_CONFIG = dict(size=12, family="Arial")

# --- 4. GENERADOR DE DATOS DEMO (Nombres idénticos al original) ---
@st.cache_data
def generar_datos_demo():
    # Nombres de campañas exactos
    campanas_dict = {
        "Directv": ["Camp_Directv_AR", "Camp_Directv_UY", "Camp_Directv_CO", "Camp_Directv_CL", "Camp_Directv_PE"],
        "Prosegur": ["Camp_Prosegur_AR", "Camp_Prosegur_UY", "Camp_Prosegur_CO"],
        "Claro": ["Camp_Claro_UY"]
    }
    
    dict_tablas = {}
    for marca, lista in campanas_dict.items():
        inv_g = np.random.uniform(2000, 5000, len(lista))
        inv_f = np.random.uniform(1000, 3000, len(lista))
        ventas = np.random.randint(15, 80, len(lista))
        
        df = pd.DataFrame({
            'Campaña': lista,
            'Inversión Google': inv_g,
            'Inversión Facebook': inv_f,
            'Inversión Total': inv_g + inv_f,
            'Total Ventas': ventas,
            'CPV Acumulado': (inv_g + inv_f) / ventas
        })
        dict_tablas[marca] = df
    return dict_tablas

DATOS_DEMO = generar_datos_demo()

# --- 5. LÓGICA DE RENDERIZADO POR BLOQUE ---
def renderizar_bloque_marca(df, nombre_marca, logo_key, ocultar_fb=False):
    col_t1, col_t2 = st.columns([0.07, 0.93])
    with col_t1:
        ruta_logo = logos.get(logo_key)
        if ruta_logo and os.path.exists(ruta_logo):
            st.image(ruta_logo, width=60)
    with col_t2: st.markdown(f"# {nombre_marca}")
    
    inv_a = df['Inversión Total'].sum()
    vnt_a = df['Total Ventas'].sum()
    cpv_a = inv_a / vnt_a

    k1, k2, k3 = st.columns(3)
    k1.metric("Inversión Total", fmt_moneda(inv_a), delta=f"Proy: {fmt_moneda(inv_a * 1.15)}")
    k2.metric("Ventas Total", f"{int(vnt_a)}", delta=f"Proy: {int(vnt_a * 1.15)}")
    k3.metric("CPV Acumulado", fmt_moneda(cpv_a))
    
    c_izq, c_der = st.columns([1.3, 0.7])
    with c_izq:
        st.write("📋 Detalle de Campañas")
        st.dataframe(df.style.background_gradient(cmap='RdYlGn_r', subset=['CPV Acumulado', 'Inversión Total']).format({
            'Inversión Google': '${:,.2f}', 'Inversión Facebook': '${:,.2f}', 
            'Inversión Total': '${:,.2f}', 'Total Ventas': '{:,.0f}', 'CPV Acumulado': '${:,.2f}'
        }, decimal=',', thousands='.'), use_container_width=True, hide_index=True)

    with c_der:
        # Gráfico de Inversión Stacked corregido
        y_graf = ['Inversión Google'] if ocultar_fb else ['Inversión Google', 'Inversión Facebook']
        fig_i = px.bar(df, x='Campaña', y=y_graf, title="Inversión", barmode='stack', template="plotly_dark")
        
        # Etiqueta de Inversión Total arriba de la barra
        fig_i.add_scatter(x=df['Campaña'], y=df['Inversión Total'], 
                          text=df['Inversión Total'].apply(lambda x: f"${x:,.2f}"),
                          mode='text', textposition='top center', showlegend=False, cliponaxis=False,
                          textfont=FONT_CONFIG)
        
        fig_i.update_layout(height=450, margin=dict(l=0, r=0, t=60, b=0), 
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=''),
                            yaxis=dict(range=[0, df['Inversión Total'].max() * 1.4]))
        st.plotly_chart(fig_i, use_container_width=True)

    cv, cp = st.columns(2)
    with cv:
        fig_v = px.bar(df, x='Campaña', y='Total Ventas', title="Ventas", text='Total Ventas', template="plotly_dark")
        fig_v.update_traces(textposition='outside', texttemplate='%{text:d}', textfont=FONT_CONFIG)
        fig_v.update_layout(height=400, yaxis=dict(range=[0, df['Total Ventas'].max() * 1.3]))
        st.plotly_chart(fig_v, use_container_width=True)
    with cp:
        fig_c = px.bar(df, x='Campaña', y='CPV Acumulado', title="CPV", text='CPV Acumulado', template="plotly_dark", color_discrete_sequence=['#d62728'])
        fig_c.update_traces(texttemplate='$%{text:,.2f}', textposition='outside', textfont=FONT_CONFIG)
        fig_c.update_layout(height=400, yaxis=dict(range=[0, df['CPV Acumulado'].max() * 1.3]))
        st.plotly_chart(fig_c, use_container_width=True)
    
    st.markdown("<hr style='border: 1.5px solid #555; margin-top: 25px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# --- 6. TABS ---
tab1, tab2 = st.tabs(["📊 Consolidado General", "🎯 Detalle por Cuenta"])

with tab1:
    renderizar_bloque_marca(DATOS_DEMO["Directv"], "Directv", "DirectTV")
    renderizar_bloque_marca(DATOS_DEMO["Prosegur"], "Prosegur", "Prosegur") # Aquí forzamos que muestre ambas si existen datos
    renderizar_bloque_marca(DATOS_DEMO["Claro"], "Claro", "Claro")

with tab2:
    st.sidebar.title("Configuración Demo")
    cuenta_demo = st.sidebar.selectbox("Seleccione Cuenta", ["Camp_Directv_AR", "Camp_Prosegur_AR", "Camp_Claro_UY"])
    
    st.title(f"🎯 Rendimiento: {cuenta_demo}")
    
    # Generar datos diarios aleatorios simulando la pestaña 2 real
    fechas = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(15, 0, -1)]
    df_det = pd.DataFrame({
        'Día': fechas,
        'Coste': np.random.uniform(500, 1500, 15),
        'Total Leeds': np.random.randint(100, 500, 15),
        'Total Ventas': np.random.randint(5, 30, 15)
    })
    df_det['Conv %'] = (df_det['Total Ventas'] / df_det['Total Leeds']) * 100
    df_det['CPV'] = df_det['Coste'] / df_det['Total Ventas']

    st.dataframe(
        df_det.style.background_gradient(cmap='RdYlGn_r', subset=['Coste', 'Conv %', 'CPV'])
                     .format({'Coste': '${:,.2f}', 'Total Ventas': '{:,.0f}', 'Total Leeds': '{:,.0f}', 'Conv %': '{:.2f}%', 'CPV': '${:,.2f}'}, decimal=',', thousands='.'),
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    st.subheader("📊 Gráficos Diarios")
    
    # Gráfico 1: CPV Diario (Rojo)
    fig_d1 = px.bar(df_det, x='Día', y='CPV', title="CPV Diario", text='CPV', template="plotly_dark", color_discrete_sequence=['#d62728'])
    fig_d1.update_traces(texttemplate='$%{text:,.2f}', textposition='outside', textfont=FONT_CONFIG)
    fig_d1.update_xaxes(type='category')
    fig_d1.update_layout(yaxis=dict(range=[0, df_det['CPV'].max() * 1.3]))
    st.plotly_chart(fig_d1, use_container_width=True)

    # Gráfico 2: Costo Diario (Azul/Default)
    fig_costo = px.bar(df_det, x='Día', y='Coste', title="Costo Diario", text='Coste', template="plotly_dark")
    fig_costo.update_traces(texttemplate='$%{text:,.2f}', textposition='outside', textfont=FONT_CONFIG)
    fig_costo.update_xaxes(type='category')
    fig_costo.update_layout(yaxis=dict(range=[0, df_det['Coste'].max() * 1.3]))
    st.plotly_chart(fig_costo, use_container_width=True)

    # Gráfico 3: Conversión % (Línea)
    fig_conv = px.line(df_det, x='Día', y='Conv %', title="Conversión %", markers=True, text='Conv %', template="plotly_dark")
    fig_conv.update_traces(texttemplate='%{text:.2f}%', textposition='top center', textfont=FONT_CONFIG)
    fig_conv.update_xaxes(type='category')
    fig_conv.update_layout(yaxis=dict(range=[df_det['Conv %'].min() * 0.8, df_det['Conv %'].max() * 1.3]))
    st.plotly_chart(fig_conv, use_container_width=True)