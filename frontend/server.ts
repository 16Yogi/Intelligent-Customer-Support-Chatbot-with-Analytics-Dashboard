import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';

const METRICS_FILE = path.join(process.cwd(), 'metrics.json');

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Load metrics from file or initialize
  let metrics = {
    queryVolume: 0,
    successCount: 0,
    errorCount: 0,
    satisfactionScores: [] as number[],
    latencies: [] as number[],
  };

  if (fs.existsSync(METRICS_FILE)) {
    try {
      const data = fs.readFileSync(METRICS_FILE, 'utf-8');
      metrics = { ...metrics, ...JSON.parse(data) };
    } catch (e) {
      console.error('Failed to load metrics:', e);
    }
  }

  const saveMetrics = () => {
    try {
      fs.writeFileSync(METRICS_FILE, JSON.stringify(metrics, null, 2));
    } catch (e) {
      console.error('Failed to save metrics:', e);
    }
  };

  // API Routes
  app.get('/api/metrics', (req, res) => {
    const total = metrics.successCount + metrics.errorCount;
    const successRate = total > 0 ? (metrics.successCount / total) * 100 : 0;
    const avgSatisfaction = metrics.satisfactionScores.length > 0 
      ? metrics.satisfactionScores.reduce((a, b) => a + b, 0) / metrics.satisfactionScores.length 
      : 0;
    const avgLatency = metrics.latencies.length > 0
      ? metrics.latencies.reduce((a, b) => a + b, 0) / metrics.latencies.length
      : 0;

    res.json({
      queryVolume: metrics.queryVolume,
      successRate: successRate.toFixed(1),
      userSatisfaction: avgSatisfaction.toFixed(1),
      avgLatency: Math.round(avgLatency),
      history: [
        { name: 'Mon', queries: Math.floor(metrics.queryVolume * 0.1) },
        { name: 'Tue', queries: Math.floor(metrics.queryVolume * 0.2) },
        { name: 'Wed', queries: Math.floor(metrics.queryVolume * 0.3) },
        { name: 'Thu', queries: Math.floor(metrics.queryVolume * 0.4) },
        { name: 'Fri', queries: metrics.queryVolume },
      ]
    });
  });

  app.post('/api/metrics/track', (req, res) => {
    const { type, score, latency } = req.body;
    if (type === 'query') metrics.queryVolume++;
    if (type === 'success') metrics.successCount++;
    if (type === 'error') metrics.errorCount++;
    if (type === 'satisfaction' && typeof score === 'number') {
      metrics.satisfactionScores.push(score);
    }
    if (typeof latency === 'number') {
      metrics.latencies.push(latency);
    }
    saveMetrics();
    res.status(204).send();
  });

  // Force Vite dev mode in this environment unless explicitly production
  const isProd = process.env.NODE_ENV === 'production';
  
  if (!isProd) {
    console.log('Starting Vite in dev mode...');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    console.log('Starting in production mode...');
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
