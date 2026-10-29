"""
Simulação em Tempo Real - Disseminação Cultural (Axelrod, 1997)
Interface Gráfica Interativa com Dashboard em Tempo Real

Características: Sexo, Período, Curso, Religião e Origem.

Para rodar:
  .venv/bin/python app_simulacao.py
ou
  python3 app_simulacao.py
"""

import http.server
import json
import os
import socketserver
import webbrowser

PORT = 8050

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Modelo de Axelrod - Disseminação Cultural</title>
  <style>
    :root {
      --bg-app: #0f172a;
      --bg-panel: #1e293b;
      --bg-subtle: #334155;
      --bg-input: #0f172a;
      --border: #334155;
      --border-light: #475569;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --danger: #ef4444;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-app);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.5;
    }

    header {
      background-color: var(--bg-panel);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .header-title h1 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-main);
    }

    .header-title p {
      font-size: 12px;
      color: var(--text-muted);
    }

    .status-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-muted);
      background: var(--bg-app);
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #64748b;
    }

    .status-dot.active { background: var(--primary); }
    .status-dot.stable { background: var(--success); }

    .main-layout {
      display: grid;
      grid-template-columns: 280px 1fr 300px;
      gap: 16px;
      padding: 16px 24px;
      max-width: 1600px;
      margin: 0 auto;
    }

    @media (max-width: 1200px) {
      .main-layout {
        grid-template-columns: 280px 1fr;
      }
      .right-column {
        grid-column: span 2;
      }
    }

    @media (max-width: 800px) {
      .main-layout {
        grid-template-columns: 1fr;
      }
      .right-column {
        grid-column: span 1;
      }
    }

    .card {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .card-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
    }

    .btn-group {
      display: flex;
      gap: 8px;
    }

    button {
      font-family: inherit;
      font-size: 13px;
      font-weight: 500;
      padding: 7px 12px;
      border-radius: 6px;
      border: 1px solid transparent;
      cursor: pointer;
      transition: background 0.15s, border-color 0.15s;
    }

    .btn-primary {
      background: var(--primary);
      color: #fff;
    }
    .btn-primary:hover { background: var(--primary-hover); }

    .btn-secondary {
      background: var(--bg-subtle);
      color: var(--text-main);
      border-color: var(--border-light);
    }
    .btn-secondary:hover { background: #475569; }

    .btn-outline {
      background: transparent;
      color: var(--text-muted);
      border-color: var(--border);
    }
    .btn-outline:hover {
      background: var(--bg-subtle);
      color: var(--text-main);
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-label {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-muted);
    }

    .form-value {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: var(--text-main);
    }

    input[type="range"] {
      width: 100%;
      accent-color: var(--primary);
    }

    select {
      width: 100%;
      padding: 6px 10px;
      background: var(--bg-input);
      border: 1px solid var(--border);
      color: var(--text-main);
      border-radius: 6px;
      font-size: 13px;
      outline: none;
    }

    select:focus {
      border-color: var(--primary);
    }

    .stats-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    .stats-table td {
      padding: 6px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stats-table td:last-child {
      text-align: right;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 600;
    }

    .stats-table tr:last-child td {
      border-bottom: none;
    }

    /* Center Visualizer */
    .center-column {
      display: flex;
      flex-direction: column;
      gap: 12px;
      align-items: center;
    }

    .nav-tabs {
      display: flex;
      gap: 4px;
      background: var(--bg-app);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border);
      width: 100%;
      max-width: 620px;
      overflow-x: auto;
    }

    .nav-tab {
      flex: 1;
      padding: 6px 10px;
      background: transparent;
      color: var(--text-muted);
      border: none;
      font-size: 12px;
      border-radius: 4px;
      white-space: nowrap;
    }

    .nav-tab.active {
      background: var(--bg-panel);
      color: var(--text-main);
      font-weight: 600;
      border: 1px solid var(--border);
    }

    .canvas-container {
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      display: inline-flex;
    }

    canvas#gridCanvas {
      display: block;
      cursor: crosshair;
    }

    .inspector-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }

    .inspector-table td {
      padding: 5px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .inspector-table td:first-child {
      color: var(--text-muted);
      width: 35%;
    }

    .inspector-table td:last-child {
      font-weight: 500;
      text-align: right;
    }

    .chart-box {
      width: 100%;
      height: 120px;
      background: var(--bg-input);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 6px;
    }

    canvas#chartCanvas {
      width: 100%;
      height: 100%;
    }

    .legend-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      max-height: 120px;
      overflow-y: auto;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      padding: 3px 6px;
      background: var(--bg-input);
      border: 1px solid var(--border);
      border-radius: 4px;
    }

    .legend-color {
      width: 10px;
      height: 10px;
      border-radius: 2px;
    }

    .hint-text {
      font-size: 11px;
      color: var(--text-muted);
      text-align: center;
    }
  </style>
</head>
<body>

  <header>
    <div class="header-title">
      <h1>Disseminação Cultural — Modelo de Axelrod (1997)</h1>
      <p>5 Características: Sexo, Período, Curso, Religião e Origem</p>
    </div>
    <div class="status-indicator">
      <div class="status-dot active" id="statusDot"></div>
      <span id="statusLabel">Executando</span>
    </div>
  </header>

  <div class="main-layout">
    
    <!-- Painel Esquerdo: Controles e Parâmetros -->
    <div class="card">
      <div class="card-title">Controles</div>

      <div class="btn-group">
        <button class="btn-primary" style="flex:1" id="btnPlayPause">Pausar</button>
        <button class="btn-secondary" style="flex:1" id="btnStep">+100 passos</button>
      </div>
      <button class="btn-outline" id="btnReset">Reiniciar População</button>

      <div class="card-title" style="margin-top: 8px;">Parâmetros</div>

      <div class="form-group">
        <div class="form-label">
          <span>Velocidade</span>
          <span class="form-value" id="valSpeed">200 / frame</span>
        </div>
        <input type="range" id="sliderSpeed" min="1" max="1000" step="5" value="200" />
      </div>

      <div class="form-group">
        <div class="form-label">
          <span>Tamanho da Grade</span>
          <span class="form-value" id="valSize">12 x 12 (144)</span>
        </div>
        <input type="range" id="sliderSize" min="5" max="25" step="1" value="12" />
      </div>

      <div class="form-group">
        <div class="form-label"><span>Vizinhança</span></div>
        <select id="selectNeighborhood">
          <option value="4" selected>Von Neumann (4 vizinhos)</option>
          <option value="8">Moore (8 vizinhos)</option>
        </select>
      </div>

      <div class="card-title" style="margin-top: 8px;">Estatísticas Globais</div>
      <table class="stats-table">
        <tr>
          <td>Eventos</td>
          <td id="statEvents">0</td>
        </tr>
        <tr>
          <td>Regiões Culturais</td>
          <td id="statRegions">0</td>
        </tr>
        <tr>
          <td>Zonas Culturais</td>
          <td id="statZones">0</td>
        </tr>
        <tr>
          <td>Similaridade Média</td>
          <td id="statSim">0.0%</td>
        </tr>
      </table>
    </div>

    <!-- Painel Central: Grade e Visualização -->
    <div class="center-column">
      <div class="nav-tabs">
        <button class="nav-tab active" data-view="regions">Regiões</button>
        <button class="nav-tab" data-view="curso">Curso</button>
        <button class="nav-tab" data-view="religiao">Religião</button>
        <button class="nav-tab" data-view="origem">Origem</button>
        <button class="nav-tab" data-view="periodo">Período</button>
        <button class="nav-tab" data-view="sexo">Sexo</button>
        <button class="nav-tab" data-view="borders">Bordas (Axelrod)</button>
      </div>

      <div class="canvas-container">
        <canvas id="gridCanvas" width="460" height="460"></canvas>
      </div>

      <p class="hint-text">Passe o cursor sobre a grade para visualizar os dados de cada sítio no painel lateral.</p>
    </div>

    <!-- Painel Direito: Inspetor e Gráfico -->
    <div class="card right-column">
      <div class="card-title" id="inspectorHeader">Indivíduo (0, 0)</div>
      
      <table class="inspector-table">
        <tr>
          <td>Sexo</td>
          <td id="inspSexo">-</td>
        </tr>
        <tr>
          <td>Período</td>
          <td id="inspPeriodo">-</td>
        </tr>
        <tr>
          <td>Curso</td>
          <td id="inspCurso">-</td>
        </tr>
        <tr>
          <td>Religião</td>
          <td id="inspReligiao">-</td>
        </tr>
        <tr>
          <td>Origem</td>
          <td id="inspOrigem">-</td>
        </tr>
        <tr>
          <td>Sim. Vizinhos</td>
          <td id="inspVizSim">-</td>
        </tr>
      </table>

      <div class="card-title" style="margin-top: 8px;">Convergência Temporal</div>
      <div class="chart-box">
        <canvas id="chartCanvas" width="280" height="110"></canvas>
      </div>

      <div class="card-title" style="margin-top: 8px;">Legenda</div>
      <div class="legend-list" id="legendBox"></div>
    </div>

  </div>

  <script>
    const CARACTERISTICAS = {
      sexo: {
        nome: "Sexo",
        tracos: ["Masculino", "Feminino", "Outro"],
        cores: ["#38bdf8", "#f472b6", "#a78bfa"]
      },
      periodo: {
        nome: "Período",
        tracos: ["1º", "2º", "3º", "4º", "5º", "6º", "7º", "8º", "9º", "10º"],
        cores: ["#f87171", "#fb923c", "#facc15", "#a3e635", "#4ade80", "#34d399", "#2dd4bf", "#38bdf8", "#818cf8", "#c084fc"]
      },
      curso: {
        nome: "Curso",
        tracos: [
          "Ciência da Computação",
          "Sistemas de Informação",
          "Engenharia Civil",
          "Engenharia Elétrica",
          "Direito",
          "Medicina",
          "Administração",
          "Agronomia",
          "Pedagogia"
        ],
        cores: ["#38bdf8", "#60a5fa", "#818cf8", "#a78bfa", "#e879f9", "#fb7185", "#34d399", "#facc15", "#fb923c"]
      },
      religiao: {
        nome: "Religião",
        tracos: [
          "Católica",
          "Evangélica",
          "Espírita",
          "Matriz Africana",
          "Outra",
          "Sem religião / Ateu"
        ],
        cores: ["#facc15", "#60a5fa", "#c084fc", "#f472b6", "#fb923c", "#94a3b8"]
      },
      origem: {
        nome: "Origem",
        tracos: [
          "Palmas",
          "Gurupi",
          "Araguaína",
          "Porto Nacional",
          "Outro município",
          "Outro estado"
        ],
        cores: ["#4ade80", "#2dd4bf", "#38bdf8", "#818cf8", "#f472b6", "#fb923c"]
      }
    };

    const CHAVES = Object.keys(CARACTERISTICAS);
    const F = CHAVES.length;

    let L = 12;
    let grid = [];
    let events = 0;
    let isRunning = true;
    let speed = 200;
    let neighborhood = 4;
    let currentView = "regions";
    let hoveredCell = { x: 0, y: 0 };
    let historyData = { events: [], regions: [], zones: [] };
    let isStable = false;

    const colorCache = new Map();
    function getCultureColor(traits) {
      const key = traits.join(",");
      if (colorCache.has(key)) return colorCache.get(key);
      let hash = 0;
      for (let i = 0; i < traits.length; i++) {
        hash = (hash * 37 + traits[i] + 11) % 360;
      }
      const h = (hash * 137.5) % 360;
      const color = `hsl(${h}, 65%, 55%)`;
      colorCache.set(key, color);
      return color;
    }

    function initGrid() {
      grid = [];
      events = 0;
      isStable = false;
      historyData = { events: [], regions: [], zones: [] };
      colorCache.clear();

      for (let x = 0; x < L; x++) {
        grid[x] = [];
        for (let y = 0; y < L; y++) {
          const traits = [];
          for (let f = 0; f < F; f++) {
            const numOptions = CARACTERISTICAS[CHAVES[f]].tracos.length;
            traits.push(Math.floor(Math.random() * numOptions));
          }
          grid[x][y] = traits;
        }
      }

      updateStatus(true);
      updateMetrics();
      updateInspector();
      updateLegend();
    }

    function getNeighbors(x, y) {
      const list = [];
      const deltas = neighborhood === 4 
        ? [[-1, 0], [1, 0], [0, -1], [0, 1]]
        : [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [-1, 1], [1, -1], [1, 1]];

      for (const [dx, dy] of deltas) {
        const nx = x + dx, ny = y + dy;
        if (nx >= 0 && nx < L && ny >= 0 && ny < L) {
          list.push({ x: nx, y: ny });
        }
      }
      return list;
    }

    function getSimilarity(traitsA, traitsB) {
      let matches = 0;
      for (let i = 0; i < F; i++) {
        if (traitsA[i] === traitsB[i]) matches++;
      }
      return matches / F;
    }

    function simulateEvents(numEvents) {
      if (isStable) return;

      for (let step = 0; step < numEvents; step++) {
        events++;
        const x = Math.floor(Math.random() * L);
        const y = Math.floor(Math.random() * L);
        const neighbors = getNeighbors(x, y);
        const neighbor = neighbors[Math.floor(Math.random() * neighbors.length)];

        const activeTraits = grid[x][y];
        const neighborTraits = grid[neighbor.x][neighbor.y];
        const sim = getSimilarity(activeTraits, neighborTraits);

        if (Math.random() < sim) {
          const diffFeatures = [];
          for (let f = 0; f < F; f++) {
            if (activeTraits[f] !== neighborTraits[f]) diffFeatures.push(f);
          }
          if (diffFeatures.length > 0) {
            const chosenF = diffFeatures[Math.floor(Math.random() * diffFeatures.length)];
            activeTraits[chosenF] = neighborTraits[chosenF];
          }
        }
      }

      if (events % (L * L * 5) < numEvents) {
        checkStability();
      }
    }

    function checkStability() {
      let canInteract = false;
      for (let x = 0; x < L; x++) {
        for (let y = 0; y < L; y++) {
          for (const n of getNeighbors(x, y)) {
            const sim = getSimilarity(grid[x][y], grid[n.x][n.y]);
            if (sim > 0 && sim < 1) {
              canInteract = true;
              break;
            }
          }
          if (canInteract) break;
        }
        if (canInteract) break;
      }

      if (!canInteract && !isStable) {
        isStable = true;
        updateStatus(false, true);
      }
    }

    function countComponents(predicate) {
      const visited = Array.from({ length: L }, () => Array(L).fill(false));
      let count = 0;

      for (let x = 0; x < L; x++) {
        for (let y = 0; y < L; y++) {
          if (visited[x][y]) continue;
          count++;
          const queue = [{ x, y }];
          visited[x][y] = true;

          while (queue.length > 0) {
            const curr = queue.shift();
            for (const n of getNeighbors(curr.x, curr.y)) {
              if (!visited[n.x][n.y] && predicate(grid[curr.x][curr.y], grid[n.x][n.y])) {
                visited[n.x][n.y] = true;
                queue.push(n);
              }
            }
          }
        }
      }
      return count;
    }

    const canvas = document.getElementById("gridCanvas");
    const ctx = canvas.getContext("2d");

    function renderGrid() {
      const size = canvas.width;
      const cellW = size / L;
      const cellH = size / L;

      ctx.clearRect(0, 0, size, size);

      for (let x = 0; x < L; x++) {
        for (let y = 0; y < L; y++) {
          const traits = grid[x][y];
          const px = x * cellW;
          const py = y * cellH;

          if (currentView === "regions") {
            ctx.fillStyle = getCultureColor(traits);
            ctx.fillRect(px, py, cellW, cellH);
          } else if (currentView === "borders") {
            ctx.fillStyle = "#1e293b";
            ctx.fillRect(px, py, cellW, cellH);
          } else {
            const fIdx = CHAVES.indexOf(currentView);
            const traitVal = traits[fIdx];
            const color = CARACTERISTICAS[currentView].cores[traitVal % CARACTERISTICAS[currentView].cores.length];
            ctx.fillStyle = color;
            ctx.fillRect(px, py, cellW, cellH);
          }

          ctx.strokeStyle = "rgba(0, 0, 0, 0.35)";
          ctx.lineWidth = 1;
          ctx.strokeRect(px, py, cellW, cellH);

          if (currentView === "borders") {
            const borders = [
              { dx: 1, dy: 0, x1: px + cellW, y1: py, x2: px + cellW, y2: py + cellH },
              { dx: 0, dy: 1, x1: px, y1: py + cellH, x2: px + cellW, y2: py + cellH }
            ];
            for (const b of borders) {
              const nx = x + b.dx, ny = y + b.dy;
              if (nx < L && ny < L) {
                const sim = getSimilarity(grid[x][y], grid[nx][ny]);
                if (sim < 1.0) {
                  ctx.lineWidth = sim === 0 ? 3 : 1;
                  ctx.strokeStyle = sim === 0 ? "#000000" : (sim >= 0.6 ? "#cbd5e1" : "#64748b");
                  ctx.beginPath();
                  ctx.moveTo(b.x1, b.y1);
                  ctx.lineTo(b.x2, b.y2);
                  ctx.stroke();
                }
              }
            }
          }
        }
      }

      if (hoveredCell.x >= 0 && hoveredCell.x < L && hoveredCell.y >= 0 && hoveredCell.y < L) {
        const hx = hoveredCell.x * cellW;
        const hy = hoveredCell.y * cellH;
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.strokeRect(hx + 1, hy + 1, cellW - 2, cellH - 2);
      }
    }

    const chartCanvas = document.getElementById("chartCanvas");
    const chartCtx = chartCanvas.getContext("2d");

    function renderChart() {
      const w = chartCanvas.width;
      const h = chartCanvas.height;
      chartCtx.clearRect(0, 0, w, h);

      if (historyData.events.length < 2) return;

      const maxVal = L * L;
      const maxPts = historyData.events.length;

      chartCtx.strokeStyle = "rgba(255, 255, 255, 0.08)";
      chartCtx.lineWidth = 1;
      chartCtx.beginPath();
      chartCtx.moveTo(0, h * 0.5); chartCtx.lineTo(w, h * 0.5);
      chartCtx.stroke();

      // Regiões (Azul claro)
      chartCtx.strokeStyle = "#38bdf8";
      chartCtx.lineWidth = 1.5;
      chartCtx.beginPath();
      for (let i = 0; i < maxPts; i++) {
        const cx = (i / (maxPts - 1)) * w;
        const cy = h - (historyData.regions[i] / maxVal) * (h - 8) - 4;
        if (i === 0) chartCtx.moveTo(cx, cy);
        else chartCtx.lineTo(cx, cy);
      }
      chartCtx.stroke();

      // Zonas (Amarelo)
      chartCtx.strokeStyle = "#facc15";
      chartCtx.lineWidth = 1.5;
      chartCtx.beginPath();
      for (let i = 0; i < maxPts; i++) {
        const cx = (i / (maxPts - 1)) * w;
        const cy = h - (historyData.zones[i] / maxVal) * (h - 8) - 4;
        if (i === 0) chartCtx.moveTo(cx, cy);
        else chartCtx.lineTo(cx, cy);
      }
      chartCtx.stroke();

      chartCtx.font = "10px sans-serif";
      chartCtx.fillStyle = "#38bdf8";
      chartCtx.fillText("Regiões", 6, 12);
      chartCtx.fillStyle = "#facc15";
      chartCtx.fillText("Zonas", 55, 12);
    }

    function updateMetrics() {
      const regions = countComponents((a, b) => getSimilarity(a, b) === 1.0);
      const zones = countComponents((a, b) => getSimilarity(a, b) > 0.0);

      let totalSim = 0, pairCount = 0;
      for (let x = 0; x < L; x++) {
        for (let y = 0; y < L; y++) {
          for (const n of getNeighbors(x, y)) {
            totalSim += getSimilarity(grid[x][y], grid[n.x][n.y]);
            pairCount++;
          }
        }
      }
      const avgSim = pairCount > 0 ? (totalSim / pairCount) * 100 : 0;

      document.getElementById("statEvents").textContent = events.toLocaleString();
      document.getElementById("statRegions").textContent = regions;
      document.getElementById("statZones").textContent = zones;
      document.getElementById("statSim").textContent = `${avgSim.toFixed(1)}%`;

      if (historyData.events.length === 0 || events - historyData.events[historyData.events.length - 1] >= 1000) {
        historyData.events.push(events);
        historyData.regions.push(regions);
        historyData.zones.push(zones);
        if (historyData.events.length > 120) {
          historyData.events.shift();
          historyData.regions.shift();
          historyData.zones.shift();
        }
        renderChart();
      }
    }

    function updateInspector() {
      const { x, y } = hoveredCell;
      if (x < 0 || x >= L || y < 0 || y >= L) return;

      const traits = grid[x][y];
      document.getElementById("inspectorHeader").textContent = `Indivíduo (${x}, ${y})`;
      document.getElementById("inspSexo").textContent = CARACTERISTICAS.sexo.tracos[traits[0]];
      document.getElementById("inspPeriodo").textContent = CARACTERISTICAS.periodo.tracos[traits[1]];
      document.getElementById("inspCurso").textContent = CARACTERISTICAS.curso.tracos[traits[2]];
      document.getElementById("inspReligiao").textContent = CARACTERISTICAS.religiao.tracos[traits[3]];
      document.getElementById("inspOrigem").textContent = CARACTERISTICAS.origem.tracos[traits[4]];

      const neighbors = getNeighbors(x, y);
      let simSum = 0;
      neighbors.forEach(n => simSum += getSimilarity(traits, grid[n.x][n.y]));
      const avg = (simSum / neighbors.length) * 100;
      document.getElementById("inspVizSim").textContent = `${avg.toFixed(0)}%`;
    }

    function updateLegend() {
      const box = document.getElementById("legendBox");
      box.innerHTML = "";

      if (currentView === "regions") {
        box.innerHTML = `<span style="font-size:11px; color: var(--text-muted);">Cores distintas para cada perfil cultural completo.</span>`;
      } else if (currentView === "borders") {
        box.innerHTML = `
          <div class="legend-item"><span class="legend-color" style="background:#000"></span> Incompatível (0%)</div>
          <div class="legend-item"><span class="legend-color" style="background:#64748b"></span> Parcial (20-60%)</div>
          <div class="legend-item"><span class="legend-color" style="background:#cbd5e1"></span> Alto (80%)</div>
        `;
      } else {
        const feat = CARACTERISTICAS[currentView];
        feat.tracos.forEach((traco, idx) => {
          const cor = feat.cores[idx % feat.cores.length];
          const item = document.createElement("div");
          item.className = "legend-item";
          item.innerHTML = `<span class="legend-color" style="background:${cor}"></span> ${traco}`;
          box.appendChild(item);
        });
      }
    }

    function updateStatus(running, stable = false) {
      const dot = document.getElementById("statusDot");
      const label = document.getElementById("statusLabel");

      dot.className = "status-dot";
      if (stable) {
        dot.classList.add("stable");
        label.textContent = "Estabilidade Alcançada";
      } else if (running) {
        dot.classList.add("active");
        label.textContent = "Executando";
      } else {
        label.textContent = "Pausado";
      }
    }

    function loop() {
      if (isRunning && !isStable) {
        simulateEvents(speed);
        updateMetrics();
      }
      renderGrid();
      requestAnimationFrame(loop);
    }

    document.getElementById("btnPlayPause").addEventListener("click", () => {
      isRunning = !isRunning;
      document.getElementById("btnPlayPause").textContent = isRunning ? "Pausar" : "Continuar";
      updateStatus(isRunning, isStable);
    });

    document.getElementById("btnStep").addEventListener("click", () => {
      simulateEvents(100);
      updateMetrics();
      renderGrid();
    });

    document.getElementById("btnReset").addEventListener("click", initGrid);

    document.getElementById("sliderSpeed").addEventListener("input", (e) => {
      speed = parseInt(e.target.value);
      document.getElementById("valSpeed").textContent = `${speed} / frame`;
    });

    document.getElementById("sliderSize").addEventListener("input", (e) => {
      L = parseInt(e.target.value);
      document.getElementById("valSize").textContent = `${L} x ${L} (${L * L})`;
      initGrid();
    });

    document.getElementById("selectNeighborhood").addEventListener("change", (e) => {
      neighborhood = parseInt(e.target.value);
    });

    document.querySelectorAll(".nav-tab").forEach(tab => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        currentView = tab.dataset.view;
        updateLegend();
        renderGrid();
      });
    });

    canvas.addEventListener("mousemove", (e) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = (e.clientX - rect.left) * (canvas.width / rect.width);
      const mouseY = (e.clientY - rect.top) * (canvas.height / rect.height);
      const cellX = Math.floor(mouseX / (canvas.width / L));
      const cellY = Math.floor(mouseY / (canvas.height / L));

      if (cellX >= 0 && cellX < L && cellY >= 0 && cellY < L) {
        if (hoveredCell.x !== cellX || hoveredCell.y !== cellY) {
          hoveredCell = { x: cellX, y: cellY };
          updateInspector();
        }
      }
    });

    initGrid();
    requestAnimationFrame(loop);
  </script>
</body>
</html>
"""

class SimulationServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # Silencia logs de requisições rotineiras
        pass


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SimulationServer) as httpd:
        url = f"http://localhost:{PORT}"
        print("=" * 70)
        print("🌐 INTERFACE DE SIMULAÇÃO EM TEMPO REAL INICIADA COM SUCESSO!")
        print("=" * 70)
        print(f"👉 Acesse no navegador: {url}")
        print("Características incluídas: Sexo, Período, Curso, Religião e Origem")
        print("Pressione Ctrl+C para encerrar o servidor.")
        print("=" * 70)
        
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")


if __name__ == "__main__":
    main()
