#!/usr/bin/env python3
"""
generate_cards.py
Renders a stack of animated, self-contained SVG cards for sidoxsinu's GitHub profile README.
Matches the design, colors, and typography of muhammedsinan.in.
Supports STATIC=1 mode for freezing at the final frame.
"""

import os
import sys
import json
import base64
import tempfile
import subprocess
import urllib.request
from datetime import datetime
from PIL import Image
import io

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(REPO_ROOT, "data")
CARDS_DIR = os.path.join(REPO_ROOT, "cards")
FONTS_DIR = os.path.join(REPO_ROOT, "fonts")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

CONTRIBUTIONS_FILE = os.path.join(DATA_DIR, "contributions.json")
PORTRAIT_FILE = os.path.join(ASSETS_DIR, "portrait.webp")

IS_STATIC = os.environ.get("STATIC") == "1" or "--static" in sys.argv
DO_REFRESH = "--refresh" in sys.argv or os.environ.get("REFRESH") == "1" or os.environ.get("GITHUB_ACTIONS") == "true"

# Brand Palette (Matched with muhammedsinan.in & verified GitHub stats)
COLORS = {
    "bg_dark": "#0a0a0d",
    "bg_card": "#121216",
    "bg_card_to": "#17171d",
    "border": "#26262e",
    "border_glow": "#e54d2e",
    "accent_ember": "#e54d2e",
    "accent_ember_light": "#ff6b4a",
    "accent_amber": "#ffaa33",
    "accent_blue": "#58a6ff",
    "accent_green": "#00bb7f",
    "text_primary": "#ffffff",
    "text_secondary": "#d4d4d8",
    "text_muted": "#888891",
    "track": "#1b1b22",
    # Contribution levels
    "level_0": "#161b22",
    "level_1": "#4a1c12",
    "level_2": "#8f2e1b",
    "level_3": "#e54d2e",
    "level_4": "#ff7b5a",
}

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CARDS_DIR, exist_ok=True)
    os.makedirs(FONTS_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

def subset_font_to_b64(ttf_path, text):
    """Subsets a TTF font to WOFF using fontTools.subset with exact characters used."""
    if not os.path.exists(ttf_path) or not text:
        return ""
    chars = "".join(sorted(set(text + " ")))
    with tempfile.NamedTemporaryFile(suffix=".woff", delete=False) as tmp:
        tmp_woff = tmp.name
    try:
        cmd = [
            sys.executable, "-m", "fontTools.subset",
            ttf_path,
            f"--text={chars}",
            "--flavor=woff",
            f"--output-file={tmp_woff}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return ""
        with open(tmp_woff, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    finally:
        if os.path.exists(tmp_woff):
            os.remove(tmp_woff)

def get_font_css(sans_bold_text="", sans_med_text="", mono_text=""):
    """Generates minimal @font-face CSS blocks containing only the characters needed."""
    bold_ttf = os.path.join(FONTS_DIR, "GeneralSans-Bold.ttf")
    medium_ttf = os.path.join(FONTS_DIR, "GeneralSans-Medium.ttf")
    mono_ttf = os.path.join(FONTS_DIR, "JetBrainsMono.ttf")

    css = []
    if sans_bold_text:
        b64_bold = subset_font_to_b64(bold_ttf, sans_bold_text)
        if b64_bold:
            css.append(f"""
        @font-face {{
          font-family: 'General Sans';
          font-style: normal;
          font-weight: 700;
          src: url('data:font/woff;charset=utf-8;base64,{b64_bold}') format('woff');
        }}""")

    if sans_med_text:
        b64_med = subset_font_to_b64(medium_ttf, sans_med_text)
        if b64_med:
            css.append(f"""
        @font-face {{
          font-family: 'General Sans';
          font-style: normal;
          font-weight: 500;
          src: url('data:font/woff;charset=utf-8;base64,{b64_med}') format('woff');
        }}""")

    if mono_text:
        b64_mono = subset_font_to_b64(mono_ttf, mono_text)
        if b64_mono:
            css.append(f"""
        @font-face {{
          font-family: 'JetBrains Mono';
          font-style: normal;
          font-weight: 500;
          src: url('data:font/woff;charset=utf-8;base64,{b64_mono}') format('woff');
        }}""")

    return "\n".join(css)

def get_base_style(start_delay=0.0):
    """Returns CSS style block with animation rules and prefers-reduced-motion support."""
    if IS_STATIC:
        anim_css = """
        * {
          animation: none !important;
          transition: none !important;
        }
        .card-container {
          opacity: 1 !important;
        }
        .pulse-dot, .pulse-ring {
          animation: none !important;
          opacity: 1 !important;
        }
        """
    else:
        anim_css = f"""
        .card-container {{
          opacity: 0;
          animation: cardFadeIn 0.75s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          animation-delay: {start_delay:.2f}s;
        }}
        @keyframes cardFadeIn {{
          0% {{ opacity: 0; transform: translateY(8px); }}
          100% {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulseRing {{
          0%, 100% {{ stroke-opacity: 0.3; transform: scale(1); }}
          50% {{ stroke-opacity: 0.85; transform: scale(1.02); }}
        }}
        @keyframes pulseDot {{
          0%, 100% {{ opacity: 0.4; transform: scale(1); }}
          50% {{ opacity: 1; transform: scale(1.15); }}
        }}
        .pulse-dot {{
          animation: pulseDot 2.2s ease-in-out infinite;
          transform-origin: center;
        }}
        .pulse-ring {{
          animation: pulseRing 3.5s ease-in-out infinite;
          transform-origin: center;
        }}
        """

    return f"""
      {anim_css}
      @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
          animation: none !important;
          transition: none !important;
        }}
        .card-container {{
          opacity: 1 !important;
        }}
        .pulse-dot, .pulse-ring {{
          animation: none !important;
          opacity: 1 !important;
        }}
      }}
      .font-sans {{ font-family: 'General Sans', system-ui, -apple-system, sans-serif; }}
      .font-mono {{ font-family: 'JetBrains Mono', 'Fira Code', monospace; }}
    """

def get_portrait_b64():
    """Reads assets/portrait.webp, resizes to 220x220, and encodes to base64 PNG."""
    if not os.path.exists(PORTRAIT_FILE):
        return ""
    try:
        img = Image.open(PORTRAIT_FILE)
        img_resized = img.resize((220, 220), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img_resized.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print("Error processing portrait:", e)
        return ""

def fetch_contributions_data():
    """Fetches live contribution data from API and saves to data/contributions.json."""
    username = "sidoxsinu"
    url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            api_data = json.loads(resp.read().decode())
        raw_days = api_data.get("contributions", [])
        if not raw_days:
            return None
        days_sorted = sorted(raw_days, key=lambda d: d["date"])
        total = sum(d["count"] for d in days_sorted)
        active_days = sum(1 for d in days_sorted if d["count"] > 0)
        busiest = max(days_sorted, key=lambda d: d["count"])

        longest_streak = 0
        temp_streak = 0
        for d in days_sorted:
            if d["count"] > 0:
                temp_streak += 1
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
            else:
                temp_streak = 0

        current_streak = 0
        today_str = datetime.now().strftime("%Y-%m-%d")
        for d in reversed(days_sorted):
            if d["count"] > 0:
                current_streak += 1
            else:
                if d["date"] == today_str and current_streak == 0:
                    continue
                break

        months_map = {}
        for d in days_sorted:
            ym = d["date"][:7]
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            m_name = dt.strftime("%b")
            if ym not in months_map:
                months_map[ym] = {"year_month": ym, "month": m_name, "count": 0}
            months_map[ym]["count"] += d["count"]

        monthly = list(months_map.values())
        if len(monthly) > 12:
            monthly = monthly[-12:]

        res = {
            "username": username,
            "updated_at": datetime.now().isoformat(),
            "total_contributions": total,
            "active_days": active_days,
            "longest_streak": longest_streak,
            "current_streak": current_streak,
            "busiest_day": busiest,
            "monthly": monthly,
            "contributions": days_sorted
        }
        with open(CONTRIBUTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"  [OK] Successfully refreshed and saved {CONTRIBUTIONS_FILE} ({total} commits)")
        return res
    except Exception as e:
        print("  [WARN] Failed to refresh live contributions:", e)
        return None

def load_or_fetch_contributions():
    """Loads data/contributions.json or fetches live from API."""
    if DO_REFRESH:
        data = fetch_contributions_data()
        if data:
            return data

    if os.path.exists(CONTRIBUTIONS_FILE):
        try:
            with open(CONTRIBUTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("contributions"):
                    return data
        except Exception as e:
            print("Error loading contributions:", e)

    # If file doesn't exist or failed to load, fetch live
    data = fetch_contributions_data()
    if data:
        return data

    # Verified static fallback
    return {
        "username": "sidoxsinu",
        "total_contributions": 586,
        "active_days": 88,
        "longest_streak": 9,
        "current_streak": 0,
        "busiest_day": {"date": "2026-11-03", "count": 54},
        "monthly": [
            {"month": "Dec", "count": 0},
            {"month": "Jan", "count": 8},
            {"month": "Feb", "count": 0},
            {"month": "Mar", "count": 27},
            {"month": "Apr", "count": 57},
            {"month": "May", "count": 37},
            {"month": "Jun", "count": 92},
            {"month": "Jul", "count": 25},
            {"month": "Aug", "count": 31},
            {"month": "Sep", "count": 30},
            {"month": "Oct", "count": 195},
            {"month": "Nov", "count": 70}
        ],
        "contributions": []
    }

# ==============================================================================
# CARD 1: HERO CARD
# ==============================================================================
def render_hero_card():
    sans_bold = "Muhammed Sinan M"
    sans_med = (
        "Second-year B.Tech CSE student & SWE Intern building full-stack web, iOS and AI systems "
        "Torcue Digital (SWE) Christ College CSE Google Build with AI Win IEEE Jt Design Lead"
    )
    mono = "@sidoxsinu OPEN TO SDE INTERNSHIPS VALANCHERY & CCE, KERALA"

    fonts_css = get_font_css(sans_bold_text=sans_bold, sans_med_text=sans_med, mono_text=mono)
    base_style = get_base_style(start_delay=0.0)
    portrait_b64 = get_portrait_b64()

    avatar_markup = ""
    if portrait_b64:
        avatar_markup = f"""
        <!-- Avatar Ring & Glow -->
        <circle cx="95" cy="115" r="62" fill="none" stroke="{COLORS['accent_ember']}" stroke-width="1.2" stroke-opacity="0.3" class="pulse-ring" />
        <circle cx="95" cy="115" r="57" fill="none" stroke="{COLORS['accent_ember']}" stroke-width="2" stroke-opacity="0.9" />
        <clipPath id="avatarClip">
          <circle cx="95" cy="115" r="53" />
        </clipPath>
        <image href="data:image/png;base64,{portrait_b64}" x="42" y="62" width="106" height="106" clip-path="url(#avatarClip)" />
        """
    else:
        avatar_markup = f"""
        <circle cx="95" cy="115" r="55" fill="{COLORS['track']}" stroke="{COLORS['accent_ember']}" stroke-width="2" />
        <text x="95" y="123" text-anchor="middle" fill="{COLORS['text_primary']}" font-size="28" font-weight="700" class="font-sans">MS</text>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 230" width="100%" height="100%">
  <defs>
    <linearGradient id="heroCardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['bg_card']}" />
      <stop offset="100%" stop-color="{COLORS['bg_card_to']}" />
    </linearGradient>
    <linearGradient id="emberLine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{COLORS['accent_ember']}" stop-opacity="0" />
      <stop offset="30%" stop-color="{COLORS['accent_ember_light']}" stop-opacity="1" />
      <stop offset="70%" stop-color="{COLORS['accent_ember']}" stop-opacity="1" />
      <stop offset="100%" stop-color="{COLORS['accent_ember']}" stop-opacity="0" />
    </linearGradient>
  </defs>
  <style>
    {fonts_css}
    {base_style}
  </style>

  <g class="card-container">
    <!-- Card Frame -->
    <rect width="850" height="230" rx="16" fill="url(#heroCardBg)" stroke="{COLORS['border']}" stroke-width="1.2" />
    <!-- Top Accent Bar -->
    <line x1="30" y1="0" x2="350" y2="0" stroke="url(#emberLine)" stroke-width="2.5" />

    {avatar_markup}

    <!-- Content Block -->
    <g transform="translate(180, 40)">
      <!-- Eyebrow & Status Row -->
      <g transform="translate(0, 0)">
        <rect width="195" height="22" rx="11" fill="#0d1f18" stroke="{COLORS['accent_green']}" stroke-width="0.8" stroke-opacity="0.8" />
        <circle cx="12" cy="11" r="3.5" fill="{COLORS['accent_green']}" class="pulse-dot" />
        <text x="22" y="15" fill="{COLORS['accent_green']}" font-size="9.5" font-weight="600" class="font-mono">OPEN TO SDE INTERNSHIPS</text>

        <rect x="205" y="0" width="200" height="22" rx="11" fill="#14141a" stroke="{COLORS['border']}" stroke-width="0.8" />
        <text x="217" y="15" fill="{COLORS['text_muted']}" font-size="9.5" font-weight="500" class="font-mono">VALANCHERY &amp; CCE, KERALA</text>
      </g>

      <!-- Name & Handle -->
      <g transform="translate(0, 48)">
        <text x="0" y="0" fill="{COLORS['text_primary']}" font-size="28" font-weight="700" class="font-sans">Muhammed Sinan M <tspan dx="10" fill="{COLORS['accent_ember']}" font-size="15" font-weight="500" class="font-mono">@sidoxsinu</tspan></text>
      </g>

      <!-- One-line Bio -->
      <text x="0" y="74" fill="{COLORS['text_secondary']}" font-size="13" font-weight="500" class="font-sans">
        Second-year B.Tech CSE student &amp; SWE Intern building full-stack web, iOS and AI systems
      </text>

      <!-- Credentials Pills -->
      <g transform="translate(0, 95)">
        <!-- Pill 1: Internship -->
        <rect width="156" height="26" rx="6" fill="#171720" stroke="{COLORS['border']}" stroke-width="0.9" />
        <circle cx="12" cy="13" r="3" fill="{COLORS['accent_ember']}" />
        <text x="22" y="17" fill="{COLORS['text_primary']}" font-size="11" font-weight="500" class="font-sans">Torcue Digital (SWE)</text>

        <!-- Pill 2: College -->
        <rect x="166" y="0" width="142" height="26" rx="6" fill="#171720" stroke="{COLORS['border']}" stroke-width="0.9" />
        <circle cx="178" cy="13" r="3" fill="{COLORS['accent_blue']}" />
        <text x="188" y="17" fill="{COLORS['text_primary']}" font-size="11" font-weight="500" class="font-sans">Christ College CSE</text>

        <!-- Pill 3: Award -->
        <rect x="318" y="0" width="178" height="26" rx="6" fill="#171720" stroke="{COLORS['border']}" stroke-width="0.9" />
        <circle cx="330" cy="13" r="3" fill="{COLORS['accent_amber']}" />
        <text x="340" y="17" fill="{COLORS['text_primary']}" font-size="11" font-weight="500" class="font-sans">Google Build with AI Win</text>

        <!-- Pill 4: Leadership -->
        <rect x="506" y="0" width="146" height="26" rx="6" fill="#171720" stroke="{COLORS['border']}" stroke-width="0.9" />
        <circle cx="518" cy="13" r="3" fill="{COLORS['accent_green']}" />
        <text x="528" y="17" fill="{COLORS['text_primary']}" font-size="11" font-weight="500" class="font-sans">IEEE Jt Design Lead</text>
      </g>
    </g>
  </g>
</svg>"""
    return svg

# ==============================================================================
# CARDS 2, 3, 4: THREE LINKED TILES (WIDTH 32.5% EACH)
# ==============================================================================
def render_tile_card(tile_index, eyebrow, title, subtitle, desc, tag, color_accent, start_delay):
    sans_bold = title
    sans_med = f"{subtitle} {desc} ->"
    mono = f"{eyebrow} {tag}"

    fonts_css = get_font_css(sans_bold_text=sans_bold, sans_med_text=sans_med, mono_text=mono)
    base_style = get_base_style(start_delay=start_delay)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 270 145" width="100%" height="100%">
  <defs>
    <linearGradient id="tileBg_{tile_index}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['bg_card']}" />
      <stop offset="100%" stop-color="{COLORS['bg_card_to']}" />
    </linearGradient>
  </defs>
  <style>
    {fonts_css}
    {base_style}
  </style>

  <g class="card-container">
    <!-- Tile Background -->
    <rect width="270" height="145" rx="14" fill="url(#tileBg_{tile_index})" stroke="{COLORS['border']}" stroke-width="1.2" />
    <!-- Top Corner Accent Strip -->
    <path d="M 0 14 L 0 0 L 70 0" fill="none" stroke="{color_accent}" stroke-width="2.5" stroke-linecap="round" />

    <g transform="translate(18, 24)">
      <!-- Eyebrow -->
      <text x="0" y="0" fill="{color_accent}" font-size="9" font-weight="700" class="font-mono" letter-spacing="1">{eyebrow}</text>
      <!-- Title -->
      <text x="0" y="24" fill="{COLORS['text_primary']}" font-size="16" font-weight="700" class="font-sans">{title}</text>
      <!-- Subtitle -->
      <text x="0" y="42" fill="{color_accent}" font-size="12" font-weight="600" class="font-sans">{subtitle}</text>
      <!-- Description -->
      <text x="0" y="62" fill="{COLORS['text_muted']}" font-size="10.5" font-weight="500" class="font-sans">{desc}</text>

      <!-- Bottom Link Indicator -->
      <g transform="translate(0, 94)">
        <rect width="234" height="20" rx="4" fill="#15151c" stroke="{COLORS['border']}" stroke-width="0.8" />
        <text x="10" y="14" fill="{COLORS['text_secondary']}" font-size="9.5" font-weight="500" class="font-mono">{tag}</text>
        <text x="218" y="14" fill="{color_accent}" font-size="11" font-weight="700" class="font-sans">→</text>
      </g>
    </g>
  </g>
</svg>"""
    return svg

# ==============================================================================
# CARD 5: CONTRIBUTIONS PER MONTH & STATS CHART
# ==============================================================================
def render_contributions_chart_card(data):
    total = data.get("total_contributions", 586)
    active_days = data.get("active_days", 88)
    longest_streak = data.get("longest_streak", 9)
    busiest = data.get("busiest_day", {})
    b_date = busiest.get("date", "2026-11-03")
    b_count = busiest.get("count", 54)
    try:
        b_dt = datetime.strptime(b_date, "%Y-%m-%d")
        b_fmt = b_dt.strftime("%b %d")
    except Exception:
        b_fmt = b_date

    monthly = data.get("monthly", [])
    if len(monthly) > 12:
        monthly = monthly[-12:]

    sans_bold = "Contribution Velocity & Activity Metrics"
    sans_med = " ".join(m["month"] for m in monthly)
    mono = (
        f"Verified GitHub commit telemetry across the last 12 months "
        f"TOTAL CONTRIBUTIONS ACTIVE COMMITTING DAYS LONGEST STREAK BUSIEST DAY "
        f"{total} {active_days} Days {longest_streak} {b_fmt} ({b_count}) "
        + " ".join(str(m["count"]) for m in monthly if m["count"] > 0)
    )

    fonts_css = get_font_css(sans_bold_text=sans_bold, sans_med_text=sans_med, mono_text=mono)
    base_style = get_base_style(start_delay=0.75)

    max_count = max(max(m["count"] for m in monthly), 100)
    scale_max = ((max_count + 49) // 50) * 50
    chart_h = 95
    baseline_y = 240

    bars_svg = []
    col_width = 32
    col_step = 64
    start_x = 74

    for i, m in enumerate(monthly):
        cnt = m["count"]
        m_name = m["month"]
        cx = start_x + i * col_step
        bar_h = max(3.0, (cnt / scale_max) * chart_h) if cnt > 0 else 2.5
        bar_y = baseline_y - bar_h

        bar_color = (
            COLORS["accent_ember"] if cnt >= 80
            else (COLORS["accent_amber"] if cnt >= 30
            else (COLORS["accent_blue"] if cnt > 0
            else "#22222e"))
        )

        count_markup = ""
        if cnt > 0:
            count_markup = f'<text x="{cx}" y="{bar_y - 6:.1f}" text-anchor="middle" fill="{COLORS["text_primary"]}" font-size="10" font-weight="700" class="font-mono">{cnt}</text>'

        bars_svg.append(f"""
        <!-- Month {m_name}: {cnt} commits -->
        <g>
          <!-- Base track -->
          <rect x="{cx - col_width/2:.1f}" y="{baseline_y - chart_h}" width="{col_width}" height="{chart_h}" rx="5" fill="{COLORS['track']}" opacity="0.6" />
          <!-- Animated Bar -->
          <rect class="chart-bar-{i}" x="{cx - col_width/2:.1f}" y="{bar_y:.1f}" width="{col_width}" height="{bar_h:.1f}" rx="5" fill="{bar_color}" />
          {count_markup}
          <!-- Month label below -->
          <text x="{cx}" y="{baseline_y + 18}" text-anchor="middle" fill="{COLORS['text_muted']}" font-size="11" font-weight="500" class="font-sans">{m_name}</text>
        </g>
        """)

    bar_keyframes = []
    if not IS_STATIC:
        for i, m in enumerate(monthly):
            cnt = m["count"]
            bh = max(3.0, (cnt / scale_max) * chart_h) if cnt > 0 else 2.5
            by = baseline_y - bh
            bar_keyframes.append(f"""
            @keyframes riseBar_{i} {{
              0% {{ height: 0px; y: {baseline_y}px; opacity: 0; }}
              100% {{ height: {bh:.1f}px; y: {by:.1f}px; opacity: 1; }}
            }}
            .chart-bar-{i} {{
              animation: riseBar_{i} 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
              animation-delay: {0.85 + (i * 0.035):.2f}s;
            }}""")

    keyframes_block = "\n".join(bar_keyframes)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 285" width="100%" height="100%">
  <defs>
    <linearGradient id="chartCardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['bg_card']}" />
      <stop offset="100%" stop-color="{COLORS['bg_card_to']}" />
    </linearGradient>
  </defs>
  <style>
    {fonts_css}
    {base_style}
    {keyframes_block}
  </style>

  <g class="card-container">
    <rect width="850" height="285" rx="16" fill="url(#chartCardBg)" stroke="{COLORS['border']}" stroke-width="1.2" />

    <!-- Card Header -->
    <g transform="translate(36, 32)">
      <text x="0" y="0" fill="{COLORS['text_primary']}" font-size="16" font-weight="700" class="font-sans">Contribution Velocity &amp; Activity Metrics</text>
      <text x="0" y="18" fill="{COLORS['text_muted']}" font-size="11" class="font-mono">Verified GitHub commit telemetry across the last 12 months</text>
    </g>

    <!-- 4 Top Metric Tiles -->
    <g transform="translate(36, 68)">
      <!-- Metric 1: Total Commits -->
      <g transform="translate(0, 0)">
        <rect width="184" height="44" rx="8" fill="#181822" stroke="{COLORS['border']}" stroke-width="0.9" />
        <text x="14" y="16" fill="{COLORS['text_muted']}" font-size="9" font-weight="600" class="font-mono">TOTAL CONTRIBUTIONS</text>
        <text x="14" y="34" fill="{COLORS['accent_ember']}" font-size="16" font-weight="700" class="font-mono">{total}</text>
      </g>

      <!-- Metric 2: Active Days -->
      <g transform="translate(198, 0)">
        <rect width="184" height="44" rx="8" fill="#181822" stroke="{COLORS['border']}" stroke-width="0.9" />
        <text x="14" y="16" fill="{COLORS['text_muted']}" font-size="9" font-weight="600" class="font-mono">ACTIVE COMMITTING DAYS</text>
        <text x="14" y="34" fill="{COLORS['accent_blue']}" font-size="16" font-weight="700" class="font-mono">{active_days} Days</text>
      </g>

      <!-- Metric 3: Longest Streak -->
      <g transform="translate(396, 0)">
        <rect width="184" height="44" rx="8" fill="#181822" stroke="{COLORS['border']}" stroke-width="0.9" />
        <text x="14" y="16" fill="{COLORS['text_muted']}" font-size="9" font-weight="600" class="font-mono">LONGEST STREAK</text>
        <text x="14" y="34" fill="{COLORS['accent_amber']}" font-size="16" font-weight="700" class="font-mono">{longest_streak} Days</text>
      </g>

      <!-- Metric 4: Busiest Day -->
      <g transform="translate(594, 0)">
        <rect width="184" height="44" rx="8" fill="#181822" stroke="{COLORS['border']}" stroke-width="0.9" />
        <text x="14" y="16" fill="{COLORS['text_muted']}" font-size="9" font-weight="600" class="font-mono">BUSIEST DAY</text>
        <text x="14" y="34" fill="{COLORS['accent_green']}" font-size="16" font-weight="700" class="font-mono">{b_fmt} ({b_count})</text>
      </g>
    </g>

    <!-- Reference Gridlines -->
    <g opacity="0.25">
      <line x1="50" y1="{baseline_y - chart_h}" x2="800" y2="{baseline_y - chart_h}" stroke="{COLORS['border']}" stroke-dasharray="3,3" />
      <line x1="50" y1="{baseline_y - chart_h/2}" x2="800" y2="{baseline_y - chart_h/2}" stroke="{COLORS['border']}" stroke-dasharray="3,3" />
      <line x1="50" y1="{baseline_y}" x2="800" y2="{baseline_y}" stroke="{COLORS['border']}" />
    </g>

    <!-- Monthly Bars -->
    {"".join(bars_svg)}
  </g>
</svg>"""
    return svg

# ==============================================================================
# CARDS 6-9: FEATURED REPOSITORY CARDS
# ==============================================================================
def render_repo_card(badge, title, desc, tags, meta, color_accent, start_delay):
    sans_bold = title
    sans_med = desc
    mono = f"{badge} ↗ " + " ".join(tags) + f" {meta}"

    fonts_css = get_font_css(sans_bold_text=sans_bold, sans_med_text=sans_med, mono_text=mono)
    base_style = get_base_style(start_delay=start_delay)

    tag_pills = []
    tx = 0
    for t in tags:
        tw = len(t) * 7.5 + 18
        tag_pills.append(f"""
        <g transform="translate({tx}, 0)">
          <rect width="{tw:.1f}" height="22" rx="5" fill="#191924" stroke="{COLORS['border']}" stroke-width="0.8" />
          <text x="{tw/2:.1f}" y="15" text-anchor="middle" fill="{color_accent}" font-size="10.5" font-weight="500" class="font-mono">{t}</text>
        </g>
        """)
        tx += tw + 10

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 145" width="100%" height="100%">
  <defs>
    <linearGradient id="repoBg_{title.replace(' ', '_').replace('•', '_')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['bg_card']}" />
      <stop offset="100%" stop-color="{COLORS['bg_card_to']}" />
    </linearGradient>
  </defs>
  <style>
    {fonts_css}
    {base_style}
  </style>

  <g class="card-container">
    <!-- Card Frame -->
    <rect width="850" height="145" rx="14" fill="url(#repoBg_{title.replace(' ', '_').replace('•', '_')})" stroke="{COLORS['border']}" stroke-width="1.2" />
    <!-- Left Accent Border -->
    <rect width="4" height="145" rx="2" fill="{color_accent}" />

    <g transform="translate(32, 24)">
      <!-- Eyebrow Badge -->
      <g transform="translate(0, 0)">
        <rect width="{len(badge)*7.2 + 20:.1f}" height="20" rx="4" fill="#14141c" stroke="{color_accent}" stroke-width="0.8" />
        <text x="10" y="14" fill="{color_accent}" font-size="9.5" font-weight="700" class="font-mono">{badge}</text>
      </g>

      <!-- Repo Title with External Link Arrow -->
      <g transform="translate(0, 38)">
        <text x="0" y="0" fill="{COLORS['text_primary']}" font-size="18" font-weight="700" class="font-sans">{title} <tspan dx="8" fill="{color_accent}" font-size="14" font-weight="600" class="font-mono">↗</tspan></text>
      </g>

      <!-- Description -->
      <text x="0" y="58" fill="{COLORS['text_muted']}" font-size="12" font-weight="400" class="font-sans">{desc}</text>

      <!-- Bottom Tech Pills & Meta Status -->
      <g transform="translate(0, 78)">
        {"".join(tag_pills)}

        <!-- Meta status badge on the right -->
        <g transform="translate(560, 0)">
          <rect width="220" height="22" rx="5" fill="#161620" stroke="{COLORS['border']}" stroke-width="0.8" />
          <circle cx="12" cy="11" r="3" fill="{COLORS['accent_green']}" />
          <text x="22" y="15" fill="{COLORS['text_secondary']}" font-size="10" font-weight="500" class="font-mono">{meta}</text>
        </g>
      </g>
    </g>
  </g>
</svg>"""
    return svg

# ==============================================================================
# CARD 10: FULL CONTRIBUTION GRAPH IN BRAND COLOUR
# ==============================================================================
def render_contribution_graph_card(data):
    total = data.get("total_contributions", 586)
    days = data.get("contributions", [])

    sans_bold = "Annual Contribution Matrix"
    sans_med = "Less More Mon Wed Fri Nov Dec Jan Feb Mar Apr May Jun Jul Aug Sep Oct"
    mono = f"{total} verified contributions in the last 12 months • @sidoxsinu"

    fonts_css = get_font_css(sans_bold_text=sans_bold, sans_med_text=sans_med, mono_text=mono)
    base_style = get_base_style(start_delay=1.85)

    if len(days) >= 364:
        recent_days = days[-364:]
    else:
        recent_days = days

    cell_size = 10.5
    gap = 3.5
    start_x = 75
    start_y = 76

    cells_svg = []
    level_colors = {
        0: COLORS["level_0"],
        1: COLORS["level_1"],
        2: COLORS["level_2"],
        3: COLORS["level_3"],
        4: COLORS["level_4"]
    }

    month_labels = []
    last_month = ""

    for c in range(52):
        for r in range(7):
            idx = c * 7 + r
            if idx < len(recent_days):
                item = recent_days[idx]
                level = item.get("level", 0)
                d_str = item.get("date", "")
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                m_str = dt.strftime("%b")
                if r == 0 and m_str != last_month and c < 50:
                    month_labels.append((start_x + c * (cell_size + gap), m_str))
                    last_month = m_str
            else:
                level = 0

            fill_color = level_colors.get(level, COLORS["level_0"])
            x = start_x + c * (cell_size + gap)
            y = start_y + r * (cell_size + gap)

            cells_svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{fill_color}" />')

    months_svg = []
    for mx, m_txt in month_labels:
        months_svg.append(f'<text x="{mx:.1f}" y="64" fill="{COLORS["text_muted"]}" font-size="10" font-weight="500" class="font-sans">{m_txt}</text>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 215" width="100%" height="100%">
  <defs>
    <linearGradient id="contribGraphBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['bg_card']}" />
      <stop offset="100%" stop-color="{COLORS['bg_card_to']}" />
    </linearGradient>
  </defs>
  <style>
    {fonts_css}
    {base_style}
  </style>

  <g class="card-container">
    <rect width="850" height="215" rx="16" fill="url(#contribGraphBg)" stroke="{COLORS['border']}" stroke-width="1.2" />

    <!-- Header -->
    <g transform="translate(36, 28)">
      <circle cx="5" cy="0" r="4" fill="{COLORS['accent_ember']}" class="pulse-dot" />
      <text x="16" y="4" fill="{COLORS['text_primary']}" font-size="15" font-weight="700" class="font-sans">Annual Contribution Matrix</text>
      <text x="16" y="20" fill="{COLORS['text_muted']}" font-size="11" class="font-mono">{total} verified contributions in the last 12 months • @sidoxsinu</text>
    </g>

    <!-- Month Labels -->
    {"".join(months_svg)}

    <!-- Day of Week Labels -->
    <g fill="{COLORS['text_muted']}" font-size="9" font-weight="500" class="font-sans" text-anchor="end">
      <text x="65" y="{start_y + 1 * (cell_size+gap) + 8}">Mon</text>
      <text x="65" y="{start_y + 3 * (cell_size+gap) + 8}">Wed</text>
      <text x="65" y="{start_y + 5 * (cell_size+gap) + 8}">Fri</text>
    </g>

    <!-- Contribution Cells Grid -->
    <g>
      {"".join(cells_svg)}
    </g>

    <!-- Legend -->
    <g transform="translate(640, 194)" fill="{COLORS['text_muted']}" font-size="10" font-weight="500" class="font-sans">
      <text x="-32" y="9">Less</text>
      <rect x="0" y="0" width="10" height="10" rx="2" fill="{COLORS['level_0']}" />
      <rect x="15" y="0" width="10" height="10" rx="2" fill="{COLORS['level_1']}" />
      <rect x="30" y="0" width="10" height="10" rx="2" fill="{COLORS['level_2']}" />
      <rect x="45" y="0" width="10" height="10" rx="2" fill="{COLORS['level_3']}" />
      <rect x="60" y="0" width="10" height="10" rx="2" fill="{COLORS['level_4']}" />
      <text x="76" y="9">More</text>
    </g>
  </g>
</svg>"""
    return svg

# ==============================================================================
# MAIN RENDERER
# ==============================================================================
def main():
    print(f"[*] Starting SVG cards generation... (STATIC mode = {IS_STATIC})")
    ensure_dirs()
    data = load_or_fetch_contributions()

    cards = {}

    # 1. Hero Card
    print("  -> Rendering cards/hero.svg...")
    cards["hero.svg"] = render_hero_card()

    # 2. Three Linked Tiles
    print("  -> Rendering cards/tile-1.svg...")
    cards["tile-1.svg"] = render_tile_card(
        tile_index=1,
        eyebrow="EXPERIENCE // 6 MONTHS",
        title="Software Intern",
        subtitle="Torcue Digital",
        desc="Full-stack web, iOS &amp; AI tickets",
        tag="Client Systems under NDA",
        color_accent=COLORS["accent_ember"],
        start_delay=0.35
    )

    print("  -> Rendering cards/tile-2.svg...")
    cards["tile-2.svg"] = render_tile_card(
        tile_index=2,
        eyebrow="LEADERSHIP // KERALA",
        title="Design &amp; Finance Lead",
        subtitle="IEEE Jt &amp; IEDC CCE",
        desc="EDS/CT/Nano Jt &#8226; Co-CFO &#8226; TinkerHub",
        tag="100+ Student Branches",
        color_accent=COLORS["accent_amber"],
        start_delay=0.45
    )

    print("  -> Rendering cards/tile-3.svg...")
    cards["tile-3.svg"] = render_tile_card(
        tile_index=3,
        eyebrow="ACHIEVEMENTS // 30+ SPRINTS",
        title="Hackathon Winner",
        subtitle="Google Build with AI",
        desc="Best Tech Project &#8226; 2nd Prize Web",
        tag="Explore Project Portfolio",
        color_accent=COLORS["accent_blue"],
        start_delay=0.55
    )

    # 3. Contributions Chart Card
    print("  -> Rendering cards/contributions-chart.svg...")
    cards["contributions-chart.svg"] = render_contributions_chart_card(data)

    # 4. Featured Repo Cards
    print("  -> Rendering cards/repo-next-gen-ai.svg...")
    cards["repo-next-gen-ai.svg"] = render_repo_card(
        badge="BEST TECHNICAL PROJECT // GOOGLE BUILD WITH AI",
        title="next-gen-ai-assistant-system",
        desc="Multi-modal AI terminal for voice and text workflows using LLaMA 3.3 for responses and Whisper for speech-to-text with integrated tool calling.",
        tags=["Python", "Groq API", "LLaMA 3.3", "Whisper"],
        meta="Award-Winning AI Platform",
        color_accent=COLORS["accent_ember"],
        start_delay=1.2
    )

    print("  -> Rendering cards/repo-ghostops.svg...")
    cards["repo-ghostops.svg"] = render_repo_card(
        badge="36-HOUR HACKATHON BUILD // CYBERSECURITY",
        title="GhostOps Zero-Trust Offboarding",
        desc="Zero-trust offboarding platform that maps and revokes developer credentials across AWS IAM, GitHub, and SSH from a single dashboard.",
        tags=["FastAPI", "Docker", "React", "AWS IAM", "SQLite"],
        meta="FastAPI + Docker Sandbox",
        color_accent=COLORS["accent_amber"],
        start_delay=1.35
    )

    print("  -> Rendering cards/repo-gate-layover.svg...")
    cards["repo-gate-layover.svg"] = render_repo_card(
        badge="TINKERSPACE CALICUT HACKATHON // TRAVEL TECH",
        title="GATE • Layover Companion",
        desc="Mobile-first app turning waiting time into location-based missions, XP rank progression, and a photo travel memory passport.",
        tags=["Next.js", "Supabase", "Groq API", "Vercel"],
        meta="Mobile-First Web App",
        color_accent=COLORS["accent_blue"],
        start_delay=1.5
    )

    print("  -> Rendering cards/repo-pylon.svg...")
    cards["repo-pylon.svg"] = render_repo_card(
        badge="2ND PRIZE // WEBATHON 2025",
        title="Pylon • Smart Scholarship Finder",
        desc="Clean scholarship discovery web application built with custom filtering algorithms and performance-tuned responsive UI without heavy frameworks.",
        tags=["Vanilla HTML5", "CSS3", "JavaScript", "Algorithms"],
        meta="Zero-Framework Engine",
        color_accent=COLORS["accent_ember_light"],
        start_delay=1.65
    )

    # 5. Full Contribution Graph
    print("  -> Rendering cards/contribution-graph.svg...")
    cards["contribution-graph.svg"] = render_contribution_graph_card(data)

    # Write out cards
    for filename, content in cards.items():
        out_path = os.path.join(CARDS_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  [OK] Saved {out_path} ({size_kb:.1f} KB)")

    print("[✓] All SVG cards rendered successfully!")

if __name__ == "__main__":
    main()
