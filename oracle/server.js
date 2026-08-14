import dotenv from 'dotenv';
import express from 'express';
import { DaemonCore } from './daemon-core/orchestrator.js';

dotenv.config();

const app = express();
app.use(express.json({ limit: '50mb' }));

const daemon = new DaemonCore();

// API Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ORACLE_ONLINE', timestamp: new Date() });
});

app.get('/api/opportunities', (req, res) => {
  res.json({ opportunities: daemon.getOpportunities() });
});

app.get('/api/opportunities/pending', (req, res) => {
  res.json({ pending: daemon.getOpportunities('ready_for_approval') });
});

app.post('/api/execute/:opportunityId', async (req, res) => {
  try {
    const result = await daemon.executeTransaction(req.params.opportunityId, 'admin');
    res.json({ status: 'success', result });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/api/dashboard', async (req, res) => {
  res.json(await daemon.getDashboardStats());
});

app.get('/api/history', (req, res) => {
  res.json({ history: daemon.getExecutionHistory() });
});

app.get('/api/audit', (req, res) => {
  res.json(daemon.auditLogger.exportAuditReport());
});

const PORT = process.env.PORT || 4000;

const startServer = async () => {
  try {
    console.log('\n╔════════════════════════════════════════════════════════╗');
    console.log('║                                                        ║');
    console.log('║    🤖 THE SOVEREIGN ORACLE - INITIALIZING...        ║');
    console.log('║       Autonomous Revenue Generator v2.0              ║');
    console.log('║                                                        ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');

    await daemon.initialize();

    app.listen(PORT, () => {
      console.log('\n╔════════════════════════════════════════════════════════╗');
      console.log('║                                                        ║');
      console.log('║    ✅ SOVEREIGN ORACLE IS LIVE                       ║');
      console.log(`║    API: http://localhost:${PORT}                          ║`);
      console.log('║                                                        ║');
      console.log('║    🎯 THE HUNTER:       SCANNING 24/7               ║');
      console.log('║    ⚡ THE SYNTHESIZER:  READY TO EXECUTE            ║');
      console.log('║    🔮 THE MIRROR:      LISTENING                   ║');
      console.log('║                                                        ║');
      console.log('║    Status: AUTONOMOUS OPERATIONS ACTIVE              ║');
      console.log('║                                                        ║');
      console.log('╚════════════════════════════════════════════════════════╝\n');
    });
  } catch (error) {
    console.error('❌ INITIALIZATION FAILED:', error);
    process.exit(1);
  }
};

startServer();

export { app, daemon };
