"""
Smartphone Screen UI HTML/CSS/JS for EaglePhone OS v5.0 (`http://127.0.0.1:8765`).
Home Screen (App 0) + 9 Apps:
  0. SpringBoard Home Screen (Anime Wallpaper, Mascot Widget, 3x3 App Icon Grid)
  1. Life, Restaurant Auto-Sync, Savings (+1.5%/d) & Loans (Overdue Debt HP Drain)
  2. Stocks (10) & Gold/Silver/Gems/Commodities (6) — Market Watch Table + Chart + Trading
  3. Crypto Exchange (8 Coins) — Market Watch Table + Chart + Trading
  4. Chronological Sportsbook (5 League Pages, Scoreboard Table, Standings)
  5. 4-in-1 Lottery (3x3 Scratch Card Box, 16:30 XSKT, 18:00 Vietlott + Virtual Keypad)
  6. EagleTimes Daily Newspaper (4 Sub-pages with Visual Banners: World, Finance, Crypto, Sports)
  7. Unified Portfolio (Asset Allocation Gauge Bars + Spot/Futures/Bets/Lottery Tables)
  8. Map Bug Reporter, Auto-Inspector (.IPL/.IDE/.IMG/.COL) & Safe Recall Unstuck (F11/F12)
  9. Settings & Anime Theme Customizer (Wallpapers, Mascots, Neon Themes)
"""

EAGLE_PHONE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EaglePhone OS v5.0 — Anime Smartphone & Life/Economy Companion</title>
<style>
  :root {
    --bg: #070b14;
    --phone-bg: #0b1120;
    --card: rgba(19, 28, 49, 0.90);
    --card-2: rgba(26, 38, 66, 0.92);
    --border: #263554;
    --accent: #38bdf8;
    --green: #10b981;
    --red: #ef4444;
    --gold: #f59e0b;
    --purple: #a855f7;
    --text: #f1f5f9;
    --muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
  body {
    background: radial-gradient(circle at top, #172554 0%, #050811 70%);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
  }
  .top-Controls {
    display: flex; gap: 6px; margin-bottom: 8px; align-items: center; font-size: 11.5px; flex-wrap: wrap; justify-content: center;
  }
  .mode-btn {
    background: #1e293b; color: #cbd5e1; border: 1px solid #334155;
    padding: 5px 11px; border-radius: 999px; cursor: pointer; font-weight: 600;
  }
  .mode-btn:hover { border-color: var(--accent); color: #fff; }

  .phone-frame {
    width: 450px;
    max-width: 100%;
    height: 890px;
    background: var(--phone-bg);
    background-size: cover;
    background-position: center;
    border: 8px solid #334155;
    border-radius: 42px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.85), inset 0 0 0 2px #0f172a;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
    transition: width 0.22s ease;
  }
  .phone-frame.tablet-mode { width: 980px; border-radius: 26px; }
  .phone-backdrop-overlay {
    position: absolute;
    inset: 0;
    background: rgba(8, 13, 26, 0.58);
    pointer-events: none;
    z-index: 0;
    transition: background 0.25s ease;
  }
  .phone-frame.on-home .phone-backdrop-overlay {
    background: rgba(8, 13, 26, 0.24);
  }
  .status-bar, .sync-bar, .toast-banner, .app-nav-header, .app-viewport, .app-dock {
    position: relative;
    z-index: 1;
  }

  .status-bar {
    height: 36px;
    padding: 0 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(8, 13, 26, 0.88);
    font-size: 11.5px;
    font-weight: 700;
    flex-shrink: 0;
  }
  .dynamic-island {
    width: 122px; height: 20px; background: #000; border-radius: 999px;
    position: absolute; left: 50%; transform: translateX(-50%);
    display: flex; align-items: center; justify-content: center;
    font-size: 9.5px; color: var(--accent); border: 1px solid #1e293b;
  }

  .sync-bar {
    background: linear-gradient(90deg, rgba(15,23,42,0.92) 0%, rgba(23,37,84,0.92) 100%);
    border-bottom: 1px solid var(--border);
    padding: 6px 10px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
    flex-shrink: 0;
  }
  .sync-item {
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid #1e293b;
    border-radius: 9px;
    padding: 4px 6px;
    text-align: center;
  }
  .sync-label { font-size: 9.5px; color: var(--muted); text-transform: uppercase; }
  .sync-val { font-size: 12.5px; font-weight: 800; margin-top: 1px; }

  .toast-banner {
    background: rgba(16, 185, 129, 0.16);
    border-bottom: 1px solid rgba(16, 185, 129, 0.35);
    color: #a7f3d0;
    font-size: 11px;
    padding: 5px 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-shrink: 0;
  }

  .app-nav-header {
    background: rgba(10, 16, 31, 0.90);
    border-bottom: 1px solid var(--border);
    padding: 6px 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }
  .nav-back-btn {
    background: rgba(56, 189, 248, 0.16);
    border: 1px solid var(--accent);
    color: #e0f2fe;
    border-radius: 8px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 800;
    cursor: pointer;
  }
  .nav-back-btn:hover { background: var(--accent); color: #06101e; }

  .app-viewport {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 9px;
  }
  .app-viewport::-webkit-scrollbar { width: 5px; }
  .app-viewport::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }

  .app-page { display: none; flex-direction: column; gap: 9px; }
  .app-page.active { display: flex; }

  /* SpringBoard Home Screen (App 0) */
  .mascot-widget {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.86), rgba(30, 41, 59, 0.78));
    border: 1px solid rgba(56, 189, 248, 0.45);
    border-radius: 18px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.45);
    backdrop-filter: blur(6px);
  }
  .mascot-widget img {
    width: 78px;
    height: 78px;
    border-radius: 14px;
    object-fit: contain;
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255,255,255,0.15);
    flex-shrink: 0;
  }
  .home-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 4px;
  }
  .home-app-tile {
    background: rgba(15, 23, 42, 0.78);
    border: 1.5px solid rgba(148, 163, 184, 0.25);
    border-radius: 18px;
    padding: 12px 8px 10px 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    cursor: pointer;
    position: relative;
    transition: all 0.15s ease;
    backdrop-filter: blur(6px);
  }
  .home-app-tile:hover, .home-app-tile.selected {
    border-color: var(--accent);
    background: rgba(30, 41, 59, 0.92);
    transform: translateY(-2px);
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
  }
  .home-app-tile img {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    object-fit: cover;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  }
  .home-app-tile .app-name {
    font-size: 11.5px;
    font-weight: 800;
    color: #f8fafc;
    text-align: center;
  }
  .home-app-tile .app-sub {
    font-size: 9.5px;
    color: #93c5fd;
    text-align: center;
  }
  .home-app-badge {
    position: absolute;
    top: 6px;
    right: 6px;
    background: #ef4444;
    color: #fff;
    font-size: 9.5px;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 999px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.5);
  }

  .visual-banner {
    width: 100%;
    height: 68px;
    border-radius: 11px;
    object-fit: cover;
    border: 1px solid var(--border);
    margin-bottom: 6px;
    display: block;
  }

  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 11px;
    backdrop-filter: blur(6px);
  }
  .card-title {
    font-size: 11.5px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 7px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }
  .btn-row { display: flex; gap: 6px; flex-wrap: wrap; }
  button.btn {
    background: var(--card-2);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 6px 9px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    flex: 1;
    transition: all 0.12s;
  }
  button.btn:hover { border-color: var(--accent); transform: translateY(-1px); }
  button.btn-green { background: rgba(16,185,129,0.2); border-color: #059669; color: #6ee7b7; }
  button.btn-red { background: rgba(239,68,68,0.2); border-color: #dc2626; color: #fca5a5; }
  button.btn-gold { background: rgba(245,158,11,0.2); border-color: #d97706; color: #fde68a; }
  button.btn-blue { background: rgba(56,189,248,0.2); border-color: #0284c7; color: #bae6fd; }
  button.btn-purple { background: rgba(168,85,247,0.2); border-color: #9333ea; color: #e9d5ff; }

  .pbar-wrap { margin-bottom: 7px; }
  .pbar-head { display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 3px; font-weight: 600; }
  .pbar-bg { height: 8px; background: #090e1a; border-radius: 999px; overflow: hidden; }
  .pbar-fill { height: 100%; border-radius: 999px; transition: width 0.25s; }

  .pill-scroll { display: flex; gap: 5px; overflow-x: auto; padding-bottom: 4px; }
  .pill-scroll::-webkit-scrollbar { height: 4px; }
  .pill-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
  .pill-row { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 6px; }
  .pill {
    background: #0f172a; border: 1px solid #263554; color: #cbd5e1;
    padding: 4px 9px; border-radius: 999px; font-size: 11px; font-weight: 700;
    cursor: pointer; white-space: nowrap;
  }
  .pill.active { background: var(--accent); color: #08101d; border-color: var(--accent); }

  .chart-box {
    background: #060a12;
    border: 1px solid #1e293b;
    border-radius: 11px;
    padding: 7px;
  }
  canvas.trade-canvas { width: 100%; height: 185px; display: block; }

  input, select {
    background: #090f1d;
    border: 1px solid var(--border);
    color: var(--text);
    padding: 6px 8px;
    border-radius: 8px;
    font-size: 11.5px;
  }

  .match-card {
    background: #0d1527;
    border: 1px solid #233252;
    border-radius: 11px;
    padding: 9px;
    margin-bottom: 7px;
  }
  .odds-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin-top: 6px; }
  .odd-btn {
    background: #16213a; border: 1px solid #2b3d63; border-radius: 7px;
    padding: 4px 3px; text-align: center; cursor: pointer; font-size: 10.5px;
  }
  .odd-btn:hover { border-color: var(--gold); background: #1e2d4f; }
  .odd-lbl { color: var(--muted); font-size: 9.5px; display: block; }
  .odd-val { color: #fde68a; font-weight: 800; font-size: 11.5px; }

  .scratch-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 7px 0; }
  .scratch-cell {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #475569; border-radius: 9px; height: 42px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 12.5px; color: #fde68a;
  }

  .keypad-grid {
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin-top: 6px;
  }
  .key-btn {
    background: #16213a; border: 1px solid #2b3d63; color: #f8fafc;
    border-radius: 8px; padding: 6px; font-weight: 800; font-size: 12px; cursor: pointer;
  }
  .key-btn:hover { border-color: var(--accent); background: #1e293b; }

  .news-paper {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 12px;
  }
  .news-sec {
    border-left: 3px solid var(--accent);
    padding-left: 9px;
    margin-bottom: 10px;
  }
  .news-sec h4 { font-size: 11.5px; text-transform: uppercase; color: #fde68a; margin-bottom: 3px; }
  .news-sec p { font-size: 12px; line-height: 1.45; color: #e2e8f0; }

  .app-dock {
    height: 62px;
    background: rgba(8, 13, 26, 0.94);
    border-top: 1px solid var(--border);
    display: grid;
    grid-template-columns: repeat(15, 1fr);
    padding: 4px 2px 6px 2px;
    gap: 2px;
    flex-shrink: 0;
  }
  .dock-btn {
    background: transparent; border: none; color: var(--muted);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 2px; cursor: pointer; border-radius: 9px; font-size: 7.5px; font-weight: 700;
  }
  .dock-btn .icon { font-size: 13.5px; }
  .dock-btn.active { background: rgba(56, 189, 248, 0.18); color: var(--accent); }
  table.mini-tbl { width: 100%; border-collapse: collapse; font-size: 11px; }
  table.mini-tbl th, table.mini-tbl td { padding: 4px 5px; border-bottom: 1px solid #1e293b; text-align: left; }
  table.mini-tbl tr.zebra { background: rgba(15, 23, 42, 0.55); }
  .port-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 8px; }
  .port-stat { background: #0b1324; border: 1px solid #223152; border-radius: 10px; padding: 7px 9px; }
  .port-stat .lbl { font-size: 10px; color: var(--muted); text-transform: uppercase; }
  .port-stat .val { font-size: 13.5px; font-weight: 800; margin-top: 2px; }
  .port-stat .sub { font-size: 10.5px; margin-top: 1px; }
</style>
</head>
<body>

<div class="top-Controls">
  <button class="mode-btn" onclick="switchApp(0)" style="border-color:#38bdf8;color:#bae6fd;" data-en="🏠 Home Screen (Bksp)" data-vi="🏠 Màn Hình Chính (Bksp)">🏠 Home Screen (Bksp)</button>
  <button class="mode-btn" onclick="switchApp(10)" style="border-color:#10b981;color:#a7f3d0;" data-en="🗺️ GG Map & GPS" data-vi="🗺️ GG Map & Chỉ Đường GPS">🗺️ GG Map & GPS</button>
  <button class="mode-btn" onclick="switchApp(12)" style="border-color:#f59e0b;color:#fde68a;" data-en="🚕 EagleRide (Uber/Xanh/Grab/Be)" data-vi="🚕 Đặt Xe EagleRide (Uber/Xanh/Grab/Be)">🚕 EagleRide (Uber/Xanh/Grab/Be)</button>
  <button class="mode-btn" onclick="switchApp(13)" style="border-color:#f43f5e;color:#fecdd3;" data-en="💖 WaifuLink (App 13)" data-vi="💖 WaifuLink (App 13)">💖 WaifuLink (App 13)</button>
  <button class="mode-btn" onclick="switchApp(14)" style="border-color:#38bdf8;color:#bae6fd;" data-en="📱 Contacts & Mondstadt DM (App 14)" data-vi="📱 Danh Bạ Mondstadt & Waifu (App 14)">📱 Contacts & Mondstadt DM (App 14)</button>
  <button class="mode-btn" onclick="toggleFrameMode()" data-en="📱 Frame: Phone / Tablet" data-vi="📱 Đổi Khung: Điện Thoại / Tablet">📱 Frame: Phone / Tablet</button>
  <button class="mode-btn" style="border-color:#ef4444;color:#fecaca;" onclick="act('report_map_bug', {})" data-en="🐛 Log Map Bug (F11)" data-vi="🐛 Báo Bug Tọa Độ (F11)">🐛 Log Map Bug (F11)</button>
  <button class="mode-btn" style="border-color:#10b981;color:#a7f3d0;" onclick="act('unstuck_player', {})" data-en="🛟 Quick Unstuck (F12)" data-vi="🛟 Cứu Hộ Nhanh (F12)">🛟 Quick Unstuck (F12)</button>
  <button class="mode-btn" onclick="act('advance_day', {delta: 1})" data-en="⏭️ Next Day (+1d)" data-vi="⏭️ Qua Ngày (+1d)">⏭️ Next Day (+1d)</button>
  <button class="mode-btn" onclick="act('toggle_hud_phone', {})" data-en="🎮 Show/Hide Phone (F7)" data-vi="🎮 Ẩn/Hiện Phone (F7)">🎮 Show/Hide Phone (F7)</button>
  <button class="mode-btn" id="langToggleBtn" style="border-color:#a855f7;color:#e9d5ff;" onclick="act('toggle_language', {})">🌐 EN | VI</button>
  <span id="syncModeBadge" style="color:#6ee7b7;font-weight:700;">● EaglePhone OS v5.0 Live</span>
</div>

<div class="phone-frame on-home" id="phoneFrame" style="background-image:url('/assets/ep_wp_furina.png');">
  <div class="phone-backdrop-overlay"></div>

  <div class="status-bar">
    <span id="clockTxt">01/01/2010 12:00</span>
    <div class="dynamic-island" id="islandTxt">5G ● EAGLE v5.0</div>
    <span id="hpBadge" style="color:#f87171;">♥ HP 100</span>
  </div>

  <div class="sync-bar">
    <div class="sync-item">
      <div class="sync-label" data-en="GTA Cash" data-vi="Tiền Mặt GTA">GTA Cash</div>
      <div class="sync-val" id="valCash" style="color:#34d399;">$500</div>
    </div>
    <div class="sync-item">
      <div class="sync-label" data-en="Bank + Savings" data-vi="Bank + Tiết Kiệm">Bank + Savings</div>
      <div class="sync-val" id="valBank" style="color:#60a5fa;">$7,500</div>
    </div>
    <div class="sync-item">
      <div class="sync-label" data-en="Loan Debt" data-vi="Dư Nợ Vay">Loan Debt</div>
      <div class="sync-val" id="valLoan" style="color:#f87171;">$0</div>
    </div>
    <div class="sync-item">
      <div class="sync-label" data-en="Net Worth" data-vi="Tài Sản Ròng">Net Worth</div>
      <div class="sync-val" id="valNet" style="color:#fbbf24;">$8,000</div>
    </div>
  </div>

  <div class="toast-banner" id="toastBanner">🚀 EaglePhone OS v5.0: Anime 10-App Grid, Sub-pages & Live Tables!</div>

  <!-- Sub-page / Back Navigation Bar (Shown when inside Apps 1..9) -->
  <div class="app-nav-header" id="appNavHeader" style="display:none;">
    <button class="nav-back-btn" onclick="act('nav_back', {})">◀ Back / Home (Bksp)</button>
    <span id="navAppTitle" style="font-size:11.5px;font-weight:800;color:#fde68a;">App</span>
    <div style="display:flex;gap:4px;">
      <button class="pill" onclick="act('step_subpage', {delta:-1})" data-en="◀ Subpage" data-vi="◀ Trang Con">◀ Subpage</button>
      <button class="pill active" onclick="act('step_subpage', {delta:1})" data-en="Subpage ▶" data-vi="Trang Con ▶">Subpage ▶</button>
    </div>
  </div>

  <div class="app-viewport">

    <!-- ==================== APP 0: SPRINGBOARD HOME SCREEN (3x3 ANIME ICON GRID) ==================== -->
    <div class="app-page active" id="page-0">
      <div class="mascot-widget">
        <div style="flex:1;">
          <div style="font-size:10px;color:#93c5fd;font-weight:800;text-transform:uppercase;" id="homeThemeTitle">✨ EAGLEPHONE OS v5.0 • GENSHIN EDITION</div>
          <div style="font-size:16px;font-weight:900;color:#fff;margin-top:2px;" id="homeGreetingTxt">Hi Aether! Wishing you a great cruise & big market wins~</div>
          <div style="font-size:11.5px;color:#fde68a;font-weight:700;margin-top:4px;" id="homeWeatherWalletTxt">☀️ Los Santos 26°C • Net Worth: $8,000</div>
          <div style="font-size:10px;color:#cbd5e1;margin-top:3px;" data-en="💡 In-game: I/K/J/L navigate • F9/Enter open App • Bksp return Home" data-vi="💡 Trong game: I/K/J/L di chuyển • F9/Enter mở App • Bksp về Home">💡 In-game: <b>I/K/J/L</b> navigate • <b>F9/Enter</b> open App • <b>Bksp</b> return Home</div>
        </div>
        <img id="homeMascotImg" src="/assets/ep_ms_furina.png" alt="Mascot">
      </div>

      <div class="home-grid" id="homeIconGrid"></div>

      <div class="card" style="padding:9px 11px;">
        <div class="card-title" style="margin-bottom:4px;">
          <span data-en="⚡ Quick Market & Status Summary" data-vi="⚡ Tóm Tắt Nhanh Thị Trường & Trạng Thái">⚡ Quick Market & Status Summary</span>
          <button class="pill" onclick="switchApp(9)" data-en="🎨 Theme & Language" data-vi="🎨 Đổi Hình Nền & Ngôn Ngữ">🎨 Theme & Language</button>
        </div>
        <div id="homeQuickSummary" style="font-size:11px;color:#cbd5e1;display:grid;grid-template-columns:repeat(2,1fr);gap:4px;"></div>
      </div>
    </div>

    <!-- ==================== APP 1: LIFE, SAVINGS & LOANS ==================== -->
    <div class="app-page" id="page-1">
      <div class="card">
        <img src="/assets/ep_cd_meal.png" class="visual-banner" alt="Meal Card">
        <div class="card-title">
          <span data-en="❤️ Vitality & In-Game Restaurant Auto-Sync" data-vi="❤️ Sinh Hoạt & Đồng Bộ Nhà Hàng Trong Game">❤️ Vitality & In-Game Restaurant Auto-Sync</span>
          <span style="color:#34d399;font-size:10px;" data-en="Auto Dining Detection" data-vi="Tự Động Nhận Diện Ăn Uống">Auto Dining Detection</span>
        </div>
        <p style="font-size:11px;color:var(--muted);margin-bottom:7px;">
          When Aether eats at any restaurant or vending machine in GTA SA, <b>Hunger & Energy automatically replenish</b>!
        </p>
        <div class="pbar-wrap">
          <div class="pbar-head"><span data-en="Character Health (GTA SA HP)" data-vi="Máu Nhân Vật (GTA SA Health)">Character Health (GTA SA HP)</span><span id="barHpTxt">100 / 100</span></div>
          <div class="pbar-bg"><div class="pbar-fill" id="barHp" style="width:100%;background:var(--red);"></div></div>
        </div>
        <div class="pbar-wrap">
          <div class="pbar-head"><span data-en="Fullness (Hunger)" data-vi="Độ No Bụng (Hunger)">Fullness (Hunger)</span><span id="barHungerTxt">88%</span></div>
          <div class="pbar-bg"><div class="pbar-fill" id="barHunger" style="width:88%;background:var(--gold);"></div></div>
        </div>
        <div class="pbar-wrap">
          <div class="pbar-head"><span data-en="Stamina (Energy)" data-vi="Năng Lượng (Energy)">Stamina (Energy)</span><span id="barEnergyTxt">92%</span></div>
          <div class="pbar-bg"><div class="pbar-fill" id="barEnergy" style="width:92%;background:var(--green);"></div></div>
        </div>
        <div class="btn-row">
          <button class="btn btn-gold" onclick="act('eat_meal', {tier:'burger'})" data-en="🍔 Burger (-$25 | +35% Hunger, +25 HP)" data-vi="🍔 Burger (-$25 | +35% No, +25 HP)">🍔 Burger (-$25 | +35% Hunger, +25 HP)</button>
          <button class="btn btn-blue" onclick="act('eat_meal', {tier:'drink'})" data-en="⚡ Energy Drink (-$15 | +30% Energy, +15 HP)" data-vi="⚡ Tăng Lực (-$15 | +30% Energy, +15 HP)">⚡ Energy Drink (-$15 | +30% Energy, +15 HP)</button>
          <button class="btn btn-purple" onclick="act('sleep_rest', {})" data-en="🛏️ Sleep Overnight (+1 Day, Full HP)" data-vi="🛏️ Ngủ Qua Đêm (+1 Ngày, Đầy HP)">🛏️ Sleep Overnight (+1 Day, Full HP)</button>
        </div>
      </div>

      <!-- ATM & Savings Account -->
      <div class="card">
        <img src="/assets/ep_cd_atm.png" class="visual-banner" alt="EagleBank Platinum Card">
        <div class="card-title">
          <span data-en="🏦 Banking & Savings Account (+1.5%/Day Yield)" data-vi="🏦 Ngân Hàng & Sổ Tiết Kiệm (Lãi +1.5%/Ngày)">🏦 Banking & Savings Account (+1.5%/Day Yield)</span>
          <span id="savingsBadge" style="color:#6ee7b7;">Tiết kiệm: $2,000</span>
        </div>
        <div style="display:flex;gap:6px;margin-bottom:6px;align-items:center;">
          <span style="font-size:11.5px;color:var(--muted);" data-en="Transaction Amount ($):" data-vi="Số tiền giao dịch ($):">Transaction Amount ($):</span>
          <input type="number" id="bankCustomAmt" value="1000" min="10" step="100" style="flex:1;" placeholder="Enter custom amount ($)">
        </div>
        <div class="btn-row">
          <button class="btn btn-green" onclick="act('bank_tx', {dir:'withdraw', amount:parseInt(document.getElementById('bankCustomAmt').value)||1000})" data-en="💵 ATM Withdraw" data-vi="💵 Rút ATM">💵 ATM Withdraw</button>
          <button class="btn btn-blue" onclick="act('bank_tx', {dir:'deposit', amount:parseInt(document.getElementById('bankCustomAmt').value)||1000})" data-en="🏦 ATM Deposit" data-vi="🏦 Nạp ATM">🏦 ATM Deposit</button>
          <button class="btn btn-gold" onclick="act('savings_tx', {dir:'deposit', amount:parseInt(document.getElementById('bankCustomAmt').value)||1000})" data-en="📈 Deposit Savings (+1.5%/d)" data-vi="📈 Gửi Tiết Kiệm (+1.5%/d)">📈 Deposit Savings (+1.5%/d)</button>
          <button class="btn" onclick="act('savings_tx', {dir:'withdraw', amount:parseInt(document.getElementById('bankCustomAmt').value)||1000})" data-en="📤 Withdraw Savings" data-vi="📤 Rút Tiết Kiệm">📤 Withdraw Savings</button>
        </div>
      </div>

      <!-- Loan System & Overdue Health Bleed -->
      <div class="card">
        <div class="card-title">
          <span data-en="🩸 Credit Loan & Overdue HP Drain" data-vi="🩸 Vay Vốn Tín Dụng & Cơ Chế Đòi Nợ Trừ Máu">🩸 Credit Loan & Overdue HP Drain</span>
          <span id="loanStatusBadge" style="color:#fde68a;">An Toàn</span>
        </div>
        <p style="font-size:11px;color:var(--muted);margin-bottom:7px;">
          Loan interest is <b>3%/day</b> (3-day term). If overdue, <b>Loan Sharks will drain Aether's HP (-2 HP per tick)</b> until repaid!
        </p>
        <div style="display:flex;gap:6px;margin-bottom:6px;align-items:center;">
          <span style="font-size:11.5px;color:var(--muted);" data-en="Borrow / Repay Amount ($):" data-vi="Số tiền Vay / Trả ($):">Borrow / Repay Amount ($):</span>
          <input type="number" id="loanCustomAmt" value="2000" min="100" step="500" style="flex:1;" placeholder="Enter borrow/repay amount ($)">
        </div>
        <div class="btn-row">
          <button class="btn btn-red" onclick="act('loan_tx', {dir:'borrow', amount:parseInt(document.getElementById('loanCustomAmt').value)||2000})" data-en="💳 Borrow Amount" data-vi="💳 Vay Theo Số Tiền Nhập">💳 Borrow Amount</button>
          <button class="btn btn-green" onclick="act('loan_tx', {dir:'repay', amount:parseInt(document.getElementById('loanCustomAmt').value)||2000})" data-en="✅ Repay Amount" data-vi="✅ Trả Nợ Theo Số Tiền Nhập">✅ Repay Amount</button>
          <button class="btn btn-green" onclick="act('loan_tx', {dir:'repay_all', amount:0})" data-en="✅ Pay Off Full Debt" data-vi="✅ Tất Toán Hết Nợ">✅ Pay Off Full Debt</button>
        </div>
      </div>
    </div>

    <!-- ==================== APP 2: STOCKS & GOLD/GEMS ==================== -->
    <div class="app-page" id="page-2">
      <div class="card">
        <div class="card-title">
          <span data-en="🏛️ Stocks (10) & Gold / Gems (6)" data-vi="🏛️ Chứng Khoán (10) & Vàng Đá Quý (6)">🏛️ Stocks (10) & Gold / Gems (6)</span>
          <div style="display:flex;gap:4px;">
            <button class="pill active" id="fltStockAll" onclick="setStockFilter('ALL')" data-en="All (16)" data-vi="Tất Cả (16)">All (16)</button>
            <button class="pill" id="fltStockOnly" onclick="setStockFilter('Stock')" data-en="Stocks" data-vi="Cổ Phiếu">Stocks</button>
            <button class="pill" id="fltCommOnly" onclick="setStockFilter('Commodity')" data-en="Gold/Gems" data-vi="Vàng/Đá Quý">Gold/Gems</button>
          </div>
        </div>
        <div class="pill-scroll" id="stockPills"></div>

        <div style="display:flex;justify-content:space-between;align-items:baseline;margin:7px 0 5px 0;">
          <div>
            <div style="font-size:15px;font-weight:800;" id="stSymName">XAU — Vàng Thế Giới</div>
            <div style="font-size:10.5px;color:var(--muted);" id="stStory">Bắt đầu từ 01/01/2010</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:17px;font-weight:900;" id="stPrice">$1,096.50</div>
            <div style="font-size:11.5px;font-weight:700;" id="stDelta">+1.15%</div>
          </div>
        </div>

        <div class="chart-box">
          <canvas id="stockCanvas" class="trade-canvas" width="760" height="210"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="⚡ Trade Stocks & Commodities (Spot / Futures)" data-vi="⚡ Giao Dịch Cổ Phiếu & Vàng Đá Quý (Spot / Futures)">⚡ Trade Stocks & Commodities (Spot / Futures)</span>
          <span id="stHoldingTxt" style="color:#fde68a;">Spot: 0</span>
        </div>
        <div style="display:flex;gap:6px;margin-bottom:7px;">
          <input type="number" id="stockUsdInput" value="500" min="50" step="100" style="flex:1;" placeholder="Số tiền ($)">
          <select id="stockLevInput" style="flex:1;">
            <option value="2">Leverage 2x</option>
            <option value="5">Leverage 5x</option>
            <option value="10" selected>Leverage 10x</option>
            <option value="20">Leverage 20x</option>
            <option value="50">Leverage 50x</option>
          </select>
        </div>
        <div class="btn-row">
          <button class="btn btn-blue" onclick="submitMarketOrder('stocks', 'spot_buy')" data-en="🛒 Buy Spot" data-vi="🛒 Mua Spot">🛒 Buy Spot</button>
          <button class="btn" onclick="submitMarketOrder('stocks', 'spot_sell')" data-en="💰 Sell Spot" data-vi="💰 Bán Spot">💰 Sell Spot</button>
          <button class="btn btn-green" onclick="submitMarketOrder('stocks', 'fut_long')" data-en="🚀 Open LONG" data-vi="🚀 Mở LONG">🚀 Open LONG</button>
          <button class="btn btn-red" onclick="submitMarketOrder('stocks', 'fut_short')" data-en="🩸 Open SHORT" data-vi="🩸 Mở SHORT">🩸 Open SHORT</button>
        </div>
        <div id="stockFuturesBox" style="margin-top:8px;font-size:11.5px;"></div>
      </div>

      <div class="card">
        <div class="card-title"><span data-en="📊 Market Watch Board (16 Stocks & Commodities)" data-vi="📊 Bảng Điện Tử Market Watch (16 Mã Cổ Phiếu & Vàng Đá Quý)">📊 Market Watch Board (16 Stocks & Commodities)</span></div>
        <div id="stockMarketWatchBox" style="max-height:190px;overflow-y:auto;"></div>
      </div>
    </div>

    <!-- ==================== APP 3: CRYPTO EXCHANGE ==================== -->
    <div class="app-page" id="page-3">
      <div class="card">
        <div class="card-title">
          <span data-en="🪙 Crypto Exchange (8 Coins • Dedicated Market)" data-vi="🪙 Sàn Tiền Điện Tử Crypto (Tách Biệt Chứng Khoán)">🪙 Crypto Exchange (8 Coins • Dedicated Market)</span>
          <span style="font-size:10px;color:#fde68a;">2010 -> 2025</span>
        </div>
        <div class="pill-scroll" id="cryptoPills"></div>

        <div style="display:flex;justify-content:space-between;align-items:baseline;margin:7px 0 5px 0;">
          <div>
            <div style="font-size:15px;font-weight:800;" id="crSymName">BTC — Bitcoin</div>
            <div style="font-size:10.5px;color:var(--muted);" id="crStory">Chỗ thiếu data giữ nguyên giá cũ</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:17px;font-weight:900;" id="crPrice">$0.08</div>
            <div style="font-size:11.5px;font-weight:700;" id="crDelta">+0.00%</div>
          </div>
        </div>

        <div class="chart-box">
          <canvas id="cryptoCanvas" class="trade-canvas" width="760" height="210"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="⚡ Trade Crypto Spot & Futures (2x - 50x)" data-vi="⚡ Giao Dịch Crypto Spot & Futures (2x - 50x)">⚡ Trade Crypto Spot & Futures (2x - 50x)</span>
          <span id="crHoldingTxt" style="color:#fde68a;">Spot: 0</span>
        </div>
        <div style="display:flex;gap:6px;margin-bottom:7px;">
          <input type="number" id="cryptoUsdInput" value="500" min="50" step="100" style="flex:1;" placeholder="Số tiền ($)">
          <select id="cryptoLevInput" style="flex:1;">
            <option value="2">Leverage 2x</option>
            <option value="5">Leverage 5x</option>
            <option value="10" selected>Leverage 10x</option>
            <option value="20">Leverage 20x</option>
            <option value="50">Leverage 50x</option>
          </select>
        </div>
        <div class="btn-row">
          <button class="btn btn-blue" onclick="submitMarketOrder('crypto', 'spot_buy')" data-en="🛒 Buy Coin Spot" data-vi="🛒 Mua Coin Spot">🛒 Buy Coin Spot</button>
          <button class="btn" onclick="submitMarketOrder('crypto', 'spot_sell')" data-en="💰 Sell Coin Spot" data-vi="💰 Bán Coin Spot">💰 Sell Coin Spot</button>
          <button class="btn btn-green" onclick="submitMarketOrder('crypto', 'fut_long')">🚀 Long Coin</button>
          <button class="btn btn-red" onclick="submitMarketOrder('crypto', 'fut_short')">🩸 Short Coin</button>
        </div>
        <div id="cryptoFuturesBox" style="margin-top:8px;font-size:11.5px;"></div>
      </div>

      <div class="card">
        <div class="card-title"><span data-en="📊 Crypto Market Watch Board (8 Coins)" data-vi="📊 Bảng Điện Tử Crypto Market Watch (8 Đồng Coin)">📊 Crypto Market Watch Board (8 Coins)</span></div>
        <div id="cryptoMarketWatchBox" style="max-height:190px;overflow-y:auto;"></div>
      </div>
    </div>

    <!-- ==================== APP 4: CHRONOLOGICAL SPORTSBOOK (MULTI-MATCH PER LEAGUE PAGE) ==================== -->
    <div class="app-page" id="page-4">
      <div class="card">
        <div class="card-title">
          <span id="sportSeasonHeader">⚽ Mùa Giải 1 • Tuần 1 (Mỗi Trang = 1 Giải Đấu Đầy Đủ)</span>
          <div style="display:flex;gap:4px;">
            <button class="pill" style="background:#2563eb;color:#fff;border:none;" onclick="simCurrentLeague()" data-en="⚡ Sim League" data-vi="⚡ Đá Giải Này">⚡ Sim League</button>
            <button class="pill" style="background:#059669;color:#fff;border:none;" onclick="act('sim_all_matches', {})" data-en="⚡ Sim All 5 Leagues" data-vi="⚡ Đá Tất Cả 5 Giải">⚡ Sim All 5 Leagues</button>
          </div>
        </div>
        <!-- League Page Switcher (Qua trang là qua giải khác!) -->
        <div class="pill-scroll" id="leaguePageTabs" style="margin-bottom:6px;"></div>
        <div class="btn-row">
          <button class="btn" onclick="stepLeaguePage(-1)" data-en="◀ Prev League" data-vi="◀ Trang Giải Trước">◀ Prev League</button>
          <button class="btn btn-blue" onclick="setSportSubTab('fixtures')" data-en="📅 Fixtures" data-vi="📅 DS Trận Của Giải">📅 Fixtures</button>
          <button class="btn" onclick="setSportSubTab('standings')" data-en="🏆 Standings" data-vi="🏆 BXH Giải Này">🏆 Standings</button>
          <button class="btn" onclick="setSportSubTab('history')" data-en="📜 History" data-vi="📜 Lịch Sử">📜 History</button>
          <button class="btn" onclick="stepLeaguePage(1)" data-en="Next League ▶" data-vi="Trang Giải Tiếp ▶">Next League ▶</button>
        </div>
      </div>

      <div class="card" id="sportSubFixtures">
        <div class="card-title">
          <span id="currentLeagueTitle">🔥 Ngoại Hạng Anh (5 Trận Trong Ngày)</span>
          <span>Stake ($): <input type="number" id="betStakeInput" value="200" min="10" step="50" style="width:82px;padding:3px 6px;"></span>
        </div>
        <div id="fixturesContainer"></div>
      </div>

      <div class="card" id="sportSubStandings" style="display:none;">
        <div class="card-title"><span id="standingsLeagueTitle">🏆 Bảng Xếp Hạng Giải Đấu</span></div>
        <div id="standingsContainer"></div>
      </div>

      <div class="card" id="sportSubHistory" style="display:none;">
        <div class="card-title"><span data-en="📜 Completed Match Results" data-vi="📜 Kết Quả Các Trận Đã Đá">📜 Completed Match Results</span></div>
        <div id="sportHistoryContainer"></div>
      </div>
    </div>

    <!-- ==================== APP 5: 4-SUBPAGE LOTTERY & CASINO ==================== -->
    <div class="app-page" id="page-5">
      <div class="card">
        <div class="card-title">
          <span data-en="🎰 EagleLotto Center (4 Dedicated Sub-pages)" data-vi="🎰 Trung Tâm Xổ Số EagleLotto (4 Trang Chuyên Biệt)">🎰 EagleLotto Center (4 Dedicated Sub-pages)</span>
          <span id="lottoJackpotTxt" style="color:#34d399;">Mega: $1.25M | Power: $3.20M</span>
        </div>
        <div class="pill-bar">
          <button class="pill active" id="lottoTab0" onclick="setLottoSubTab(0)" data-en="🎫 1. Scratch 3x3 (0s)" data-vi="🎫 1. Vé Cào 3x3 (0s)">🎫 1. Scratch 3x3 (0s)</button>
          <button class="pill" id="lottoTab1" onclick="setLottoSubTab(1)" data-en="🏛️ 2. XSKT & 2D/3D (16:30)" data-vi="🏛️ 2. XSKT & Lô Đề (16:30)">🏛️ 2. XSKT & 2D/3D (16:30)</button>
          <button class="pill" id="lottoTab2" onclick="setLottoSubTab(2)">💎 3. Vietlott 6/45 & 6/55 (18:00)</button>
          <button class="pill" id="lottoTab3" onclick="setLottoSubTab(3)" data-en="⚡ 4. Keno & Max 3D (0s)" data-vi="⚡ 4. Keno & Max 3D (0s)">⚡ 4. Keno & Max 3D (0s)</button>
        </div>
      </div>

      <!-- SUBPAGE 0: INSTANT SCRATCH CARD 3x3 -->
      <div class="card" id="lottoSub0">
        <div class="card-title"><span data-en="🎫 Page 1/4: 3x3 Matrix Scratch Card (Instant 0s Payout)" data-vi="🎫 Trang 1/4: Vé Số Cào Ma Trận 3x3 (Trả Thưởng Tức Thì 0 Giây)">🎫 Page 1/4: 3x3 Matrix Scratch Card (Instant 0s Payout)</span></div>
        <div class="scratch-grid" id="scratchGrid"></div>
        <div id="scratchResultTxt" style="font-size:11.5px;text-align:center;color:#6ee7b7;margin-bottom:6px;font-weight:700;"></div>
        <div class="btn-row">
          <button class="btn btn-blue" onclick="act('buy_scratch', {tier:'SILVER_20', combo:1})" data-en="🪙 Silver (-$20)" data-vi="🪙 Vé Bạc (-$20)">🪙 Silver (-$20)</button>
          <button class="btn btn-gold" onclick="act('buy_scratch', {tier:'GOLD_50', combo:1})" data-en="✨ Gold (-$50)" data-vi="✨ Vé Vàng (-$50)">✨ Gold (-$50)</button>
          <button class="btn btn-purple" onclick="act('buy_scratch', {tier:'GOLD_100', combo:1})" data-en="💎 Diamond (-$100)" data-vi="💎 Kim Cương (-$100)">💎 Diamond (-$100)</button>
          <button class="btn btn-green" onclick="act('buy_scratch', {tier:'VIP_500', combo:1})" data-en="👑 Fortune VIP (-$500)" data-vi="👑 Thần Tài VIP (-$500)">👑 Fortune VIP (-$500)</button>
        </div>
        <div class="btn-row" style="margin-top:6px;">
          <button class="btn btn-gold" onclick="act('buy_scratch', {tier:'GOLD_100', combo:5})" data-en="🔥 Quick Scratch 5x Diamond Combo (-$500)" data-vi="🔥 Cào Nhanh Combo 5 Vé Kim Cương (-$500)">🔥 Quick Scratch 5x Diamond Combo (-$500)</button>
        </div>
      </div>

      <!-- SUBPAGE 1: XSKT MIEN NAM & LO DE (16:30 EXCLUSIVE) -->
      <div class="card" id="lottoSub1" style="display:none;">
        <div class="card-title">
          <span data-en="🏛️ Page 2/4: Traditional 6D & 2D/3D Numbers (16:30 Draw)" data-vi="🏛️ Trang 2/4: Xổ Số Kiến Thiết & Lô Đề Miền Nam (Mở Thưởng 16:30)">🏛️ Page 2/4: Traditional 6D & 2D/3D Numbers (16:30 Draw)</span>
          <span style="color:#fde68a;" data-en="Grand Prize: $200,000" data-vi="Độc Biệt: $200,000">Grand Prize: $200,000</span>
        </div>
        <div id="xsktResultsBox" style="background:#081022;border:1px solid #1e3a8a;border-radius:8px;padding:7px;font-size:11.5px;margin-bottom:8px;"></div>
        <div style="display:flex;gap:6px;margin-bottom:6px;">
          <input type="text" id="xsktNumInput" placeholder="Enter 6-digit XSKT or 2/3-digit numbers (e.g. 686868)" style="flex:1;font-weight:800;color:#fde68a;">
          <input type="number" id="xsktStakeInput" value="100" min="10" step="50" style="width:85px;font-weight:800;color:#34d399;" title="Tiền cược Lô Đề ($)">
        </div>
        <div class="btn-row">
          <button class="btn btn-blue" onclick="buyXsktWeb('XSKT_6D')" data-en="🎫 6-Digit XSKT Ticket (-$10)" data-vi="🎫 Vé Kiến Thiết 6 Số (-$10)">🎫 6-Digit XSKT Ticket (-$10)</button>
          <button class="btn btn-gold" onclick="buyXsktWeb('LODE_DE')" data-en="🎯 2D Grand Tail (x70)" data-vi="🎯 Đánh Đề 2 Số ĐB (x70)">🎯 2D Grand Tail (x70)</button>
        </div>
        <div class="btn-row" style="margin-top:6px;">
          <button class="btn btn-green" onclick="buyXsktWeb('LODE_LO2')" data-en="📊 2D 18-Prize Roll (x3.5/hit)" data-vi="📊 Bao Lô 2 Số 18 Giải (x3.5/nháy)">📊 2D 18-Prize Roll (x3.5/hit)</button>
          <button class="btn btn-purple" onclick="buyXsktWeb('LODE_3CANG')" data-en="👑 3D Grand Tail (x400)" data-vi="👑 3 Càng Đặc Biệt (x400)">👑 3D Grand Tail (x400)</button>
        </div>
        <div class="btn-row" style="margin-top:6px;">
          <button class="btn" style="background:#0284c7;color:#fff;" onclick="act('draw_lottery_now', {filter_type:'XSKT_6D'})" data-en="🎰 Draw 16:30 XSKT Now (Separate from Vietlott)" data-vi="🎰 Quay Thử Kỳ XSKT 16:30 Ngay (Không Gộp Vietlott)">🎰 Draw 16:30 XSKT Now (Separate from Vietlott)</button>
        </div>
      </div>

      <!-- SUBPAGE 2: VIETLOTT 18:00 (MEGA 6/45 & POWER 6/55 ON SAME PAGE WITH SEPARATE PRIZE POOLS) -->
      <div class="card" id="lottoSub2" style="display:none;">
        <div class="card-title">
          <span data-en="💎 Page 3/4: Vietlott Jackpot (18:00 Draw • Separate Prize Pools)" data-vi="💎 Trang 3/4: Vietlott Điện Toán (Mở Thưởng 18:00 • Tách Biệt Prize Pool)">💎 Page 3/4: Vietlott Jackpot (18:00 Draw • Separate Prize Pools)</span>
        </div>
        <div id="vietlottPoolsBox" style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;"></div>
        <div style="display:flex;gap:6px;margin-bottom:6px;">
          <input type="text" id="vietlottBallsInput" placeholder="Enter 6 balls (e.g. 05-12-19-26-38-44) or leave blank for QuickPick" style="flex:1;font-weight:800;color:#6ee7b7;">
          <button class="btn" style="flex:0 0 70px;" onclick="document.getElementById('vietlottBallsInput').value=''" data-en="QuickPick" data-vi="Tự Chọn">QuickPick</button>
        </div>
        <div class="btn-row">
          <button class="btn btn-green" onclick="buyVietlottWeb('MEGA_645')" data-en="🟢 Buy Mega 6/45 Single (-$10)" data-vi="🟢 Mua Mega 6/45 Đơn (-$10)">🟢 Buy Mega 6/45 Single (-$10)</button>
          <button class="btn btn-purple" onclick="buyVietlottWeb('POWER_655')" data-en="🟣 Buy Power 6/55 Single (-$10)" data-vi="🟣 Mua Power 6/55 Đơn (-$10)">🟣 Buy Power 6/55 Single (-$10)</button>
        </div>
        <div class="btn-row" style="margin-top:6px;">
          <button class="btn btn-blue" onclick="buyVietlottWeb('MEGA_BAO7')" data-en="🔥 Mega 6/45 7-Ball System (-$70)" data-vi="🔥 Mega 6/45 Bao 7 Số (-$70)">🔥 Mega 6/45 7-Ball System (-$70)</button>
          <button class="btn btn-gold" onclick="buyVietlottWeb('POWER_BAO7')" data-en="👑 Power 6/55 7-Ball System (-$70)" data-vi="👑 Power 6/55 Bao 7 Số (-$70)">👑 Power 6/55 7-Ball System (-$70)</button>
        </div>
        <div class="btn-row" style="margin-top:6px;">
          <button class="btn" style="background:#7c3aed;color:#fff;" onclick="act('draw_lottery_now', {filter_type:'VIETLOTT'})" data-en="🎰 Draw 18:00 Vietlott Now (Separate 6/45 & 6/55)" data-vi="🎰 Quay Thử Kỳ Vietlott 18:00 Ngay (6/45 & 6/55 Riêng Biệt)">🎰 Draw 18:00 Vietlott Now (Separate 6/45 & 6/55)</button>
        </div>
      </div>

      <!-- SUBPAGE 3: KENO 20/80 & MAX 3D PRO INSTANT DRAW -->
      <div class="card" id="lottoSub3" style="display:none;">
        <div class="card-title">
          <span data-en="⚡ Page 4/4: Keno Express 20/80 & Max 3D Pro (Instant 0s Draw)" data-vi="⚡ Trang 4/4: Keno Quay Nhanh 20/80 & Max 3D Pro (Sổ Ngay 0 Giây)">⚡ Page 4/4: Keno Express 20/80 & Max 3D Pro (Instant 0s Draw)</span>
        </div>
        <div id="kenoResultsBox" style="background:#081022;border:1px solid #3b0764;border-radius:8px;padding:7px;font-size:11.5px;margin-bottom:8px;"></div>
        <div style="display:flex;gap:6px;margin-bottom:6px;">
          <input type="text" id="kenoNumbersInput" placeholder="Bộ số Bậc 3 / Max 3D (VD: 123456)" style="flex:1;font-weight:800;color:#fde68a;">
          <input type="number" id="kenoStakeInput" value="100" min="10" step="50" style="width:90px;font-weight:800;color:#34d399;" title="Tiền cược Keno ($)">
        </div>
        <div class="btn-row">
          <button class="btn btn-gold" onclick="playKenoWeb('KENO_TAI')" data-en="🔥 Big (&ge;811pts • x2.0)" data-vi="🔥 Tài (&ge;811đ • x2.0)">🔥 Big (&ge;811pts • x2.0)</button>
          <button class="btn btn-blue" onclick="playKenoWeb('KENO_XIU')" data-en="❄️ Small (&le;810pts • x2.0)" data-vi="❄️ Xỉu (&le;810đ • x2.0)">❄️ Small (&le;810pts • x2.0)</button>
          <button class="btn btn-green" onclick="playKenoWeb('KENO_CHAN')" data-en="⚡ Even (x2.2)" data-vi="⚡ Chẵn (x2.2)">⚡ Even (x2.2)</button>
          <button class="btn btn-purple" onclick="playKenoWeb('KENO_LE')" data-en="🌟 Odd (x2.2)" data-vi="🌟 Lẻ (x2.2)">🌟 Odd (x2.2)</button>
        </div>
        <div class="btn-row" style="margin-top:6px;">
          <button class="btn" onclick="playKenoWeb('KENO_KIM')">🪙 Kim (x2.4)</button>
          <button class="btn" onclick="playKenoWeb('KENO_MOC')">🌿 Mộc (x2.4)</button>
          <button class="btn" onclick="playKenoWeb('KENO_THUY')">💧 Thủy (x2.4)</button>
          <button class="btn" onclick="playKenoWeb('KENO_HOA')">🔥 Hỏa (x2.4)</button>
          <button class="btn" onclick="playKenoWeb('KENO_THO')">⛰️ Thổ (x2.4)</button>
        </div>
        <div class="btn-row" style="margin-top:6px;">
          <button class="btn btn-blue" onclick="playKenoWeb('KENO_BAC3')" data-en="🎯 Keno Pick-3 (x40)" data-vi="🎯 Keno Bậc 3 (Ăn x40)">🎯 Keno Pick-3 (x40)</button>
          <button class="btn btn-purple" onclick="playKenoWeb('MAX3D_PRO')" data-en="👑 Max 3D Pro Twin Trios (x400)" data-vi="👑 Max 3D Pro Bộ Đôi 3 Số (Ăn x400)">👑 Max 3D Pro Twin Trios (x400)</button>
        </div>
      </div>

      <!-- ACTIVE TICKETS SUMMARY -->
      <div class="card">
        <div id="lottoTicketsBox" style="font-size:11px;color:#cbd5e1;"></div>
      </div>
    </div>

    <!-- ==================== APP 6: DAILY NEWSPAPER (2010-2025) ==================== -->
    <div class="app-page" id="page-6">
      <div class="card">
        <div class="card-title">
          <span id="newsHeaderDate">📰 Báo Ngày EagleTimes — 01/01/2010</span>
          <div style="display:flex;gap:4px;">
            <button class="pill" onclick="act('advance_day', {delta: -1})" data-en="◀ Prev Day" data-vi="◀ Hôm Trước">◀ Prev Day</button>
            <button class="pill active" onclick="act('advance_day', {delta: 1})" data-en="Next Day ▶" data-vi="Ngày Tiếp ▶">Next Day ▶</button>
          </div>
        </div>
        <div class="news-paper">
          <img src="/assets/ep_bn_pol.png" class="visual-banner" alt="World Breaking News">
          <div class="news-sec">
            <h4 data-en="🌍 Desk 1: World & Geopolitical Headlines" data-vi="🌍 Chuyên Mục 1: Sự Kiện Chính Trị & Thế Giới Nổi Bật">🌍 Desk 1: World & Geopolitical Headlines</h4>
            <p id="newsPolTxt"></p>
          </div>
          <img src="/assets/ep_bn_fin.png" class="visual-banner" alt="Wall Street & Gold">
          <div class="news-sec" style="border-color:var(--gold);">
            <h4 data-en="🏛️ Desk 2: Wall Street, Stocks & Precious Metals" data-vi="🏛️ Chuyên Mục 2: Thị Trường Chứng Khoán & Vàng Bạc Đá Quý">🏛️ Desk 2: Wall Street, Stocks & Precious Metals</h4>
            <p id="newsFinTxt"></p>
          </div>
          <img src="/assets/ep_bn_wibu.png" class="visual-banner" alt="Crypto & Anime Culture">
          <div class="news-sec" style="border-color:var(--green);">
            <h4 data-en="🪙 Desk 3: Crypto, Tech & Anime/Game Culture" data-vi="🪙 Chuyên Mục 3: Bản Tin Crypto, Blockchain & Văn Hóa Anime">🪙 Desk 3: Crypto, Tech & Anime/Game Culture</h4>
            <p id="newsCryTxt"></p>
          </div>
          <img src="/assets/ep_bn_spt.png" class="visual-banner" alt="Sports Arena">
          <div class="news-sec" style="border-color:var(--purple);margin-bottom:0;">
            <h4 data-en="⚽🏀 Desk 4: Global Football & Pro Sports" data-vi="⚽🏀 Chuyên Mục 4: Toàn Cảnh Thể Thao & Giải Đấu">⚽🏀 Desk 4: Global Football & Pro Sports</h4>
            <p id="newsSptTxt"></p>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== APP 7: UNIFIED PORTFOLIO (STOCKS, CRYPTO, BETTING & LOTTERY) ==================== -->
    <div class="app-page" id="page-7">
      <div class="card">
        <div class="card-title">
          <span data-en="💼 Unified Investment Portfolio (All-in-One)" data-vi="💼 Danh Mục Đầu Tư Chung (Portfolio All-in-One)">💼 Unified Investment Portfolio (All-in-One)</span>
          <span id="portNetWorthBadge" style="color:#fbbf24;">Tài Sản Ròng: $8,000</span>
        </div>
        <!-- Asset Allocation Gauge Bar -->
        <div style="margin-bottom:9px;">
          <div style="display:flex;justify-content:space-between;font-size:10.5px;margin-bottom:3px;font-weight:700;" id="portAllocLegend">
            <span style="color:#fde68a;">Spot: 0%</span>
            <span style="color:#a855f7;">Futures: 0%</span>
            <span style="color:#34d399;">Tiền/Bank: 100%</span>
          </div>
          <div style="height:10px;background:#090e1a;border-radius:999px;overflow:hidden;display:flex;border:1px solid #1e293b;">
            <div id="portBarSpot" style="width:0%;background:#f59e0b;transition:width 0.25s;"></div>
            <div id="portBarFut" style="width:0%;background:#a855f7;transition:width 0.25s;"></div>
            <div id="portBarCash" style="width:100%;background:#10b981;transition:width 0.25s;"></div>
          </div>
        </div>
        <div class="port-grid" id="portOverviewGrid"></div>
        <div class="btn-row">
          <button class="btn btn-gold" onclick="act('sell_all_spot', {})" data-en="💰 Sell All Spot Holdings" data-vi="💰 Bán Chốt Lời Tất Cả Spot">💰 Sell All Spot Holdings</button>
          <button class="btn btn-red" onclick="act('close_all_futures', {})" data-en="⚡ Close All Futures" data-vi="⚡ Đóng Tất Cả Futures">⚡ Close All Futures</button>
          <button class="btn btn-green" onclick="act('settle_all_portfolio', {})" data-en="🎲 Settle All Bets & Draw Lottery" data-vi="🎲 Chấm Hết Kèo Bet & Quay Vé Số">🎲 Settle All Bets & Draw Lottery</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="🏛️🪙 Active Stocks, Gold & Crypto Spot Holdings" data-vi="🏛️🪙 Cổ Phiếu, Vàng Đá Quý & Crypto Spot Đang Nắm Giữ">🏛️🪙 Active Stocks, Gold & Crypto Spot Holdings</span>
          <span id="portSpotCountBadge" style="color:#6ee7b7;">0 mã</span>
        </div>
        <div id="portSpotContainer" style="font-size:11.5px;"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="🚀🩸 Open Long / Short Futures Positions" data-vi="🚀🩸 Vị Thế Long / Short Futures Đang Mở">🚀🩸 Open Long / Short Futures Positions</span>
          <span id="portFutCountBadge" style="color:#38bdf8;">0 lệnh</span>
        </div>
        <div id="portFuturesContainer" style="font-size:11.5px;"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="⚽🎰 Active Sports Bets & Pending Lottery Tickets" data-vi="⚽🎰 Kèo Thể Thao Đang Cược & Vé Số Chờ Quay">⚽🎰 Active Sports Bets & Pending Lottery Tickets</span>
          <span id="portBetLottoBadge" style="color:#c084fc;">0 kèo • 0 vé</span>
        </div>
        <div id="portBetLottoContainer" style="font-size:11.5px;"></div>
      </div>
    </div>

    <!-- ==================== APP 8: MAP BUG REPORTER, AUTO-INSPECTOR (.IPL/.COL) & UNSTUCK ==================== -->
    <div class="app-page" id="page-8">
      <div class="card" style="border-color:#ef4444;">
        <div class="card-title">
          <span data-en="📍 Live RAM Coordinates, 5s Trail & Quick Unstuck" data-vi="📍 Tọa Độ Thực Tế (RAM Live), Vệt 5s & Cứu Hộ Nhanh (Unstuck)">📍 Live RAM Coordinates, 5s Trail & Quick Unstuck</span>
          <span id="bugIndexBadge" style="color:#34d399;font-size:10px;">Index Sẵn Sàng</span>
        </div>
        <div class="port-grid" id="bugTelemetryGrid"></div>
        <div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 8px;margin-bottom:7px;font-size:11px;color:#a7f3d0;" id="bugTrailBox"></div>
        <div class="btn-row">
          <button class="btn btn-green" onclick="act('unstuck_player', {mode:'recall_3s'})" data-en="🛟 Safe Recall -3s (F12)" data-vi="🛟 Về Vị Trí An Toàn -3s (F12)">🛟 Safe Recall -3s (F12)</button>
          <button class="btn btn-blue" onclick="act('unstuck_player', {mode:'step_back_5m'})" data-en="↩️ Step Back 5m" data-vi="↩️ Lùi Lại 5m Thoát Kẹt">↩️ Step Back 5m</button>
          <button class="btn btn-gold" onclick="act('unstuck_player', {mode:'lift_surface'})" data-en="⬆️ Lift to Surface (+4.5m)" data-vi="⬆️ Nâng Lên Mặt Đất (+4.5m)">⬆️ Lift to Surface (+4.5m)</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="🐛 Log Map Bug (1-Click / F11) & Bug Category" data-vi="🐛 Ghi Nhận Bug Tọa Độ (1-Click / Phím F11) & Phân Loại Lỗi">🐛 Log Map Bug (1-Click / F11) & Bug Category</span>
          <span id="bugSavedCountBadge" style="color:#fde68a;">Đã lưu: 0 bug</span>
        </div>
        <div class="pill-row" id="bugCategoryPills"></div>
        <div style="display:flex;gap:6px;margin-bottom:7px;">
          <input type="text" id="bugNoteInput" placeholder="Optional note (e.g. Fell through stairs near police station)..." style="flex:1;">
        </div>
        <div class="btn-row">
          <button class="btn btn-red" onclick="submitBugReport()" data-en="🐛 Log Bug & Scan .IPL/.COL Now (F11)" data-vi="🐛 Ghi Nhận Bug & Quét .IPL/.COL Ngay (F11)">🐛 Log Bug & Scan .IPL/.COL Now (F11)</button>
          <button class="btn btn-blue" onclick="act('inspect_live_coords', {})" data-en="🔍 Live Scan 15m Radius" data-vi="🔍 Quét Trực Tiếp Bán Kính 15m">🔍 Live Scan 15m Radius</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="🔬 Auto-Inspector Diagnostics (15m Radius — .IPL / .IDE / .IMG / .COL)" data-vi="🔬 Chẩn Đoán Auto-Inspector (15m Quanh Nhân Vật — .IPL / .IDE / .IMG / .COL)">🔬 Auto-Inspector Diagnostics (15m Radius — .IPL / .IDE / .IMG / .COL)</span>
          <span id="bugPrimarySuspectBadge" style="color:#f87171;">Sẵn sàng</span>
        </div>
        <div id="bugDiagnosisBox" style="font-size:11.5px;margin-bottom:8px;"></div>
        <div id="bugSuspectsTableBox" style="font-size:11px;overflow-x:auto;"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="📋 Saved Bug Reports (docs/project-eagle/map-bug-reports.md)" data-vi="📋 Nhật Ký Bug Đã Lưu (docs/project-eagle/map-bug-reports.md)">📋 Saved Bug Reports (docs/project-eagle/map-bug-reports.md)</span>
          <span style="color:#93c5fd;font-size:10px;">Chuẩn Hóa Cho Agent & Discord</span>
        </div>
        <div id="bugReportsHistoryBox" style="font-size:11.5px;"></div>
      </div>

      <div class="card" style="border-color:#a855f7;">
        <div class="card-title">
          <span data-en="🛡️ On-Demand Deep Debugger, Pre-Flight Doctor & Auto-Probe Tester" data-vi="🛡️ Hệ Thống Debugger Chuyên Sâu, Doctor & Auto-Probe Theo Yêu Cầu">🛡️ On-Demand Deep Debugger, Pre-Flight Doctor & Auto-Probe Tester</span>
          <span id="dbgModeBadge" style="color:#34d399;font-size:10.5px;font-weight:800;">LITE [0% OVERHEAD]</span>
        </div>
        <div id="dbgOverviewBox" style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:7px 9px;margin-bottom:7px;font-size:11px;line-height:1.45;"></div>
        <div class="btn-row" style="margin-bottom:6px;">
          <button class="btn btn-gold" onclick="act('toggle_debug_mode', {})" data-en="🔬 Toggle LITE ⇄ DEEP DEBUG (Ctrl+Shift+F11)" data-vi="🔬 Bật/Tắt LITE ⇄ DEEP DEBUG (Ctrl+Shift+F11)">🔬 Toggle LITE ⇄ DEEP DEBUG (Ctrl+Shift+F11)</button>
          <button class="btn btn-green" onclick="act('run_preflight_doctor', {})" data-en="🩺 Run 10-Point Doctor" data-vi="🩺 Chạy Doctor 10 Điểm">🩺 Run 10-Point Doctor</button>
          <button class="btn btn-blue" onclick="act('analyze_latest_crash', {})" data-en="💥 Correlate Latest Crash" data-vi="💥 Phân Tích Crash Mới Nhất">💥 Correlate Latest Crash</button>
        </div>
        <div class="btn-row" style="margin-bottom:6px;">
          <button class="btn" onclick="act('cycle_probe_suite', {delta:1})" data-en="🧪 Switch Probe Suite" data-vi="🧪 Đổi Gói Auto-Probe">🧪 Switch Probe Suite</button>
          <button class="btn btn-red" onclick="act('toggle_auto_probe', {})" data-en="🚀 Start / Stop Auto-Probe Tour" data-vi="🚀 Chạy / Dừng Auto-Probe Tour">🚀 Start / Stop Auto-Probe Tour</button>
        </div>
        <div class="btn-row" style="margin-bottom:6px;">
          <button class="btn btn-blue" onclick="act('capture_forensic_snapshot', {})" data-en="📸 Camera X-Ray & PNG" data-vi="📸 Tia X-Quang Camera & Chụp PNG">📸 Camera X-Ray & PNG</button>
          <button class="btn btn-green" onclick="act('audit_live_scene', {})" data-en="🔎 Audit Live RAM Scene (55m)" data-vi="🔎 Kiểm Toán RAM Quanh 55m">🔎 Audit Live RAM Scene (55m)</button>
          <button class="btn btn-gold" onclick="act('inspect_npcs', {})" data-en="👥 Audit NPC Slots (RAM/IMG)" data-vi="👥 Kiểm Toán NPC (RAM/IMG)">👥 Audit NPC Slots (RAM/IMG)</button>
        </div>
        <div class="btn-row">
          <button class="btn" onclick="act('run_aether_test', {})" data-en="⚔️ Test Aether Rig (6-Step)" data-vi="⚔️ Test Rig Aether (6 Bước)">⚔️ Test Aether Rig (6-Step)</button>
          <button class="btn" onclick="act('run_route_crawler', {suite:'WIBU01_BRIDGE_SEAM'})" data-en="🤖 Crawl WIBU-01 Seam" data-vi="🤖 Bot Dò Đường WIBU-01">🤖 Crawl WIBU-01 Seam</button>
          <button class="btn" onclick="act('run_visual_contact_sheet', {suite:'WIBU01_TOUR'})" data-en="🖼️ Contact Sheet Tour" data-vi="🖼️ Chụp Contact Sheet">🖼️ Contact Sheet Tour</button>
        </div>
        <div id="dbgDetailsBox" style="margin-top:7px;font-size:11px;"></div>
      </div>
    </div>

    <!-- ==================== APP 9: SETTINGS & ANIME THEME CUSTOMIZER ==================== -->
    <div class="app-page" id="page-9">
      <div class="card">
        <div class="card-title">
          <span data-en="🖼️ 1. Select Anime / Genshin Wallpaper (.TXD & Web Sync)" data-vi="🖼️ 1. Chọn Hình Nền Anime / Genshin (.TXD & Web Sync)">🖼️ 1. Select Anime / Genshin Wallpaper (.TXD & Web Sync)</span>
          <span id="setWpBadge" style="color:#38bdf8;">Furina Hydro</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;" id="setWpGrid"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="✨ 2. Select Home Screen Mascot Widget" data-vi="✨ 2. Chọn Nhân Vật Mascot Widget Màn Hình Chính">✨ 2. Select Home Screen Mascot Widget</span>
          <span id="setMascotBadge" style="color:#fde68a;">Furina</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;" id="setMascotGrid"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="🎨 3. Neon Border Theme (Glassmorphism)" data-vi="🎨 3. Chủ Đề Viền Neon (Glassmorphism Theme)">🎨 3. Neon Border Theme (Glassmorphism)</span>
          <span id="setThemeBadge" style="color:#a855f7;">Hydro Cyan</span>
        </div>
        <div class="btn-row" id="setThemeGrid"></div>
      </div>

      <div class="card" style="border-color:#a855f7;">
        <div class="card-title">
          <span data-en="🌐 4. System Language (In-Game HUD & Web Sync)" data-vi="🌐 4. Ngôn Ngữ Hệ Thống (Đồng Bộ HUD Trong Game & Web)">🌐 4. System Language (In-Game HUD & Web Sync)</span>
          <span id="setLangBadge" style="color:#e9d5ff;">ENGLISH (EN)</span>
        </div>
        <div class="btn-row">
          <button class="btn btn-blue" id="btnLangEn" onclick="act('set_language',{lang:'en'})">🇬🇧 English (EN - Default)</button>
          <button class="btn" id="btnLangVi" onclick="act('set_language',{lang:'vi'})">🇻🇳 Tiếng Việt (VI)</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span data-en="⌨️ 5. In-Game Hotkey Controls (No Alt+Tab Needed)" data-vi="⌨️ 5. Sơ Đồ Phím Nóng Điều Khiển Trong Game (Không Cần Alt+Tab)">⌨️ 5. In-Game Hotkey Controls (No Alt+Tab Needed)</span>
        </div>
        <div style="font-size:11.5px;color:#cbd5e1;line-height:1.6;" id="settingsHotkeysBox">
          <div>• <b>F7:</b> Show / Hide EaglePhone OS v5.0 on the bottom-right of GTA SA (all Apps 1..10 including GG Map are inside F7).</div>
          <div>• <b>Backspace (or F8):</b> Back to Previous Page / Return to Home Screen.</div>
          <div>• <b>I / K / J / L:</b> 4-way D-Pad navigation on the 10-App Grid (1.Life/Bank .. 10.GG Map) or Tables.</div>
          <div>• <b>F9 / Enter:</b> Open selected App / Pin Red GPS Waypoint (T) / Execute command.</div>
          <div>• <b>F10:</b> Secondary action inside App (Clear GPS Waypoint in GG Map, Quick Buy / Draw).</div>
          <div>• <b>F6:</b> Toggle direct numeric keypad input (<code>0-9</code>).</div>
          <div>• <b>F11:</b> Log Map Bug immediately + Scan <code>.ipl/.ide/.img/.col</code> within 15m radius.</div>
          <div>• <b>F12:</b> Quick Unstuck Rescue (Safe Recall -3s) to free Aether from falling/clipping immediately.</div>
        </div>
      </div>
    </div>

    <!-- ==================== APP 10: GG MAP (GTA GENSHIN MAP) & AUTO GPS WAYPOINT ==================== -->
    <div class="app-page" id="page-10">
      <div class="card" style="border-color:#10b981;">
        <img src="/assets/ep_bn_map.png" class="visual-banner" alt="GG Map Banner">
        <div class="card-title">
          <span data-en="🗺️ GG Map (GTA Genshin Map) & Auto GPS Routing" data-vi="🗺️ GG Map (GTA Genshin Map) & Chỉ Đường GPS Tự Động">🗺️ GG Map (GTA Genshin Map) & Auto GPS Routing</span>
          <span id="ggmapTotalBadge" style="color:#6ee7b7;">83 Địa Điểm & Sự Kiện</span>
        </div>
        <div id="ggmapActiveGpsBox" style="margin-bottom:8px;"></div>
        <div class="pill-row" id="ggmapCatPills" style="margin-bottom:8px;"></div>
        <div style="display:flex;gap:6px;margin-bottom:6px;">
          <input type="text" id="ggmapSearchInput" oninput="renderAll()" placeholder="🔍 Search landmarks, events, Fight Club, bridges, airports, cities (e.g. Gant Bridge, Casino, Vice)..." style="flex:1;">
          <button class="btn" style="flex:0 0 80px;" onclick="document.getElementById('ggmapSearchInput').value='';renderAll();" data-en="Clear" data-vi="Xóa Lọc">Clear</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span id="ggmapListHeaderTitle">📍 Danh Sách Điểm Đến (Sắp Xếp Theo Khoảng Cách Thực Tế)</span>
          <span id="ggmapPlayerPosBadge" style="color:#93c5fd;font-size:10px;">X:0 Y:0 Z:0</span>
        </div>
        <div id="ggmapPoiListBox" style="max-height:460px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;"></div>
      </div>
    </div>

    <div class="app-page" id="page-11">
      <div class="card"><div class="card-title">Paimon - your companion</div>
        <div id="paimonStatus">AI connection pending</div><div id="paimonDate"></div>
        <div style="margin:12px 0;padding:12px;border:1px solid #e6ca9760;border-radius:8px;background:#172038;">
          <a href="/paimon" class="btn btn-blue" style="display:inline-block;text-decoration:none;">Try Paimon on web</a>
          <p style="margin:8px 0 0;color:#cbd5e1;">Visual novel dialogue, suggested replies and the existing AI. No GTA required; test memory stays separate.</p>
        </div>
        <p>Call Paimon beside you in game. Speak English; TAB ends the conversation.</p>
        <div class="btn-row"><button class="btn btn-blue" onclick="act('paimon_call',{mode:1})">Call Paimon &amp; talk</button></div>
        <div class="btn-row"><button class="btn" onclick="act('paimon_call',{mode:2})">Review portfolio</button><button class="btn" onclick="act('paimon_call',{mode:3})">Suggest activities</button></div>
        <div class="btn-row"><button class="btn" onclick="act('paimon_call',{mode:4})">Today's EagleTimes</button></div>
      </div><div class="card"><div class="card-title">Paimon's last reply</div><div id="paimonReply"></div></div>
    </div>

    <!-- ==================== APP 12: EAGLERIDE (UBER / XANH SM / GRAB / BE + RADIO + FAST-FORWARD) ==================== -->
    <div class="app-page" id="page-12">
      <div class="card" style="border-color:#06b6d4;">
        <img src="/assets/ep_bn_ride.png" class="visual-banner" alt="EagleRide Banner">
        <div class="card-title">
          <span data-en="🚕 EagleRide — Book Car / Bike (Uber • Xanh SM • Grab • Be)" data-vi="🚕 EagleRide — Đặt Xe Ô Tô / Xe Máy (Uber • Xanh SM • Grab • Be)">🚕 EagleRide — Book Car / Bike (Uber • Xanh SM • Grab • Be)</span>
          <span id="rideUnlockedBadge" style="color:#6ee7b7;">18/715 Đã Mở Khóa</span>
        </div>
        <div id="rideActiveTripBox" style="margin-bottom:8px;"></div>
        <div style="font-size:11px;font-weight:800;color:#fde68a;margin-bottom:4px;" data-en="🚘 1. Select Ride Brand & Vehicle Type (Keys 1..5 or U in-game):" data-vi="🚘 1. Chọn Hãng Xe Ô Tô / Xe Máy (Phím 1..5 hoặc U trong game):">🚘 1. Select Ride Brand & Vehicle Type (Keys 1..5 or U in-game):</div>
        <div id="rideServiceGrid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:5px;margin-bottom:8px;"></div>
        <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;flex-wrap:wrap;background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 9px;margin-bottom:8px;">
          <div style="font-size:11px;color:#93c5fd;">📻 <b data-en="Passenger Radio (Key O):" data-vi="Đài Radio Trên Xe (Phím O):">Passenger Radio (Key O):</b> <span id="rideRadioBadge" style="color:#fde68a;font-weight:800;">Flash FM</span></div>
          <div style="display:flex;gap:4px;">
            <button class="pill" onclick="act('ride_cycle_radio',{delta:-1})">◀ Radio</button>
            <button class="pill active" onclick="act('ride_cycle_radio',{delta:1})">Radio ▶</button>
          </div>
        </div>
        <div class="pill-row" id="rideCatPills" style="margin-bottom:8px;"></div>
        <div style="display:flex;gap:6px;">
          <input type="text" id="rideSearchInput" oninput="act('ride_set_search',{query:this.value});renderAll();" placeholder="🔍 Search destination, Mondstadt, WIBU-01, airport, casino, bridge..." style="flex:1;">
          <button class="btn" style="flex:0 0 80px;" onclick="document.getElementById('rideSearchInput').value='';act('ride_set_search',{query:''});renderAll();" data-en="Clear" data-vi="Xóa Lọc">Clear</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span id="rideListHeaderTitle">📍 Điểm Đến Đặt Xe (Chỉ Đặt Được Điểm Đã Tự Lái Tới)</span>
          <span id="rideStatsBadge" style="color:#93c5fd;font-size:10px;">0 chuyến • $0</span>
        </div>
        <div id="ridePoiListBox" style="max-height:440px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;"></div>
      </div>
    </div>

    <!-- ==================== APP 13: WAIFULINK v4.0 (TRAVELER AETHER VN + OPEN-WORLD + AI DATING SIM) ==================== -->
    <div class="app-page" id="page-13">
      <div class="card" style="border-color:#f472b6;padding:8px 10px;">
        <div class="card-title" style="margin-bottom:6px;flex-wrap:wrap;gap:4px;">
          <span>💖 WaifuLink v4.0 — VN + Open-World + AI Dating Sim</span>
          <div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap;">
            <span id="wlAiModelBadge" style="font-size:9.5px;background:#1e1b4b;color:#c4b5fd;border:1px solid #6366f1;padding:2px 7px;border-radius:999px;font-weight:800;">🤖 AI: gpt-6-luna</span>
            <span id="wlSafetyBadge" style="font-size:9.5px;background:#065f46;color:#6ee7b7;padding:2px 7px;border-radius:999px;font-weight:800;">🛡️ Hot Coffee: LOCKED</span>
          </div>
        </div>
        <!-- 6 Girlfriends Horizontal Selector -->
        <div id="wlRosterStrip" style="display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin-bottom:8px;"></div>
        <!-- Selected Girlfriend Header Card (Includes 3-Pillar Progression & Stage-Gate Lock) -->
        <div id="wlSelectedHeader" style="background:linear-gradient(135deg, rgba(15,23,42,0.96), rgba(49,16,47,0.88));border:1px solid #f472b6;border-radius:11px;padding:8px 10px;margin-bottom:8px;"></div>
        <!-- 5-Subtab Navigation -->
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px;">
          <button class="pill active" id="wlTabBtn-chat" onclick="setWaifuSubtab('chat')">💬 Chat</button>
          <button class="pill" id="wlTabBtn-scenarios" onclick="setWaifuSubtab('scenarios')">🎭 VN Scenarios</button>
          <button class="pill" id="wlTabBtn-dates" onclick="setWaifuSubtab('dates')">🚗 Outings &amp; Gifts</button>
          <button class="pill" id="wlTabBtn-profile" onclick="setWaifuSubtab('profile')">🧠 3-Tier Memory</button>
          <button class="pill" id="wlTabBtn-gallery" onclick="setWaifuSubtab('gallery')">📸 15 CGs &amp; Lore</button>
        </div>
      </div>

      <!-- SUBTAB 1: MESSENGER CHAT, LIVE AI SUGGESTED REPLIES & TIME-APART MILESTONE PHOTO DROPS -->
      <div id="wlSub-chat">
        <div class="card" style="padding:8px 10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:6px;flex-wrap:wrap;">
            <span style="font-size:10px;color:#93c5fd;font-weight:800;">📱 EaglePhone Small-Talk Pillar (+5..6 ♥/turn • Cap 45 ♥/Stage)</span>
            <button class="btn btn-gold" style="padding:3px 9px;font-size:10px;" onclick="act('dating_time_apart_drop',{})" title="Simulate time apart after reaching a milestone so she proactively texts you a new Milestone Photo + 3 reaction options!">
              ⏱️ Time Apart: Receive Milestone Photo
            </button>
          </div>
          <div id="wlChatMessagesBox" style="height:285px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;padding-right:4px;margin-bottom:8px;"></div>

          <!-- Live AI Recommended Dialogue Options (Updated every turn by gpt-6-luna or Milestone Photo Drop) -->
          <div style="font-size:10.5px;font-weight:800;color:#fde68a;margin-bottom:4px;">⚡ Live Recommended Dialogue Options (1-Click Reply):</div>
          <div id="wlSuggestedRepliesBox" style="display:flex;flex-direction:column;gap:4px;margin-bottom:7px;"></div>

          <!-- Pre-Generated Stage Chat Starters / Topics -->
          <div style="font-size:10px;font-weight:800;color:#f9a8d4;margin-bottom:4px;">📋 Pre-Generated Stage Chat Topics:</div>
          <div id="wlChoicesBox" style="display:flex;flex-direction:column;gap:4px;margin-bottom:8px;"></div>

          <div style="display:flex;gap:5px;">
            <input type="text" id="wlChatInput" onkeydown="if(event.key==='Enter')sendWaifuChat()" placeholder="Type freely as Traveler Aether (or click any recommended reply above)..." style="flex:1;">
            <button class="btn btn-purple" style="flex:0 0 auto;padding:6px 10px;" onclick="act('dating_time_apart_drop',{})" title="Trigger next Milestone CG Photo Drop">📸 CG</button>
            <button class="btn btn-blue" style="flex:0 0 auto;padding:6px 14px;" onclick="sendWaifuChat()">Send ➤</button>
          </div>
        </div>
      </div>

      <!-- SUBTAB 2: VISUAL NOVEL SCENARIOS (20 CORE + 10 EXTRA GENSHIN CAMEOS + 4 CGS EACH + ANTI-STUCK GUARDRAIL) -->
      <div id="wlSub-scenarios" style="display:none;">
        <div class="card">
          <div class="card-title" style="flex-wrap:wrap;gap:6px;">
            <span>🎭 30 Visual Novel Scenarios (20 Core + 10 Extra Genshin Cameos • 4 CGs/Scenario • +35 ♥)</span>
            <div style="display:flex;gap:5px;flex-wrap:wrap;">
              <button class="btn btn-gold" style="padding:4px 9px;font-size:10px;" onclick="act('dating_open_house_menu',{})">
                🏠 Visit Her House (Event Menu)
              </button>
              <button class="btn btn-purple" style="padding:4px 10px;font-size:10.5px;" onclick="act('dating_encore_vn',{})">
                ✨ + Generate AI Encore Scenario
              </button>
            </div>
          </div>
          <div style="font-size:10.5px;color:#cbd5e1;margin-bottom:8px;line-height:1.42;">
            Includes <b>20 Core Romance Scenarios</b> + <b>10 Extra Genshin Cameo &amp; Daily-Life Scenarios</b> (featuring <b>Xiangling, Xingqiu, Chongyun, Zhongli, Yun Jin, Keqing, Ganyu, Venti, Yoimiya &amp; Furina</b> with stage-responsive reactions: friendly hangouts → teasing sparks → caught red-handed on a date → soulmate blessings!). Every scenario has <b>4 unique 16:9 CGs</b>, pre-generated options + custom free-text input, and an <b>AI Off-Topic Re-Ask &amp; Anti-Stuck Guardrail</b>.
          </div>
          <div id="wlScenariosListBox" style="display:flex;flex-direction:column;gap:8px;max-height:480px;overflow-y:auto;"></div>
        </div>
      </div>

      <!-- SUBTAB 3: FREE-ROAM CHAUFFEUR OUTINGS & GIFT SHOP -->
      <div id="wlSub-dates" style="display:none;">
        <div class="card">
          <div class="card-title">
            <span>🚗 Free-Roam Chauffeur Outing (Cap 75 ♥ / Stage)</span>
            <span style="font-size:10px;color:#6ee7b7;">S-Rank Smooth +25 ♥ • Safe +20 ♥</span>
          </div>
          <div style="font-size:10.5px;color:#cbd5e1;margin-bottom:7px;line-height:1.4;">
            Pin a Date Spot on your GTA SA radar and drive her there cleanly without crashing or getting a Wanted Star!
          </div>
          <div id="wlActiveFreeroamBanner" style="margin-bottom:8px;"></div>
          <div id="wlDateSpotsBox" style="display:flex;flex-direction:column;gap:6px;"></div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>🎁 Send Gift Delivery (Uses GTA SA Cash)</span>
            <span style="font-size:10px;color:#fde68a;">★ Favored = 1.4x Bonus</span>
          </div>
          <div id="wlGiftsBox" style="display:flex;flex-direction:column;gap:6px;"></div>
        </div>
      </div>

      <!-- SUBTAB 4: 3-TIER HIERARCHICAL MEMORY (L1 WORKING / L2 EPISODIC / L3 ON-DEMAND ARCHIVE) -->
      <div id="wlSub-profile" style="display:none;">
        <div class="card">
          <div class="card-title">
            <span>🧠 3-Tier Hierarchical Memory Architecture (L1 / L2 / L3)</span>
            <span id="wlMemCountBadge" style="font-size:10px;color:#c084fc;">0 notes</span>
          </div>
          <div style="font-size:10.5px;color:#94a3b8;margin-bottom:6px;line-height:1.4;">
            Small talk only loads compact <b>Tier 1 (L1 Working Digest)</b>; scenarios load <b>Tier 2 (L2 Episodic Summaries)</b>; <b>Tier 3 (L3 Deep Lore &amp; Past Quests)</b> is retrieved on-demand when your message mentions matching keywords!
          </div>
          <div id="wlTieredMemoryBox" style="margin-bottom:8px;"></div>
          <div style="display:flex;gap:5px;margin-bottom:8px;">
            <input type="text" id="wlMemInput" onkeydown="if(event.key==='Enter')addWaifuMemory()" placeholder="Add custom L1/L3 memory note for her to remember..." style="flex:1;">
            <button class="btn btn-purple" style="flex:0 0 auto;padding:5px 10px;" onclick="addWaifuMemory()">+ Save Note</button>
          </div>
          <div id="wlMemoriesListBox" style="display:flex;flex-direction:column;gap:5px;max-height:190px;overflow-y:auto;"></div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>📖 5-Layer Character Dossier &amp; GTA SA Sync</span>
          </div>
          <div id="wlDossierBox" style="font-size:11.5px;color:#e2e8f0;line-height:1.45;"></div>
          <div class="btn-row" style="margin-top:8px;">
            <button class="btn btn-green" onclick="act('dating_sync_ram',{})">🔓 Unlock &amp; Sync All 6 in GTA RAM</button>
            <button class="btn btn-gold" onclick="act('dating_toggle_blips',{})">🌙 Toggle Vanilla Blips ($406)</button>
          </div>
        </div>
      </div>

      <!-- SUBTAB 5: 15 MILESTONE CGS (M01..M15), VISUAL APPEARANCE & COMPLETED PAST QUESTS -->
      <div id="wlSub-gallery" style="display:none;">
        <div class="card">
          <div class="card-title">
            <span>📸 Milestone Photo Album (15 CGs for Hu Tao: Friendly → Romantic → Spicy)</span>
            <span id="wlGalleryCountBadge" style="font-size:10px;color:#f9a8d4;">Unlocked</span>
          </div>
          <div id="wlGalleryGrid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;"></div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>👗 Canonical Visual Appearance &amp; Outfit Bible</span>
            <span id="wlVisualSkinBadge" style="font-size:10px;color:#6ee7b7;">Skin Info</span>
          </div>
          <div id="wlVisualBox" style="font-size:11.5px;color:#e2e8f0;line-height:1.48;"></div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>⚔️ Completed Past Quests &amp; Events with Traveler Aether (L3 Archive)</span>
            <span style="font-size:10px;color:#fde68a;">Past Shared History</span>
          </div>
          <div id="wlQuestsBox" style="display:flex;flex-direction:column;gap:6px;"></div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>🤝 Character Network &amp; Interactions</span>
            <span style="font-size:10px;color:#93c5fd;">Teyvat &amp; San Andreas</span>
          </div>
          <div id="wlRelationsBox" style="display:flex;flex-direction:column;gap:5px;"></div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>🎙️ Canonical Voice-Overs, Teapot Lines &amp; Fanfic Tropes</span>
          </div>
          <div id="wlQuotesBox" style="font-size:11px;color:#e2e8f0;line-height:1.45;"></div>
        </div>
      </div>
    </div>

    <!-- GIRLFRIEND HOUSE DOORSTEP EVENT SELECTOR MODAL -->
    <div id="wlHouseVisitModal" style="display:none;position:fixed;inset:0;background:rgba(4,7,17,0.93);z-index:9997;align-items:center;justify-content:center;padding:12px;">
      <div id="wlHouseVisitContent" style="max-width:540px;width:100%;max-height:92vh;overflow-y:auto;background:linear-gradient(180deg,#0f172a 0%,#1e1028 100%);border:2px solid #fbbf24;border-radius:18px;box-shadow:0 24px 70px rgba(0,0,0,0.95);padding:14px;"></div>
    </div>

    <!-- FULLSCREEN VISUAL NOVEL DATING SIM OVERLAY MODAL -->
    <div id="wlVnOverlayModal" style="display:none;position:fixed;inset:0;background:rgba(4,7,17,0.96);z-index:9998;align-items:center;justify-content:center;padding:12px;">
      <div id="wlVnOverlayContent" style="max-width:1180px;width:96vw;max-height:94vh;overflow:hidden;background:#05040c;border:2px solid rgba(244,114,182,0.75);border-radius:16px;box-shadow:0 24px 70px rgba(0,0,0,0.95);"></div>
    </div>

    <!-- FULLSCREEN PHOTO LIGHTBOX MODAL -->
    <div id="wlLightboxModal" onclick="closeWaifuLightbox()" style="display:none;position:fixed;inset:0;background:rgba(4,7,17,0.92);z-index:9999;align-items:center;justify-content:center;padding:16px;">
      <div onclick="event.stopPropagation()" style="max-width:460px;width:100%;background:#0f172a;border:2px solid #f472b6;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.9);">
        <img id="wlLightboxImg" src="" alt="Girlfriend Photo" style="width:100%;max-height:520px;object-fit:cover;display:block;">
        <div style="padding:12px 14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <b id="wlLightboxTitle" style="font-size:13.5px;color:#fde68a;"></b>
            <span id="wlLightboxChar" style="font-size:10.5px;background:#831843;color:#fbcfe8;padding:2px 8px;border-radius:999px;font-weight:800;"></span>
          </div>
          <div id="wlLightboxCaption" style="font-size:12px;color:#e2e8f0;line-height:1.45;font-style:italic;"></div>
          <div style="margin-top:10px;text-align:right;">
            <button class="btn btn-red" style="padding:5px 14px;" onclick="closeWaifuLightbox()">Close ✕</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== APP 14: UNIFIED CONTACTS (14 MONDSTADT NPCS + 6 WAIFUS) ==================== -->
  <div class="app-page" id="page-14">
    <div class="card" style="background:linear-gradient(135deg,#09192f 0%,#0f2942 60%,#131c38 100%);border-color:#38bdf8;">
      <div class="card-title" style="margin-bottom:4px;">
        <span>📱 Contacts &amp; Social Links (14 Mondstadt + 6 Waifus)</span>
        <span id="ctUnlockBadge" style="font-size:10.5px;background:#0369a1;color:#e0f2fe;padding:2px 8px;border-radius:999px;font-weight:800;">6/20 Unlocked</span>
      </div>
      <div style="font-size:11px;color:#cbd5e1;line-height:1.42;margin-bottom:8px;">
        Meet Mondstadt characters face-to-face on the map (<b>[E]</b>) to exchange contacts and unlock remote messaging! Remote DMs share the exact same <b>SQLite conversation history &amp; memories</b> as in-person Persona talks.
      </div>
      <div style="display:flex;gap:5px;flex-wrap:wrap;">
        <button class="pill active" id="ctTabBtn-0" onclick="act('contacts_set_tab',{tab_idx:0})">All (20)</button>
        <button class="pill" id="ctTabBtn-1" onclick="act('contacts_set_tab',{tab_idx:1})">🍃 Mondstadt (14)</button>
        <button class="pill" id="ctTabBtn-2" onclick="act('contacts_set_tab',{tab_idx:2})">💖 Waifus (6)</button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <span>📋 Directory</span>
        <span style="font-size:10px;color:#93c5fd;">Click any contact to DM or Pin GPS</span>
      </div>
      <div id="ctListBox" style="display:flex;flex-direction:column;gap:6px;max-height:240px;overflow-y:auto;"></div>
    </div>

    <div class="card" id="ctChatCard">
      <div class="card-title">
        <span id="ctSelHeader">💬 Messenger</span>
        <div style="display:flex;gap:5px;">
          <button class="pill" onclick="act('contacts_pin_gps',{})">📍 Pin GPS</button>
        </div>
      </div>
      <div id="ctChatBody"></div>
    </div>
  </div>

  <!-- 15-Button Bottom Dock (Home 0 + Apps 1..14) -->
  <div class="app-dock">
    <button class="dock-btn active" id="dock-0" onclick="switchApp(0)"><span class="icon">🏠</span><span>Home</span></button>
    <button class="dock-btn" id="dock-1" onclick="switchApp(1)"><span class="icon">❤️</span><span data-en="Life" data-vi="SinhHoạt">Life</span></button>
    <button class="dock-btn" id="dock-2" onclick="switchApp(2)"><span class="icon">🏛️</span><span data-en="Stocks" data-vi="CổPhiếu">Stocks</span></button>
    <button class="dock-btn" id="dock-3" onclick="switchApp(3)"><span class="icon">🪙</span><span>Crypto</span></button>
    <button class="dock-btn" id="dock-4" onclick="switchApp(4)"><span class="icon">⚽</span><span data-en="Sports" data-vi="ThểThao">Sports</span></button>
    <button class="dock-btn" id="dock-5" onclick="switchApp(5)"><span class="icon">🎰</span><span data-en="Lotto" data-vi="VéSố">Lotto</span></button>
    <button class="dock-btn" id="dock-6" onclick="switchApp(6)"><span class="icon">📰</span><span data-en="News" data-vi="BáoNgày">News</span></button>
    <button class="dock-btn" id="dock-7" onclick="switchApp(7)"><span class="icon">💼</span><span data-en="Portfolio" data-vi="DanhMục">Portfolio</span></button>
    <button class="dock-btn" id="dock-8" onclick="switchApp(8)"><span class="icon">🐛</span><span data-en="MapBug" data-vi="BáoBug">MapBug</span></button>
    <button class="dock-btn" id="dock-9" onclick="switchApp(9)"><span class="icon">⚙️</span><span data-en="Settings" data-vi="CàiĐặt">Settings</span></button>
    <button class="dock-btn" id="dock-10" onclick="switchApp(10)"><span class="icon">🗺️</span><span>GGMap</span></button>
    <button class="dock-btn" id="dock-11" onclick="switchApp(11)"><span class="icon">✨</span><span>Paimon</span></button>
    <button class="dock-btn" id="dock-12" onclick="switchApp(12)"><span class="icon">🚕</span><span>Ride</span></button>
    <button class="dock-btn" id="dock-13" onclick="switchApp(13)"><span class="icon">💖</span><span>Waifu</span></button>
    <button class="dock-btn" id="dock-14" onclick="switchApp(14)"><span class="icon">📱</span><span data-en="Contacts" data-vi="DanhBạ">Contacts</span></button>
  </div>
</div>

<script>
let STATE = null;
let currentAppId = 0;
let userLockedApp = false;
let selectedStockSym = 'XAU';
let selectedCryptoSym = 'BTC';
let stockFilter = 'ALL';
const LEAGUE_PAGES = [
  {id: 'EPL', short: '1.Premier League', short_vi: '1.Ngoại Hạng Anh', name: 'Premier League'},
  {id: 'LALIGA', short: '2.La Liga', short_vi: '2.La Liga', name: 'La Liga Santander'},
  {id: 'SERIE_BUND', short: '3.SerieA/Bund', short_vi: '3.SerieA/Bund', name: 'Serie A & Bundesliga'},
  {id: 'UCL', short: '4.UCL Champions', short_vi: '4.Cúp C1 UCL', name: 'UEFA Champions League'},
  {id: 'NBA', short: '5.NBA Basketball', short_vi: '5.Bóng Rổ NBA', name: 'NBA Regular Season'}
];
let selectedLeagueIdx = 0;

function stepLeaguePage(delta) {
  selectedLeagueIdx = (selectedLeagueIdx + delta + LEAGUE_PAGES.length) % LEAGUE_PAGES.length;
  const lg = LEAGUE_PAGES[selectedLeagueIdx];
  act('select_league_page', {league_idx: selectedLeagueIdx, league_id: lg.id});
}

function selectLeaguePage(idx) {
  selectedLeagueIdx = ((idx % LEAGUE_PAGES.length) + LEAGUE_PAGES.length) % LEAGUE_PAGES.length;
  const lg = LEAGUE_PAGES[selectedLeagueIdx];
  act('select_league_page', {league_idx: selectedLeagueIdx, league_id: lg.id});
}

function simCurrentLeague() {
  const lg = LEAGUE_PAGES[selectedLeagueIdx];
  act('sim_league_matches', {league_id: lg.id});
}

function toggleFrameMode() {
  document.getElementById('phoneFrame').classList.toggle('tablet-mode');
  setTimeout(() => { drawAssetChart('stockCanvas', STATE?.stocks_market?.[selectedStockSym]); drawAssetChart('cryptoCanvas', STATE?.crypto_market?.[selectedCryptoSym]); }, 50);
}

function applyActiveAppDOM(appId) {
  currentAppId = appId;
  for (let i = 0; i <= 14; i++) {
    const pg = document.getElementById('page-' + i);
    const dk = document.getElementById('dock-' + i);
    if (pg) pg.classList.toggle('active', i === appId);
    if (dk) dk.classList.toggle('active', i === appId);
  }
  const pf = document.getElementById('phoneFrame');
  if (pf) pf.classList.toggle('on-home', appId === 0);
  const navHdr = document.getElementById('appNavHeader');
  if (navHdr) navHdr.style.display = (appId === 0) ? 'none' : 'flex';
}

let wlActiveSubtab = 'chat';
let wlLastMsgCount = 0;
let wlLastCharId = '';

function setWaifuSubtab(tab) {
  wlActiveSubtab = tab;
  ['chat', 'scenarios', 'dates', 'profile', 'gallery'].forEach(t => {
    const box = document.getElementById('wlSub-' + t);
    const btn = document.getElementById('wlTabBtn-' + t);
    if (box) box.style.display = (t === tab) ? 'block' : 'none';
    if (btn) btn.classList.toggle('active', t === tab);
  });
  act('dating_set_subtab', {subtab: tab});
}

function sendVnFreeText() {
  const inp = document.getElementById('wlVnFreeTextInput');
  if (!inp) return;
  const txt = inp.value.trim();
  if (!txt) return;
  inp.value = '';
  act('dating_choose_vn', {free_text: txt});
}

function sendWaifuChat() {
  const inp = document.getElementById('wlChatInput');
  if (!inp) return;
  const txt = inp.value.trim();
  if (!txt) return;
  inp.value = '';
  act('dating_send_message', {text: txt});
}

function addWaifuMemory() {
  const inp = document.getElementById('wlMemInput');
  if (!inp) return;
  const txt = inp.value.trim();
  if (!txt) return;
  inp.value = '';
  act('dating_add_memory', {text: txt});
}

function openWaifuLightbox(url, title, charName, caption) {
  const modal = document.getElementById('wlLightboxModal');
  if (!modal) return;
  document.getElementById('wlLightboxImg').src = url;
  document.getElementById('wlLightboxTitle').textContent = title || 'Smartphone Snapshot';
  document.getElementById('wlLightboxChar').textContent = '📸 ' + (charName || 'Girlfriend');
  document.getElementById('wlLightboxCaption').textContent = '"' + (caption || '') + '"';
  modal.style.display = 'flex';
}

function closeWaifuLightbox() {
  const modal = document.getElementById('wlLightboxModal');
  if (modal) modal.style.display = 'none';
}

function switchApp(appId) {
  applyActiveAppDOM(appId);
  act('set_phone_app', {app: appId});
  if (appId === 2 || appId === 3) {
    setTimeout(() => {
      drawAssetChart('stockCanvas', STATE?.stocks_market?.[selectedStockSym]);
      drawAssetChart('cryptoCanvas', STATE?.crypto_market?.[selectedCryptoSym]);
    }, 40);
  }
}

function submitBugReport() {
  const noteEl = document.getElementById('bugNoteInput');
  const note = noteEl ? noteEl.value.trim() : '';
  act('report_map_bug', {note});
  if (noteEl) noteEl.value = '';
}

function copyDiscordBug(idx) {
  const rep = STATE?.bug_inspector?.reports?.[idx];
  if (!rep || !rep.discord_snippet) return;
  navigator.clipboard.writeText(rep.discord_snippet);
  document.getElementById('toastBanner').textContent = `📋 Đã copy mẫu báo bug #${rep.id} chuẩn Discord vào Clipboard!`;
}

function setStockFilter(flt) {
  stockFilter = flt;
  document.getElementById('fltStockAll').classList.toggle('active', flt === 'ALL');
  document.getElementById('fltStockOnly').classList.toggle('active', flt === 'Stock');
  document.getElementById('fltCommOnly').classList.toggle('active', flt === 'Commodity');
  renderAll();
}

function setSportSubTab(tab) {
  document.getElementById('sportSubFixtures').style.display = (tab === 'fixtures') ? 'block' : 'none';
  document.getElementById('sportSubStandings').style.display = (tab === 'standings') ? 'block' : 'none';
  document.getElementById('sportSubHistory').style.display = (tab === 'history') ? 'block' : 'none';
}

let lottoSubTabIdx = 0;
function setLottoSubTab(idx) {
  lottoSubTabIdx = idx;
  for (let i = 0; i < 4; i++) {
    const el = document.getElementById('lottoSub' + i);
    const tb = document.getElementById('lottoTab' + i);
    if (el) el.style.display = (i === idx) ? 'block' : 'none';
    if (tb) tb.classList.toggle('active', i === idx);
  }
}

function buyXsktWeb(mode) {
  const num = (document.getElementById('xsktNumInput').value || '').trim();
  const stake = parseInt(document.getElementById('xsktStakeInput').value) || 100;
  act('buy_lotto_6d', {mode, number: num, stake});
}

function buyVietlottWeb(game) {
  const raw = (document.getElementById('vietlottBallsInput').value || '').trim();
  act('buy_vietlott', {game, numbers: raw});
}

function playKenoWeb(mode) {
  const num = (document.getElementById('kenoNumbersInput').value || '').trim();
  const stake = parseInt(document.getElementById('kenoStakeInput').value) || 100;
  act('play_keno', {mode, stake, numbers: num});
}

async function act(action, payload) {
  try {
    const res = await fetch('/api/action', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action, ...payload})
    });
    STATE = await res.json();
    renderAll();
  } catch (e) { console.error(e); }
}

function submitMarketOrder(marketGroup, mode) {
  const isCrypto = (marketGroup === 'crypto');
  const sym = isCrypto ? selectedCryptoSym : selectedStockSym;
  const usd = parseFloat(document.getElementById(isCrypto ? 'cryptoUsdInput' : 'stockUsdInput').value) || 500;
  const lev = parseInt(document.getElementById(isCrypto ? 'cryptoLevInput' : 'stockLevInput').value) || 10;
  act('trade_order', {market_group: marketGroup, symbol: sym, mode, usd, leverage: lev});
}

function placeSportBet(matchId, pick, label) {
  const stake = parseInt(document.getElementById('betStakeInput').value) || 200;
  act('place_bet', {match_id: matchId, pick, stake, label});
}

function drawAssetChart(canvasId, asset) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !asset || !asset.candles || !asset.candles.length) return;
  const candles = asset.candles;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  let minP = Infinity, maxP = -Infinity;
  candles.forEach(c => { if (c.l < minP) minP = c.l; if (c.h > maxP) maxP = c.h; });
  const span = Math.max(maxP - minP, minP * 0.005, 0.0001);
  const padT = 12, padB = 16, padL = 8, padR = 58;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const yOf = (p) => padT + plotH - ((p - minP) / span) * plotH;

  ctx.strokeStyle = '#162038'; ctx.lineWidth = 1; ctx.fillStyle = '#64748b'; ctx.font = '10px Segoe UI';
  for (let i = 0; i <= 4; i++) {
    const gy = padT + (plotH * i) / 4;
    const gp = maxP - (span * i) / 4;
    ctx.beginPath(); ctx.moveTo(padL, gy); ctx.lineTo(W - padR, gy); ctx.stroke();
    ctx.fillText(gp >= 10 ? gp.toFixed(1) : gp.toFixed(4), W - padR + 4, gy + 3);
  }

  const n = candles.length;
  const stepX = plotW / n;
  const bodyW = Math.max(3, stepX * 0.62);

  candles.forEach((c, idx) => {
    const cx = padL + idx * stepX + stepX * 0.5;
    const isUp = c.c >= c.o;
    ctx.strokeStyle = isUp ? '#10b981' : '#ef4444';
    ctx.fillStyle = isUp ? '#10b981' : '#ef4444';
    ctx.beginPath(); ctx.moveTo(cx, yOf(c.h)); ctx.lineTo(cx, yOf(c.l)); ctx.stroke();
    const topY = Math.min(yOf(c.o), yOf(c.c));
    const bh = Math.max(2, Math.abs(yOf(c.c) - yOf(c.o)));
    ctx.fillRect(cx - bodyW / 2, topY, bodyW, bh);
  });

  // MA7 line
  ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 1.4; ctx.beginPath();
  let started = false;
  for (let i = 6; i < n; i++) {
    let s = 0; for (let k = i - 6; k <= i; k++) s += candles[k].c;
    const cx = padL + i * stepX + stepX * 0.5, cy = yOf(s / 7);
    if (!started) { ctx.moveTo(cx, cy); started = true; } else ctx.lineTo(cx, cy);
  }
  ctx.stroke();
}

function renderFuturesBox(boxId, list) {
  const el = document.getElementById(boxId);
  if (!list || list.length === 0) {
    el.innerHTML = `<div style="color:var(--muted);">${(STATE && STATE.lang === 'vi') ? 'Chưa có vị thế Long/Short nào đang mở.' : 'No open Long/Short Futures positions.'}</div>`;
    return;
  }
  el.innerHTML = list.map(f => {
    const col = f.pnl >= 0 ? '#34d399' : '#f87171';
    return `<div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 8px;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center;">
      <div><b style="color:${f.side==='LONG'?'#34d399':'#f87171'}">${f.side} ${f.leverage}x ${f.symbol}</b> <span style="color:#94a3b8;">Vốn $${f.margin} | Entry $${f.entry} | Liq $${f.liq_price}</span></div>
      <div style="display:flex;gap:6px;align-items:center;">
        <b style="color:${col}">${f.pnl>=0?'+':''}$${f.pnl.toFixed(1)} (${f.roe_pct>=0?'+':''}${f.roe_pct.toFixed(1)}%)</b>
        <button class="pill" style="background:#dc2626;color:#fff;border:none;" onclick="act('close_future',{id:'${f.id}'})">Đóng</button>
      </div>
    </div>`;
  }).join('');
}

function renderAll() {
  if (!STATE) return;
  const paimon = STATE.paimon || {};
  document.getElementById('paimonStatus').textContent = paimon.status || 'AI connection pending';
  document.getElementById('paimonDate').textContent = 'Game date: ' + (paimon.game_date || '2010-01-01');
  document.getElementById('paimonReply').textContent = paimon.last_reply || paimon.last_error || 'Call Paimon to start a conversation.';
  const p = STATE.player;
  const ui5 = STATE.ui_v5 || {};
  const isVi = (STATE.lang === 'vi' || ui5.lang === 'vi');
  document.documentElement.lang = isVi ? 'vi' : 'en';
  document.querySelectorAll('[data-en]').forEach(el => {
    el.textContent = isVi ? (el.getAttribute('data-vi') || el.getAttribute('data-en')) : el.getAttribute('data-en');
  });
  const langBtn = document.getElementById('langToggleBtn');
  if (langBtn) langBtn.textContent = isVi ? '🌐 VI (Đổi sang EN)' : '🌐 EN (Switch to VI)';
  const setLangBadge = document.getElementById('setLangBadge');
  if (setLangBadge) setLangBadge.textContent = isVi ? 'TIẾNG VIỆT (VI)' : 'ENGLISH (EN)';
  const btnLangEn = document.getElementById('btnLangEn');
  const btnLangVi = document.getElementById('btnLangVi');
  if (btnLangEn) btnLangEn.className = 'btn ' + (!isVi ? 'btn-blue' : '');
  if (btnLangVi) btnLangVi.className = 'btn ' + (isVi ? 'btn-blue' : '');

  // Sync active app from engine if changed in-game
  if (typeof ui5.phone_app === 'number' && ui5.phone_app !== currentAppId) {
    applyActiveAppDOM(ui5.phone_app);
  }

  // Apply Wallpaper, Mascot & Theme
  const wpTex = ui5.wp_tex || 'ep_wp_furina';
  const msTex = ui5.mascot_tex || 'ep_ms_furina';
  const pfEl = document.getElementById('phoneFrame');
  if (pfEl) pfEl.style.backgroundImage = `url('/assets/${wpTex}.png')`;
  const msEl = document.getElementById('homeMascotImg');
  if (msEl) msEl.src = `/assets/${msTex}.png`;
  const themeColors = ['#38bdf8', '#a855f7', '#f59e0b'];
  document.documentElement.style.setProperty('--accent', themeColors[ui5.theme_idx || 0] || '#38bdf8');

  document.getElementById('clockTxt').textContent = `${p.date_str} • ${p.clock}`;
  document.getElementById('hpBadge').textContent = `♥ HP ${p.health}`;
  document.getElementById('valCash').textContent = '$' + p.cash.toLocaleString();
  document.getElementById('valBank').textContent = '$' + (p.bank + p.savings).toLocaleString();
  document.getElementById('valLoan').textContent = '$' + p.loan.toLocaleString();
  document.getElementById('valNet').textContent = '$' + p.net_worth.toLocaleString();
  document.getElementById('toastBanner').textContent = '🔔 ' + (STATE.last_toast || '');

  // Navigation Header when inside Apps 1..9
  const homeApps = ui5.home_apps || [];
  const curAppMeta = homeApps.find(a => a.id === currentAppId);
  const subPg = (ui5.app_subpage || {})[String(currentAppId)] || 0;
  if (curAppMeta) {
    document.getElementById('navAppTitle').textContent = `App ${currentAppId}: ${curAppMeta.name} (${curAppMeta.sub}) • ${isVi ? 'Trang con' : 'Subpage'} #${subPg + 1}`;
  }

  // App 0: SpringBoard Home Screen
  const msPresets = ui5.mascot_presets || [];
  const curMs = msPresets[ui5.mascot_idx || 0] || {name: 'Furina', greeting: 'Chào Aether! Chúc một ngày dạo phố vui vẻ~'};
  document.getElementById('homeGreetingTxt').textContent = `${curMs.name}: "${curMs.greeting}"`;
  document.getElementById('homeWeatherWalletTxt').textContent = isVi ? `☀️ Los Santos 26°C • Ngày ${p.date_str} • Ròng: $${p.net_worth.toLocaleString()}` : `☀️ Los Santos 26°C • Date ${p.date_str} • Net Worth: $${p.net_worth.toLocaleString()}`;

  const pf = STATE.portfolio || {};
  const bi = STATE.bug_inspector || {};
  const gm = STATE.gg_map || {};
  const rd = STATE.eagleride || {};
  const ds = STATE.dating_sim || {};
  const dsSel = ds.selected || {};
  const appBadges = {
    1: p.loan > 0 ? (isVi ? `Nợ $${p.loan}` : `Debt $${p.loan}`) : '',
    2: isVi ? `${Object.keys(STATE.stocks_market||{}).length} mã` : `${Object.keys(STATE.stocks_market||{}).length} assets`,
    3: `${Object.keys(STATE.crypto_market||{}).length} coins`,
    4: isVi ? `${(pf.active_bets||[]).length} kèo` : `${(pf.active_bets||[]).length} bets`,
    5: isVi ? `${(pf.active_tickets||[]).length} vé` : `${(pf.active_tickets||[]).length} tks`,
    6: `Day ${p.day}`,
    7: isVi ? `${(pf.spot_holdings||[]).length + (pf.open_futures||[]).length} vị thế` : `${(pf.spot_holdings||[]).length + (pf.open_futures||[]).length} pos`,
    8: `${bi.reports_count||0} bugs`,
    9: (STATE.lang || 'en').toUpperCase(),
    10: gm.active_gps ? `📍 ${gm.active_gps.dist_str}` : `${gm.total_pois || 715} POIs`,
    11: 'AI',
    12: rd.active_trip ? `🚕 $${rd.active_trip.fare}` : `${rd.unlocked_count || 18}/${rd.total_pois || 715}`,
    13: dsSel.short_name ? `💖 ${dsSel.short_name} Lv.${dsSel.stage||1}` : '6 Girls',
    14: `${((STATE.contacts_app||{}).unlocked_mondstadt_count||0) + 6}/${(STATE.contacts_app||{}).total_contacts || 20}`
  };

  document.getElementById('homeIconGrid').innerHTML = homeApps.map((app, idx) => {
    const isSel = (idx === (ui5.home_cursor_idx || 0));
    const bdg = appBadges[app.id] || '';
    return `<div class="home-app-tile ${isSel ? 'selected' : ''}" onclick="switchApp(${app.id})">
      ${bdg ? `<span class="home-app-badge">${bdg}</span>` : ''}
      <img src="/assets/${app.tex}.png" alt="${app.name}">
      <div class="app-name">${app.id}. ${app.name}</div>
      <div class="app-sub">${app.sub}</div>
    </div>`;
  }).join('');

  const xau = (STATE.stocks_market || {})['XAU'];
  const btc = (STATE.crypto_market || {})['BTC'];
  document.getElementById('homeQuickSummary').innerHTML = `
    <div>🥇 <b>${isVi ? 'Vàng (XAU):' : 'Gold (XAU):'}</b> $${xau ? xau.price.toFixed(1) : '1096.5'} (${xau && xau.delta_pct>=0?'+':''}${xau ? xau.delta_pct.toFixed(2) : '0.00'}%)</div>
    <div>🪙 <b>Bitcoin (BTC):</b> $${btc ? btc.price.toFixed(2) : '0.08'} (${btc && btc.delta_pct>=0?'+':''}${btc ? btc.delta_pct.toFixed(2) : '0.00'}%)</div>
    <div>❤️ <b>${isVi ? 'No / Energy:' : 'Hunger / Energy:'}</b> ${p.hunger}% / ${p.energy}%</div>
    <div>🎰 <b>Jackpot:</b> $${((STATE.lottery||{}).jackpot||1250000).toLocaleString()}</div>
  `;

  // App 1
  const hpPct = Math.min(100, Math.round((p.health / Math.max(100, p.max_health)) * 100));
  document.getElementById('barHpTxt').textContent = `${p.health} / ${p.max_health} (${isVi ? 'Giáp' : 'Armor'}: ${p.armor})`;
  document.getElementById('barHp').style.width = hpPct + '%';
  document.getElementById('barHungerTxt').textContent = p.hunger + '%';
  document.getElementById('barHunger').style.width = p.hunger + '%';
  document.getElementById('barEnergyTxt').textContent = p.energy + '%';
  document.getElementById('barEnergy').style.width = p.energy + '%';
  document.getElementById('savingsBadge').textContent = `${isVi ? 'Sổ Tiết Kiệm' : 'Savings'}: $${p.savings.toLocaleString()}`;
  document.getElementById('loanStatusBadge').textContent = p.loan_status;

  // App 2: Stocks & Commodities
  const stAssets = Object.values(STATE.stocks_market || {}).filter(a => stockFilter === 'ALL' || a.category === stockFilter);
  document.getElementById('stockPills').innerHTML = stAssets.map(a =>
    `<button class="pill ${a.symbol===selectedStockSym?'active':''}" onclick="selectedStockSym='${a.symbol}';act('select_symbol',{market_group:'stocks',symbol:'${a.symbol}'})">${a.symbol} ${a.delta_pct>=0?'+':''}${a.delta_pct.toFixed(1)}%</button>`
  ).join('');
  const curSt = (STATE.stocks_market || {})[selectedStockSym] || stAssets[0];
  if (curSt) {
    selectedStockSym = curSt.symbol;
    document.getElementById('stSymName').textContent = `${curSt.symbol} — ${curSt.name}`;
    document.getElementById('stStory').textContent = curSt.story;
    document.getElementById('stPrice').textContent = '$' + curSt.price.toFixed(curSt.decimals);
    const sd = document.getElementById('stDelta');
    sd.textContent = `${curSt.delta_pct>=0?'+':''}${curSt.delta_pct.toFixed(2)}%`;
    sd.style.color = curSt.delta_pct >= 0 ? '#34d399' : '#f87171';
    document.getElementById('stHoldingTxt').textContent = `Spot: ${curSt.spot_qty.toFixed(3)} ${curSt.symbol} ($${Math.round(curSt.spot_val).toLocaleString()})`;
    drawAssetChart('stockCanvas', curSt);
  }
  renderFuturesBox('stockFuturesBox', (STATE.futures || []).filter(f => f.market_group === 'stocks'));
  document.getElementById('stockMarketWatchBox').innerHTML = `
    <table class="mini-tbl">
      <thead><tr><th>${isVi?'Mã':'Sym'}</th><th>${isVi?'Tên Tài Sản':'Asset Name'}</th><th>${isVi?'Giá ($)':'Price ($)'}</th><th>% 24h</th><th>${isVi?'Đang Giữ':'Holding'}</th></tr></thead>
      <tbody>${stAssets.map((a, idx) => `
        <tr class="${idx%2===1?'zebra':''}" style="cursor:pointer;${a.symbol===selectedStockSym?'background:rgba(56,189,248,0.16);':''}" onclick="selectedStockSym='${a.symbol}';act('select_symbol',{market_group:'stocks',symbol:'${a.symbol}'})">
          <td><b style="color:#fde68a;">${a.symbol}</b></td>
          <td>${a.name}</td>
          <td><b>$${a.price.toFixed(a.decimals)}</b></td>
          <td style="color:${a.delta_pct>=0?'#34d399':'#f87171'};font-weight:700;">${a.delta_pct>=0?'+':''}${a.delta_pct.toFixed(2)}%</td>
          <td style="color:#93c5fd;">${a.spot_qty>0?`$${Math.round(a.spot_val).toLocaleString()}`:'-'}</td>
        </tr>`).join('')}</tbody>
    </table>`;

  // App 3: Crypto
  const crAssets = Object.values(STATE.crypto_market || {});
  document.getElementById('cryptoPills').innerHTML = crAssets.map(a =>
    `<button class="pill ${a.symbol===selectedCryptoSym?'active':''}" onclick="selectedCryptoSym='${a.symbol}';act('select_symbol',{market_group:'crypto',symbol:'${a.symbol}'})">${a.symbol} ${a.delta_pct>=0?'+':''}${a.delta_pct.toFixed(1)}%</button>`
  ).join('');
  const curCr = (STATE.crypto_market || {})[selectedCryptoSym] || crAssets[0];
  if (curCr) {
    selectedCryptoSym = curCr.symbol;
    document.getElementById('crSymName').textContent = `${curCr.symbol} — ${curCr.name}`;
    document.getElementById('crStory').textContent = curCr.story;
    document.getElementById('crPrice').textContent = '$' + curCr.price.toFixed(curCr.decimals);
    const cd = document.getElementById('crDelta');
    cd.textContent = `${curCr.delta_pct>=0?'+':''}${curCr.delta_pct.toFixed(2)}%`;
    cd.style.color = curCr.delta_pct >= 0 ? '#34d399' : '#f87171';
    document.getElementById('crHoldingTxt').textContent = `Spot: ${curCr.spot_qty.toFixed(4)} ${curCr.symbol} ($${Math.round(curCr.spot_val).toLocaleString()})`;
    drawAssetChart('cryptoCanvas', curCr);
  }
  renderFuturesBox('cryptoFuturesBox', (STATE.futures || []).filter(f => f.market_group === 'crypto'));
  document.getElementById('cryptoMarketWatchBox').innerHTML = `
    <table class="mini-tbl">
      <thead><tr><th>Coin</th><th>${isVi?'Tên Crypto':'Crypto Name'}</th><th>${isVi?'Giá ($)':'Price ($)'}</th><th>% 24h</th><th>${isVi?'Đang Giữ':'Holding'}</th></tr></thead>
      <tbody>${crAssets.map((a, idx) => `
        <tr class="${idx%2===1?'zebra':''}" style="cursor:pointer;${a.symbol===selectedCryptoSym?'background:rgba(56,189,248,0.16);':''}" onclick="selectedCryptoSym='${a.symbol}';act('select_symbol',{market_group:'crypto',symbol:'${a.symbol}'})">
          <td><b style="color:#38bdf8;">${a.symbol}</b></td>
          <td>${a.name}</td>
          <td><b>$${a.price.toFixed(a.decimals)}</b></td>
          <td style="color:${a.delta_pct>=0?'#34d399':'#f87171'};font-weight:700;">${a.delta_pct>=0?'+':''}${a.delta_pct.toFixed(2)}%</td>
          <td style="color:#93c5fd;">${a.spot_qty>0?`$${Math.round(a.spot_val).toLocaleString()}`:'-'}</td>
        </tr>`).join('')}</tbody>
    </table>`;

  // App 4: Chronological Sportsbook (Multi-Match League Pages)
  const fixtures = STATE.fixtures || [];
  if (typeof STATE.selected_league_idx === 'number') {
    selectedLeagueIdx = STATE.selected_league_idx;
  }
  const activeLg = LEAGUE_PAGES[selectedLeagueIdx] || LEAGUE_PAGES[0];
  document.getElementById('leaguePageTabs').innerHTML = LEAGUE_PAGES.map((lg, idx) =>
    `<button class="pill ${idx===selectedLeagueIdx?'active':''}" onclick="selectLeaguePage(${idx})">${isVi ? lg.short_vi : lg.short}</button>`
  ).join('');
  const leagueFixtures = fixtures.filter(m => m.league_id === activeLg.id);
  const roundLbl = leagueFixtures.length > 0 ? leagueFixtures[0].round_label : (fixtures[0]?.round_label || '');
  document.getElementById('sportSeasonHeader').textContent = isVi ? `⚽ ${roundLbl} (${fixtures.length} Trận / 5 Giải)` : `⚽ ${roundLbl} (${fixtures.length} Matches / 5 Leagues)`;
  document.getElementById('currentLeagueTitle').textContent = isVi ? `🏆 Trang ${selectedLeagueIdx + 1}/5: ${activeLg.name} (${leagueFixtures.length} Trận Trong Ngày)` : `🏆 Page ${selectedLeagueIdx + 1}/5: ${activeLg.name} (${leagueFixtures.length} Matches Today)`;

  document.getElementById('fixturesContainer').innerHTML = leagueFixtures.map((m, idx) => `
    <div class="match-card">
      <div style="display:flex;justify-content:space-between;font-size:10.5px;color:#93c5fd;margin-bottom:3px;">
        <span>#${idx + 1} • 🏆 ${m.league_name} (${m.round_label})</span>
        <span>⏰ ${isVi?'Giờ đá':'Kickoff'}: ${m.kickoff} | ${isVi?'Chấp':'Hcap'}: ${m.hcap}</span>
      </div>
      <div style="font-size:13.5px;font-weight:800;display:flex;justify-content:space-between;align-items:center;">
        <span>${m.home} <span style="color:#64748b;">vs</span> ${m.away}</span>
        <button class="pill" style="font-size:10px;" onclick="act('sim_one_match',{match_id:'${m.id}'})">${isVi?'Đá Trận Này ▶':'Sim Match ▶'}</button>
      </div>
      ${m.active_bet ? `<div style="margin-top:3px;font-size:11px;color:#34d399;font-weight:700;">✅ ${isVi?'Đã cược':'Active Bet'}: $${m.active_bet.stake} (${m.active_bet.label} @ ${m.active_bet.odd}x)</div>` : ''}
      <div class="odds-grid">
        <div class="odd-btn" onclick="placeSportBet('${m.id}','HOME','${m.home} Win')"><span class="odd-lbl">${isVi?'1 (Chủ)':'1 (Home)'}</span><span class="odd-val">${m.odds[0].toFixed(2)}</span></div>
        <div class="odd-btn" onclick="placeSportBet('${m.id}','DRAW','Draw')"><span class="odd-lbl">${isVi?'X (Hòa)':'X (Draw)'}</span><span class="odd-val">${m.odds[1].toFixed(2)}</span></div>
        <div class="odd-btn" onclick="placeSportBet('${m.id}','AWAY','${m.away} Win')"><span class="odd-lbl">${isVi?'2 (Khách)':'2 (Away)'}</span><span class="odd-val">${m.odds[2].toFixed(2)}</span></div>
        <div class="odd-btn" onclick="placeSportBet('${m.id}','OVER','Over ${m.ou_line}')"><span class="odd-lbl">${isVi?'Tài':'Over'} ${m.ou_line}</span><span class="odd-val">1.90</span></div>
        <div class="odd-btn" onclick="placeSportBet('${m.id}','UNDER','Under ${m.ou_line}')"><span class="odd-lbl">${isVi?'Xỉu':'Under'} ${m.ou_line}</span><span class="odd-val">1.90</span></div>
      </div>
    </div>
  `).join('');

  const stRows = (STATE.standings && STATE.standings[activeLg.id]) || [];
  document.getElementById('standingsContainer').innerHTML = `
    <div style="font-size:11px;font-weight:800;color:#60a5fa;margin-bottom:4px;">📊 ${isVi?'Bảng Xếp Hạng':'Standings'}: ${activeLg.name}</div>
    <table class="mini-tbl">
      <thead><tr><th>#</th><th>${isVi?'CLB':'Club'}</th><th>${isVi?'Trận':'P'}</th><th>${isVi?'T-H-B':'W-D-L'}</th><th>GD</th><th>${isVi?'Điểm':'Pts'}</th></tr></thead>
      <tbody>${stRows.map((r, idx) => `<tr class="${idx%2===1?'zebra':''}"><td>${idx+1}</td><td><b>${r.team}</b></td><td>${r.p}</td><td>${r.w}-${r.d}-${r.l}</td><td>${r.gd>=0?'+'+r.gd:r.gd}</td><td style="color:#fde68a;font-weight:800;">${r.pts}</td></tr>`).join('')}</tbody>
    </table>`;
  document.getElementById('sportHistoryContainer').innerHTML = (STATE.sport_history || []).map(h =>
    `<div style="border-bottom:1px solid #1e293b;padding:5px 0;font-size:11px;">${h}</div>`
  ).join('');

  // App 5: 4-Subpage Lottery
  const lt = STATE.lottery || {};
  const jp645 = lt.jackpot_mega645 || lt.jackpot || 1250000;
  const jp655_1 = lt.jackpot_power655_jp1 || 3200000;
  const jp655_2 = lt.jackpot_power655_jp2 || 350000;
  document.getElementById('lottoJackpotTxt').textContent = `Mega 6/45: $${jp645.toLocaleString()} | Power 6/55: $${jp655_1.toLocaleString()}`;
  document.getElementById('scratchGrid').innerHTML = (lt.scratch_cells || []).map(c => `<div class="scratch-cell">${c}</div>`).join('');
  document.getElementById('scratchResultTxt').textContent = lt.last_scratch_msg || '';

  const xsktBox = document.getElementById('xsktResultsBox');
  if (xsktBox) {
    const lo18 = (lt.last_xskt_lo18 || []).join(' • ');
    xsktBox.innerHTML = `
      <div style="color:#fde68a;font-weight:800;margin-bottom:3px;">🏆 KQ XSKT Miền Nam (16:30) — ĐB: <span style="color:#34d399;font-size:13px;">${lt.last_6d || '------'}</span> | G.Nhất: <span style="color:#93c5fd;">${lt.last_xskt_g1 || '-----'}</span></div>
      <div style="color:#cbd5e1;font-size:10.5px;"><b>Bảng Lô 2 Số (18 Giải):</b> ${lo18 || 'Chưa mở thưởng'}</div>
    `;
  }

  const vietPoolsBox = document.getElementById('vietlottPoolsBox');
  if (vietPoolsBox) {
    vietPoolsBox.innerHTML = `
      <div style="background:#061a14;border:1px solid #10b981;border-radius:8px;padding:7px;">
        <div style="color:#34d399;font-weight:800;font-size:11.5px;">🟢 MEGA 6/45 (01..45)</div>
        <div style="color:#fde68a;font-weight:800;font-size:12.5px;margin:2px 0;">Jackpot: $${jp645.toLocaleString()}</div>
        <div style="color:#a7f3d0;font-size:10.5px;">KQ 18:00: <b>${lt.last_mega645 || lt.last_645 || '--'}</b></div>
      </div>
      <div style="background:#170926;border:1px solid #a855f7;border-radius:8px;padding:7px;">
        <div style="color:#e879f9;font-weight:800;font-size:11.5px;">🟣 POWER 6/55 (01..55 + ĐB)</div>
        <div style="color:#fde68a;font-weight:800;font-size:11.5px;margin:2px 0;">JP1: $${jp655_1.toLocaleString()} | JP2: $${jp655_2.toLocaleString()}</div>
        <div style="color:#f5d0fe;font-size:10.5px;">KQ 18:00: <b>${lt.last_power655 || '--'} + [${lt.last_power655_bonus || '--'}]</b></div>
      </div>
    `;
  }

  const kenoBox = document.getElementById('kenoResultsBox');
  if (kenoBox) {
    kenoBox.innerHTML = `
      <div style="color:#fde68a;font-weight:800;margin-bottom:2px;">⚡ Bóng Keno (10/20 bóng đầu): <span style="color:#38bdf8;">${lt.last_keno_balls || '--'}</span></div>
      <div style="color:#cbd5e1;font-size:10.5px;margin-bottom:2px;">${lt.last_keno_meta || ''}</div>
      <div style="color:#34d399;font-weight:700;">${lt.last_keno_msg || ''}</div>
    `;
  }

  const allTks = lt.tickets || [];
  const xsktTks = allTks.filter(t => ['XSKT_6D','LODE_DE','LODE_LO2','LODE_3CANG'].includes(t.type));
  const vietTks = allTks.filter(t => ['MEGA_645','POWER_655','MEGA_BAO7','POWER_BAO7'].includes(t.type));
  document.getElementById('lottoTicketsBox').innerHTML = `
    <div style="color:#fde68a;margin-bottom:3px;"><b>🏛️ Vé Chờ Mở Thưởng 16:30 (XSKT/Lô Đề - ${xsktTks.length} vé):</b> ${xsktTks.map(t => `[${t.type}: ${t.numbers}]`).join(', ') || 'Chưa có'}</div>
    <div style="color:#6ee7b7;"><b>💎 Vé Chờ Mở Thưởng 18:00 (Vietlott 6/45 & 6/55 - ${vietTks.length} vé):</b> ${vietTks.map(t => `[${t.type}: ${t.numbers}]`).join(', ') || 'Chưa có'}</div>
  `;

  // App 6: Newspaper
  const nw = STATE.newspaper || {};
  document.getElementById('newsHeaderDate').textContent = isVi ? `📰 Báo Ngày EagleTimes — Ngày ${nw.date_str || p.date_str} (Day ${p.day})` : `📰 EagleTimes Daily — ${nw.date_str || p.date_str} (Day ${p.day})`;
  document.getElementById('newsPolTxt').textContent = nw.politics || '';
  document.getElementById('newsFinTxt').textContent = nw.finance || '';
  document.getElementById('newsCryTxt').textContent = nw.crypto || '';
  document.getElementById('newsSptTxt').textContent = nw.sports || '';

  // App 7: Unified Portfolio + Allocation Gauge Bar
  const pfStats = pf.stats || {};
  const totNw = Math.max(1, pf.total_net_worth || p.net_worth || 1);
  const spotVal = (pf.stocks_spot_val || 0) + (pf.crypto_spot_val || 0);
  const futVal = Math.max(0, pf.fut_equity || 0);
  const cashVal = Math.max(0, (p.cash || 0) + (p.bank || 0) + (p.savings || 0));
  const sumAssets = Math.max(1, spotVal + futVal + cashVal);
  const pctSpot = Math.round((spotVal / sumAssets) * 100);
  const pctFut = Math.round((futVal / sumAssets) * 100);
  const pctCash = Math.max(0, 100 - pctSpot - pctFut);

  document.getElementById('portAllocLegend').innerHTML = `
    <span style="color:#fde68a;">🏛️🪙 Spot: ${pctSpot}% ($${Math.round(spotVal).toLocaleString()})</span>
    <span style="color:#a855f7;">🚀 Futures: ${pctFut}% ($${Math.round(futVal).toLocaleString()})</span>
    <span style="color:#34d399;">💵 ${isVi?'Tiền/Bank':'Cash/Bank'}: ${pctCash}% ($${Math.round(cashVal).toLocaleString()})</span>
  `;
  document.getElementById('portBarSpot').style.width = pctSpot + '%';
  document.getElementById('portBarFut').style.width = pctFut + '%';
  document.getElementById('portBarCash').style.width = pctCash + '%';

  document.getElementById('portNetWorthBadge').textContent = `${isVi ? 'Tài Sản Ròng' : 'Net Worth'}: $${(pf.total_net_worth || p.net_worth || 0).toLocaleString()}`;
  const stSpotPnl = pf.stocks_spot_pnl || 0;
  const crSpotPnl = pf.crypto_spot_pnl || 0;
  const futPnl = pf.fut_pnl || 0;
  const realMktPnl = pfStats.realized_market_pnl || 0;
  const betNetPnl = pfStats.bet_net_pnl || 0;
  const lottoNetPnl = pfStats.lotto_net_pnl || 0;

  document.getElementById('portOverviewGrid').innerHTML = `
    <div class="port-stat">
      <div class="lbl">🏛️ ${isVi?'Cổ Phiếu & Vàng Spot':'Stocks & Gold Spot'}</div>
      <div class="val" style="color:#fde68a;">$${Math.round(pf.stocks_spot_val || 0).toLocaleString()}</div>
      <div class="sub" style="color:${stSpotPnl>=0?'#34d399':'#f87171'};">${isVi?'Lãi/Lỗ Tạm Tính':'Unrealized P&L'}: ${stSpotPnl>=0?'+':''}$${stSpotPnl.toFixed(1)}</div>
    </div>
    <div class="port-stat">
      <div class="lbl">🪙 Crypto Spot</div>
      <div class="val" style="color:#38bdf8;">$${Math.round(pf.crypto_spot_val || 0).toLocaleString()}</div>
      <div class="sub" style="color:${crSpotPnl>=0?'#34d399':'#f87171'};">${isVi?'Lãi/Lỗ Tạm Tính':'Unrealized P&L'}: ${crSpotPnl>=0?'+':''}$${crSpotPnl.toFixed(1)}</div>
    </div>
    <div class="port-stat">
      <div class="lbl">🚀 ${isVi?`Vị Thế Futures (${(pf.open_futures||[]).length} lệnh)`:`Open Futures (${(pf.open_futures||[]).length} pos)`}</div>
      <div class="val" style="color:#a855f7;">Equity: $${Math.round(pf.fut_equity || 0).toLocaleString()}</div>
      <div class="sub" style="color:${futPnl>=0?'#34d399':'#f87171'};">${isVi?'Vốn':'Margin'} $${(pf.fut_margin||0).toLocaleString()} • PnL ${futPnl>=0?'+':''}$${futPnl.toFixed(1)}</div>
    </div>
    <div class="port-stat">
      <div class="lbl">📊 ${isVi?'Tổng P&L Đã Chốt (Realized)':'Total Realized P&L'}</div>
      <div class="val" style="color:${(realMktPnl+betNetPnl+lottoNetPnl)>=0?'#34d399':'#f87171'};">${(realMktPnl+betNetPnl+lottoNetPnl)>=0?'+':''}$${Math.round(realMktPnl+betNetPnl+lottoNetPnl).toLocaleString()}</div>
      <div class="sub" style="color:#cbd5e1;">Mkt: ${realMktPnl>=0?'+':''}$${Math.round(realMktPnl)} | Bet: ${betNetPnl>=0?'+':''}$${betNetPnl} | Lotto: ${lottoNetPnl>=0?'+':''}$${lottoNetPnl}</div>
    </div>
  `;

  const spots = pf.spot_holdings || [];
  document.getElementById('portSpotCountBadge').textContent = `${spots.length} mã ($${Math.round((pf.stocks_spot_val||0)+(pf.crypto_spot_val||0)).toLocaleString()})`;
  if (spots.length === 0) {
    document.getElementById('portSpotContainer').innerHTML = '<div style="color:var(--muted);">Chưa nắm giữ mã Cổ Phiếu, Vàng Đá Quý hay Crypto Spot nào.</div>';
  } else {
    document.getElementById('portSpotContainer').innerHTML = spots.map(h => {
      const col = h.pnl >= 0 ? '#34d399' : '#f87171';
      return `<div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 8px;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <b>[${h.symbol}] ${h.name}</b> <span style="font-size:10px;color:#94a3b8;">(${h.category})</span>
          <div style="font-size:10.5px;color:#cbd5e1;">SL: ${h.qty} • Giá hiện tại: $${h.price} • Giá trị: <b>$${Math.round(h.val).toLocaleString()}</b></div>
        </div>
        <div style="display:flex;gap:6px;align-items:center;">
          <b style="color:${col};">${h.pnl>=0?'+':''}$${h.pnl.toFixed(1)} (${h.pnl_pct>=0?'+':''}${h.pnl_pct.toFixed(1)}%)</b>
          <button class="pill" style="background:#d97706;color:#fff;border:none;" onclick="act('sell_spot_all_one',{market_group:'${h.market_group}',symbol:'${h.symbol}'})">Bán Hết</button>
        </div>
      </div>`;
    }).join('');
  }

  const allFuts = pf.open_futures || [];
  document.getElementById('portFutCountBadge').textContent = `${allFuts.length} lệnh đang mở`;
  renderFuturesBox('portFuturesContainer', allFuts);

  const actBets = pf.active_bets || [];
  const actTks = pf.active_tickets || [];
  document.getElementById('portBetLottoBadge').textContent = `${actBets.length} kèo ($${(pf.bets_stake||0).toLocaleString()}) • ${actTks.length} vé số`;
  let blHtml = '';
  actBets.forEach(b => {
    blHtml += `<div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 8px;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center;">
      <div>
        <b style="color:#c084fc;">⚽ [${b.league_name}] ${b.match}</b> <span style="color:#94a3b8;">(${b.kickoff})</span>
        <div style="font-size:10.5px;color:#34d399;">Kèo: <b>${b.pick_label} @ ${b.odd.toFixed(2)}x</b> • Vốn cược: $${b.stake.toLocaleString()} → Thắng nhận: <b>+$${b.potential_payout.toLocaleString()}</b></div>
      </div>
      <button class="pill" style="background:#2563eb;color:#fff;border:none;" onclick="act('sim_one_match',{match_id:'${b.match_id}'})">Đá Ngay ▶</button>
    </div>`;
  });
  actTks.forEach(t => {
    blHtml += `<div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 8px;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center;">
      <div><b style="color:#fde68a;">🎰 Vé Số ${t.type}: [${t.numbers}]</b> <span style="color:#94a3b8;">(Chờ quay thưởng • Vé $10)</span></div>
      <button class="pill" style="background:#059669;color:#fff;border:none;" onclick="act('draw_lottery_now',{})">Quay Ngay 🎰</button>
    </div>`;
  });
  if (!blHtml) {
    blHtml = '<div style="color:var(--muted);">Chưa có kèo Bet thể thao hay Vé Số nào đang chờ mở thưởng.</div>';
  }
  document.getElementById('portBetLottoContainer').innerHTML = blHtml;

  // App 8: Map Bug Reporter, Auto-Inspector (.IPL/.IDE/.IMG/.COL) & Safe Recall Unstuck
  const idxSt = bi.index_stats || {};
  const telem = bi.live_telemetry || {};
  const safeR = telem.safe_recall || {x: 0, y: 0, z: 0, label: 'N/A'};
  document.getElementById('bugIndexBadge').textContent = bi.index_ready
    ? `✅ ${idxSt.ide_models||0} IDE • ${idxSt.ipl_insts||0} IPL • ${idxSt.col_entries||0} COL`
    : '⏳ Đang nạp Index...';
  document.getElementById('bugSavedCountBadge').textContent = `Đã lưu: ${bi.reports_count || 0} bug`;

  document.getElementById('bugTelemetryGrid').innerHTML = `
    <div class="port-stat">
      <div class="lbl">📍 Tọa Độ Hiện Tại (RAM Live)</div>
      <div class="val" style="color:#fde68a;">(${(telem.x||0).toFixed(2)}, ${(telem.y||0).toFixed(2)}, ${(telem.z||0).toFixed(2)})</div>
      <div class="sub" style="color:#cbd5e1;">Hướng: ${(telem.heading||0).toFixed(1)}° • Vz: ${(telem.vz||0).toFixed(3)} • ${telem.in_vehicle?'🚗 Đang lái xe':'🚶 Đi bộ'}</div>
    </div>
    <div class="port-stat">
      <div class="lbl">🛟 Điểm Cứu Hộ An Toàn (-3s)</div>
      <div class="val" style="color:#34d399;">(${(safeR.x||0).toFixed(2)}, ${(safeR.y||0).toFixed(2)}, ${(safeR.z||0).toFixed(2)})</div>
      <div class="sub" style="color:#93c5fd;">Int: ${telem.area_code||0}/${telem.game_area||0} • ${telem.zone_label||'San Andreas'}</div>
    </div>
  `;

  const trail = telem.trail_5s || [];
  document.getElementById('bugTrailBox').innerHTML = `
    <div style="font-weight:800;color:#6ee7b7;margin-bottom:2px;">⏱️ Vệt Di Chuyển 5 Giây Trước Khi Báo Lỗi (Position Trail):</div>
    <div>${trail.map(s => `<span style="margin-right:8px;"><b>${s.offset_sec}s:</b> (${s.x}, ${s.y}, ${s.z}) [Vz:${s.vz}]</span>`).join(' → ')}</div>
  `;

  const cats = bi.categories || [];
  document.getElementById('bugCategoryPills').innerHTML = cats.map((c, idx) =>
    `<button class="pill ${idx===bi.selected_category_idx?'active':''}" onclick="act('set_bug_category',{idx:${idx}})">${c.label}</button>`
  ).join('');

  const scan = bi.live_scan || {};
  const suspects = scan.suspects || [];
  const topSus = suspects[0] || null;
  document.getElementById('bugPrimarySuspectBadge').textContent = topSus
    ? `🎯 ${topSus.dff_name}.dff (ID ${topSus.model_id}, cách ${topSus.surface_dist}m)`
    : 'Chưa có dữ liệu quét';

  if (topSus) {
    document.getElementById('bugDiagnosisBox').innerHTML = `
      <div style="background:#0a101f;border:1px solid #ef4444;border-radius:9px;padding:8px 10px;">
        <div style="color:#fca5a5;font-weight:800;margin-bottom:3px;">
          🎯 Nghi Phạm Số 1: <code>${topSus.dff_name}.dff</code> (Model ID <b>${topSus.model_id}</b>) • TXD: <code>${topSus.txd_name}.txd</code> • Cách mặt/tâm: <b>${topSus.surface_dist}m / ${topSus.center_dist}m</b>
        </div>
        <div style="color:#cbd5e1;margin-bottom:3px;">
          📂 <b>IPL:</b> <code>${topSus.ipl_source}</code> | <b>IDE:</b> <code>${topSus.ide_source}</code> | <b>IMG:</b> <code>${topSus.dff_img}</code>
        </div>
        <div style="color:#fde68a;margin-bottom:4px;">
          🧱 <b>Collision (.COL):</b> <code>${topSus.col_source}</code> (${topSus.col_version}, R=${topSus.col_radius}m, <b>${topSus.col_boxes} boxes / ${topSus.col_faces} faces</b>) • Cờ: <b>${(topSus.issue_flags||[]).join(', ')}</b>
        </div>
        <div style="color:#6ee7b7;font-size:11px;">
          💡 <b>Gợi ý sửa tự động:</b> ${(scan.diagnosis_lines||[])[0] || ''}
        </div>
      </div>
    `;
    document.getElementById('bugSuspectsTableBox').innerHTML = `
      <table class="mini-tbl">
        <thead><tr><th>#</th><th>ID</th><th>Model (.dff)</th><th>Cách</th><th>File .IPL</th><th>.COL (Faces/Boxes)</th><th>Cờ Chẩn Đoán</th></tr></thead>
        <tbody>
          ${suspects.slice(0, 8).map((s, idx) => `
            <tr class="${idx%2===1?'zebra':''}">
              <td>${idx+1}</td>
              <td><b>${s.model_id}</b></td>
              <td style="color:#93c5fd;"><b>${s.dff_name}.dff</b></td>
              <td>${s.surface_dist}m</td>
              <td>${s.ipl_source.split('/').pop()}</td>
              <td style="color:${s.col_faces===0?'#f87171':'#34d399'};">${s.col_source.split('/').pop()} (${s.col_faces}F/${s.col_boxes}B)</td>
              <td style="color:#fde68a;">${(s.issue_flags||[]).join(', ')}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } else {
    document.getElementById('bugDiagnosisBox').innerHTML = '<div style="color:var(--muted);">Hãy bấm <b>🔍 Quét Trực Tiếp Bán Kính 15m</b> hoặc <b>🐛 Ghi Nhận Bug (F11)</b> để tra cứu .ipl/.ide/.img/.col quanh Aether.</div>';
    document.getElementById('bugSuspectsTableBox').innerHTML = '';
  }

  const reps = bi.reports || [];
  if (reps.length === 0) {
    document.getElementById('bugReportsHistoryBox').innerHTML = '<div style="color:var(--muted);">Chưa có báo cáo bug nào. Bấm <b>F11</b> trong game hoặc nút đỏ bên trên để lưu báo cáo chuẩn hóa!</div>';
  } else {
    document.getElementById('bugReportsHistoryBox').innerHTML = reps.map((r, idx) => {
      const ps = r.primary_suspect;
      return `<div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:7px 9px;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
        <div>
          <b style="color:#f87171;">#${r.id} [${r.category_label}]</b> <span style="color:#94a3b8;">(${r.timestamp}) • ${r.zone_label}</span>
          <div style="font-size:10.5px;color:#fde68a;">📍 Tọa độ: (${r.coords.x}, ${r.coords.y}, ${r.coords.z}) | An toàn -3s: (${r.pre_fall_safe_pos?.x||0}, ${r.pre_fall_safe_pos?.y||0}, ${r.pre_fall_safe_pos?.z||0})</div>
          <div style="font-size:10.5px;color:#93c5fd;">🎯 Suspect: <b>${ps ? `${ps.dff_name}.dff (ID ${ps.model_id}) — ${ps.ipl_source} — COL: ${ps.col_source} (${ps.col_faces} faces)` : 'N/A'}</b></div>
        </div>
        <button class="pill" style="background:#2563eb;color:#fff;border:none;flex-shrink:0;" onclick="copyDiscordBug(${idx})">📋 Copy Discord</button>
      </div>`;
    }).join('');
  }

  // On-Demand Debugger, Doctor & Auto-Probe Tester (Page 3/3 of App 8)
  const dbg = STATE.debug_system || {};
  const dbgMode = dbg.mode || 'lite';
  const dbgBdg = document.getElementById('dbgModeBadge');
  if (dbgBdg) {
    dbgBdg.textContent = dbg.mode_badge || (dbgMode === 'deep' ? 'DEEP DEBUG [LIVE RAM]' : 'LITE [0% OVERHEAD]');
    dbgBdg.style.color = dbgMode === 'deep' ? '#fde047' : '#34d399';
  }
  const dbgLines = dbg.hud_lines || [];
  const dbgOv = document.getElementById('dbgOverviewBox');
  if (dbgOv) {
    dbgOv.innerHTML = dbgLines.map((ln, idx) =>
      `<div style="color:${idx===0?(dbgMode==='deep'?'#fde047':'#6ee7b7'):'#e2e8f0'};font-weight:${idx===0?'800':'500'};">${ln}</div>`
    ).join('');
  }
  const dbgDet = document.getElementById('dbgDetailsBox');
  if (dbgDet) {
    const docChecks = (dbg.doctor_report || {}).checks || [];
    const ca = (dbg.crash_audit || {}).latest;
    const lgSt = dbg.logger_stats || {};
    let detHtml = `<div style="color:#93c5fd;margin-bottom:4px;">🧪 <b>Auto-Probe Suite:</b> ${dbg.selected_suite_label || 'Core Cities'} | <b>Unified Log:</b> PyErr=${lgSt.error_count||0}, LuaErr=${lgSt.lua_error_count||0}</div>`;
    if (ca) {
      detHtml += `<div style="color:#fca5a5;margin-bottom:4px;">💥 <b>Latest Crash Log:</b> <code>${ca.file}</code> (${ca.mtime}) → <b>${ca.category}</b> at <code>${ca.exception_addr}</code> in <code>${ca.exception_module}</code></div>`;
    }
    const igt = dbg.ingame_tester || {};
    if (igt.last_snapshot && igt.last_snapshot.crosshair_target) {
      const ch = igt.last_snapshot.crosshair_target;
      detHtml += `<div style="color:#fde68a;margin-bottom:4px;">📸 <b>Camera Look-At X-Ray:</b> <code>${ch.dff_name}.dff</code> (ID <b>${ch.model_id}</b>, TXD <code>${ch.txd_name}</code>) @ ${ch.dist_m}m • RAM DFF:${ch.ram_dff_loaded?'OK':'NO'} TXD:${ch.ram_txd_loaded?'OK':'NO'} COL:${ch.ram_col_triangles||0}F</div>`;
    }
    if (igt.last_scene_audit) {
      detHtml += `<div style="color:#6ee7b7;margin-bottom:4px;">🔎 <b>${igt.last_scene_audit.summary}</b></div>`;
    }
    if (igt.last_aether_test) {
      detHtml += `<div style="color:#c084fc;margin-bottom:4px;">⚔️ <b>${igt.last_aether_test.summary}</b></div>`;
    }
    if (igt.last_crawler) {
      detHtml += `<div style="color:#38bdf8;margin-bottom:4px;">🤖 <b>${igt.last_crawler.summary}</b></div>`;
    }
    if (igt.last_npc_report) {
      detHtml += `<div style="color:#fcd34d;margin-bottom:4px;">👥 <b>${igt.last_npc_report.summary}</b></div>`;
    }
    if (docChecks.length > 0) {
      detHtml += `<div style="max-height:130px;overflow-y:auto;border-top:1px solid #1e293b;padding-top:4px;">` +
        docChecks.map(c => `<div style="font-size:10.5px;"><b style="color:${c.status==='PASS'?'#34d399':(c.status==='WARN'?'#fbbf24':'#f87171')};">[${c.status}]</b> <code>${c.id}</code>: ${c.detail}</div>`).join('') +
        `</div>`;
    }
    dbgDet.innerHTML = detHtml;
  }

  // App 9: Settings & Anime Theme Customizer
  const wpPresets = ui5.wallpapers || [];
  const themePresets = ui5.theme_presets || [];
  document.getElementById('setWpBadge').textContent = ui5.wp_name || 'Furina Hydro';
  document.getElementById('setMascotBadge').textContent = ui5.mascot_name || 'Furina';
  document.getElementById('setThemeBadge').textContent = ui5.theme_name || 'Hydro Cyan';

  document.getElementById('setWpGrid').innerHTML = wpPresets.map((w, idx) => {
    const active = (idx === (ui5.wp_idx || 0));
    return `<div onclick="act('set_ui_settings',{wp_idx:${idx}})" style="cursor:pointer;border:2px solid ${active?'var(--accent)':'#263554'};border-radius:12px;overflow:hidden;background:#0a101f;text-align:center;padding-bottom:6px;">
      <img src="/assets/${w.tex}.png" style="width:100%;height:110px;object-fit:cover;display:block;margin-bottom:5px;">
      <div style="font-size:11px;font-weight:800;color:${active?'#fde68a':'#f1f5f9'};">${w.name}</div>
      <div style="font-size:9.5px;color:#94a3b8;">${w.sub}</div>
    </div>`;
  }).join('');

  document.getElementById('setMascotGrid').innerHTML = msPresets.map((m, idx) => {
    const active = (idx === (ui5.mascot_idx || 0));
    return `<div onclick="act('set_ui_settings',{mascot_idx:${idx}})" style="cursor:pointer;border:2px solid ${active?'var(--accent)':'#263554'};border-radius:12px;padding:6px;background:#0a101f;text-align:center;">
      <img src="/assets/${m.tex}.png" style="width:64px;height:64px;object-fit:contain;margin:0 auto 4px auto;display:block;">
      <div style="font-size:10.5px;font-weight:800;color:${active?'#fde68a':'#f1f5f9'};">${m.name}</div>
    </div>`;
  }).join('');

  document.getElementById('setThemeGrid').innerHTML = themePresets.map((t, idx) => {
    const active = (idx === (ui5.theme_idx || 0));
    return `<button class="btn ${active?'btn-blue':''}" onclick="act('set_ui_settings',{theme_idx:${idx}})">${active?'● ':''}${t.name}</button>`;
  }).join('');

  // App 10: GG Map (GTA Genshin Map) & Auto GPS Waypoint
  const gmCats = gm.categories || [];
  const gmSelCatIdx = gm.selected_cat_idx || 0;
  const gmPois = gm.pois || [];
  const gmCoords = gm.player_coords || {x: 0, y: 0, z: 0};
  const gmActGps = gm.active_gps || null;

  document.getElementById('ggmapTotalBadge').textContent = isVi ? `${gm.filtered_count || gmPois.length}/${gm.total_pois || 631} Địa Điểm & Sự Kiện` : `${gm.filtered_count || gmPois.length}/${gm.total_pois || 631} POIs & Events`;
  document.getElementById('ggmapPlayerPosBadge').textContent = `Aether: (${gmCoords.x}, ${gmCoords.y}, ${gmCoords.z})`;
  document.getElementById('ggmapListHeaderTitle').textContent = `📍 ${gm.selected_cat_title || '1/10: Tất Cả (Gần Nhất)'}`;

  if (gmActGps) {
    document.getElementById('ggmapActiveGpsBox').innerHTML = `
      <div style="background:linear-gradient(90deg, rgba(6,78,59,0.92), rgba(15,23,42,0.95));border:1.5px solid #10b981;border-radius:10px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
        <div>
          <div style="font-size:11.5px;font-weight:800;color:#6ee7b7;">🎯 ${isVi?'ĐANG DẪN ĐƯỜNG GPS (MỐC ĐỎ T)':'ACTIVE GPS ROUTING (RED T WAYPOINT)'}: <span style="color:#fde68a;">${gmActGps.name}</span> (${gmActGps.region})</div>
          <div style="font-size:10.5px;color:#e2e8f0;margin-top:2px;">📏 ${isVi?'Khoảng cách':'Distance'}: <b>${gmActGps.dist_str}</b> (${gmActGps.bearing}) • Coords: (${gmActGps.x}, ${gmActGps.y}, ${gmActGps.z}) • ${isVi?'Tự xóa khi tới nơi':'Auto-clears on arrival'} (&le;25m)</div>
        </div>
        <button class="btn btn-red" style="flex:0 0 auto;padding:5px 10px;" onclick="act('clear_gps_waypoint', {})">❌ ${isVi?'Hủy Chỉ Đường (F10)':'Clear GPS (F10)'}</button>
      </div>
    `;
  } else {
    document.getElementById('ggmapActiveGpsBox').innerHTML = `
      <div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 10px;font-size:11px;color:#93c5fd;">
        ${isVi ? '💡 Chọn một địa danh / sự kiện bên dưới và bấm <b>📍 Chỉ Đường GPS (Mốc T)</b> (hoặc <b>F9 / Enter</b> trong game) để tự động vẽ đường dẫn GPS màu đỏ trên radar!' : '💡 Select any destination or event below and click <b>📍 Set GPS Waypoint (Red T)</b> (or press <b>F9 / Enter</b> in-game) to draw the red GPS route on the radar without opening the Pause Map!'}
      </div>
    `;
  }

  document.getElementById('ggmapCatPills').innerHTML = gmCats.map((c, idx) =>
    `<button class="pill ${idx===gmSelCatIdx?'active':''}" onclick="act('set_ggmap_category',{cat_idx:${idx}})">${idx+1}. ${c.short}</button>`
  ).join('');

  const searchKw = ((document.getElementById('ggmapSearchInput')?.value) || '').trim().toLowerCase();
  const visiblePois = searchKw
    ? gmPois.filter(item =>
        (item.name || '').toLowerCase().includes(searchKw) ||
        (item.region || '').toLowerCase().includes(searchKw) ||
        (item.note || '').toLowerCase().includes(searchKw) ||
        (item.cat || '').toLowerCase().includes(searchKw)
      )
    : gmPois;

  document.getElementById('ggmapPoiListBox').innerHTML = visiblePois.map((item, idx) => {
    const isGps = !!item.is_gps_target;
    const isSel = (idx === (gm.selected_poi_idx || 0)) && !searchKw;
    const borderCol = isGps ? '#ef4444' : (isSel ? '#f59e0b' : '#233252');
    const bgCol = isGps ? 'rgba(6, 62, 46, 0.85)' : (isSel ? 'rgba(30, 58, 138, 0.55)' : '#0b1324');
    return `<div style="background:${bgCol};border:1.5px solid ${borderCol};border-radius:10px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
      <div style="flex:1;">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <b style="font-size:12.5px;color:${isGps?'#6ee7b7':'#fde68a'};">${isGps?'🎯 [GPS] ':''}${item.name}</b>
          <span style="background:#1e293b;color:#c084fc;font-size:10px;font-weight:800;padding:1px 6px;border-radius:999px;">${item.region}</span>
          <span style="background:${isGps?'#dc2626':'#0284c7'};color:#fff;font-size:10px;font-weight:800;padding:1px 7px;border-radius:999px;">📏 ${item.dist_str} • ${item.bearing}</span>
        </div>
        <div style="font-size:11px;color:#e2e8f0;margin-top:3px;">${item.note || ''}</div>
        <div style="font-size:10px;color:#94a3b8;margin-top:2px;">${isVi?'Tọa độ':'Coords'}: X:${item.x} • Y:${item.y} • Z:${item.z}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:4px;flex-shrink:0;">
        <button class="btn btn-green" style="padding:5px 9px;font-size:11px;" onclick="act('set_gps_waypoint',{poi_id:'${item.id}'})">📍 ${isVi?'Chỉ Đường GPS (Mốc T)':'Set GPS Waypoint (Red T)'}</button>
        <button class="btn btn-gold" style="padding:4px 9px;font-size:10.5px;" onclick="switchApp(12);act('ride_book',{poi_id:'${item.id}'})">🚕 ${isVi?'Đặt Xe EagleRide':'Book EagleRide'}</button>
      </div>
    </div>`;
  }).join('') || '<div style="color:var(--muted);padding:10px;">Không tìm thấy địa điểm nào khớp từ khóa.</div>';

  // App 12: EagleRide (Uber / Xanh SM / Grab / Be + Passenger Radio + Fast-Forward)
  const rdSvcs = rd.services || [];
  const rdCats = rd.categories || [];
  const rdPois = rd.pois || [];
  const rdAct = rd.active_trip || null;
  document.getElementById('rideUnlockedBadge').textContent = isVi
    ? `🔓 ${rd.unlocked_count || 18}/${rd.total_pois || 715} Đã Mở Khóa`
    : `🔓 ${rd.unlocked_count || 18}/${rd.total_pois || 715} Unlocked`;
  document.getElementById('rideRadioBadge').textContent = rd.radio_name || 'Flash FM';
  document.getElementById('rideListHeaderTitle').textContent = `📍 ${rd.cat_label || 'Tất Cả'} (${rd.count_str || ''})`;
  document.getElementById('rideStatsBadge').textContent = isVi
    ? `${rd.total_trips || 0} chuyến • Đã chi $${(rd.total_spent || 0).toLocaleString()}`
    : `${rd.total_trips || 0} trips • Spent $${(rd.total_spent || 0).toLocaleString()}`;

  if (rdAct) {
    document.getElementById('rideActiveTripBox').innerHTML = `
      <div style="background:linear-gradient(90deg, rgba(6,78,59,0.94), rgba(15,23,42,0.96));border:1.5px solid #10b981;border-radius:10px;padding:9px 11px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
          <div>
            <div style="font-size:12px;font-weight:800;color:#6ee7b7;">🚕 ${isVi?'CHUYẾN XE ĐANG CHẠY':'ACTIVE EAGLERIDE TRIP'} [${rd.ride_state}]: <span style="color:#fde68a;">${rdAct.service_short} → ${rdAct.poi_name}</span></div>
            <div style="font-size:11px;color:#e2e8f0;margin-top:2px;">💵 ${isVi?'Giá cước':'Fare'}: <b>$${rdAct.fare.toLocaleString()}</b> • 📏 ${isVi?'Còn lại':'Remaining'}: <b>${Math.round(rdAct.remaining_dist_m || 0)}m</b> (Node ${rdAct.wp_idx}/${rdAct.total_wps}) • 📻 Radio: <b>${rdAct.radio_station}</b></div>
          </div>
          <div style="display:flex;gap:5px;flex-wrap:wrap;">
            <button class="btn btn-gold" style="flex:0 0 auto;padding:5px 10px;" onclick="act('ride_fast_forward', {})">⏩ ${isVi?'Tua Nhanh Tới Nơi (F10)':'Fast-Forward Arrival (F10)'}</button>
            <button class="btn btn-red" style="flex:0 0 auto;padding:5px 10px;" onclick="act('ride_cancel', {})">❌ ${isVi?'Hủy Chuyến':'Cancel Ride'}</button>
          </div>
        </div>
      </div>
    `;
  } else {
    document.getElementById('rideActiveTripBox').innerHTML = `
      <div style="background:#0a101f;border:1px solid #263554;border-radius:9px;padding:6px 10px;font-size:11px;color:#93c5fd;">
        ${isVi
          ? '💡 Chọn hãng xe (<b>Uber / Xanh SM / Grab / Be</b>) rồi bấm <b>🚕 Đặt Xe</b> tới bất kỳ địa điểm nào bạn đã từng tự lái xe tới (&le;85m). Trong lúc ngồi xe có thể đổi Radio (phím <b>O</b>) hoặc bấm <b>F10</b> để tua nhanh tới nơi!'
          : '💡 Select a ride brand (<b>Uber / Xanh SM / Grab / Be</b>) and click <b>🚕 Book Ride</b> to any POI you have visited in person (&le;85m). Change Radio freely (key <b>O</b>) or press <b>F10</b> to fast-forward arrival!'}
      </div>
    `;
  }

  document.getElementById('rideServiceGrid').innerHTML = rdSvcs.map(s => {
    const active = (s.idx === (rd.service_idx || 0));
    const icon = (s.kind === 'BIKE') ? '🛵' : '🚘';
    return `<div onclick="act('ride_select_service',{service_idx:${s.idx}})" style="cursor:pointer;background:${active?'rgba(6, 182, 212, 0.22)':'#0b1324'};border:1.5px solid ${active?'#06b6d4':'#233252'};border-radius:10px;padding:6px 5px;text-align:center;">
      <div style="font-size:14px;">${icon}</div>
      <div style="font-size:10.5px;font-weight:800;color:${active?'#fde68a':'#f1f5f9'};">${s.idx+1}. ${s.short}</div>
      <div style="font-size:9.5px;color:#6ee7b7;">$${s.base_fare} + $${s.per_km}/km</div>
    </div>`;
  }).join('');

  document.getElementById('rideCatPills').innerHTML =
    `<button class="pill ${rd.filter_visited_only?'active':''}" onclick="act('ride_toggle_filter',{})">🔓 ${isVi?'Chỉ Hiện Đã Mở':'Unlocked Only'}</button>` +
    rdCats.map(c =>
      `<button class="pill ${c.idx===(rd.cat_idx||0)?'active':''}" onclick="act('ride_select_cat',{cat_idx:${c.idx}})">${c.idx+1}. ${c.short}</button>`
    ).join('');

  const rideInpEl = document.getElementById('rideSearchInput');
  if (rideInpEl && document.activeElement !== rideInpEl && typeof rd.search_query === 'string' && rideInpEl.value !== rd.search_query) {
    rideInpEl.value = rd.search_query;
  }
  const rideKw = ((rideInpEl?.value) || '').trim().toLowerCase();
  const visibleRidePois = rideKw
    ? rdPois.filter(item =>
        (item.name || '').toLowerCase().includes(rideKw) ||
        (item.region || '').toLowerCase().includes(rideKw) ||
        (item.desc || item.note || '').toLowerCase().includes(rideKw)
      )
    : rdPois.slice(0, 80);

  document.getElementById('ridePoiListBox').innerHTML = visibleRidePois.map(item => {
    const isOpen = !!item.unlocked;
    const isSel = rd.selected_poi && rd.selected_poi.id === item.id;
    const borderCol = isSel ? '#f59e0b' : (isOpen ? '#059669' : '#334155');
    const bgCol = isSel ? 'rgba(30, 58, 138, 0.55)' : (isOpen ? '#0b1628' : 'rgba(15, 23, 42, 0.65)');
    return `<div style="background:${bgCol};border:1.5px solid ${borderCol};border-radius:10px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
      <div style="flex:1;">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <b style="font-size:12.5px;color:${isOpen?'#fde68a':'#94a3b8'};">${isOpen?'🔓':'🔒'} ${item.name}</b>
          <span style="background:#1e293b;color:#c084fc;font-size:10px;font-weight:800;padding:1px 6px;border-radius:999px;">${item.region}</span>
          <span style="background:#0284c7;color:#fff;font-size:10px;font-weight:800;padding:1px 7px;border-radius:999px;">📏 ${item.dist_str}</span>
          <span style="background:${isOpen?'#059669':'#b45309'};color:#fff;font-size:10px;font-weight:800;padding:1px 7px;border-radius:999px;">💵 $${(item.fare||0).toLocaleString()}</span>
        </div>
        <div style="font-size:11px;color:#e2e8f0;margin-top:3px;">${item.desc || item.note || ''}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:4px;flex-shrink:0;">
        ${isOpen
          ? `<button class="btn btn-green" style="padding:5px 9px;font-size:11px;" onclick="act('ride_book',{poi_id:'${item.id}'})">🚕 ${isVi?'Đặt Xe Ngay':'Book Ride'}</button>`
          : `<button class="btn btn-gold" style="padding:5px 9px;font-size:10.5px;" onclick="act('ride_book',{poi_id:'${item.id}'})">📍 ${isVi?'Chưa Tới (Cắm GPS)':'Locked (Pin GPS)'}</button>`
        }
      </div>
    </div>`;
  }).join('') || '<div style="color:var(--muted);padding:10px;">Không tìm thấy địa điểm nào khớp bộ lọc.</div>';

  // App 13: WaifuLink (6 Girlfriends Dating Sim, Memory & Photos)
  renderWaifuLink(ds);
  // App 14: Contacts & Remote Messenger
  renderContactsApp(STATE.contacts_app);
}

function escapeJsStr(s) {
  return String(s || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, ' ');
}

let wlLastVnJson = '';

function renderWaifuLink(ds) {
  if (!ds || !ds.roster) return;
  const roster = ds.roster || [];
  const sel = ds.selected || roster[0] || {};
  const msgs = ds.messages || [];
  const mems = ds.memories || [];
  const gifts = ds.gifts || [];
  const gallery = ds.gallery || [];

  const aiBadgeEl = document.getElementById('wlAiModelBadge');
  if (aiBadgeEl) {
    aiBadgeEl.textContent = '🤖 AI: ' + (ds.ai_status || ds.ai_model || 'gpt-6-luna (OpenAI Live)');
  }

  const safetyEl = document.getElementById('wlSafetyBadge');
  if (safetyEl) {
    safetyEl.textContent = ds.hot_coffee_guard_enabled
      ? (ds.vanilla_blips_hibernated ? '🛡️ Hot Coffee: LOCKED • Pure Sim' : '🛡️ Hot Coffee: LOCKED')
      : '⚠️ Censor Unlocked';
  }

  // 1. Roster Strip (6 Girlfriends — Hu Tao marked as Full v4.0 Pilot)
  const stripEl = document.getElementById('wlRosterStrip');
  if (stripEl) {
    stripEl.innerHTML = roster.map(g => {
      const isAct = (g.id === sel.id);
      return `<div onclick="act('dating_select_char',{char_id:'${g.id}'})" style="position:relative;cursor:pointer;background:${isAct?'rgba(244,114,182,0.22)':'#091020'};border:1.5px solid ${isAct?g.accent_color:'#233252'};border-radius:10px;padding:5px 3px;text-align:center;transition:transform 0.15s;">
        ${g.is_pilot_complete ? `<span style="position:absolute;top:2px;right:2px;background:#dc2626;color:#fff;font-size:7.5px;font-weight:900;padding:1px 4px;border-radius:999px;">v4★</span>` : ''}
        <img src="${g.avatar_url}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid ${g.accent_color};margin:0 auto 3px auto;display:block;">
        <div style="font-size:10px;font-weight:800;color:${isAct?'#fde68a':'#f1f5f9'};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${g.short_name}</div>
        <div style="font-size:8.5px;color:${g.stage_color};font-weight:700;">Lv.${g.stage} • ${g.affection}♥</div>
      </div>`;
    }).join('');
  }

  // 2. Selected Girlfriend Header Card + 5-Heart HUD + 3-Pillar Progression + House Doorstep Trigger
  const hdrEl = document.getElementById('wlSelectedHeader');
  if (hdrEl && sel.id) {
    const heartsHtml = [1, 2, 3, 4, 5].map(sNum =>
      `<span style="font-size:12px;color:${sNum <= sel.stage ? '#f43f5e' : '#475569'};margin-right:2px;">${sNum <= sel.stage ? '♥' : '♡'}</span>`
    ).join('');
    const msDotsHtml = Array.from({length: 15}, (_, idx) => {
      const mReq = Math.round((idx + 1) * 62);
      const reached = sel.affection >= mReq;
      return `<span title="Milestone M${String(idx+1).padStart(2,'0')} (${mReq} ♥)" style="display:inline-block;width:9px;height:6px;border-radius:2px;background:${reached ? '#f472b6' : '#1e293b'};border:1px solid ${reached ? '#fde68a' : '#334155'};"></span>`;
    }).join('');
    const gateHtml = sel.stage_gate_locked
      ? `<div style="margin-top:4px;background:rgba(185,28,28,0.35);border:1px solid #f87171;border-radius:7px;padding:3px 7px;font-size:9.5px;color:#fecaca;font-weight:800;">
           🔒 Stage-Gate Locked at ${sel.affection} ♥! Pass ${sel.stage_scenarios_req - sel.stage_scenarios_passed} more Stage-${sel.stage} VN Scenario(s) to advance to Stage ${sel.stage + 1}! (Carryover scenarios from earlier stages stay playable for +35 ♥ &amp; 4 CGs!)
         </div>`
      : '';
    const houseCoords = sel.home_coords || [0, 0, 0];
    hdrEl.innerHTML = `
      <div style="display:flex;gap:10px;align-items:center;">
        <img src="${sel.avatar_url}" onclick="openWaifuLightbox('${sel.avatar_url}','${escapeJsStr(sel.name)}','${escapeJsStr(sel.short_name)}','${escapeJsStr(sel.bio)}')" style="cursor:pointer;width:66px;height:66px;border-radius:14px;object-fit:cover;border:2px solid ${sel.accent_color};flex-shrink:0;" title="Click to enlarge CG">
        <div style="flex:1;min-width:0;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:4px;flex-wrap:wrap;">
            <b style="font-size:13.5px;color:#fff;">${sel.monogram || ''} ${sel.name} ${sel.is_pilot_complete ? '<span style="background:#dc2626;color:#fde68a;font-size:9px;padding:1px 6px;border-radius:999px;margin-left:4px;">★ v4.0 Pilot (15 CGs • 20×4 Couple CGs)</span>' : ''}</b>
            <span style="background:#1e293b;color:#f9a8d4;font-size:9.5px;font-weight:800;padding:2px 7px;border-radius:999px;">Mood: ${sel.mood}</span>
          </div>
          <div style="font-size:10.5px;color:#cbd5e1;margin-top:1px;">${sel.title} • <span style="color:#fde68a;">🏠 Home: ${sel.home_label || ''} (${houseCoords[0]}, ${houseCoords[1]})</span></div>
          <!-- 5-Heart Relationship Stage & 15-Milestone Progress HUD -->
          <div style="margin-top:5px;">
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:10px;font-weight:800;margin-bottom:2px;">
              <span>${heartsHtml} <span style="color:${sel.stage_color};">Stage ${sel.stage}/5: ${sel.stage_title} (${sel.stage_subtitle})</span></span>
              <span style="color:#fde68a;">${sel.affection} / ${sel.next_stage_pts} ♥</span>
            </div>
            <div style="height:8px;background:#090d16;border-radius:999px;overflow:hidden;border:1px solid #334155;">
              <div style="width:${sel.stage_progress_pct}%;height:100%;background:linear-gradient(90deg, ${sel.accent_color}, #f472b6, #fde68a);"></div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:3px;gap:4px;">
              <span style="font-size:9px;color:#fbcfe8;font-weight:700;">📸 15 Milestone Goal Track:</span>
              <div style="display:flex;gap:2px;flex-wrap:wrap;">${msDotsHtml}</div>
            </div>
            <!-- 3-Pillar Economy Caps & Scenario Gate Counters -->
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px;margin-top:5px;">
              <div style="background:#091020;border:1px solid #1e293b;border-radius:6px;padding:3px 6px;font-size:9.5px;text-align:center;">
                <span style="color:#93c5fd;font-weight:800;">💬 Chat Cap:</span> <b style="color:#fff;">${sel.stage_chat_pts || 0}/${sel.stage_chat_cap || 45}</b>
              </div>
              <div style="background:#091020;border:1px solid #1e293b;border-radius:6px;padding:3px 6px;font-size:9.5px;text-align:center;">
                <span style="color:#6ee7b7;font-weight:800;">🚗 Free-Roam:</span> <b style="color:#fff;">${sel.stage_freeroam_pts || 0}/${sel.stage_freeroam_cap || 75}</b>
              </div>
              <div style="background:#091020;border:1px solid ${sel.stage_scenarios_passed >= sel.stage_scenarios_req ? '#10b981' : '#f59e0b'};border-radius:6px;padding:3px 6px;font-size:9.5px;text-align:center;">
                <span style="color:#fde68a;font-weight:800;">🎭 Stage ${sel.stage} Gate:</span> <b style="color:#fff;">${sel.stage_scenarios_passed || 0}/${sel.stage_scenarios_req || 3} VN</b>
              </div>
            </div>
            <!-- House Visit Event Selector Quick Triggers -->
            <div style="display:flex;gap:5px;margin-top:6px;flex-wrap:wrap;">
              <button class="btn btn-gold" style="flex:1;padding:4px 8px;font-size:10px;" onclick="act('dating_open_house_menu',{char_id:'${sel.id}'})">
                🏠 Visit ${sel.short_name}'s House (Open Event Menu)
              </button>
              <button class="btn btn-blue" style="flex:0 0 auto;padding:4px 8px;font-size:10px;" onclick="act('dating_teleport_house',{char_id:'${sel.id}'})" title="Teleport Aether to her house doorstep in GTA SA and open Event Menu">
                📍 Teleport to Her Doorstep
              </button>
            </div>
            ${gateHtml}
            ${sel.active_stage_persona ? `<div style="font-size:9.5px;color:#e9d5ff;margin-top:3px;font-style:italic;">🎭 ${sel.active_stage_persona}</div>` : ''}
          </div>
        </div>
      </div>
    `;
  }

  // 3. Chat Messages (Roleplay Protagonist = Traveler Aether + Dual-Channel Inner Thought / Action Cue + Clickable Milestone CGs)
  const chatBox = document.getElementById('wlChatMessagesBox');
  if (chatBox) {
    const shouldScroll = (msgs.length !== wlLastMsgCount) || (sel.id !== wlLastCharId);
    wlLastMsgCount = msgs.length;
    wlLastCharId = sel.id;
    chatBox.innerHTML = msgs.map(m => {
      const isMe = (m.sender === 'player');
      const align = isMe ? 'flex-end' : 'flex-start';
      const bg = isMe ? 'linear-gradient(135deg, #0284c7, #1d4ed8)' : 'rgba(30, 41, 59, 0.95)';
      const border = isMe ? '#38bdf8' : sel.accent_color;
      const thoughtHtml = (!isMe && m.inner_thought) ? `
        <div style="background:rgba(88, 28, 135, 0.36);border-left:2.5px solid #c084fc;border-radius:6px;padding:4px 7px;margin-bottom:4px;font-size:10px;color:#e9d5ff;">
          <b>${sel.inner_channel_label || '💭 Inner Thought'}:</b> <i>${m.inner_thought}</i>
        </div>
      ` : '';
      const actionHtml = (!isMe && m.action_cue) ? `
        <div style="font-size:10.5px;color:#fde68a;font-style:italic;margin-bottom:3px;">${m.action_cue}</div>
      ` : '';
      const photoHtml = m.photo_url ? `
        <div style="margin-top:6px;border-radius:10px;overflow:hidden;border:1.5px solid rgba(255,255,255,0.22);cursor:pointer;background:#050811;"
             onclick="openWaifuLightbox('${m.photo_url}','${escapeJsStr(m.photo_title || sel.name)}','${escapeJsStr(sel.short_name)}','${escapeJsStr(m.photo_caption || m.text)}')">
          <img src="${m.photo_url}" alt="${m.photo_title}" style="width:100%;max-height:220px;object-fit:cover;display:block;">
          <div style="padding:5px 8px;font-size:10px;color:#fbcfe8;display:flex;justify-content:space-between;align-items:center;">
            <span>📸 <b>${m.photo_title || 'Milestone CG'}</b></span>
            <span style="color:#fde68a;">🔍 Tap to Enlarge</span>
          </div>
        </div>
      ` : '';
      const deltaBadge = (!isMe && m.affection_delta !== 0)
        ? `<span style="color:${m.affection_delta > 0 ? '#f472b6' : '#f87171'};font-weight:800;margin-left:5px;">${m.affection_delta > 0 ? '+' : ''}${m.affection_delta} ♥</span>`
        : '';
      return `<div style="display:flex;flex-direction:column;align-items:${align};">
        <div style="max-width:88%;background:${bg};border:1px solid ${border};border-radius:12px;padding:7px 10px;font-size:11.5px;color:#f8fafc;line-height:1.42;">
          <div style="font-size:9.5px;color:${isMe?'#bae6fd':'#f9a8d4'};font-weight:800;margin-bottom:3px;">
            ${isMe ? 'You (Traveler Aether)' : sel.short_name} ${m.mood ? `• [${m.mood}]` : ''} <span style="color:#94a3b8;font-weight:400;">${m.created_at || ''}</span>${deltaBadge}
          </div>
          ${thoughtHtml}
          ${actionHtml}
          <div>${m.text}</div>
          ${photoHtml}
        </div>
      </div>`;
    }).join('');
    if (shouldScroll) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  // 4A. Live AI Recommended Dialogue Options (suggested_replies)
  const sugBox = document.getElementById('wlSuggestedRepliesBox');
  if (sugBox) {
    const sugs = sel.suggested_replies || [];
    sugBox.innerHTML = sugs.map(s => `
      <button class="btn" style="text-align:left;justify-content:space-between;background:linear-gradient(90deg,rgba(88,28,135,0.45),rgba(30,41,59,0.9));border:1px solid #c084fc;padding:5px 9px;font-size:11px;color:#f8fafc;"
              onclick="act('dating_send_message',{char_id:'${sel.id}',choice_id:'${s.id}',text:'${escapeJsStr(s.player_text)}'})">
        <span>⚡ <b>${s.label}:</b> "${s.player_text}"</span>
        <span style="color:#fde68a;font-weight:800;margin-left:6px;flex-shrink:0;">+6 ♥</span>
      </button>
    `).join('');
  }

  // 4B. Pre-Generated Stage Chat Topics / Starters
  const choicesBox = document.getElementById('wlChoicesBox');
  if (choicesBox) {
    const choices = sel.stage_chat_starters || sel.hangout_choices || [];
    choicesBox.innerHTML = choices.map(c => `
      <button class="btn" style="text-align:left;justify-content:space-between;background:#111c33;border:1px solid #334155;padding:5px 9px;font-size:10.5px;color:#e2e8f0;"
              onclick="act('dating_send_message',{char_id:'${sel.id}',choice_id:'${c.id}',text:'${escapeJsStr(c.player_text || c.label)}'})">
        <span>💬 ${c.label}</span>
        <span style="color:#f472b6;font-weight:800;margin-left:6px;flex-shrink:0;">+6 ♥</span>
      </button>
    `).join('');
  }

  // 5. Visual Novel Scenarios List (20 Authored Scenarios for Hu Tao + 4 Couple CGs Each + Carryover Rule)
  const scListBox = document.getElementById('wlScenariosListBox');
  if (scListBox) {
    const scs = sel.scenarios || [];
    scListBox.innerHTML = scs.map(sc => {
      const isDone = !!sc.completed;
      const isOpen = !!sc.unlocked;
      const isCarry = !!sc.is_carryover;
      const borderCol = isDone ? '#10b981' : (isCarry ? '#f59e0b' : (isOpen ? sel.accent_color : '#334155'));
      const cgSeq = sc.cg_sequence || [];
      const filmstripHtml = cgSeq.map(cgItem => `
        <div onclick="openWaifuLightbox('${cgItem.url}','${escapeJsStr(sc.title + ' — ' + cgItem.label)}','${escapeJsStr(sel.short_name + ' & Traveler Aether')}','${escapeJsStr(sc.summary_l2)}')"
             style="cursor:pointer;position:relative;border-radius:6px;overflow:hidden;border:1px solid ${borderCol};">
          <img src="${cgItem.url}" style="width:100%;height:42px;object-fit:cover;display:block;">
          <div style="background:rgba(9,13,24,0.88);font-size:8px;color:#fde68a;text-align:center;padding:1px 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            Scene ${cgItem.scene_num}/4
          </div>
        </div>
      `).join('');
      const badgeBg = isDone ? '#065f46' : (isCarry ? '#78350f' : (isOpen ? '#831843' : '#1e293b'));
      const badgeCol = isDone ? '#6ee7b7' : (isCarry ? '#fde68a' : (isOpen ? '#fbcfe8' : '#94a3b8'));
      const cameoCast = (sc.cameo_cast || []).join(', ');
      const cameoPill = sc.is_extra_cameo
        ? `<span style="background:#3b0764;border:1px solid #c084fc;color:#f3e8ff;font-size:8.5px;font-weight:900;padding:1px 7px;border-radius:999px;">🌟 EXTRA GENSHIN CAMEO: ${cameoCast}</span>`
        : `<span style="background:#0f172a;border:1px solid #475569;color:#cbd5e1;font-size:8.5px;font-weight:800;padding:1px 6px;border-radius:999px;">💖 CORE ROMANCE</span>`;
      return `<div style="background:#0b1324;border:1.5px solid ${borderCol};border-radius:11px;padding:8px 10px;">
        <div style="display:flex;gap:9px;align-items:center;">
          <img src="${sc.cg_url}" onclick="openWaifuLightbox('${sc.cg_url}','${escapeJsStr(sc.title)}','${escapeJsStr(sel.short_name + ' & Aether')}','${escapeJsStr(sc.summary_l2)}')" style="cursor:pointer;width:72px;height:54px;border-radius:8px;object-fit:cover;border:1px solid ${borderCol};flex-shrink:0;">
          <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;gap:5px;flex-wrap:wrap;">
              <span style="background:#1e293b;color:#fde68a;font-size:9px;font-weight:800;padding:1px 6px;border-radius:999px;">Stage ${sc.stage} • #${sc.order}</span>
              ${cameoPill}
              <b style="font-size:12px;color:#fff;">${sc.title}</b>
              <span style="background:${badgeBg};color:${badgeCol};font-size:8.5px;font-weight:800;padding:1px 6px;border-radius:999px;">${sc.stage_status_badge || ''}</span>
            </div>
            <div style="font-size:10px;color:#f9a8d4;margin-top:2px;">📍 ${sc.location} — ${sc.subtitle}</div>
            ${sc.cameo_dynamic_tier ? `<div style="font-size:9.5px;color:#e9d5ff;margin-top:1px;">🤝 ${sc.cameo_dynamic_tier}</div>` : ''}
            <div style="font-size:9.5px;color:#94a3b8;margin-top:2px;">Reward: +${sc.reward_affection} ♥ • 4 Unique 16:9 CGs • Pre-Gen + Custom Input (Anti-Stuck Active)</div>
          </div>
          <button class="btn ${isDone ? 'btn-blue' : (isCarry ? 'btn-gold' : 'btn-purple')}" style="flex:0 0 auto;padding:6px 10px;font-size:10.5px;"
                  onclick="act('dating_start_vn',{char_id:'${sel.id}',scenario_id:'${sc.id}'})">
            ${isDone ? '🔄 Replay VN' : (isCarry ? '🔄 Carryover VN' : '▶ Start VN')}
          </button>
        </div>
        ${cgSeq.length > 0 ? `<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:5px;margin-top:6px;">${filmstripHtml}</div>` : ''}
      </div>`;
    }).join('');
  }

  // 5A. Girlfriend House Doorstep Event Selector Modal
  const hmModal = document.getElementById('wlHouseVisitModal');
  const hmContent = document.getElementById('wlHouseVisitContent');
  if (hmModal && hmContent) {
    const hm = ds.active_house_menu;
    if (!hm) {
      hmModal.style.display = 'none';
    } else {
      hmModal.style.display = 'flex';
      const optsHtml = (hm.options || []).map((o, idx) => `
        <button class="btn" style="text-align:left;justify-content:space-between;background:linear-gradient(90deg,#1e1b4b,#31102f);border:1.5px solid #fbbf24;padding:8px 11px;color:#fff;"
                onclick="act('dating_select_house_opt',{option_idx:${idx}})">
          <div>
            <div style="font-size:11.5px;font-weight:900;color:#fde68a;">[${idx + 1}] ${o.label}</div>
            <div style="font-size:9.5px;color:#cbd5e1;margin-top:2px;">${o.sub || ''}</div>
          </div>
          <span style="color:#6ee7b7;font-size:10.5px;font-weight:800;margin-left:8px;flex-shrink:0;">Start ▶</span>
        </button>
      `).join('');
      hmContent.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <div>
            <div style="font-size:14.5px;font-weight:900;color:#fde68a;">🏠 At ${hm.char_name}'s Home (${hm.home_label})</div>
            <div style="font-size:10.5px;color:#f9a8d4;">Stage ${hm.stage}: ${hm.stage_title} • ${hm.affection}/1000 ♥ • Stage Gate: ${hm.stage_scenarios_passed}/3 VN</div>
          </div>
          <button class="btn btn-red" style="padding:4px 10px;font-size:10px;" onclick="act('dating_close_house_menu',{})">✕ Leave Doorstep</button>
        </div>
        <div style="font-size:10.5px;color:#cbd5e1;margin-bottom:9px;">
          Choose which event to start with <b>${hm.short_name}</b> right from her doorstep (also controllable in-game via <b>[1-5]</b> or <b>[I/K + F9]</b>):
        </div>
        <div style="display:flex;flex-direction:column;gap:7px;">${optsHtml}</div>
      `;
    }
  }

  // 5B. Fullscreen 4-Scene Visual Novel Overlay Modal (Renders over screen & auto-closes after Scene 4/4)
  const vnModal = document.getElementById('wlVnOverlayModal');
  const vnContent = document.getElementById('wlVnOverlayContent');
  if (vnModal && vnContent) {
    const vn = ds.active_vn_session;
    if (!vn) {
      vnModal.style.display = 'none';
      wlLastVnJson = '';
    } else {
      vnModal.style.display = 'flex';
      const curVnJson = JSON.stringify(vn);
      if (curVnJson !== wlLastVnJson) {
        wlLastVnJson = curVnJson;
        const cgSeq = vn.cg_sequence || [];
        const scNum = vn.scene_num || 1;
        const activeCgObj = cgSeq[Math.max(0, Math.min(cgSeq.length - 1, scNum - 1))] || {url: vn.ending_cg_url || '/dating-media/hutao_sc01_cg1.jpg', label: 'Scene ' + scNum + '/4'};
        const activeCgUrl = vn.finished ? (vn.ending_cg_url || activeCgObj.url) : activeCgObj.url;
        const activeSceneLbl = vn.finished ? (vn.ending_scene_label || 'Scene 4/4 • Couple Ending') : (activeCgObj.label || ('Scene ' + scNum + '/4'));

        const strip4Html = cgSeq.map(cItem => {
          const isCur = (cItem.scene_num === scNum);
          const isPast = (cItem.scene_num < scNum) || vn.finished;
          return `<div style="background:${isCur ? '#be185d' : (isPast ? '#065f46' : '#0f172a')};border:1px solid ${isCur ? '#fde68a' : '#334155'};border-radius:6px;padding:3px 5px;text-align:center;">
            <div style="font-size:8.5px;font-weight:900;color:#fff;">SCENE ${cItem.scene_num}/4 ${isCur ? '◀' : (isPast ? '✓' : '')}</div>
          </div>`;
        }).join('');

        const lr = vn.last_reaction;
        const isReask = lr && lr.off_topic_action === 'REASK_CURRENT_NODE';
        const isAntiStuck = lr && lr.off_topic_action === 'ANTI_STUCK_BRIDGE';
        const reactBorder = isReask ? '#f59e0b' : (isAntiStuck ? '#c084fc' : (lr && lr.grade==='BEST'?'#10b981':(lr && lr.grade==='GOOD'?'#38bdf8':'#f87171')));
        const reactTag = isReask
          ? '🔄 AI OFF-TOPIC RE-ASK (Current Scene Stays Active — Please Answer Properly!)'
          : (isAntiStuck ? '🛡️ ANTI-STUCK GRACEFUL BRIDGE (+10 pts — Auto-Advanced So Scenario Never Locks!)' : `[${lr ? lr.grade : ''} +${lr ? lr.score : 0} pts]`);
        const lastReactHtml = lr ? `
          <div style="background:rgba(15,23,42,0.94);border:1.5px solid ${reactBorder};border-radius:10px;padding:8px 10px;margin-bottom:9px;">
            <div style="font-size:9.5px;color:#93c5fd;font-weight:800;margin-bottom:2px;">
              Traveler Aether: "${lr.player_text}" • <span style="color:#fde68a;">${reactTag}</span>
            </div>
            ${lr.reaction_thought ? `<div style="font-size:10px;color:#e9d5ff;font-style:italic;margin-bottom:2px;">🦋 ${lr.reaction_thought}</div>` : ''}
            ${lr.reaction_action ? `<div style="font-size:10px;color:#fde68a;font-style:italic;margin-bottom:2px;">${lr.reaction_action}</div>` : ''}
            <div style="font-size:11.5px;color:#fff;"><b>${vn.short_name}:</b> "${lr.reaction_reply}"</div>
          </div>
        ` : '';
        const cameoBannerHtml = (vn.is_extra_cameo && (vn.cameo_cast || []).length > 0) ? `
          <div style="background:rgba(59,7,100,0.48);border:1px solid #c084fc;border-radius:8px;padding:5px 8px;font-size:10px;color:#f3e8ff;margin-bottom:7px;">
            🌟 <b>Extra Genshin Cameo Cast:</b> ${(vn.cameo_cast || []).join(', ')} — <i>${vn.cameo_dynamic_tier || ''}</i>
          </div>
        ` : '';

        if (vn.finished) {
          vnContent.innerHTML = `
            <div style="position:relative;width:100%;aspect-ratio:16/9;max-height:90vh;background:#04040a;overflow:hidden;">
              <img src="${activeCgUrl}" style="width:100%;height:100%;object-fit:cover;display:block;">
              <div style="position:absolute;top:10px;left:14px;right:14px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
                <div style="background:rgba(8,10,22,0.56);backdrop-filter:blur(6px);border:1px solid rgba(244,114,182,0.65);padding:4px 12px;border-radius:999px;font-size:11px;font-weight:800;color:#fde68a;">
                  🎭 ${activeSceneLbl} • ${vn.is_carryover ? `Carryover Stage ${vn.stage}` : `Stage ${vn.stage}`}
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,auto);gap:5px;opacity:0.9;">${strip4Html}</div>
              </div>
              <div style="position:absolute;left:16px;right:16px;bottom:12px;background:rgba(8,10,22,0.58);backdrop-filter:blur(7px);border-top:2px solid rgba(244,114,182,0.8);border-radius:12px;padding:12px 16px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                  <span style="background:rgba(136,19,55,0.82);color:#fef08a;font-weight:900;font-size:12px;padding:3px 12px;border-radius:8px;">${vn.title} — ${vn.passed ? '✅ SCENARIO PASSED!' : '⚠️ RETRY AVAILABLE'}</span>
                  <span style="font-size:11px;color:#f9a8d4;font-weight:700;">📍 ${vn.location} • Score: ${vn.total_score}/45 • +${vn.effective_affection_gain || 0} ♥</span>
                </div>
                ${lastReactHtml}
                <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:6px;">
                  <div style="font-size:11px;color:#a7f3d0;font-weight:800;">⏱️ Auto-closing overlay after Scene 4/4 to return to gameplay!</div>
                  <div style="display:flex;gap:8px;">
                    <button class="btn btn-purple" onclick="act('dating_start_vn',{char_id:'${vn.char_id}',scenario_id:'${vn.scenario_id}'})">🔄 Replay</button>
                    <button class="btn btn-green" onclick="act('dating_close_vn',{})">✅ Finish &amp; Return</button>
                  </div>
                </div>
              </div>
            </div>
          `;
        } else if (vn.current_node) {
          const nd = vn.current_node;
          const choicesHtml = (nd.choices || []).map((c, idx) => `
            <button class="btn" style="text-align:left;justify-content:space-between;background:rgba(15,23,42,0.52);border:1px solid rgba(244,114,182,0.55);padding:6px 12px;font-size:11.5px;color:#fff;"
                    onclick="act('dating_choose_vn',{choice_id:'${c.id}'})">
              <span><b>[${idx + 1}] ${c.label}:</b> "${c.player_text}"</span>
              <span style="color:#fde68a;font-size:10px;margin-left:6px;flex-shrink:0;">Select ▶</span>
            </button>
          `).join('');
          vnContent.innerHTML = `
            <div style="position:relative;width:100%;aspect-ratio:16/9;max-height:90vh;background:#04040a;overflow:hidden;">
              <img src="${activeCgUrl}" style="width:100%;height:100%;object-fit:cover;display:block;">
              <div style="position:absolute;top:10px;left:14px;right:14px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
                <div style="background:rgba(8,10,22,0.56);backdrop-filter:blur(6px);border:1px solid rgba(244,114,182,0.65);padding:4px 12px;border-radius:999px;font-size:11px;font-weight:800;color:#fde68a;">
                  🎭 ${activeSceneLbl} • ${vn.is_carryover ? `🔄 Carryover Stage ${vn.stage}` : `🎯 Stage ${vn.stage}`}
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                  <div style="display:grid;grid-template-columns:repeat(4,auto);gap:4px;opacity:0.9;">${strip4Html}</div>
                  <button onclick="act('dating_close_vn',{})" style="background:rgba(127,29,29,0.78);color:#fff;border:1px solid #f87171;border-radius:999px;padding:3px 10px;font-size:10px;font-weight:800;cursor:pointer;">✕ Exit</button>
                </div>
              </div>
              <div style="position:absolute;left:16px;right:16px;bottom:12px;background:rgba(8,10,22,0.58);backdrop-filter:blur(7px);border-top:2px solid rgba(244,114,182,0.82);border-radius:12px;padding:10px 16px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                  <span style="background:rgba(136,19,55,0.85);color:#fef08a;font-weight:900;font-size:12.5px;padding:2px 12px;border-radius:7px;">${vn.char_name} ${nd.action_cue ? `<span style="color:#fbcfe8;font-weight:600;font-style:italic;font-size:11px;margin-left:6px;">${nd.action_cue}</span>` : ''}</span>
                  <span style="font-size:10.5px;color:#fde68a;background:rgba(15,23,42,0.65);padding:2px 10px;border-radius:999px;">${vn.title} ${vn.is_extra_cameo && (vn.cameo_cast||[]).length ? '• 🌟 ' + vn.cameo_cast.join(', ') : ''}</span>
                </div>
                ${lastReactHtml}
                <div style="font-size:11px;color:#f9a8d4;font-style:italic;margin-bottom:3px;">* ${nd.inner_thought} *</div>
                <div style="font-size:13.5px;color:#ffffff;font-weight:600;line-height:1.42;text-shadow:0 1px 3px rgba(0,0,0,0.95);margin-bottom:8px;">"${nd.speaker_line || nd.dialogue || ''}"</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-bottom:6px;">${choicesHtml}</div>
                <div style="display:flex;gap:6px;">
                  <input type="text" id="wlVnFreeTextInput" onkeydown="if(event.key==='Enter')sendVnFreeText()" placeholder="Or type your own custom response to ${vn.short_name} (AI evaluates live)..." style="flex:1;background:rgba(15,23,42,0.62);border:1px solid rgba(196,181,253,0.45);color:#fff;">
                  <button class="btn btn-blue" style="flex:0 0 auto;padding:5px 12px;" onclick="sendVnFreeText()">Speak ➤</button>
                </div>
              </div>
            </div>
          `;
        }
      }
    }
  }

  // 6. Free-Roam Chauffeur Outings & Gift Shop
  const frBanner = document.getElementById('wlActiveFreeroamBanner');
  if (frBanner) {
    const fr = ds.active_freeroam_session;
    frBanner.innerHTML = `
      <div style="background:rgba(6,95,70,0.32);border:1px solid #10b981;border-radius:10px;padding:8px 10px;">
        <div style="font-size:11px;font-weight:800;color:#6ee7b7;margin-bottom:4px;">
          🚗 ${fr ? `Active Outing: Driving ${fr.char_name} to ${fr.spot_name}` : `Complete / Simulate Free-Roam Chauffeur Outing with ${sel.short_name}`}
        </div>
        <div style="font-size:10px;color:#cbd5e1;margin-bottom:6px;">
          Criteria: Arrive at the pinned GPS destination without vehicle crashes or Wanted Stars (Cap: ${sel.stage_freeroam_pts || 0}/${sel.stage_freeroam_cap || 75} ♥ in Stage ${sel.stage}).
        </div>
        <div style="display:flex;gap:5px;flex-wrap:wrap;">
          <button class="btn btn-green" style="padding:4px 9px;font-size:10px;" onclick="act('dating_complete_freeroam',{char_id:'${sel.id}',grade:'S'})">🏆 S-Rank Smooth Chauffeur (+25 ♥)</button>
          <button class="btn btn-blue" style="padding:4px 9px;font-size:10px;" onclick="act('dating_complete_freeroam',{char_id:'${sel.id}',grade:'A'})">✅ A-Rank Safe Arrival (+20 ♥)</button>
          <button class="btn btn-red" style="padding:4px 9px;font-size:10px;" onclick="act('dating_complete_freeroam',{char_id:'${sel.id}',grade:'FAIL'})">💥 Crash / Wanted (0 ♥)</button>
        </div>
      </div>
    `;
  }

  const spotsBox = document.getElementById('wlDateSpotsBox');
  if (spotsBox) {
    spotsBox.innerHTML = (sel.date_spots || []).map(sp => `
      <div style="background:#0b1324;border:1px solid #263554;border-radius:10px;padding:7px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
        <div>
          <div style="font-size:12px;font-weight:800;color:#fde68a;">📍 ${sp.name}</div>
          <div style="font-size:10.5px;color:#cbd5e1;margin-top:2px;">${sp.desc}</div>
          <div style="font-size:9.5px;color:#94a3b8;margin-top:1px;">Coords: (${sp.coords[0]}, ${sp.coords[1]}, ${sp.coords[2]})</div>
        </div>
        <button class="btn btn-green" style="flex:0 0 auto;padding:5px 10px;font-size:11px;" onclick="act('dating_schedule_date',{char_id:'${sel.id}',spot_id:'${sp.id}'})">
          🚗 Start Outing &amp; Pin GPS
        </button>
      </div>
    `).join('');
  }

  const giftsBox = document.getElementById('wlGiftsBox');
  if (giftsBox) {
    giftsBox.innerHTML = gifts.map(gfItem => {
      const isFav = (gfItem.favored_by || []).includes(sel.id);
      const gain = Math.round(gfItem.base_affection * (isFav ? 1.4 : 1.0));
      return `<div style="background:${isFav?'rgba(80,27,62,0.45)':'#0b1324'};border:1px solid ${isFav?'#f472b6':'#263554'};border-radius:10px;padding:7px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
        <div>
          <div style="font-size:12px;font-weight:800;color:#f8fafc;">
            ${gfItem.icon} ${gfItem.name}
            ${isFav ? `<span style="background:#be185d;color:#fff;font-size:9.5px;padding:1px 6px;border-radius:999px;margin-left:4px;">★ ${sel.short_name}'s Favorite!</span>` : ''}
          </div>
          <div style="font-size:10.5px;color:#cbd5e1;margin-top:2px;">${gfItem.desc}</div>
          <div style="font-size:10px;color:#6ee7b7;margin-top:2px;font-weight:700;">Cost: $${gfItem.price} • Affection: +${gain} ♥</div>
        </div>
        <button class="btn btn-gold" style="flex:0 0 auto;padding:5px 10px;font-size:11px;" onclick="act('dating_send_gift',{char_id:'${sel.id}',gift_id:'${gfItem.id}'});setWaifuSubtab('chat');">
          🎁 Send (-$${gfItem.price})
        </button>
      </div>`;
    }).join('');
  }

  // 7. 3-Tier Hierarchical Memory Inspector (L1 Working / L2 Episodic / L3 On-Demand Archive) + 5-Layer Dossier
  const tmBox = document.getElementById('wlTieredMemoryBox');
  if (tmBox && ds.tiered_memory_preview) {
    const tm = ds.tiered_memory_preview;
    tmBox.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:5px;font-size:10px;">
        <div style="background:#0b1324;border-left:3px solid #38bdf8;border-radius:6px;padding:6px 8px;">
          <b style="color:#38bdf8;">Tier 1 (L1 Always-On Working Digest — Compact Context):</b>
          <div style="color:#e2e8f0;margin-top:2px;white-space:pre-line;">${tm.l1_working_digest || ''}</div>
        </div>
        <div style="background:#0b1324;border-left:3px solid #f59e0b;border-radius:6px;padding:6px 8px;">
          <b style="color:#fde68a;">Tier 2 (L2 Episodic Scenario &amp; Outing Summaries):</b>
          <div style="color:#cbd5e1;margin-top:2px;white-space:pre-line;">${tm.l2_episodic_summary || 'Play VN Scenarios or Free-Roam Outings to build episodic memories.'}</div>
        </div>
        <div style="background:#0b1324;border-left:3px solid #c084fc;border-radius:6px;padding:6px 8px;">
          <b style="color:#e9d5ff;">Tier 3 (L3 Deep Archive Keyword Recall — Triggered On-Demand: ${(tm.l3_hits_count || 0)} hits):</b>
          <div style="color:#cbd5e1;margin-top:2px;white-space:pre-line;">${tm.l3_triggered_archive || 'Standby (only injected when your message mentions past quests, companions, or saved facts).'}</div>
        </div>
      </div>
    `;
  }

  const dosBox = document.getElementById('wlDossierBox');
  if (dosBox) {
    const stMatrix = sel.stage_persona_matrix || {};
    const stageRows = [1, 2, 3, 4, 5].map(stNum => {
      const isCurr = (stNum === sel.stage);
      const txt = stMatrix[String(stNum)] || '';
      return txt ? `<div style="padding:4px 7px;margin-bottom:3px;border-radius:6px;background:${isCurr?'rgba(244,114,182,0.18)':'#0b1324'};border:1px solid ${isCurr?sel.accent_color:'#263554'};font-size:10.5px;">
        <b style="color:${isCurr?'#fde68a':'#94a3b8'};">${isCurr?'▶ ACTIVE ':''}</b><span style="color:#f1f5f9;">${txt}</span>
      </div>` : '';
    }).join('');
    const dnaRows = (sel.speech_dna || []).map(d => `<div style="font-size:10.5px;color:#cbd5e1;margin-bottom:2px;">• ${d}</div>`).join('');
    dosBox.innerHTML = `
      <div style="margin-bottom:6px;"><b>Biography:</b> ${sel.bio || ''}</div>
      <div style="margin-bottom:4px;">🔮 <b>Inner Channel:</b> <span style="color:#e9d5ff;font-weight:800;">${sel.inner_channel_label || '💭 Inner Thought'}</span></div>
      <div style="margin-bottom:4px;">🕒 <b>Schedule:</b> <span style="color:#fde68a;">${sel.schedule_label || ''}</span></div>
      <div style="margin-bottom:4px;">🎁 <b>Special Perk:</b> <span style="color:#6ee7b7;">${sel.perk_label || ''}</span></div>
      <div style="margin-bottom:4px;">💗 <b>Likes:</b> ${(sel.likes || []).join(' • ')}</div>
      <div style="margin-bottom:8px;">⚡ <b>Dislikes:</b> ${(sel.dislikes || []).join(' • ')}</div>
      <div style="font-weight:800;color:#f9a8d4;margin-bottom:4px;">🎭 Layer 1: Stage-Gated Persona Matrix (Stage 1 → 5):</div>
      <div style="margin-bottom:8px;">${stageRows}</div>
      <div style="font-weight:800;color:#fde68a;margin-bottom:4px;">🗣️ Layer 2: Speech DNA &amp; Roleplay Guardrails:</div>
      <div>${dnaRows}</div>
    `;
  }

  const memCntEl = document.getElementById('wlMemCountBadge');
  if (memCntEl) memCntEl.textContent = `${mems.length} notes saved`;
  const memListBox = document.getElementById('wlMemoriesListBox');
  if (memListBox) {
    memListBox.innerHTML = mems.map(m => `
      <div style="background:#0b1324;border:1px solid #334155;border-radius:8px;padding:5px 8px;display:flex;justify-content:space-between;align-items:center;gap:6px;font-size:11px;">
        <div>
          <span style="background:#3b0764;color:#e9d5ff;font-size:9.5px;font-weight:800;padding:1px 6px;border-radius:999px;margin-right:5px;">${m.kind}</span>
          <span style="color:#f1f5f9;">${m.text}</span>
        </div>
        <button class="pill" style="background:#7f1d1d;color:#fecaca;border:none;padding:2px 6px;font-size:9.5px;" onclick="act('dating_delete_memory',{char_id:'${sel.id}',mem_id:${m.id}})">✕</button>
      </div>
    `).join('') || '<div style="color:#94a3b8;font-size:11px;">No memories recorded yet. Chat with her to build memories!</div>';
  }

  // 8. Subtab 5: 15 Milestone CGs (M01..M15 for Hu Tao) + Canonical Visual Appearance + Completed Past Quests
  const galCntEl = document.getElementById('wlGalleryCountBadge');
  if (galCntEl) galCntEl.textContent = `${gallery.filter(p => p.unlocked).length}/${gallery.length} Unlocked`;
  const galGrid = document.getElementById('wlGalleryGrid');
  if (galGrid) {
    galGrid.innerHTML = gallery.map(p => `
      <div style="background:#0b1324;border:1.5px solid ${p.unlocked ? sel.accent_color : '#334155'};border-radius:12px;overflow:hidden;cursor:pointer;position:relative;"
           onclick="openWaifuLightbox('${p.url}','${escapeJsStr(p.title)}','${escapeJsStr(p.char_name)}','${escapeJsStr(p.caption)}')">
        <img src="${p.url}" alt="${p.title}" style="width:100%;height:150px;object-fit:cover;display:block;filter:${p.unlocked?'none':'brightness(0.72)'};">
        <div style="position:absolute;top:5px;left:5px;background:rgba(9,13,24,0.86);color:#fde68a;font-size:8.5px;font-weight:800;padding:2px 6px;border-radius:999px;border:1px solid ${sel.accent_color};">
          M${String(p.milestone_num || 1).padStart(2,'0')} • ${p.req_affection || 60}♥ • ${p.spice_tier || 'Stage ' + p.stage}
        </div>
        <div style="padding:6px 8px;">
          <div style="font-size:10.5px;font-weight:800;color:#fde68a;">${p.title}</div>
          <div style="font-size:9.5px;color:#cbd5e1;margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">"${p.caption}"</div>
        </div>
      </div>
    `).join('');
  }

  const visBadge = document.getElementById('wlVisualSkinBadge');
  if (visBadge) visBadge.textContent = `Ped #${sel.ped_id} • ${sel.model_name} (Skin #${sel.skin_number})`;
  const visBox = document.getElementById('wlVisualBox');
  if (visBox) {
    const va = sel.visual_appearance;
    if (typeof va === 'string') {
      visBox.innerHTML = `<div style="color:#f8fafc;">👗 ${va}</div>`;
    } else if (va && typeof va === 'object') {
      visBox.innerHTML = `
        <div style="margin-bottom:5px;">👗 <b>Outfit in GTA SA:</b> <span style="color:#fde68a;">${va.outfit_name || ''}</span></div>
        <div style="margin-bottom:5px;">💇‍♀️ <b>Hair &amp; Eyes:</b> ${va.hair_and_eyes || ''}</div>
        <div style="margin-bottom:5px;">🧵 <b>Attire Details:</b> ${va.attire_details || ''}</div>
        <div>✨ <b>Signature Visual Motifs:</b> <span style="color:#a7f3d0;">${va.signature_motifs || ''}</span></div>
      `;
    }
  }

  const questsBox = document.getElementById('wlQuestsBox');
  if (questsBox) {
    questsBox.innerHTML = (sel.quests_and_events || []).map(q => `
      <div style="background:#0b1324;border:1px solid #263554;border-radius:10px;padding:7px 10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;">
          <b style="font-size:11.5px;color:#fde68a;">⚔️ ${q.title}</b>
          ${q.type ? `<span style="background:#1e293b;color:#38bdf8;font-size:9.5px;font-weight:800;padding:1px 7px;border-radius:999px;">${q.type}</span>` : ''}
        </div>
        <div style="font-size:11px;color:#cbd5e1;margin-top:3px;line-height:1.42;">${q.summary}</div>
      </div>
    `).join('');
  }

  const relBox = document.getElementById('wlRelationsBox');
  if (relBox) {
    relBox.innerHTML = (sel.relationships || []).map(r => `
      <div style="background:#0b1324;border:1px solid #263554;border-radius:9px;padding:6px 9px;font-size:11px;line-height:1.42;">
        <b style="color:#93c5fd;">🤝 ${r.name || r.person}:</b> <span style="color:#e2e8f0;">${r.role || r.relation}</span>
      </div>
    `).join('');
  }

  const quotesBox = document.getElementById('wlQuotesBox');
  if (quotesBox) {
    const quotesHtml = (sel.canonical_quotes || []).map(qt => `<div style="margin-bottom:5px;padding:5px 8px;background:#0b1324;border-left:3px solid ${sel.accent_color};border-radius:6px;font-style:italic;color:#f8fafc;">"${qt}"</div>`).join('');
    const tropesHtml = (sel.fanfic_tropes || []).map(tr => `<div style="margin-bottom:3px;color:#fbcfe8;">• ${tr}</div>`).join('');
    quotesBox.innerHTML = `
      <div style="font-weight:800;color:#fde68a;margin-bottom:4px;">🎙️ Canonical Voice-Overs &amp; Serenitea Pot Lines:</div>
      ${quotesHtml}
      <div style="font-weight:800;color:#f472b6;margin:8px 0 4px 0;">💞 Popular Aether Romance &amp; Fanfic Tropes:</div>
      ${tropesHtml}
    `;
  }
}


function sendContactDmInput() {
  const inp = document.getElementById('ctDmInput');
  if (!inp) return;
  const txt = inp.value.trim();
  if (!txt) return;
  inp.value = '';
  act('contacts_send_dm', {text: txt});
}

function renderContactsApp(ct) {
  if (!ct) return;
  const mTotal = Math.max(0, (ct.total_contacts || 20) - 6);
  const unBadge = document.getElementById('ctUnlockBadge');
  if (unBadge) unBadge.textContent = `${(ct.unlocked_mondstadt_count || 0) + 6}/${ct.total_contacts || 20} Unlocked (${ct.unlocked_mondstadt_count || 0}/${mTotal} Mondstadt)`;
  const tb0 = document.getElementById('ctTabBtn-0');
  const tb1 = document.getElementById('ctTabBtn-1');
  if (tb0) tb0.textContent = `All (${ct.total_contacts || 20})`;
  if (tb1) tb1.textContent = `🍃 Mondstadt (${mTotal})`;
  [0, 1, 2].forEach(i => {
    const b = document.getElementById('ctTabBtn-' + i);
    if (b) b.classList.toggle('active', i === (ct.tab_idx || 0));
  });

  const listEl = document.getElementById('ctListBox');
  const items = ct.filtered_contacts || [];
  const sel = ct.selected || items[0] || null;
  if (listEl) {
    listEl.innerHTML = items.map(it => {
      const isSel = sel && sel.key === it.key;
      const bCol = isSel ? '#38bdf8' : (it.unlocked ? '#1e3a5f' : '#334155');
      const bg = isSel ? 'rgba(14,116,144,0.28)' : '#091224';
      const avatarSrc = it.kind === 'mondstadt' ? `/assets/${it.icon_tex}.png` : `/assets/${it.icon_tex}.png`;
      return `<div onclick="act('contacts_select',{key:'${it.key}',open_chat:true})" style="cursor:pointer;background:${bg};border:1.5px solid ${bCol};border-radius:10px;padding:7px 9px;display:flex;align-items:center;justify-content:space-between;gap:8px;">
        <div style="display:flex;align-items:center;gap:8px;min-width:0;">
          <img src="${avatarSrc}" alt="${it.name}" style="width:36px;height:36px;border-radius:50%;border:1.5px solid ${it.accent};object-fit:cover;filter:${it.unlocked?'none':'grayscale(0.75) brightness(0.7)'};">
          <div style="min-width:0;">
            <div style="font-size:12px;font-weight:800;color:${it.unlocked?'#f8fafc':'#94a3b8'};">${it.unlocked ? '🟢' : '🔒'} ${it.name} <span style="font-size:10px;color:#93c5fd;font-weight:600;">• ${it.title}</span></div>
            <div style="font-size:10.5px;color:#cbd5e1;">📍 ${it.zone} (${it.dist_str}) • <b style="color:${it.unlocked?'#6ee7b7':'#fbbf24'};">${it.status_badge}</b></div>
          </div>
        </div>
        <button class="pill" onclick="event.stopPropagation();act('contacts_pin_gps',{key:'${it.key}'})" title="Pin GPS">📍 GPS</button>
      </div>`;
    }).join('');
  }

  const hdrEl = document.getElementById('ctSelHeader');
  const bodyEl = document.getElementById('ctChatBody');
  if (!sel || !bodyEl) return;
  if (hdrEl) hdrEl.textContent = `💬 ${sel.name} — ${sel.title}`;

  if (!sel.unlocked) {
    bodyEl.innerHTML = `<div style="background:#0b1324;border:1px dashed #f59e0b;border-radius:10px;padding:12px;text-align:center;">
      <div style="font-size:13px;font-weight:800;color:#fde68a;margin-bottom:4px;">🔒 Social Link Not Yet Unlocked</div>
      <div style="font-size:11.5px;color:#cbd5e1;line-height:1.45;margin-bottom:10px;">
        Travel to <b>${sel.zone}</b> (${sel.dist_str}) and press <b>[E]</b> to greet <b>${sel.name}</b> in person first! Once you've met face-to-face, remote phone messaging unlocks permanently.
      </div>
      <button class="btn btn-gold" onclick="act('contacts_pin_gps',{key:'${sel.key}'})">📍 Pin Red 'T' GPS Waypoint (${sel.dist_str})</button>
    </div>`;
    return;
  }

  let histHtml = '';
  if (sel.kind === 'mondstadt') {
    const turns = sel.history || [];
    histHtml = turns.length ? turns.map(t => `
      <div style="align-self:flex-end;background:#0369a1;color:#f8fafc;padding:6px 10px;border-radius:10px 10px 2px 10px;max-width:85%;font-size:11.5px;"><b>Aether:</b> ${t.user}</div>
      <div style="align-self:flex-start;background:#0f172a;border:1px solid #334155;color:#e2e8f0;padding:7px 10px;border-radius:10px 10px 10px 2px;max-width:90%;font-size:11.5px;line-height:1.42;"><b style="color:#fde68a;">${sel.name}:</b> ${t.reply}</div>
    `).join('') : `<div style="background:#0f172a;border:1px solid #334155;color:#e2e8f0;padding:8px 10px;border-radius:10px;font-size:11.5px;"><b style="color:#fde68a;">${sel.name}:</b> ${sel.last_reply}</div>`;
  } else {
    histHtml = (sel.history || []).map(m => m.role === 'user'
      ? `<div style="align-self:flex-end;background:#9d174d;color:#fff;padding:6px 10px;border-radius:10px 10px 2px 10px;max-width:85%;font-size:11.5px;"><b>Aether:</b> ${m.content}</div>`
      : `<div style="align-self:flex-start;background:#0f172a;border:1px solid #4c1d95;color:#fce7f3;padding:7px 10px;border-radius:10px 10px 10px 2px;max-width:90%;font-size:11.5px;"><b style="color:#f9a8d4;">${sel.name}:</b> ${m.content}</div>`
    ).join('');
  }

  const choicesHtml = (sel.choices || []).map(c =>
    `<button class="pill" style="text-align:left;border-color:#38bdf8;color:#e0f2fe;" onclick="act('contacts_send_dm',{key:'${sel.key}',choice_id:'${escapeJsStr(c.id)}'})">➤ ${c.label}</button>`
  ).join('');

  bodyEl.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;background:#081122;border:1px solid #1e3a5f;border-radius:10px;padding:8px;margin-bottom:8px;">
      <img src="${sel.sprite_url}" alt="${sel.name}" style="width:64px;height:64px;object-fit:contain;background:radial-gradient(circle,rgba(56,189,248,0.22),transparent 70%);border-radius:8px;">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.4;">
        <div><b style="color:#fde68a;">Mood:</b> ${sel.mood_label || 'Calm'} • <b style="color:#6ee7b7;">Memories:</b> ${sel.memories_count || 0} notes</div>
        ${sel.pending ? `<div style="color:#38bdf8;font-weight:800;margin-top:2px;">⏳ ${sel.name} is typing a reply...</div>` : ''}
        ${sel.last_error ? `<div style="color:#fca5a5;margin-top:2px;">⚠️ ${sel.last_error}</div>` : ''}
      </div>
    </div>
    <div style="max-height:210px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;margin-bottom:8px;padding-right:3px;">${histHtml}</div>
    <div style="display:flex;flex-direction:column;gap:4px;margin-bottom:8px;">${choicesHtml}</div>
    <div style="display:flex;gap:5px;">
      <input type="text" id="ctDmInput" onkeydown="if(event.key==='Enter')sendContactDmInput()" placeholder="Message ${sel.name} remotely..." style="flex:1;">
      <button class="btn btn-blue" style="flex:0 0 auto;padding:6px 12px;" onclick="sendContactDmInput()">Send ➤</button>
    </div>
  `;
}

async function pollState() {
  try {
    const res = await fetch('/api/state');
    STATE = await res.json();
    renderAll();
  } catch (e) {}
}

setInterval(pollState, 1000);
pollState();
</script>
</body>
</html>
"""

