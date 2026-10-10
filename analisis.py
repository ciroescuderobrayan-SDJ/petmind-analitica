from src.extract.fetch_api import fetch as ejecutar_extraccion
from src.transform.cargar_datos import cargar_datos
from src.transform.combinar_datos import combinar_datos
from src.transform.limpiar_datos import limpiar_datos

datos = {}
datos_limpios = {}
datos_combinados = None
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
            if not datos_limpios:
                print("Primero debes limpiar los datos usando la opción 3.")
            else:
                datos_combinados = combinar_datos(datos_limpios)
                print(datos_combinados.to_string(index=False))
        case 6:
            if datos_combinados is None:
                print("Primero debes combinar los datos usando la opción 5.")
            else:
                # 1. Frecuencia: usuario con más favoritos.
                conteo = datos_combinados["id_user"].value_counts()
                id_usuario = conteo.idxmax()
                nombre = datos_combinados.loc[
                    datos_combinados["id_user"] == id_usuario, "name"
                ].iloc[0]
                print("\n1. ¿Qué usuario tiene más favoritos?")
                print(f"{nombre} (id {id_usuario}) con {conteo.max()} favoritos.")

                # 2. Agregación: cantidad de favoritos por ciudad.
                print("\n2. ¿Cuántos favoritos hay por ciudad?")
                print(datos_combinados.groupby("city").size().to_string())

                # 3. Filtrado y conteo: usuarios que viven en Medellín.
                usuarios = datos_limpios["user"]
                usuarios_medellin = usuarios[usuarios["city"] == "medellín"]
                print("\n3. ¿Cuántos usuarios son de Medellín?")
                print(f"{len(usuarios_medellin)} usuarios.")