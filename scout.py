"""
KIMI OS - AGENTE: SCOUT
Detecta oportunidades de mercado 24/7.
Autonomía: 99%
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

class ScoutAgente:
    """
    El explorador del mercado. Nunca duerme.
    Lee Reddit, Twitter, LinkedIn, foros, news.
    Detecta: "Necesito API para...", "Cómo automatizar...", "Alguien sabe..."
    """

    def __init__(self, nucleo, memoria):
        self.nucleo = nucleo
        self.memoria = memoria
        self.oportunidades_detectadas = []
        self.fuentes = [
            "reddit", "twitter", "linkedin", "hackernews",
            "indiehackers", "producthunt", "github_issues"
        ]

    async def escanear_mercado(self) -> List[Dict[str, Any]]:
        """
        Escanear todas las fuentes por oportunidades.
        """
        oportunidades = []

        for fuente in self.fuentes:
            ops = await self._escanear_fuente(fuente)
            oportunidades.extend(ops)

        # Filtrar por valor
        oportunidades_valiosas = [
            op for op in oportunidades 
            if op.get("intencion_compra", 0) > 0.7
        ]

        self.oportunidades_detectadas.extend(oportunidades_valiosas)

        print(f"🔍 Scout: {len(oportunidades_valiosas)} oportunidades detectadas")
        return oportunidades_valiosas

    async def _escanear_fuente(self, fuente: str) -> List[Dict]:
        """Escanear una fuente específica (simulado)"""
        # En producción: APIs reales de Reddit, Twitter, etc.
        oportunidades_simuladas = [
            {
                "fuente": fuente,
                "texto": "Necesito API para resumir contratos legales en español",
                "industria": "legal",
                "idioma": "es",
                "intencion_compra": 0.9,
                "volumen_estimado": 50,
                "timestamp": datetime.now()
            },
            {
                "fuente": fuente,
                "texto": "Cómo automatizar respuestas de WhatsApp para mi restaurante",
                "industria": "restaurantes",
                "idioma": "es",
                "intencion_compra": 0.85,
                "volumen_estimado": 30,
                "timestamp": datetime.now()
            }
        ]
        return oportunidades_simuladas

    async def priorizar(self, oportunidades: List[Dict]) -> Dict[str, Any]:
        """
        Priorizar la mejor oportunidad basado en:
        - Intención de compra
        - Volumen estimado
        - Competencia baja
        - Facilidad de construcción
        """
        if not oportunidades:
            return None

        # Score compuesto
        for op in oportunidades:
            op["score"] = (
                op["intencion_compra"] * 0.4 +
                min(op["volumen_estimado"] / 100, 1.0) * 0.3 +
                0.2 +  # Facilidad (asumida alta)
                0.1   # Competencia baja (asumida)
            )

        mejor = max(oportunidades, key=lambda x: x["score"])
        print(f"🎯 Scout: Mejor oportunidad -> {mejor['industria']} (score: {mejor['score']:.2f})")
        return mejor
