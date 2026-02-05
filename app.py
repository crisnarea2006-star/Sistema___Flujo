import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# ---------------- 1. CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Hospital Integral Pro", layout="wide", page_icon="🏥")

# ---------------- 2. LÓGICA DE LA PORTADA (SESSION STATE) ----------------
if 'ingreso_confirmado' not in st.session_state:
    st.session_state['ingreso_confirmado'] = False

def entrar():
    st.session_state['ingreso_confirmado'] = True

# ---------------- 3. PANTALLA DE BIENVENIDA (SI NO HA ENTRADO) ----------------
if not st.session_state['ingreso_confirmado']:
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
        .subtitle {
            font-size: 24px;
            font-weight: 300;
            margin-bottom: 40px;
            color: #dcdcdc;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

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

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.button("🚀 QUIERO ACCEDER AL SISTEMA", on_click=entrar, use_container_width=True, type="primary")

# ---------------- 4. APLICACIÓN PRINCIPAL (SI YA ENTRÓ) ----------------
else:
    st.markdown("""
        <style>
        .stApp { background: white; }
        </style>
    """, unsafe_allow_html=True)

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

    # ================= TAB 1: FLUJO =================
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
            
            # Cálculo
            f_num = sp.lambdify(t, funcion, "numpy")
            res_exacto = float(sp.integrate(funcion, (t, 0, horas)).evalf())
            
            # Gráfica
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
            ax.plot(x, y, '#e74c3c', label="Tasa Real", linewidth=2)
            ax.fill_between(x, y, alpha=0.1, color='red')
            ax.bar(x_r, y_r, width=dx, align='edge', alpha=0.4, color='#3498db', edgecolor='blue', label="Riemann")
            ax.set_title("Ingresos vs Tiempo")
            ax.set_xlabel("Horas")
            ax.legend()
            st.pyplot(fig)

    # ================= TAB 2: LOGÍSTICA (GRÁFICA NUEVA) =================
    with tabs[1]:
        st.subheader("🚑 Optimización de Rutas")
        col_a, col_b = st.columns(2)
        with col_a:
            st.info("Función de la carretera:")
            st.latex(r"Trayectoria: f(t) = 0.5t^2")
            tiempo_viaje = st.number_input("Duración (h)", 1.0, 10.0, 3.0)
            
            # Cálculo
            f_ruta = 0.5 * t**2
            df = sp.diff(f_ruta, t)
            integrando = sp.sqrt(1 + df**2)
            distancia = sp.integrate(integrando, (t, 0, tiempo_viaje)).evalf()
            
            st.metric("Distancia Real Recorrida", f"{distancia:.2f} km")
            if st.button("💾 Guardar Ruta"):
                guardar_registro("Ruta Ambulancia", f"{distancia:.2f} km")
                
        with col_b:
            # --- NUEVA GRÁFICA DE LA CARRETERA ---
            st.write("**Visualización de la Ruta:**")
            t_vals = np.linspace(0, tiempo_viaje, 100)
            y_vals = 0.5 * t_vals**2  # La función de la parábola
            
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.plot(t_vals, y_vals, color='#8e44ad', linewidth=3, label="Carretera")
            ax2.fill_between(t_vals, y_vals, alpha=0.1, color='purple')
            ax2.set_title("Trayectoria Curva de la Ambulancia")
            ax2.set_xlabel("Tiempo / Distancia Eje X")
            ax2.set_ylabel("Desplazamiento")
            ax2.grid(True, linestyle='--', alpha=0.6)
            ax2.legend()
            st.pyplot(fig2)

    # ================= TAB 3: FARMACIA (GRÁFICA NUEVA) =================
    with tabs[2]:
        st.subheader("💊 Cinética de Medicamentos")
        col_f1, col_f2 = st.columns([1, 1])
        
        with col_f1:
            num = 3*t + 2
            den = (t+1)*(t+3)
            fraccion = num/den
            
            st.markdown("**Función de Concentración:**")
            st.latex(r"C(t) = " + sp.latex(fraccion))
            
            st.markdown("**Descomposición en Fracciones:**")
            parciales = sp.apart(fraccion)
            st.latex(r"C(t) = " + sp.latex(parciales))
            
            st.info("La integral resulta en Ln(|t+3|) y Ln(|t+1|).")
            if st.button("💾 Guardar Fármaco"):
                guardar_registro("Farmacia", "Descomposición Exitosa")

        with col_f2:
            # --- NUEVA GRÁFICA DE CONCENTRACIÓN ---
            st.write("**Curva de Absorción/Eliminación:**")
            
            # Creamos la función numérica para graficar
            t_med = np.linspace(0, 15, 100) # Graficamos 15 horas
            # Fórmula numpy: (3t + 2) / ((t+1)(t+3))
            c_med = (3*t_med + 2) / ((t_med + 1)*(t_med + 3))
            
            fig3, ax3 = plt.subplots(figsize=(6, 4))
            ax3.plot(t_med, c_med, color='#2ecc71', linewidth=3, label="Concentración en Sangre")
            ax3.fill_between(t_med, c_med, alpha=0.2, color='#2ecc71')
            ax3.set_title("Comportamiento del Fármaco")
            ax3.set_xlabel("Horas desde la ingesta")
            ax3.set_ylabel("Concentración (mg/L)")
            ax3.grid(True, linestyle='--', alpha=0.6)
            ax3.legend()
            st.pyplot(fig3)

    # ================= TAB 4: SUMINISTROS =================
    with tabs[3]:
        st.subheader("🛢️ Tanques de Oxígeno")
        col_x, col_y = st.columns([1, 1])
        with col_x:
            h_tanque = st.slider("Altura del Tanque (m)", 1, 10, 5)
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
            ax_v.plot(x_p, y_p, 'g', linewidth=2)
            ax_v.fill_between(x_p, y_p, alpha=0.2, color='green')
            ax_v.set_title("Perfil del Tanque (Sólido Revolución)")
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