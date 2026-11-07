import unittest

from app.analytics import build_dashboard
from app.data_cleaning import clean_dataframes, convert_resources_to_dataframes


def dashboard_from(resources):
    """Pasa los datos por la misma limpieza que usa la API antes de agrupar."""
    return build_dashboard(clean_dataframes(convert_resources_to_dataframes(resources)))


class DashboardTest(unittest.TestCase):
    def setUp(self):
        # Como responde el backend hoy: las relaciones llegan solo como ids.
        self.resources = {
            "mascotas": [
                {"id": 1, "fundacionId": 19, "especie": "PERRO", "estadoAdopcion": "DISPONIBLE", "fechaPublicacion": "2026-10-27T09:00:00"},
                {"id": 2, "fundacionId": 19, "especie": "GATO", "estadoAdopcion": "ADOPTADO", "fechaPublicacion": "2026-11-02T15:30:00"},
                {"id": 3, "fundacionId": 20, "especie": "PERRO", "estadoAdopcion": "DISPONIBLE", "fechaPublicacion": None, "fechaCreacion": "2026-10-12T08:00:00"},
            ],
            "fundaciones": [
                {"id": 19, "nombre": "Patas Unidas Bello"},
                {"id": 20, "nombre": "Fundación Corazón Peludo"},
            ],
            "solicitudes": [
                {"id": 7, "mascotaId": 1, "estado": "PENDIENTE"},
                {"id": 8, "mascotaId": 2, "estado": "APROBADA"},
            ],
            "favoritos": [
                {"id": 4, "mascotaId": 1, "campanaId": None},
                {"id": 5, "mascotaId": None, "campanaId": 3},
            ],
            "donaciones": [],
            "campanas": [],
        }

    def test_mascotas_por_fundacion_cruza_el_id_con_la_lista_de_fundaciones(self):
        self.assertEqual(
            dashboard_from(self.resources)["mascotasPorFundacion"],
            [{"fundacion": "PATAS UNIDAS BELLO", "cantidad": 2}, {"fundacion": "FUNDACIÓN CORAZÓN PELUDO", "cantidad": 1}],
        )

    def test_solicitudes_y_favoritos_por_especie_cruzan_mascota_id(self):
        dashboard = dashboard_from(self.resources)
        self.assertEqual(
            dashboard["solicitudesPorEspecie"],
            [{"especie": "GATO", "cantidad": 1}, {"especie": "PERRO", "cantidad": 1}],
        )
        # El favorito de una campaña no tiene mascota: no cuenta como especie.
        self.assertEqual(dashboard["favoritosPorEspecie"], [{"especie": "PERRO", "cantidad": 1}])

    def test_mascotas_por_estado_de_adopcion(self):
        self.assertEqual(
            dashboard_from(self.resources)["mascotasPorEstadoAdopcion"],
            [{"categoria": "DISPONIBLE", "cantidad": 2}, {"categoria": "ADOPTADO", "cantidad": 1}],
        )

    def test_mascotas_por_semana_llena_las_semanas_sin_publicaciones(self):
        # Semanas de lunes a domingo: 12 oct (por fecha de creación), 26 oct y 2 nov; la del 19 oct queda en cero.
        self.assertEqual(
            dashboard_from(self.resources)["mascotasPorSemana"],
            [
                {"semana": "2026-10-12", "cantidad": 1},
                {"semana": "2026-10-19", "cantidad": 0},
                {"semana": "2026-10-26", "cantidad": 1},
                {"semana": "2026-11-02", "cantidad": 1},
            ],
        )

    def test_sin_datos_no_falla(self):
        vacio = {name: [] for name in self.resources}
        dashboard = dashboard_from(vacio)
        self.assertEqual(dashboard["mascotasPorSemana"], [])
        self.assertEqual(dashboard["mascotasPorFundacion"], [])
        self.assertEqual(dashboard["solicitudesPorEspecie"], [])

    def test_sigue_aceptando_relaciones_anidadas(self):
        recursos = dict(self.resources)
        recursos["mascotas"] = [{"id": 1, "especie": "PERRO", "fundacion": {"nombre": "Huellas"}}]
        recursos["solicitudes"] = [{"id": 7, "mascota": {"especie": "GATO"}, "estado": "PENDIENTE"}]
        dashboard = dashboard_from(recursos)
        self.assertEqual(dashboard["mascotasPorFundacion"], [{"fundacion": "HUELLAS", "cantidad": 1}])
        self.assertEqual(dashboard["solicitudesPorEspecie"], [{"especie": "GATO", "cantidad": 1}])


if __name__ == "__main__":
    unittest.main()
