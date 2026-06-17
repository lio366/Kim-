"""
KIMI OS - AGENTE: CASHIER
Cobra, factura, entrega. El cajero automático.
Autonomía: 99%
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

class CashierAgente:
    """
    El cajero. Cobra por uso, genera facturas, envía API keys.
    Nunca olvida cobrar. Nunca cobra de más.
    """

    def __init__(self, nucleo, mercado):
        self.nucleo = nucleo
        self.mercado = mercado
        self.stripe = None  # Inicializado con credenciales
        self.facturas = []
        self.api_keys = {}

    async def cobrar(self, cliente: str, servicio: str, 
                     cantidad: int, precio_unitario: float) -> Dict[str, Any]:
        """
        Cobrar a un cliente por uso de API.
        """
        monto = cantidad * precio_unitario

        # 1. Generar factura
        factura = await self._generar_factura(cliente, servicio, cantidad, monto)

        # 2. Procesar pago (Stripe)
        pago = await self._procesar_pago(cliente, monto, factura["id"])

        if pago["exitoso"]:
            # 3. Generar/entregar API key
            api_key = await self._generar_api_key(cliente, servicio)

            # 4. Registrar en mercado interno
            self.mercado.depositar("kimi_os", monto * 0.30)
            self.mercado.depositar("creador", monto * 0.70)

            print(f"💰 Cashier: Cobrado ${monto:.2f} a {cliente} ({servicio})")

            return {
                "exitoso": True,
                "factura": factura,
                "api_key": api_key,
                "monto": monto
            }
        else:
            print(f"❌ Cashier: Pago fallido de {cliente}")
            return {"exitoso": False, "error": pago["error"]}

    async def _generar_factura(self, cliente: str, servicio: str,
                                cantidad: int, monto: float) -> Dict:
        """Generar factura automática"""
        factura = {
            "id": f"inv_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "cliente": cliente,
            "servicio": servicio,
            "cantidad": cantidad,
            "precio_unitario": monto / cantidad,
            "monto_total": monto,
            "fecha": datetime.now(),
            "estado": "generada"
        }
        self.facturas.append(factura)
        return factura

    async def _procesar_pago(self, cliente: str, monto: float, 
                             factura_id: str) -> Dict:
        """Procesar pago con Stripe"""
        # En producción: Stripe API real
        return {
            "exitoso": True,
            "transaction_id": f"tx_{factura_id}",
            "error": None
        }

    async def _generar_api_key(self, cliente: str, servicio: str) -> str:
        """Generar API key única"""
        import hashlib
        key = hashlib.sha256(f"{cliente}:{servicio}:{datetime.now()}".encode()).hexdigest()[:32]
        self.api_keys[cliente] = key
        return f"luz_sk_{key}"

    async def reporte_ingresos(self, periodo: str = "mes") -> Dict[str, Any]:
        """Generar reporte de ingresos"""
        facturas_periodo = [f for f in self.facturas 
                           if f["fecha"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]

        total = sum(f["monto_total"] for f in facturas_periodo)

        return {
            "periodo": periodo,
            "facturas_emitidas": len(facturas_periodo),
            "ingresos_totales": total,
            "promedio_factura": total / len(facturas_periodo) if facturas_periodo else 0,
            "clientes_activos": len(set(f["cliente"] for f in facturas_periodo))
        }
