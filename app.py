import streamlit as st
import pandas as pd
from io import BytesIO
import math

# Precios de materiales y peso por unidad (en kg) de cada perfil
precios_por_kg = {
    'blanco': 10557,
    'negro_color': 10732,
    'anodizado_natural': 11077
}

pesos_materiales = {
    'angulo_30_30': 1.5,
    'tubo_50_75': 6,
    'tubo_40_20': 2.9,
    'guia_techo_corredizo': 5.58
}

precio_poliacrilico_m2 = 47093

def calcular_materiales_costo(tipo_techo, ancho, largo, tratamiento, cubierta, costo_vidrio, costo_zingueria, otros_costos, cantidad_paños=None):
    resultado = []
    costo_total = 0
    area_techo = ancho * largo  # m2 de la cubierta

    # Calcular los tramos necesarios para el ancho
    cantidad_tramos_ancho = math.ceil(ancho / 0.65)+1

    # Determinar el número total de tubos de 50-75 según el largo del techo
    if largo <= 3:
        tubos_totales_50_75 = math.ceil(cantidad_tramos_ancho / 3)  # Un solo tubo cubre 3 tramos
    else:
        tubos_totales_50_75 = cantidad_tramos_ancho * math.ceil(largo / 6)  # 6 metros por tubo

    # Agregar los tubos de frente y fondo según el ancho del techo
    if ancho <= 3:
        tubos_frente_fondo = 1  # Sin tubos adicionales para frente y fondo
    else:
        tubos_frente_fondo = 2  # Agregar 2 tubos para frente y fondo si el ancho es mayor a 3m

    tubos_totales_50_75 += tubos_frente_fondo

    # Calcular el peso total de los tubos de 50-75 y su costo
    peso_tubo_50_75 = tubos_totales_50_75 * pesos_materiales['tubo_50_75']
    costo_tubos_50_75 = peso_tubo_50_75 * precios_por_kg[tratamiento]
    costo_total += costo_tubos_50_75
    resultado.append({
        'Material': 'Tubo 50-75',
        'Cantidad': tubos_totales_50_75,
        'Peso Total (kg)': peso_tubo_50_75,
        'Costo Material': costo_tubos_50_75
    })

    # Calcular ángulos 30-30 para la estructura fija
    if tipo_techo == 'fijo':
        cantidad_angulo_30_30 = tubos_totales_50_75 // 2
        peso_angulo_30_30 = cantidad_angulo_30_30 * pesos_materiales['angulo_30_30']
        costo_angulo_30_30 = peso_angulo_30_30 * precios_por_kg[tratamiento]
        costo_total += costo_angulo_30_30
        resultado.append({
            'Material': 'Ángulo 30-30',
            'Cantidad': cantidad_angulo_30_30,
            'Peso Total (kg)': peso_angulo_30_30,
            'Costo Material': costo_angulo_30_30
        })

    # Materiales adicionales para techo corredizo
    if tipo_techo == 'corredizo':
        # Preguntar cuántos paños corredizos tiene el usuario
        if cantidad_paños is None:
            cantidad_paños = st.number_input("Cantidad de paños corredizos:", min_value=1, step=1, key="cantidad_paños")

        # Duplicar la cantidad de materiales por cada paño adicional
        cantidad_tubo_40_20 = math.ceil(tubos_totales_50_75 / 2) * cantidad_paños
        peso_tubo_40_20 = cantidad_tubo_40_20 * pesos_materiales['tubo_40_20']
        costo_tubo_40_20 = peso_tubo_40_20 * precios_por_kg[tratamiento]
        costo_total += costo_tubo_40_20
        resultado.append({
            'Material': 'Tubo 40-20',
            'Cantidad': cantidad_tubo_40_20,
            'Peso Total (kg)': peso_tubo_40_20,
            'Costo Material': costo_tubo_40_20
        })

        # Duplicar la cantidad de molinillos por cada paño
        cantidad_molinillos = cantidad_paños * st.number_input("Cantidad de molinillos por paño:", min_value=1, step=1, key="cantidad_molinillos")
        costo_molinillos = cantidad_molinillos * 45900
        costo_total += costo_molinillos
        resultado.append({
            'Material': 'Molinillo',
            'Cantidad': cantidad_molinillos,
            'Peso Total (kg)': None,
            'Costo Material': costo_molinillos
        })

        # Duplicar la cantidad de guías por cada paño
        cantidad_guia = 2 * cantidad_paños if largo > 3 else 1 * cantidad_paños
        peso_guia = cantidad_guia * pesos_materiales['guia_techo_corredizo']
        costo_guia = peso_guia * precios_por_kg[tratamiento]
        costo_total += costo_guia
        resultado.append({
            'Material': 'Guía para techo corredizo',
            'Cantidad': cantidad_guia,
            'Peso Total (kg)': peso_guia,
            'Costo Material': costo_guia
        })

        # Ángulos 30-30 para techo corredizo
        cantidad_angulo_30_30 = tubos_totales_50_75 // 2 * cantidad_paños  # Duplicar según los paños
        peso_angulo_30_30 = cantidad_angulo_30_30 * pesos_materiales['angulo_30_30']
        costo_angulo_30_30 = peso_angulo_30_30 * precios_por_kg[tratamiento]
        costo_total += costo_angulo_30_30
        resultado.append({
            'Material': 'Ángulo 30-30',
            'Cantidad': cantidad_angulo_30_30,
            'Peso Total (kg)': peso_angulo_30_30,
            'Costo Material': costo_angulo_30_30
        })

    # Cálculo del material de cubierta
    if cubierta == 'poliacrilico':
        costo_cubierta = area_techo * precio_poliacrilico_m2
        resultado.append({
            'Material': 'Poliacrílico',
            'Cantidad (m²)': area_techo,
            'Peso Total (kg)': None,
            'Costo Material': costo_cubierta
        })
        costo_total += costo_cubierta
    elif cubierta == 'vidrio':
        resultado.append({
            'Material': 'Vidrio',
            'Cantidad (m²)': area_techo,
            'Peso Total (kg)': None,
            'Costo Material': costo_vidrio
        })
        costo_total += costo_vidrio

    # Agregar costos adicionales
    resultado.append({
        'Material': 'Zinguería',
        'Cantidad': None,
        'Peso Total (kg)': None,
        'Costo Material': costo_zingueria
    })
    costo_total += costo_zingueria

    resultado.append({
        'Material': 'Otros costos adicionales',
        'Cantidad': None,
        'Peso Total (kg)': None,
        'Costo Material': otros_costos
    })
    costo_total += otros_costos

    df_resultado = pd.DataFrame(resultado)
    df_resultado.loc['Total'] = df_resultado[['Costo Material']].sum()

    return df_resultado, costo_total

def generar_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Materiales y Costos")
    output.seek(0)
    return output

# Interfaz de usuario con Streamlit
st.title("Calculadora de Materiales para Techos")
st.write("Ingrese las dimensiones y el tipo de techo para calcular los materiales y costos.")

# Inputs del usuario
ancho = st.number_input("Ancho del techo (m):", min_value=0.1, step=0.1)
largo = st.number_input("Largo del techo (m):", min_value=0.1, step=0.1)
tipo_techo = st.selectbox("Tipo de techo:", ["fijo", "corredizo"])
tratamiento = st.selectbox("Color de la estructura:", ["blanco", "negro_color", "anodizado_natural"])
cubierta = st.selectbox("Cubierta del techo:", ["poliacrilico", "vidrio"])
costo_vidrio = st.number_input("Costo del vidrio (solo si se selecciona vidrio):", min_value=0.0, step=100.0)
costo_zingueria = st.number_input("Costo de zinguería:", min_value=0.0, step=100.0)
otros_costos = st.number_input("Otros costos adicionales:", min_value=0.0, step=100.0)

# Calcular materiales y costos
if tipo_techo == "corredizo":
    df_resultado, costo_total = calcular_materiales_costo(tipo_techo, ancho, largo, tratamiento, cubierta, costo_vidrio, costo_zingueria, otros_costos)
else:
    df_resultado, costo_total = calcular_materiales_costo(tipo_techo, ancho, largo, tratamiento, cubierta, costo_vidrio, costo_zingueria, otros_costos)

# Mostrar los resultados
st.write(df_resultado)
st.write(f"El costo total es: ${costo_total}")

# Opción de descargar el archivo Excel
excel_data = generar_excel(df_resultado)
st.download_button(
    label="Descargar Excel",
    data=excel_data,
    file_name="materiales_y_costos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
