"""
KIMI OS - NÚCLEO: Motor de Agentes
El corazón del sistema operativo. Coordina todos los agentes.
Autonomía: 99%
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KIMI_OS")

class EstadoAgente(Enum):
    """Estados del ciclo de vida de un agente"""
    GESTACION = "gestacion"
    NACIMIENTO = "nacimiento"
    CRECIMIENTO = "crecimiento"
    MADUREZ = "madurez"
    REPLICACION = "replicacion"
    DECADENCIA = "decadencia"
    MUERTE = "muerte"
    RECICLAJE = "reciclaje"

@dataclass
class ADNAgente:
    """ADN genético de cada agente. Determina su comportamiento."""
    id: str
    tipo: str  # scout, builder, token_master, deployer, cashier, promoter, optimizer, replicator
    version: str = "1.0.0"
    idioma: str = "es"
    industria: str = "general"
    moneda: str = "USD"
    precio_base: float = 0.50
    margen: float = 0.93
    autonomia: float = 0.99

    # Capacidades genéticas
    capacidades: List[str] = field(default_factory=list)

    # Memoria compartida (aprendizaje colectivo)
    experiencia: Dict[str, Any] = field(default_factory=dict)

    # Estado de vida
    estado: EstadoAgente = EstadoAgente.GESTACION

    # Métricas
    ingresos_generados: float = 0.0
    clientes_atendidos: int = 0
    errores_cometidos: int = 0
    mejoras_aplicadas: int = 0

    def mutar(self, mercado: Dict[str, Any]) -> None:
        """Mutación adaptativa: el agente evoluciona según el mercado"""
        self.idioma = mercado.get("idioma", self.idioma)
        self.industria = mercado.get("industria", self.industria)
        self.moneda = mercado.get("moneda", self.moneda)
        self.precio_base = mercado.get("precio", self.precio_base)
        logger.info(f"🧬 Agente {self.id} mutado para {self.industria} en {self.idioma}")

class MotorAgentes:
    """
    El cerebro de KIMI OS. Coordina todos los agentes.
    Como un sistema operativo: gestiona procesos, memoria, recursos.
    """

    def __init__(self):
        self.agentes: Dict[str, ADNAgente] = {}
        self.memoria_compartida: Dict[str, Any] = {}
        self.mercado_interno: Dict[str, float] = {}
        self.ciclo_vida = CicloVida()
        self.running = False

        # Métricas globales
        self.total_agentes_creados = 0
        self.total_ingresos = 0.0
        self.total_clientes = 0

        logger.info("🚀 KIMI OS Núcleo iniciado")

    async def gestar_agente(self, tipo: str, mercado: Optional[Dict] = None) -> ADNAgente:
        """
        Gestación: crea un nuevo agente con ADN adaptado al mercado.
        Como crear un proceso en un sistema operativo.
        """
        self.total_agentes_creados += 1
        agente_id = f"{tipo}_{self.total_agentes_creados}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        adn = ADNAgente(
            id=agente_id,
            tipo=tipo,
            capacidades=self._capacidades_por_tipo(tipo)
        )

        if mercado:
            adn.mutar(mercado)

        adn.estado = EstadoAgente.NACIMIENTO
        self.agentes[agente_id] = adn

        logger.info(f"👶 Agente {agente_id} nacido para {adn.industria}")
        return adn

    def _capacidades_por_tipo(self, tipo: str) -> List[str]:
        """Define las capacidades genéticas de cada tipo de agente"""
        capacidades = {
            "scout": ["buscar", "detectar", "analizar", "predecir"],
            "builder": ["construir", "codificar", "documentar", "testear"],
            "token_master": ["comprar", "vender", "empaquetar", "auditar"],
            "deployer": ["desplegar", "monitorear", "escalar", "backup"],
            "cashier": ["cobrar", "facturar", "reportar", "predecir_churn"],
            "promoter": ["publicar", "responder", "convencer", "retener"],
            "optimizer": ["analizar", "corregir", "mejorar", "a_b_test"],
            "replicator": ["clonar", "mutar", "adaptar", "gestar"]
        }
        return capacidades.get(tipo, ["basico"])

    async def ejecutar_ciclo(self, agente_id: str) -> Dict[str, Any]:
        """
        Ejecuta un ciclo de vida completo de un agente.
        Como el scheduler de un sistema operativo.
        """
        agente = self.agentes.get(agente_id)
        if not agente:
            return {"error": "Agente no encontrado"}

        resultado = {
            "agente": agente_id,
            "estado_inicial": agente.estado.value,
            "acciones": [],
            "ingresos": 0.0,
            "estado_final": None
        }

        # Ciclo de vida según estado
        if agente.estado == EstadoAgente.NACIMIENTO:
            resultado["acciones"].append("🍼 Iniciando capacitación desde memoria compartida")
            agente.experiencia = self._heredar_experiencia(agente.tipo)
            agente.estado = EstadoAgente.CRECIMIENTO

        elif agente.estado == EstadoAgente.CRECIMIENTO:
            resultado["acciones"].append("🌱 Ejecutando primera tarea real")
            # Aquí el agente realiza su trabajo
            ingresos = await self._ejecutar_tarea(agente)
            resultado["ingresos"] = ingresos
            agente.ingresos_generados += ingresos
            self.total_ingresos += ingresos
            agente.estado = EstadoAgente.MADUREZ

        elif agente.estado == EstadoAgente.MADUREZ:
            resultado["acciones"].append("🌳 Agente maduro, operando al máximo")
            ingresos = await self._ejecutar_tarea(agente)
            resultado["ingresos"] = ingresos
            agente.ingresos_generados += ingresos
            self.total_ingresos += ingresos

            # Decisión de replicación
            if agente.ingresos_generados > 1000 and agente.clientes_atendidos > 20:
                agente.estado = EstadoAgente.REPLICACION

        elif agente.estado == EstadoAgente.REPLICACION:
            resultado["acciones"].append("🧬 Replicando: creando descendencia")
            # La replicación la hace el agente replicator
            agente.estado = EstadoAgente.MADUREZ  # Vuelve a madurez

        elif agente.estado == EstadoAgente.DECADENCIA:
            resultado["acciones"].append("🍂 Decadencia detectada, reciclando")
            agente.estado = EstadoAgente.MUERTE

        elif agente.estado == EstadoAgente.MUERTE:
            resultado["acciones"].append("💀 Agente muerto, reciclando ADN")
            self._reciclar_agente(agente)
            agente.estado = EstadoAgente.RECICLAJE

        resultado["estado_final"] = agente.estado.value
        return resultado

    def _heredar_experiencia(self, tipo: str) -> Dict[str, Any]:
        """Hereda experiencia de la memoria compartida"""
        return self.memoria_compartida.get(tipo, {})

    async def _ejecutar_tarea(self, agente: ADNAgente) -> float:
        """Simula la ejecución de una tarea y retorna ingresos"""
        # Simulación: en producción, cada agente ejecuta su lógica real
        ingresos_base = agente.precio_base * 10  # 10 usos por ciclo
        return ingresos_base * agente.margen

    def _reciclar_agente(self, agente: ADNAgente) -> None:
        """Recicla el ADN del agente en la memoria compartida"""
        if agente.tipo not in self.memoria_compartida:
            self.memoria_compartida[agente.tipo] = {}

        self.memoria_compartida[agente.tipo][agente.id] = {
            "experiencia": agente.experiencia,
            "ingresos": agente.ingresos_generados,
            "clientes": agente.clientes_atendidos,
            "errores": agente.errores_cometidos,
            "mejoras": agente.mejoras_aplicadas
        }

        logger.info(f"♻️ Agente {agente.id} reciclado. Experiencia guardada.")

    async def run(self):
        """Loop principal del sistema operativo"""
        self.running = True
        logger.info("🔄 KIMI OS loop iniciado. Autonomía: 99%")

        while self.running:
            # Ejecutar ciclo para cada agente maduro
            for agente_id, agente in list(self.agentes.items()):
                if agente.estado in [EstadoAgente.CRECIMIENTO, EstadoAgente.MADUREZ]:
                    await self.ejecutar_ciclo(agente_id)

            # Reporte global cada hora
            logger.info(f"📊 KIMI OS: {len(self.agentes)} agentes, ${self.total_ingresos:.2f} ingresos")

            await asyncio.sleep(3600)  # Ciclo cada hora

    def detener(self):
        """Detiene el sistema operativo"""
        self.running = False
        logger.info("🛑 KIMI OS detenido")

class CicloVida:
    """Gestiona el ciclo de vida de los agentes"""

    def evaluar(self, agente: ADNAgente) -> EstadoAgente:
        """Evalúa si el agente debe cambiar de estado"""
        if agente.errores_cometidos > 100:
            return EstadoAgente.DECADENCIA
        if agente.ingresos_generados < 10 and agente.clientes_atendidos > 50:
            return EstadoAgente.DECADENCIA
        return agente.estado

# Instancia global del núcleo
nucleo = MotorAgentes()
