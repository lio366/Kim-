"""
KIMI OS - NÚCLEO: Mercado Interno
Los agentes se contratan entre sí. Economía circular.
Autonomía: 99%
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TipoTransaccion(Enum):
    CONTRATACION = "contratacion"  # Agente A contrata Agente B
    PAGO = "pago"                   # Agente A paga a Agente B
    COMISION = "comision"           # KIMI OS cobra comisión
    TOKEN = "token"                 # Intercambio de tokens
    RECURSO = "recurso"             # Uso de recursos compartidos

@dataclass
class Transaccion:
    id: str
    tipo: TipoTransaccion
    emisor: str      # Agente que paga
    receptor: str    # Agente que recibe
    monto: float
    concepto: str
    timestamp: datetime
    estado: str = "completada"

class MercadoInterno:
    """
    La economía dentro de KIMI OS.
    Los agentes son empresas. Se contratan, pagan, cooperan.
    """

    def __init__(self):
        self.transacciones: List[Transaccion] = []
        self.saldos: Dict[str, float] = {}  # Agente -> saldo
        self.comision_kimi = 0.30  # 30% para KIMI OS
        self.historial_contratos: Dict[str, List[str]] = {}

        print("💰 Mercado Interno iniciado. Agentes se contratan entre sí.")

    async def contratar(self, contratista: str, contratado: str, 
                       servicio: str, precio: float) -> bool:
        """
        Agente A contrata Agente B para un servicio.
        Como Upwork, pero entre IAs.
        """
        # Verificar saldo
        saldo_contratista = self.saldos.get(contratista, 0)
        if saldo_contratista < precio:
            print(f"❌ {contratista} no tiene fondos para contratar a {contratado}")
            return False

        # Calcular comisión
        comision = precio * self.comision_kimi
        pago_real = precio - comision

        # Ejecutar transacción
        self.saldos[contratista] -= precio
        self.saldos[contratado] = self.saldos.get(contratado, 0) + pago_real
        self.saldos["kimi_os"] = self.saldos.get("kimi_os", 0) + comision

        # Registrar
        trans = Transaccion(
            id=f"tx_{len(self.transacciones)}_{datetime.now().strftime('%H%M%S')}",
            tipo=TipoTransaccion.CONTRATACION,
            emisor=contratista,
            receptor=contratado,
            monto=pago_real,
            concepto=servicio,
            timestamp=datetime.now()
        )
        self.transacciones.append(trans)

        # Registrar contrato
        if contratista not in self.historial_contratos:
            self.historial_contratos[contratista] = []
        self.historial_contratos[contratista].append(contratado)

        print(f"✅ {contratista} contrató a {contratado} por ${precio:.2f} ({servicio})")
        print(f"   💰 {contratado} recibe ${pago_real:.2f} | KIMI OS: ${comision:.2f}")
        return True

    def depositar(self, agente: str, monto: float) -> None:
        """Deposita fondos en un agente (desde ingresos externos)"""
        self.saldos[agente] = self.saldos.get(agente, 0) + monto
        print(f"💵 {agente} recibió ${monto:.2f} (ingreso externo)")

    def consultar_saldo(self, agente: str) -> float:
        return self.saldos.get(agente, 0)

    def ranking_agentes(self) -> List[Dict[str, Any]]:
        """Ranking de agentes por ingresos generados"""
        ranking = []
        for agente, saldo in self.saldos.items():
            if agente != "kimi_os":
                ranking.append({
                    "agente": agente,
                    "saldo": saldo,
                    "contratos": len(self.historial_contratos.get(agente, [])),
                    "eficiencia": saldo / max(len(self.historial_contratos.get(agente, [1])), 1)
                })

        ranking.sort(key=lambda x: x["saldo"], reverse=True)
        return ranking

    def reporte_economico(self) -> Dict[str, Any]:
        """Reporte completo de la economía interna"""
        total_circulacion = sum(self.saldos.values())
        total_comisiones = self.saldos.get("kimi_os", 0)

        return {
            "transacciones_totales": len(self.transacciones),
            "dinero_en_circulacion": total_circulacion,
            "comisiones_kimi_os": total_comisiones,
            "agentes_activos": len([a for a in self.saldos if a != "kimi_os"]),
            "transacciones_hoy": len([t for t in self.transacciones 
                                     if t.timestamp.date() == datetime.now().date()]),
            "top_agente": self.ranking_agentes()[0] if self.ranking_agentes() else None
        }

# Instancia global
mercado = MercadoInterno()
