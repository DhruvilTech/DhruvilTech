import re
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image
import fitz

def build_perfect_4phase_terminal():
    print("Step 1: Extracting Phase 0 (Dhruvil portrait) exact peak dots directly from dhruvil_user_chosen.jpg...")
    img = cv2.imread('assets/dhruvil_user_chosen.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    x1, x2 = 110, 870
    y1, y2 = 88, 1000
    crop = gray[y1:y2, x1:x2]
    ch, cw = crop.shape

    target_w = 300
    target_h = 340
    aspect_correction = 1.2400 / 1.4471
    svg_w = target_w
    svg_h = int(round(svg_w * (ch / cw) * aspect_correction))
    y_start = max(0, 338 - svg_h)

    resized = cv2.resize(crop, (svg_w, svg_h), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((target_h, target_w), dtype=np.uint8)
    canvas[y_start:y_start+svg_h, :svg_w] = resized

    # Serpentine dithering with dampening to preserve authentic stipple noise without directional artifacts
    d = canvas.astype(float).copy()
    h_c, w_c = d.shape
    binary = np.zeros_like(canvas)

    for y in range(h_c):
        if y % 2 == 0:
            x_range = range(w_c)
            direction = 1
        else:
            x_range = range(w_c - 1, -1, -1)
            direction = -1

        for x in x_range:
            if canvas[y, x] < 15:
                continue
            old_val = d[y, x]
            th = 105
            new_val = 255 if old_val > th else 0
            binary[y, x] = 255 if new_val == 255 else 0
            err = (old_val - new_val) * 0.85

            if 0 <= x + direction < w_c:
                d[y, x + direction] += err * 7 / 16
            if y + 1 < h_c:
                if 0 <= x - direction < w_c:
                    d[y + 1, x - direction] += err * 3 / 16
                d[y + 1, x] += err * 5 / 16
                if 0 <= x + direction < w_c:
                    d[y + 1, x + direction] += err * 1 / 16

    ys0, xs0 = np.where(binary > 0)
    pts0_all = np.column_stack([xs0.astype(np.float32), ys0.astype(np.float32)])
    print(f"Total available stipple noise points: {len(pts0_all)}")

    # Protect all face points (100% kept to preserve eyes, pupils, eyebrows, smile)
    is_face = (pts0_all[:, 1] < 175) & (pts0_all[:, 0] > 90) & (pts0_all[:, 0] < 225)
    face_pts = pts0_all[is_face]
    body_pts = pts0_all[~is_face]
    print(f"Face points (100% protected): {len(face_pts)}, Body points: {len(body_pts)}")

    target_total = 9000
    needed_body = target_total - len(face_pts)
    np.random.seed(42)
    body_idx = np.random.choice(len(body_pts), size=needed_body, replace=False)
    p0 = np.vstack([face_pts, body_pts[body_idx]])
    print(f"Phase 0 (Dhruvil) selected points: {len(p0)}")

    print("Step 2: Extracting Phase 1 (React Logo), Phase 2 (Brackets), Phase 3 (Node.js Logo), Phase 4 (Python Logo)...")
    p2_base = np.load('assets/brackets_coords.npy')
    assert len(p2_base) == 900

    logo_size = 180
    cx, cy = 148, 168
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

    # Phase 1: React Logo (900 centroids: central nucleus + 3 atomic orbital rings)
    react_img = cv2.imread('assets/react_logo.png')
    react_gray = cv2.cvtColor(react_img, cv2.COLOR_BGR2GRAY)
    react_mask = react_gray < 220
    ys_r, xs_r = np.where(react_mask)
    min_x, max_x = xs_r.min(), xs_r.max()
    min_y, max_y = ys_r.min(), ys_r.max()
    cropped_react = react_mask[min_y:max_y+1, min_x:max_x+1]
    rw, rh = max_x - min_x + 1, max_y - min_y + 1
    scale_r = logo_size / max(rw, rh)
    new_rw, new_rh = int(round(rw * scale_r)), int(round(rh * scale_r))
    react_resized = cv2.resize(cropped_react.astype(np.uint8) * 255, (new_rw, new_rh), interpolation=cv2.INTER_AREA) > 100
    x0_react = int(round(cx - new_rw / 2))
    y0_react = int(round(cy - new_rh / 2))

    np.random.seed(42)
    ys_re, xs_re = np.where(react_resized)
    cand_react = np.column_stack([xs_re, ys_re]).astype(np.float32)
    if len(cand_react) > 10000:
        c_idx = np.random.choice(len(cand_react), 10000, replace=False)
        cand_react = cand_react[c_idx]
    _, _, p1_base = cv2.kmeans(cand_react, 900, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
    p1_base[:, 0] += x0_react
    p1_base[:, 1] += y0_react
    assert len(p1_base) == 900

    # Phase 3: Node.js Logo (900 centroids: 'node' wordmark + 'JS' hexagon)
    node_img = cv2.imread('assets/nodejs_logo.png')
    node_gray = cv2.cvtColor(node_img, cv2.COLOR_BGR2GRAY)
    node_mask = node_gray < 220
    ys_n, xs_n = np.where(node_mask)
    min_x, max_x = xs_n.min(), xs_n.max()
    min_y, max_y = ys_n.min(), ys_n.max()
    cropped_node = node_mask[min_y:max_y+1, min_x:max_x+1]
    nw, nh = max_x - min_x + 1, max_y - min_y + 1
    target_node_w = 215
    scale_n = target_node_w / nw
    new_nw, new_nh = int(round(nw * scale_n)), int(round(nh * scale_n))
    node_resized = cv2.resize(cropped_node.astype(np.uint8) * 255, (new_nw, new_nh), interpolation=cv2.INTER_AREA) > 100
    x0_node = int(round(cx - new_nw / 2))
    y0_node = int(round(cy - new_nh / 2))

    np.random.seed(123)
    ys_nr, xs_nr = np.where(node_resized)
    cand_node = np.column_stack([xs_nr, ys_nr]).astype(np.float32)
    if len(cand_node) > 10000:
        c_idx = np.random.choice(len(cand_node), 10000, replace=False)
        cand_node = cand_node[c_idx]
    _, _, p3_base = cv2.kmeans(cand_node, 900, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
    p3_base[:, 0] += x0_node
    p3_base[:, 1] += y0_node
    assert len(p3_base) == 900

    # Phase 4: Python Logo (450 centroids for blue snake + 450 centroids for yellow snake = 900 base points)
    logo_img = cv2.imread('assets/python_logo.png', cv2.IMREAD_UNCHANGED)
    b_l, g_l, r_l, a_l = cv2.split(logo_img)
    mask_l = a_l > 128
    blue_mask_l = mask_l & (b_l > r_l)
    yellow_mask_l = mask_l & (r_l > b_l)

    x_off = int(round(cx - logo_size / 2))
    y_off = int(round(cy - logo_size / 2))
    blue_resized = cv2.resize(blue_mask_l.astype(np.uint8) * 255, (logo_size, logo_size), interpolation=cv2.INTER_AREA) > 100
    yellow_resized = cv2.resize(yellow_mask_l.astype(np.uint8) * 255, (logo_size, logo_size), interpolation=cv2.INTER_AREA) > 100

    def sample_snake(submask, num_pts, seed):
        np.random.seed(seed)
        ys, xs = np.where(submask)
        candidates = np.column_stack([xs, ys]).astype(np.float32)
        if len(candidates) > 10000:
            c_idx = np.random.choice(len(candidates), 10000, replace=False)
            candidates = candidates[c_idx]
        _, _, centers = cv2.kmeans(candidates, num_pts, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
        centers[:, 0] += x_off
        centers[:, 1] += y_off
        return centers

    pts_blue = sample_snake(blue_resized, 450, seed=101)
    pts_yellow = sample_snake(yellow_resized, 450, seed=202)
    p4_base = np.vstack([pts_blue, pts_yellow])
    assert len(p4_base) == 900

    def expand_900_to_target(base_pts, target_count=9000):
        base_arr = np.array(base_pts, dtype=np.float32)
        expanded = []
        np.random.seed(42)
        ratio = target_count // len(base_pts)
        for i in range(len(base_pts)):
            for k in range(ratio):
                jitter = np.random.uniform(-0.35, 0.35, size=2) if k > 0 else np.zeros(2)
                expanded.append(base_arr[i] + jitter)
        return np.array(expanded, dtype=np.float32)

    p1 = expand_900_to_target(p1_base, 9000)
    p2 = expand_900_to_target(p2_base, 9000)
    p3 = expand_900_to_target(p3_base, 9000)
    p4 = expand_900_to_target(p4_base, 9000)
    print(f"Phases 1, 2, 3, 4 points ready: {len(p1)}, {len(p2)}, {len(p3)}, {len(p4)}")

    print("Step 3: Computing laminar spatial sweep matching across all 5 phases...")
    def spatial_sort(pts):
        return np.lexsort((pts[:, 0], pts[:, 1]))

    order0 = spatial_sort(p0)
    order1 = spatial_sort(p1)
    order2 = spatial_sort(p2)
    order3 = spatial_sort(p3)
    order4 = spatial_sort(p4)

    p0_canon = p0[order0]
    p1_canon = p1[order1]
    p2_canon = p2[order2]
    p3_canon = p3[order3]
    p4_canon = p4[order4]

    print("Spatial alignment completed!")

    print("Step 4: Generating 9000 morphing particle elements for 5-phase loop...")
    key_times = "0.000;0.120;0.200;0.320;0.400;0.520;0.600;0.720;0.800;0.920;1.000"
    dur = "18.0s"

    uses_list = []
    for i in range(9000):
        s0 = f"{p0_canon[i][0]:.1f} {p0_canon[i][1]:.1f}"
        s1 = f"{p1_canon[i][0]:.1f} {p1_canon[i][1]:.1f}"
        s2 = f"{p2_canon[i][0]:.1f} {p2_canon[i][1]:.1f}"
        s3 = f"{p3_canon[i][0]:.1f} {p3_canon[i][1]:.1f}"
        s4 = f"{p4_canon[i][0]:.1f} {p4_canon[i][1]:.1f}"

        val_str = f"{s0};{s0};{s1};{s1};{s2};{s2};{s3};{s3};{s4};{s4};{s0}"
        u_elem = f'<use href="#tvdark"><animateTransform attributeName="transform" type="translate" values="{val_str}" keyTimes="{key_times}" dur="{dur}" repeatCount="indefinite"/></use>'
        uses_list.append(u_elem)

    particles_body = "\n".join(uses_list)
    print(f"Generated {len(uses_list)} particle elements!")

    header = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="648" viewBox="0 0 1200 648" font-family="'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" role="img" aria-label="Dhruvil Dattani — Developer Profile">
<defs>
  <linearGradient id="stack-hairline"><stop stop-color="#247bff" stop-opacity=".7"/><stop offset=".5" stop-color="#567394" stop-opacity=".25"/><stop offset="1" stop-color="#ff354f" stop-opacity=".65"/></linearGradient>
  <pattern id="stack-dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#99b1db" opacity=".13"/></pattern>
  <linearGradient id="barGradCyan" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#22d3ee"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient>
  <linearGradient id="barGradViolet" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#a78bfa"/><stop offset="100%" stop-color="#ec4899"/></linearGradient>
  <linearGradient id="barGradEmerald" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#34d399"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient>
  <linearGradient id="tagGrad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#22d3ee"/>
    <stop offset="50%" stop-color="#a78bfa"/>
    <stop offset="100%" stop-color="#38bdf8"/>
  </linearGradient>
  <filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="tagTextGlow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="winClip"><rect x="1" y="1" width="1198" height="646" rx="22"/></clipPath>
  <rect id="tvdark" width="1.6" height="1.3" rx="0.4" fill="#a78bfa"/>
</defs>
<rect x="1" y="1" width="1198" height="646" rx="22" fill="#070b16" stroke="url(#stack-hairline)" stroke-width="1.2"/>
<rect x="2" y="2" width="1196" height="644" rx="21" fill="url(#stack-dots)" stroke="none"/>
<rect x="1" y="1" width="1198" height="3" rx="1.5" fill="url(#barGradCyan)"/>
<g clip-path="url(#winClip)">
  <!-- LEFT: HALFTONE PORTRAIT & LOGO MORPH -->
  <rect x="24" y="20" width="418" height="536" rx="16" fill="#0d182c" stroke="#1d2d48" stroke-width="1.2"/>
  <rect x="24" y="20" width="418" height="3" rx="1.5" fill="url(#barGradCyan)"/>
  <rect x="38" y="32" width="116" height="24" rx="6" fill="#070b16" stroke="#22d3ee" stroke-opacity=".4" stroke-width="1"/>
  <text x="96" y="48" text-anchor="middle" font-size="11" font-weight="900" letter-spacing="2" fill="#22d3ee">VISUAL.MAP</text>

  <rect x="34" y="66" width="398" height="476" rx="10" fill="#070b16" stroke="#1d2d48" stroke-width="1"/>
  <rect x="34" y="66" width="398" height="476" rx="10" fill="url(#stack-dots)" opacity="0.08"/>
  <g transform="translate(48, 52) scale(1.2400, 1.4000)">
'''

    particles_footer = '''  </g>
  <path d="M 48 80 L 38 80 L 38 90" fill="none" stroke="#22d3ee" stroke-width="2" opacity="0.85"/>
  <path d="M 418 80 L 428 80 L 428 90" fill="none" stroke="#22d3ee" stroke-width="2" opacity="0.85"/>
  <path d="M 48 530 L 38 530 L 38 520" fill="none" stroke="#22d3ee" stroke-width="2" opacity="0.85"/>
  <path d="M 418 530 L 428 530 L 428 520" fill="none" stroke="#22d3ee" stroke-width="2" opacity="0.85"/>

  <!-- UNIFIED RIGHT PANEL: ENGINEER IDENTITY & ACADEMIC ACHIEVEMENTS -->
  <g transform="translate(460, 20)">
    <rect width="716" height="536" rx="16" fill="#0d182c" stroke="#1d2d48" stroke-width="1.2"/>
    <rect width="716" height="3" rx="1.5" fill="url(#barGradCyan)"/>
    
    <!-- Top Header -->
    <text x="24" y="28" font-size="13" font-weight="900" letter-spacing="1.5" fill="#22d3ee" filter="url(#txtGlow)">01 · DEVELOPER PROFILE &amp; ACADEMIC STANDING</text>
    <rect x="520" y="14" width="176" height="24" rx="6" fill="#070b16" stroke="#10b981" stroke-opacity=".4" stroke-width="1"/>
    <circle cx="536" cy="26" r="4" fill="#10b981"><animate attributeName="opacity" values="1;0.2;1" dur="1.8s" repeatCount="indefinite"/></circle>
    <text x="548" y="30" font-size="11" font-weight="800" letter-spacing="1" fill="#34d399">AVAILABLE FOR HIRE</text>
    
    <line x1="24" y1="46" x2="692" y2="46" stroke="rgba(255,255,255,0.08)"/>

    <!-- Section 1: Identity & Combined Education Details -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.3s" fill="freeze"/>
      <text x="24" y="78" font-size="15" font-weight="700" fill="#67e8f9">Subject</text>
      <text x="180" y="78" font-size="18" font-weight="900" fill="#ffffff">Dhruvil Dattani</text>
    </g>

    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.45s" fill="freeze"/>
      <text x="24" y="116" font-size="15" font-weight="700" fill="#67e8f9">Role</text>
      <text x="180" y="116" font-size="16" font-weight="800" fill="#f8fafc">Full Stack &amp; AI Systems Engineer</text>
    </g>

    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.60s" fill="freeze"/>
      <text x="24" y="154" font-size="15" font-weight="700" fill="#67e8f9">Education</text>
      <text x="180" y="154" font-size="15.5" font-weight="800" fill="#34d399">B.E. CSE @ MSU Baroda · 8.43 CGPA (3rd Year)</text>
    </g>

    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.75s" fill="freeze"/>
      <text x="24" y="192" font-size="15" font-weight="700" fill="#67e8f9">CORE_FOCUS</text>
      <text x="180" y="192" font-size="15" font-weight="800" fill="#22d3ee">LLM Agentic Workflows · Computer Vision · Scalable Web</text>
    </g>

    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.90s" fill="freeze"/>
      <text x="24" y="230" font-size="15" font-weight="700" fill="#67e8f9">Location</text>
      <text x="180" y="230" font-size="15" font-weight="700" fill="#94a3b8">Vadodara, Gujarat, India (Remote OK)</text>
    </g>

    <!-- Hairline Divider -->
    <line x1="24" y1="256" x2="692" y2="256" stroke="rgba(255,255,255,0.08)"/>

    <!-- Section 2: Achievements & Technical Capabilities -->
    <text x="24" y="284" font-size="12.5" font-weight="900" letter-spacing="1.5" fill="#a78bfa" filter="url(#txtGlow)">02 · KEY ACHIEVEMENTS &amp; TECHNICAL CAPABILITIES</text>

    <!-- State Merit -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.1s" fill="freeze"/>
      <text x="24" y="320" font-size="15" font-weight="700" fill="#67e8f9">State Merit</text>
      <text x="180" y="320" font-size="15" font-weight="800" fill="#e2e8f0">Gujarat State Rank 90 in DDCET (Diploma to Degree)</text>
    </g>

    <!-- Hackathons & Contests -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.25s" fill="freeze"/>
      <text x="24" y="358" font-size="15" font-weight="700" fill="#67e8f9">Contests</text>
      <text x="180" y="358" font-size="15" font-weight="700" fill="#c084fc">Selected for IIT Bombay Impact Contest · Odoo Offline Round</text>
    </g>

    <!-- ToolChain -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.4s" fill="freeze"/>
      <text x="24" y="396" font-size="15" font-weight="700" fill="#67e8f9">Toolchain</text>
      <text x="180" y="396" font-size="15" font-weight="700" fill="#38bdf8">Groq LLM · Gemini API · YOLOv8 · FastAPI · React · Node.js</text>
    </g>

    <!-- Current Availability -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.55s" fill="freeze"/>
      <text x="24" y="434" font-size="15" font-weight="700" fill="#67e8f9">Availability</text>
      <text x="180" y="434" font-size="15" font-weight="800" fill="#34d399">Open to Software Engineering Internships &amp; AI Roles</text>
    </g>

    <!-- Bottom Status Card Pill -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="1.7s" fill="freeze"/>
      <rect x="24" y="466" width="668" height="42" rx="10" fill="#070b16" stroke="#1d2d48" stroke-width="1.2"/>
      <circle cx="46" cy="487" r="4" fill="#34d399"/>
      <text x="62" y="491" font-size="13" font-weight="700" fill="#e2e8f0">B.E. CSE @ MSU Baroda · 8.43 CGPA · Gujarat State Rank 90</text>
    </g>
  </g>

  <!-- INTEGRATED BOTTOM FOCUS & MISSION STATUS RIBBON (Full Width Tagline Dock) -->
  <g transform="translate(24, 572)">
    <rect width="1152" height="54" rx="14" fill="#0d182c" stroke="#1d2d48" stroke-width="1.2"/>
    <rect width="1152" height="2.5" rx="1" fill="url(#barGradCyan)"/>

    <!-- Left Focus Chip -->
    <rect x="16" y="11" width="96" height="32" rx="8" fill="#070b16" stroke="#22d3ee" stroke-opacity=".5" stroke-width="1.2"/>
    <circle cx="32" cy="27" r="4" fill="#22d3ee">
      <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="46" y="31.5" fill="#22d3ee" font-size="11.5" font-weight="900" letter-spacing="1.5">FOCUS</text>

    <!-- Dynamic Cycling Focus Headlines -->
    <g font-size="13.5" font-weight="800">
      <!-- Phrase 1 -->
      <text x="135" y="33" fill="url(#tagGrad)" filter="url(#tagTextGlow)">
        Agentic AI Systems Engineer · Building Autonomous LLM Workflows
        <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
                 keyTimes="0; 0.28; 0.33; 0.95; 1"
                 values="1; 1; 0; 0; 1"/>
      </text>

      <!-- Phrase 2 -->
      <text x="135" y="33" fill="url(#tagGrad)" filter="url(#tagTextGlow)">
        Computer Vision (YOLOv8) · Real-Time Inferences · Full-Stack Web
        <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
                 keyTimes="0; 0.28; 0.33; 0.61; 0.66; 1"
                 values="0; 0; 1; 1; 0; 0"/>
      </text>

      <!-- Phrase 3 -->
      <text x="135" y="33" fill="url(#tagGrad)" filter="url(#tagTextGlow)">
        B.E. CSE @ MSU Baroda · Open to SDE &amp; AI Engineering Roles
        <animate attributeName="opacity" dur="9s" repeatCount="indefinite"
                 keyTimes="0; 0.61; 0.66; 0.94; 0.99; 1"
                 values="0; 0; 1; 1; 0; 0"/>
      </text>
    </g>

    <!-- Right Availability Chip -->
    <rect x="1024" y="13" width="112" height="28" rx="7" fill="#070b16" stroke="#1d2d48" stroke-width="1.2"/>
    <circle cx="1040" cy="27" r="3.5" fill="#10b981">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <text x="1086" y="31" text-anchor="middle" font-size="10.5" font-weight="800" fill="#34d399" letter-spacing="1">AVAILABLE</text>
  </g>
</g>
</svg>
'''

    full_svg = header + particles_body + "\n" + particles_footer

    print("Step 5: Validating XML...")
    ET.fromstring(full_svg)
    print("XML Validation PASSED successfully!")

    with open('assets/hero-terminal.svg', 'w', encoding='utf-8') as f:
        f.write(full_svg)
    print("assets/hero-terminal.svg successfully updated with perfect 4-phase loop!")

if __name__ == '__main__':
    build_perfect_4phase_terminal()
