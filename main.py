from src.extract.fetch_api import fetch as ejecutar_extraccion
from src.transform.cargar_datos import cargar_datos
from src.transform.limpiar_datos import limpiar_datos

datos = {}
datos_limpios = {}
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
            if not datos:
                print("Primero debes cargar los datos usando la opción 2.")
            else:
                datos_limpios = limpiar_datos(datos)
                print("Proceso de limpieza finalizado.")
        case 4:
            if not datos_limpios:
                print("Primero debes limpiar los datos usando la opción 3.")
            else:
                for nombre, df in datos_limpios.items():
                    print(f"\n{'=' * 55}")
                    print(f"DATAFRAME LIMPIO: {nombre.upper()}")
                    print(f"{'=' * 55}")
                    print(df.to_string(index=False))

                    print("\nValores nulos por columna:")
                    print(df.isnull().sum())

                    print(f"\nCantidad de registros limpios: {len(df)}")
        case 5:
            pass
        case 6:
            pass