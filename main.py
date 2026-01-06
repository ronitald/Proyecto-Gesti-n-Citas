# DESCRIPCIÓN DEL PROYECYO:
# Este es un proyecto final desarrollado por Ronald Puerto. 
# Se trata de una aplicación web sencilla para la gestión de citas médicas en el Hospital San José. 
# Está construida en Python usando Streamlit, por lo que se ejecuta con el comando:
# ** py -m streamlit run main.py **

import streamlit as st
import pandas as pd
from datetime import datetime, time

# Configuración inicial de la página en Streamlit
st.set_page_config(page_title="Gestión de Citas - Demo", page_icon="🏥", layout="wide")

# Título principal del sistema
st.title("🏥 Demo de Gestión de Citas Médicas - Ronald Puerto")
st.caption("Gestión de citas en el Hospital San José")

# =========================
#  INICIALIZACIÓN DE DATOS
# =========================

# Validamos si ya existe una "base de datos" en memoria.
# Si no existe, creamos una estructura tipo DataFrame vacía.
if "citas" not in st.session_state:
    st.session_state.citas = pd.DataFrame(
        columns=[
            "id",
            "paciente",
            "documento",
            "especialidad",
            "medico",
            "fecha",
            "hora",
            "estado",
        ]
    )

# Contador para asignar ID único a cada cita
if "contador_id" not in st.session_state:
    st.session_state.contador_id = 1

# Listas de apoyo para especialidades, médicos y estados disponibles
ESPECIALIDADES = ["Medicina General", "Pediatría", "Cardiología", "Ginecología"]

MEDICOS = {
    "Medicina General": ["Dr. Ronald Puerto", "Dra. Sandra Fuentes"],
    "Pediatría": ["Dra. Catalina Mora"],
    "Cardiología": ["Dr. Sebastian Puerto"],
    "Ginecología": ["Dra. Monica Martinez"],
}

ESTADOS = ["Programada", "Atendida", "Cancelada"]

# ============================
# SELECCIÓN DE ROL DE USUARIO
# ============================

st.sidebar.header("Rol de acceso")

# El usuario selecciona si entra como paciente o administrador
rol = st.sidebar.radio(
    "Seleccione el tipo de usuario",
    ["Paciente", "Administrador"],
)

st.sidebar.info(
    "Este es un DEMO Para el ACA 3. Los datos son simulados y se pierden al cerrar la sesión."
)

# =========================
# FUNCIONES PRINCIPALES
# =========================

def crear_cita(paciente, documento, especialidad, medico, fecha, hora):
    """
    Esta función crea una nueva cita médica,
    valida que el médico no tenga otra cita a la misma hora,
    y luego guarda la cita en memoria.
    """
    global_id = st.session_state.contador_id

    df = st.session_state.citas

    # Validamos si el médico ya tiene cita programada en ese mismo horario
    conflicto = df[
        (df["medico"] == medico)
        & (df["fecha"] == fecha.strftime("%Y-%m-%d"))
        & (df["hora"] == hora.strftime("%H:%M"))
        & (df["estado"] == "Programada")
    ]

    # Si ya hay una cita, mostramos error
    if not conflicto.empty:
        st.error(
            "El horario seleccionado ya está ocupado para este médico. "
            "Por favor elija otra hora o médico."
        )
        return

    # Construimos el registro de la nueva cita
    nueva_fila = {
        "id": global_id,
        "paciente": paciente,
        "documento": str(documento),
        "especialidad": especialidad,
        "medico": medico,
        "fecha": fecha.strftime("%Y-%m-%d"),
        "hora": hora.strftime("%H:%M"),
        "estado": "Programada",
    }

    # Guardamos la nueva cita en el DataFrame
    st.session_state.citas = pd.concat(
        [st.session_state.citas, pd.DataFrame([nueva_fila])],
        ignore_index=True,
    )

    # Incrementamos el contador de turnos
    st.session_state.contador_id += 1

    st.success(f"Cita creada correctamente. Número de turno: {global_id}")


def actualizar_estado(id_cita, nuevo_estado):
    """
    Esta función permite cambiar el estado de una cita:
    Programada / Atendida / Cancelada
    """
    df = st.session_state.citas
    st.session_state.citas.loc[df["id"] == id_cita, "estado"] = nuevo_estado


# =========================
# VISTA PARA PACIENTES
# =========================

if rol == "Paciente":
    st.subheader("👤 Módulo de Pacientes")

    # Creamos pestañas: Solicitar cita y Consultar citas
    tab_crear, tab_consultar = st.tabs(
        ["Solicitar nueva cita", "Consultar mis citas"]
    )

    # -------- TAB DE CREACIÓN DE CITA --------
    with tab_crear:
        with st.form("form_crear_cita"):
            nombre = st.text_input("Nombre completo del paciente*")
            documento = st.text_input("Documento de identificación*")
            especialidad = st.selectbox("Especialidad requerida*", ESPECIALIDADES)

            medico = st.selectbox(
                "Médico",
                MEDICOS.get(especialidad, []),
            )

            fecha = st.date_input("Fecha de la cita*", min_value=datetime.now().date())
            hora = st.time_input("Hora de la cita*", value=time(8, 0))

            enviado = st.form_submit_button("Confirmar solicitud de cita")

            # Validación simple de campos obligatorios
            if enviado:
                if not nombre or not documento:
                    st.error("Por favor complete todos los campos obligatorios.")
                else:
                    crear_cita(nombre, documento, especialidad, medico, fecha, hora)

    # -------- TAB DE CONSULTA DE CITAS --------
    with tab_consultar:
        documento_busqueda = st.text_input(
            "Ingrese su documento para consultar sus citas"
        )

        if st.button("Buscar citas"):
            df = st.session_state.citas
            resultados = df[df["documento"] == documento_busqueda]

            # Si no hay citas, se informa al usuario
            if resultados.empty:
                st.warning("No se encontraron citas asociadas a ese documento.")
            else:
                st.write("Estas son sus citas registradas:")
                st.dataframe(resultados.sort_values(by=["fecha", "hora"]))


# =========================
# VISTA PARA ADMINISTRADOR
# =========================

elif rol == "Administrador":
    st.subheader("👨‍⚕️ Módulo Administrativo")

    tab_agenda, tab_resumen = st.tabs(
        ["Agenda de citas", "Indicadores Basicos"]
    )

    # -------- TAB DE AGENDA --------
    with tab_agenda:
        st.markdown("### Gestión de citas programadas")

        df = st.session_state.citas

        # Validamos si hay citas registradas
        if df.empty:
            st.info("Aún no hay citas registradas.")
        else:
            # Filtro por fecha
            fecha_filtro = st.date_input(
                "Filtrar por fecha",
                value=datetime.now().date(),
            )

            fecha_str = fecha_filtro.strftime("%Y-%m-%d")
            df_filtrado = df[df["fecha"] == fecha_str]

            if df_filtrado.empty:
                st.warning("No hay citas para la fecha seleccionada.")
            else:
                st.write("Citas para la fecha seleccionada:")
                st.dataframe(df_filtrado.sort_values(by=["hora"]))

                # Seleccionar cita a actualizar
                ids_disponibles = df_filtrado["id"].tolist()

                id_seleccionado = st.selectbox(
                    "Seleccione el ID de la cita para actualizar",
                    ids_disponibles,
                )

                nuevo_estado = st.selectbox(
                    "Nuevo estado",
                    ESTADOS,
                )

                if st.button("Actualizar estado de la cita"):
                    actualizar_estado(id_seleccionado, nuevo_estado)
                    st.success("Estado actualizado correctamente.")

    # -------- TAB DE INDICADORES --------
    with tab_resumen:
        st.markdown("### Indicadores de operación (simulados)")

        df = st.session_state.citas

        # Validación de existencia de datos
        if df.empty:
            st.info("No hay datos suficientes para calcular indicadores.")
        else:
            total_citas = len(df)
            citas_programadas = len(df[df["estado"] == "Programada"])
            citas_atendidas = len(df[df["estado"] == "Atendida"])
            citas_canceladas = len(df[df["estado"] == "Cancelada"])

            # Métricas en columnas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de citas", total_citas)
            col2.metric("Programadas", citas_programadas)
            col3.metric("Atendidas", citas_atendidas)
            col4.metric("Canceladas", citas_canceladas)

            # Cálculo simple de tiempo de espera
            minutos_espera = citas_programadas * 15
            horas = minutos_espera // 60
            minutos = minutos_espera % 60

            st.write(
                f"⏱️ Tiempo de espera estimado actual (simulado): "
                f"**{horas} h {minutos} min** para los pacientes en cola."
            )

            # Conteo de citas por especialidad
            citas_por_especialidad = (
                df.groupby("especialidad")["id"].count().reset_index(name="cantidad")
            )

            st.write("Distribución de citas por especialidad:")
            st.dataframe(citas_por_especialidad)
