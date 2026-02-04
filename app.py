import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# ---------------- 1. CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Hospital Integral Pro", layout="wide", page_icon="🏥")

# ---------------- 2. LÓGICA DE LA PORTADA (SESSION STATE) ----------------
# Inicializamos la variable para saber si ya entró o no
if 'ingreso_confirmado' not in st.session_state:
    st.session_state['ingreso_confirmado'] = False

def entrar():
    st.session_state['ingreso_confirmado'] = True

# ---------------- 3. PANTALLA DE BIENVENIDA (SI NO HA ENTRADO) ----------------
if not st.session_state['ingreso_confirmado']:
    
    # CSS para centrar todo, fondo elegante y estilo del botón
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            background-attachment: fixed;
            background-size: cover;
        }
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh;
            text-align: center;
            color: white;
            padding: 20px;
        }
        .title {
            font-size: 60px;
            font-weight: 800;
            margin-bottom: 10px;
            text-shadow: 0 4px 10px rgba(0,0,0,0.5);
            background: -webkit-linear-gradient(#eee, #333);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            color: white; /* Fallback */
        }
        .subtitle {
            font-size: 24px;
            font-weight: 300;
            margin-bottom: 40px;
            color: #dcdcdc;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        /* Ocultar elementos predeterminados de Streamlit en la portada */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Contenedor visual
    st.markdown("""
    <div class="main-container">
        <div style="font-size: 80px;">🏥</div>
        <h1 style="font-size: 50px; color: white; text-shadow: 2px 2px 4px #000000;">SISTEMA HOSPITALARIO INTEGRAL</h1>
        <p class="subtitle">
            Simulación avanzada aplicada a la Gestión de Salud.<br>
            Cálculo de Flujos, Logística, Farmacia y Suministros.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Botón centrado usando columnas
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # El botón nativo de Streamlit
        st.button("🚀 QUIERO ACCEDER AL SISTEMA", on_click=entrar, use_container_width=True, type="primary")


# ---------------- 4. APLICACIÓN PRINCIPAL (SI YA ENTRÓ) ----------------
else:
    # --- AQUÍ EMPIEZA TU CÓDIGO DEL SIMULADOR ---
    
    # CSS para regresar el fondo a blanco (limpio) dentro de la app
    st.markdown("""
        <style>
        .stApp {
            background: white; 
        }
        </style>
    """, unsafe_allow_html=True)

    # Banner superior dentro de la app
    st.markdown("""
    <div style="padding:15px; background:linear-gradient(90deg, #005C97, #363795); border-radius:10px; color:white; margin-bottom:20px; text-align:center;">
        <h2 style="margin:0; color:white;">🏥 DASHBOARD DE CONTROL</h2>
    </div>
    """, unsafe_allow_html=True)

    # --- BASE DE DATOS ---
    def init_db():
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_calculo TEXT,
                resultado TEXT,
                fecha TEXT
            )
        """)
        conn.commit()
        return conn

    conn = init_db()
    cursor = conn.cursor()

    def guardar_registro(tipo, resultado):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO simulaciones (tipo_calculo, resultado, fecha) VALUES (?, ?, ?)", 
                    (tipo, resultado, fecha))
        conn.commit()
        st.sidebar.success(f"✅ ¡{tipo} Guardado!")

    # --- SIMULADOR ---
    t = sp.symbols('t')

    tabs = st.tabs([
        "📈 Flujo (Ingresos)", 
        "🚑 Logística (Arco)", 
        "💊 Farmacia (Fracciones)", 
        "🛢️ Suministros (Volumen)"
    ])

    # TAB 1
    with tabs[0]:
        st.subheader("📊 Análisis de Saturación de Urgencias")
        col1, col2 = st.columns([1, 2])
        with col1:
            intensidad = st.slider("Intensidad de llegada", 1, 50, 15)
            horas = st.slider("Horas del turno", 1, 24, 8)
            n_rects = st.slider("Precisión (Riemann)", 5, 60, 20)
            if st.button("💾 Guardar Análisis Flujo"):
                k = 5.0
                f_sym = intensidad * t * sp.exp(-t/k)
                res = sp.integrate(f_sym, (t, 0, horas)).evalf()
                guardar_registro("Flujo Pacientes", f"{res:.1f} pacientes")
        with col2:
            k = 5.0
            funcion = intensidad * t * sp.exp(-t/k)
            st.latex(r"f(t) = " + sp.latex(funcion))
            integral_exacta = sp.integrate(funcion, (t, 0, horas))
            res_exacto = float(integral_exacta.evalf())
            f_num = sp.lambdify(t, funcion, "numpy")
            x = np.linspace(0, horas, 200)
            y = f_num(x)
            dx = horas / n_rects
            x_r = np.linspace(0, horas - dx, n_rects)
            y_r = f_num(x_r)
            area_riemann = np.sum(y_r * dx)
            c_a, c_b = st.columns(2)
            c_a.metric("Total Exacto", f"{res_exacto:.2f}", delta="Pacientes")
            c_b.metric("Aprox. Riemann", f"{area_riemann:.2f}")
            fig, ax = plt.subplots(figsize=(8, 3.5))
            ax.plot(x, y, '#e74c3c', label="Tasa Real")
            ax.fill_between(x, y, alpha=0.1, color='red')
            ax.bar(x_r, y_r, width=dx, align='edge', alpha=0.4, color='#3498db', edgecolor='blue', label="Riemann")
            ax.legend()
            st.pyplot(fig)

    # TAB 2
    with tabs[1]:
        st.subheader("🚑 Optimización de Rutas")
        col_a, col_b = st.columns(2)
        with col_a:
            st.latex(r"Trayectoria: f(t) = 0.5t^2")
            tiempo_viaje = st.number_input("Duración (h)", 1.0, 10.0, 3.0)
            f_ruta = 0.5 * t**2
            df = sp.diff(f_ruta, t)
            integrando = sp.sqrt(1 + df**2)
            distancia = sp.integrate(integrando, (t, 0, tiempo_viaje)).evalf()
            st.metric("Distancia Real", f"{distancia:.2f} km")
            if st.button("💾 Guardar Ruta"):
                guardar_registro("Ruta Ambulancia", f"{distancia:.2f} km")
        with col_b:
            st.latex(r"L = \int_0^T \sqrt{1 + [f'(t)]^2} \, dt")

    # TAB 3
    with tabs[2]:
        st.subheader("💊 Cinética de Medicamentos")
        num = 3*t + 2
        den = (t+1)*(t+3)
        fraccion = num/den
        st.latex(r"C(t) = " + sp.latex(fraccion))
        st.write("Descomposición automática:")
        parciales = sp.apart(fraccion)
        st.latex(r"C(t) = " + sp.latex(parciales))
        st.info("La integral resulta en Logaritmos Naturales (ln).")
        if st.button("💾 Guardar Fármaco"):
            guardar_registro("Farmacia", "Descomposición Exitosa")

    # TAB 4
    with tabs[3]:
        st.subheader("🛢️ Tanques de Oxígeno")
        col_x, col_y = st.columns([1, 1])
        with col_x:
            h_tanque = st.slider("Altura (m)", 1, 10, 5)
            radio_fun = sp.sqrt(t + 1)
            st.latex(r"Radio(t) = \sqrt{t+1}")
            volumen = sp.pi * sp.integrate(radio_fun**2, (t, 0, h_tanque)).evalf()
            st.metric("Volumen Total", f"{volumen:.2f} m³")
            if st.button("💾 Guardar Volumen"):
                guardar_registro("Volumen Tanque", f"{volumen:.2f} m3")
        with col_y:
            x_p = np.linspace(0, h_tanque, 100)
            y_p = np.sqrt(x_p + 1)
            fig_v, ax_v = plt.subplots(figsize=(5,3))
            ax_v.plot(x_p, y_p, 'g')
            ax_v.fill_between(x_p, y_p, alpha=0.2, color='green')
            st.pyplot(fig_v)

    # SIDEBAR
    with st.sidebar:
        st.header("📂 Historial")
        if st.button("🔄 Actualizar"):
            st.rerun()
        if st.button("🏠 Cerrar Sesión"):
            st.session_state['ingreso_confirmado'] = False
            st.rerun()
            
        cursor.execute("SELECT tipo_calculo, resultado, fecha FROM simulaciones ORDER BY id DESC")
        datos = cursor.fetchall()
        if datos:
            st.dataframe(datos, hide_index=True)
            if st.button("🗑️ Borrar Todo"):
                cursor.execute("DELETE FROM simulaciones")
                conn.commit()
                st.rerun()
        else:
            st.info("Sin datos.")