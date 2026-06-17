"""
KIMI OS - DASHBOARD
Centro de control del ecosistema.
Ves todo desde una pantalla.
"""

from flask import Flask, render_template, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Datos simulados del ecosistema
ecosistema = {
    "agentes_activos": 8,
    "apis_construidas": 12,
    "clientes_atendidos": 47,
    "ingresos_totales": 2350.50,
    "tokens_vendidos": 45000,
    "transacciones_hoy": 1247,
    "uptime": 99.97,
    "autonomia": 99.7
}

agentes_status = [
    {"nombre": "Scout", "estado": "🟢 Activo", "tarea": "Escaneando Reddit, Twitter, LinkedIn", "ultima_accion": "2 min ago"},
    {"nombre": "Builder", "estado": "🟢 Activo", "tarea": "Construyendo API para restaurantes", "ultima_accion": "5 min ago"},
    {"nombre": "Token Master", "estado": "🟢 Activo", "tarea": "Comprando tokens Groq", "ultima_accion": "1 min ago"},
    {"nombre": "Deployer", "estado": "🟢 Activo", "tarea": "Desplegando API-Legal-ES", "ultima_accion": "3 min ago"},
    {"nombre": "Cashier", "estado": "🟢 Activo", "tarea": "Cobrando $49 a DentalPlus", "ultima_accion": "Just now"},
    {"nombre": "Promoter", "estado": "🟢 Activo", "tarea": "Post en LinkedIn, Twitter", "ultima_accion": "4 min ago"},
    {"nombre": "Optimizer", "estado": "🟢 Activo", "tarea": "Optimizando API-Medical-EN", "ultima_accion": "6 min ago"},
    {"nombre": "Replicator", "estado": "🟡 Esperando", "tarea": "Listo para colonizar Brasil", "ultima_accion": "10 min ago"}
]

mercados = [
    {"pais": "USA", "estado": "🟢 Activo", "apis": 3, "ingresos": 850.00, "clientes": 15},
    {"pais": "Mexico", "estado": "🟢 Activo", "apis": 2, "ingresos": 420.00, "clientes": 8},
    {"pais": "Brasil", "estado": "🟡 Gestionando", "apis": 0, "ingresos": 0, "clientes": 0},
    {"pais": "España", "estado": "🟢 Activo", "apis": 2, "ingresos": 380.00, "clientes": 7},
    {"pais": "India", "estado": "🟡 Gestionando", "apis": 0, "ingresos": 0, "clientes": 0},
    {"pais": "Colombia", "estado": "🟢 Activo", "apis": 1, "ingresos": 200.50, "clientes": 4}
]

@app.route("/")
def dashboard():
    return render_template("index.html", 
                          ecosistema=ecosistema,
                          agentes=agentes_status,
                          mercados=mercados,
                          timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "online",
        "autonomia": 99.7,
        "agentes": len(agentes_status),
        "apis_activas": ecosistema["apis_construidas"],
        "ingresos_hoy": 1247.00,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/agentes")
def api_agentes():
    return jsonify(agentes_status)

@app.route("/api/ingresos")
def api_ingresos():
    return jsonify({
        "hoy": 1247.00,
        "semana": 8234.50,
        "mes": 2350.50,
        "proyeccion_proximo_mes": 4500.00,
        "fuentes": {
            "suscripciones": 60,
            "transacciones": 25,
            "tokens": 10,
            "publicidad": 5
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
