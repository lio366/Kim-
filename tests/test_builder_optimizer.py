import unittest

from builder import BuilderAgente
from memoria_compartida import MemoriaCompartida
from optimizer import OptimizerAgente


class BuilderOptimizerTests(unittest.IsolatedAsyncioTestCase):
    async def test_builder_and_optimizer_store_experiences(self):
        memoria = MemoriaCompartida()
        builder = BuilderAgente(None, memoria)
        optimizer = OptimizerAgente(None, memoria)

        api = await builder.construir_api(
            {
                "industria": "salud",
                "idioma": "es",
                "texto": "API de ejemplo",
            }
        )
        result = await optimizer.optimizar_api(
            api["id"], [{"nivel": "error", "latencia_ms": 1200}]
        )

        self.assertEqual(api["estado"], "construida")
        self.assertEqual(result["errores_corregidos"], 1)
        self.assertEqual(result["mejoras_aplicadas"], 1)
        self.assertEqual(len(memoria.experiencias), 2)
