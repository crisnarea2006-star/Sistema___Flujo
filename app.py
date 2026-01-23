import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# ---------------- 1. CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Hospital Integral Pro", layout="wide")

# ---------------- 2. GESTIÓN DE BASE DE DATOS ----------------
def init_db():
    """Inicializa la base de datos si no existe"""
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

# Conexión persistente
conn = init_db()
cursor = conn.cursor()

def guardar_registro(tipo, resultado):
    """Guarda un resultado en la BD"""
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO simulaciones (tipo_calculo, resultado, fecha) VALUES (?, ?, ?)", 
                   (tipo, resultado, fecha_actual))
    conn.commit()
    st.sidebar.success("✅ ¡Guardado en Historial!")

# ---------------- 3. INTERFAZ PRINCIPAL ----------------
st.title("🏥 Sistema de Cálculo Integral Hospitalario")
st.markdown("Plataforma de simulación médica basada en cálculo diferencial e integral.")

# Variable simbólica global
t = sp.symbols('t')

# Pestañas del sistema
tabs = st.tabs([
    "📈 Flujo (Ingresos)", 
    "🚑 Logística (Arco)", 
    "💊 Farmacia (Fracciones)", 
    "🛢️ Suministros (Volumen)"
])

# ================= TAB 1: FLUJO (INTEGRAL + BD) =================
with tabs[0]:
    st.header("Análisis de Ingresos a Urgencias")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Configuración")
        intensidad = st.slider("Intensidad (Pacientes/h)", 1, 50, 15)
        horas = st.slider("Duración del Turno (h)", 1, 24, 8)
        n_rects = st.slider("Precisión (Riemann)", 5, 50, 20)
        
        # Botón para guardar en BD
        if st.button("💾 Guardar Simulación de Flujo"):
            # Calculamos rápido para guardar
            k = 5.0
            f_sym = intensidad * t * sp.exp(-t/k)
            res = sp.integrate(f_sym, (t, 0, horas)).evalf()
            guardar_registro("Flujo Pacientes", f"{res:.2f} pacientes en {horas}h")

    with col2:
        k = 5.0
        funcion = intensidad * t * sp.exp(-t/k)
        
        st.latex(r"f(t) = " + sp.latex(funcion))
        
        # Cálculo Simbólico
        integral_exacta = sp.integrate(funcion, (t, 0, horas))
        res_exacto = float(integral_exacta.evalf())
        
        # Gráfica y Riemann
        f_num = sp.lambdify(t, funcion, "numpy")
        x = np.linspace(0, horas, 200)
        y = f_num(x)
        
        dx = horas / n_rects
        x_r = np.linspace(0, horas - dx, n_rects)
        y_r = f_num(x_r)
        area_riemann = np.sum(y_r * dx)
        
        # Métricas
        c_a, c_b = st.columns(2)
        c_a.metric("Total Pacientes (Integral)", f"{res_exacto:.2f}")
        c_b.metric("Aprox. Riemann", f"{area_riemann:.2f}")
        
        # Plot
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(x, y, 'r', label="Curva Real")
        ax.bar(x_r, y_r, width=dx, align='edge', alpha=0.3, color='blue', label="Riemann")
        ax.legend()
        st.pyplot(fig)

# ================= TAB 2: LOGÍSTICA (ARCO) =================
with tabs[1]:
    st.header("Ruta de Ambulancia")
    st.write("Cálculo de distancia real en ruta curva (Longitud de Arco).")
    
    f_ruta = 0.4 * t**2
    df = sp.diff(f_ruta, t)
    integrando = sp.sqrt(1 + df**2)
    
    tiempo_viaje = st.number_input("Tiempo de viaje (h)", 1.0, 5.0, 3.0)
    distancia = sp.integrate(integrando, (t, 0, tiempo_viaje)).evalf()
    
    st.latex(r"y = 0.4t^2 \quad \rightarrow \quad L = \int_0^T \sqrt{1 + (0.8t)^2} dt")
    st.success(f"Distancia recorrida: {distancia:.2f} km")
    
    if st.button("💾 Guardar Ruta"):
        guardar_registro("Ruta Ambulancia", f"{distancia:.2f} km")

# ================= TAB 3: FARMACIA (FRACCIONES) =================
with tabs[2]:
    st.header("Cinética de Medicamentos")
    num = 3*t + 2
    den = (t+1)*(t+3)
    fraccion = num/den
    
    st.latex(r"C(t) = " + sp.latex(fraccion))
    st.write("Descomposición en **Fracciones Parciales**:")
    parciales = sp.apart(fraccion)
    st.latex(sp.latex(parciales))
    
    st.info("La integral de esto resulta en Logaritmos Naturales (ln).")

# ================= TAB 4: SUMINISTROS (VOLUMEN) =================
with tabs[3]:
    st.header("Volumen de Tanque (Sólidos de Rev.)")
    radio = sp.sqrt(t + 2)
    st.latex(r"Radio = \sqrt{t+2}")
    
    h_tanque = st.slider("Altura Tanque (m)", 1, 10, 4)
    volumen = sp.pi * sp.integrate(radio**2, (t, 0, h_tanque)).evalf()
    
    st.metric("Volumen Total", f"{volumen:.2f} m³")
    
    if st.button("💾 Guardar Volumen"):
        guardar_registro("Volumen Tanque", f"{volumen:.2f} m3")

# ---------------- 4. SIDEBAR - HISTORIAL ----------------
with st.sidebar:
    st.header("🗂️ Base de Datos")
    st.write("Registro histórico de cálculos realizados.")
    
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()

    cursor.execute("SELECT * FROM simulaciones ORDER BY id DESC")
    datos = cursor.fetchall()
    
    if datos:
        st.dataframe(
            datos, 
            column_config={
                0: "ID",
                1: "Tipo",
                2: "Resultado",
                3: "Fecha"
            },
            hide_index=True
        )
        
        if st.button("🗑️ Borrar Historial"):
            cursor.execute("DELETE FROM simulaciones")
            conn.commit()
            st.warning("Historial borrado.")
            st.rerun()
    else:
        st.info("No hay registros aún.")

# Cerrar conexión al apagar (buena práctica, aunque Streamlit lo maneja)
# conn.close()