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

    header = '''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Dhruvil Dattani — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7C3AED"><animate attributeName="stop-color" values="#7C3AED;#22D3EE;#10B981;#7C3AED" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="0.5" stop-color="#22D3EE"><animate attributeName="stop-color" values="#22D3EE;#10B981;#7C3AED;#22D3EE" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#7C3AED;#22D3EE;#10B981" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
<linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#60A5FA"/>
      <stop offset="0.45" stop-color="#A78BFA"/>
      <stop offset="1" stop-color="#22D3EE"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0 -120; 0 120; 0 -120" dur="9s" repeatCount="indefinite"/>
    </linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A101F"/><stop offset="1" stop-color="#0C1426"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<rect id="tvdark" width="1.6" height="1.3" rx="0.4" fill="#A78BFA"/>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="#070B16"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="#0B1222"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="rgba(255,255,255,0.10)"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="#94A3B8">dhruvildattani9@gmail.com - % ./profile.sh --live</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="#475569">VISUAL.MAP</text>
<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="36" y="84" width="400" height="492" rx="10" fill="#0A101F" stroke="rgba(34,211,238,0.35)"/>
<g transform="translate(50,86) scale(1.2400,1.4471)">
'''

    particles_footer = '''</g>
<path d="M 50 84 L 36 84 L 36 98" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.8"/>
<path d="M 422 84 L 436 84 L 436 98" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.8"/>
<path d="M 50 576 L 36 576 L 36 562" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.8"/>
<path d="M 422 576 L 436 576 L 436 562" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.8"/>
<text x="470" y="106" font-size="13" letter-spacing="2" fill="#22D3EE" filter="url(#txtGlow)">SYSTEM.INFO</text>
<line x1="566" y1="102" x2="1061" y2="102" stroke="rgba(255,255,255,0.10)"/>
<text x="1125" y="106" text-anchor="end" font-size="12" fill="#F87171" font-weight="700"><tspan>&#9679;</tspan> LIVE</text>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>
<rect x="470" y="122" width="245" height="20" rx="4" fill="#4C1D95"/>
<text x="479" y="136" font-size="14" font-weight="700" fill="#E9D5FF">dhruvildattani9@gmail.com</text>
<line x1="725" y1="130" x2="1125" y2="130" stroke="rgba(255,255,255,0.10)"/>
</g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.90s" fill="freeze"/><text x="470" y="165" font-size="13" fill="#67E8F9">Subject</text><text x="590" y="165" font-size="13" fill="#E2E8F0">Dhruvil Dattani</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.02s" fill="freeze"/><text x="470" y="185" font-size="13" fill="#67E8F9">Role ...</text><text x="590" y="185" font-size="13" fill="#F8FAFC" font-weight="700">Full Stack &amp; AI Systems Engineer</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.14s" fill="freeze"/><text x="470" y="205" font-size="13" fill="#67E8F9">Origin .</text><text x="590" y="205" font-size="13" fill="#94A3B8">Gujarat, India</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.26s" fill="freeze"/><text x="470" y="225" font-size="13" fill="#67E8F9">Education</text><text x="590" y="225" font-size="13" fill="#94A3B8">B.Tech Computer Science &amp; Engineering</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.38s" fill="freeze"/><text x="470" y="245" font-size="13" fill="#67E8F9">Status .</text><text x="590" y="245" font-size="13" fill="#34D399" font-weight="700">Open for Opportunities &amp; AI Projects</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.50s" fill="freeze"/><text x="470" y="265" font-size="13" fill="#67E8F9">ToolChain</text><text x="590" y="265" font-size="13" fill="#CBD5E1">Next.js &#183; React &#183; Node.js &#183; Python &#183; TypeScript</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.72s" fill="freeze"/><text x="470" y="295" font-size="13" fill="#22D3EE">Core.Languages</text><text x="615" y="295" font-size="13" fill="#E2E8F0">TypeScript &#183; Python &#183; JavaScript &#183; Go &#183; C++</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.84s" fill="freeze"/><text x="470" y="315" font-size="13" fill="#22D3EE">Core.Frontend</text><text x="615" y="315" font-size="13" fill="#CBD5E1">Next.js 14 &#183; React &#183; Tailwind CSS &#183; Redux</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.96s" fill="freeze"/><text x="470" y="335" font-size="13" fill="#22D3EE">Core.Backend</text><text x="615" y="335" font-size="13" fill="#CBD5E1">Node.js &#183; Express &#183; FastAPI &#183; Django</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.08s" fill="freeze"/><text x="470" y="355" font-size="13" fill="#22D3EE">Core.Database</text><text x="615" y="355" font-size="13" fill="#CBD5E1">PostgreSQL &#183; MongoDB &#183; Redis &#183; Supabase</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.20s" fill="freeze"/><text x="470" y="375" font-size="13" fill="#22D3EE">Core.Cloud/AI</text><text x="615" y="375" font-size="13" fill="#CBD5E1">Docker &#183; AWS &#183; LangChain &#183; OpenAI &#183; Git</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.42s" fill="freeze"/><text x="470" y="415" font-size="13" fill="#A78BFA">- Contact &amp; Networks</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.54s" fill="freeze"/><text x="470" y="435" font-size="13" fill="#67E8F9">Grid.Mail ....</text><text x="590" y="435" font-size="13" fill="#CBD5E1">dhruvildattani9@gmail.com</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.66s" fill="freeze"/><text x="470" y="455" font-size="13" fill="#67E8F9">Grid.GitHub ..</text><text x="590" y="455" font-size="13" fill="#CBD5E1">github.com/DhruvilTech</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.78s" fill="freeze"/><text x="470" y="475" font-size="13" fill="#67E8F9">Grid.LinkedIn</text><text x="590" y="475" font-size="13" fill="#CBD5E1">linkedin.com/in/dhruvildattani</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.90s" fill="freeze"/><text x="470" y="495" font-size="13" fill="#67E8F9">Grid.Portfolio</text><text x="590" y="495" font-size="13" fill="#CBD5E1">dhruviltech.dev</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="3.02s" fill="freeze"/><text x="470" y="515" font-size="13" fill="#67E8F9">Grid.Status ..</text><text x="590" y="515" font-size="13" fill="#34D399">&#9679; Available for hire &amp; collaborations</text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="3.34s" fill="freeze"/>
<text x="470" y="555" font-size="13" fill="#94A3B8">&#9656; More about me &amp; projects below in README</text>
</g>
</g>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="2" opacity="0.75" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.5" opacity="0.95"/>
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
