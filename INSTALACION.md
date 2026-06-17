# 📖 Guía de Instalación KIMI OS

## Paso 1: Preparar Cuentas (10 minutos)

### 1.1 Railway (Hosting)
1. Ve a https://railway.app
2. Crea cuenta con GitHub
3. Verifica email
4. Obtén $5 crédito gratis

### 1.2 Groq (Tokens IA)
1. Ve a https://console.groq.com
2. Crea cuenta
3. Genera API Key
4. Copia la key (empieza con `gsk_`)

### 1.3 Stripe (Pagos)
1. Ve a https://stripe.com
2. Crea cuenta
3. Activa modo test primero
4. Copia Secret Key (empieza con `sk_test_`)

### 1.4 Dominio (Opcional)
1. Ve a https://namecheap.com
2. Compra dominio ($12/año)
3. O usa subdominio Railway gratis

---

## Paso 2: Configurar Variables (5 minutos)

Crea archivo `.env`:
```
GROQ_API_KEY=gsk_tu_key_aqui
STRIPE_SECRET_KEY=sk_test_tu_key_aqui
DATABASE_URL=postgresql://kimi:password@localhost/kimi_os
REDIS_URL=redis://localhost:6379
SECRET_KEY=tu_secreto_seguro
```

---

## Paso 3: Deployar (5 minutos)

### Opción A: Railway (Recomendado)
```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Iniciar proyecto
railway init

# Subir código
railway up

# Obtener URL
railway domain
```

### Opción B: Docker Local
```bash
# Construir
docker-compose up -d

# Ver logs
docker logs -f kimi-os
```

---

## Paso 4: Verificar (2 minutos)

1. Abre tu URL
2. Verás el Dashboard
3. Los agentes empiezan a trabajar
4. En 1 hora: primera oportunidad detectada
5. En 2 horas: primera API construida

---

## Paso 5: Tu 1% (10 minutos/semana)

### Domingos:
1. Abre Dashboard
2. Revisa ingresos
3. Retira dinero de Stripe
4. Ajusta parámetros si quieres

### Listo.

La IA hace el resto.

---

## 🆘 Troubleshooting

| Problema | Solución |
|----------|----------|
| Agentes no inician | Verificar GROQ_API_KEY |
| No cobra | Verificar STRIPE_SECRET_KEY |
| No despliega | Verificar railway.json |
| Error en logs | Revisar `docker logs` |

---

## 📞 Soporte

- **IA**: Pregunta a los agentes en el dashboard
- **Humano**: Abre issue en GitHub
- **Tú**: Eres el CEO. La IA es el empleado.

---

**Tiempo total: 22 minutos**
**Costo: $5/mes**
**Retorno: $500-$25,000/mes**
