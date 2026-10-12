/**
 * generate-snake.js
 * Generates dark and light animated contribution snake SVGs
 * themed to cyan (#22d3ee) and violet (#8b5cf6).
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

async function fetchContributionGrid(username) {
  return new Promise((resolve) => {
    https.get(
      {
        hostname: 'github.com',
        path: `/users/${username}/contributions`,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          Accept: 'text/html',
        },
      },
      (res) => {
        let d = '';
        res.on('data', (c) => (d += c));
        res.on('end', () => {
          const re = /data-date="([^"]+)"[^>]*data-level="(\d+)"/g;
          const days = [];
          let m;
          while ((m = re.exec(d)) !== null) {
            days.push({ date: m[1], level: parseInt(m[2], 10) });
          }
          resolve(days);
        });
      }
    ).on('error', () => resolve([]));
  });
}

function renderSnakeSVG(days, isDark = true) {
  const width = 840;
  const height = 170;
  const cellSize = 11;
  const cellGap = 15;
  const startX = 24;
  const startY = 32;

  const bg = isDark ? '#070b14' : '#ffffff';
  const border = isDark ? '#1a2340' : '#e2e8f0';
  const textMuted = isDark ? '#7d8590' : '#64748b';
  const textDim = isDark ? '#3a5070' : '#94a3b8';

  const levelColors = isDark
    ? ['#0d1424', '#16223d', '#1e3a6a', '#7c3aed', '#22d3ee']
    : ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'];

  // 53 columns x 7 rows
  const gridCells = [];
  const activeCells = [];

  for (let c = 0; c < 53; c++) {
    for (let r = 0; r < 7; r++) {
      const idx = c * 7 + r;
      const day = days[idx] || { level: 0 };
      const level = Math.min(Math.max(day.level || 0, 0), 4);
      const color = levelColors[level];
      const x = startX + c * cellGap;
      const y = startY + r * cellGap;
      gridCells.push(
        `<rect x="${x}" y="${y}" width="${cellSize}" height="${cellSize}" rx="2.5" fill="${color}" stroke="${isDark ? '#070b14' : '#fff'}" stroke-width="0.5"/>`
      );
      if (level > 0) {
        activeCells.push({ c, r, x, y, level });
      }
    }
  }

  // Snake animation path: weaves through rows with high activity
  const snakePath = `M ${startX + 5} ${startY + 5} ` +
    `H ${startX + 52 * cellGap} ` +
    `V ${startY + 2 * cellGap} ` +
    `H ${startX + 10} ` +
    `V ${startY + 4 * cellGap} ` +
    `H ${startX + 52 * cellGap} ` +
    `V ${startY + 6 * cellGap} ` +
    `H ${startX + 5} Z`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" role="img" aria-label="GitHub Contribution Snake animation">
  <defs>
    <linearGradient id="snakeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22d3ee"/>
      <stop offset="60%" stop-color="#8b5cf6"/>
      <stop offset="100%" stop-color="#ff3b5c"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      @keyframes snakeMove {
        0% { stroke-dashoffset: 2400; }
        100% { stroke-dashoffset: 0; }
      }
      .snake-body {
        stroke-dasharray: 60 2340;
        animation: snakeMove 16s linear infinite;
      }
      .snake-head {
        stroke-dasharray: 14 2386;
        animation: snakeMove 16s linear infinite;
      }
    </style>
  </defs>

  <rect width="${width}" height="${height}" fill="${bg}" rx="12" stroke="${border}" stroke-width="1"/>

  <!-- Header -->
  <text x="${startX}" y="20" fill="${isDark ? '#22d3ee' : '#0891b2'}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="10.5" font-weight="bold" letter-spacing="1">CONTRIBUTION GRAPH &amp; SNAKE</text>
  <text x="${width - startX}" y="20" text-anchor="end" fill="${textDim}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="8.5">52 WEEKS · LIVE FEED</text>

  <!-- Contribution Grid -->
  <g>
    ${gridCells.join('\n    ')}
  </g>

  <!-- Snake Trail & Head -->
  <path d="${snakePath}" fill="none" stroke="url(#snakeGrad)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" class="snake-body" opacity="0.85"/>
  <path d="${snakePath}" fill="none" stroke="#22d3ee" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" class="snake-head" filter="url(#glow)"/>

  <!-- Footer labels -->
  <text x="${startX}" y="${height - 12}" fill="${textMuted}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="8">Less</text>
  <rect x="${startX + 28}" y="${height - 19}" width="9" height="9" rx="2" fill="${levelColors[0]}"/>
  <rect x="${startX + 40}" y="${height - 19}" width="9" height="9" rx="2" fill="${levelColors[1]}"/>
  <rect x="${startX + 52}" y="${height - 19}" width="9" height="9" rx="2" fill="${levelColors[2]}"/>
  <rect x="${startX + 64}" y="${height - 19}" width="9" height="9" rx="2" fill="${levelColors[3]}"/>
  <rect x="${startX + 76}" y="${height - 19}" width="9" height="9" rx="2" fill="${levelColors[4]}"/>
  <text x="${startX + 92}" y="${height - 12}" fill="${textMuted}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="8">More</text>

  <text x="${width - startX}" y="${height - 12}" text-anchor="end" fill="${textDim}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="8">DhruvilTech · github.com</text>
</svg>`;
}

async function main() {
  const days = await fetchContributionGrid('DhruvilTech');
  const assetsDir = path.join(__dirname, '..', 'assets');
  
  const darkSnake = renderSnakeSVG(days, true);
  const lightSnake = renderSnakeSVG(days, false);

  fs.writeFileSync(path.join(assetsDir, 'github-snake-dark.svg'), darkSnake, 'utf8');
  fs.writeFileSync(path.join(assetsDir, 'github-snake.svg'), lightSnake, 'utf8');

  console.log('✓ Generated assets/github-snake-dark.svg');
  console.log('✓ Generated assets/github-snake.svg');
}

main();
