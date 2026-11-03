from src.extract.fetch_api import fetch as ejecutar_extraccion
from src.transform.cargar_datos import cargar_datos
from src.transform.limpiar_datos import limpiar_datos

# datos = {}
# print("Bienvenido al sistema de análisis de datos (en proceso) de PetMind")
# while True:
#     print("""
#     Haz ingresado al menú, estas son las opciones disponibles:
#     1. Traer datos desde la API
#     2. Cargar datos
#     3. Limpiar datos
#     4. Imprimir datos limpios
#     5. Mergear datos
#     6. Consultas de datos
#     0. Salir""")
#     while True:
#         try:
#             opcion = int(input("Seleccione su opción: \n"))
#             if opcion < 0 or opcion > 6:
#                 print("Seleccione una opción válida")
#                 continue
#             else:
#                 break
#         except:
#             print("Opción no disponible")
#             continue
#     match opcion:
#         case 0:
#             print("Gracias por usar nuestro servicio")
#             break
#         case 1:
#             ejecutar_extraccion()
#         case 2:
#             datos = cargar_datos()
#         case 3:
#             datos = limpiar_datos(datos)
#         case 4:
#             pass
#         case 5:
#             pass
#         case 6:
#             pass

# Importaciones necesarias
import requests
import pandas as pd

# 1. URL del endpoint del API
url_api = "https://backendpetmind2-3bhm9fqy.b4a.run/api/usuarios"  # Cambia esto según el endpoint que quieras consultar

# 2. Realizar la petición GET para obtener los datos
response = requests.get(url_api)

# 3. Convertir la respuesta (que viene en formato JSON) a un diccionario de Python
datos_json = response.json()

# 4. Cargar los datos en un DataFrame
df_api = pd.DataFrame(datos_json)

df_api.info()