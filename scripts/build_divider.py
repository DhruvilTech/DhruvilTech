import xml.etree.ElementTree as ET

def generate_perfect_divider():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 24" width="1200" height="24" role="img" aria-label="Professional Developer Animated Section Divider">
  <defs>
    <!-- 1. Base Gradient with userSpaceOnUse (Guarantees 100% perfect rendering across all browsers) -->
    <linearGradient id="lineGrad" gradientUnits="userSpaceOnUse" x1="60" y1="0" x2="1140" y2="0">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0"/>
      <stop offset="12%" stop-color="#22d3ee" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#a855f7" stop-opacity="0.95"/>
      <stop offset="88%" stop-color="#ff354f" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#ff354f" stop-opacity="0"/>
    </linearGradient>

    <!-- 2. Traveling Photon Beam Head (White hot center, cyan leading, purple trailing) -->
    <linearGradient id="beamHeadGrad" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="200" y2="0">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0"/>
      <stop offset="35%" stop-color="#22d3ee" stop-opacity="0.7"/>
      <stop offset="70%" stop-color="#ffffff" stop-opacity="1"/>
      <stop offset="90%" stop-color="#c084fc" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#a855f7" stop-opacity="0"/>
    </linearGradient>

    <!-- 3. Optical Sheen Filter -->
    <filter id="lineGlow" x="-20%" y="-200%" width="140%" height="500%">
      <feGaussianBlur stdDeviation="3.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="beamGlow" x="-30%" y="-300%" width="160%" height="700%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <style>
    /* Ultra-smooth hardware accelerated traveling light beam */
    .traveling-beam {
      animation: beamSweep 3.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    }
    .center-halo {
      animation: haloPulse 3s ease-in-out infinite;
    }
    .center-core {
      animation: coreShift 3.8s ease-in-out infinite alternate;
    }

    @keyframes beamSweep {
      0% {
        transform: translateX(40px);
        opacity: 0;
      }
      12% {
        opacity: 1;
      }
      88% {
        opacity: 1;
      }
      100% {
        transform: translateX(960px);
        opacity: 0;
      }
    }

    @keyframes haloPulse {
      0% {
        r: 3.5px;
        opacity: 0.8;
      }
      50% {
        r: 7.5px;
        opacity: 0.2;
      }
      100% {
        r: 3.5px;
        opacity: 0.8;
      }
    }

    @keyframes coreShift {
      0% {
        fill: #22d3ee;
      }
      50% {
        fill: #a855f7;
      }
      100% {
        fill: #ff354f;
      }
    }
  </style>

  <!-- 1. Ambient Background Glow Beam (Soft 6px aura) -->
  <rect x="60" y="9" width="1080" height="6" rx="3" fill="url(#lineGrad)" opacity="0.45" filter="url(#lineGlow)"/>

  <!-- 2. Crisp Razor-Sharp Developer Baseline (2px solid line, bright and visible) -->
  <rect x="60" y="11" width="1080" height="2" rx="1" fill="url(#lineGrad)"/>

  <!-- 3. Traveling Light Beam (Smooth 200px glowing pulse sweeping across the line) -->
  <g class="traveling-beam">
    <rect x="0" y="10" width="200" height="4" rx="2" fill="url(#beamHeadGrad)" filter="url(#beamGlow)"/>
    <ellipse cx="140" cy="12" rx="10" ry="2.5" fill="#ffffff" filter="url(#beamGlow)"/>
  </g>

  <!-- 4. Clean Minimalist Center Reticle (Linear / Vercel style) -->
  <!-- Pulsing ambient ring -->
  <circle cx="600" cy="12" r="4.5" fill="none" stroke="#a855f7" stroke-width="1.2" class="center-halo"/>

  <!-- Geometric precision diamond -->
  <polygon points="600,8 604,12 600,16 596,12" fill="#070b16" stroke="#c084fc" stroke-width="1.2"/>

  <!-- Central luminous core dot -->
  <circle cx="600" cy="12" r="1.8" class="center-core"/>
</svg>'''
    return svg

if __name__ == '__main__':
    svg_code = generate_perfect_divider()
    ET.fromstring(svg_code)
    with open('assets/section-divider.svg', 'w', encoding='utf-8') as f:
        f.write(svg_code)
    print("SAVED PERFECT DEVELOPER DIVIDER!")
