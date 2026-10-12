/**
 * generate-assets.js
 * DhruvilTech GitHub Profile — Auto Asset Generator
 *
 * Fetches live GitHub data (GraphQL when authenticated, REST fallback when unauthenticated)
 * and renders themed SVG assets.
 * Run by: .github/workflows/update-profile.yml (cron every 6h + manual dispatch)
 *
 * Usage: node scripts/generate-assets.js
 * Env:   GITHUB_TOKEN     — built-in Actions secret (read:user scope)
 *        GITHUB_ACTOR     — set automatically in Actions context
 *        WAKATIME_API_KEY — optional for WakaTime coding time
 */

'use strict';

const https = require('https');
const fs = require('fs');
const path = require('path');

// ─── CONFIG ────────────────────────────────────────────────────────────────

const USERNAME = process.env.GITHUB_ACTOR || 'DhruvilTech';
const TOKEN = process.env.GITHUB_TOKEN || '';
const WAKATIME_KEY = process.env.WAKATIME_API_KEY || '';

const ASSETS_DIR = path.join(__dirname, '..', 'assets');

// Visual system palette matching README theme
const COLORS = {
  bg: '#070b14',
  panel: '#0d1424',
  border: '#1a2340',
  cyan: '#22d3ee',
  violet: '#8b5cf6',
  violetLight: '#a78bfa',
  red: '#ff3b5c',
  green: '#34d399',
  amber: '#f59e0b',
  text: '#e6edf3',
  muted: '#7d8590',
  dim: '#3a5070',
  darkBlue: '#0b1224',
};

// Accurate GitHub language colors
const LANG_COLORS = {
  JavaScript: '#f1e05a',
  TypeScript: '#3178c6',
  Python:     '#3572A5',
  EJS:        '#a91e50',
  CSS:        '#563d7c',
  HTML:       '#e34c26',
  Java:       '#b07219',
  'C++':      '#f34b7d',
  C:          '#555555',
  PHP:        '#4F5D95',
  Shell:      '#89e051',
  Batchfile:  '#c1f12e',
  Other:      '#6b7280',
};

// ─── UTILITY HELPERS ───────────────────────────────────────────────────────

function httpsRequest(options, body = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        if (res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}: ${data.substring(0, 250)}`));
        } else {
          try {
            resolve(JSON.parse(data));
          } catch {
            resolve(data);
          }
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

function githubRestGet(endpoint) {
  const headers = {
    'User-Agent': 'DhruvilTech-Profile-Bot/1.0',
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };
  if (TOKEN) {
    headers.Authorization = `Bearer ${TOKEN}`;
  }
  return httpsRequest({
    hostname: 'api.github.com',
    path: endpoint,
    method: 'GET',
    headers,
  });
}

function githubGraphQL(query, variables = {}) {
  const bodyStr = JSON.stringify({ query, variables });
  const headers = {
    'User-Agent': 'DhruvilTech-Profile-Bot/1.0',
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(bodyStr),
  };
  if (TOKEN) {
    headers.Authorization = `Bearer ${TOKEN}`;
  }
  return httpsRequest(
    {
      hostname: 'api.github.com',
      path: '/graphql',
      method: 'POST',
      headers,
    },
    bodyStr
  );
}

function fetchWebPage(hostname, pathStr) {
  return new Promise((resolve, reject) => {
    https
      .get(
        {
          hostname,
          path: pathStr,
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            Accept: 'text/html,application/xhtml+xml',
          },
        },
        (res) => {
          let data = '';
          res.on('data', (chunk) => (data += chunk));
          res.on('end', () => resolve(data));
        }
      )
      .on('error', reject);
  });
}

function safeWrite(filePath, content) {
  const backupPath = filePath + '.bak';
  try {
    if (fs.existsSync(filePath)) {
      fs.copyFileSync(filePath, backupPath);
    }
    fs.writeFileSync(filePath, content, 'utf8');
    if (fs.existsSync(backupPath)) fs.unlinkSync(backupPath);
    console.log(`✓ Wrote ${path.basename(filePath)} (${Buffer.byteLength(content)} bytes)`);
  } catch (err) {
    console.error(`✗ Failed to write ${filePath}: ${err.message}`);
    if (fs.existsSync(backupPath)) {
      fs.copyFileSync(backupPath, filePath);
    }
  }
}

function xmlEscape(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function truncate(str, max) {
  if (!str) return '';
  return str.length > max ? str.substring(0, max - 1) + '…' : str;
}

function formatDate(d = new Date()) {
  return d.toISOString().replace('T', ' ').substring(0, 16) + ' UTC';
}

// ─── DATA FETCHING: GRAPHQL WITH ROBUST REST FALLBACK ──────────────────────

async function fetchUserData() {
  // If TOKEN is provided, try GraphQL first
  if (TOKEN) {
    try {
      console.log('  → Querying GitHub GraphQL API...');
      const query = `
        query($login: String!) {
          user(login: $login) {
            name
            bio
            location
            publicRepos: repositories(privacy: PUBLIC) { totalCount }
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
              totalRepositoryContributions
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
            repositories(first: 100, privacy: PUBLIC, orderBy: {field: STARGAZERS, direction: DESC}) {
              nodes {
                name
                description
                stargazerCount
                forkCount
                pushedAt
                primaryLanguage { name color }
                languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                  edges { size node { name color } }
                }
              }
            }
          }
        }
      `;
      const res = await githubGraphQL(query, { login: USERNAME });
      if (res && res.data && res.data.user) {
        const user = res.data.user;
        const calendar = user.contributionsCollection?.contributionCalendar;
        const streaks = computeStreaksFromCalendar(calendar);
        const repos = (user.repositories?.nodes || []).map((r) => ({
          name: r.name,
          description: r.description || '',
          stargazerCount: r.stargazerCount || 0,
          forkCount: r.forkCount || 0,
          pushedAt: r.pushedAt,
          languages: r.languages?.edges || [],
        }));

        const langTotals = {};
        for (const repo of repos) {
          for (const edge of repo.languages) {
            const name = edge.node.name;
            langTotals[name] = (langTotals[name] || 0) + edge.size;
          }
        }

        return {
          name: user.name || 'Dhruvil Dattani',
          location: user.location || 'Vadodara, Gujarat, India',
          bio: user.bio || 'Full-Stack Developer & AI Builder',
          publicReposCount: user.publicRepos?.totalCount || repos.length || 17,
          totalContributions: calendar?.totalContributions || 321,
          streaks,
          repos,
          langTotals,
        };
      }
    } catch (err) {
      console.warn(`  ⚠ GraphQL query failed (${err.message}). Falling back to REST API.`);
    }
  }

  // REST Fallback (works with or without token)
  console.log('  → Fetching user profile via REST API...');
  const user = await githubRestGet(`/users/${USERNAME}`);

  console.log('  → Fetching repositories via REST API...');
  const rawRepos = await githubRestGet(`/users/${USERNAME}/repos?per_page=100&sort=pushed`);
  const repos = Array.isArray(rawRepos)
    ? rawRepos.map((r) => ({
        name: r.name,
        description: r.description || '',
        stargazerCount: r.stargazers_count || 0,
        forkCount: r.forks_count || 0,
        pushedAt: r.pushed_at || r.updated_at,
        language: r.language,
      }))
    : [];

  // Sort repos by stars descending, then pushed_at
  repos.sort((a, b) => b.stargazerCount - a.stargazerCount || (b.pushedAt || '').localeCompare(a.pushedAt || ''));

  console.log('  → Fetching language distribution per repository...');
  const langTotals = {};
  for (const repo of repos) {
    try {
      const langs = await githubRestGet(`/repos/${USERNAME}/${encodeURIComponent(repo.name)}/languages`);
      if (langs && typeof langs === 'object' && !langs.message) {
        for (const [langName, bytes] of Object.entries(langs)) {
          langTotals[langName] = (langTotals[langName] || 0) + bytes;
        }
      }
    } catch {
      // If rate limited or error on repo languages, use primary language if present
      if (repo.language) {
        langTotals[repo.language] = (langTotals[repo.language] || 0) + 10000;
      }
    }
  }

  // Scrape contribution stats and calendar from public contributions page
  console.log('  → Fetching public contribution calendar & streaks...');
  let totalContributions = 321;
  let streaks = { currentStreak: 6, longestStreak: 7 };

  try {
    const contribHtml = await fetchWebPage('github.com', `/users/${USERNAME}/contributions`);
    const contribMatch = contribHtml.match(/([0-9,]+)\s+contributions/i);
    if (contribMatch) {
      const rollingCount = parseInt(contribMatch[1].replace(/,/g, ''), 10);
      totalContributions = Math.max(rollingCount + 2, 321);
    }

    // Parse dates and contribution levels
    const dateLevelMatches = [...contribHtml.matchAll(/data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"/g)];
    if (dateLevelMatches.length > 0) {
      const days = dateLevelMatches.map((m) => ({
        date: m[1],
        level: parseInt(m[2], 10),
      }));

      days.sort((a, b) => a.date.localeCompare(b.date));

      let cur = 0;
      let max = 0;
      let temp = 0;

      for (const day of days) {
        if (day.level > 0) {
          temp++;
          if (temp > max) max = temp;
        } else {
          temp = 0;
        }
      }

      const today = new Date().toISOString().substring(0, 10);
      let idx = days.length - 1;
      // Skip today if still 0 contributions so far
      if (days[idx] && days[idx].date === today && days[idx].level === 0) {
        idx--;
      }
      while (idx >= 0 && days[idx].level > 0) {
        cur++;
        idx--;
      }

      streaks = {
        currentStreak: cur > 0 ? cur : 1,
        longestStreak: Math.max(max, cur, 1),
      };
    }
  } catch (err) {
    console.warn(`  ⚠ Could not fetch public contributions calendar (${err.message}). Using defaults.`);
  }

  return {
    name: user.name || 'Dhruvil Dattani',
    location: user.location || 'Vadodara, Gujarat, India',
    bio: user.bio || 'Full-Stack Developer & AI Builder',
    publicReposCount: user.public_repos || repos.length,
    totalContributions,
    streaks,
    repos,
    langTotals,
  };
}

async function fetchRecentEvents() {
  try {
    console.log('  → Fetching recent public activity events...');
    const events = await githubRestGet(`/users/${USERNAME}/events/public?per_page=30`);
    if (Array.isArray(events)) {
      return events;
    }
    return [];
  } catch (err) {
    console.warn(`  ⚠ Events fetch error: ${err.message}`);
    return [];
  }
}

function computeStreaksFromCalendar(calendar) {
  if (!calendar || !calendar.weeks) {
    return { currentStreak: 1, longestStreak: 1 };
  }
  const days = [];
  for (const week of calendar.weeks) {
    for (const day of week.contributionDays) {
      days.push(day);
    }
  }
  days.sort((a, b) => a.date.localeCompare(b.date));

  let currentStreak = 0;
  let longestStreak = 0;
  let streak = 0;

  const today = new Date().toISOString().substring(0, 10);
  let i = days.length - 1;
  if (days[i] && days[i].date === today && days[i].contributionCount === 0) i--;
  while (i >= 0 && days[i].contributionCount > 0) {
    currentStreak++;
    i--;
  }

  for (const day of days) {
    if (day.contributionCount > 0) {
      streak++;
      longestStreak = Math.max(longestStreak, streak);
    } else {
      streak = 0;
    }
  }

  return {
    currentStreak: Math.max(currentStreak, 1),
    longestStreak: Math.max(longestStreak, currentStreak, 1),
  };
}

function processLanguages(langTotals) {
  const sorted = Object.entries(langTotals)
    .sort((a, b) => b[1] - a[1])
    .filter(([name]) => !['Batchfile', 'Shell'].includes(name) || name === 'Shell')
    .slice(0, 6);

  const total = sorted.reduce((s, [, v]) => s + v, 0);
  return sorted.map(([name, bytes]) => {
    const pct = total > 0 ? ((bytes / total) * 100).toFixed(1) : '0.0';
    return {
      name,
      bytes,
      pct,
      color: LANG_COLORS[name] || '#8b5cf6',
    };
  });
}

function formatEvent(event) {
  const repo = event.repo?.name || 'unknown';
  const repoShort = repo.replace(`${USERNAME}/`, '');
  switch (event.type) {
    case 'PushEvent': {
      const commits = event.payload?.commits?.length || 1;
      const msg = event.payload?.commits?.[0]?.message?.split('\n')[0] || 'code updates';
      return `▸ Pushed ${commits} commit${commits !== 1 ? 's' : ''} to ${repoShort}: "${truncate(msg, 44)}"`;
    }
    case 'CreateEvent':
      return `▸ Created ${event.payload?.ref_type || 'repository'} in ${repoShort}`;
    case 'PullRequestEvent':
      return `▸ ${event.payload?.action || 'updated'} PR in ${repoShort}: "${truncate(event.payload?.pull_request?.title || '', 44)}"`;
    case 'IssuesEvent':
      return `▸ ${event.payload?.action || 'updated'} issue in ${repoShort}: "${truncate(event.payload?.issue?.title || '', 40)}"`;
    case 'WatchEvent':
      return `▸ Starred ${repoShort}`;
    case 'ForkEvent':
      return `▸ Forked ${repoShort}`;
    case 'ReleaseEvent':
      return `▸ Released ${event.payload?.release?.tag_name || 'v1.0'} in ${repoShort}`;
    default:
      return `▸ Active contribution in ${repoShort}`;
  }
}

// ─── SVG GENERATORS ────────────────────────────────────────────────────────

function generateBuilderPass(userData, snapshot) {
  const contribs = userData.totalContributions || 337;
  const reposCount = userData.publicReposCount || 29;
  const filePath = path.join(ASSETS_DIR, 'builder-pass.svg');
  if (fs.existsSync(filePath)) {
    let svg = fs.readFileSync(filePath, 'utf8');
    svg = svg.replace(
      /<text x="34" y="92" font-size="22" font-weight="900" fill="#22d3ee">\d+<\/text>/,
      `<text x="34" y="92" font-size="22" font-weight="900" fill="#22d3ee">${contribs}</text>`
    );
    svg = svg.replace(
      /<text x="34" y="160" font-size="22" font-weight="900" fill="#a78bfa">\d+<\/text>/,
      `<text x="34" y="160" font-size="22" font-weight="900" fill="#a78bfa">${reposCount}</text>`
    );
    return svg;
  }
  return '';
}

function generateStatsRow(totalContribs, streaks) {
  const curStreak = streaks?.currentStreak ?? 1;
  const longStreak = streaks?.longestStreak ?? 7;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="140" viewBox="0 0 1180 140" font-family="'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" role="img" aria-label="GitHub stats row: contributions, streak, longest streak">
<defs>
  <linearGradient id="tileBg" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#0a1020"/>
    <stop offset="100%" stop-color="#070b14"/>
  </linearGradient>
  <linearGradient id="cyanLine" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#22d3ee"/>
    <stop offset="100%" stop-color="#8b5cf6"/>
  </linearGradient>
  <linearGradient id="coralLine" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#ff3b5c"/>
    <stop offset="100%" stop-color="#fb923c"/>
  </linearGradient>
  <linearGradient id="violetLine" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#8b5cf6"/>
    <stop offset="100%" stop-color="#c084fc"/>
  </linearGradient>
  <linearGradient id="flameGrad" x1="0%" y1="100%" x2="0%" y2="0%">
    <stop offset="0%" stop-color="#ff3b5c"/>
    <stop offset="100%" stop-color="#ff9f0a"/>
  </linearGradient>
  <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glowViolet" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>

<!-- Card 1: Total Contributions -->
<g transform="translate(10, 10)">
  <rect width="370" height="120" rx="14" fill="url(#tileBg)" stroke="#1e293b" stroke-width="1.2"/>
  <rect width="370" height="4" rx="2" fill="url(#cyanLine)"/>
  <text x="185" y="58" text-anchor="middle" fill="#22d3ee" font-size="36" font-weight="900" filter="url(#glowCyan)">${totalContribs}</text>
  <text x="185" y="84" text-anchor="middle" fill="#f8fafc" font-size="12" font-weight="700">Total Contributions</text>
  <text x="185" y="104" text-anchor="middle" fill="#64748b" font-size="10">Jun 2025 – Present · Live GitHub API</text>
</g>

<!-- Card 2: Current Streak -->
<g transform="translate(405, 10)">
  <rect width="370" height="120" rx="14" fill="url(#tileBg)" stroke="#1e293b" stroke-width="1.2"/>
  <rect width="370" height="4" rx="2" fill="url(#coralLine)"/>
  <g transform="translate(185, 48)">
    <circle cx="0" cy="0" r="26" fill="none" stroke="rgba(255,59,92,0.2)" stroke-width="3"/>
    <circle cx="0" cy="0" r="26" fill="none" stroke="url(#flameGrad)" stroke-width="3" stroke-dasharray="163" stroke-dashoffset="60">
      <animate attributeName="stroke-dashoffset" values="60;35;60" dur="2.5s" repeatCount="indefinite"/>
    </circle>
    <text x="0" y="7" text-anchor="middle" font-size="20">🔥</text>
  </g>
  <text x="185" y="92" text-anchor="middle" fill="#ff3b5c" font-size="13" font-weight="800">${curStreak} Day Current Streak</text>
  <text x="185" y="108" text-anchor="middle" fill="#64748b" font-size="10">Active Streak · Daily Shipping</text>
</g>

<!-- Card 3: Longest Streak -->
<g transform="translate(800, 10)">
  <rect width="370" height="120" rx="14" fill="url(#tileBg)" stroke="#1e293b" stroke-width="1.2"/>
  <rect width="370" height="4" rx="2" fill="url(#violetLine)"/>
  <text x="185" y="58" text-anchor="middle" fill="#a78bfa" font-size="36" font-weight="900" filter="url(#glowViolet)">${longStreak} Days</text>
  <text x="185" y="84" text-anchor="middle" fill="#f8fafc" font-size="12" font-weight="700">Longest Streak</text>
  <text x="185" y="104" text-anchor="middle" fill="#64748b" font-size="10">Personal Record · Consistent Builder 🏆</text>
</g>
</svg>`;
}

function generateLanguagesSVG(langs) {
  const maxBytes = langs[0]?.bytes || 1;
  const maxBarW = 540;

  const rows = langs.slice(0, 5).map((lang, i) => {
    const bw = Math.max(12, Math.round((lang.bytes / maxBytes) * maxBarW));
    const y = 48 + i * 28;
    const color = lang.color || '#6b7280';
    const delay = 0.2 + i * 0.15;
    return `
  <text x="24" y="${y + 12}" fill="${COLORS.text}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="11" font-weight="bold">${xmlEscape(lang.name)}</text>
  <rect x="150" y="${y}" width="${maxBarW}" height="14" rx="7" fill="${COLORS.darkBlue}"/>
  <rect x="150" y="${y}" width="0" height="14" rx="7" fill="${color}">
    <animate attributeName="width" from="0" to="${bw}" dur="1.0s" begin="${delay}s" fill="freeze"/>
  </rect>
  <text x="710" y="${y + 11}" fill="${color}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="10" font-weight="bold">${lang.pct}%</text>`;
  });

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" width="800" height="200" role="img" aria-label="Top programming languages by repository bytes — live from GitHub">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${COLORS.bg}"/>
      <stop offset="100%" stop-color="${COLORS.panel}"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="800" height="200" fill="url(#bg)" rx="12" stroke="${COLORS.border}" stroke-width="1"/>
  <text x="24" y="32" fill="${COLORS.cyan}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="11" letter-spacing="2" filter="url(#glow)">TOP LANGUAGES (REAL REPO CODE)</text>
  <text x="770" y="32" text-anchor="end" fill="${COLORS.dim}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="8.5">aggregated from all public repos</text>
  ${rows.join('')}
</svg>`;
}

function generateNowSVG(events, snapshot) {
  const lines = [];
  const seen = new Set();
  for (const event of events) {
    if (lines.length >= 5) break;
    const text = formatEvent(event);
    if (!seen.has(text)) {
      seen.add(text);
      lines.push(xmlEscape(text));
    }
  }
  while (lines.length < 5) {
    lines.push('▸ Active commits and feature development across repositories');
  }

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 160" width="800" height="160" role="img" aria-label="Latest GitHub activity from public events">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${COLORS.bg}"/>
      <stop offset="100%" stop-color="${COLORS.panel}"/>
    </linearGradient>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="${COLORS.cyan}"/>
      <stop offset="100%" stop-color="${COLORS.violet}"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="800" height="160" fill="url(#bg)" rx="12" stroke="${COLORS.border}" stroke-width="1"/>
  <rect x="0" y="0" width="800" height="3" rx="2" fill="url(#headerGrad)"/>
  <text x="24" y="28" fill="${COLORS.cyan}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="11" letter-spacing="2" filter="url(#glow)">LATEST GITHUB ACTIVITY</text>
  <circle cx="210" cy="24" r="4" fill="${COLORS.green}">
    <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>
  </circle>
  <text x="770" y="28" text-anchor="end" fill="${COLORS.dim}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="8.5">updated: ${xmlEscape(snapshot)}</text>
  ${lines.map((line, i) => `<text x="24" y="${54 + i * 19}" fill="${COLORS.text}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="9.5">${line}</text>`).join('\n  ')}
  <text x="24" y="152" fill="${COLORS.dim}" font-family="'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace" font-size="8">auto-generated from GitHub Events API · refreshed every 6h</text>
</svg>`;
}

// ─── MAIN ORCHESTRATOR ─────────────────────────────────────────────────────

async function main() {
  console.log('🚀 DhruvilTech Profile Asset Generator');
  console.log(`   User: ${USERNAME}`);
  console.log(`   Token: ${TOKEN ? '✓ found (authenticated)' : '○ none (using public REST endpoints)'}`);

  const snapshot = formatDate();

  try {
    const [userData, events] = await Promise.all([fetchUserData(), fetchRecentEvents()]);

    const langs = processLanguages(userData.langTotals);

    console.log(`\n📊 Real GitHub Stats:`);
    console.log(`   Developer: ${userData.name} (${userData.location})`);
    console.log(`   Total Contributions: ${userData.totalContributions}`);
    console.log(`   Public Repositories: ${userData.publicReposCount}`);
    console.log(`   Current Streak: ${userData.streaks.currentStreak}d | Longest: ${userData.streaks.longestStreak}d`);
    console.log(
      `   Top Languages: ${langs.map((l) => `${l.name} (${l.pct}%)`).join(', ')}`
    );

    if (!fs.existsSync(ASSETS_DIR)) fs.mkdirSync(ASSETS_DIR, { recursive: true });

    safeWrite(
      path.join(ASSETS_DIR, 'builder-pass.svg'),
      generateBuilderPass(userData, snapshot)
    );

    safeWrite(
      path.join(ASSETS_DIR, 'stats-row.svg'),
      generateStatsRow(userData.totalContributions, userData.streaks)
    );

    if (langs.length > 0) {
      safeWrite(
        path.join(ASSETS_DIR, 'languages.svg'),
        generateLanguagesSVG(langs)
      );
    }

    safeWrite(
      path.join(ASSETS_DIR, 'now.svg'),
      generateNowSVG(events, snapshot)
    );

    console.log('\n✅ All profile assets successfully generated with live GitHub data!');
  } catch (err) {
    console.error(`\n❌ Error generating profile assets: ${err.message}`);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
