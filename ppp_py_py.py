# -*- coding: utf-8 -*-
"""ppp_py.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13l3xIiSQGe5y65KfIJTxZBVunOfXR6Wl
"""

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# import streamlit as st
# import gspread
# import pandas as pd
# from google.colab import auth
# from google.auth import default
# 
# # Autenticación
# auth.authenticate_user()
# creds, _ = default()
# gc = gspread.authorize(creds)
# 
# # Carga de datos desde Google Sheets
# sheet_url = "https://docs.google.com/spreadsheets/d/1DXNDdLWuNEVfykJeO9NkNzn6JFBkfrc0u4YTLNh3xP8/edit"
# worksheet_name = "INVENTARIO-VENTASXMES"
# st.title("Sistema de Inventario")
# st.write("Cargando datos...")
# 
# spreadsheet = gc.open_by_url(sheet_url)
# worksheet = spreadsheet.worksheet(worksheet_name)
# data = worksheet.get_all_records()
# df = pd.DataFrame(data)
# 
# st.write("Datos cargados:")
# st.dataframe(df)
# 
# # Agregar análisis o gráficos
# st.write("Resumen de productos a pedir:")
# df['Pedido recomendado'] = (df['Inventario minimo'] + df['inventario de seguridad'] - df['Existencia']).clip(lower=0)
# resumen = df[df['Pedido recomendado'] > 0]
# st.dataframe(resumen)
#

# Instalación de las bibliotecas necesarias


import gspread
from google.colab import auth
from google.auth import default
import pandas as pd
import matplotlib.pyplot as plt
from google.colab import files

# ==========================
# 🔐 AUTENTICACIÓN CON GOOGLE
# ==========================
print("\n🔐 Autenticando con Google...")
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)
print("✅ Autenticación exitosa.")

# ==========================
# 📂 CONECTAR A GOOGLE SHEETS
# ==========================
sheet_url = "https://docs.google.com/spreadsheets/d/1DXNDdLWuNEVfykJeO9NkNzn6JFBkfrc0u4YTLNh3xP8/edit"
print(f"\n📂 Conectando a la hoja de cálculo:\n{sheet_url}")
spreadsheet = gc.open_by_url(sheet_url)

# ==========================
# 📑 SELECCIONAR LA HOJA PRINCIPAL
# ==========================
worksheet_name = "INVENTARIO-VENTASXMES"
print(f"📑 Seleccionando la hoja: '{worksheet_name}'")
worksheet = spreadsheet.worksheet(worksheet_name)

# ==========================
# 📊 CARGAR LOS DATOS EN UN DATAFRAME
# ==========================
print("\n📊 Cargando datos...")
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Verificar las columnas disponibles
print("\n📝 Encabezados disponibles en la hoja:")
print(df.columns.tolist())

# ==========================
# 🔍 VERIFICACIÓN DE COLUMNAS
# ==========================
necesarias = ['Nombre', 'Existencia', 'Inventario minimo', 'inventario de seguridad']  # Nombres exactos del archivo
opcional = 'Vendido'  # Columna opcional para el gráfico de ventas
disponibles = df.columns.tolist()

faltantes = [col for col in necesarias if col not in disponibles]
if faltantes:
    print(f"\n⚠️ Error: Las siguientes columnas necesarias no están en la hoja: {faltantes}")
    print(f"📌 Columnas disponibles: {disponibles}")
    raise KeyError("Columnas faltantes en el archivo")

# ==========================
# 🔧 LIMPIEZA DE DATOS
# ==========================
print("\n🔧 Limpiando datos...")
columnas_numericas = ['Existencia', 'Inventario minimo', 'inventario de seguridad']

for columna in columnas_numericas:
    df[columna] = (
        df[columna]
        .replace({',': '', '\.': ''}, regex=True)  # Eliminar separadores de miles
        .astype(str)  # Asegurarse de que todo sea texto antes de convertir
        .str.replace(' ', '')  # Eliminar espacios
    )
    df[columna] = pd.to_numeric(df[columna], errors='coerce').fillna(0)  # Convertir a número

# Calcular el pedido recomendado
df['Pedido recomendado'] = (df['Inventario minimo'] + df['inventario de seguridad'] - df['Existencia']).clip(lower=0)

if opcional in disponibles:
    df[opcional] = pd.to_numeric(df[opcional], errors='coerce').fillna(0)

print("✅ Datos preparados correctamente.")

# ==========================
# 📄 FUNCIÓN: RESUMEN DE PRODUCTOS A PEDIR
# ==========================
def generar_resumen():
    print("\n🔎 Generando resumen de productos a pedir...")
    try:
        productos_a_pedir = df[df['Pedido recomendado'] > 0]

        if not productos_a_pedir.empty:
            print("\n📋 Resumen de productos a pedir:")
            print(productos_a_pedir[['Nombre', 'Existencia', 'Inventario minimo', 'inventario de seguridad', 'Pedido recomendado']])

            file_name = "Resumen_Productos_Pedir.xlsx"
            productos_a_pedir.to_excel(file_name, index=False, engine='openpyxl')
            print(f"\n✅ Resumen guardado como: {file_name}")
            files.download(file_name)
        else:
            print("\n⚠️ No hay productos que necesiten ser pedidos.")
    except Exception as e:
        print(f"❌ Error al generar el resumen: {e}")

# ==========================
# 📈 FUNCIÓN: GRÁFICO DE PRODUCTOS MÁS VENDIDOS
# ==========================
def generar_grafico_ventas():
    if opcional not in disponibles:
        print("\n⚠️ La columna 'Vendido' no está disponible. No se puede generar el gráfico.")
        return

    print("\n📊 Generando gráfico de productos más vendidos...")
    try:
        productos_mas_vendidos = df.sort_values(by=opcional, ascending=False).head(10)

        plt.figure(figsize=(10, 6))
        plt.barh(productos_mas_vendidos['Nombre'], productos_mas_vendidos[opcional], color='green')
        plt.xlabel("Cantidad Vendida")
        plt.ylabel("Producto")
        plt.title("Top 10 Productos Más Vendidos")
        plt.gca().invert_yaxis()
        plt.tight_layout()

        grafico_file = "Grafico_Top10_Ventas.png"
        plt.savefig(grafico_file)
        plt.show()
        print(f"\n✅ Gráfico guardado como: {grafico_file}")
        files.download(grafico_file)
    except Exception as e:
        print(f"❌ Error al generar el gráfico: {e}")

# ==========================
# 📌 MENÚ PRINCIPAL
# ==========================
def menu():
    while True:
        print("\n📌 MENÚ PRINCIPAL:")
        print("1️⃣ Generar resumen de productos a pedir")
        print("2️⃣ Generar gráfico de productos más vendidos")
        print("3️⃣ Salir")
        opcion = input("👉 Selecciona una opción (1, 2 o 3): ").strip()

        if opcion == "1":
            generar_resumen()
        elif opcion == "2":
            generar_grafico_ventas()
        elif opcion == "3":
            print("\n👋 Programa terminado. ¡Hasta luego!")
            break
        else:
            print("⚠️ Opción no válida. Intenta nuevamente.")

# ==========================
# 🚀 EJECUTAR EL MENÚ
# ==========================
menu()

columnas_numericas = ['Existencia', 'Inventario minimo', 'inventario de seguridad']

for columna in columnas_numericas:
    df[columna] = (
        df[columna]
        .replace({',': '', '\.': ''}, regex=True)  # Eliminar separadores de miles
        .astype(str)  # Asegurarse de que todo sea texto antes de convertir
        .str.replace(' ', '')  # Eliminar espacios
    )
    df[columna] = pd.to_numeric(df[columna], errors='coerce').fillna(0)  # Convertir a número

!pip install streamlit pyngrok

import streamlit as st

st.title("Mi Aplicación de Inventario")
st.write("Bienvenido a la aplicación.")

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# import streamlit as st
# st.title("Mi Aplicación de Inventario")
# st.write("¡Hola! Este es un ejemplo básico de Streamlit.")
#

!pip install --upgrade pyngrok

!streamlit run app.py & ./cloudflared tunnel --url http://localhost:8501

with open("requirements.txt", "w") as f:
    f.write("""streamlit
gspread
pandas
matplotlib
openpyxl
google-auth
google-auth-oauthlib
google-auth-httplib2
""")

from google.colab import files
files.download("requirements.txt")


!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
!chmod +x cloudflared
