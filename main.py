from src.extract.fetch_api import fetch as ejecutar_extraccion
from src.transform.cargar_datos import cargar_datos

datos = {}
print("Bienvenido al sistema de análisis de datos (en proceso) de PetMind")
while True:
    print("""
    Haz ingresado al menú, estas son las opciones disponibles:
    1. Traer datos desde la API
    2. Cargar datos
    3. Limpiar datos
    4. Imprimir datos limpios
    5. Mergear datos
    6. Consultas de datos
    0. Salir""")
    while True:
        try:
            opcion = int(input("Seleccione su opción: \n"))
            if opcion < 0 or opcion > 6:
                print("Seleccione una opción válida")
                continue
            else:
                break
        except:
            print("Opción no disponible")
            continue
    match opcion:
        case 0:
            break
        case 1:
            ejecutar_extraccion()
        case 2:
            datos = cargar_datos()
        case 3:
            pass
        case 4:
            pass
        case 5:
            pass
        case 6:
            pass