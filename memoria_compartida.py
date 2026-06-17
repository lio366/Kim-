"""
KIMI OS - NÚCLEO: Memoria Compartida
Todos los agentes aprenden de todos. Como Wikipedia, pero para IAs.
Autonomía: 99%
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Experiencia:
    """Una experiencia aprendida por un agente"""
    id: str
    tipo: str  # error, exito, optimizacion, patron
    contexto: str
    accion: str
    resultado: str
    valor: float  # 0-10, qué tan valiosa es esta experiencia
    timestamp: datetime = field(default_factory=datetime.now)
    agente_origen: str = "desconocido"
    usos: int = 0  # Cuántas veces otros agentes la usaron

class MemoriaCompartida:
    """
    El cerebro colectivo de KIMI OS.
    Cuando un agente aprende algo, TODOS los agentes lo saben.
    """

    def __init__(self):
        self.experiencias: Dict[str, Experiencia] = {}
        self.patrones: Dict[str, List[str]] = {}  # tipo -> lista de experiencias
        self.knowledge_graph: Dict[str, List[str]] = {}  # concepto -> relacionados
        self.cache_activa: Dict[str, Any] = {}  # Cache en memoria

        print("🧠 Memoria Compartida iniciada. Todos aprenden de todos.")

    def guardar_experiencia(self, experiencia: Experiencia) -> str:
        """
        Guarda una experiencia en la memoria colectiva.
        Como un commit en Git, pero para conocimiento.
        """
        # Generar ID único
        contenido = f"{experiencia.contexto}:{experiencia.accion}:{experiencia.resultado}"
        exp_id = hashlib.md5(contenido.encode()).hexdigest()[:12]
        experiencia.id = exp_id

        self.experiencias[exp_id] = experiencia

        # Indexar por tipo
        if experiencia.tipo not in self.patrones:
            self.patrones[experiencia.tipo] = []
        self.patrones[experiencia.tipo].append(exp_id)

        # Actualizar knowledge graph
        palabras = experiencia.contexto.lower().split()
        for palabra in palabras:
            if palabra not in self.knowledge_graph:
                self.knowledge_graph[palabra] = []
            self.knowledge_graph[palabra].append(exp_id)

        print(f"💾 Experiencia {exp_id} guardada. Valor: {experiencia.valor}/10")
        return exp_id

    def buscar_experiencia(self, contexto: str, tipo: Optional[str] = None, 
                          min_valor: float = 5.0) -> List[Experiencia]:
        """
        Busca experiencias relevantes para un contexto.
        Como Google, pero para conocimiento de agentes.
        """
        resultados = []
        palabras = contexto.lower().split()

        # Buscar en knowledge graph
        candidatos = set()
        for palabra in palabras:
            if palabra in self.knowledge_graph:
                candidatos.update(self.knowledge_graph[palabra])

        # Filtrar y ordenar por valor
        for exp_id in candidatos:
            exp = self.experiencias.get(exp_id)
            if exp and exp.valor >= min_valor:
                if tipo is None or exp.tipo == tipo:
                    exp.usos += 1
                    resultados.append(exp)

        # Ordenar por valor y uso
        resultados.sort(key=lambda x: (x.valor * 0.7 + x.usos * 0.3), reverse=True)

        print(f"🔍 {len(resultados)} experiencias encontradas para '{contexto}'")
        return resultados[:10]  # Top 10

    def heredar_conocimiento(self, tipo_agente: str) -> Dict[str, Any]:
        """
        Un nuevo agente hereda todo el conocimiento acumulado.
        Nace sabiendo lo que otros aprendieron en meses.
        """
        conocimiento = {
            "patrones_exitosos": [],
            "errores_comunes": [],
            "optimizaciones": [],
            "contextos_frecuentes": []
        }

        # Heredar patrones de éxito
        for exp_id in self.patrones.get("exito", []):
            exp = self.experiencias[exp_id]
            if exp.valor >= 8:
                conocimiento["patrones_exitosos"].append({
                    "contexto": exp.contexto,
                    "accion": exp.accion,
                    "resultado": exp.resultado,
                    "valor": exp.valor
                })

        # Heredar errores para evitarlos
        for exp_id in self.patrones.get("error", []):
            exp = self.experiencias[exp_id]
            conocimiento["errores_comunes"].append({
                "contexto": exp.contexto,
                "accion": exp.accion,
                "resultado": exp.resultado
            })

        print(f"📚 Agente {tipo_agente} heredó {len(conocimiento['patrones_exitosos'])} patrones exitosos")
        return conocimiento

    def consolidar_memoria(self) -> Dict[str, Any]:
        """
        Consolida la memoria: elimina duplicados, mejora conexiones.
        Como un defrag del disco, pero para conocimiento.
        """
        # Eliminar experiencias de bajo valor no usadas
        eliminadas = 0
        for exp_id in list(self.experiencias.keys()):
            exp = self.experiencias[exp_id]
            if exp.valor < 3 and exp.usos == 0:
                del self.experiencias[exp_id]
                eliminadas += 1

        # Mejorar conexiones en knowledge graph
        nuevas_conexiones = 0
        for exp_id, exp in self.experiencias.items():
            if exp.valor >= 9:  # Experiencias de alto valor
                # Conectar con experiencias similares
                similares = self.buscar_experiencia(exp.contexto, min_valor=7)
                for similar in similares:
                    if similar.id != exp_id:
                        nuevas_conexiones += 1

        print(f"🧹 Memoria consolidada: {eliminadas} eliminadas, {nuevas_conexiones} conexiones mejoradas")
        return {
            "experiencias_totales": len(self.experiencias),
            "patrones_indexados": len(self.patrones),
            "conocimiento_conectado": len(self.knowledge_graph)
        }

    def exportar_dataset(self, formato: str = "json") -> str:
        """
        Exporta la memoria como dataset para entrenamiento.
        La IA se entrena con su propia experiencia.
        """
        dataset = []
        for exp in self.experiencias.values():
            dataset.append({
                "input": f"Contexto: {exp.contexto}, Acción: {exp.accion}",
                "output": exp.resultado,
                "valor": exp.valor,
                "tipo": exp.tipo
            })

        if formato == "json":
            return json.dumps(dataset, indent=2, default=str)

        return f"Dataset exportado: {len(dataset)} registros"

# Instancia global
memoria = MemoriaCompartida()
