"""Pruebas del cálculo de la SUS. Ejecutar desde la raíz: python -m unittest scripts.usabilidad.test_procesar_sus"""

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.usabilidad import procesar_sus as sus


class CalculoSUS(unittest.TestCase):
    def test_ejemplo_de_brooke(self):
        # Ejemplo resuelto del artículo original: contribuciones 4,1,1,4,1,2,1,1,4,3 -> total 22 -> 55.
        respuestas = [5, 4, 2, 1, 2, 3, 2, 4, 5, 2]
        self.assertEqual(sus.contribuciones(respuestas), [4, 1, 1, 4, 1, 2, 1, 1, 4, 3])
        self.assertEqual(sus.puntaje(respuestas), 55.0)

    def test_filas_del_material_del_curso(self):
        self.assertEqual(sus.puntaje([4, 1, 5, 2, 4, 1, 3, 2, 5, 1]), 85.0)
        self.assertEqual(sus.puntaje([3, 2, 4, 1, 5, 2, 4, 3, 4, 2]), 75.0)
        self.assertEqual(sus.puntaje([2, 3, 4, 2, 3, 3, 2, 4, 4, 3]), 50.0)

    def test_extremos(self):
        self.assertEqual(sus.puntaje([5, 1, 5, 1, 5, 1, 5, 1, 5, 1]), 100.0)
        self.assertEqual(sus.puntaje([1, 5, 1, 5, 1, 5, 1, 5, 1, 5]), 0.0)
        self.assertEqual(sus.puntaje([3] * 10), 50.0)

    def test_rechaza_valores_invalidos(self):
        with self.assertRaises(ValueError):
            sus.puntaje([6, 1, 5, 1, 5, 1, 5, 1, 5, 1])
        with self.assertRaises(ValueError):
            sus.puntaje([0, 1, 5, 1, 5, 1, 5, 1, 5, 1])
        with self.assertRaises(ValueError):
            sus.puntaje([3] * 9)

    def test_el_umbral_de_68_cuenta_como_aceptable(self):
        # La consigna define el umbral como >= 68: un 68 exacto debe alcanzarlo.
        self.assertEqual(sus.grado(68.0), "C")
        self.assertEqual(sus.grado(84.1), "A+")
        self.assertEqual(sus.grado(51.6), "F")
        self.assertIn("Sí", next(l for l in sus.informe([sus.Participante("P01", [4, 2, 4, 2, 4, 2, 4, 2, 4, 2], {})]).splitlines() if "Alcanza" in l))


class LecturaCSV(unittest.TestCase):
    def _csv(self, filas, encabezado=None, delimitador=","):
        encabezado = encabezado or (
            ["Marca temporal", "¿Con qué rol probaste el sistema?"]
            + [f"P{i}. Enunciado {i}" for i in range(1, 11)]
            + ["¿Qué fue lo que más te costó o te confundió al usar el sistema?"]
        )
        archivo = Path(tempfile.mkdtemp()) / "r.csv"
        with archivo.open("w", encoding="utf-8-sig", newline="") as f:
            escritor = csv.writer(f, delimiter=delimitador)
            escritor.writerow(encabezado)
            escritor.writerows(filas)
        return archivo

    def test_lee_exportacion_de_forms(self):
        archivo = self._csv([["2026/11/18 10:00", "Operador", 4, 1, 5, 2, 4, 1, 3, 2, 5, 1, "nada"]])
        participantes = sus.leer_csv(archivo)
        self.assertEqual(participantes[0].codigo, "P01")
        self.assertEqual(participantes[0].puntaje, 85.0)
        self.assertEqual(participantes[0].contexto, {"¿Con qué rol probaste el sistema?": "Operador"})

    def test_acepta_punto_y_coma(self):
        archivo = self._csv([["2026/11/18 10:00", "Conductor", 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, ""]], delimitador=";")
        self.assertEqual(sus.leer_csv(archivo)[0].puntaje, 50.0)

    def test_fila_con_respuesta_fuera_de_rango_da_error_claro(self):
        archivo = self._csv([["2026/11/18 10:00", "Operador", 4, 1, 9, 2, 4, 1, 3, 2, 5, 1, ""]])
        with self.assertRaisesRegex(ValueError, "Fila 1"):
            sus.leer_csv(archivo)

    def test_faltan_columnas(self):
        archivo = self._csv([["x", "y", 1, 2]], encabezado=["Marca temporal", "rol", "P1. a", "P2. b"])
        with self.assertRaisesRegex(ValueError, "columnas"):
            sus.leer_csv(archivo)


if __name__ == "__main__":
    unittest.main()
