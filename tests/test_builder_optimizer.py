import asyncio

from builder import BuilderAgente
from memoria_compartida import MemoriaCompartida
from optimizer import OptimizerAgente


def test_builder_and_optimizer_store_experiences():
    async def run_flow():
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

        assert api["estado"] == "construida"
        assert result["errores_corregidos"] == 1
        assert result["mejoras_aplicadas"] == 1
        assert len(memoria.experiencias) == 2

    asyncio.run(run_flow())
