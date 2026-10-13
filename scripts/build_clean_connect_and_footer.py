import base64
import cv2
import numpy as np
import xml.etree.ElementTree as ET

def build_clean_connect_hub():
    # Load and prepare portrait
    img = cv2.imread('assets/contact_portrait_blended.jpg')
    if img is None:
        raise ValueError("Could not read assets/contact_portrait_blended.jpg")
    
    # 360x360 portrait
    resized = cv2.resize(img, (360, 360), interpolation=cv2.INTER_AREA)
    _, buf = cv2.imencode('.jpg', resized, [cv2.IMWRITE_JPEG_QUALITY, 90])
    b64_portrait = base64.b64encode(buf).decode('ascii')
    portrait_data_uri = f"data:image/jpeg;base64,{b64_portrait}"

    # Viewbox: 1150 x 530
    # Left column: portrait center at cx=190, cy=200
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1150 530" width="1150" height="530" role="img" aria-label="Dhruvil Dattani - Transmission Protocol &amp; Direct Channels">
  <title>Dhruvil Dattani - Direct Transmission Protocol</title>
  <defs>
    <!-- Background Gradient (matching builder-pass.svg) -->
    <linearGradient id="hubBgClean" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a1022"/>
      <stop offset="50%" stop-color="#070b14"/>
      <stop offset="100%" stop-color="#050811"/>
    </linearGradient>

    <!-- Outer Border Gradient (matching builder-pass.svg hairline) -->
    <linearGradient id="hubBorderClean" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#247bff" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#567394" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#ff354f" stop-opacity="0.75"/>
    </linearGradient>

    <!-- Title Gradient for REAL IMPACT -->
    <linearGradient id="titleImpactGradClean" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ff354f"/>
      <stop offset="50%" stop-color="#f43f5e"/>
      <stop offset="100%" stop-color="#fb7185"/>
    </linearGradient>

    <!-- Channel Card Border Gradients -->
    <linearGradient id="cardGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#0284c7" stop-opacity="0.2"/>
    </linearGradient>
    <linearGradient id="cardGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#a78bfa" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#6366f1" stop-opacity="0.2"/>
    </linearGradient>
    <linearGradient id="cardGrad3" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ff354f" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#f43f5e" stop-opacity="0.2"/>
    </linearGradient>
    <linearGradient id="cardGrad4" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#c084fc" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.2"/>
    </linearGradient>

    <!-- Dot Pattern (exact builder-pass.svg stack-dots) -->
    <pattern id="hubDotsClean" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.7" fill="#99b1db" opacity="0.14"/>
    </pattern>

    <!-- Soft Glow Filter -->
    <filter id="softGlowClean" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Container Base -->
  <rect x="2" y="2" width="1146" height="526" rx="20" fill="url(#hubBgClean)" stroke="url(#hubBorderClean)" stroke-width="1.5"/>
  <rect x="2" y="2" width="1146" height="526" rx="20" fill="url(#hubDotsClean)"/>

  <!-- Cyber Corner Tech Ticks -->
  <path d="M2 18 L2 2 L18 2" fill="none" stroke="#22d3ee" stroke-width="2.5" opacity="0.9"/>
  <path d="M1148 508 L1148 526 L1130 526" fill="none" stroke="#ff354f" stroke-width="2.5" opacity="0.9"/>

  <!-- Top System Header Track (Matching builder-pass.svg hierarchy) -->
  <g transform="translate(42, 34)">
    <circle cx="5" cy="5" r="4" fill="#10b981">
      <animate attributeName="opacity" values="1;0.35;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="5" cy="5" r="7" fill="none" stroke="#10b981" stroke-width="1" opacity="0.5">
      <animate attributeName="r" values="5;10;5" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;0;0.7" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="20" y="9" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="900" fill="#22d3ee" letter-spacing="1.8">05 // TRANSMISSION PROTOCOL &amp; DIRECT CHANNELS</text>
  </g>

  <!-- ============================================================ -->
  <!-- LEFT COLUMN: PORTRAIT + CLEAN CONCENTRIC ANIMATED CYBER HUD  -->
  <!-- Center of portrait is at (190, 200) inside this group        -->
  <!-- ============================================================ -->
  <g transform="translate(44, 72)">

    <!-- [ANIMATION 1] Soft Breathing Halo Ring -->
    <circle cx="190" cy="200" r="176" fill="none" stroke="#22d3ee" stroke-width="1.4">
      <animate attributeName="r" values="176;186;176" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.6;0.1;0.6" dur="4s" repeatCount="indefinite"/>
    </circle>

    <!-- [ANIMATION 2] Concentric Rotating Cyber Arc 1 (Clockwise) -->
    <circle cx="190" cy="200" r="182" fill="none" stroke="#38bdf8" stroke-width="1.6" stroke-dasharray="80 180 40 120" opacity="0.75">
      <animateTransform attributeName="transform" type="rotate" from="0 190 200" to="360 190 200" dur="16s" repeatCount="indefinite"/>
    </circle>

    <!-- [ANIMATION 3] Concentric Counter-Rotating Tech Ticks 2 (Counter-Clockwise) -->
    <circle cx="190" cy="200" r="188" fill="none" stroke="#8b5cf6" stroke-width="1.2" stroke-dasharray="6 14" opacity="0.6">
      <animateTransform attributeName="transform" type="rotate" from="360 190 200" to="0 190 200" dur="22s" repeatCount="indefinite"/>
    </circle>

    <!-- [ANIMATION 4] Two Orbiting Micro-Beacons on the HUD Track (at r=182) -->
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0 190 200" to="360 190 200" dur="16s" repeatCount="indefinite"/>
      <!-- Cyan Beacon -->
      <circle cx="372" cy="200" r="4.5" fill="#22d3ee" filter="url(#softGlowClean)"/>
      <circle cx="372" cy="200" r="1.8" fill="#ffffff"/>
      <!-- Coral Opposite Beacon -->
      <circle cx="8" cy="200" r="4" fill="#ff354f" filter="url(#softGlowClean)"/>
      <circle cx="8" cy="200" r="1.6" fill="#ffffff"/>
    </g>

    <!-- Fixed Outer Tech Circular Frame -->
    <circle cx="190" cy="200" r="172" fill="none" stroke="#1e293b" stroke-width="1.2"/>

    <!-- Embedded Blended Portrait (r=168) -->
    <clipPath id="portClipClean">
      <circle cx="190" cy="200" r="168"/>
    </clipPath>
    <image href="{portrait_data_uri}" x="10" y="20" width="360" height="360" clip-path="url(#portClipClean)"/>

    <!-- Dark Vignette Guard Ring -->
    <circle cx="190" cy="200" r="169" fill="none" stroke="#070b14" stroke-width="6" opacity="0.85"/>
  </g>

  <!-- ============================================================ -->
  <!-- CENTER DIVIDER: MINIMALIST GUIDELINE                         -->
  <!-- ============================================================ -->
  <line x1="432" y1="78" x2="432" y2="486" stroke="#1e293b" stroke-width="1" stroke-dasharray="4 6" opacity="0.6"/>

  <!-- ============================================================ -->
  <!-- RIGHT COLUMN: BUILDER-PASS HEADLINE & STREAMLINED CHANNELS   -->
  <!-- ============================================================ -->
  <g transform="translate(468, 52)">

    <!-- MAIN PUNCHY HEADLINE (Exact style of builder-pass.svg right header) -->
    <text x="0" y="32" font-family="'Inter', -apple-system, sans-serif" font-size="32" font-weight="900" letter-spacing="-0.5">
      <tspan fill="#f2f5ff">LET'S ENGINEER </tspan>
      <tspan fill="url(#titleImpactGradClean)">REAL IMPACT.</tspan>
    </text>

    <!-- SUBHEADING (Matching builder-pass.svg font-size 13, letter-spacing 1.8, #8e9db9) -->
    <text x="0" y="55" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="800" fill="#8e9db9" letter-spacing="1.8">
      COLLABORATIONS // FULL-STACK SYSTEMS // AGENTIC AI
    </text>

    <!-- ========================================================== -->
    <!-- REDESIGNED CHANNELS: ZERO TEXT BLOAT · HIGH IMPACT         -->
    <!-- ========================================================== -->

    <!-- CHANNEL 1: PORTFOLIO -->
    <g transform="translate(0, 76)">
      <rect width="636" height="66" rx="12" fill="#0b1122" fill-opacity="0.85" stroke="url(#cardGrad1)" stroke-width="1.2"/>
      
      <!-- Icon Container (Cyan) -->
      <circle cx="36" cy="33" r="18" fill="#070b14" stroke="#38bdf8" stroke-width="1.2" stroke-opacity="0.6"/>
      <circle cx="36" cy="33" r="9" fill="none" stroke="#38bdf8" stroke-width="1.4"/>
      <ellipse cx="36" cy="33" rx="3.6" ry="9" fill="none" stroke="#38bdf8" stroke-width="1.1"/>
      <line x1="27" y1="33" x2="45" y2="33" stroke="#38bdf8" stroke-width="1.1"/>

      <!-- Clean Texts (2 crisp lines, no clutter) -->
      <text x="68" y="25" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="800" fill="#38bdf8" letter-spacing="1.5">01 // LIVE PORTFOLIO</text>
      <text x="68" y="47" font-family="'Inter', sans-serif" font-size="15" font-weight="700" fill="#f8fafc">dhruvildattani-portfolio.vercel.app</text>

      <!-- Action Chip -->
      <g transform="translate(546, 20)">
        <rect width="76" height="26" rx="6" fill="#38bdf8" fill-opacity="0.1" stroke="#38bdf8" stroke-width="1" stroke-opacity="0.6"/>
        <text x="38" y="17" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="10.5" font-weight="900" fill="#38bdf8">EXPLORE ↗</text>
      </g>
    </g>

    <!-- CHANNEL 2: LINKEDIN -->
    <g transform="translate(0, 154)">
      <rect width="636" height="66" rx="12" fill="#0b1122" fill-opacity="0.85" stroke="url(#cardGrad2)" stroke-width="1.2"/>
      
      <!-- Icon Container (Violet) -->
      <circle cx="36" cy="33" r="18" fill="#070b14" stroke="#a78bfa" stroke-width="1.2" stroke-opacity="0.6"/>
      <text x="36" y="39" text-anchor="middle" font-family="'Inter', sans-serif" font-size="14" font-weight="900" fill="#a78bfa">in</text>

      <!-- Clean Texts -->
      <text x="68" y="25" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="800" fill="#a78bfa" letter-spacing="1.5">02 // LINKEDIN NETWORK</text>
      <text x="68" y="47" font-family="'Inter', sans-serif" font-size="15" font-weight="700" fill="#f8fafc">in/dhruvil-dattani-b43599317</text>

      <!-- Action Chip -->
      <g transform="translate(546, 20)">
        <rect width="76" height="26" rx="6" fill="#a78bfa" fill-opacity="0.1" stroke="#a78bfa" stroke-width="1" stroke-opacity="0.6"/>
        <text x="38" y="17" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="10.5" font-weight="900" fill="#a78bfa">CONNECT ↗</text>
      </g>
    </g>

    <!-- CHANNEL 3: DIRECT EMAIL -->
    <g transform="translate(0, 232)">
      <rect width="636" height="66" rx="12" fill="#0b1122" fill-opacity="0.85" stroke="url(#cardGrad3)" stroke-width="1.2"/>
      
      <!-- Icon Container (Coral) -->
      <circle cx="36" cy="33" r="18" fill="#070b14" stroke="#ff354f" stroke-width="1.2" stroke-opacity="0.6"/>
      <path d="M27 27 L36 34 L45 27 M27 26 L45 26 L45 39 L27 39 Z" fill="none" stroke="#ff354f" stroke-width="1.4" stroke-linejoin="round"/>

      <!-- Clean Texts -->
      <text x="68" y="25" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="800" fill="#ff354f" letter-spacing="1.5">03 // PRIORITY INBOX</text>
      <text x="68" y="47" font-family="'Inter', sans-serif" font-size="15" font-weight="700" fill="#f8fafc">dhruvildattani9@gmail.com</text>

      <!-- Action Chip -->
      <g transform="translate(546, 20)">
        <rect width="76" height="26" rx="6" fill="#ff354f" fill-opacity="0.1" stroke="#ff354f" stroke-width="1" stroke-opacity="0.6"/>
        <text x="38" y="17" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="10.5" font-weight="900" fill="#ff354f">DISPATCH ↗</text>
      </g>
    </g>

    <!-- CHANNEL 4: GITHUB -->
    <g transform="translate(0, 310)">
      <rect width="636" height="66" rx="12" fill="#0b1122" fill-opacity="0.85" stroke="url(#cardGrad4)" stroke-width="1.2"/>
      
      <!-- Icon Container (Purple) -->
      <circle cx="36" cy="33" r="18" fill="#070b14" stroke="#c084fc" stroke-width="1.2" stroke-opacity="0.6"/>
      <path d="M36 24 C31.5 24 28 27.5 28 32 C28 35.6 30.3 38.6 33.5 39.7 C33.9 39.8 34.1 39.5 34.1 39.3 C34.1 39 34.1 38.5 34.1 37.7 C31.9 38.2 31.3 36.6 31.3 36.6 C31 35.7 30.4 35.4 30.4 35.4 C29.7 34.9 30.5 34.9 30.5 34.9 C31.3 35 31.7 35.8 31.7 35.8 C32.4 37 33.6 36.7 34 36.4 C34.1 35.9 34.4 35.5 34.7 35.2 C32.9 35 31 34.3 31 31.2 C31 30.3 31.3 29.7 31.8 29.1 C31.7 28.9 31.4 28.1 31.9 26.9 C31.9 26.9 32.6 26.6 34.1 27.7 C34.7 27.5 35.4 27.4 36 27.4 C36.6 27.4 37.3 27.5 37.9 27.7 C39.4 26.6 40.1 26.9 40.1 26.9 C40.6 28.1 40.3 28.9 40.2 29.1 C40.7 29.7 41 30.3 41 31.2 C41 34.3 39.1 35 37.3 35.2 C37.6 35.5 37.9 36.1 37.9 36.8 C37.9 37.9 37.9 38.8 37.9 39.1 C37.9 39.4 38.1 39.6 38.5 39.5 C41.7 38.4 44 35.4 44 32 C44 27.5 40.5 24 36 24 Z" fill="#c084fc"/>

      <!-- Clean Texts -->
      <text x="68" y="25" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="800" fill="#c084fc" letter-spacing="1.5">04 // GITHUB CODEBASES</text>
      <text x="68" y="47" font-family="'Inter', sans-serif" font-size="15" font-weight="700" fill="#f8fafc">github.com/DhruvilTech</text>

      <!-- Action Chip -->
      <g transform="translate(546, 20)">
        <rect width="76" height="26" rx="6" fill="#c084fc" fill-opacity="0.1" stroke="#c084fc" stroke-width="1" stroke-opacity="0.6"/>
        <text x="38" y="17" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="10.5" font-weight="900" fill="#c084fc">SOURCE ↗</text>
      </g>
    </g>

    <!-- Bottom Status Ribbon -->
    <text x="0" y="408" font-family="'JetBrains Mono', monospace" font-size="11.5" font-weight="800" fill="#38bdf8" letter-spacing="1.6">
      REAL SYSTEMS · REAL UTILITY // OPEN TO AGENTIC AI &amp; FULL-STACK WORK
    </text>
  </g>
</svg>'''

    ET.fromstring(svg_content)
    with open('assets/connect-hub.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("Successfully built streamlined assets/connect-hub.svg!")

def build_perfect_signal_footer():
    # Width: 1150, Height: 155
    # Requirements applied:
    # 1. Removed robotic line '06 // TRANSMISSION COMPLETE · ALL SIGNALS NOMINAL'
    # 2. Replaced with impressive bold headline: 'FROM THOUGHT TO THING. KEEP BUILDING.'
    # 3. Subline: 'DHRUVIL DATTANI // AI SYSTEMS & FULL-STACK ENGINEER'
    # 4. Removed 'LATENCY 12ms · 100%' pill completely
    # 5. Clean, fluid, unobstructed oscilloscope wave
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1150 155" width="1150" height="155" role="img" aria-label="Dhruvil Dattani - System Status &amp; Signal Telemetry Carrier">
  <title>Dhruvil Dattani - Signal Telemetry Carrier</title>
  <defs>
    <!-- Background Gradient (matching builder-pass.svg) -->
    <linearGradient id="cleanFooterBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a1022"/>
      <stop offset="50%" stop-color="#070b14"/>
      <stop offset="100%" stop-color="#050811"/>
    </linearGradient>

    <!-- Border Gradient (exact builder-pass.svg hairline) -->
    <linearGradient id="cleanFooterBorder" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#247bff" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#567394" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#ff354f" stop-opacity="0.75"/>
    </linearGradient>

    <!-- Punchline Gradient -->
    <linearGradient id="cleanPunchline" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22d3ee"/>
      <stop offset="50%" stop-color="#c084fc"/>
      <stop offset="100%" stop-color="#ff354f"/>
    </linearGradient>

    <!-- Wave Line Gradient -->
    <linearGradient id="signalWaveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.3"/>
      <stop offset="30%" stop-color="#22d3ee" stop-opacity="1.0"/>
      <stop offset="70%" stop-color="#8b5cf6" stop-opacity="1.0"/>
      <stop offset="100%" stop-color="#ff354f" stop-opacity="0.85"/>
    </linearGradient>

    <!-- Dot Pattern (exact builder-pass.svg stack-dots) -->
    <pattern id="cleanFooterDots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.7" fill="#99b1db" opacity="0.14"/>
    </pattern>

    <!-- Neon Glow Filter -->
    <filter id="waveGlow" x="-20%" y="-40%" width="140%" height="180%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Container Base -->
  <rect x="2" y="2" width="1146" height="151" rx="18" fill="url(#cleanFooterBg)" stroke="url(#cleanFooterBorder)" stroke-width="1.5"/>
  <rect x="2" y="2" width="1146" height="151" rx="18" fill="url(#cleanFooterDots)"/>

  <!-- Cyber Corner Tech Ticks -->
  <path d="M2 18 L2 2 L18 2" fill="none" stroke="#22d3ee" stroke-width="2.5" opacity="0.9"/>
  <path d="M1148 137 L1148 153 L1132 153" fill="none" stroke="#ff354f" stroke-width="2.5" opacity="0.9"/>

  <!-- ============================================================ -->
  <!-- LEFT SIDE: FULL DEVELOPER DETAILS IN ABSOLUTE PERFECTION      -->
  <!-- ============================================================ -->
  <g transform="translate(46, 24)">
    <!-- 1. Powerful Display Heading (Replaces the robotic 06 line) -->
    <text y="38" font-family="'Inter', -apple-system, sans-serif" font-size="28" font-weight="900" letter-spacing="-0.5">
      <tspan fill="#f8fafc">FROM THOUGHT TO THING. </tspan>
      <tspan fill="url(#cleanPunchline)">KEEP BUILDING.</tspan>
    </text>

    <!-- 2. Developer Name & Core Engineering Domain -->
    <text y="70" font-family="'JetBrains Mono', monospace" font-size="13" font-weight="800" letter-spacing="1.6">
      <tspan fill="#22d3ee">DHRUVIL DATTANI</tspan>
      <tspan fill="#64748b"> // </tspan>
      <tspan fill="#94a3b8">AI SYSTEMS &amp; FULL-STACK ENGINEER</tspan>
    </text>

    <!-- 3. Academic Institution, Location & Availability Badges Strip (y=92) -->
    <g transform="translate(0, 92)">
      <!-- Academic Badge: MSU BARODA · CSE -->
      <g>
        <rect width="165" height="24" rx="5" fill="#070b14" stroke="#a78bfa" stroke-opacity="0.45" stroke-width="1"/>
        <rect width="3.5" height="24" rx="1.5" fill="#a78bfa"/>
        <text x="10" y="16" font-family="'JetBrains Mono', monospace" font-size="9.5" font-weight="800" fill="#c4b5fd" letter-spacing="0.8">MSU BARODA · CSE</text>
      </g>
      <!-- Location Badge -->
      <g transform="translate(175, 0)">
        <rect width="205" height="24" rx="5" fill="#070b14" stroke="#22d3ee" stroke-opacity="0.45" stroke-width="1"/>
        <rect width="3.5" height="24" rx="1.5" fill="#22d3ee"/>
        <text x="10" y="16" font-family="'JetBrains Mono', monospace" font-size="9.5" font-weight="800" fill="#67e8f9" letter-spacing="0.8">VADODARA, GUJARAT 🇮🇳</text>
      </g>
      <!-- Availability Badge -->
      <g transform="translate(390, 0)">
        <rect width="180" height="24" rx="5" fill="#070b14" stroke="#34d399" stroke-opacity="0.5" stroke-width="1"/>
        <rect width="3.5" height="24" rx="1.5" fill="#34d399"/>
        <circle cx="12" cy="12" r="2.8" fill="#34d399"/>
        <text x="20" y="16" font-family="'JetBrains Mono', monospace" font-size="9.5" font-weight="800" fill="#34d399" letter-spacing="0.8">OPEN TO SDE &amp; AI</text>
      </g>
    </g>
  </g>

  <!-- ============================================================ -->
  <!-- RIGHT SIDE: PURE UNOBSTRUCTED SIGNAL OSCILLOSCOPE WAVE       -->
  <!-- (Latency pill removed for a clean, elegant aesthetic)       -->
  <!-- ============================================================ -->
  <g transform="translate(710, 24)">

    <!-- Background Guideline Grid -->
    <line x1="0" y1="52" x2="390" y2="52" stroke="#1e293b" stroke-width="1" stroke-dasharray="4 6" opacity="0.5"/>
    <line x1="0" y1="28" x2="390" y2="28" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="2 4" opacity="0.3"/>
    <line x1="0" y1="76" x2="390" y2="76" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="2 4" opacity="0.3"/>

    <!-- Glowing Continuous Cyber Telemetry Wave (Animated smoothly) -->
    <path fill="none" stroke="url(#signalWaveGrad)" stroke-width="2.6" filter="url(#waveGlow)">
      <animate attributeName="d" dur="3.5s" repeatCount="indefinite"
        values="M0,52 Q48,16 98,52 T195,52 T292,52 T390,52;
                M0,52 Q48,82 98,52 T195,52 T292,52 T390,52;
                M0,52 Q48,26 98,52 T195,52 T292,52 T390,52;
                M0,52 Q48,16 98,52 T195,52 T292,52 T390,52"/>
    </path>

    <!-- Traveling Laser Photon Packet along the Waveform -->
    <circle cx="0" cy="52" r="5" fill="#22d3ee" filter="url(#waveGlow)">
      <animate attributeName="cx" values="0;390;0" dur="4.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.4;1;0.4" dur="4.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="0" cy="52" r="2.2" fill="#ffffff">
      <animate attributeName="cx" values="0;390;0" dur="4.2s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>'''

    ET.fromstring(svg_content)
    with open('assets/footer.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    with open('assets/footer-wave.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("Successfully built Perfect Signal Footer assets/footer.svg!")

if __name__ == "__main__":
    build_clean_connect_hub()
    build_perfect_signal_footer()
