"""
EagleCompanion.py v4.0 — Chronological 2010-2025 Life, Markets, Multi-Match League Sportsbook,
Lottery, Full-Text Newspaper, Direct Keypad Input & In-Game Event Notification Banner
for Project Eagle v1.3 Gameplay Lab.
"""

import ctypes
import ctypes.wintypes as wt
import datetime
import json
import math
import random
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from eagle_dialogue.paimon_phone import PaimonPhone
from eagle_debug_system import EagleDebugSystem

from eagle_historical_data import (
    CRYPTO_ASSETS,
    LEAGUE_TEAMS,
    LEAGUES,
    LOTTERY_6DIGIT_TIERS,
    SCRATCH_CARD_TYPES,
    START_DATE,
    STOCK_AND_COMMODITY_ASSETS,
    generate_daily_fixtures,
    generate_daily_newspaper,
    get_chronological_target_price,
    to_clean_viet_ascii,
    wrap_hud_lines,
)
from eagle_gg_map_pois import (
    CURATED_GG_MAP_POIS,
    GG_MAP_CATEGORIES,
    GG_MAP_CATEGORIES_EN,
    GG_MAP_CATEGORIES_VI,
    compute_compass_dir,
    format_distance,
    get_gg_map_categories,
    get_pois_for_category,
    localize_poi_item,
)
from eagle_map_inspector import (
    BUG_CATEGORIES,
    BUG_CATEGORIES_EN,
    BUG_CATEGORIES_VI,
    EagleMapInspector,
    get_bug_categories,
)
from eagle_phone_ui import EAGLE_PHONE_HTML
from eagle_dialogue.paimon_web import wrap_handler

PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400
TH32CS_SNAPPROCESS = 0x00000002

ADDR_PLAYER_PED_PTR = 0x00B7CD98     # CWorld::Players[0].m_pPed
ADDR_PLAYER_MONEY = 0x00B7CE50       # CWorld::Players[0].m_nMoney
ADDR_PLAYER_DISP_MONEY = 0x00B7CE54  # CWorld::Players[0].m_nDisplayMoney
ADDR_CLOCK_HOURS = 0x00B70153        # CClock::ms_nGameClockHours (uint8)
ADDR_CLOCK_MINUTES = 0x00B70152      # CClock::ms_nGameClockMinutes (uint8)
ADDR_GAME_CURR_AREA = 0x00B72914     # CGame::currArea (int32 active interior ID)
ADDR_TARGET_BLIP_INDEX = 0x00BA6774  # FrontEndMenuManager.m_nTargetBlipIndex (Native 'T' Waypoint handle)
ADDR_RADAR_TRACE_DEFAULT = 0x00BA86F0     # CRadar::ms_RadarTrace default base (175 * 40B)
ADDR_FLA_TRACE_BASE_PATCH = 0x005838B2    # Immediate u32 in CRadar::SetCoordBlip relocated by FLA (verified in PECore.asi 0x100D1A35)
ADDR_FLA_TRACE_COUNT_PATCH = 0x0058384E   # Immediate u32 (MAX_RADAR_TRACES=3000) in CRadar::SetCoordBlip patched by FLA (PECore.asi 0x100D1A48)
ADDR_EAGLE_MAILBOX = 0x00CAFE00      # 24-byte PAGE_READWRITE RAM mailbox in _rwdseg
EAGLE_MAILBOX_MAGIC = 0x4541474C     # 'EAGL'

UNSTUCK_MODES_EN = [
    ("recall_3s", "Safe Ground 3s Before Fall"),
    ("step_back_5m", "Step Back 5m (Escape Invisible Wall)"),
    ("lift_surface", "Lift to Surface (+4m / Z>=15m)"),
]
UNSTUCK_MODES_VI = [
    ("recall_3s", "Ve Vi Tri An Toan 3s Truoc Khi Roi"),
    ("step_back_5m", "Lui Lai 5m Thoat Ket Tuong Vo Hinh"),
    ("lift_surface", "Nang Cao Len Mat Dat (+4m / Z>=15m)"),
]
UNSTUCK_MODES = UNSTUCK_MODES_EN

AMOUNT_PRESETS = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 25000, 50000]
TRADE_MODES_EN = [
    ("spot_buy", 1, "Spot BUY"),
    ("spot_sell", 1, "Spot SELL"),
    ("fut_long", 5, "LONG 5x"),
    ("fut_short", 5, "SHORT 5x"),
    ("fut_long", 10, "LONG 10x"),
    ("fut_short", 10, "SHORT 10x"),
    ("fut_long", 25, "LONG 25x"),
    ("fut_short", 25, "SHORT 25x"),
    ("fut_long", 50, "LONG 50x"),
    ("fut_short", 50, "SHORT 50x"),
]
TRADE_MODES_VI = [
    ("spot_buy", 1, "Spot MUA"),
    ("spot_sell", 1, "Spot BAN"),
    ("fut_long", 5, "LONG 5x"),
    ("fut_short", 5, "SHORT 5x"),
    ("fut_long", 10, "LONG 10x"),
    ("fut_short", 10, "SHORT 10x"),
    ("fut_long", 25, "LONG 25x"),
    ("fut_short", 25, "SHORT 25x"),
    ("fut_long", 50, "LONG 50x"),
    ("fut_short", 50, "SHORT 50x"),
]
TRADE_MODES = TRADE_MODES_EN

SPORT_PICKS_EN = [
    ("HOME", "1 (Home Win)"),
    ("DRAW", "X (Draw)"),
    ("AWAY", "2 (Away Win)"),
    ("OVER", "Over (O)"),
    ("UNDER", "Under (U)"),
]
SPORT_PICKS_VI = [
    ("HOME", "1 (Chu Thang)"),
    ("DRAW", "X (Hoa)"),
    ("AWAY", "2 (Khach Thang)"),
    ("OVER", "Tai (Over)"),
    ("UNDER", "Xiu (Under)"),
]
SPORT_PICKS = SPORT_PICKS_EN

LOTTO_SUBPAGES_EN = [
    "1/4: 3x3 Scratch Card (Instant 0s)",
    "2/4: Daily 6D & 2D/3D Lotto (16:30 Draw)",
    "3/4: Vietlott 6/45 & 6/55 (18:00 Draw)",
    "4/4: Keno & Max 3D (Instant 0s)",
]
LOTTO_SUBPAGES_VI = [
    "1/4: Ve Cao 3x3 (Cao Ngay 0s)",
    "2/4: XSKT & Lo De (Quay 16:30)",
    "3/4: Vietlott 6/45 & 6/55 (Quay 18:00)",
    "4/4: Keno & Max 3D (Quay Nhanh 0s)",
]
LOTTO_SUBPAGES = LOTTO_SUBPAGES_EN

SCRATCH_TIERS_EN = [
    ("SILVER_20", 20, "Silver Scratch ($20 - $10,000 Jackpot)"),
    ("GOLD_50", 50, "Gold Scratch ($50 - $25,000 Jackpot)"),
    ("DIAMOND_100", 100, "Diamond Scratch ($100 - $50,000 Jackpot)"),
    ("VIP_500", 500, "Fortune VIP Scratch ($500 - $250,000 Jackpot)"),
]
SCRATCH_TIERS_VI = [
    ("SILVER_20", 20, "Ve Cao Bac ($20 - Jackpot $10,000)"),
    ("GOLD_50", 50, "Ve Cao Vang ($50 - Jackpot $25,000)"),
    ("DIAMOND_100", 100, "Ve Cao Kim Cuong ($100 - Jackpot $50,000)"),
    ("VIP_500", 500, "Ve Cao Than Tai VIP ($500 - Jackpot $250,000)"),
]
SCRATCH_TIERS = SCRATCH_TIERS_EN

XSKT_MODES_EN = [
    ("XSKT_6D", 10, "6-Digit Classic Ticket ($10 - $200,000 Top Prize)"),
    ("LODE_DE", 0, "Last 2 Digits Grand Prize (Payout x70 Stake)"),
    ("LODE_LO2", 0, "2-Digit Multi-Roll 18 Draws (Payout x3.5/hit)"),
    ("LODE_3CANG", 0, "Last 3 Digits Grand Prize (Payout x400)"),
]
XSKT_MODES_VI = [
    ("XSKT_6D", 10, "Ve Kien Thiet 6 So ($10 - DB $200,000)"),
    ("LODE_DE", 0, "Danh De 2 So Cuoi DB (An x70 Von GD)"),
    ("LODE_LO2", 0, "Bao Lo 2 So 18 Giai (An x3.5/nhay)"),
    ("LODE_3CANG", 0, "3 Cang Dac Biet 3 So Cuoi (An x400)"),
]
XSKT_MODES = XSKT_MODES_EN

VIETLOTT_MODES_EN = [
    ("MEGA_645", 45, 6, 10, "Mega 6/45 - Standard 6 Balls ($10 | 01..45)"),
    ("POWER_655", 55, 6, 10, "Power 6/55 - Standard 6 Balls ($10 | 01..55)"),
    ("MEGA_BAO7", 45, 7, 70, "Mega 6/45 - System 7 Combo ($70 | 7 Lines)"),
    ("POWER_BAO7", 55, 7, 70, "Power 6/55 - System 7 Combo ($70 | 7 Lines)"),
]
VIETLOTT_MODES_VI = [
    ("MEGA_645", 45, 6, 10, "Mega 6/45 - Ve Don 6 So ($10 | 01..45)"),
    ("POWER_655", 55, 6, 10, "Power 6/55 - Ve Don 6 So ($10 | 01..55)"),
    ("MEGA_BAO7", 45, 7, 70, "Mega 6/45 - Bao 7 So ($70 | 7 To Hop)"),
    ("POWER_BAO7", 55, 7, 70, "Power 6/55 - Bao 7 So ($70 | 7 To Hop)"),
]
VIETLOTT_MODES = VIETLOTT_MODES_EN

KENO_MODES_EN = [
    ("KENO_TAI", 2.0, "Keno BIG (20-ball sum > 810 - Wins x2.0)"),
    ("KENO_XIU", 2.0, "Keno SMALL (20-ball sum <= 810 - Wins x2.0)"),
    ("KENO_CHAN", 2.2, "Keno EVEN (>=11 Even balls - Wins x2.2)"),
    ("KENO_LE", 2.2, "Keno ODD (>=11 Odd balls - Wins x2.2)"),
    ("KENO_NGUHANH", 4.5, "Keno 5 Elements METAL/FIRE/WATER (Wins x4.5)"),
    ("KENO_BAC3", 40.0, "Keno Pick-3 (Match 3 custom numbers - Wins x40)"),
    ("MAX3D_PRO", 400.0, "Max 3D Pro (Dual 3-Digit Pair - Wins x400)"),
]
KENO_MODES_VI = [
    ("KENO_TAI", 2.0, "Keno TAI (Tong 20 bong > 810d - An x2.0)"),
    ("KENO_XIU", 2.0, "Keno XIU (Tong 20 bong <= 810d - An x2.0)"),
    ("KENO_CHAN", 2.2, "Keno CHAN (>=11 bong Chan - An x2.2)"),
    ("KENO_LE", 2.2, "Keno LE (>=11 bong Le - An x2.2)"),
    ("KENO_NGUHANH", 4.5, "Keno Ngu Hanh KIM/HOA/THUY (An x4.5)"),
    ("KENO_BAC3", 40.0, "Keno Bac 3 (Trung 3 so tu chon - An x40)"),
    ("MAX3D_PRO", 400.0, "Vietlott Max 3D Pro (Bo Doi 3 So - An x400)"),
]
KENO_MODES = KENO_MODES_EN

LOTTO_MODES_EN = [
    ("SCRATCH", "SILVER_20", "Silver Scratch ($20 - Instant)"),
    ("SCRATCH", "GOLD_50", "Gold Scratch ($50 - Instant)"),
    ("SCRATCH", "DIAMOND_100", "Diamond Scratch ($100 - Instant)"),
    ("XSKT_6D", "XSKT_6D", "6-Digit Classic Lotto ($10 - 16:30 Draw)"),
    ("VIETLOTT", "MEGA_645", "Mega 6/45 Jackpot ($10 - 18:00 Draw)"),
    ("VIETLOTT", "POWER_655", "Power 6/55 Jackpot ($10 - 18:00 Draw)"),
]
LOTTO_MODES_VI = [
    ("SCRATCH", "SILVER_20", "Ve Cao Bac ($20 - Cao Ngay)"),
    ("SCRATCH", "GOLD_50", "Ve Cao Vang ($50 - Cao Ngay)"),
    ("SCRATCH", "DIAMOND_100", "Ve Cao Kim Cuong ($100 - Cao Ngay)"),
    ("XSKT_6D", "XSKT_6D", "XSKT 6 Chu So ($10 - Quay 16:30)"),
    ("VIETLOTT", "MEGA_645", "Vietlott Mega 6/45 ($10 - Quay 18:00)"),
    ("VIETLOTT", "POWER_655", "Vietlott Power 6/55 ($10 - Quay 18:00)"),
]
LOTTO_MODES = LOTTO_MODES_EN


WALLPAPER_PRESETS = [
    ("ep_wp_furina", "Furina Hydro Neon"),
    ("ep_wp_raiden", "Raiden Electro Violet"),
    ("ep_wp_hutao", "Hu Tao Crimson Night"),
]

MASCOT_PRESETS = [
    ("ep_ms_furina", "Furina (Focalors)"),
    ("ep_ms_hutao", "Hu Tao (Wangsheng)"),
    ("ep_ms_keqing", "Keqing (Yuheng)"),
    ("ep_ms_raiden", "Raiden Shogun (Ei)"),
]

THEME_PRESETS = [
    ("cyan", "Furina Hydro Cyan"),
    ("purple", "Raiden Electro Purple"),
    ("crimson", "Hu Tao Pyro Crimson"),
    ("gold", "Zhongli Geo Gold"),
]

HOME_APPS_EN = [
    (1, "ep_ic_life", "Life & Bank", "Vitality, ATM & Credit"),
    (2, "ep_ic_stck", "Stocks", "Wall St, Gold & Crude Oil"),
    (3, "ep_ic_cryp", "Crypto", "Spot & Futures Exchange"),
    (4, "ep_ic_bet", "Sportsbook", "5 Pro Leagues & Standings"),
    (5, "ep_ic_loto", "Lottery", "3x3 Scratch, 6/45 & Keno"),
    (6, "ep_ic_news", "EagleNews", "2010-2025 Chronicle & Anime"),
    (7, "ep_ic_port", "Portfolio", "Net Worth & P&L Analytics"),
    (8, "ep_ic_bug", "Bug Radar", ".IPL/.COL Inspector & Rescue"),
    (9, "ep_ic_set", "Settings", "Anime Theme & Language (EN/VI)"),
    (10, "ep_ic_ggmap", "GG Map", "631 POIs & Native GPS"),
    (11, "ep_ic_life", "Paimon", "Call your English companion"),
]
HOME_APPS_VI = [
    (1, "ep_ic_life", "Doi Song", "Sinh Hoat, ATM & Tiet Kiem"),
    (2, "ep_ic_stck", "Co Phieu", "San CK, Vang & Dau Tho"),
    (3, "ep_ic_cryp", "Crypto", "San Coin Spot & Futures"),
    (4, "ep_ic_bet", "Bong Da", "Bang Keo 5 Giai & BXH"),
    (5, "ep_ic_loto", "Xo So", "Ve Cao 3x3 & Vietlott"),
    (6, "ep_ic_news", "Bao Eagle", "Tin Tuc & Banner Anime"),
    (7, "ep_ic_port", "Danh Muc", "Phan Bo Von & Loi Nhuan"),
    (8, "ep_ic_bug", "Bao Bug", "Soi .IPL/.COL & Cuu Ho"),
    (9, "ep_ic_set", "Cai Dat", "Giao Dien & Ngon Ngu (EN/VI)"),
    (10, "ep_ic_ggmap", "GG Map", "Ban Do & Chi Duong GPS"),
    (11, "ep_ic_life", "Paimon", "Call your English companion"),
]
HOME_APPS = HOME_APPS_EN



class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wt.DWORD),
        ("cntUsage", wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wt.DWORD),
        ("cntThreads", wt.DWORD),
        ("th32ParentProcessID", wt.DWORD),
        ("pcPriClassBase", wt.LONG),
        ("dwFlags", wt.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


class GTAProcessBridge:
    def __init__(self):
        self.k32 = ctypes.windll.kernel32
        self.u32 = ctypes.windll.user32
        self.handle = None
        self.pid = 0
        self.last_scan = 0.0
        self.key_states = {}
        self._thread_desktops = {}
        self._ensure_interactive_desktop()

    def _ensure_interactive_desktop(self):
        """
        Attaches the current thread to the interactive user desktop ('Default' / InputDesktop)
        so Win32 GetForegroundWindow() and GetAsyncKeyState() work reliably even when
        EagleCompanion.py is spawned from a sandboxed ConPTY / exebox desktop.
        """
        tid = self.k32.GetCurrentThreadId()
        if tid in self._thread_desktops:
            return
        hdesk = self.u32.OpenInputDesktop(0, False, 0x01FF)
        if not hdesk:
            hdesk = self.u32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hdesk:
            self.u32.SetThreadDesktop(hdesk)
            self._thread_desktops[tid] = hdesk

    def try_attach(self) -> bool:
        if self.handle:
            exit_code = wt.DWORD(0)
            if self.k32.GetExitCodeProcess(self.handle, ctypes.byref(exit_code)) and exit_code.value == 259:
                return True
            self.k32.CloseHandle(self.handle)
            self.handle = None
            self.pid = 0

        now = time.time()
        if now - self.last_scan < 1.5:
            return False
        self.last_scan = now

        snap = self.k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == -1 or snap == 0:
            return False

        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
        found_pid = 0
        try:
            if self.k32.Process32First(snap, ctypes.byref(pe)):
                while True:
                    exe_name = pe.szExeFile.decode("ascii", errors="ignore").lower()
                    if exe_name in ("gta_pe.exe", "gta_sa.exe"):
                        found_pid = pe.th32ProcessID
                        break
                    if not self.k32.Process32Next(snap, ctypes.byref(pe)):
                        break
        finally:
            self.k32.CloseHandle(snap)

        if found_pid:
            access = PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION
            h = self.k32.OpenProcess(access, False, found_pid)
            if h:
                self.handle = h
                self.pid = found_pid
                self._apply_engine_safety_patches()
                return True
        return False

    def _apply_engine_safety_patches(self):
        """
        Patches CPathFind::DoPathSearch (0x00451A0A..0x00451B18) in gta_pe.exe so asymmetric
        path link lengths in custom NODES*.DAT (e.g. NODES1890.DAT len 20 vs 19) never cause
        an infinite backtracking loop, and patches PECore.asi so GPS renders on foot too.
        """
        if not self.handle:
            return
        gs = self.read_u32(0x00C8D4C0)
        if gs is None or gs < 7:
            return
        self._ensure_pecore_onfoot_gps_patch()
        self._ensure_streaming_unsigned_patch()
        buf = ctypes.create_string_buffer(2)
        nread = ctypes.c_size_t(0)
        if not self.k32.ReadProcessMemory(self.handle, ctypes.c_void_p(0x00451A7E), buf, 2, ctypes.byref(nread)):
            return
        if buf.raw != b"\x3b\xdf":
            return
        patches = [
            (0x00451A0A, bytes.fromhex("8B6C24109090")),
            (0x00451A1F, bytes.fromhex("0F86F4000000")),
            (0x00451A7E, bytes.fromhex("2BDF8B7C243CEB2E")),
            (0x00451AB4, bytes.fromhex("4383FB02773DEBCA90909090")),
            (0x00451B08, bytes.fromhex("84F6740D")),
            (0x00451B13, bytes.fromhex("0F8CF1FEFFFF")),
        ]
        old_prot = wt.DWORD(0)
        if self.k32.VirtualProtectEx(self.handle, ctypes.c_void_p(0x00451A00), 0x200, 0x40, ctypes.byref(old_prot)):
            for addr, data in patches:
                nw = ctypes.c_size_t(0)
                self.k32.WriteProcessMemory(self.handle, ctypes.c_void_p(addr), data, len(data), ctypes.byref(nw))
            self.k32.VirtualProtectEx(
                self.handle, ctypes.c_void_p(0x00451A00), 0x200, old_prot.value, ctypes.byref(old_prot)
            )

    def _ensure_pecore_onfoot_gps_patch(self):
        """
        Patches PECore.asi at RVA +0x000D0743 (8B 81 8C 05 00 00 -> EB 45 90 90 90 90)
        so PECore.asi computes and draws the GPS route line on the Radar immediately
        both when the player is walking/running on foot AND when driving a vehicle.
        """
        if not self.handle:
            return
        # PECore.asi hooks 0x005BA345 with E8 <rel32> -> pecore_base + 0x000C6290
        hook_raw = self.read_bytes(0x005BA345, 5)
        if not hook_raw or hook_raw[0] != 0xE8:
            return
        rel32 = struct.unpack("<i", hook_raw[1:5])[0]
        target_va = (0x005BA34A + rel32) & 0xFFFFFFFF
        pecore_base = (target_va - 0x000C6290) & 0xFFFFFFFF
        if pecore_base < 0x01000000 or self.read_bytes(pecore_base, 2) != b"MZ":
            return
        patch_addr = pecore_base + 0x000D0743
        cur_bytes = self.read_bytes(patch_addr, 6)
        if cur_bytes == b"\x8b\x81\x8c\x05\x00\x00":
            old_prot = wt.DWORD(0)
            if self.k32.VirtualProtectEx(self.handle, ctypes.c_void_p(patch_addr), 16, 0x40, ctypes.byref(old_prot)):
                nw = ctypes.c_size_t(0)
                self.k32.WriteProcessMemory(
                    self.handle, ctypes.c_void_p(patch_addr), b"\xeb\x45\x90\x90\x90\x90", 6, ctypes.byref(nw)
                )
                self.k32.VirtualProtectEx(
                    self.handle, ctypes.c_void_p(patch_addr), 16, old_prot.value, ctypes.byref(old_prot)
                )

    def clear_hotkey_states(self):
        """Syncs current key states so held keys during loading/menus do not trigger rising edges."""
        self._ensure_interactive_desktop()
        for vk in list(self.key_states.keys()):
            self.key_states[vk] = bool(self.u32.GetAsyncKeyState(vk) & 0x8000)

    def is_game_active_and_unpaused(self) -> bool:
        """
        Returns True only when:
        1) gta_pe.exe / gta_sa.exe is attached and is the active foreground window,
        2) FrontEndMenuManager.m_bMenuActive (0x00BA677B) == 0 (not in Main Menu / Pause Map),
        3) Player ped pointer (0x00B6F5F0) is valid in world memory,
        4) At least 1.5s has elapsed since leaving the Main Menu / Loading screen so pressing Enter
           to load a save game never triggers an app open on the first frame of gameplay.
        """
        if not self.try_attach():
            return False
        self._ensure_interactive_desktop()
        now = time.time()
        fg_hwnd = self.u32.GetForegroundWindow()
        if fg_hwnd:
            fg_pid = wt.DWORD(0)
            self.u32.GetWindowThreadProcessId(fg_hwnd, ctypes.byref(fg_pid))
            if fg_pid.value and fg_pid.value != self.pid:
                return False
        menu_active = self.read_u8(0x00BA677B)
        ped_ptr = self.read_u32(ADDR_PLAYER_PED_PTR)
        if menu_active is None or menu_active != 0 or not ped_ptr or ped_ptr < 0x00400000:
            self.menu_cooldown_until = now + 1.5
            return False
        if now < getattr(self, "menu_cooldown_until", 0.0):
            return False
        return True

    def poll_hotkey_edge(self, vk: int) -> bool:
        """Detects rising edge of virtual key `vk` via Win32 GetAsyncKeyState."""
        self._ensure_interactive_desktop()
        state = self.u32.GetAsyncKeyState(vk)
        down = bool(state & 0x8000)
        prev = self.key_states.get(vk, False)
        self.key_states[vk] = down
        return down and not prev

    def is_key_down(self, vk: int) -> bool:
        """Checks if virtual key `vk` is currently held down."""
        self._ensure_interactive_desktop()
        return bool(self.u32.GetAsyncKeyState(vk) & 0x8000)

    def read_bytes(self, addr: int, size: int):
        if not self.try_attach():
            return None
        buf = ctypes.create_string_buffer(size)
        nread = ctypes.c_size_t(0)
        ok = self.k32.ReadProcessMemory(self.handle, ctypes.c_void_p(addr), buf, size, ctypes.byref(nread))
        if not ok or nread.value != size:
            return None
        return buf.raw

    def write_bytes(self, addr: int, data: bytes) -> bool:
        if not self.try_attach():
            return False
        nwritten = ctypes.c_size_t(0)
        ok = self.k32.WriteProcessMemory(self.handle, ctypes.c_void_p(addr), data, len(data), ctypes.byref(nwritten))
        return bool(ok and nwritten.value == len(data))

    def read_u32(self, addr: int):
        raw = self.read_bytes(addr, 4)
        return struct.unpack("<I", raw)[0] if raw else None

    def read_i32(self, addr: int):
        raw = self.read_bytes(addr, 4)
        return struct.unpack("<i", raw)[0] if raw else None

    def write_i32(self, addr: int, val: int) -> bool:
        return self.write_bytes(addr, struct.pack("<i", int(val)))

    def read_f32(self, addr: int):
        raw = self.read_bytes(addr, 4)
        return struct.unpack("<f", raw)[0] if raw else None

    def write_f32(self, addr: int, val: float) -> bool:
        return self.write_bytes(addr, struct.pack("<f", float(val)))

    def read_u8(self, addr: int):
        raw = self.read_bytes(addr, 1)
        return struct.unpack("<B", raw)[0] if raw else None

    def read_live_player(self):
        ped_ptr = self.read_u32(ADDR_PLAYER_PED_PTR)
        if not ped_ptr or ped_ptr < 0x00400000:
            return None
        money = self.read_i32(ADDR_PLAYER_MONEY)
        hp = self.read_f32(ped_ptr + 0x540)
        max_hp = self.read_f32(ped_ptr + 0x544)
        armor = self.read_f32(ped_ptr + 0x548)
        hours = self.read_u8(ADDR_CLOCK_HOURS)
        mins = self.read_u8(ADDR_CLOCK_MINUTES)
        area_code = self.read_u8(ped_ptr + 0x2F) or 0
        game_area = self.read_i32(ADDR_GAME_CURR_AREA) or 0

        ped_flags_b1 = self.read_u8(ped_ptr + 0x46D) or 0
        in_vehicle = bool(ped_flags_b1 & 0x01)
        veh_ptr = self.read_u32(ped_ptr + 0x58C) if in_vehicle else 0
        active_ent = veh_ptr if (in_vehicle and veh_ptr and veh_ptr > 0x00400000) else ped_ptr

        pos = None
        heading = 0.0
        mat_ptr = self.read_u32(active_ent + 0x14) or self.read_u32(ped_ptr + 0x14)
        if mat_ptr and mat_ptr > 0x00400000:
            mat_raw = self.read_bytes(mat_ptr, 0x40)
            if mat_raw and len(mat_raw) >= 0x3C:
                fx, fy, _fz = struct.unpack("<fff", mat_raw[0x10:0x1C])
                pos = struct.unpack("<fff", mat_raw[0x30:0x3C])
                if abs(fx) > 1e-5 or abs(fy) > 1e-5:
                    heading = (math.degrees(math.atan2(-fx, fy)) + 360.0) % 360.0
        if pos is None:
            raw_pl = self.read_bytes(active_ent + 0x04, 16)
            if raw_pl:
                px, py, pz, rot_rad = struct.unpack("<ffff", raw_pl)
                pos = (px, py, pz)
                heading = (math.degrees(rot_rad) + 360.0) % 360.0

        vel = (0.0, 0.0, 0.0)
        raw_vel = self.read_bytes(active_ent + 0x44, 12)
        if raw_vel:
            vel = struct.unpack("<fff", raw_vel)

        if money is None or hp is None:
            return None
        return {
            "ped_ptr": ped_ptr,
            "veh_ptr": veh_ptr or 0,
            "in_vehicle": in_vehicle,
            "area_code": int(area_code),
            "game_area": int(game_area),
            "cash": int(money),
            "health": max(0, int(round(hp))),
            "max_health": max(100, int(round(max_hp or 100.0))),
            "armor": max(0, int(round(armor or 0.0))),
            "hours": int(hours or 12),
            "mins": int(mins or 0),
            "pos": pos,
            "heading": round(heading, 1),
            "vel": vel,
        }

    def teleport_player(self, x: float, y: float, z: float, area_code: int = None) -> bool:
        """
        Safely teleports the player (and vehicle if driving) to (x, y, z) and zeroes out
        move/turn velocity vectors so falling momentum never causes impact damage on landing.
        """
        ped_ptr = self.read_u32(ADDR_PLAYER_PED_PTR)
        if not ped_ptr or ped_ptr < 0x00400000:
            return False
        xyz_bytes = struct.pack("<fff", float(x), float(y), float(z))
        zero_vel = b"\x00" * 24  # m_vecMoveSpeed (12B) + m_vecTurnSpeed (12B)

        ok = self.write_bytes(ped_ptr + 0x04, xyz_bytes)
        ped_mat = self.read_u32(ped_ptr + 0x14)
        if ped_mat and ped_mat > 0x00400000:
            ok = self.write_bytes(ped_mat + 0x30, xyz_bytes) or ok
        self.write_bytes(ped_ptr + 0x44, zero_vel)

        ped_flags_b1 = self.read_u8(ped_ptr + 0x46D) or 0
        if ped_flags_b1 & 0x01:
            veh_ptr = self.read_u32(ped_ptr + 0x58C)
            if veh_ptr and veh_ptr > 0x00400000:
                self.write_bytes(veh_ptr + 0x04, xyz_bytes)
                veh_mat = self.read_u32(veh_ptr + 0x14)
                if veh_mat and veh_mat > 0x00400000:
                    self.write_bytes(veh_mat + 0x30, xyz_bytes)
                self.write_bytes(veh_ptr + 0x44, zero_vel)

        if area_code is not None:
            self.write_bytes(ped_ptr + 0x2F, struct.pack("<B", int(area_code) & 0xFF))
            self.write_i32(ADDR_GAME_CURR_AREA, int(area_code))
        return ok

    def add_money(self, delta: int) -> bool:
        cur = self.read_i32(ADDR_PLAYER_MONEY)
        if cur is None:
            return False
        new_val = max(0, cur + int(delta))
        ok1 = self.write_i32(ADDR_PLAYER_MONEY, new_val)
        self.write_i32(ADDR_PLAYER_DISP_MONEY, new_val)
        return ok1

    def add_health(self, delta: float, set_full: bool = False, allow_fatal: bool = False) -> bool:
        ped_ptr = self.read_u32(ADDR_PLAYER_PED_PTR)
        if not ped_ptr or ped_ptr < 0x00400000:
            return False
        cur_hp = self.read_f32(ped_ptr + 0x540) or 100.0
        max_hp = self.read_f32(ped_ptr + 0x544) or 100.0
        target_max = max(100.0, float(max_hp))
        if set_full:
            new_hp = max(150.0, target_max)
        else:
            min_hp = 0.0 if allow_fatal else 2.0
            new_hp = min(max(150.0, target_max), max(min_hp, cur_hp + float(delta)))
        return self.write_f32(ped_ptr + 0x540, new_hp)

    def _ensure_streaming_unsigned_patch(self):
        """
        Patches the 7 signed 32-bit comparisons (JL/JGE -> JB/JAE) in
        CStreaming::DeleteRwObjectsBehindCamera (0x40D7C0) and its 4 sub-functions
        so ms_memoryUsed / ms_memoryAvailable work as unsigned uint32_t above 2048 MB (0x80000000).
        """
        if not self.handle:
            return
        unsigned_patches = (
            (0x004099C0, 0x7C, 0x72),
            (0x00409A69, 0x7C, 0x72),
            (0x0040D2C8, 0x7C, 0x72),
            (0x0040D3A7, 0x7C, 0x72),
            (0x0040D7CF, 0x8C, 0x82),
            (0x0040E0FF, 0x7C, 0x72),
            (0x0040E115, 0x7D, 0x73),
        )
        for va, old_b, new_b in unsigned_patches:
            cur = self.read_u8(va)
            if cur == old_b:
                old_prot = wt.DWORD(0)
                if self.k32.VirtualProtectEx(self.handle, ctypes.c_void_p(va), 1, 0x40, ctypes.byref(old_prot)):
                    nw = ctypes.c_size_t(0)
                    self.k32.WriteProcessMemory(
                        self.handle, ctypes.c_void_p(va), bytes([new_b]), 1, ctypes.byref(nw)
                    )
                    self.k32.VirtualProtectEx(
                        self.handle, ctypes.c_void_p(va), 1, old_prot.value, ctypes.byref(old_prot)
                    )

    def _get_radar_trace_table(self) -> tuple[int, int]:
        """
        Resolves the active CRadar::ms_RadarTrace base pointer and max trace count,
        supporting both vanilla (0x00BA86F0, 175 slots) and Fastman92 Limit Adjuster
        relocated radar trace pools (patched at 0x005838B2 and 0x0058384E, 3000 slots,
        matching PECore.asi at 0x100D1A35 and 0x100D1A48).
        """
        trace_base = self.read_u32(ADDR_FLA_TRACE_BASE_PATCH) or ADDR_RADAR_TRACE_DEFAULT
        if not trace_base or not (0x00400000 <= trace_base < 0x7FFF0000):
            trace_base = ADDR_RADAR_TRACE_DEFAULT
        max_traces = self.read_u32(ADDR_FLA_TRACE_COUNT_PATCH) or 175
        if not (175 <= max_traces <= 100000):
            max_traces = 175
        return int(trace_base), int(max_traces)

    def clear_target_waypoint(self) -> bool:
        """
        Clears FrontEndMenuManager.m_nTargetBlipIndex (0x00BA6774) and zeroes the active
        sRadarTrace slot in CRadar::ms_RadarTrace (matching CRadar::ClearBlip at 0x00587C10).
        """
        if not self.try_attach():
            return False
        old_handle = self.read_u32(ADDR_TARGET_BLIP_INDEX)
        if old_handle:
            trace_base, max_traces = self._get_radar_trace_table()
            slot = old_handle & 0xFFFF
            if 0 <= slot < max_traces:
                entry_addr = trace_base + slot * 40
                b26 = self.read_u8(entry_addr + 0x26) or 0
                self.write_bytes(entry_addr + 0x24, struct.pack("<BBB", 0, 0, b26 & 0xC0))
            self.write_i32(ADDR_TARGET_BLIP_INDEX, 0)
        return True

    def set_target_waypoint(self, x: float, y: float, z: float = 0.0) -> int:
        """
        Places the native Project Eagle Target Waypoint (exact equivalent of pressing 'T' on Pause Map:
        CRadar::SetCoordBlip(4, x, y, 0.0f, 2, 3) + CRadar::SetBlipSprite(handle, 41) + write handle
        to FrontEndMenuManager.m_nTargetBlipIndex at 0x00BA6774) so PECore.asi automatically renders
        the GPS route line on the radar without opening Pause Map.
        """
        if not self.try_attach():
            return 0
        self._ensure_pecore_onfoot_gps_patch()
        trace_base, max_traces = self._get_radar_trace_table()
        old_handle = self.read_u32(ADDR_TARGET_BLIP_INDEX) or 0
        reuse_slot = None
        if old_handle != 0:
            old_slot = old_handle & 0xFFFF
            if 0 <= old_slot < max_traces:
                reuse_slot = old_slot
                entry_addr = trace_base + old_slot * 40
                b26 = self.read_u8(entry_addr + 0x26) or 0
                self.write_bytes(entry_addr + 0x24, struct.pack("<BBB", 0, 0, b26 & 0xC0))
            self.write_i32(ADDR_TARGET_BLIP_INDEX, 0)

        target_slot = reuse_slot
        if target_slot is None:
            chunk_slots = 64
            for base_idx in range(1, max_traces, chunk_slots):
                cnt = min(chunk_slots, max_traces - base_idx)
                raw_chunk = self.read_bytes(trace_base + base_idx * 40, cnt * 40)
                if not raw_chunk:
                    break
                for i in range(cnt):
                    f25 = raw_chunk[i * 40 + 0x25]
                    if (f25 & 0x02) == 0:
                        target_slot = base_idx + i
                        break
                if target_slot is not None:
                    break

        if target_slot is None:
            target_slot = 170

        entry_addr = trace_base + target_slot * 40
        old_raw = self.read_bytes(entry_addr, 40) or (b"\x00" * 40)
        old_counter = struct.unpack("<H", old_raw[0x14:0x16])[0]
        old_f26 = old_raw[0x26]
        new_counter = 1 if old_counter >= 0xFFFE else (old_counter + 1)
        if new_counter == 0:
            new_counter = 1

        new_f26 = (old_f26 & 0xC0) | 0x12  # BLIP_COORD (4 << 2) | BLIP_DISPLAY_BLIPONLY (2)
        trace_payload = struct.pack(
            "<IIfffHHfHHIBBBB",
            8,               # +0x00: m_nColour = 8
            0,               # +0x04: m_nEntityHandle = 0
            float(x),        # +0x08: m_vPosition.x
            float(y),        # +0x0C: m_vPosition.y
            0.0,             # +0x10: m_vPosition.z (0.0f matches Pause Map 'T' at 0x005775D9)
            new_counter,     # +0x14: m_nCounter (uint16)
            0,               # +0x16: align pad
            1.0,             # +0x18: m_fSphereRadius = 1.0f
            1,               # +0x1C: m_nBlipSize = 1 (set by SetBlipSprite at 0x00583D9F)
            0,               # +0x1E: align pad
            0,               # +0x20: m_pEntryExit = NULL
            41,              # +0x24: m_nBlipSprite = 41 (RADAR_SPRITE_WAYPOINT)
            3,               # +0x25: m_bBright (1) | m_bTrackingBlip (2) = 3
            new_f26,         # +0x26: BLIP_COORD | BLIP_DISPLAY_BLIPONLY
            0,               # +0x27: align pad
        )
        if not self.write_bytes(entry_addr, trace_payload):
            return 0
        handle = ((new_counter & 0xFFFF) << 16) | (target_slot & 0xFFFF)
        self.write_bytes(ADDR_TARGET_BLIP_INDEX, struct.pack("<I", handle))
        return handle

    def read_target_waypoint(self):
        if not self.try_attach():
            return None
        handle = self.read_u32(ADDR_TARGET_BLIP_INDEX)
        if not handle:
            return None
        trace_base, max_traces = self._get_radar_trace_table()
        slot = handle & 0xFFFF
        expected_counter = (handle >> 16) & 0xFFFF
        if slot >= max_traces:
            return None
        raw = self.read_bytes(trace_base + slot * 40, 40)
        if not raw or len(raw) < 40:
            return None
        wx, wy, wz = struct.unpack("<fff", raw[0x08:0x14])
        counter = struct.unpack("<H", raw[0x14:0x16])[0]
        sprite = raw[0x24]
        f25 = raw[0x25]
        if counter != expected_counter or (f25 & 0x02) == 0:
            return None
        return {
            "handle": handle,
            "slot": slot,
            "x": round(wx, 2),
            "y": round(wy, 2),
            "z": round(wz, 2),
            "sprite": int(sprite),
        }


class EagleCompanionEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.cleo_dir = base_dir / "cleo"
        self.cleo_dir.mkdir(parents=True, exist_ok=True)
        self.ini_path = self.cleo_dir / "EagleLifeState.ini"
        self.hud_dat_path = self.cleo_dir / "EaglePhoneHUD.dat"
        self.hud_lua_path = self.cleo_dir / "EaglePhoneState.lua"
        self._last_lua_payload = ""
        self.state_version = 1
        self.last_attached_pid = 0
        self.lock = threading.Lock()
        self.bridge = GTAProcessBridge()

        # Initialize Map Bug Reporter & Auto-Inspector (Hạng mục 1)
        self.map_inspector = EagleMapInspector(base_dir)
        self.map_inspector.start_background_index()

        # Initialize Zero-Overhead On-Demand Debugger, Tester & Unified Logger (Default: LITE mode)
        self.debug_sys = EagleDebugSystem(base_dir, self.map_inspector.md_report_path.parent)

        # Load ATMs
        self.atms = []
        for p in [base_dir / "world_pois.json", base_dir.parent.parent / "staging" / "project-eagle" / "gameplay-lab-poc" / "world_pois.json"]:
            if p.exists():
                try:
                    self.atms = json.loads(p.read_text(encoding="utf-8")).get("atms", [])
                    break
                except Exception:
                    pass

        # Master Chronological Calendar (Starts 01/01/2010 = Day 1)
        self.day = 1
        self.current_date = START_DATE
        self.last_game_hour = -1
        self.drew_1630_today = False
        self.drew_1800_today = False

        # Player & Banking State (EaglePhone OS v5.0: app=0 is SpringBoard Home Screen)
        self.lang = "en"  # Default language: "en" (English) | toggleable to "vi" (Tiếng Việt)
        self.phone_open = 1
        self.phone_app = 0  # 0:Home, 1:Life, 2:Stocks, 3:Crypto, 4:Sports, 5:Lotto, 6:News, 7:Portfolio, 8:BugInspector, 9:Settings, 10:GGMap
        self.home_cursor_idx = 0  # 0..9 on Home Screen (11 App Icons: 1.Life & Bank .. 10.GG Map)
        self.last_home_col = 0
        self.app_subpage = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        self.wp_idx = 0      # 0: Furina, 1: Raiden, 2: Hu Tao
        self.mascot_idx = 0  # 0: Furina, 1: Hu Tao, 2: Keqing, 3: Raiden
        self.theme_idx = 0   # 0: Cyan, 1: Purple, 2: Crimson, 3: Gold
        self.ram_attached = False
        self.cash = 500
        self.bank = 5500
        self.savings = 2000
        self.loan = 0
        self.loan_days_left = 0
        self.loan_overdue = False
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.hunger = 88
        self.energy = 92
        self.clock_str = "08:00"
        self.nearest_atm = "140m"
        self.last_live_hp = None
        self.last_live_cash = None
        self.ignore_next_hp_jump = False
        self.last_toast = "EaglePhone OS v5.0: Press F7 Phone | I/K/J/L Select App | F9 Open | Backspace/F8 Back!"

        # Live Coordinates, Position Trail Buffer (5-8s) & Safe Ground Recall State (Hạng mục 1)
        self.player_pos = (2495.0, -1687.0, 13.5)
        self.player_heading = 90.0
        self.player_velocity = (0.0, 0.0, 0.0)
        self.player_area_code = 0
        self.player_game_area = 0
        self.player_in_vehicle = False
        self.last_trail_sample_time = 0.0
        self.position_trail = [
            {
                "t": time.time() - i * 0.5,
                "x": 2495.0,
                "y": -1687.0,
                "z": 13.5,
                "heading": 90.0,
                "vz": 0.0,
                "area": 0,
                "in_veh": False,
                "is_safe": True,
            }
            for i in range(10, -1, -1)
        ]
        self.safe_ground_history = list(self.position_trail)
        self.bug_cat_idx = 0           # Index into BUG_CATEGORIES
        self.unstuck_mode_idx = 0      # Index into UNSTUCK_MODES
        self.last_bug_report = self.map_inspector.reports[0] if self.map_inspector.reports else None
        self.last_live_scan = None

        # App 10: GG Map (GTA Genshin Map) & Native 'T' GPS Waypoint State (Hạng mục 5)
        self.ggmap_cat_idx = 0         # 0..9 into GG_MAP_CATEGORIES (0: ALL, 1: LANDMARKS, 2: ACTIVITIES...)
        self.ggmap_poi_idx = 0         # Selected row index inside current category
        self.ggmap_selected_id = None  # Stable POI ID so live distance sorting never jumps selection
        self.active_gps_target = None  # Dict when GPS navigation is active: {id, name, region, x, y, z, handle, dist_2d, compass, set_at}

        # In-Game Top-Center Event Notification Banner (Pop-up on Game Screen)
        self.event_banner = {
            "title": "EAGLEPHONE OS v5.0 READY (PRESS F7 TO OPEN)!",
            "sub": "F7: Phone | I/K/J/L: Select App (1..11) | F9: Open/OK | Backspace/F8: Home",
            "kind": "info",  # info | win | warn | danger
            "until": time.time() + 6.0,
        }

        # Ergonomic Multi-Row Cursor & Direct Number Keypad State (Home + 10 Apps)
        self.app_cursor = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        self.tx_amount = 500
        self.amount_preset_idx = 3  # $500
        self.keypad_active = False
        self.keypad_buffer = ""
        self.keypad_target = "amount"  # "amount" or "lotto"

        # App 1 Sub-selectors
        self.life_meal_idx = 0   # 0: Burger (-$25), 1: Energy Drink (-$15), 2: Sleep Overnight (+1d)
        self.life_bank_idx = 0   # 0: Deposit ATM, 1: Withdraw ATM, 2: Deposit Savings, 3: Withdraw Savings
        self.life_loan_idx = 0   # 0: Borrow Loan, 1: Repay Loan, 2: Repay All Loan

        # App 2 & 3 Sub-selectors
        self.trade_mode_idx = 0  # Index into TRADE_MODES
        self.market_watch_idx = {"stocks": 0, "crypto": 0}

        # App 4 Sub-selectors (Multi-Match League Pages: 5 Leagues x 5 Matches/day)
        self.selected_league_idx = 0   # 0..4 (EPL, LALIGA, SERIE_BUND, UCL, NBA)
        self.sport_match_idx = 0       # 0..4 (Match #1..#5 inside selected league)
        self.sport_pick_idx = 0        # 0..4 (HOME, DRAW, AWAY, OVER, UNDER)

        # App 5 Sub-selectors (4 Dedicated Sub-pages: 0:Scratch, 1:XSKT 16:30, 2:Vietlott 18:00, 3:Keno 0s)
        self.lotto_mode_idx = 3
        self.scratch_tier_idx = 0      # 0: SILVER_20, 1: GOLD_50, 2: DIAMOND_100, 3: VIP_500
        self.xskt_mode_idx = 0         # 0: XSKT_6D ($10), 1: LODE_DE (x70), 2: LODE_LO2 (x3.5), 3: LODE_3CANG (x400)
        self.vietlott_mode_idx = 0     # 0: MEGA_645 ($10), 1: POWER_655 ($10), 2: MEGA_BAO7 ($70), 3: POWER_BAO7 ($70)
        self.keno_mode_idx = 0         # 0..6 (TAI, XIU, CHAN, LE, NGUHANH, BAC3, MAX3D_PRO)
        self.keypad_presets = ["686868", "168168", "797979", "123456", "888888", "397939", "201025"]
        self.keypad_idx = 0
        self.custom_lotto_str = "686868"
        self.vietlott_presets_645 = [
            "05 12 19 26 38 44",
            "07 14 21 28 35 42",
            "03 09 18 27 36 45",
            "02 06 15 24 33 41",
            "08 16 23 31 39 43",
        ]
        self.vietlott_presets_655 = [
            "03 14 22 37 48 54",
            "06 15 25 36 47 55",
            "01 11 23 34 45 52",
            "08 18 29 40 49 53",
            "04 12 26 38 46 51",
        ]
        self.vietlott_preset_idx = 0
        self.custom_vietlott_str = "05 12 19 26 38 44"

        # App 6 Sub-selectors (4 Topic Sub-pages with Anime Banners)
        self.news_sec_idx = 0          # 0: Politics, 1: Finance, 2: Crypto/Tech, 3: Sports
        self.news_step_idx = 1         # 0: -1 Day, 1: +1 Day, 2: +7 Days, 3: +30 Days

        # App 7 Sub-selectors (Unified Portfolio: 0: Gauges, 1: Spot Table, 2: Futures/Bet Table)
        self.port_tab_idx = 0
        self.portfolio_stats = {
            "realized_market_pnl": 0.0,
            "bet_won_count": 0,
            "bet_lost_count": 0,
            "bet_net_pnl": 0,
            "lotto_spent": 30,
            "lotto_won": 0,
            "lotto_net_pnl": -30,
        }

        # Separated Markets: Stocks/Commodities (16) vs Crypto (8)
        self.selected_stock_sym = "XAU"
        self.selected_crypto_sym = "BTC"
        self.stocks_market = {}
        self.crypto_market = {}
        self._init_markets()
        self.futures = []

        # Chronological Sportsbook (Day 1 = Season 1 Week 1 Day 1, 25 matches/day across 5 leagues)
        self.standings = {}
        self._init_standings()
        self.fixtures = generate_daily_fixtures(self.day, lang=self.lang)
        self.sport_history = [
            "🏆 [Season 1 • Opening Day] Premier League, La Liga, Serie A, UCL & NBA officially kick off!"
        ]

        # 4-Page Multi-Game Lottery System (Strictly Separated XSKT 16:30 vs Vietlott 18:00 Mega 6/45 & Power 6/55)
        self.lottery = {
            "xskt_db_prize": 200000,
            "jackpot": 1250000,
            "jackpot_mega645": 1250000,
            "jackpot_power655_jp1": 3200000,
            "jackpot_power655_jp2": 350000,
            "scratch_cells": ["$20", "$100", "★", "$100", "$500", "$20", "💎", "$100", "$40"],
            "last_scratch_msg": "Scratch Cards ($20/$50/$100/$500): Scratch & win instantly (0s)!",
            # XSKT 16:30 Exclusive Results
            "last_6d": "686868",
            "last_xskt_g1": "49201",
            "last_xskt_lo18": ["68", "01", "15", "27", "39", "44", "52", "63", "79", "88"],
            "last_xskt_summary": "6D Lotto (16:30) • Grand: 686868 | 1st: 49201 | 2D Rolls: 68, 01, 15, 27, 39, 79",
            # Vietlott 18:00 Exclusive Results (Mega 6/45 & Power 6/55 Separate!)
            "last_viet": "05-12-19-26-38-44",
            "last_mega645": "05-12-19-26-38-44",
            "last_power655": "03-14-22-37-48-54",
            "last_power655_bonus": "18",
            "last_vietlott_summary": "Vietlott (18:00) • Mega 6/45: 05-12-19-26-38-44 | Power 6/55: 03-14-22-37-48-54 +[18]",
            # Keno 20/80 & Max 3D Instant Draw Results
            "last_keno_balls": "04-09-15-22-31-38-45-52-67-78",
            "last_keno_meta": "20-Ball Sum: 824 pts (BIG) | 11 Even - 9 Odd | Element: FIRE | Max3D: 389 + 712",
            "last_keno_msg": "Keno & Max 3D (Instant 0s): Select a pick & press F9 to draw now!",
            "last_draw_summary": "6D Lotto (16:30): 686868 | Mega 6/45: 05-12-19-26-38-44 | Power 6/55: 03-14-22-37-48-54 +[18]",
            "tickets": [
                {"type": "XSKT_6D", "numbers": "686868", "cost": 10},
                {"type": "MEGA_645", "numbers": "05 12 19 26 38 44", "cost": 10},
                {"type": "POWER_655", "numbers": "03 14 22 37 48 54", "cost": 10},
            ],
        }


        # Daily Newspaper (01/01/2010 -> 31/12/2025)
        self.newspaper = generate_daily_newspaper(
            self.current_date, self.day, self.stocks_market, self.crypto_market, self.sport_history, self.fixtures, lang=self.lang
        )

        self.paimon = PaimonPhone(base_dir)
        self.app_cursor[11] = 0
        self.app_subpage[11] = 0
        self._write_hud_dat(force=True)

    def _is_vi(self) -> bool:
        return self.lang == "vi"

    def _t(self, en_str: str, vi_str: str) -> str:
        return vi_str if self.lang == "vi" else en_str

    def _get_home_apps(self) -> list:
        return HOME_APPS_VI if self._is_vi() else HOME_APPS_EN

    def _get_unstuck_modes(self) -> list:
        return UNSTUCK_MODES_VI if self._is_vi() else UNSTUCK_MODES_EN

    def _get_trade_modes(self) -> list:
        return TRADE_MODES_VI if self._is_vi() else TRADE_MODES_EN

    def _get_sport_picks(self) -> list:
        return SPORT_PICKS_VI if self._is_vi() else SPORT_PICKS_EN

    def _get_lotto_subpages(self) -> list:
        return LOTTO_SUBPAGES_VI if self._is_vi() else LOTTO_SUBPAGES_EN

    def _get_scratch_tiers(self) -> list:
        return SCRATCH_TIERS_VI if self._is_vi() else SCRATCH_TIERS_EN

    def _get_xskt_modes(self) -> list:
        return XSKT_MODES_VI if self._is_vi() else XSKT_MODES_EN

    def _get_vietlott_modes(self) -> list:
        return VIETLOTT_MODES_VI if self._is_vi() else VIETLOTT_MODES_EN

    def _get_keno_modes(self) -> list:
        return KENO_MODES_VI if self._is_vi() else KENO_MODES_EN

    def _get_lotto_modes(self) -> list:
        return LOTTO_MODES_VI if self._is_vi() else LOTTO_MODES_EN

    def _get_bug_categories(self) -> list:
        return get_bug_categories(self.lang)

    def _get_ggmap_categories(self) -> list:
        return get_gg_map_categories(self.lang)

    def _set_language(self, lang: str):
        new_lang = "vi" if str(lang).strip().lower().startswith("vi") else "en"
        self.lang = new_lang
        is_vi = (new_lang == "vi")

        # Refresh asset names & stories in Stocks & Crypto markets
        for cfg in STOCK_AND_COMMODITY_ASSETS:
            sym = cfg["symbol"]
            if sym in self.stocks_market:
                self.stocks_market[sym]["name"] = cfg.get("name_vi", cfg["name"]) if is_vi else cfg["name"]
                self.stocks_market[sym]["story"] = cfg.get("story_vi", cfg["story"]) if is_vi else cfg["story"]
        for cfg in CRYPTO_ASSETS:
            sym = cfg["symbol"]
            if sym in self.crypto_market:
                self.crypto_market[sym]["name"] = cfg.get("name_vi", cfg["name"]) if is_vi else cfg["name"]
                self.crypto_market[sym]["story"] = cfg.get("story_vi", cfg["story"]) if is_vi else cfg["story"]

        # Refresh fixture labels & headlines while keeping active bets
        for m in self.fixtures:
            m["round_label"] = m.get("round_label_vi", m["round_label"]) if is_vi else m.get("round_label_en", m["round_label"])
            m["headline"] = m.get("headline_vi", m["headline"]) if is_vi else m.get("headline_en", m["headline"])

        # Refresh newspaper for the active language
        self.newspaper = generate_daily_newspaper(
            self.current_date, self.day, self.stocks_market, self.crypto_market, self.sport_history, self.fixtures, lang=self.lang
        )

        # Refresh active GPS waypoint if set
        if self.active_gps_target:
            poi_id = self.active_gps_target.get("id", "")
            matched = next((p for p in CURATED_GG_MAP_POIS if p["id"] == poi_id), None)
            if matched:
                loc_p = localize_poi_item(matched, self.lang)
                self.active_gps_target["name"] = loc_p["name"]
                self.active_gps_target["name_ascii"] = to_clean_viet_ascii(loc_p["name"])
                self.active_gps_target["note"] = loc_p["desc"]
            px, py, _ = self.player_pos
            tx, ty = self.active_gps_target["x"], self.active_gps_target["y"]
            compass = compute_compass_dir(tx - px, ty - py, lang=self.lang)
            self.active_gps_target["compass"] = compass
            self.active_gps_target["bearing"] = compass

        if is_vi:
            self.last_toast = "🌐 Da chuyen ngon ngu sang TIENG VIET (VI)!"
            self.push_event_banner(
                "NGON NGU HE THONG: TIENG VIET (VI)",
                "Toan bo EaglePhone OS v5.0, Bao EagleTimes & GG Map da hien thi Tieng Viet!",
                kind="info",
                duration=5.0,
            )
        else:
            self.last_toast = "🌐 Language switched to ENGLISH (EN)!"
            self.push_event_banner(
                "SYSTEM LANGUAGE: ENGLISH (EN)",
                "EaglePhone OS v5.0, EagleTimes Chronicle & GG Map are now in English!",
                kind="info",
                duration=5.0,
            )

    def _toggle_language(self):
        self._set_language("en" if self._is_vi() else "vi")

    set_language = _set_language
    toggle_language = _toggle_language

    def push_event_banner(self, title: str, sub: str, kind: str = "info", duration: float = 6.5):
        """Triggers a floating Top-Center Notification Banner in GTA SA for important events."""
        self.event_banner = {
            "title": to_clean_viet_ascii(title)[:68],
            "sub": to_clean_viet_ascii(sub)[:82],
            "kind": kind,
            "until": time.time() + duration,
        }

    def _init_markets(self):
        for cfg in STOCK_AND_COMMODITY_ASSETS:
            self.stocks_market[cfg["symbol"]] = self._build_asset_dict(cfg, "stocks")
        for cfg in CRYPTO_ASSETS:
            self.crypto_market[cfg["symbol"]] = self._build_asset_dict(cfg, "crypto")

    def _build_asset_dict(self, cfg: dict, group: str) -> dict:
        base_p = get_chronological_target_price(cfg, self.current_date)
        dec = cfg["decimals"]
        vol = cfg["volatility"]
        candles = []
        p = base_p
        for _ in range(48):
            o = p
            c = max(base_p * 0.2, o * (1.0 + random.gauss(0.0, vol * 0.35)))
            h = max(o, c) * (1.0 + abs(random.gauss(0, vol * 0.25)))
            l = min(o, c) * (1.0 - abs(random.gauss(0, vol * 0.25)))
            candles.append({"o": round(o, dec), "h": round(h, dec), "l": round(l, dec), "c": round(c, dec)})
            p = c
        is_vi = getattr(self, "lang", "en") == "vi"
        return {
            **cfg,
            "name": cfg.get("name_vi", cfg["name"]) if is_vi else cfg["name"],
            "story": cfg.get("story_vi", cfg["story"]) if is_vi else cfg["story"],
            "market_group": group,
            "price": round(p, dec),
            "delta_pct": round(((p - candles[0]["o"]) / candles[0]["o"]) * 100.0, 2),
            "candles": candles,
            "spot_qty": 0.0,
            "spot_cost": 0.0,
            "spot_val": 0.0,
            "spot_pnl": 0.0,
            "spot_pnl_pct": 0.0,
        }

    def _init_standings(self):
        for lg in LEAGUES:
            lid = lg["id"]
            rows = []
            for t_name, _ in LEAGUE_TEAMS[lid]:
                rows.append({"team": t_name, "p": 0, "w": 0, "d": 0, "l": 0, "gd": 0, "pts": 0})
            self.standings[lid] = rows

    def _get_active_league_fixtures(self):
        lg_id = LEAGUES[self.selected_league_idx % len(LEAGUES)]["id"]
        return [m for m in self.fixtures if m["league_id"] == lg_id]

    # ========================================================================
    # CASH & HEALTH SYNC + IN-GAME RESTAURANT DETECTION
    # ========================================================================
    def modify_cash(self, delta: int) -> bool:
        delta = int(delta)
        if delta < 0 and self.cash + delta < 0:
            return False
        if self.bridge.add_money(delta):
            self.cash = max(0, self.cash + delta)
            self.last_live_cash = self.cash
            self.ram_attached = True
        else:
            self.cash = max(0, self.cash + delta)
        return True

    def modify_health(self, delta: int, set_full: bool = False, allow_fatal: bool = False):
        self.ignore_next_hp_jump = True
        if self.bridge.add_health(delta, set_full=set_full, allow_fatal=allow_fatal):
            if set_full:
                self.health = max(150, self.max_health)
            else:
                min_hp = 0 if allow_fatal else 2
                self.health = min(max(150, self.max_health), max(min_hp, self.health + int(delta)))
            self.last_live_hp = self.health
            self.ram_attached = True
        else:
            if set_full:
                self.health = 150
            else:
                self.health = min(150, max(1, self.health + int(delta)))

    # ========================================================================
    # MAP BUG REPORTER, POSITION TRAIL (5-8s) & SAFE RECALL / UNSTUCK (Hạng mục 1)
    # ========================================================================
    def _sample_position_trail(self, live: dict = None):
        now = time.time()
        if live is None:
            live = self.bridge.read_live_player()
        if not live or not live.get("pos"):
            return
        px, py, pz = live["pos"]
        vx, vy, vz = live.get("vel") or (0.0, 0.0, 0.0)
        hdg = float(live.get("heading", 0.0))
        area = int(live.get("area_code", 0))
        game_area = int(live.get("game_area", 0))
        in_veh = bool(live.get("in_vehicle", False))

        self.player_pos = (round(px, 3), round(py, 3), round(pz, 3))
        self.player_heading = round(hdg, 1)
        self.player_velocity = (round(vx, 4), round(vy, 4), round(vz, 4))
        self.player_area_code = area
        self.player_game_area = game_area
        self.player_in_vehicle = in_veh

        if now - self.last_trail_sample_time < 0.24:
            return
        self.last_trail_sample_time = now

        # Consider position "safe ground" when vertical speed is mild and Z is not deep in the void
        is_safe = (abs(vz) < 0.16) and (pz > -35.0)
        sample = {
            "t": now,
            "x": round(px, 2),
            "y": round(py, 2),
            "z": round(pz, 2),
            "heading": round(hdg, 1),
            "vz": round(vz, 3),
            "area": area,
            "in_veh": in_veh,
            "is_safe": is_safe,
        }
        self.position_trail.append(sample)
        if len(self.position_trail) > 36:  # ~9 seconds at 4Hz
            self.position_trail.pop(0)

        if is_safe:
            # Only append to safe_ground_history if moved >= 0.8m or >= 0.8s elapsed
            if (
                not self.safe_ground_history
                or (now - self.safe_ground_history[-1]["t"] >= 0.75)
                or math.hypot(px - self.safe_ground_history[-1]["x"], py - self.safe_ground_history[-1]["y"]) >= 0.8
            ):
                self.safe_ground_history.append(sample)
                if len(self.safe_ground_history) > 32:
                    self.safe_ground_history.pop(0)

    def _get_trail_5s_snapshots(self) -> list:
        now = time.time()
        px, py, pz = self.player_pos
        vx, vy, vz = self.player_velocity
        if not self.position_trail:
            return [
                {
                    "offset_sec": 0.0,
                    "ago_sec": 0.0,
                    "x": round(px, 2),
                    "y": round(py, 2),
                    "z": round(pz, 2),
                    "vz": round(vz, 3),
                    "area": self.player_area_code,
                    "is_safe": True,
                }
            ]
        targets = [-5.0, -3.0, -2.0, -1.0]
        snaps = []
        for off in targets:
            target_t = now + off
            best = min(self.position_trail, key=lambda s: abs(s["t"] - target_t))
            snaps.append({
                "offset_sec": off,
                "ago_sec": abs(off),
                "x": best["x"],
                "y": best["y"],
                "z": best["z"],
                "vz": best.get("vz", 0.0),
                "area": best.get("area", self.player_area_code),
                "is_safe": best.get("is_safe", True),
            })
        snaps.append({
            "offset_sec": 0.0,
            "ago_sec": 0.0,
            "x": round(px, 2),
            "y": round(py, 2),
            "z": round(pz, 2),
            "vz": round(vz, 3),
            "area": self.player_area_code,
            "is_safe": (abs(vz) < 0.16 and pz > -35.0),
        })
        return snaps

    def _normalize_inspection(self, raw: dict) -> dict:
        if not raw:
            return {}
        suspects = []
        for o in raw.get("nearby_objects", []):
            col = o.get("col") or {}
            col_rad = float(col.get("rad", 0.0))
            dist_3d = float(o.get("dist_3d", 0.0))
            surf_dist = round(max(0.0, dist_3d - col_rad), 2) if col_rad > 0 else round(dist_3d, 2)
            dff_imgs = o.get("dff_archives") or []
            col_src = f"{col.get('img', '')}::{col.get('col_file', '')}".strip(":") if col else "MISSING_COL"
            flags = list(o.get("suspects") or ["OK_COL"])
            suspects.append({
                "model_id": o.get("model_id", 0),
                "dff_name": o.get("model_name", "unknown"),
                "txd_name": o.get("txd_name", "unknown"),
                "surface_dist": surf_dist,
                "center_dist": round(dist_3d, 2),
                "ipl_source": o.get("ipl_source", "unknown"),
                "ide_source": o.get("ide_source", "unknown"),
                "dff_img": dff_imgs[0] if dff_imgs else "MISSING_DFF",
                "col_source": col_src,
                "col_version": col.get("ver", "NONE"),
                "col_radius": col_rad,
                "col_boxes": int(col.get("boxes", 0)),
                "col_faces": int(col.get("faces", 0)),
                "issue_flags": flags,
            })

        top_s = suspects[0] if suspects else None
        telem = raw.get("telemetry") or {}
        pos_list = telem.get("pos") or raw.get("inspect_ref_pos") or list(self.player_pos)
        coords = {
            "x": round(float(pos_list[0]), 2),
            "y": round(float(pos_list[1]), 2),
            "z": round(float(pos_list[2]), 2),
        }
        bug_id = raw.get("bug_id") or raw.get("id") or "SCAN"
        cat_lbl = raw.get("category_label") or BUG_CATEGORIES[self.bug_cat_idx % len(BUG_CATEGORIES)][1]
        zone_lbl = raw.get("zone") or self.map_inspector.lookup_zone(coords["x"], coords["y"], coords["z"], lang=self.lang)
        safe_pos = raw.get("safe_recall_pos") or raw.get("pre_fall_edge") or {"x": coords["x"], "y": coords["y"], "z": coords["z"]}
        top_str = (
            f"{top_s['dff_name']}.dff (ID {top_s['model_id']}) in {top_s['ipl_source']} [COL: {top_s['col_source']} ({top_s['col_faces']}F/{top_s['col_boxes']}B)]"
            if top_s
            else "No IPL object within 15m"
        )
        discord_snippet = (
            f"[{bug_id}] {cat_lbl} @ {zone_lbl}\n"
            f"- Coords: X={coords['x']:.2f}, Y={coords['y']:.2f}, Z={coords['z']:.2f} (Int={telem.get('ped_area_code', self.player_area_code)})\n"
            f"- Safe Recall (-3s): X={safe_pos.get('x', coords['x']):.2f}, Y={safe_pos.get('y', coords['y']):.2f}, Z={safe_pos.get('z', coords['z']):.2f}\n"
            f"- Primary Suspect: {top_str}\n"
            f"- Diagnosis: {raw.get('agent_fix_hint', '')}"
        )
        return {
            **raw,
            "id": bug_id,
            "zone_label": zone_lbl,
            "coords": coords,
            "pre_fall_safe_pos": safe_pos,
            "suspects": suspects,
            "primary_suspect": top_s,
            "diagnosis_lines": [raw.get("agent_fix_hint", ""), raw.get("primary_summary", "")],
            "discord_snippet": discord_snippet,
        }

    def _get_safe_recall_target(self, mode_key: str = "recall_3s") -> dict:
        now = time.time()
        px, py, pz = self.player_pos
        hdg = self.player_heading
        area = self.player_area_code

        # Pick a safe point ~3s ago (or >= 3.5m away from the hole edge)
        safe_pt = None
        if self.safe_ground_history:
            candidates = [
                s for s in reversed(self.safe_ground_history)
                if (now - s["t"]) >= 2.5 or math.hypot(s["x"] - px, s["y"] - py) >= 3.5
            ]
            safe_pt = candidates[0] if candidates else self.safe_ground_history[0]

        if mode_key == "step_back_5m":
            rad = math.radians(hdg)
            # GTA SA forward vector is (-sin(hdg), cos(hdg)), so backward 5m is (+5*sin(hdg), -5*cos(hdg))
            tx = round(px + 5.0 * math.sin(rad), 2)
            ty = round(py - 5.0 * math.cos(rad), 2)
            base_z = max(pz, safe_pt["z"] if safe_pt else pz)
            tz = round(base_z + 1.0, 2)
            return {
                "x": tx,
                "y": ty,
                "z": tz,
                "area_code": area,
                "mode": mode_key,
                "label": self._t("Step Back 5m Unstuck", "Lui 5m Thoat Ket"),
            }

        if mode_key == "lift_surface":
            tx = round(safe_pt["x"] if (safe_pt and pz < -5.0) else px, 2)
            ty = round(safe_pt["y"] if (safe_pt and pz < -5.0) else py, 2)
            base_z = max(pz + 4.5, (safe_pt["z"] + 2.5) if safe_pt else (pz + 4.5))
            if pz < 0.0 and base_z < 12.0:
                base_z = 15.0
            tz = round(base_z, 2)
            return {
                "x": tx,
                "y": ty,
                "z": tz,
                "area_code": area,
                "mode": mode_key,
                "label": self._t("Lift to Surface (+4.5m)", "Nang Len Mat Dat (+4.5m)"),
            }

        # Default: recall_3s (Safe Ground 3s before falling)
        if safe_pt:
            tx = round(safe_pt["x"], 2)
            ty = round(safe_pt["y"], 2)
            tz = round(safe_pt["z"] + 0.65, 2)
            t_area = int(safe_pt.get("area", area))
            return {
                "x": tx,
                "y": ty,
                "z": tz,
                "area_code": t_area,
                "mode": "recall_3s",
                "label": self._t("Safe Ground (-3s)", "Vi Tri An Toan (-3s)"),
            }

        rad = math.radians(hdg)
        return {
            "x": round(px + 4.0 * math.sin(rad), 2),
            "y": round(py - 4.0 * math.cos(rad), 2),
            "z": round(max(pz + 2.0, 14.0), 2),
            "area_code": area,
            "mode": "recall_3s",
            "label": self._t("Fallback Safe Spot", "Vi Tri An Toan Du Phong"),
        }

    def _perform_unstuck(self, mode_key: str = None, silent_banner: bool = False) -> dict:
        live = self.bridge.read_live_player()
        if live:
            self._sample_position_trail(live)
        modes = self._get_unstuck_modes()
        if not mode_key:
            mode_key = modes[self.unstuck_mode_idx % len(modes)][0]
        target = self._get_safe_recall_target(mode_key)
        tx, ty, tz = target["x"], target["y"], target["z"]
        t_area = target.get("area_code", self.player_area_code)

        tele_ok = False
        if self.bridge.try_attach():
            tele_ok = self.bridge.teleport_player(tx, ty, tz, area_code=t_area)

        self.player_pos = (tx, ty, tz)
        self.player_velocity = (0.0, 0.0, 0.0)
        status_tag = "RAM Teleport OK" if tele_ok else "Sim Target Ready"
        self.last_toast = self._t(
            f"🛟 QUICK RESCUE ({target['label']}): ({tx:.1f}, {ty:.1f}, {tz:.1f}) [{status_tag}]",
            f"🛟 CUU HO NHANH ({target['label']}): ({tx:.1f}, {ty:.1f}, {tz:.1f}) [{status_tag}]",
        )
        if not silent_banner:
            self.push_event_banner(
                self._t(
                    f"QUICK RESCUE (UNSTUCK): {target['label'].upper()}",
                    f"CUU HO NHANH (UNSTUCK): {target['label'].upper()}",
                ),
                self._t(
                    f"Returned Aether to ({tx:.1f}, {ty:.1f}, {tz:.1f}) & zeroed fall velocity!",
                    f"Da dua Aether ve ({tx:.1f}, {ty:.1f}, {tz:.1f}) & triet tieu van toc roi!",
                ),
                kind="win",
                duration=6.0,
            )
        return {"ok": tele_ok, "target": target}

    def _refresh_live_scan(self) -> dict:
        live = self.bridge.read_live_player()
        if live:
            self._sample_position_trail(live)
        px, py, pz = self.player_pos
        bug_cats = self._get_bug_categories()
        cat_code, cat_lbl = bug_cats[self.bug_cat_idx % len(bug_cats)]
        raw_scan = self.map_inspector.inspect_location(
            x=px,
            y=py,
            z=pz,
            heading=self.player_heading,
            area_code=self.player_area_code,
            game_area=self.player_game_area,
            in_vehicle=self.player_in_vehicle,
            velocity=self.player_velocity,
            trail=self._get_trail_5s_snapshots(),
            category_code=cat_code,
            category_label=cat_lbl,
            radius=15.0,
        )
        scan = self._normalize_inspection(raw_scan)
        self.last_live_scan = scan
        top = scan.get("primary_suspect")
        if top:
            self.last_toast = self._t(
                f"🔍 15m Scan: {top['dff_name']}.dff (ID {top['model_id']}, {top['surface_dist']}m away) "
                f"| COL: {top['col_source']} ({top['col_faces']} faces)",
                f"🔍 Quet 15m: {top['dff_name']}.dff (ID {top['model_id']}, cach {top['surface_dist']}m) "
                f"| COL: {top['col_source']} ({top['col_faces']} faces)",
            )
        else:
            self.last_toast = self._t(
                f"🔍 15m Scan at ({px:.1f}, {py:.1f}, {pz:.1f}): No nearby IPL object!",
                f"🔍 Quet 15m tai ({px:.1f}, {py:.1f}, {pz:.1f}): Khong co object IPL!",
            )
        return scan

    def trigger_bug_report(
        self, category_code: str = None, note: str = "", auto_rescue_if_falling: bool = True
    ) -> dict:
        live = self.bridge.read_live_player()
        if live:
            self._sample_position_trail(live)
        bug_cats = self._get_bug_categories()
        if not category_code:
            category_code, category_label = bug_cats[self.bug_cat_idx % len(bug_cats)]
        else:
            category_label = next(
                (lbl for c, lbl in bug_cats if c == category_code),
                bug_cats[0][1],
            )

        px, py, pz = self.player_pos
        vx, vy, vz = self.player_velocity
        trail_5s = self._get_trail_5s_snapshots()
        pre_fall = self._get_safe_recall_target("recall_3s")

        raw_report = self.map_inspector.record_bug_report(
            x=px,
            y=py,
            z=pz,
            heading=self.player_heading,
            area_code=self.player_area_code,
            game_area=self.player_game_area,
            in_vehicle=self.player_in_vehicle,
            velocity=self.player_velocity,
            trail=trail_5s,
            safe_recall_pos=pre_fall,
            category_code=category_code,
            category_label=category_label,
            note=note,
        )
        report = self._normalize_inspection(raw_report)
        try:
            snap = self.debug_sys.ingame_tester.capture_forensic_snapshot(
                self, tag=report.get("id", "BUG"), note=note, base_bug_report=report
            )
            report["forensic_snapshot"] = {
                "snapshot_id": snap.get("snapshot_id"),
                "screenshot": snap.get("screenshot"),
                "crosshair_target": snap.get("crosshair_target"),
                "nearby_dynamic_entities": snap.get("nearby_dynamic_entities"),
            }
            ch = snap.get("crosshair_target")
            if ch:
                report["discord_snippet"] = (
                    report.get("discord_snippet", "")
                    + f"\n- Camera Look-At X-Ray: {ch['dff_name']}.dff (ID {ch['model_id']}, TXD {ch['txd_name']}) @ {ch['dist_m']}m [RAM: DFF={ch.get('ram_dff_loaded')} TXD={ch.get('ram_txd_loaded')} COL={ch.get('ram_col_triangles',0)}F]"
                )
        except Exception as e:
            self.debug_sys.logger.log_exception("EagleCompanion", "trigger_bug_report.forensic", e)
        self.last_bug_report = report
        self.last_live_scan = report

        rescued_msg = ""
        if auto_rescue_if_falling and (vz < -0.20 or pz < -3.0):
            res = self._perform_unstuck("recall_3s", silent_banner=True)
            t_pos = res["target"]
            rescued_msg = self._t(
                f" + Auto-Rescued to ({t_pos['x']:.1f}, {t_pos['y']:.1f}, {t_pos['z']:.1f})!",
                f" + Da Cuu Ho ve ({t_pos['x']:.1f}, {t_pos['y']:.1f}, {t_pos['z']:.1f})!",
            )

        top = report.get("primary_suspect")
        if top:
            sub_msg = (
                f"Suspect: {top['dff_name']}.dff (ID {top['model_id']}) | IPL: {Path(top['ipl_source']).name} "
                f"| COL: {top['col_source']} ({top['col_faces']} faces){rescued_msg}"
            )
        else:
            sub_msg = self._t(
                f"Coords ({px:.1f}, {py:.1f}, {pz:.1f}) • Zone: {report.get('zone_label', 'N/A')}{rescued_msg}",
                f"Toa do ({px:.1f}, {py:.1f}, {pz:.1f}) • Zone: {report.get('zone_label', 'N/A')}{rescued_msg}",
            )

        self.last_toast = self._t(
            f"🐛 Saved #{report['id']} [{report['category_label']}]: {sub_msg}",
            f"🐛 Da luu #{report['id']} [{report['category_label']}]: {sub_msg}",
        )
        self.push_event_banner(
            self._t(
                f"BUG REPORT SAVED #{report['id']} • {report['category_label'].upper()}",
                f"DA LUU BAO BUG #{report['id']} • {report['category_label'].upper()}",
            ),
            sub_msg,
            kind="warn" if not rescued_msg else "win",
            duration=7.5,
        )
        return report

    def _get_active_ggmap_pois(self) -> list[dict]:
        gg_cats = self._get_ggmap_categories()
        cat_code = gg_cats[self.ggmap_cat_idx % len(gg_cats)][0]
        pois = get_pois_for_category(cat_code, self.player_pos, lang=self.lang)
        if not pois:
            return []
        for p in pois:
            p["note"] = p.get("desc", p.get("note", ""))
            p["bearing"] = p.get("compass", "N")
            p["is_gps_target"] = bool(self.active_gps_target and self.active_gps_target.get("id") == p["id"])
        if self.ggmap_selected_id:
            for idx_p, p in enumerate(pois):
                if p["id"] == self.ggmap_selected_id:
                    self.ggmap_poi_idx = idx_p
                    break
        self.ggmap_poi_idx = self.ggmap_poi_idx % len(pois)
        self.ggmap_selected_id = pois[self.ggmap_poi_idx]["id"]
        return pois

    def _set_gps_waypoint_to_poi(self, poi: dict) -> dict:
        tx, ty, tz = float(poi["x"]), float(poi["y"]), float(poi["z"])
        handle = self.bridge.set_target_waypoint(tx, ty, tz)
        px, py, _ = self.player_pos
        dist_2d = math.hypot(px - tx, py - ty)
        compass = compute_compass_dir(tx - px, ty - py, lang=self.lang)
        dist_str = format_distance(dist_2d)
        disp_name = poi.get("name_vi", poi.get("name", "Diem Den GPS")) if self._is_vi() else poi.get("name", "GPS Destination")
        self.active_gps_target = {
            "id": poi.get("id", "CUSTOM"),
            "name": disp_name,
            "name_ascii": to_clean_viet_ascii(disp_name),
            "region": poi.get("region", "San Andreas"),
            "cat": poi.get("cat", "LANDMARKS"),
            "x": round(tx, 2),
            "y": round(ty, 2),
            "z": round(tz, 2),
            "area_code": int(poi.get("area_code", 0)),
            "note": poi.get("desc", poi.get("note", "")),
            "handle": int(handle),
            "dist_2d": round(dist_2d, 1),
            "dist_m": round(dist_2d, 1),
            "dist_str": dist_str,
            "compass": compass,
            "bearing": compass,
            "set_at": time.time(),
        }
        ram_tag = f"Blip 0x{handle:08X}" if handle else "Sim GPS"
        self.last_toast = self._t(
            f"📍 GPS Waypoint set: {disp_name} ({poi['region']}) • {dist_str} [{compass}] ({ram_tag})",
            f"📍 Da cam moc GPS: {disp_name} ({poi['region']}) • Cach {dist_str} [{compass}] ({ram_tag})",
        )
        self.push_event_banner(
            self._t(
                f"GPS NAVIGATION: {to_clean_viet_ascii(disp_name).upper()[:28]}",
                f"CHI DUONG GPS: {to_clean_viet_ascii(disp_name).upper()[:28]}",
            ),
            self._t(
                f"Region: {poi['region']} • Distance: {dist_str} ({compass}) • Coords: ({tx:.0f}, {ty:.0f})",
                f"Khu vuc: {poi['region']} • Cach: {dist_str} ({compass}) • Toa do: ({tx:.0f}, {ty:.0f})",
            ),
            kind="win",
            duration=6.5,
        )
        return self.active_gps_target

    def _clear_gps_waypoint(self, arrived: bool = False):
        self.bridge.clear_target_waypoint()
        old_name = self.active_gps_target["name"] if self.active_gps_target else self._t("Target Blip (T)", "Moc Toa Do (T)")
        self.active_gps_target = None
        if arrived:
            self.last_toast = self._t(
                f"🏁 Arrived at GPS destination: {old_name}! Route automatically cleared.",
                f"🏁 Da den diem hen GPS: {old_name}! Da tu dong tat chi duong.",
            )
            self.push_event_banner(
                self._t(
                    f"ARRIVED AT GPS: {to_clean_viet_ascii(old_name).upper()[:26]}",
                    f"DA DEN DIEM HEN GPS: {to_clean_viet_ascii(old_name).upper()[:26]}",
                ),
                self._t(
                    "You have reached your destination (< 25m) • Target waypoint automatically cleared!",
                    "Ban da toi gan diem dich (< 25m) • He thong da tu dong xoa moc chi duong!",
                ),
                kind="win",
                duration=7.0,
            )
        else:
            self.last_toast = self._t(
                f"❌ Cleared GPS route ({old_name}) & removed red radar blip!",
                f"❌ Da huy chi duong GPS ({old_name}) & xoa moc do tren Radar!",
            )
            self.push_event_banner(
                self._t("GPS ROUTE CLEARED (REMOVED BLIP T)", "DA HUY CHI DUONG GPS (XOA MOC T)"),
                self._t(
                    f"Removed GPS target waypoint to {to_clean_viet_ascii(old_name)} on Radar!",
                    f"Da xoa moc chi duong toi {to_clean_viet_ascii(old_name)} tren ban do Radar!",
                ),
                kind="info",
                duration=5.0,
            )

    def _check_gps_arrival_and_sync(self):
        # Always ensure PECore on-foot GPS patch and unsigned streaming patches are active in RAM
        if self.bridge.handle:
            self.bridge._ensure_pecore_onfoot_gps_patch()
            self.bridge._ensure_streaming_unsigned_patch()
        # Never interfere with 0x00BA6774 while the user is in the Pause Map (menu_active != 0)!
        menu_active = self.bridge.read_u8(0x00BA677B)
        in_pause_menu = (menu_active is not None and menu_active != 0)
        live_wp = None if in_pause_menu else self.bridge.read_target_waypoint()
        if not self.active_gps_target:
            if live_wp is not None:
                wx, wy, wz = live_wp["x"], live_wp["y"], live_wp["z"]
                px, py, _ = self.player_pos
                w_dist = math.hypot(px - wx, py - wy)
                w_comp = compute_compass_dir(wx - px, wy - py, lang=self.lang)
                self.active_gps_target = {
                    "id": "MAP_T",
                    "name": self._t("Pause Map Waypoint (T)", "Moc Ban Do Pause Map (T)"),
                    "name_ascii": self._t("Pause Map Waypoint (T)", "Moc Ban Do Pause Map (T)"),
                    "region": "Map (T)",
                    "cat": "CUSTOM",
                    "x": round(wx, 2),
                    "y": round(wy, 2),
                    "z": round(wz, 2),
                    "area_code": 0,
                    "note": "Set via Pause Map (T)",
                    "handle": int(live_wp["handle"]),
                    "dist_2d": round(w_dist, 1),
                    "dist_m": round(w_dist, 1),
                    "dist_str": format_distance(w_dist),
                    "compass": w_comp,
                    "bearing": w_comp,
                    "set_at": time.time(),
                }
            return
        px, py, _ = self.player_pos
        tx, ty = self.active_gps_target["x"], self.active_gps_target["y"]
        tz = self.active_gps_target.get("z", 0.0)
        dist_2d = math.hypot(px - tx, py - ty)
        compass = compute_compass_dir(tx - px, ty - py, lang=self.lang)
        self.active_gps_target["dist_2d"] = round(dist_2d, 1)
        self.active_gps_target["dist_m"] = round(dist_2d, 1)
        self.active_gps_target["dist_str"] = format_distance(dist_2d)
        self.active_gps_target["compass"] = compass
        self.active_gps_target["bearing"] = compass
        if dist_2d <= 35.0 and (time.time() - self.active_gps_target.get("set_at", 0.0)) >= 1.5:
            self._clear_gps_waypoint(arrived=True)
            return
        if in_pause_menu:
            return
        # Only write to RAM if active_gps_target was created before the game attached (handle == 0).
        # Once handle != 0 has been written to RAM, respect Pause Map 'T' clears or new 'T' waypoints!
        if self.active_gps_target.get("handle", 0) == 0:
            if dist_2d > 45.0 and live_wp is None:
                new_h = self.bridge.set_target_waypoint(tx, ty, tz)
                if new_h:
                    self.active_gps_target["handle"] = int(new_h)
        else:
            if live_wp is None:
                self.active_gps_target = None
            elif math.hypot(live_wp["x"] - tx, live_wp["y"] - ty) > 5.0:
                wx, wy, wz = live_wp["x"], live_wp["y"], live_wp["z"]
                w_dist = math.hypot(px - wx, py - wy)
                w_comp = compute_compass_dir(wx - px, wy - py, lang=self.lang)
                self.active_gps_target = {
                    "id": "MAP_T",
                    "name": self._t("Pause Map Waypoint (T)", "Moc Ban Do Pause Map (T)"),
                    "name_ascii": self._t("Pause Map Waypoint (T)", "Moc Ban Do Pause Map (T)"),
                    "region": "Map (T)",
                    "cat": "CUSTOM",
                    "x": round(wx, 2),
                    "y": round(wy, 2),
                    "z": round(wz, 2),
                    "area_code": 0,
                    "note": "Set via Pause Map (T)",
                    "handle": int(live_wp["handle"]),
                    "dist_2d": round(w_dist, 1),
                    "dist_m": round(w_dist, 1),
                    "dist_str": format_distance(w_dist),
                    "compass": w_comp,
                    "bearing": w_comp,
                    "set_at": time.time(),
                }

    # ========================================================================
    # IN-GAME NAVIGATION, HOME GRID + GG MAP DOCK, SUB-PAGES & KEYPAD (v5.0)
    # ========================================================================
    def _open_app(self, app_id: int):
        home_apps = self._get_home_apps()
        app_id = max(0, min(len(home_apps), int(app_id)))
        self.phone_app = app_id
        self.keypad_active = False
        if app_id > 0:
            self.home_cursor_idx = app_id - 1
            if self.home_cursor_idx < 9:
                self.last_home_col = self.home_cursor_idx % 3
            _, _, short_lbl, desc_lbl = home_apps[app_id - 1]
            self.last_toast = self._t(
                f"Opened App {app_id}. {short_lbl}: {desc_lbl} (Backspace/F8: Back)",
                f"Mo App {app_id}. {short_lbl}: {desc_lbl} (Backspace/F8: Quay Lai)",
            )
            if app_id == 8 and self.last_live_scan is None:
                self._refresh_live_scan()
            elif app_id == 10:
                pois = self._get_active_ggmap_pois()
                gg_cats = self._get_ggmap_categories()
                cat_lbl = gg_cats[self.ggmap_cat_idx % len(gg_cats)][1]
                self.last_toast = self._t(
                    f"GG Map [{cat_lbl}]: {len(pois)} POIs (J/L Tab, I/K Select, PgUp/PgDn Fast Scroll, F9 Set GPS)",
                    f"GG Map [{cat_lbl}]: {len(pois)} diem den (J/L Doi Tab, I/K Chon, PgUp/PgDn Cuon Nhanh, F9 Cam Moc GPS)",
                )
        else:
            self.last_toast = self._t(
                "EaglePhone v5.0 Home Screen (I/K/J/L Select App 1..11, F9 Open)",
                "Man Hinh Chinh EaglePhone v5.0 (I/K/J/L Chon Icon 1..10, F9 Mo App)",
            )

    def _navigate_back(self, from_f8: bool = False):
        self.phone_open = 1
        self.keypad_active = False
        app = self.phone_app
        home_apps = self._get_home_apps()
        if app == 0:
            if from_f8:
                self._open_app(self.home_cursor_idx + 1)
            else:
                self.last_toast = self._t(
                    "EaglePhone v5.0 Home Screen (I/K/J/L Select App 1..11, F9 Open)",
                    "Man Hinh Chinh EaglePhone v5.0 (I/K/J/L Chon Icon 1..10, F9 Mo App)",
                )
            return

        # If inside detail Sub-page 1 of App 2, 3, or 4 -> return to Sub-page 0 (Table View)
        if app in (2, 3, 4) and self.app_subpage.get(app, 0) > 0:
            self.app_subpage[app] = 0
            self.last_toast = self._t(
                "Returned to Market / Match Table (Press Backspace/F8 again for Home Screen)",
                "Quay lai Bang Gia / Bang Keo (Bam Backspace/F8 lan nua ve Man Hinh Chinh)",
            )
            return

        # Otherwise return from App 1..11 to Home Screen (app = 0)
        self.home_cursor_idx = max(0, min(len(home_apps) - 1, app - 1))
        if self.home_cursor_idx < 9:
            self.last_home_col = self.home_cursor_idx % 3
        self.phone_app = 0
        self.last_toast = self._t(
            "EaglePhone v5.0 Home Screen (I/K/J/L Select App 1..11, F9 Open)",
            "Man Hinh Chinh EaglePhone v5.0 (I/K/J/L Chon Icon 1..10, F9 Mo App)",
        )

    def poll_ingame_hotkeys(self):
        """
        Polls in-game controls at 40Hz via Win32 GetAsyncKeyState ONLY when gta_pe.exe is active and unpaused:
        - F7 (0x76): Show / Hide Smartphone (All apps 1..10 including GG Map are accessed inside F7!)
        - When Smartphone is OPEN (self.phone_open == 1):
          - I / K / J / L (0x49, 0x4B, 0x4A, 0x4C): 4-way navigation on Home Screen 10-App Grid & inside Apps
          - F9 (0x78): Open selected App / Confirm action (OK / Set GPS Waypoint)
          - F10 (0x79): Secondary Quick Action inside App (e.g., Clear GPS Waypoint in GG Map)
          - Backspace (0x08) / F8 (0x77): Go Back (Sub-page -> App Table -> Home Screen 0)
          - F6 (0x75): Toggle Direct Keypad Input Mode (0-9 only captured while keypad_active == True)
        - Ctrl+F11 (0x11 + 0x7A): Instant Map Bug Report + Auto-Inspector (.ipl/.ide/.img/.col) + Auto-Rescue if falling
        - F12 (0x7B): Instant Safe Recall / Unstuck (Quick Rescue to safe ground 3s ago)
        """
        if not self.bridge.try_attach():
            return

        # Sample position trail at 4Hz (every 0.25s) for 5-8s trail, Safe Ground Recall & Live GPS Distance
        if time.time() - self.last_trail_sample_time >= 0.24:
            with self.lock:
                self._sample_position_trail()
                self._check_gps_arrival_and_sync()
                if self.phone_open and (self.phone_app in (8, 10) or self.active_gps_target is not None):
                    self._write_hud_dat()

        # Never process hotkeys when in GTA SA Main Menu / Pause Map or when Alt-Tabbed out of the game!
        if not self.bridge.is_game_active_and_unpaused():
            self.bridge.clear_hotkey_states()
            return

        # GLOBAL HOTKEY Ctrl + F11 (0x11 + 0x7A): Instant Bug Report + Auto-Inspector
        # Ctrl + Shift + F11 (0x11 + 0x10 + 0x7A): Toggle On-Demand DEEP DEBUG Mode vs LITE (0% Overhead) Mode!
        # Pressing F11 alone without Ctrl shows a reminder toast to prevent accidental reports!
        if self.bridge.poll_hotkey_edge(0x7A):
            with self.lock:
                ctrl_down = self.bridge.is_key_down(0x11) or self.bridge.is_key_down(0xA2) or self.bridge.is_key_down(0xA3)
                shift_down = self.bridge.is_key_down(0x10) or self.bridge.is_key_down(0xA0) or self.bridge.is_key_down(0xA1)
                if ctrl_down and shift_down:
                    new_m = self.debug_sys.toggle_mode(engine=self)
                    if new_m == "deep":
                        self.last_toast = self._t(
                            "🔬 DEEP DEBUG ENABLED: Live Pools, Streaming RAM, Thrashing & FPS Profiler active!",
                            "🔬 DA BAT DEEP DEBUG: Dang do trực tiếp Pool RAM, Streaming, Thrashing & FPS!",
                        )
                        self.push_event_banner(
                            self._t("ON-DEMAND DEEP DEBUGGER: ENABLED", "DA BAT CHE DO DEBUG CHUYEN SAU"),
                            self._t(
                                "Live GTA SA Pools, CStreaming RAM & Thrashing Watchdog active (Ctrl+Shift+F11 to return to LITE)",
                                "Dang giam sat Pool RAM, Streaming & Thrashing (Bam Ctrl+Shift+F11 de ve LITE 0% Overhead)",
                            ),
                            kind="warn",
                            duration=5.5,
                        )
                    else:
                        self.last_toast = self._t(
                            "🛡️ Switched to LITE Mode (0% Game Overhead — Only Bug Report & Crash Guard active)",
                            "🛡️ Da chuyen ve Che do LITE (0% Anh huong FPS — Chi bat Bao Bug & Bat Crash Ngam)",
                        )
                        self.push_event_banner(
                            self._t("DEBUGGER MODE: LITE (ZERO OVERHEAD)", "CHE DO DEBUG: LITE (0% OVERHEAD)"),
                            self._t(
                                "Deep RAM/Pool polling paused. Bug Reporter (Ctrl+F11) & Crash Guard remain active.",
                                "Da tat quet RAM chuyen sau. Chi giu Bao Bug (Ctrl+F11), Cuu Ho (F12) & Bat Crash.",
                            ),
                            kind="info",
                            duration=5.0,
                        )
                elif ctrl_down:
                    self.trigger_bug_report(auto_rescue_if_falling=True)
                else:
                    self.last_toast = self._t(
                        "Ctrl+F11: Log Bug | Ctrl+Shift+F11: Toggle Deep Debug | F12: Quick Rescue",
                        "Ctrl+F11: Bao Bug | Ctrl+Shift+F11: Bat/Tat Deep Debug | F12: Cuu Ho Nhanh",
                    )
                self._write_hud_dat(force=True)
            return

        # GLOBAL HOTKEY F12 (0x7B): Instant Unstuck / Safe Recall (or Abort Auto-Probe if active!)
        if self.bridge.poll_hotkey_edge(0x7B):
            with self.lock:
                if self.debug_sys.probe_active:
                    self.debug_sys.stop_auto_probe(self, reason="Aborted by user (F12)")
                else:
                    self._perform_unstuck()
                self._write_hud_dat(force=True)
            return

        # F7 (0x76): Toggle Smartphone Open/Close
        if self.bridge.poll_hotkey_edge(0x76):
            with self.lock:
                self.phone_open = 0 if self.phone_open == 1 else 1
                self.keypad_active = False
                if self.phone_open:
                    self.last_toast = self._t(
                        "Opened EaglePhone v5.0 (I/K/J/L Select App 1..11, F9 Open, Backspace/F8 Back)",
                        "Da mo EaglePhone v5.0 (I/K/J/L Chon App 1..11, F9 Mo, Backspace/F8 Quay Lai)",
                    )
                else:
                    self.last_toast = self._t(
                        "Phone minimized (Press F7 to open)",
                        "Da thu nho Dien Thoai (Bam F7 de mo)",
                    )
                self._write_hud_dat(force=True)
            return

        if not self.phone_open:
            return

        # F8 (0x77): Navigate Back (Sub-page -> App -> Home Screen 0)
        if self.bridge.poll_hotkey_edge(0x77):
            with self.lock:
                self._navigate_back(from_f8=True)
                self._write_hud_dat(force=True)
            return

        # If Direct Keypad Input Mode is ACTIVE (toggled by F6): capture digits 0-9, Backspace, F6, F9
        if self.keypad_active:
            changed = False
            for d in range(10):
                # Top-row 0-9 (0x30 + d) or Numpad 0-9 (0x60 + d)
                if self.bridge.poll_hotkey_edge(0x30 + d) or self.bridge.poll_hotkey_edge(0x60 + d):
                    with self.lock:
                        max_len = 6 if self.keypad_target == "lotto" else (14 if self.keypad_target == "vietlott" else 8)
                        if len(self.keypad_buffer) < max_len:
                            self.keypad_buffer += str(d)
                            changed = True
            # Backspace (0x08): Delete last digit
            if self.bridge.poll_hotkey_edge(0x08):
                with self.lock:
                    self.keypad_buffer = self.keypad_buffer[:-1]
                    changed = True
            # Delete (0x2E): Clear buffer
            if self.bridge.poll_hotkey_edge(0x2E):
                with self.lock:
                    self.keypad_buffer = ""
                    changed = True
            # Confirm typed number: F6 (0x75) or F9 (0x78) or Enter (0x0D)
            if (
                self.bridge.poll_hotkey_edge(0x75)
                or self.bridge.poll_hotkey_edge(0x78)
                or self.bridge.poll_hotkey_edge(0x0D)
            ):
                with self.lock:
                    self.keypad_active = False
                    if self.keypad_target == "lotto":
                        if len(self.keypad_buffer) > 0:
                            self.custom_lotto_str = self.keypad_buffer.zfill(6)[:6]
                        self.last_toast = self._t(
                            f"Set 6D Lotto number: [{self.custom_lotto_str}] (Press F9 to buy ticket)",
                            f"Da nhap day so XSKT/Lo De: [{self.custom_lotto_str}] (Bam F9 mua ve)",
                        )
                    elif self.keypad_target == "vietlott":
                        self.custom_vietlott_str = self._normalize_vietlott_picks(self.keypad_buffer)
                        self.last_toast = self._t(
                            f"Set Vietlott balls: [{self.custom_vietlott_str.replace(' ', '-')}] (Press F9 to buy)",
                            f"Da chon bo bong Vietlott: [{self.custom_vietlott_str.replace(' ', '-')}] (Bam F9 mua ve)",
                        )
                    else:
                        val = int(self.keypad_buffer) if self.keypad_buffer.isdigit() and int(self.keypad_buffer) > 0 else self.tx_amount
                        self.tx_amount = max(1, min(99999999, val))
                        self.last_toast = self._t(
                            f"Custom Transaction Amount set: ${self.tx_amount:,}!",
                            f"Da dat So Tien Tuy Chinh: ${self.tx_amount:,}!",
                        )
                    self._write_hud_dat(force=True)
                return

            if changed:
                with self.lock:
                    if self.keypad_target == "lotto":
                        lbl = self._t("6D Lotto Number", "6 So XSKT/Lo De")
                    elif self.keypad_target == "vietlott":
                        lbl = self._t("Vietlott Balls (e.g. 051219263844)", "Bo Bong Vietlott (VD: 051219263844)")
                    else:
                        lbl = self._t("Amount $", "So Tien $")
                    self.last_toast = self._t(
                        f"Typing {lbl}: [{self.keypad_buffer or '_'}] (0-9 Type, Backspace Del, F6/Enter Save)",
                        f"Dang go {lbl}: [{self.keypad_buffer or '_'}] (0-9 Go, Backspace Xoa, F6/Enter Luu)",
                    )
                    self._write_hud_dat(force=True)
            return

        # Backspace (0x08 when not typing): Navigate Back (Sub-page -> App -> Home Screen 0)
        if self.bridge.poll_hotkey_edge(0x08):
            with self.lock:
                self._navigate_back(from_f8=False)
                self._write_hud_dat(force=True)
            return

        # F6 (0x75): Open Direct Keypad Input Mode!
        if self.bridge.poll_hotkey_edge(0x75):
            with self.lock:
                self.keypad_active = True
                self.keypad_buffer = ""
                sub5 = self.app_subpage.get(5, 0)
                if self.phone_app == 5 and sub5 == 1:
                    self.keypad_target = "lotto"
                    self.last_toast = self._t(
                        "TYPE 6D LOTTO NUMBER: Press 0-9 on keyboard, F6/Enter to save!",
                        "GO 6 SO XSKT/LO DE: Bam phim 0-9 tren ban phim, F6/Enter de luu!",
                    )
                elif self.phone_app == 5 and sub5 == 2:
                    self.keypad_target = "vietlott"
                    self.last_toast = self._t(
                        "TYPE VIETLOTT BALLS (2 digits/ball, e.g. 051219263844), F6/Enter to save!",
                        "GO BO BONG VIETLOTT (2 chu so/bong, VD: 051219263844), F6/Enter de luu!",
                    )
                else:
                    self.keypad_target = "amount"
                    self.last_toast = self._t(
                        "TYPE AMOUNT ($): Press 0-9 on keyboard, F6/Enter to save!",
                        "CHE DO GO SO TIEN ($): Hay bam phim 0-9 tren ban phim, F6/Enter de luu!",
                    )
                self._write_hud_dat(force=True)
            return

        # Quick number keys 1..9 and 0 on Home Screen (app == 0)
        if self.phone_app == 0:
            for d in range(1, 10):
                if self.bridge.poll_hotkey_edge(0x30 + d):
                    with self.lock:
                        self._open_app(d)
                        self._write_hud_dat(force=True)
                    return
            if self.bridge.poll_hotkey_edge(0x30):
                with self.lock:
                    self._open_app(10)
                    self._write_hud_dat(force=True)
                return

        # Cursor UP: I (0x49) or Numpad 8 (0x68)
        if self.bridge.poll_hotkey_edge(0x49) or self.bridge.poll_hotkey_edge(0x68):
            self._move_cursor_vertical(-1)
            return

        # PageUp (0x21): Fast scroll -6 rows in GG Map (app == 10), -1 elsewhere
        if self.bridge.poll_hotkey_edge(0x21):
            self._move_cursor_vertical(-6 if self.phone_app == 10 else -1)
            return

        # Cursor DOWN: K (0x4B) or Numpad 2 (0x62)
        if self.bridge.poll_hotkey_edge(0x4B) or self.bridge.poll_hotkey_edge(0x62):
            self._move_cursor_vertical(+1)
            return

        # PageDown (0x22): Fast scroll +6 rows in GG Map (app == 10), +1 elsewhere
        if self.bridge.poll_hotkey_edge(0x22):
            self._move_cursor_vertical(+6 if self.phone_app == 10 else +1)
            return

        # Option LEFT: J (0x4A) or Numpad 4 (0x64)
        if self.bridge.poll_hotkey_edge(0x4A) or self.bridge.poll_hotkey_edge(0x64):
            self._adjust_active_row(-1)
            return

        # Option RIGHT: L (0x4C) or Numpad 6 (0x66)
        if self.bridge.poll_hotkey_edge(0x4C) or self.bridge.poll_hotkey_edge(0x66):
            self._adjust_active_row(+1)
            return

        # Execute / Confirm (OK): F9 (0x78) or Enter (0x0D) or U (0x55) or Numpad 5 (0x65)
        if (
            self.bridge.poll_hotkey_edge(0x78)
            or self.bridge.poll_hotkey_edge(0x0D)
            or self.bridge.poll_hotkey_edge(0x55)
            or self.bridge.poll_hotkey_edge(0x65)
        ):
            self._execute_active_row(secondary=False)
            return

        # Secondary Quick Action inside Apps (F10 0x79 / O 0x4F / Numpad 0 0x60)
        if (
            self.bridge.poll_hotkey_edge(0x79)
            or self.bridge.poll_hotkey_edge(0x4F)
            or self.bridge.poll_hotkey_edge(0x60)
        ):
            self._execute_active_row(secondary=True)
            return

    def _normalize_vietlott_picks(self, raw_str: str = "") -> str:
        v_code, max_n, cnt_n, _, _ = VIETLOTT_MODES[self.vietlott_mode_idx % len(VIETLOTT_MODES)]
        nums = []
        s = str(raw_str).strip()
        if " " in s or "-" in s or "," in s:
            tokens = s.replace("-", " ").replace(",", " ").split()
        else:
            digits = "".join(ch for ch in s if ch.isdigit())
            tokens = [digits[i : i + 2] for i in range(0, len(digits), 2)]
        for tok in tokens:
            if tok.isdigit():
                v = int(tok)
                if 1 <= v <= max_n and v not in nums:
                    nums.append(v)
        pool = [x for x in range(1, max_n + 1) if x not in nums]
        while len(nums) < cnt_n and pool:
            pick = random.choice(pool)
            pool.remove(pick)
            nums.append(pick)
        nums = sorted(nums[:cnt_n])
        return " ".join(f"{x:02d}" for x in nums)

    def _move_cursor_vertical(self, delta: int):
        with self.lock:
            app = self.phone_app
            sub = self.app_subpage.get(app, 0)
            home_apps = self._get_home_apps()
            if app == 0:
                if self.home_cursor_idx >= 9:
                    col = self.home_cursor_idx - 9
                    self.home_cursor_idx = (6 + col) if delta < 0 else col
                else:
                    self.last_home_col = self.home_cursor_idx % 3
                    nxt = self.home_cursor_idx + delta * 3
                    if nxt >= 9 or nxt < 0:
                        self.home_cursor_idx = 9 + min(self.last_home_col, 1)
                    else:
                        self.home_cursor_idx = nxt
                _, _, short_lbl, desc_lbl = home_apps[self.home_cursor_idx % len(home_apps)]
                self.last_toast = self._t(
                    f"Select App {self.home_cursor_idx + 1}. {short_lbl}: {desc_lbl} [F9: Open]",
                    f"Chon App {self.home_cursor_idx + 1}. {short_lbl}: {desc_lbl} [F9: Mo]",
                )
            elif app == 10:
                pois = self._get_active_ggmap_pois()
                if pois:
                    self.ggmap_poi_idx = (self.ggmap_poi_idx + delta) % len(pois)
                    p = pois[self.ggmap_poi_idx]
                    self.ggmap_selected_id = p["id"]
                    self.last_toast = self._t(
                        f"📍 [{self.ggmap_poi_idx+1}/{len(pois)}] {p['name']} ({p['region']}) • "
                        f"{p['dist_str']} [{p['compass']}] (F9: Set GPS | F10: Clear GPS)",
                        f"📍 [{self.ggmap_poi_idx+1}/{len(pois)}] {p['name']} ({p['region']}) • "
                        f"Cach {p['dist_str']} [{p['compass']}] (F9: Chi Duong GPS | F10: Huy GPS)",
                    )
            elif app in (2, 3) and sub == 0:
                grp = "stocks" if app == 2 else "crypto"
                m_dict = self.stocks_market if app == 2 else self.crypto_market
                syms = list(m_dict.keys())
                cur_s = self.selected_stock_sym if app == 2 else self.selected_crypto_sym
                idx = (syms.index(cur_s) + delta) % len(syms) if cur_s in syms else 0
                self.market_watch_idx[grp] = idx
                if app == 2:
                    self.selected_stock_sym = syms[idx]
                else:
                    self.selected_crypto_sym = syms[idx]
                a = m_dict[syms[idx]]
                self.last_toast = self._t(
                    f"Market Watch: {a['symbol']} (${a['price']}) [Press F9 for Candlestick Chart & Trade]",
                    f"Bang Gia: {a['symbol']} (${a['price']}) [Bam F9 xem Bieu Do Nen & Dat Lenh]",
                )
            elif app == 4 and sub == 0:
                lg_matches = self._get_active_league_fixtures()
                if lg_matches:
                    self.sport_match_idx = (self.sport_match_idx + delta) % len(lg_matches)
                    m = lg_matches[self.sport_match_idx]
                    self.last_toast = self._t(
                        f"Match #{self.sport_match_idx+1}: {m['home']} vs {m['away']} [Press F9 for Odds & Bet]",
                        f"Tran #{self.sport_match_idx+1}: {m['home']} vs {m['away']} [Bam F9 Dat Keo]",
                    )
            else:
                if app == 6:
                    max_rows = 2
                elif app == 5:
                    max_rows = 3 if sub == 0 else 4
                elif app in (1, 2, 3, 4, 7):
                    max_rows = 3
                else:
                    max_rows = 4
                self.app_cursor[app] = (self.app_cursor.get(app, 0) + delta) % max_rows
            self._write_hud_dat(force=True)

    def _step_tx_amount(self, delta: int):
        total_opts = len(AMOUNT_PRESETS) + 2  # + 50% Cash, ALL-IN Cash
        self.amount_preset_idx = (self.amount_preset_idx + delta) % total_opts
        if self.amount_preset_idx < len(AMOUNT_PRESETS):
            self.tx_amount = AMOUNT_PRESETS[self.amount_preset_idx]
            self.last_toast = self._t(
                f"Tx Amount: ${self.tx_amount:,} (Or press F6 to type any custom amount!)",
                f"Muc tien GD: ${self.tx_amount:,} (Hoac bam F6 de go so tu do!)",
            )
        elif self.amount_preset_idx == len(AMOUNT_PRESETS):
            self.tx_amount = max(10, self.cash // 2)
            self.last_toast = self._t(
                f"Tx Amount: 50% Cash (${self.tx_amount:,})",
                f"Muc tien GD: 50% Tien Mat (${self.tx_amount:,})",
            )
        else:
            self.tx_amount = max(10, self.cash)
            self.last_toast = self._t(
                f"Tx Amount: ALL-IN Cash (${self.tx_amount:,})",
                f"Muc tien GD: ALL-IN Tien Mat (${self.tx_amount:,})",
            )

    def _adjust_active_row(self, delta: int):
        with self.lock:
            app = self.phone_app
            sub = self.app_subpage.get(app, 0)
            row = self.app_cursor.get(app, 0)
            home_apps = self._get_home_apps()
            gg_cats = self._get_ggmap_categories()
            trade_modes = self._get_trade_modes()
            sport_picks = self._get_sport_picks()
            lotto_subpages = self._get_lotto_subpages()
            scratch_tiers = self._get_scratch_tiers()
            xskt_modes = self._get_xskt_modes()
            viet_modes = self._get_vietlott_modes()
            keno_modes = self._get_keno_modes()
            bug_cats = self._get_bug_categories()
            unstuck_modes = self._get_unstuck_modes()

            if app == 0:
                self.home_cursor_idx = (self.home_cursor_idx + delta) % len(home_apps)
                if self.home_cursor_idx < 9:
                    self.last_home_col = self.home_cursor_idx % 3
                _, _, short_lbl, desc_lbl = home_apps[self.home_cursor_idx]
                self.last_toast = self._t(
                    f"Select App {self.home_cursor_idx + 1}. {short_lbl}: {desc_lbl} [F9: Open]",
                    f"Chon App {self.home_cursor_idx + 1}. {short_lbl}: {desc_lbl} [F9: Mo]",
                )

            elif app == 10:
                self.ggmap_cat_idx = (self.ggmap_cat_idx + delta) % len(gg_cats)
                self.app_subpage[10] = self.ggmap_cat_idx
                self.ggmap_poi_idx = 0
                self.ggmap_selected_id = None
                pois = self._get_active_ggmap_pois()
                cat_lbl = gg_cats[self.ggmap_cat_idx][1]
                self.last_toast = self._t(
                    f"🗺️ GG Map [{cat_lbl}]: {len(pois)} POIs (I/K Select POI, F9 Set GPS)",
                    f"🗺️ GG Map [{cat_lbl}]: {len(pois)} diem den (I/K Chon Diem, F9 Cam Moc GPS)",
                )

            elif app == 1:
                if row == 0:
                    self.app_subpage[1] = (sub + delta) % 3
                    sub_names = (
                        ["1/3: Sinh Hoat & An Uong", "2/3: The ATM & Tiet Kiem", "3/3: Tin Dung & Vay Von"]
                        if self._is_vi()
                        else ["1/3: Vitality & Dining", "2/3: ATM & Savings", "3/3: Credit & Loans"]
                    )
                    self.last_toast = self._t(
                        f"Life & Bank - Page {sub_names[self.app_subpage[1]]}",
                        f"Doi Song - Trang {sub_names[self.app_subpage[1]]}",
                    )
                elif row == 1:
                    if sub == 0:
                        self.life_meal_idx = (self.life_meal_idx + delta) % 3
                    else:
                        self._step_tx_amount(delta)
                elif row == 2:
                    if sub == 0:
                        self.life_meal_idx = (self.life_meal_idx + delta) % 3
                    elif sub == 1:
                        self.life_bank_idx = (self.life_bank_idx + delta) % 4
                    else:
                        self.life_loan_idx = (self.life_loan_idx + delta) % 3

            elif app in (2, 3):
                syms = list((self.stocks_market if app == 2 else self.crypto_market).keys())
                if sub == 0:
                    self._step_tx_amount(delta)
                else:
                    if row == 0:
                        self.trade_mode_idx = (self.trade_mode_idx + delta) % len(trade_modes)
                        _, _, lbl = trade_modes[self.trade_mode_idx]
                        self.last_toast = self._t(
                            f"Order Mode: {lbl} (Press F9/Enter to execute order)",
                            f"Che do Lenh: {lbl} (Bam F9/Enter de khop lenh)",
                        )
                    elif row == 1:
                        self._step_tx_amount(delta)
                    elif row == 2:
                        cur_s = self.selected_stock_sym if app == 2 else self.selected_crypto_sym
                        idx = (syms.index(cur_s) + delta) % len(syms)
                        if app == 2:
                            self.selected_stock_sym = syms[idx]
                        else:
                            self.selected_crypto_sym = syms[idx]
                        self.last_toast = self._t(
                            f"Switched ticker: {syms[idx]} (Backspace/F8 for Market Watch)",
                            f"Chuyen ma: {syms[idx]} (Backspace/F8 ve Bang Gia)",
                        )

            elif app == 4:
                if sub == 0:
                    self.selected_league_idx = (self.selected_league_idx + delta) % len(LEAGUES)
                    self.sport_match_idx = 0
                    lg = LEAGUES[self.selected_league_idx]
                    self.last_toast = self._t(
                        f"League ({self.selected_league_idx+1}/5): {lg['name']} (I/K Select Match, F9 Open Odds)",
                        f"Giai ({self.selected_league_idx+1}/5): {lg['name']} (I/K Chon Tran, F9 Mo Keo)",
                    )
                else:
                    if row == 0:
                        self.sport_pick_idx = (self.sport_pick_idx + delta) % len(sport_picks)
                        _, lbl = sport_picks[self.sport_pick_idx]
                        self.last_toast = self._t(
                            f"Selected Pick: {lbl} (Press F9/Enter to place bet)",
                            f"Chon Keo: {lbl} (Bam F9/Enter dat cuoc)",
                        )
                    elif row == 1:
                        self._step_tx_amount(delta)
                    elif row == 2:
                        lg_matches = self._get_active_league_fixtures()
                        if lg_matches:
                            self.sport_match_idx = (self.sport_match_idx + delta) % len(lg_matches)

            elif app == 5:
                if row == 0:
                    self.app_subpage[5] = (sub + delta) % 4
                    self.app_cursor[5] = 0
                    self.last_toast = self._t(
                        f"Lottery - Page {lotto_subpages[self.app_subpage[5]]}",
                        f"Xo So - Trang {lotto_subpages[self.app_subpage[5]]}",
                    )
                elif sub == 0:
                    self.scratch_tier_idx = (self.scratch_tier_idx + delta) % len(scratch_tiers)
                    self.last_toast = self._t(
                        f"Scratch Card Tier: {scratch_tiers[self.scratch_tier_idx][2]}",
                        f"Chon hang Ve Cao: {scratch_tiers[self.scratch_tier_idx][2]}",
                    )
                elif sub == 1:
                    if row == 1:
                        self.xskt_mode_idx = (self.xskt_mode_idx + delta) % len(xskt_modes)
                        self.last_toast = self._t(
                            f"16:30 Lotto Mode: {xskt_modes[self.xskt_mode_idx][2]}",
                            f"Loai hinh XSKT 16:30: {xskt_modes[self.xskt_mode_idx][2]}",
                        )
                    elif row == 2:
                        self.keypad_idx = (self.keypad_idx + delta) % len(self.keypad_presets)
                        self.custom_lotto_str = self.keypad_presets[self.keypad_idx]
                        self.last_toast = self._t(
                            f"6D Lotto Number: [{self.custom_lotto_str}] (Or press F6 to type 6 digits!)",
                            f"Day so XSKT/Lo De: [{self.custom_lotto_str}] (Hoac bam F6 de go 6 so!)",
                        )
                    else:
                        if self.xskt_mode_idx == 0:
                            self.xskt_mode_idx = (self.xskt_mode_idx + delta) % len(xskt_modes)
                            self.last_toast = self._t(
                                f"16:30 Lotto Mode: {xskt_modes[self.xskt_mode_idx][2]}",
                                f"Loai hinh XSKT 16:30: {xskt_modes[self.xskt_mode_idx][2]}",
                            )
                        else:
                            self._step_tx_amount(delta)
                elif sub == 2:
                    if row == 1:
                        self.vietlott_mode_idx = (self.vietlott_mode_idx + delta) % len(viet_modes)
                        self.custom_vietlott_str = self._normalize_vietlott_picks(self.custom_vietlott_str)
                        self.last_toast = self._t(
                            f"18:00 Vietlott Game: {viet_modes[self.vietlott_mode_idx][4]}",
                            f"Dai Vietlott 18:00: {viet_modes[self.vietlott_mode_idx][4]}",
                        )
                    elif row == 2:
                        _, max_n, cnt_n, _, _ = viet_modes[self.vietlott_mode_idx % len(viet_modes)]
                        picks = sorted(random.sample(range(1, max_n + 1), cnt_n))
                        self.custom_vietlott_str = " ".join(f"{x:02d}" for x in picks)
                        self.last_toast = self._t(
                            f"Vietlott Balls: [{self.custom_vietlott_str.replace(' ', '-')}] (F6: Type custom balls)",
                            f"Bo bong Vietlott: [{self.custom_vietlott_str.replace(' ', '-')}] (F6: Tu go so)",
                        )
                    else:
                        self.vietlott_mode_idx = (self.vietlott_mode_idx + delta) % len(viet_modes)
                        self.custom_vietlott_str = self._normalize_vietlott_picks(self.custom_vietlott_str)
                        self.last_toast = self._t(
                            f"18:00 Vietlott Game: {viet_modes[self.vietlott_mode_idx][4]}",
                            f"Dai Vietlott 18:00: {viet_modes[self.vietlott_mode_idx][4]}",
                        )
                elif sub == 3:
                    if row == 1:
                        self.keno_mode_idx = (self.keno_mode_idx + delta) % len(keno_modes)
                        self.last_toast = self._t(
                            f"Keno/Max3D Pick: {keno_modes[self.keno_mode_idx][2]}",
                            f"Cua Keno/Max3D: {keno_modes[self.keno_mode_idx][2]}",
                        )
                    else:
                        self._step_tx_amount(delta)

            elif app == 6:
                if row == 0:
                    self.news_sec_idx = (self.news_sec_idx + delta) % 4
                    sec_names = (
                        [
                            "1/4: The Gioi & Chinh Tri",
                            "2/4: Tai Chinh & Vang",
                            "3/4: Crypto & Cong Nghe",
                            "4/4: The Thao & Giai Dau",
                        ]
                        if self._is_vi()
                        else [
                            "1/4: World & Politics",
                            "2/4: Wall St & Gold",
                            "3/4: Crypto, Tech & Anime",
                            "4/4: Pro Sports & Leagues",
                        ]
                    )
                    self.last_toast = f"EagleTimes - {sec_names[self.news_sec_idx]}"
                elif row == 1:
                    self.news_step_idx = (self.news_step_idx + delta) % 4

            elif app == 7:
                self.port_tab_idx = (self.port_tab_idx + delta) % 3
                tab_names = (
                    [
                        "Trang 1/3: Phan Bo Von & Thanh Tien Do",
                        "Trang 2/3: Bang Nam Giu Spot (CK/Vang/Crypto)",
                        "Trang 3/3: Bang Vi The Futures & Keo Bet",
                    ]
                    if self._is_vi()
                    else [
                        "Page 1/3: Asset Allocation & Gauges",
                        "Page 2/3: Spot Holdings (Stocks/Gold/Crypto)",
                        "Page 3/3: Open Futures & Active Bets",
                    ]
                )
                self.last_toast = self._t(
                    f"Portfolio - {tab_names[self.port_tab_idx]}",
                    f"Danh Muc - {tab_names[self.port_tab_idx]}",
                )

            elif app == 8:
                if row == 3:
                    self.app_subpage[8] = (sub + delta) % 3
                    if self.app_subpage[8] == 0:
                        self.last_toast = self._t("App 8: Page 1/3 Radar & Suspect #1", "App 8: Trang 1/3 Radar & Nghi Pham #1")
                    elif self.app_subpage[8] == 1:
                        self.last_toast = self._t("App 8: Page 2/3 4-Col .IPL/.COL Table (15m)", "App 8: Trang 2/3 Bang 4 Cot .IPL/.COL (15m)")
                    else:
                        self.last_toast = self._t(
                            "App 8: Page 3/3 On-Demand Debugger, Doctor & Auto-Probe",
                            "App 8: Trang 3/3 Debugger, Doctor & Auto-Probe Theo Yeu Cau",
                        )
                elif sub == 2:
                    if row == 0:
                        new_m = self.debug_sys.toggle_mode(engine=self)
                        self.last_toast = self._t(
                            f"Debugger Mode: {new_m.upper()} ({'Live Pools/Streaming/FPS' if new_m == 'deep' else '0% Game Overhead'})",
                            f"Che do Debug: {new_m.upper()} ({'Do RAM/Pool/FPS' if new_m == 'deep' else '0% Anh Huong Game'})",
                        )
                    elif row == 1:
                        rep = self.debug_sys.run_preflight_doctor(engine=self)
                        self.last_toast = rep["summary"]
                    elif row == 2:
                        suites = self.debug_sys.get_probe_suites(is_vi=self._is_vi())
                        self.debug_sys.probe_suite_idx = (self.debug_sys.probe_suite_idx + delta) % len(suites)
                        _, s_lbl, _ = suites[self.debug_sys.probe_suite_idx]
                        self.last_toast = self._t(
                            f"Auto-Probe Suite: {s_lbl} (Press F9 to Start/Stop Tour)",
                            f"Goi Auto-Probe: {s_lbl} (Bam F9 de Chay/Dung Tour)",
                        )
                else:
                    if row in (0, 1):
                        self.bug_cat_idx = (self.bug_cat_idx + delta) % len(bug_cats)
                        _, cat_lbl = bug_cats[self.bug_cat_idx]
                        self.last_toast = self._t(
                            f"Bug Category: {cat_lbl} (Press F9 or Ctrl+F11 to record)",
                            f"Phan loai Bug: {cat_lbl} (Bam F9 hoac Ctrl+F11 de ghi nhan)",
                        )
                    elif row == 2:
                        self.unstuck_mode_idx = (self.unstuck_mode_idx + delta) % len(unstuck_modes)
                        _, mode_lbl = unstuck_modes[self.unstuck_mode_idx]
                        self.last_toast = self._t(
                            f"Unstuck Mode: {mode_lbl} (Press F9/F10/F12)",
                            f"Che do Cuu Ho: {mode_lbl} (Bam F9/F10/F12)",
                        )

            elif app == 9:
                if row == 0:
                    self.wp_idx = (self.wp_idx + delta) % len(WALLPAPER_PRESETS)
                    self.last_toast = self._t(
                        f"Anime Wallpaper: {WALLPAPER_PRESETS[self.wp_idx][1]}",
                        f"Hinh nen Anime: {WALLPAPER_PRESETS[self.wp_idx][1]}",
                    )
                elif row == 1:
                    self.mascot_idx = (self.mascot_idx + delta) % len(MASCOT_PRESETS)
                    self.last_toast = f"Mascot Widget: {MASCOT_PRESETS[self.mascot_idx][1]}"
                elif row == 2:
                    self.theme_idx = (self.theme_idx + delta) % len(THEME_PRESETS)
                    self.last_toast = self._t(
                        f"Neon Border Theme: {THEME_PRESETS[self.theme_idx][1]}",
                        f"Chu de vien Neon: {THEME_PRESETS[self.theme_idx][1]}",
                    )
                elif row == 3:
                    self._set_language("vi" if self.lang == "en" else "en")

            self._write_hud_dat(force=True)

    def _execute_active_row(self, secondary: bool = False):
        app = self.phone_app
        sub = self.app_subpage.get(app, 0)
        row = self.app_cursor.get(app, 0)
        trade_modes = self._get_trade_modes()
        sport_picks = self._get_sport_picks()
        lotto_subpages = self._get_lotto_subpages()
        scratch_tiers = self._get_scratch_tiers()
        xskt_modes = self._get_xskt_modes()
        viet_modes = self._get_vietlott_modes()
        keno_modes = self._get_keno_modes()

        if app == 0:
            if not secondary:
                with self.lock:
                    self._open_app(self.home_cursor_idx + 1)
                    self._write_hud_dat(force=True)
            return

        if app == 11:
            with self.lock:
                self.paimon.call(self, (row % 4) + 1)
                self._write_hud_dat(force=True)
            return

        if app == 10:
            with self.lock:
                if secondary:
                    self._clear_gps_waypoint(arrived=False)
                else:
                    pois = self._get_active_ggmap_pois()
                    if pois:
                        sel_poi = pois[self.ggmap_poi_idx % len(pois)]
                        self._set_gps_waypoint_to_poi(sel_poi)
                self._write_hud_dat(force=True)
            return

        if app == 1:
            if secondary:
                self.handle_action({"action": "sleep_rest"})
                return
            if row == 0:
                with self.lock:
                    self.app_subpage[1] = (sub + 1) % 3
                    self._write_hud_dat(force=True)
                return
            if sub == 0:
                if self.life_meal_idx == 0:
                    self.handle_action({"action": "eat_meal", "tier": "burger"})
                elif self.life_meal_idx == 1:
                    self.handle_action({"action": "eat_meal", "tier": "drink"})
                else:
                    self.handle_action({"action": "sleep_rest"})
            elif sub == 1:
                if row == 1:
                    with self.lock:
                        self.keypad_active = True
                        self.keypad_buffer = ""
                        self.keypad_target = "amount"
                        self.last_toast = self._t(
                            "Type amount ($) using keys 0-9, press Enter/F6 to save!",
                            "Go so tien ($) bang phim 0-9, bam Enter/F6 de luu!",
                        )
                        self._write_hud_dat(force=True)
                else:
                    dirs = [("bank_tx", "deposit"), ("bank_tx", "withdraw"), ("savings_tx", "deposit"), ("savings_tx", "withdraw")]
                    act_name, d_val = dirs[self.life_bank_idx % 4]
                    self.handle_action({"action": act_name, "dir": d_val, "amount": self.tx_amount})
            else:
                if row == 1:
                    with self.lock:
                        self.keypad_active = True
                        self.keypad_buffer = ""
                        self.keypad_target = "amount"
                        self.last_toast = self._t(
                            "Type amount ($) using keys 0-9, press Enter/F6 to save!",
                            "Go so tien ($) bang phim 0-9, bam Enter/F6 de luu!",
                        )
                        self._write_hud_dat(force=True)
                else:
                    l_dirs = ["borrow", "repay", "repay_all"]
                    self.handle_action({"action": "loan_tx", "dir": l_dirs[self.life_loan_idx % 3], "amount": self.tx_amount})

        elif app in (2, 3):
            grp = "stocks" if app == 2 else "crypto"
            sym = self.selected_stock_sym if app == 2 else self.selected_crypto_sym
            if sub == 0:
                if secondary:
                    self.handle_action({
                        "action": "trade_order",
                        "market_group": grp,
                        "symbol": sym,
                        "mode": "spot_buy",
                        "usd": self.tx_amount,
                        "leverage": 1,
                    })
                else:
                    with self.lock:
                        self.app_subpage[app] = 1
                        self.app_cursor[app] = 0
                        self.last_toast = self._t(
                            f"Opened Candlestick Chart & Order Panel: {sym} (Backspace/F8 for Table)",
                            f"Mo Bieu Do Nen & Dat Lenh: {sym} (Backspace/F8 ve Bang Gia)",
                        )
                        self._write_hud_dat(force=True)
                return

            if secondary or row == 2:
                grp_futs = [f for f in self.futures if f["market_group"] == grp]
                if grp_futs:
                    self.handle_action({"action": "close_future", "id": grp_futs[0]["id"]})
                else:
                    with self.lock:
                        self.app_subpage[app] = 0
                        self.last_toast = self._t("Returned to Market Watch!", "Da quay lai Bang Gia!")
                        self._write_hud_dat(force=True)
                return
            mode_key, lev_val, _ = trade_modes[self.trade_mode_idx % len(trade_modes)]
            self.handle_action({
                "action": "trade_order",
                "market_group": grp,
                "symbol": sym,
                "mode": mode_key,
                "usd": self.tx_amount,
                "leverage": lev_val,
            })

        elif app == 4:
            lg = LEAGUES[self.selected_league_idx % len(LEAGUES)]
            if secondary:
                self.handle_action({"action": "sim_league_matches", "league_id": lg["id"]})
                return
            if sub == 0:
                with self.lock:
                    self.app_subpage[4] = 1
                    self.app_cursor[4] = 0
                    lg_matches = self._get_active_league_fixtures()
                    m = lg_matches[self.sport_match_idx % len(lg_matches)] if lg_matches else None
                    if m:
                        self.last_toast = self._t(
                            f"Bet Slip & Standings: {m['home']} vs {m['away']} (Backspace/F8 for Match Table)",
                            f"Phieu Cuoc & BXH: {m['home']} vs {m['away']} (Backspace/F8 ve Bang Keo)",
                        )
                    self._write_hud_dat(force=True)
                return
            lg_matches = self._get_active_league_fixtures()
            if not lg_matches:
                return
            m = lg_matches[self.sport_match_idx % len(lg_matches)]
            if row == 2:
                self.handle_action({"action": "sim_one_match", "match_id": m["id"]})
                return
            pick_code, pick_lbl = sport_picks[self.sport_pick_idx % len(sport_picks)]
            self.handle_action({
                "action": "place_bet",
                "match_id": m["id"],
                "pick": pick_code,
                "stake": self.tx_amount,
                "label": f"{m['home']} vs {m['away']} ({pick_lbl})",
            })

        elif app == 5:
            if row == 0 and not secondary:
                with self.lock:
                    self.app_subpage[5] = (sub + 1) % 4
                    self.app_cursor[5] = 0
                    self.last_toast = self._t(
                        f"Lottery - Page {lotto_subpages[self.app_subpage[5]]}",
                        f"Xo So - Trang {lotto_subpages[self.app_subpage[5]]}",
                    )
                    self._write_hud_dat(force=True)
                return
            if sub == 0:
                tier_key = scratch_tiers[self.scratch_tier_idx % len(scratch_tiers)][0]
                if row == 1 and not secondary:
                    with self.lock:
                        self.scratch_tier_idx = (self.scratch_tier_idx + 1) % len(scratch_tiers)
                        self.last_toast = self._t(
                            f"Scratch Card Tier: {scratch_tiers[self.scratch_tier_idx][2]}",
                            f"Chon hang Ve Cao: {scratch_tiers[self.scratch_tier_idx][2]}",
                        )
                        self._write_hud_dat(force=True)
                    return
                self.handle_action({"action": "buy_scratch", "tier": tier_key, "combo": 5 if secondary else 1})
            elif sub == 1:
                if secondary:
                    self.handle_action({"action": "draw_lottery_now", "filter_type": "XSKT_6D"})
                    return
                if row == 1:
                    with self.lock:
                        self.xskt_mode_idx = (self.xskt_mode_idx + 1) % len(xskt_modes)
                        self.last_toast = self._t(
                            f"16:30 Lotto Mode: {xskt_modes[self.xskt_mode_idx][2]}",
                            f"Loai hinh XSKT 16:30: {xskt_modes[self.xskt_mode_idx][2]}",
                        )
                        self._write_hud_dat(force=True)
                    return
                if row == 2:
                    with self.lock:
                        self.keypad_active = True
                        self.keypad_buffer = ""
                        self.keypad_target = "lotto"
                        self.last_toast = self._t(
                            "Type 6 digits for 16:30 Lotto using 0-9, press Enter/F6 to save!",
                            "Go 6 chu so XSKT/Lo De bang phim 0-9, bam Enter/F6 de luu!",
                        )
                        self._write_hud_dat(force=True)
                    return
                x_code, _, _ = xskt_modes[self.xskt_mode_idx % len(xskt_modes)]
                self.handle_action({
                    "action": "buy_lotto_6d",
                    "mode": x_code,
                    "number": self.custom_lotto_str,
                    "stake": self.tx_amount,
                })
            elif sub == 2:
                if secondary:
                    self.handle_action({"action": "draw_lottery_now", "filter_type": "VIETLOTT"})
                    return
                if row == 1:
                    with self.lock:
                        self.vietlott_mode_idx = (self.vietlott_mode_idx + 1) % len(viet_modes)
                        self.custom_vietlott_str = self._normalize_vietlott_picks(self.custom_vietlott_str)
                        self.last_toast = self._t(
                            f"18:00 Vietlott Game: {viet_modes[self.vietlott_mode_idx][4]}",
                            f"Dai Vietlott 18:00: {viet_modes[self.vietlott_mode_idx][4]}",
                        )
                        self._write_hud_dat(force=True)
                    return
                if row == 2:
                    with self.lock:
                        self.keypad_active = True
                        self.keypad_buffer = ""
                        self.keypad_target = "vietlott"
                        self.last_toast = self._t(
                            "Type Vietlott balls (2 digits/ball, e.g. 051219263844), press Enter/F6 to save!",
                            "Go bo bong Vietlott (2 so/bong, VD: 051219263844), bam Enter/F6 luu!",
                        )
                        self._write_hud_dat(force=True)
                    return
                v_code, _, _, _, _ = viet_modes[self.vietlott_mode_idx % len(viet_modes)]
                self.handle_action({
                    "action": "buy_vietlott",
                    "game": v_code,
                    "numbers": self.custom_vietlott_str,
                })
            elif sub == 3:
                if row == 1 and not secondary:
                    with self.lock:
                        self.keno_mode_idx = (self.keno_mode_idx + 1) % len(keno_modes)
                        self.last_toast = self._t(
                            f"Keno/Max3D Pick: {keno_modes[self.keno_mode_idx][2]}",
                            f"Cua Keno/Max3D: {keno_modes[self.keno_mode_idx][2]}",
                        )
                        self._write_hud_dat(force=True)
                    return
                if row == 2 and not secondary:
                    with self.lock:
                        self.keypad_active = True
                        self.keypad_buffer = ""
                        self.keypad_target = "amount"
                        self.last_toast = self._t(
                            "Type Keno stake ($) using 0-9, press Enter/F6 to save!",
                            "Go so tien cuoc Keno ($) bang phim 0-9, bam Enter/F6 de luu!",
                        )
                        self._write_hud_dat(force=True)
                    return
                k_code, _, _ = keno_modes[self.keno_mode_idx % len(keno_modes)]
                self.handle_action({
                    "action": "play_keno",
                    "mode": k_code,
                    "stake": self.tx_amount,
                    "numbers": self.custom_lotto_str,
                })


        elif app == 6:
            if secondary:
                self.handle_action({"action": "advance_day", "delta": 1})
                return
            if row == 0:
                with self.lock:
                    self.news_sec_idx = (self.news_sec_idx + 1) % 4
                    self._write_hud_dat(force=True)
                return
            steps = [-1, 1, 7, 30]
            d_val = steps[self.news_step_idx % 4]
            self.handle_action({"action": "advance_day", "delta": d_val})

        elif app == 7:
            if secondary:
                self.handle_action({"action": "close_all_futures"})
            elif row == 0:
                with self.lock:
                    self.port_tab_idx = (self.port_tab_idx + 1) % 3
                    self._write_hud_dat(force=True)
            elif row == 1:
                self.handle_action({"action": "sell_all_spot"})
            elif row == 2:
                self.handle_action({"action": "settle_all_portfolio"})

        elif app == 8:
            if secondary:
                if self.debug_sys.probe_active:
                    self.handle_action({"action": "stop_auto_probe"})
                else:
                    self.handle_action({"action": "unstuck_player"})
                return
            if sub == 2:
                if row == 0:
                    self.handle_action({"action": "toggle_debug_mode"})
                elif row == 1:
                    self.handle_action({"action": "run_preflight_doctor"})
                elif row == 2:
                    self.handle_action({"action": "toggle_auto_probe"})
                elif row == 3:
                    self.handle_action({"action": "analyze_latest_crash"})
            else:
                if row in (0, 1):
                    self.handle_action({"action": "report_map_bug"})
                elif row == 2:
                    self.handle_action({"action": "unstuck_player"})
                elif row == 3:
                    self.handle_action({"action": "inspect_live_coords"})

        elif app == 9:
            if secondary or row == 3:
                with self.lock:
                    self._set_language("vi" if self.lang == "en" else "en")
                    self._write_hud_dat(force=True)
                return
            with self.lock:
                if row == 0:
                    self.wp_idx = (self.wp_idx + 1) % len(WALLPAPER_PRESETS)
                    self.last_toast = self._t(
                        f"Anime Wallpaper: {WALLPAPER_PRESETS[self.wp_idx][1]}",
                        f"Hinh nen Anime: {WALLPAPER_PRESETS[self.wp_idx][1]}",
                    )
                elif row == 1:
                    self.mascot_idx = (self.mascot_idx + 1) % len(MASCOT_PRESETS)
                    self.last_toast = f"Mascot Widget: {MASCOT_PRESETS[self.mascot_idx][1]}"
                elif row == 2:
                    self.theme_idx = (self.theme_idx + 1) % len(THEME_PRESETS)
                    self.last_toast = self._t(
                        f"Neon Border Theme: {THEME_PRESETS[self.theme_idx][1]}",
                        f"Chu de vien Neon: {THEME_PRESETS[self.theme_idx][1]}",
                    )
                self._write_hud_dat(force=True)

    def _sync_ram_mailbox(self):
        payload = struct.pack(
            "<iiiiii",
            EAGLE_MAILBOX_MAGIC,
            int(self.state_version),
            int(self.phone_open),
            int(self.phone_app),
            int(self.hunger),
            int(self.energy),
        )
        self.bridge.write_bytes(ADDR_EAGLE_MAILBOX, payload)

    def sync_player_state(self):
        was_attached = self.ram_attached
        live = self.bridge.read_live_player()
        if live:
            self.ram_attached = True
            self._sample_position_trail(live)
            self._check_gps_arrival_and_sync()
            if self.bridge.pid != self.last_attached_pid or not was_attached:
                self.last_attached_pid = self.bridge.pid
                # Always reset to Home Screen (app=0) on game entry so it never auto-opens into Lottery (app=5)!
                self.phone_open = 1
                self.phone_app = 0
                self.home_cursor_idx = 0
                self.last_home_col = 0
                self.keypad_active = False
                self.bridge.menu_cooldown_until = time.time() + 1.5
                self.bridge.clear_hotkey_states()
                self._last_lua_payload = ""
                self._write_hud_dat(force=True)
            else:
                self._sync_ram_mailbox()

            # Detect in-game Restaurant / Food Vendor eating!
            if (
                self.last_live_hp is not None
                and not self.ignore_next_hp_jump
                and live["health"] >= self.last_live_hp + 5
                and self.last_live_cash is not None
                and (self.last_live_cash - 500) <= live["cash"] < self.last_live_cash
            ):
                self.hunger = min(100, self.hunger + 35)
                self.energy = min(100, self.energy + 20)
                self.last_toast = self._t(
                    "🍔 GTA SA Restaurant Meal synced: +35% Fullness & +20% Energy!",
                    "🍔 Dong bo an uong Nha Hang GTA SA: +35% No & +20% Energy!",
                )
                self.push_event_banner(
                    self._t("DINING AT GTA SA RESTAURANT", "AN UONG TAI NHA HANG GTA SA"),
                    self._t(
                        f"Restored +35% Fullness ({self.hunger}%) & +20% Energy ({self.energy}%)",
                        f"Da hoi +35% Do No ({self.hunger}%) & +20% Nang Luong ({self.energy}%)",
                    ),
                    kind="win",
                )
            self.ignore_next_hp_jump = False
            self.last_live_hp = live["health"]
            self.last_live_cash = live["cash"]

            self.cash = live["cash"]
            self.health = live["health"]
            self.max_health = live["max_health"]
            self.armor = live["armor"]
            h, m = live["hours"], live["mins"]
            self.clock_str = f"{h:02d}:{m:02d}"

            # Check if GTA SA clock rolled past Midnight (23 -> 0)
            if self.last_game_hour >= 22 and h <= 2:
                self._advance_chronological_day(1)
            self.last_game_hour = h

            # Check automatic daily lottery draw hours (Strictly Separated: 16:30 XSKT vs 18:00 Vietlott!)
            if (h == 16 and m >= 30 or h == 17) and not self.drew_1630_today:
                self.drew_1630_today = True
                self._run_lottery_draw(filter_type="XSKT_6D")
            if h >= 18 and not self.drew_1800_today:
                self.drew_1800_today = True
                self._run_lottery_draw(filter_type="VIETLOTT")

            if live["pos"] and self.atms:
                px, py, _ = live["pos"]
                best_d = min(math.hypot(px - a["x"], py - a["y"]) for a in self.atms)
                self.nearest_atm = f"{int(round(best_d / 10.0) * 10)}m"
        else:
            self.ram_attached = False

        try:
            self.debug_sys.tick_from_companion(self, was_attached, self.ram_attached)
        except Exception as e:
            self.debug_sys.logger.log_exception("EagleCompanion", "tick_from_companion", e)

    def _advance_chronological_day(self, delta_days: int):
        if delta_days > 0:
            if any(t["type"] in ("XSKT_6D", "LODE_DE", "LODE_LO2", "LODE_3CANG") for t in self.lottery["tickets"]):
                self._run_lottery_draw(filter_type="XSKT_6D")
            if any(t["type"] in ("MEGA_645", "POWER_655", "MEGA_BAO7", "POWER_BAO7") for t in self.lottery["tickets"]):
                self._run_lottery_draw(filter_type="VIETLOTT")

        self.day = max(1, min(5844, self.day + delta_days))
        self.current_date = START_DATE + datetime.timedelta(days=self.day - 1)
        self.drew_1630_today = False
        self.drew_1800_today = False


        if delta_days > 0:
            # 1. Settle any remaining sports bets from yesterday
            for idx in range(len(self.fixtures) - 1, -1, -1):
                if self.fixtures[idx].get("active_bet"):
                    self._resolve_fixture(idx, replace=False)

            # 2. Generate new day's sequential fixtures (25 matches across 5 leagues)
            self.fixtures = generate_daily_fixtures(self.day, lang=self.lang)
            self.sport_match_idx = 0

            # 3. Credit +1.5% daily Savings interest
            sav_interest = 0
            if self.savings > 0:
                sav_interest = max(1, int(round(self.savings * 0.015)))
                self.savings += sav_interest

            # 4. Loan interest (+3%/day) & Overdue check
            if self.loan > 0:
                loan_interest = max(1, int(round(self.loan * 0.03)))
                self.loan += loan_interest
                self.loan_days_left -= 1
                if self.loan_days_left <= 0:
                    self.loan_overdue = True
                    self.last_toast = self._t(
                        f"🩸 OVERDUE LOAN WARNING (${self.loan:,}): Loan sharks are draining Aether's HP!",
                        f"🩸 CANH BAO NO QUA HAN (${self.loan:,}): Giang ho dang tru mau Aether!",
                    )
                    self.push_event_banner(
                        self._t(
                            f"OVERDUE LOAN WARNING: ${self.loan:,}!",
                            f"CANH BAO NO QUA HAN: ${self.loan:,}!",
                        ),
                        self._t(
                            f"Added +${loan_interest:,} interest (3%/day) & Loan Sharks draining HP (-2 HP)!",
                            f"Bi cong lai +${loan_interest:,} (3%/ngay) & Giang Ho dang tru mau (-2 HP)!",
                        ),
                        kind="danger",
                        duration=8.0,
                    )
                else:
                    self.last_toast = self._t(
                        f"New Day {self.current_date.strftime('%d/%m/%Y')}: Loan Interest +${loan_interest:,} | Savings +${sav_interest:,}",
                        f"Qua ngay {self.current_date.strftime('%d/%m/%Y')}: Lai Vay +${loan_interest:,} | Lai Tiet Kiem +${sav_interest:,}",
                    )
                    self.push_event_banner(
                        self._t(
                            f"NEW DAY {self.current_date.strftime('%d/%m/%Y')} • LOAN & SAVINGS INTEREST",
                            f"NGAY MOI {self.current_date.strftime('%d/%m/%Y')} • LAI VAY & TIET KIEM",
                        ),
                        self._t(
                            f"Loan interest +${loan_interest:,} ({self.loan_days_left}d left) | Savings interest +${sav_interest:,}",
                            f"Tru lai vay +${loan_interest:,} (Con {self.loan_days_left} ngay) | Cong lai Tiet Kiem +${sav_interest:,}",
                        ),
                        kind="warn",
                        duration=7.0,
                    )
            else:
                self.loan_overdue = False
                self.last_toast = self._t(
                    f"🌅 New Day {self.current_date.strftime('%d/%m/%Y')} (Day {self.day}): EagleTimes & 25 new matches are out!",
                    f"🌅 Ngay moi {self.current_date.strftime('%d/%m/%Y')} (Day {self.day}): Bao EagleTimes & 25 Tran moi da ra!",
                )
                self.push_event_banner(
                    self._t(
                        f"NEW DAY {self.current_date.strftime('%d/%m/%Y')} (DAY {self.day})",
                        f"NGAY MOI {self.current_date.strftime('%d/%m/%Y')} (DAY {self.day})",
                    ),
                    self._t(
                        f"Savings Interest +${sav_interest:,} • EagleTimes Chronicle & 25 Sports Fixtures ready!",
                        f"Lai Tiet Kiem +${sav_interest:,} • Bao EagleTimes & 25 Keo The Thao moi da san sang!",
                    ),
                    kind="info",
                    duration=6.0,
                )
        else:
            self.fixtures = generate_daily_fixtures(self.day, lang=self.lang)
            self.last_toast = self._t(
                f"📅 Viewing historical date {self.current_date.strftime('%d/%m/%Y')} (Day {self.day})",
                f"📅 Dang xem lich su ngay {self.current_date.strftime('%d/%m/%Y')} (Day {self.day})",
            )

        # Re-anchor market prices toward the chronological date
        for sym, asset in self.stocks_market.items():
            target = get_chronological_target_price(asset, self.current_date)
            asset["price"] = round(target, asset["decimals"])
        for sym, asset in self.crypto_market.items():
            target = get_chronological_target_price(asset, self.current_date)
            asset["price"] = round(target, asset["decimals"])

        self.newspaper = generate_daily_newspaper(
            self.current_date, self.day, self.stocks_market, self.crypto_market, self.sport_history, self.fixtures, lang=self.lang
        )

    # ========================================================================
    # SIMULATION TICK (EVERY 2.0 SECONDS)
    # ========================================================================
    def step_simulation(self):
        with self.lock:
            self.sync_player_state()

            # Overdue Loan Health Drain ("tra khong du se bi mat mau dan toi chet")
            if self.loan > 0 and self.loan_overdue:
                self.modify_health(-2, allow_fatal=True)
                self.last_toast = self._t(
                    f"🩸 LOAN SHARKS: Draining -2 HP due to overdue loan ${self.loan:,}! Repay now!",
                    f"🩸 GIANG HO DOI NO: Bi tru -2 HP vi khoan vay qua han ${self.loan:,}! Hay tra no ngay!",
                )
                if time.time() > self.event_banner.get("until", 0):
                    self.push_event_banner(
                        self._t(
                            f"OVERDUE LOAN SHARKS (${self.loan:,})",
                            f"GIANG HO DOI NO QUA HAN (${self.loan:,})",
                        ),
                        self._t(
                            "Aether loses -2 HP per tick! Open App 1 (Life & Bank) to repay now!",
                            "Aether bi tru -2 HP moi nhip! Vao App 1 (Life & Bank) tra no ngay!",
                        ),
                        kind="danger",
                        duration=5.5,
                    )

            # Gentle Hunger/Energy decay
            if random.random() < 0.05:
                self.hunger = max(10, self.hunger - 1)
            if random.random() < 0.04:
                self.energy = max(10, self.energy - 1)

            # Step Stocks/Commodities & Crypto toward chronological anchor
            for group_dict in (self.stocks_market, self.crypto_market):
                for sym, asset in group_dict.items():
                    target = get_chronological_target_price(asset, self.current_date)
                    o = asset["price"]
                    dec = asset["decimals"]
                    vol = asset["volatility"]
                    y = self.current_date.year
                    a0 = asset["anchors"].get(y, o)
                    a1 = asset["anchors"].get(min(2025, y + 1), a0)
                    if a0 == a1 and abs(o - a0) < a0 * 0.02:
                        c = a0
                        h = a0
                        l = a0
                    else:
                        pull = (target - o) / max(o, 0.0001) * 0.15
                        shock = random.gauss(pull, vol * 0.45)
                        c = max(target * 0.1, o * (1.0 + shock))
                        h = max(o, c) * (1.0 + abs(random.gauss(0, vol * 0.25)))
                        l = min(o, c) * (1.0 - abs(random.gauss(0, vol * 0.25)))

                    candle = {"o": round(o, dec), "h": round(h, dec), "l": round(l, dec), "c": round(c, dec)}
                    asset["candles"].append(candle)
                    if len(asset["candles"]) > 48:
                        asset["candles"].pop(0)
                    asset["price"] = candle["c"]
                    open_0 = asset["candles"][0]["o"] or candle["c"]
                    asset["delta_pct"] = round(((asset["price"] - open_0) / open_0) * 100.0, 2)
                    asset["spot_val"] = round(asset["spot_qty"] * asset["price"], 2)
                    cost_b = asset.get("spot_cost", 0.0)
                    asset["spot_pnl"] = round(asset["spot_val"] - cost_b, 2) if asset["spot_qty"] > 0 else 0.0
                    asset["spot_pnl_pct"] = round((asset["spot_pnl"] / cost_b) * 100.0, 2) if cost_b > 0 and asset["spot_qty"] > 0 else 0.0

            # Update Futures Positions
            surviving = []
            for f in self.futures:
                m_dict = self.crypto_market if f["market_group"] == "crypto" else self.stocks_market
                mark = m_dict[f["symbol"]]["price"]
                f["mark"] = mark
                if f["side"] == "LONG":
                    pct = (mark - f["entry"]) / f["entry"]
                    if mark <= f["liq_price"]:
                        self.portfolio_stats["realized_market_pnl"] = round(
                            self.portfolio_stats["realized_market_pnl"] - f["margin"], 2
                        )
                        self.last_toast = self._t(
                            f"💥 Liquidated LONG {f['leverage']}x {f['symbol']} @ ${mark}!",
                            f"💥 Thanh ly LONG {f['leverage']}x {f['symbol']} @ ${mark}!",
                        )
                        self.push_event_banner(
                            self._t(
                                f"LIQUIDATED FUTURES LONG {f['leverage']}x {f['symbol']}!",
                                f"CHAY LENH FUTURES LONG {f['leverage']}x {f['symbol']}!",
                            ),
                            self._t(
                                f"Price hit liquidation threshold ${mark} (Lost margin -${f['margin']:,})",
                                f"Gia cham nguong thanh ly ${mark} (Mat von -${f['margin']:,})",
                            ),
                            kind="danger",
                        )
                        continue
                else:
                    pct = (f["entry"] - mark) / f["entry"]
                    if mark >= f["liq_price"]:
                        self.portfolio_stats["realized_market_pnl"] = round(
                            self.portfolio_stats["realized_market_pnl"] - f["margin"], 2
                        )
                        self.last_toast = self._t(
                            f"💥 Liquidated SHORT {f['leverage']}x {f['symbol']} @ ${mark}!",
                            f"💥 Thanh ly SHORT {f['leverage']}x {f['symbol']} @ ${mark}!",
                        )
                        self.push_event_banner(
                            self._t(
                                f"LIQUIDATED FUTURES SHORT {f['leverage']}x {f['symbol']}!",
                                f"CHAY LENH FUTURES SHORT {f['leverage']}x {f['symbol']}!",
                            ),
                            self._t(
                                f"Price hit liquidation threshold ${mark} (Lost margin -${f['margin']:,})",
                                f"Gia cham nguong thanh ly ${mark} (Mat von -${f['margin']:,})",
                            ),
                            kind="danger",
                        )
                        continue
                f["roe_pct"] = round(pct * f["leverage"] * 100.0, 2)
                f["pnl"] = round(f["margin"] * (f["roe_pct"] / 100.0), 2)
                surviving.append(f)
            self.futures = surviving

            # Progressive Jackpot pools grow independently for Mega 6/45 and Power 6/55 (JP1 & JP2)
            self.lottery["jackpot_mega645"] += random.randint(180, 650)
            self.lottery["jackpot_power655_jp1"] += random.randint(350, 1100)
            self.lottery["jackpot_power655_jp2"] += random.randint(50, 220)
            self.lottery["jackpot"] = self.lottery["jackpot_mega645"]
            self._write_hud_dat()

    # ========================================================================
    # USER ACTIONS
    # ========================================================================
    def handle_action(self, payload: dict) -> dict:
        with self.lock:
            act = payload.get("action", "")

            if act == "paimon_call":
                self.paimon.call(self, max(1, min(4, int(payload.get("mode", 1)))))

            elif act == "toggle_hud_phone":
                self.phone_open = 0 if self.phone_open == 1 else 1

            elif act == "set_language":
                self._set_language(payload.get("lang", "en"))

            elif act == "toggle_language":
                self._set_language("vi" if self.lang == "en" else "en")

            elif act == "set_phone_app":
                self._open_app(int(payload.get("app", 0)))
                if "subpage" in payload:
                    self.app_subpage[self.phone_app] = int(payload["subpage"])

            elif act in ("navigate_back", "nav_back"):
                self._navigate_back(from_f8=False)

            elif act == "step_subpage":
                target_app = int(payload.get("app", self.phone_app))
                delta = int(payload.get("delta", 1))
                max_subs = {1: 3, 2: 2, 3: 2, 4: 2, 5: 4, 6: 4, 7: 3, 8: 3, 9: 1, 10: len(GG_MAP_CATEGORIES)}.get(target_app, 2)
                cur_sub = self.app_subpage.get(target_app, 0)
                new_sub = (cur_sub + delta) % max_subs
                self.app_subpage[target_app] = new_sub
                if target_app == 6:
                    self.news_sec_idx = new_sub % 4
                elif target_app == 7:
                    self.port_tab_idx = new_sub % 3
                elif target_app == 10:
                    self.ggmap_cat_idx = new_sub % len(GG_MAP_CATEGORIES)
                    self.ggmap_poi_idx = 0
                    self.ggmap_selected_id = None


            elif act == "set_subpage":
                target_app = int(payload.get("app", self.phone_app))
                sub_val = int(payload.get("subpage", 0))
                self.app_subpage[target_app] = sub_val
                if target_app == 6:
                    self.news_sec_idx = sub_val % 4
                elif target_app == 7:
                    self.port_tab_idx = sub_val % 3
                elif target_app == 10:
                    self.ggmap_cat_idx = sub_val % len(GG_MAP_CATEGORIES)
                    self.ggmap_poi_idx = 0
                    self.ggmap_selected_id = None

            elif act == "set_ui_settings":
                if "wp_idx" in payload:
                    self.wp_idx = int(payload["wp_idx"]) % len(WALLPAPER_PRESETS)
                if "mascot_idx" in payload:
                    self.mascot_idx = int(payload["mascot_idx"]) % len(MASCOT_PRESETS)
                if "theme_idx" in payload:
                    self.theme_idx = int(payload["theme_idx"]) % len(THEME_PRESETS)
                if "lang" in payload:
                    self._set_language(payload["lang"])
                self.last_toast = self._t(
                    f"🎨 Theme: {WALLPAPER_PRESETS[self.wp_idx][1]} • "
                    f"Mascot {MASCOT_PRESETS[self.mascot_idx][1]} • {THEME_PRESETS[self.theme_idx][1]}",
                    f"🎨 Giao dien: {WALLPAPER_PRESETS[self.wp_idx][1]} • "
                    f"Mascot {MASCOT_PRESETS[self.mascot_idx][1]} • {THEME_PRESETS[self.theme_idx][1]}",
                )

            elif act == "select_league_page":
                self.selected_league_idx = int(payload.get("league_idx", 0)) % len(LEAGUES)
                self.sport_match_idx = 0

            elif act == "advance_day":
                delta = int(payload.get("delta", 1))
                self._advance_chronological_day(delta)

            elif act == "select_symbol":
                grp = payload.get("market_group", "stocks")
                sym = payload.get("symbol", "")
                if grp == "crypto" and sym in self.crypto_market:
                    self.selected_crypto_sym = sym
                    if payload.get("open_chart"):
                        self.app_subpage[3] = 1
                elif sym in self.stocks_market:
                    self.selected_stock_sym = sym
                    if payload.get("open_chart"):
                        self.app_subpage[2] = 1

            elif act == "eat_meal":
                tier = payload.get("tier", "burger")
                if tier == "burger":
                    if self.modify_cash(-25):
                        self.hunger = min(100, self.hunger + 35)
                        self.modify_health(+25)
                        self.last_toast = self._t(
                            "🍔 Ate Burger (-$25): +35% Fullness & +25 GTA SA HP!",
                            "🍔 Da an Burger (-$25): +35% No & +25 Mau GTA SA!",
                        )
                    else:
                        self.last_toast = self._t(
                            "Not enough $25 GTA SA cash!",
                            "Khong du $25 tien mat GTA SA!",
                        )
                elif tier == "drink":
                    if self.modify_cash(-15):
                        self.energy = min(100, self.energy + 30)
                        self.modify_health(+15)
                        self.last_toast = self._t(
                            "⚡ Drank Energy Drink (-$15): +30% Energy & +15 GTA SA HP!",
                            "⚡ Da uong Tang Luc (-$15): +30% Energy & +15 Mau GTA SA!",
                        )
                    else:
                        self.last_toast = self._t("Not enough $15 cash!", "Khong du $15 tien mat!")

            elif act == "sleep_rest":
                self.energy = 100
                self.modify_health(150, set_full=True)
                self._advance_chronological_day(1)
                self.last_toast = self._t(
                    f"🛏️ Aether slept overnight to {self.current_date.strftime('%d/%m/%Y')}: Full 100% HP & Energy!",
                    f"🛏️ Aether da ngu qua dem sang ngay {self.current_date.strftime('%d/%m/%Y')}: Day 100% Mau & Energy!",
                )

            elif act == "bank_tx":
                d = payload.get("dir", "withdraw")
                amt = max(1, int(payload.get("amount", self.tx_amount)))
                if d == "withdraw":
                    if self.bank >= amt:
                        self.bank -= amt
                        self.modify_cash(+amt)
                        self.last_toast = self._t(
                            f"💵 Withdrew ${amt:,} from ATM to GTA SA Cash!",
                            f"💵 Da rut ${amt:,} tu ATM ra Tien Mat GTA SA!",
                        )
                    else:
                        self.last_toast = self._t(
                            f"Bank balance (${self.bank:,}) is less than ${amt:,}!",
                            f"So du Bank (${self.bank:,}) khong du ${amt:,}!",
                        )
                else:
                    if self.modify_cash(-amt):
                        self.bank += amt
                        self.last_toast = self._t(
                            f"🏦 Deposited ${amt:,} into Bank!",
                            f"🏦 Da nap ${amt:,} vao Bank!",
                        )
                    else:
                        self.last_toast = self._t(
                            f"GTA SA Cash (${self.cash:,}) is less than ${amt:,}!",
                            f"Tien Mat GTA SA (${self.cash:,}) khong du ${amt:,}!",
                        )

            elif act == "savings_tx":
                d = payload.get("dir", "deposit")
                amt = max(1, int(payload.get("amount", self.tx_amount)))
                if d == "deposit":
                    if self.bank >= amt:
                        self.bank -= amt
                        self.savings += amt
                        self.last_toast = self._t(
                            f"📈 Transferred ${amt:,} from Bank to Savings (+1.5%/day)!",
                            f"📈 Da chuyen ${amt:,} tu Bank sang So Tiet Kiem (+1.5%/ngay)!",
                        )
                    elif self.modify_cash(-amt):
                        self.savings += amt
                        self.last_toast = self._t(
                            f"📈 Deposited ${amt:,} Cash into Savings (+1.5%/day)!",
                            f"📈 Da gui ${amt:,} Tien Mat vao So Tiet Kiem (+1.5%/ngay)!",
                        )
                    else:
                        self.last_toast = self._t(
                            f"Not enough ${amt:,} to deposit into Savings!",
                            f"Khong du ${amt:,} de gui Tiet Kiem!",
                        )
                else:
                    if self.savings >= amt:
                        self.savings -= amt
                        self.modify_cash(+amt)
                        self.last_toast = self._t(
                            f"📤 Withdrew ${amt:,} from Savings to GTA SA Cash!",
                            f"📤 Da rut ${amt:,} tu So Tiet Kiem ra Tien Mat GTA SA!",
                        )
                    else:
                        self.last_toast = self._t(
                            f"Savings balance (${self.savings:,}) is less than ${amt:,}!",
                            f"So Tiet Kiem (${self.savings:,}) khong du ${amt:,}!",
                        )

            elif act == "loan_tx":
                d = payload.get("dir", "borrow")
                amt = max(1, int(payload.get("amount", self.tx_amount)))
                if d == "borrow":
                    if self.loan + amt <= 50000:
                        self.loan += amt
                        self.loan_days_left = 3
                        self.loan_overdue = False
                        self.modify_cash(+amt)
                        self.last_toast = self._t(
                            f"💳 Borrowed ${amt:,} (3-day term, 3%/day interest). Cash credited!",
                            f"💳 Da vay ${amt:,} (Han 3 ngay, Lai 3%/ngay). Nhan tien mat ngay!",
                        )
                        self.push_event_banner(
                            self._t(f"LOAN DISBURSED +${amt:,}", f"GIAI NGAN KHOAN VAY +${amt:,}"),
                            self._t(
                                f"Total debt: ${self.loan:,} • Due in: 3 days (3%/day interest)",
                                f"Tong du no: ${self.loan:,} • Han tra: 3 ngay (Lai suat 3%/ngay)",
                            ),
                            kind="warn",
                        )
                    else:
                        self.last_toast = self._t(
                            "Exceeds maximum credit limit of $50,000!",
                            "Vuot han muc vay toi da $50,000!",
                        )
                elif d in ("repay", "repay_all"):
                    pay = self.loan if d == "repay_all" else min(amt, self.loan)
                    if pay <= 0:
                        self.last_toast = self._t("You have no active loan debt!", "Ban khong co khoan no nao!")
                    elif self.modify_cash(-pay):
                        self.loan -= pay
                        if self.loan <= 0:
                            self.loan = 0
                            self.loan_overdue = False
                            self.loan_days_left = 0
                        self.last_toast = self._t(
                            f"✅ Repaid loan ${pay:,}! Remaining debt: ${self.loan:,}",
                            f"✅ Da tra no ${pay:,}! Du no con lai: ${self.loan:,}",
                        )
                        self.push_event_banner(
                            self._t(f"REPAID BANK LOAN -${pay:,}", f"DA TRA NO NGAN HANG -${pay:,}"),
                            self._t(
                                f"Remaining debt: ${self.loan:,} ({'Safe' if self.loan == 0 else 'Active'})",
                                f"Du no con lai: ${self.loan:,} ({'An Toan' if self.loan == 0 else 'Con no'})",
                            ),
                            kind="win",
                        )
                    elif self.bank >= pay:
                        self.bank -= pay
                        self.loan -= pay
                        if self.loan <= 0:
                            self.loan = 0
                            self.loan_overdue = False
                            self.loan_days_left = 0
                        self.last_toast = self._t(
                            f"✅ Paid loan ${pay:,} from Bank! Remaining debt: ${self.loan:,}",
                            f"✅ Da trich Bank tra no ${pay:,}! Du no con: ${self.loan:,}",
                        )
                        self.push_event_banner(
                            self._t(f"REPAID LOAN FROM BANK -${pay:,}", f"DA TRICH BANK TRA NO -${pay:,}"),
                            self._t(f"Remaining debt: ${self.loan:,}", f"Du no con lai: ${self.loan:,}"),
                            kind="win",
                        )
                    else:
                        self.last_toast = self._t(
                            "Not enough Cash or Bank balance to repay loan!",
                            "Khong du tien mat hoac Bank de tra no!",
                        )

            elif act == "trade_order":
                grp = payload.get("market_group", "stocks")
                m_dict = self.crypto_market if grp == "crypto" else self.stocks_market
                sym = payload.get("symbol", "BTC" if grp == "crypto" else "XAU")
                mode = payload.get("mode", "spot_buy")
                usd = max(1.0, float(payload.get("usd", self.tx_amount)))
                lev = int(payload.get("leverage", 10))
                asset = m_dict.get(sym)
                if asset:
                    price = asset["price"]
                    if mode == "spot_buy":
                        if self.modify_cash(-int(usd)):
                            qty = usd / price
                            asset["spot_qty"] += qty
                            asset["spot_cost"] = round(asset.get("spot_cost", 0.0) + float(int(usd)), 2)
                            asset["spot_val"] = round(asset["spot_qty"] * price, 2)
                            asset["spot_pnl"] = round(asset["spot_val"] - asset["spot_cost"], 2)
                            asset["spot_pnl_pct"] = round((asset["spot_pnl"] / asset["spot_cost"]) * 100.0, 2) if asset["spot_cost"] > 0 else 0.0
                            self.last_toast = self._t(
                                f"🛒 Spot BUY {qty:.4f} {sym} @ ${price} (-${int(usd):,})",
                                f"🛒 Mua Spot {qty:.4f} {sym} @ ${price} (-${int(usd):,})",
                            )
                        else:
                            self.last_toast = self._t(
                                f"Not enough ${int(usd):,} GTA SA Cash!",
                                f"Khong du ${int(usd):,} Tien Mat GTA SA!",
                            )
                    elif mode == "spot_sell":
                        if asset["spot_qty"] > 0:
                            sell_val = max(1, int(round(min(usd, asset["spot_val"]))))
                            qty_sold = min(asset["spot_qty"], sell_val / price)
                            ratio = qty_sold / asset["spot_qty"] if asset["spot_qty"] > 0 else 1.0
                            cost_sold = asset.get("spot_cost", 0.0) * ratio
                            realized = sell_val - cost_sold
                            self.portfolio_stats["realized_market_pnl"] = round(
                                self.portfolio_stats["realized_market_pnl"] + realized, 2
                            )
                            asset["spot_qty"] = max(0.0, asset["spot_qty"] - qty_sold)
                            asset["spot_cost"] = round(max(0.0, asset.get("spot_cost", 0.0) - cost_sold), 2) if asset["spot_qty"] > 1e-8 else 0.0
                            if asset["spot_qty"] <= 1e-8:
                                asset["spot_qty"] = 0.0
                            asset["spot_val"] = round(asset["spot_qty"] * price, 2)
                            asset["spot_pnl"] = round(asset["spot_val"] - asset["spot_cost"], 2) if asset["spot_qty"] > 0 else 0.0
                            asset["spot_pnl_pct"] = round((asset["spot_pnl"] / asset["spot_cost"]) * 100.0, 2) if asset["spot_cost"] > 0 and asset["spot_qty"] > 0 else 0.0
                            self.modify_cash(+sell_val)
                            self.last_toast = self._t(
                                f"💰 Spot SELL {qty_sold:.4f} {sym} (+${sell_val:,} | PnL {realized:+.1f}$)",
                                f"💰 Ban Spot {qty_sold:.4f} {sym} (+${sell_val:,} | PnL {realized:+.1f}$)",
                            )
                        else:
                            self.last_toast = self._t(
                                f"No {sym} Spot holdings to sell!",
                                f"Chua nam giu {sym} Spot!",
                            )
                    elif mode in ("fut_long", "fut_short"):
                        margin = int(usd)
                        if self.modify_cash(-margin):
                            side = "LONG" if mode == "fut_long" else "SHORT"
                            liq = price * (1.0 - 0.92 / lev) if side == "LONG" else price * (1.0 + 0.92 / lev)
                            self.futures.insert(0, {
                                "id": f"F{int(time.time()*1000)%100000}",
                                "market_group": grp,
                                "symbol": sym,
                                "side": side,
                                "leverage": lev,
                                "margin": margin,
                                "entry": price,
                                "mark": price,
                                "liq_price": round(liq, asset["decimals"]),
                                "pnl": 0.0,
                                "roe_pct": 0.0,
                            })
                            self.last_toast = self._t(
                                f"🚀 Opened {side} {lev}x {sym} | Margin ${margin:,} | Entry ${price}",
                                f"🚀 Mo {side} {lev}x {sym} | Von ${margin:,} | Entry ${price}",
                            )
                        else:
                            self.last_toast = self._t(
                                f"Not enough ${margin:,} GTA SA Cash!",
                                f"Khong du ${margin:,} Tien Mat GTA SA!",
                            )

            elif act == "close_future":
                fid = payload.get("id", "")
                for idx, f in enumerate(self.futures):
                    if f["id"] == fid:
                        payout = max(0, int(round(f["margin"] + f["pnl"])))
                        self.portfolio_stats["realized_market_pnl"] = round(
                            self.portfolio_stats["realized_market_pnl"] + f["pnl"], 2
                        )
                        self.modify_cash(+payout)
                        self.last_toast = self._t(
                            f"✅ Closed {f['side']} {f['symbol']}: Received ${payout:,} (PnL ${f['pnl']:+.1f})!",
                            f"✅ Dong {f['side']} {f['symbol']}: Nhan ve ${payout:,} (PnL ${f['pnl']:+.1f})!",
                        )
                        self.push_event_banner(
                            self._t(
                                f"CLOSED {f['side']} {f['leverage']}x {f['symbol']}",
                                f"CHOT VI THE {f['side']} {f['leverage']}x {f['symbol']}",
                            ),
                            self._t(
                                f"Credited +${payout:,} to GTA SA Cash (PnL: ${f['pnl']:+.1f} / {f['roe_pct']:+.1f}%)",
                                f"Thu ve +${payout:,} vao Tien Mat GTA SA (PnL: ${f['pnl']:+.1f} / {f['roe_pct']:+.1f}%)",
                            ),
                            kind="win" if f["pnl"] >= 0 else "warn",
                        )
                        self.futures.pop(idx)
                        break

            elif act == "sell_spot_all_one":
                grp = payload.get("market_group", "stocks")
                sym = payload.get("symbol", "")
                m_dict = self.crypto_market if grp == "crypto" else self.stocks_market
                asset = m_dict.get(sym)
                if asset and asset["spot_qty"] > 0:
                    sell_val = max(1, int(round(asset["spot_val"])))
                    realized = sell_val - asset.get("spot_cost", 0.0)
                    self.portfolio_stats["realized_market_pnl"] = round(
                        self.portfolio_stats["realized_market_pnl"] + realized, 2
                    )
                    asset["spot_qty"] = 0.0
                    asset["spot_val"] = 0.0
                    asset["spot_cost"] = 0.0
                    asset["spot_pnl"] = 0.0
                    asset["spot_pnl_pct"] = 0.0
                    self.modify_cash(+sell_val)
                    self.last_toast = self._t(
                        f"💰 Sold all {sym} Spot (+${sell_val:,} | PnL {realized:+.1f}$)",
                        f"💰 Da ban het {sym} Spot (+${sell_val:,} | PnL {realized:+.1f}$)",
                    )
                    self.push_event_banner(
                        self._t(
                            f"SOLD ALL {sym} SPOT: +${sell_val:,}",
                            f"CHOT LOI TOAN BO SPOT {sym}: +${sell_val:,}",
                        ),
                        self._t(
                            f"Realized P&L: {realized:+.1f}$ • Credited to GTA SA Cash!",
                            f"Loi nhuan thuc nhan: {realized:+.1f}$ • Tien da cong vao GTA SA!",
                        ),
                        kind="win" if realized >= 0 else "warn",
                    )

            elif act == "sell_all_spot":
                total_sell = 0
                total_realized = 0.0
                cnt = 0
                for m_dict in (self.stocks_market, self.crypto_market):
                    for a in m_dict.values():
                        if a["spot_qty"] > 0 and a["spot_val"] >= 1:
                            val = int(round(a["spot_val"]))
                            realized = val - a.get("spot_cost", 0.0)
                            total_sell += val
                            total_realized += realized
                            cnt += 1
                            a["spot_qty"] = 0.0
                            a["spot_val"] = 0.0
                            a["spot_cost"] = 0.0
                            a["spot_pnl"] = 0.0
                            a["spot_pnl_pct"] = 0.0
                if cnt > 0:
                    self.portfolio_stats["realized_market_pnl"] = round(
                        self.portfolio_stats["realized_market_pnl"] + total_realized, 2
                    )
                    self.modify_cash(+total_sell)
                    self.last_toast = self._t(
                        f"💰 Sold all {cnt} Spot assets (+${total_sell:,} | PnL {total_realized:+.1f}$)",
                        f"💰 Da ban het {cnt} ma Spot (+${total_sell:,} | PnL {total_realized:+.1f}$)",
                    )
                    self.push_event_banner(
                        self._t(
                            f"SOLD ENTIRE SPOT PORTFOLIO ({cnt} ASSETS): +${total_sell:,}",
                            f"CHOT TOAN BO DANH MUC SPOT ({cnt} MA): +${total_sell:,}",
                        ),
                        self._t(
                            f"Total realized P&L: {total_realized:+.1f}$ • Credited directly to GTA SA Cash!",
                            f"Tong PnL thuc nhan: {total_realized:+.1f}$ • Da cong thang vao Tien Mat GTA SA!",
                        ),
                        kind="win" if total_realized >= 0 else "warn",
                    )
                else:
                    self.last_toast = self._t("Spot portfolio is empty!", "Danh muc Spot dang trong!")

            elif act == "close_all_futures":
                if self.futures:
                    cnt = len(self.futures)
                    total_payout = 0
                    total_pnl = 0.0
                    for f in self.futures:
                        total_payout += max(0, int(round(f["margin"] + f["pnl"])))
                        total_pnl += f["pnl"]
                    self.futures = []
                    self.portfolio_stats["realized_market_pnl"] = round(
                        self.portfolio_stats["realized_market_pnl"] + total_pnl, 2
                    )
                    self.modify_cash(+total_payout)
                    self.last_toast = self._t(
                        f"✅ Closed all {cnt} Futures positions (+${total_payout:,} | PnL {total_pnl:+.1f}$)",
                        f"✅ Da dong tat ca {cnt} vi the Futures (+${total_payout:,} | PnL {total_pnl:+.1f}$)",
                    )
                    self.push_event_banner(
                        self._t(
                            f"CLOSED ALL {cnt} FUTURES POSITIONS: +${total_payout:,}",
                            f"DONG TOAN BO {cnt} VI THE FUTURES: +${total_payout:,}",
                        ),
                        self._t(
                            f"Total Futures P&L: {total_pnl:+.1f}$ • Credited to GTA SA Cash!",
                            f"Tong PnL Futures: {total_pnl:+.1f}$ • Tien da cong vao GTA SA!",
                        ),
                        kind="win" if total_pnl >= 0 else "warn",
                    )
                else:
                    self.last_toast = self._t("No open Futures positions!", "Khong co vi the Futures nao dang mo!")

            elif act == "settle_all_portfolio":
                active_bet_indices = [idx for idx, m in enumerate(self.fixtures) if m.get("active_bet")]
                for idx in reversed(active_bet_indices):
                    self._resolve_fixture(idx, replace=True)
                had_tickets = len(self.lottery["tickets"]) > 0
                if had_tickets:
                    self._run_lottery_draw(filter_type="ALL")
                if not active_bet_indices and not had_tickets:
                    self.last_toast = self._t(
                        "No pending Sports Bets or Lottery Tickets!",
                        "Khong co keo Bet hoac Ve So nao dang cho!",
                    )

            elif act == "place_bet":
                mid = payload.get("match_id", "")
                pick = payload.get("pick", "HOME")
                stake = max(1, int(payload.get("stake", self.tx_amount)))
                label = payload.get("label", pick)
                for m in self.fixtures:
                    if m["id"] == mid:
                        if self.modify_cash(-stake):
                            odd = m["odds"][0] if pick == "HOME" else (m["odds"][1] if pick == "DRAW" else (m["odds"][2] if pick == "AWAY" else 1.90))
                            m["active_bet"] = {"pick": pick, "stake": stake, "odd": odd, "label": label}
                            self.last_toast = self._t(
                                f"⚽ Placed ${stake:,} bet on [{label}] ({odd}x) for {m['home']} vs {m['away']}!",
                                f"⚽ Da cuoc ${stake:,} vao [{label}] ({odd}x) tran {m['home']} vs {m['away']}!",
                            )
                        else:
                            self.last_toast = self._t(
                                f"Not enough ${stake:,} GTA SA Cash!",
                                f"Khong du ${stake:,} Tien Mat GTA SA!",
                            )
                        break

            elif act == "sim_one_match":
                mid = payload.get("match_id", "")
                for idx, m in enumerate(self.fixtures):
                    if m["id"] == mid:
                        self._resolve_fixture(idx, replace=True)
                        break

            elif act == "sim_league_matches":
                lid = payload.get("league_id", LEAGUES[self.selected_league_idx % len(LEAGUES)]["id"])
                for idx in range(len(self.fixtures) - 1, -1, -1):
                    if self.fixtures[idx]["league_id"] == lid:
                        self._resolve_fixture(idx, replace=True)

            elif act == "sim_all_matches":
                for idx in range(len(self.fixtures) - 1, -1, -1):
                    self._resolve_fixture(idx, replace=True)

            elif act == "buy_scratch":
                tier_key = payload.get("tier", "SILVER_20")
                combo = max(1, min(10, int(payload.get("combo", 1))))
                cfg = SCRATCH_CARD_TYPES.get(tier_key, SCRATCH_CARD_TYPES["SILVER_20"])
                card_name = cfg.get("name_vi", cfg["name"]) if self._is_vi() else cfg["name"]
                outcomes_list = cfg.get("outcomes_vi", cfg["outcomes"]) if self._is_vi() else cfg["outcomes"]
                total_cost = cfg["cost"] * combo
                if self.modify_cash(-total_cost):
                    self.portfolio_stats["lotto_spent"] += total_cost
                    total_prize = 0
                    last_msg = self._t("Better luck next time!", "Chuc ban may man lan sau!")
                    last_cells = []
                    symbols = ["$20", "$40", "$100", "$250", "★", "💎", "👑"]
                    for _ in range(combo):
                        r = random.random()
                        acc = 0.0
                        prize, msg_text = 0, self._t("Better luck next time!", "Chuc ban may man lan sau!")
                        for prob, p_val, p_msg in outcomes_list:
                            acc += prob
                            if r <= acc:
                                prize, msg_text = p_val, p_msg
                                break
                        cells = [random.choice(symbols) for _ in range(9)]
                        if prize > 0:
                            for pos in random.sample(range(9), 3):
                                cells[pos] = f"${prize}"
                            total_prize += prize
                            last_msg = msg_text
                        last_cells = cells
                    if total_prize > 0:
                        self.modify_cash(+total_prize)
                        self.portfolio_stats["lotto_won"] += total_prize
                        self.push_event_banner(
                            self._t(
                                f"SCRATCH CARD WIN {card_name.upper()}: +${total_prize:,}!",
                                f"TRUNG VE CAO {card_name.upper()}: +${total_prize:,}!",
                            ),
                            self._t(
                                f"Scratched {combo} card(s) (-${total_cost:,}) • Prize +${total_prize:,} added to GTA SA Cash!",
                                f"Cao {combo} ve (-${total_cost:,}) • Tien thuong +${total_prize:,} cong thang vao GTA SA!",
                            ),
                            kind="win",
                        )
                        if combo > 1:
                            last_msg = self._t(
                                f"{combo}-Card Combo: Won total +${total_prize:,}! ({last_msg})",
                                f"Combo {combo} ve: Trung tong +${total_prize:,}! ({last_msg})",
                            )
                    elif combo > 1:
                        last_msg = self._t(
                            f"Scratched {combo}-Card Combo (-${total_cost:,}): No prize this time, try again!",
                            f"Da cao Combo {combo} ve (-${total_cost:,}): Chua trung giai, thu lai nhe!",
                        )
                    self.portfolio_stats["lotto_net_pnl"] = (
                        self.portfolio_stats["lotto_won"] - self.portfolio_stats["lotto_spent"]
                    )
                    self.lottery["scratch_cells"] = last_cells
                    self.lottery["last_scratch_msg"] = f"{card_name}: {last_msg}"
                    self.last_toast = f"🎫 {card_name}: {last_msg}"
                else:
                    self.last_toast = self._t(
                        f"Not enough ${total_cost:,} GTA SA Cash!",
                        f"Khong du ${total_cost:,} Tien Mat GTA SA!",
                    )

            elif act == "buy_lotto_6d":
                mode = payload.get("mode", "XSKT_6D")
                raw = "".join(ch for ch in str(payload.get("number", self.custom_lotto_str)) if ch.isdigit())[:6]
                if len(raw) != 6:
                    raw = f"{random.randint(0, 999999):06d}"
                self.custom_lotto_str = raw
                if mode == "XSKT_6D":
                    cost = 10
                    num_pick = raw
                    mode_lbl = self._t(f"6-Digit Classic Ticket [{num_pick}]", f"Ve Kien Thiet 6 So [{num_pick}]")
                elif mode == "LODE_DE":
                    cost = max(10, int(payload.get("stake", self.tx_amount)))
                    num_pick = raw[-2:]
                    mode_lbl = self._t(f"Last 2 Digits Grand Prize [{num_pick}] (x70)", f"Danh De 2 So Cuoi [{num_pick}] (x70)")
                elif mode == "LODE_LO2":
                    cost = max(10, int(payload.get("stake", self.tx_amount)))
                    num_pick = raw[-2:]
                    mode_lbl = self._t(f"2-Digit 18-Roll Lotto [{num_pick}] (x3.5/hit)", f"Bao Lo 2 So [{num_pick}] (18 Giai, x3.5/nhay)")
                else:  # LODE_3CANG
                    cost = max(10, int(payload.get("stake", self.tx_amount)))
                    num_pick = raw[-3:]
                    mode_lbl = self._t(f"Last 3 Digits Grand Prize [{num_pick}] (x400)", f"3 Cang Dac Biet [{num_pick}] (x400)")

                if self.modify_cash(-cost):
                    self.portfolio_stats["lotto_spent"] += cost
                    self.portfolio_stats["lotto_net_pnl"] = (
                        self.portfolio_stats["lotto_won"] - self.portfolio_stats["lotto_spent"]
                    )
                    self.lottery["tickets"].append({"type": mode, "numbers": num_pick, "cost": cost})
                    self.last_toast = self._t(
                        f"🔢 Bought {mode_lbl} (-${cost:,}, 16:30 Daily Draw)!",
                        f"🔢 Da mua {mode_lbl} (-${cost:,}, Mo thuong XSKT 16:30)!",
                    )
                else:
                    self.last_toast = self._t(
                        f"Not enough ${cost:,} GTA SA Cash!",
                        f"Khong du ${cost:,} Tien Mat GTA SA!",
                    )

            elif act == "buy_vietlott":
                game = payload.get("game", "MEGA_645")
                max_n = 45 if game in ("MEGA_645", "MEGA_BAO7") else 55
                cnt_n = 7 if game in ("MEGA_BAO7", "POWER_BAO7") else 6
                cost = 70 if cnt_n == 7 else 10
                raw = str(payload.get("numbers", "")).strip()
                nums = []
                for p in raw.replace("-", " ").replace(",", " ").split():
                    if p.isdigit():
                        v = int(p)
                        if 1 <= v <= max_n and v not in nums:
                            nums.append(v)
                pool = [x for x in range(1, max_n + 1) if x not in nums]
                while len(nums) < cnt_n and pool:
                    pick = random.choice(pool)
                    pool.remove(pick)
                    nums.append(pick)
                nums = sorted(nums[:cnt_n])
                num_str = " ".join(f"{x:02d}" for x in nums)
                self.custom_vietlott_str = num_str
                if self.modify_cash(-cost):
                    self.portfolio_stats["lotto_spent"] += cost
                    self.portfolio_stats["lotto_net_pnl"] = (
                        self.portfolio_stats["lotto_won"] - self.portfolio_stats["lotto_spent"]
                    )
                    # Add ticket contribution to the respective progressive prize pool!
                    if game in ("MEGA_645", "MEGA_BAO7"):
                        self.lottery["jackpot_mega645"] += cost * 50
                        self.lottery["jackpot"] = self.lottery["jackpot_mega645"]
                    else:
                        self.lottery["jackpot_power655_jp1"] += cost * 60
                        self.lottery["jackpot_power655_jp2"] += cost * 15
                    self.lottery["tickets"].append({"type": game, "numbers": num_str, "cost": cost})
                    self.last_toast = self._t(
                        f"💎 Bought Vietlott {game} [{num_str.replace(' ', '-')}] (-${cost}, Draw 18:00)!",
                        f"💎 Da mua Vietlott {game} [{num_str.replace(' ', '-')}] (-${cost}, Quay 18:00)!",
                    )
                else:
                    self.last_toast = self._t(
                        f"Not enough ${cost} GTA SA Cash!",
                        f"Khong du ${cost} Tien Mat GTA SA!",
                    )

            elif act == "play_keno":
                mode = payload.get("mode", "KENO_TAI")
                stake = max(10, int(payload.get("stake", self.tx_amount)))
                if not self.modify_cash(-stake):
                    self.last_toast = self._t(
                        f"Not enough ${stake:,} Cash to play Keno/Max3D!",
                        f"Khong du ${stake:,} Tien Mat de quay Keno/Max3D!",
                    )
                else:
                    self.portfolio_stats["lotto_spent"] += stake
                    keno_20 = sorted(random.sample(range(1, 81), 20))
                    total_pts = sum(keno_20)
                    even_cnt = sum(1 for x in keno_20 if x % 2 == 0)
                    odd_cnt = 20 - even_cnt
                    tai_xiu = self._t("BIG", "TAI") if total_pts > 810 else self._t("SMALL", "XIU")
                    if total_pts <= 695:
                        ngu_hanh = self._t("METAL", "KIM")
                        ngu_hanh_code = "KIM"
                    elif total_pts <= 763:
                        ngu_hanh = self._t("WOOD", "MOC")
                        ngu_hanh_code = "MOC"
                    elif total_pts <= 855:
                        ngu_hanh = self._t("WATER", "THUY")
                        ngu_hanh_code = "THUY"
                    elif total_pts <= 923:
                        ngu_hanh = self._t("FIRE", "HOA")
                        ngu_hanh_code = "HOA"
                    else:
                        ngu_hanh = self._t("EARTH", "THO")
                        ngu_hanh_code = "THO"

                    m3d_a = f"{random.randint(0, 999):03d}"
                    m3d_b = f"{random.randint(0, 999):03d}"

                    payout = 0
                    win_desc = ""
                    if mode == "KENO_TAI" and total_pts > 810:
                        payout = int(round(stake * 2.0))
                        win_desc = self._t(
                            f"Won Keno BIG ({total_pts}pts > 810pts, x2.0)",
                            f"Trung Keno TAI ({total_pts}d > 810d, x2.0)",
                        )
                    elif mode == "KENO_XIU" and total_pts <= 810:
                        payout = int(round(stake * 2.0))
                        win_desc = self._t(
                            f"Won Keno SMALL ({total_pts}pts <= 810pts, x2.0)",
                            f"Trung Keno XIU ({total_pts}d <= 810d, x2.0)",
                        )
                    elif mode == "KENO_CHAN" and even_cnt >= 11:
                        payout = int(round(stake * 2.2))
                        win_desc = self._t(
                            f"Won Keno EVEN ({even_cnt} Even balls, x2.2)",
                            f"Trung Keno CHAN ({even_cnt} bong Chan, x2.2)",
                        )
                    elif mode == "KENO_LE" and odd_cnt >= 11:
                        payout = int(round(stake * 2.2))
                        win_desc = self._t(
                            f"Won Keno ODD ({odd_cnt} Odd balls, x2.2)",
                            f"Trung Keno LE ({odd_cnt} bong Le, x2.2)",
                        )
                    elif mode == "KENO_NGUHANH" and ngu_hanh_code in ("KIM", "HOA", "THUY"):
                        payout = int(round(stake * 4.5))
                        win_desc = self._t(
                            f"Won Keno Element [{ngu_hanh}] (Total {total_pts}pts, x4.5)",
                            f"Trung Keno Ngu Hanh [{ngu_hanh}] (Tong {total_pts}d, x4.5)",
                        )
                    elif mode == "KENO_BAC3":
                        raw_d = "".join(ch for ch in str(payload.get("numbers", self.custom_lotto_str)) if ch.isdigit()).zfill(6)
                        p3 = {
                            max(1, min(80, int(raw_d[0:2]) or 7)),
                            max(1, min(80, int(raw_d[2:4]) or 28)),
                            max(1, min(80, int(raw_d[4:6]) or 68)),
                        }
                        while len(p3) < 3:
                            p3.add(random.randint(1, 80))
                        hits = len(p3.intersection(keno_20))
                        if hits == 3:
                            payout = int(round(stake * 40.0))
                            win_desc = self._t(
                                f"Won Keno Pick-3 (3/3 balls {sorted(p3)}, x40)",
                                f"Trung Keno Bac 3 (3/3 so {sorted(p3)}, x40)",
                            )
                        elif hits == 2:
                            payout = int(round(stake * 2.5))
                            win_desc = self._t(
                                f"Won Keno Pick-3 (2/3 balls {sorted(p3)}, x2.5)",
                                f"Trung Keno Bac 3 (2/3 so {sorted(p3)}, x2.5)",
                            )
                    elif mode == "MAX3D_PRO":
                        my_3d = str(payload.get("numbers", self.custom_lotto_str)).zfill(6)
                        p_a, p_b = my_3d[:3], my_3d[3:6]
                        if (p_a == m3d_a and p_b == m3d_b) or (p_a == m3d_b and p_b == m3d_a):
                            payout = int(round(stake * 400.0))
                            win_desc = self._t(
                                f"MEGA WIN MAX 3D PRO [{m3d_a}+{m3d_b}] (x400)!",
                                f"SIEU TRUNG MAX 3D PRO [{m3d_a}+{m3d_b}] (x400)!",
                            )
                        elif p_a in (m3d_a, m3d_b) or p_b in (m3d_a, m3d_b):
                            payout = int(round(stake * 15.0))
                            win_desc = self._t(
                                f"Matched 1 Max 3D Trio [{m3d_a}+{m3d_b}] (x15)!",
                                f"Trung 1 bo 3 so Max 3D [{m3d_a}+{m3d_b}] (x15)!",
                            )
                        elif p_a[-2:] in (m3d_a[-2:], m3d_b[-2:]) or p_b[-2:] in (m3d_a[-2:], m3d_b[-2:]):
                            payout = int(round(stake * 3.0))
                            win_desc = self._t(
                                f"Matched Last 2 Digits Max 3D [{m3d_a}+{m3d_b}] (x3.0)!",
                                f"Trung 2 so cuoi Max 3D [{m3d_a}+{m3d_b}] (x3.0)!",
                            )

                    self.lottery["last_keno_balls"] = "-".join(f"{x:02d}" for x in keno_20[:10])
                    self.lottery["last_keno_meta"] = self._t(
                        f"Sum 20 balls: {total_pts}pts ({tai_xiu}) | {even_cnt}E-{odd_cnt}O | "
                        f"Elem: {ngu_hanh} | Max3D: {m3d_a}+{m3d_b}",
                        f"Tong 20 bong: {total_pts}d ({tai_xiu}) | {even_cnt}C-{odd_cnt}L | "
                        f"Hanh: {ngu_hanh} | Max3D: {m3d_a}+{m3d_b}",
                    )
                    if payout > 0:
                        self.modify_cash(+payout)
                        self.portfolio_stats["lotto_won"] += payout
                        self.lottery["last_keno_msg"] = self._t(
                            f"WON +${payout:,}! {win_desc}",
                            f"THANG +${payout:,}! {win_desc}",
                        )
                        self.last_toast = self._t(
                            f"⚡ {win_desc}: Instant payout +${payout:,}!",
                            f"⚡ {win_desc}: Nhan ngay +${payout:,}!",
                        )
                        self.push_event_banner(
                            self._t(
                                f"KENO / MAX 3D EXPRESS WIN: +${payout:,}!",
                                f"THANG KENO / MAX 3D QUAY NHANH: +${payout:,}!",
                            ),
                            f"{win_desc} • {self.lottery['last_keno_meta']}",
                            kind="win",
                            duration=6.5,
                        )
                    else:
                        self.lottery["last_keno_msg"] = self._t(
                            f"No win (-${stake:,}) • Draw: {total_pts}pts ({tai_xiu}), {even_cnt}E-{odd_cnt}O, {ngu_hanh}",
                            f"Chua trung (-${stake:,}) • KQ: {total_pts}d ({tai_xiu}), {even_cnt}C-{odd_cnt}L, {ngu_hanh}",
                        )
                        self.last_toast = self._t(
                            f"⚡ Keno Draw: {total_pts}pts ({tai_xiu}) | {even_cnt}E-{odd_cnt}O | {ngu_hanh} (No match)",
                            f"⚡ KQ Keno: {total_pts}d ({tai_xiu}) | {even_cnt}C-{odd_cnt}L | {ngu_hanh} (Chua trung)",
                        )
                    self.portfolio_stats["lotto_net_pnl"] = (
                        self.portfolio_stats["lotto_won"] - self.portfolio_stats["lotto_spent"]
                    )

            elif act == "draw_lottery_now":
                ftype = payload.get("filter_type")
                if not ftype:
                    sub5 = self.app_subpage.get(5, 0)
                    if sub5 == 1:
                        ftype = "XSKT_6D"
                    elif sub5 == 2:
                        ftype = "VIETLOTT"
                    else:
                        ftype = "ALL"
                self._run_lottery_draw(filter_type=ftype)


            elif act == "set_bug_category":
                bug_cats = self._get_bug_categories()
                if "idx" in payload:
                    self.bug_cat_idx = int(payload["idx"]) % len(bug_cats)
                elif "category" in payload:
                    code = str(payload["category"])
                    for idx_c, (c_code, _) in enumerate(bug_cats):
                        if c_code == code:
                            self.bug_cat_idx = idx_c
                            break
                _, cat_lbl = bug_cats[self.bug_cat_idx]
                self.last_toast = self._t(f"Selected bug category: {cat_lbl}", f"Đã chọn loại lỗi: {cat_lbl}")

            elif act == "set_unstuck_mode":
                u_modes = self._get_unstuck_modes()
                if "idx" in payload:
                    self.unstuck_mode_idx = int(payload["idx"]) % len(u_modes)
                elif "mode" in payload:
                    m_code = str(payload["mode"])
                    for idx_m, (k_mode, _) in enumerate(u_modes):
                        if k_mode == m_code:
                            self.unstuck_mode_idx = idx_m
                            break
                _, mode_lbl = u_modes[self.unstuck_mode_idx]
                self.last_toast = self._t(f"Quick Rescue Mode: {mode_lbl}", f"Chế độ Cứu Hộ Nhanh: {mode_lbl}")

            elif act == "inspect_live_coords":
                custom_pos = payload.get("custom_pos")
                if isinstance(custom_pos, (list, tuple)) and len(custom_pos) >= 3:
                    self.player_pos = (float(custom_pos[0]), float(custom_pos[1]), float(custom_pos[2]))
                self._refresh_live_scan()

            elif act == "unstuck_player":
                mode_key = payload.get("mode")
                self._perform_unstuck(mode_key=mode_key)

            elif act in ("toggle_debug_mode", "set_debug_mode"):
                if act == "set_debug_mode" and "mode" in payload:
                    new_m = self.debug_sys.set_mode(payload["mode"], engine=self)
                else:
                    new_m = self.debug_sys.toggle_mode(engine=self)
                if new_m == "deep":
                    self.last_toast = self._t(
                        "🔬 DEEP DEBUG ENABLED: Live Pools, Streaming RAM & Thrashing Profiler active!",
                        "🔬 DA BAT DEEP DEBUG: Dang giam sat truc tiep Pool RAM, Streaming & Thrashing!",
                    )
                else:
                    self.last_toast = self._t(
                        "🛡️ Switched to LITE Mode (0% Game Overhead — Only Bug Report & Crash Guard active)",
                        "🛡️ Da chuyen ve Che do LITE (0% Anh huong FPS — Chi bat Bao Bug & Bat Crash Ngam)",
                    )

            elif act == "run_preflight_doctor":
                rep = self.debug_sys.run_preflight_doctor(engine=self)
                self.last_toast = f"🩺 {rep['summary']}"
                self.push_event_banner(
                    self._t(f"PRE-FLIGHT DOCTOR: {rep['status']}", f"KIEM TOAN DOCTOR: {rep['status']}"),
                    rep["summary"],
                    kind="win" if rep["failed"] == 0 else "danger",
                    duration=5.5,
                )

            elif act == "analyze_latest_crash":
                self.debug_sys._known_crash_files.clear()
                crep = self.debug_sys.check_for_new_crashes(triggered_by_detach=True)
                if crep:
                    cd = crep["crash_dump"]
                    self.last_toast = f"💥 {cd['file']}: {cd['category']} ({cd['exception_addr']} in {cd['exception_module']})"
                    self.push_event_banner(
                        f"CRASH AUDIT: {cd['category']}",
                        f"{cd['file']} -> {cd['exception_addr']} in {cd['exception_module']} (Last: {cd['last_file_loaded']})",
                        kind="info" if cd.get("is_exit_crash") else "danger",
                        duration=6.5,
                    )
                else:
                    self.last_toast = self._t("No crash logs found in ProjectEagle_crashes/", "Khong co log crash nao")

            elif act == "cycle_probe_suite":
                suites = self.debug_sys.get_probe_suites(is_vi=self._is_vi())
                delta = int(payload.get("delta", 1))
                self.debug_sys.probe_suite_idx = (self.debug_sys.probe_suite_idx + delta) % len(suites)
                _, s_lbl, _ = suites[self.debug_sys.probe_suite_idx]
                self.last_toast = f"🧪 Auto-Probe Suite: {s_lbl}"

            elif act in ("toggle_auto_probe", "start_auto_probe", "stop_auto_probe"):
                if act == "stop_auto_probe" or (act == "toggle_auto_probe" and self.debug_sys.probe_active):
                    self.debug_sys.stop_auto_probe(self, reason="Stopped by user")
                else:
                    suite_c = payload.get("suite")
                    self.debug_sys.start_auto_probe(self, suite_code=suite_c)

            elif act == "capture_forensic_snapshot":
                tag = str(payload.get("tag", "WEB_SNAPSHOT"))
                note = str(payload.get("note", ""))
                snap = self.debug_sys.ingame_tester.capture_forensic_snapshot(self, tag=tag, note=note)
                ch = snap.get("crosshair_target")
                ch_str = f"{ch['dff_name']}.dff (ID {ch['model_id']}, {ch['dist_m']}m)" if ch else "No crosshair hit"
                self.last_toast = f"📸 Snapshot {snap['snapshot_id']}: LookAt={ch_str}"
                self.push_event_banner("FORENSIC SNAPSHOT & X-RAY SAVED", f"{snap['snapshot_id']} • {ch_str}", kind="win", duration=5.5)

            elif act == "audit_live_scene":
                coords = payload.get("coords")
                t_xyz = tuple(float(x) for x in coords[:3]) if isinstance(coords, (list, tuple)) and len(coords) >= 3 else None
                rad = float(payload.get("radius", 55.0))
                rep = self.debug_sys.ingame_tester.audit_live_scene_ram(self, target_coords=t_xyz, radius=rad)
                self.last_toast = f"🔬 {rep.get('summary', rep.get('message', 'Scene Audit done'))}"
                if rep.get("ok"):
                    self.push_event_banner(
                        f"LIVE RAM SCENE AUDIT: {rep['status']}",
                        rep["summary"],
                        kind="win" if rep["anomalies_count"] == 0 else "warn",
                        duration=5.5,
                    )

            elif act == "run_route_crawler":
                suite_c = str(payload.get("suite", "WIBU01_BRIDGE_SEAM"))
                def _crawl_bg():
                    rep = self.debug_sys.ingame_tester.run_route_crawler(self, suite_or_coords=suite_c)
                    self.last_toast = f"🤖 {rep.get('summary', rep.get('message', 'Crawler finished'))}"
                    if rep.get("ok"):
                        self.push_event_banner(f"ROUTE CRAWLER: {rep['status']}", rep["summary"], kind="win" if rep["status"] == "PASS" else "danger", duration=6.0)
                    self._write_hud_dat(force=True)
                threading.Thread(target=_crawl_bg, daemon=True).start()
                self.last_toast = f"🤖 Started In-Game Bot Route Crawler ({suite_c})... Press F12 to abort"

            elif act == "run_aether_test":
                def _aether_bg():
                    rep = self.debug_sys.ingame_tester.run_aether_action_test(self)
                    self.last_toast = f"⚔️ {rep.get('summary', rep.get('message', 'Aether test finished'))}"
                    if rep.get("ok"):
                        self.push_event_banner(f"AETHER RIG TEST: {rep['status']}", rep["summary"], kind="win" if rep["status"] == "PASS" else "warn", duration=6.0)
                    self._write_hud_dat(force=True)
                threading.Thread(target=_aether_bg, daemon=True).start()
                self.last_toast = "⚔️ Running 6-Step Aether Rig & Action Verification in-game..."

            elif act == "run_visual_contact_sheet":
                suite_c = str(payload.get("suite", "WIBU01_TOUR"))
                def _sheet_bg():
                    rep = self.debug_sys.ingame_tester.run_visual_contact_sheet(self, suite_code=suite_c)
                    self.last_toast = f"🖼️ {rep.get('summary', rep.get('message', 'Contact sheet done'))}"
                    if rep.get("ok"):
                        self.push_event_banner("VISUAL CONTACT SHEET READY", rep["summary"], kind="win", duration=6.0)
                    self._write_hud_dat(force=True)
                threading.Thread(target=_sheet_bg, daemon=True).start()
                self.last_toast = f"🖼️ Generating In-Game Visual Contact Sheet ({suite_c})..."

            elif act == "inspect_npcs":
                raw_ids = payload.get("ped_ids")
                ped_ids = [int(x) for x in raw_ids] if isinstance(raw_ids, list) else None
                rep = self.debug_sys.ingame_tester.inspect_npc_models(self, ped_ids=ped_ids)
                self.last_toast = f"👥 {rep.get('summary', 'NPC Inspection done')}"
                self.push_event_banner("NPC ARCHIVE & RAM AUDIT", rep["summary"], kind="info", duration=5.5)

            elif act == "report_map_bug":
                custom_pos = payload.get("custom_pos")
                if isinstance(custom_pos, (list, tuple)) and len(custom_pos) >= 3:
                    self.player_pos = (float(custom_pos[0]), float(custom_pos[1]), float(custom_pos[2]))
                if "velocity" in payload and isinstance(payload["velocity"], (list, tuple)) and len(payload["velocity"]) >= 3:
                    v = payload["velocity"]
                    self.player_velocity = (float(v[0]), float(v[1]), float(v[2]))
                if "area_code" in payload:
                    self.player_area_code = int(payload["area_code"])
                if "game_area" in payload:
                    self.player_game_area = int(payload["game_area"])
                cat_code = payload.get("category") or payload.get("category_code")
                bug_cats = self._get_bug_categories()
                if cat_code:
                    for idx_c, (c_code, _) in enumerate(bug_cats):
                        if c_code == cat_code:
                            self.bug_cat_idx = idx_c
                            break
                note = str(payload.get("note", "")).strip()
                auto_rescue = bool(payload.get("auto_rescue", True))
                self.trigger_bug_report(category_code=cat_code, note=note, auto_rescue_if_falling=auto_rescue)

            elif act == "set_ggmap_category":
                gg_cats = self._get_ggmap_categories()
                if "cat_idx" in payload:
                    self.ggmap_cat_idx = int(payload["cat_idx"]) % len(gg_cats)
                elif "idx" in payload:
                    self.ggmap_cat_idx = int(payload["idx"]) % len(gg_cats)
                elif "cat_code" in payload:
                    code = str(payload["cat_code"])
                    for idx_g, entry in enumerate(gg_cats):
                        if entry[0] == code:
                            self.ggmap_cat_idx = idx_g
                            break
                self.app_subpage[10] = self.ggmap_cat_idx
                self.ggmap_poi_idx = 0
                self.ggmap_selected_id = None
                pois = self._get_active_ggmap_pois()
                cat_lbl = gg_cats[self.ggmap_cat_idx][1]
                self.last_toast = self._t(
                    f"🗺️ GG Map [{cat_lbl}]: {len(pois)} destinations",
                    f"🗺️ GG Map [{cat_lbl}]: {len(pois)} điểm đến",
                )

            elif act == "select_ggmap_poi":
                poi_id = str(payload.get("poi_id", "")).strip()
                pois = self._get_active_ggmap_pois()
                if poi_id:
                    for idx_p, p in enumerate(pois):
                        if p["id"] == poi_id:
                            self.ggmap_poi_idx = idx_p
                            self.ggmap_selected_id = poi_id
                            break
                elif "idx" in payload and pois:
                    self.ggmap_poi_idx = int(payload["idx"]) % len(pois)
                    self.ggmap_selected_id = pois[self.ggmap_poi_idx]["id"]

            elif act == "set_gps_waypoint":
                poi_id = str(payload.get("poi_id", "")).strip()
                target_poi = None
                if poi_id:
                    all_pois = get_pois_for_category("ALL", self.player_pos, lang=self.lang)
                    for p in all_pois:
                        if p["id"] == poi_id:
                            target_poi = dict(p)
                            self.ggmap_selected_id = poi_id
                            break
                if target_poi is None and "x" in payload and "y" in payload:
                    target_poi = {
                        "id": "CUSTOM_GPS",
                        "cat": payload.get("cat", "LANDMARKS"),
                        "name": str(payload.get("name", self._t("Custom Waypoint", "Điểm Hẹn Tùy Chọn"))),
                        "region": str(payload.get("region", "San Andreas")),
                        "x": float(payload["x"]),
                        "y": float(payload["y"]),
                        "z": float(payload.get("z", 15.0)),
                        "area_code": int(payload.get("area_code", 0)),
                        "note": str(payload.get("note", self._t("Custom coordinate marker", "Mốc tọa độ tùy chỉnh"))),
                    }
                if target_poi is None:
                    pois = self._get_active_ggmap_pois()
                    if pois:
                        target_poi = pois[self.ggmap_poi_idx % len(pois)]
                if target_poi:
                    self._set_gps_waypoint_to_poi(target_poi)

            elif act == "clear_gps_waypoint":
                self._clear_gps_waypoint(arrived=False)

            elif act == "teleport_ggmap_poi":
                poi_id = str(payload.get("poi_id", "")).strip()
                target_poi = None
                if poi_id:
                    all_pois = get_pois_for_category("ALL", self.player_pos, lang=self.lang)
                    for p in all_pois:
                        if p["id"] == poi_id:
                            target_poi = dict(p)
                            self.ggmap_selected_id = poi_id
                            break
                if target_poi is None:
                    pois = self._get_active_ggmap_pois()
                    if pois:
                        target_poi = pois[self.ggmap_poi_idx % len(pois)]
                if target_poi:
                    tx, ty, tz = float(target_poi["x"]), float(target_poi["y"]), float(target_poi["z"])
                    t_area = int(target_poi.get("area_code", 0))
                    tele_ok = False
                    if self.bridge.try_attach():
                        tele_ok = self.bridge.teleport_player(tx, ty, tz, area_code=t_area)
                    self.player_pos = (tx, ty, tz)
                    self.player_velocity = (0.0, 0.0, 0.0)
                    self.player_area_code = t_area
                    self.last_toast = self._t(
                        f"⚡ Teleported to {target_poi['name']} ({target_poi['region']}) [{'RAM OK' if tele_ok else 'Sim OK'}]",
                        f"⚡ Dịch chuyển tới {target_poi['name']} ({target_poi['region']}) [{'RAM OK' if tele_ok else 'Sim OK'}]",
                    )
                    self.push_event_banner(
                        self._t(
                            f"FAST TRAVEL: {target_poi['name'].upper()}",
                            f"DICH CHUYEN NHANH: {target_poi['name'].upper()}",
                        ),
                        self._t(
                            f"Region: {target_poi['region']} • Coords: ({tx:.1f}, {ty:.1f}, {tz:.1f})",
                            f"Khu vuc: {target_poi['region']} • Toa do: ({tx:.1f}, {ty:.1f}, {tz:.1f})",
                        ),
                        kind="win",
                        duration=5.5,
                    )

            self._write_hud_dat(force=True)
            return self.get_state()

    def _resolve_fixture(self, idx: int, replace: bool = True):
        m = self.fixtures[idx]
        hs, as_ = m["h_base"], m["a_base"]
        if m["league"] == "NBA" and hs == as_:
            hs += 2
        total_goals = hs + as_
        winner = "HOME" if hs > as_ else ("AWAY" if as_ > hs else "DRAW")

        # Update League Standings
        st_list = self.standings.get(m["league_id"], [])
        for r in st_list:
            if r["team"] == m["home"]:
                r["p"] += 1
                r["gd"] += (hs - as_)
                if winner == "HOME":
                    r["w"] += 1
                    r["pts"] += (2 if m["league"] == "NBA" else 3)
                elif winner == "DRAW":
                    r["d"] += 1
                    r["pts"] += 1
                else:
                    r["l"] += 1
            elif r["team"] == m["away"]:
                r["p"] += 1
                r["gd"] += (as_ - hs)
                if winner == "AWAY":
                    r["w"] += 1
                    r["pts"] += (2 if m["league"] == "NBA" else 3)
                elif winner == "DRAW":
                    r["d"] += 1
                    r["pts"] += 1
                else:
                    r["l"] += 1
        st_list.sort(key=lambda x: (x["pts"], x["gd"]), reverse=True)

        bet = m.get("active_bet")
        bet_summary = ""
        if bet:
            won = (
                (bet["pick"] == winner)
                or (bet["pick"] == "OVER" and total_goals > m["ou_line"])
                or (bet["pick"] == "UNDER" and total_goals < m["ou_line"])
            )
            if won:
                payout = int(round(bet["stake"] * bet["odd"]))
                net_gain = payout - bet["stake"]
                self.portfolio_stats["bet_won_count"] += 1
                self.portfolio_stats["bet_net_pnl"] += net_gain
                self.modify_cash(+payout)
                bet_summary = self._t(f" 🎉 WON +${payout:,}!", f" 🎉 THANG +${payout:,}!")
                self.push_event_banner(
                    self._t(
                        f"SPORTS BET WON: +${payout:,}!",
                        f"THANG KEO BET THE THAO: +${payout:,}!",
                    ),
                    self._t(
                        f"Result: {m['home']} {hs} - {as_} {m['away']} ({m['league_name']}) • Credited +${payout:,}!",
                        f"Ket qua: {m['home']} {hs} - {as_} {m['away']} ({m['league_name']}) • Da cong +${payout:,}!",
                    ),
                    kind="win",
                    duration=7.5,
                )
            else:
                self.portfolio_stats["bet_lost_count"] += 1
                self.portfolio_stats["bet_net_pnl"] -= bet["stake"]
                bet_summary = self._t(f" ❌ Lost (-${bet['stake']:,})", f" ❌ Thua (-${bet['stake']:,})")
                self.push_event_banner(
                    self._t(
                        f"BET RESULT: {m['home']} {hs} - {as_} {m['away']}",
                        f"KET QUA KEO BET: {m['home']} {hs} - {as_} {m['away']}",
                    ),
                    self._t(
                        f"Pick [{bet['label']}] missed (-${bet['stake']:,}) • {m['league_name']}",
                        f"Keo [{bet['label']}] chua trung (-${bet['stake']:,}) • Giai {m['league_name']}",
                    ),
                    kind="warn",
                    duration=6.5,
                )

        line = f"⚽ [{m['league_name']} • {m['round_label']}] <b>{m['home']} {hs} - {as_} {m['away']}</b>{bet_summary}"
        self.sport_history.insert(0, line)
        self.last_toast = self._t(
            f"Full Time: {m['home']} {hs}-{as_} {m['away']}{bet_summary}",
            f"Ket qua: {m['home']} {hs}-{as_} {m['away']}{bet_summary}",
        )

        if replace:
            new_fixtures = generate_daily_fixtures(self.day + random.randint(1, 30), lang=self.lang)
            same_lg = [nf for nf in new_fixtures if nf["league_id"] == m["league_id"]]
            if same_lg:
                self.fixtures[idx] = same_lg[idx % len(same_lg)]

    def _run_lottery_draw(self, filter_type: str = "ALL"):
        import itertools

        xskt_types = ("XSKT_6D", "LODE_DE", "LODE_LO2", "LODE_3CANG")
        viet_types = ("MEGA_645", "POWER_655", "MEGA_BAO7", "POWER_BAO7")

        do_xskt = filter_type in ("XSKT_6D", "ALL")
        do_viet = filter_type in ("VIETLOTT", "ALL")

        total_won = 0
        remaining = []
        win_details = []

        # --------------------------------------------------------------------
        # 1. XSKT MIEN NAM & LO DE (16:30 DRAW — STRICTLY SEPARATED FROM VIETLOTT!)
        # --------------------------------------------------------------------
        win_6d = self.lottery.get("last_6d", "686868")
        win_g1 = self.lottery.get("last_xskt_g1", "49201")
        win_lo18 = list(self.lottery.get("last_xskt_lo18") or ["68", "01", "15", "27", "39", "44", "52", "63", "79", "88"])
        if do_xskt:
            win_6d = f"{random.randint(0, 999999):06d}"
            win_g1 = f"{random.randint(0, 99999):05d}"
            lo_extra = [f"{random.randint(0, 99):02d}" for _ in range(16)]
            win_lo18 = [win_6d[-2:], win_g1[-2:]] + lo_extra
            self.lottery["last_6d"] = win_6d
            self.lottery["last_xskt_g1"] = win_g1
            self.lottery["last_xskt_lo18"] = win_lo18[:10]
            lo_preview = ", ".join(win_lo18[:7])
            self.lottery["last_xskt_summary"] = self._t(
                f"XSKT (16:30) • Grand: {win_6d} | 1st: {win_g1} | 2D Roll: {lo_preview}",
                f"XSKT (16:30) • G.DB: {win_6d} | G.Nhat: {win_g1} | Lo 2 So: {lo_preview}",
            )

        # --------------------------------------------------------------------
        # 2. VIETLOTT 18:00 DRAW — SEPARATE MEGA 6/45 & POWER 6/55 DRAWS & POOLS!
        # --------------------------------------------------------------------
        win_645 = [int(x) for x in self.lottery.get("last_mega645", "05-12-19-26-38-44").split("-") if x.isdigit()]
        win_655_main = [int(x) for x in self.lottery.get("last_power655", "03-14-22-37-48-54").split("-") if x.isdigit()]
        win_655_bonus = int(self.lottery.get("last_power655_bonus", "18") or 18)
        mega_jp_hit = False
        power_jp1_hit = False
        power_jp2_hit = False

        if do_viet:
            win_645 = sorted(random.sample(range(1, 46), 6))
            win_655_main = sorted(random.sample(range(1, 56), 6))
            win_655_bonus = random.choice([x for x in range(1, 56) if x not in win_655_main])
            s645 = "-".join(f"{x:02d}" for x in win_645)
            s655 = "-".join(f"{x:02d}" for x in win_655_main)
            s655_b = f"{win_655_bonus:02d}"
            self.lottery["last_viet"] = s645
            self.lottery["last_mega645"] = s645
            self.lottery["last_power655"] = s655
            self.lottery["last_power655_bonus"] = s655_b
            self.lottery["last_vietlott_summary"] = (
                f"Vietlott (18:00) • Mega 6/45: {s645} | Power 6/55: {s655} +[{s655_b}]"
            )

        # --------------------------------------------------------------------
        # 3. SETTLE MATCHING TICKETS ONLY
        # --------------------------------------------------------------------
        for t in self.lottery["tickets"]:
            ttype = t["type"]
            stake = int(t.get("cost", 10))
            if ttype in xskt_types and not do_xskt:
                remaining.append(t)
                continue
            if ttype in viet_types and not do_viet:
                remaining.append(t)
                continue

            if ttype == "XSKT_6D":
                num = str(t["numbers"]).zfill(6)
                for tier in LOTTERY_6DIGIT_TIERS:
                    d = tier["digits"]
                    if num[-d:] == win_6d[-d:]:
                        total_won += tier["payout"]
                        win_details.append(f"XSKT [{num}] (+${tier['payout']:,})")
                        break
                else:
                    if num[-5:] == win_g1:
                        total_won += 15000
                        win_details.append(self._t(f"1st Prize XSKT [{num}] (+$15,000)", f"G.Nhat XSKT [{num}] (+$15,000)"))
            elif ttype == "LODE_DE":
                pick2 = str(t["numbers"]).zfill(2)[-2:]
                if pick2 == win_6d[-2:]:
                    p_win = stake * 70
                    total_won += p_win
                    win_details.append(self._t(f"Won 2D Tail [{pick2}] x70 (+${p_win:,})", f"Trung De [{pick2}] x70 (+${p_win:,})"))
            elif ttype == "LODE_LO2":
                pick2 = str(t["numbers"]).zfill(2)[-2:]
                nhay = win_lo18.count(pick2)
                if nhay > 0:
                    p_win = int(round(stake * 3.5 * nhay))
                    total_won += p_win
                    win_details.append(self._t(f"Won 2D Roll [{pick2}] {nhay}x (+${p_win:,})", f"Trung Lo [{pick2}] {nhay} nhay (+${p_win:,})"))
            elif ttype == "LODE_3CANG":
                pick3 = str(t["numbers"]).zfill(3)[-3:]
                if pick3 == win_6d[-3:]:
                    p_win = stake * 400
                    total_won += p_win
                    win_details.append(self._t(f"Won 3D Tail [{pick3}] x400 (+${p_win:,})", f"Trung 3 Cang DB [{pick3}] x400 (+${p_win:,})"))
            elif ttype in ("MEGA_645", "MEGA_BAO7"):
                raw_picks = [int(x) for x in str(t["numbers"]).replace("-", " ").split() if x.isdigit()]
                combos = list(itertools.combinations(raw_picks, 6)) if len(raw_picks) >= 7 else [tuple(raw_picks)]
                ticket_win = 0
                for c_set in combos:
                    hits = len(set(c_set).intersection(win_645))
                    if hits == 6:
                        ticket_win += self.lottery["jackpot_mega645"]
                        mega_jp_hit = True
                    elif hits == 5:
                        ticket_win += 5000
                    elif hits == 4:
                        ticket_win += 250
                    elif hits == 3:
                        ticket_win += 30
                if ticket_win > 0:
                    total_won += ticket_win
                    win_details.append(f"{ttype} (+${ticket_win:,})")
            elif ttype in ("POWER_655", "POWER_BAO7"):
                raw_picks = [int(x) for x in str(t["numbers"]).replace("-", " ").split() if x.isdigit()]
                combos = list(itertools.combinations(raw_picks, 6)) if len(raw_picks) >= 7 else [tuple(raw_picks)]
                ticket_win = 0
                for c_set in combos:
                    hits = len(set(c_set).intersection(win_655_main))
                    if hits == 6:
                        ticket_win += self.lottery["jackpot_power655_jp1"]
                        power_jp1_hit = True
                    elif hits == 5 and win_655_bonus in c_set:
                        ticket_win += self.lottery["jackpot_power655_jp2"]
                        power_jp2_hit = True
                    elif hits == 5:
                        ticket_win += 10000
                    elif hits == 4:
                        ticket_win += 500
                    elif hits == 3:
                        ticket_win += 50
                if ticket_win > 0:
                    total_won += ticket_win
                    win_details.append(f"{ttype} (+${ticket_win:,})")

        # Roll over or reset progressive Vietlott Jackpot pools after 18:00 draw
        if do_viet:
            if mega_jp_hit:
                self.lottery["jackpot_mega645"] = 1250000
            else:
                self.lottery["jackpot_mega645"] += 150000 + random.randint(10, 45) * 1000
            if power_jp1_hit:
                self.lottery["jackpot_power655_jp1"] = 3200000
            else:
                self.lottery["jackpot_power655_jp1"] += 350000 + random.randint(15, 60) * 1000
            if power_jp2_hit:
                self.lottery["jackpot_power655_jp2"] = 350000
            else:
                self.lottery["jackpot_power655_jp2"] += 45000 + random.randint(5, 18) * 1000
            self.lottery["jackpot"] = self.lottery["jackpot_mega645"]

        if total_won > 0:
            self.modify_cash(+total_won)
            self.portfolio_stats["lotto_won"] += total_won
            self.portfolio_stats["lotto_net_pnl"] = (
                self.portfolio_stats["lotto_won"] - self.portfolio_stats["lotto_spent"]
            )

        self.lottery["tickets"] = remaining
        self.lottery["last_draw_summary"] = (
            f"XSKT (16:30): {self.lottery['last_6d']} | "
            f"Mega 6/45: {self.lottery['last_mega645']} | "
            f"Power 6/55: {self.lottery['last_power655']} +[{self.lottery['last_power655_bonus']}]"
        )

        # --------------------------------------------------------------------
        # 4. PUSH STRICTLY SEPARATED NOTIFICATION BANNER & TOAST!
        # --------------------------------------------------------------------
        if do_xskt and not do_viet:
            lo_short = ", ".join(self.lottery["last_xskt_lo18"][:6])
            if total_won > 0:
                detail_str = ", ".join(win_details[:2])
                self.last_toast = self._t(
                    f"🎉 WON XSKT / NUMBERS (16:30): +${total_won:,}! ({detail_str})",
                    f"🎉 TRUNG XSKT / LO DE (16:30): +${total_won:,}! ({detail_str})",
                )
                self.push_event_banner(
                    self._t(
                        f"XSKT / NUMBERS DRAW WIN (16:30): +${total_won:,}!",
                        f"TRUNG XO SO KIEN THIET / LO DE (16:30): +${total_won:,}!",
                    ),
                    self._t(
                        f"Grand: {win_6d} | 1st: {win_g1} | 2D Roll: {lo_short} • {detail_str}",
                        f"G.DB: {win_6d} | G.Nhat: {win_g1} | Lo: {lo_short} • {detail_str}",
                    ),
                    kind="win",
                    duration=8.5,
                )
            else:
                self.last_toast = self._t(
                    f"🎰 XSKT Draw (16:30): Grand [{win_6d}] | 1st [{win_g1}] | 2D Roll: {lo_short}",
                    f"🎰 KQ XSKT Mien Nam (16:30): G.DB [{win_6d}] | G.Nhat [{win_g1}] | Lo: {lo_short}",
                )
                self.push_event_banner(
                    self._t(
                        f"XSKT 6-DIGIT DRAW RESULTS (16:30) • GRAND: {win_6d}",
                        f"KET QUA XO SO KIEN THIET (16:30) • DB: {win_6d}",
                    ),
                    self._t(
                        f"Grand Prize: {win_6d} • 1st Prize: {win_g1} • 2D Roll: {lo_short}",
                        f"Giai Dac Biet: {win_6d} • Giai Nhat: {win_g1} • Lo 2 So: {lo_short}",
                    ),
                    kind="info",
                    duration=6.5,
                )
        elif do_viet and not do_xskt:
            s645 = self.lottery["last_mega645"]
            s655 = self.lottery["last_power655"]
            s655_b = self.lottery["last_power655_bonus"]
            if total_won > 0:
                detail_str = ", ".join(win_details[:2])
                self.last_toast = self._t(
                    f"🎉 WON VIETLOTT (18:00): +${total_won:,}! ({detail_str})",
                    f"🎉 TRUNG VIETLOTT (18:00): +${total_won:,}! ({detail_str})",
                )
                self.push_event_banner(
                    self._t(
                        f"VIETLOTT DRAW WIN (18:00): +${total_won:,}!",
                        f"TRUNG VIETLOTT (18:00): +${total_won:,}!",
                    ),
                    f"Mega 6/45: {s645} | Power 6/55: {s655} +[{s655_b}] • {detail_str}",
                    kind="win",
                    duration=8.5,
                )
            else:
                self.last_toast = self._t(
                    f"💎 Vietlott Draw (18:00) • Mega 6/45: [{s645}] | Power 6/55: [{s655} + {s655_b}]",
                    f"💎 KQ Vietlott (18:00) • Mega 6/45: [{s645}] | Power 6/55: [{s655} + {s655_b}]",
                )
                self.push_event_banner(
                    self._t(
                        "VIETLOTT DRAW RESULTS (18:00): MEGA 6/45 & POWER 6/55",
                        "KET QUA VIETLOTT (18:00): MEGA 6/45 & POWER 6/55",
                    ),
                    f"Mega 6/45: {s645} • Power 6/55: {s655} + [{s655_b}]",
                    kind="info",
                    duration=6.5,
                )
        else:
            s645 = self.lottery["last_mega645"]
            s655 = self.lottery["last_power655"]
            s655_b = self.lottery["last_power655_bonus"]
            if total_won > 0:
                self.last_toast = self._t(
                    f"🎉 LOTTERY WIN +${total_won:,} CREDITED TO GTA SA CASH!",
                    f"🎉 TRUNG SO +${total_won:,} VAO TIEN MAT GTA SA!",
                )
                self.push_event_banner(
                    self._t(
                        f"CONGRATULATIONS! LOTTERY WIN +${total_won:,}!",
                        f"CHUC MUNG TRUNG VE SO +${total_won:,}!",
                    ),
                    f"XSKT: {win_6d} | Mega: {s645} | Power: {s655}+[{s655_b}]",
                    kind="win",
                    duration=8.5,
                )
            else:
                self.last_toast = self._t(
                    f"🎰 Draw Results: XSKT {win_6d} | Mega 6/45: {s645} | Power 6/55: {s655}+[{s655_b}]",
                    f"🎰 KQ XSKT: {win_6d} | Mega 6/45: {s645} | Power 6/55: {s655}+[{s655_b}]",
                )
                self.push_event_banner(
                    self._t("ALL LOTTERY DRAW RESULTS", "KET QUA TAT CA KY QUAY XO SO"),
                    f"XSKT: {win_6d} • Mega 6/45: {s645} • Power 6/55: {s655}+[{s655_b}]",
                    kind="info",
                    duration=6.5,
                )


    def _build_portfolio_data(self) -> dict:
        spot_holdings = []
        stocks_spot_val = 0.0
        stocks_spot_pnl = 0.0
        for sym, a in self.stocks_market.items():
            if a["spot_qty"] > 0 and a["spot_val"] >= 0.01:
                stocks_spot_val += a["spot_val"]
                stocks_spot_pnl += a.get("spot_pnl", 0.0)
                spot_holdings.append({
                    "market_group": "stocks",
                    "symbol": sym,
                    "name": a["name"],
                    "category": a["category"],
                    "qty": round(a["spot_qty"], 4),
                    "price": a["price"],
                    "cost": round(a.get("spot_cost", 0.0), 2),
                    "val": round(a["spot_val"], 2),
                    "pnl": round(a.get("spot_pnl", 0.0), 2),
                    "pnl_pct": round(a.get("spot_pnl_pct", 0.0), 2),
                })

        crypto_spot_val = 0.0
        crypto_spot_pnl = 0.0
        for sym, a in self.crypto_market.items():
            if a["spot_qty"] > 0 and a["spot_val"] >= 0.01:
                crypto_spot_val += a["spot_val"]
                crypto_spot_pnl += a.get("spot_pnl", 0.0)
                spot_holdings.append({
                    "market_group": "crypto",
                    "symbol": sym,
                    "name": a["name"],
                    "category": a["category"],
                    "qty": round(a["spot_qty"], 4),
                    "price": a["price"],
                    "cost": round(a.get("spot_cost", 0.0), 2),
                    "val": round(a["spot_val"], 2),
                    "pnl": round(a.get("spot_pnl", 0.0), 2),
                    "pnl_pct": round(a.get("spot_pnl_pct", 0.0), 2),
                })

        fut_margin = sum(f["margin"] for f in self.futures)
        fut_pnl = round(sum(f["pnl"] for f in self.futures), 2)
        fut_equity = round(fut_margin + fut_pnl, 2)

        active_bets = []
        bets_stake = 0
        bets_pot_payout = 0
        for m in self.fixtures:
            b = m.get("active_bet")
            if b:
                pot = int(round(b["stake"] * b["odd"]))
                bets_stake += b["stake"]
                bets_pot_payout += pot
                active_bets.append({
                    "match_id": m["id"],
                    "league_name": m["league_name"],
                    "kickoff": m["kickoff"],
                    "match": f"{m['home']} vs {m['away']}",
                    "pick_label": b["label"],
                    "odd": b["odd"],
                    "stake": b["stake"],
                    "potential_payout": pot,
                })

        active_tickets = list(self.lottery["tickets"])
        lotto_pending_cost = len(active_tickets) * 10
        unrealized_pnl = round(stocks_spot_pnl + crypto_spot_pnl + fut_pnl, 2)
        total_net_worth = int(
            round(
                self.cash
                + self.bank
                + self.savings
                - self.loan
                + stocks_spot_val
                + crypto_spot_val
                + fut_equity
                + bets_stake
                + lotto_pending_cost
            )
        )

        # Build 8 HUD lines depending on self.port_tab_idx (0..3)
        tab_idx = self.port_tab_idx % 4
        lines = []
        if tab_idx == 0:
            if self._is_vi():
                lines = [
                    f"[PHAN BO TAI SAN] Tong Tai San Rong: ${total_net_worth:,}",
                    f"1. Tien Mat GTA: ${self.cash:,} | Bank: ${self.bank:,} | Tiet Kiem: ${self.savings:,}",
                    f"2. Co Phieu & Vang Spot ({len([x for x in spot_holdings if x['market_group']=='stocks'])} ma): ${int(stocks_spot_val):,} (PnL {stocks_spot_pnl:+.0f}$)",
                    f"3. Crypto Spot ({len([x for x in spot_holdings if x['market_group']=='crypto'])} ma): ${int(crypto_spot_val):,} (PnL {crypto_spot_pnl:+.0f}$)",
                    f"4. Vi The Futures ({len(self.futures)} lenh): Von ${fut_margin:,} | Equity ${int(fut_equity):,} (PnL {fut_pnl:+.0f}$)",
                    f"5. Keo Bet Dang Cho ({len(active_bets)} tran): Von ${bets_stake:,} -> Ky vong +${bets_pot_payout:,}",
                    f"6. Ve So Cho Quay ({len(active_tickets)} ve): Von ${lotto_pending_cost:,} | No Vay: -${self.loan:,}",
                    f"[TONG P&L] Market Da Chot: {self.portfolio_stats['realized_market_pnl']:+.0f}$ | Bet PnL: {self.portfolio_stats['bet_net_pnl']:+,}$ | Xo So PnL: {self.portfolio_stats['lotto_net_pnl']:+,}$",
                ]
            else:
                lines = [
                    f"[ASSET ALLOCATION] Total Net Worth: ${total_net_worth:,}",
                    f"1. GTA Cash: ${self.cash:,} | Bank: ${self.bank:,} | Savings: ${self.savings:,}",
                    f"2. Stocks & Gold Spot ({len([x for x in spot_holdings if x['market_group']=='stocks'])} assets): ${int(stocks_spot_val):,} (PnL {stocks_spot_pnl:+.0f}$)",
                    f"3. Crypto Spot ({len([x for x in spot_holdings if x['market_group']=='crypto'])} assets): ${int(crypto_spot_val):,} (PnL {crypto_spot_pnl:+.0f}$)",
                    f"4. Open Futures ({len(self.futures)} pos): Margin ${fut_margin:,} | Equity ${int(fut_equity):,} (PnL {fut_pnl:+.0f}$)",
                    f"5. Active Sports Bets ({len(active_bets)} matches): Stake ${bets_stake:,} -> Pot +${bets_pot_payout:,}",
                    f"6. Pending Lottery ({len(active_tickets)} tickets): Cost ${lotto_pending_cost:,} | Loan Debt: -${self.loan:,}",
                    f"[TOTAL P&L] Realized Market: {self.portfolio_stats['realized_market_pnl']:+.0f}$ | Bet PnL: {self.portfolio_stats['bet_net_pnl']:+,}$ | Lotto PnL: {self.portfolio_stats['lotto_net_pnl']:+,}$",
                ]
        elif tab_idx == 1:
            lines.append(
                self._t(
                    f"[SPOT HOLDINGS: {len(spot_holdings)} ASSETS | TOTAL ${int(stocks_spot_val + crypto_spot_val):,}]",
                    f"[DANH MUC SPOT DANG NAM GIU: {len(spot_holdings)} MA | TONG ${int(stocks_spot_val + crypto_spot_val):,}]",
                )
            )
            if not spot_holdings:
                lines.append(self._t("No Stocks, Gold, or Crypto Spot holdings yet.", "Chua nam giu ma Co Phieu, Vang hay Crypto Spot nao."))
                lines.append(self._t("-> Open App 2.STCK or 3.CRYP to buy Spot assets!", "-> Hay sang App 2.STCK hoac 3.CRYP de mua tich san Spot!"))
            else:
                for idx_h, h in enumerate(spot_holdings[:7]):
                    lines.append(
                        self._t(
                            f"#{idx_h+1} [{h['symbol']}] Qty: {h['qty']:.3f} | Price: ${h['price']} | Val: ${int(h['val']):,} ({h['pnl']:+.0f}$ / {h['pnl_pct']:+.1f}%)",
                            f"#{idx_h+1} [{h['symbol']}] SL: {h['qty']:.3f} | Gia: ${h['price']} | GT: ${int(h['val']):,} ({h['pnl']:+.0f}$ / {h['pnl_pct']:+.1f}%)",
                        )
                    )
        elif tab_idx == 2:
            lines.append(
                self._t(
                    f"[OPEN FUTURES POSITIONS: {len(self.futures)} ORDERS | EQUITY ${int(fut_equity):,}]",
                    f"[VI THE FUTURES DANG MO: {len(self.futures)} LENH | EQUITY ${int(fut_equity):,}]",
                )
            )
            if not self.futures:
                lines.append(self._t("No open Long/Short Futures positions.", "Chua co vi the Long/Short Futures nao dang mo."))
                lines.append(self._t("-> Open App 2.STCK or 3.CRYP to trade Long/Short!", "-> Hay sang App 2.STCK hoac 3.CRYP de mo Long/Short!"))
            else:
                for idx_f, f in enumerate(self.futures[:7]):
                    lines.append(
                        self._t(
                            f"#{idx_f+1} {f['side']} {f['leverage']}x {f['symbol']} | Margin ${f['margin']:,} | Entry ${f['entry']} -> ${f['mark']} ({f['pnl']:+.0f}$ / {f['roe_pct']:+.0f}%)",
                            f"#{idx_f+1} {f['side']} {f['leverage']}x {f['symbol']} | Von ${f['margin']:,} | Entry ${f['entry']} -> ${f['mark']} ({f['pnl']:+.0f}$ / {f['roe_pct']:+.0f}%)",
                        )
                    )
        else:
            lines.append(
                self._t(
                    f"[SPORTS BETS ({len(active_bets)}) & PENDING LOTTERY ({len(active_tickets)})]",
                    f"[KEO BET ({len(active_bets)}) & VE SO CHO QUAY ({len(active_tickets)})]",
                )
            )
            for b in active_bets[:4]:
                lines.append(
                    self._t(
                        f"[BET] {b['kickoff']} {b['match']} -> [{b['pick_label']}] ${b['stake']:,} @ {b['odd']:.2f}x (Win +${b['potential_payout']:,})",
                        f"[BET] {b['kickoff']} {b['match']} -> [{b['pick_label']}] ${b['stake']:,} @ {b['odd']:.2f}x (Thang +${b['potential_payout']:,})",
                    )
                )
            for t in active_tickets[:3]:
                lines.append(
                    self._t(
                        f"[TICKET] {t['type']}: Numbers [{t['numbers']}] (Pending Draw)",
                        f"[VE SO] {t['type']}: Day so [{t['numbers']}] (Ve $10 - Cho quay)",
                    )
                )
            if not active_bets and not active_tickets:
                lines.append(self._t("No active Sports Bets or pending Lottery tickets.", "Chua co keo Bet hay Ve So nao dang cho ket qua."))
            lines.append(
                self._t(
                    f"Stats: Bet Won {self.portfolio_stats['bet_won_count']}/Lost {self.portfolio_stats['bet_lost_count']} ({self.portfolio_stats['bet_net_pnl']:+,}$) | Lotto ({self.portfolio_stats['lotto_net_pnl']:+,}$)",
                    f"Thong ke: Bet Thang {self.portfolio_stats['bet_won_count']}/Thua {self.portfolio_stats['bet_lost_count']} ({self.portfolio_stats['bet_net_pnl']:+,}$) | Xo So ({self.portfolio_stats['lotto_net_pnl']:+,}$)",
                )
            )

        while len(lines) < 8:
            lines.append("")

        return {
            "total_net_worth": total_net_worth,
            "stocks_spot_val": round(stocks_spot_val, 2),
            "stocks_spot_pnl": round(stocks_spot_pnl, 2),
            "crypto_spot_val": round(crypto_spot_val, 2),
            "crypto_spot_pnl": round(crypto_spot_pnl, 2),
            "fut_margin": fut_margin,
            "fut_pnl": fut_pnl,
            "fut_equity": fut_equity,
            "bets_stake": bets_stake,
            "bets_potential_payout": bets_pot_payout,
            "lotto_pending_cost": lotto_pending_cost,
            "unrealized_pnl": unrealized_pnl,
            "spot_holdings": spot_holdings,
            "open_futures": self.futures,
            "active_bets": active_bets,
            "active_tickets": active_tickets,
            "stats": self.portfolio_stats,
            "hud_lines": [to_clean_viet_ascii(ln) for ln in lines[:8]],
        }

    def _build_bug_inspector_data(self) -> dict:
        px, py, pz = self.player_pos
        vx, vy, vz = self.player_velocity
        zone_lbl = self.map_inspector.lookup_zone(px, py, pz, lang=self.lang) if self.map_inspector.ready else "San Andreas"
        u_modes = self._get_unstuck_modes()
        safe_t = self._get_safe_recall_target(u_modes[self.unstuck_mode_idx % len(u_modes)][0])
        trail_5s = self._get_trail_5s_snapshots()

        # If on App 8 and no live scan yet, run a fast 4ms scan once index is ready
        if self.phone_app == 8 and self.last_live_scan is None and self.map_inspector.ready:
            self._refresh_live_scan()

        norm_reports = [self._normalize_inspection(r) for r in self.map_inspector.reports[:12]]
        active_scan = self.last_live_scan or (norm_reports[0] if norm_reports else None)
        suspects = active_scan.get("suspects", []) if active_scan else []
        top = suspects[0] if suspects else None
        last_rep = norm_reports[0] if norm_reports else None
        st_idx = self.map_inspector.index_stats
        total_ipl = int(st_idx.get("text_ipl_inst", 0)) + int(st_idx.get("stream_ipl_inst", 0))

        hud_lines = []
        if top:
            hud_lines.append(
                self._t(
                    f"[SUSPECT #1] {top['dff_name']}.dff (ID {top['model_id']}) | TXD: {top['txd_name']}.txd | Dist: {top['surface_dist']}m",
                    f"[NGHI PHAM SO 1] {top['dff_name']}.dff (ID {top['model_id']}) | TXD: {top['txd_name']}.txd | Cach: {top['surface_dist']}m",
                )
            )
            hud_lines.append(
                f"-> File IPL: {top['ipl_source']} | IDE: {top['ide_source']}"
            )
            hud_lines.append(
                f"-> File IMG: {top['dff_img']} | COL: {top['col_source']} ({top['col_version']}, R={top['col_radius']}m, {top['col_boxes']}B/{top['col_faces']}F)"
            )
            hud_lines.append(
                self._t(
                    f"-> Flags: {', '.join(top.get('issue_flags', ['OK']))}",
                    f"-> Co (Flags): {', '.join(top.get('issue_flags', ['OK']))}",
                )
            )
        else:
            idx_st = self._t("READY", "SAN SANG") if self.map_inspector.ready else self._t("INDEXING...", "DANG NAP INDEX...")
            hud_lines.append(
                self._t(
                    f"[AUTO-INSPECTOR: {idx_st}] Press F9 (Row 4) or Ctrl+F11 to scan 15m around Aether!",
                    f"[AUTO-INSPECTOR: {idx_st}] Bam F9 (Dong 4) hoac Ctrl+F11 de quet 15m quanh Aether!",
                )
            )
            hud_lines.append(
                f"Index: {st_idx.get('ide_models', 0)} IDE | {total_ipl} IPL | {st_idx.get('col_models', 0)} COL"
            )
            hud_lines.append(
                self._t(
                    "Supports both Text IPL and Binary Stream IPL (.img::*_stream*.ipl)!",
                    "Ho tro quet ca IPL Text va Binary Stream IPL (.img::*_stream*.ipl)!",
                )
            )
            hud_lines.append(
                self._t(
                    "Auto cross-checks .dff/.txd/.col and detects missing Collision (0 faces)!",
                    "Tu dong doi chieu .dff/.txd/.col va phat hien thieu Collision (0 faces)!",
                )
            )

        if len(suspects) > 1:
            others = ", ".join(f"{s['dff_name']}(ID {s['model_id']},{s['surface_dist']}m)" for s in suspects[1:4])
            hud_lines.append(self._t(f"[NEARBY 15M] {others}", f"[LAN CAN 15M] {others}"))
        else:
            hud_lines.append(
                self._t(
                    "[NEARBY 15M] No secondary objects in scan radius.",
                    "[LAN CAN 15M] Khong co object phu trong tam quet.",
                )
            )

        if last_rep:
            hud_lines.append(
                self._t(
                    f"[SAVED {len(self.map_inspector.reports)} BUGS] Latest: #{last_rep['id']} ({last_rep['category_label']}) -> docs/project-eagle/map-bug-reports.md",
                    f"[DA LUU {len(self.map_inspector.reports)} BUG] Moi nhat: #{last_rep['id']} ({last_rep['category_label']}) -> docs/project-eagle/map-bug-reports.md",
                )
            )
        else:
            hud_lines.append(
                self._t(
                    "[BUG LOG] No bugs logged yet. Press Ctrl+F11 (or F9 in App 8) to log & rescue!",
                    "[LOG BAO BUG] Chua co bug nao. Bam Ctrl+F11 (hoac F9 trong App 8) de ghi nhan & cuu ho!",
                )
            )

        while len(hud_lines) < 6:
            hud_lines.append("")

        t5 = trail_5s[0] if len(trail_5s) >= 1 else {"x": px, "y": py, "z": pz}
        t3 = trail_5s[1] if len(trail_5s) >= 2 else {"x": px, "y": py, "z": pz}
        now_lbl = self._t("Now", "Nay")
        trail_str = (
            f"Trail 5s: -5s({t5['x']:.0f},{t5['y']:.0f},{t5['z']:.1f}) -> "
            f"-3s({t3['x']:.0f},{t3['y']:.0f},{t3['z']:.1f}) -> "
            f"{now_lbl}({px:.0f},{py:.0f},{pz:.1f})"
        )

        bug_cats = self._get_bug_categories()
        return {
            "index_ready": self.map_inspector.ready,
            "index_stats": {
                "ide_models": st_idx.get("ide_models", 0),
                "ipl_insts": total_ipl,
                "col_entries": st_idx.get("col_models", 0),
                "enex_entries": st_idx.get("enex_count", 0),
                "build_ms": int(round(st_idx.get("elapsed_sec", 0.0) * 1000)),
            },
            "live_telemetry": {
                "x": round(px, 3),
                "y": round(py, 3),
                "z": round(pz, 3),
                "heading": round(self.player_heading, 1),
                "vx": round(vx, 4),
                "vy": round(vy, 4),
                "vz": round(vz, 4),
                "area_code": self.player_area_code,
                "game_area": self.player_game_area,
                "in_vehicle": self.player_in_vehicle,
                "zone_label": zone_lbl,
                "safe_recall": safe_t,
                "trail_5s": trail_5s,
                "trail_str": trail_str,
            },
            "selected_category_idx": self.bug_cat_idx,
            "selected_category_code": bug_cats[self.bug_cat_idx % len(bug_cats)][0],
            "selected_category_label": bug_cats[self.bug_cat_idx % len(bug_cats)][1],
            "categories": [{"code": c, "label": l} for c, l in bug_cats],
            "selected_unstuck_idx": self.unstuck_mode_idx,
            "selected_unstuck_mode": u_modes[self.unstuck_mode_idx % len(u_modes)][0],
            "selected_unstuck_label": u_modes[self.unstuck_mode_idx % len(u_modes)][1],
            "unstuck_modes": [{"mode": m, "label": l} for m, l in u_modes],
            "live_scan": active_scan,
            "reports_count": len(self.map_inspector.reports),
            "reports": norm_reports,
            "reports_md_path": str(self.map_inspector.md_report_path),
            "reports_json_path": str(self.map_inspector.json_report_path),
            "hud_lines": [to_clean_viet_ascii(ln) for ln in hud_lines[:6]],
        }

    def _build_ggmap_data(self) -> dict:
        gg_cats = self._get_ggmap_categories()
        cat_idx = self.ggmap_cat_idx % len(gg_cats)
        cat_code, cat_lbl, cat_title = gg_cats[cat_idx]
        pois = self._get_active_ggmap_pois()
        sel_idx = self.ggmap_poi_idx % max(1, len(pois))
        sel_poi = pois[sel_idx] if pois else None

        win_size = 5
        win_start = max(0, min(sel_idx - 2, max(0, len(pois) - win_size)))
        table_rows = []
        for r_i in range(win_size):
            p_idx = win_start + r_i
            if p_idx < len(pois):
                p = pois[p_idx]
                is_gps = bool(self.active_gps_target and self.active_gps_target.get("id") == p["id"])
                table_rows.append({
                    "idx": p_idx + 1,
                    "id": p["id"],
                    "name": to_clean_viet_ascii(p["name"])[:24],
                    "region": to_clean_viet_ascii(p["region"])[:13],
                    "dist": p["dist_str"],
                    "compass": p["compass"],
                    "sel": "1" if p_idx == sel_idx else "0",
                    "gps": "1" if is_gps else "0",
                })
            else:
                table_rows.append({
                    "idx": 0,
                    "id": "",
                    "name": "",
                    "region": "",
                    "dist": "",
                    "compass": "",
                    "sel": "0",
                    "gps": "0",
                })

        if self.active_gps_target:
            gt = self.active_gps_target
            gps_bar = self._t(
                f"GPS ROUTING: {to_clean_viet_ascii(gt['name'])[:22]} "
                f"({gt['dist_str']} - {gt['compass']}) [F10: Clear]",
                f"DANG CHI DUONG GPS: {to_clean_viet_ascii(gt['name'])[:22]} "
                f"({gt['dist_str']} - {gt['compass']}) [F10: Huy]",
            )
            gps_active_str = "1"
        else:
            gps_bar = self._t(
                "No GPS Waypoint (Select POI I/K & press F9/Enter to pin Red T on Radar!)",
                "Chua cam moc GPS (Chon diem I/K & bam F9/Enter de cam moc do T tren Radar!)",
            )
            gps_active_str = "0"

        if sel_poi:
            sel_title = f"[{sel_idx+1}/{len(pois)}] {to_clean_viet_ascii(sel_poi['name'])}"
            sel_coords = self._t(
                f"Region: {to_clean_viet_ascii(sel_poi['region'])} | "
                f"Dist: {sel_poi['dist_str']} ({sel_poi['compass']}) | "
                f"Coords: ({sel_poi['x']:.0f}, {sel_poi['y']:.0f}, {sel_poi['z']:.1f})",
                f"Khu vuc: {to_clean_viet_ascii(sel_poi['region'])} | "
                f"Cach: {sel_poi['dist_str']} ({sel_poi['compass']}) | "
                f"Toa do: ({sel_poi['x']:.0f}, {sel_poi['y']:.0f}, {sel_poi['z']:.1f})",
            )
            sel_note = to_clean_viet_ascii(sel_poi.get("desc", sel_poi.get("note", "")))[:66]
        else:
            sel_title = self._t("No destination selected", "Chua co diem den")
            sel_coords = ""
            sel_note = ""

        px, py, pz = self.player_pos
        return {
            "selected_cat_idx": cat_idx,
            "selected_cat_id": cat_code,
            "selected_cat_code": cat_code,
            "selected_cat_label": cat_lbl,
            "selected_cat_title": cat_title,
            "categories": [
                {"idx": idx_c, "id": c, "code": c, "short": l, "label": l, "title": t}
                for idx_c, (c, l, t) in enumerate(gg_cats)
            ],
            "total_pois": len(CURATED_GG_MAP_POIS),
            "filtered_count": len(pois),
            "cat_pois_count": len(pois),
            "player_coords": {"x": round(px, 1), "y": round(py, 1), "z": round(pz, 1)},
            "selected_poi_idx": sel_idx,
            "selected_poi": sel_poi,
            "pois": pois,
            "table_rows": table_rows,
            "active_gps": self.active_gps_target,
            "gps_active_str": gps_active_str,
            "gps_bar": to_clean_viet_ascii(gps_bar),
            "sel_title": sel_title,
            "sel_coords": sel_coords,
            "sel_note": sel_note,
        }

    def _write_hud_dat(self, force: bool = False):
        self.paimon.tick(self)
        port_data = self._build_portfolio_data()
        bug_data = self._build_bug_inspector_data()
        ggmap_data = self._build_ggmap_data()
        dbg_proj = self.debug_sys.build_hud_and_web_projection(self)
        net_worth = port_data["total_net_worth"]
        if self._is_vi():
            port_tabs = [
                "Trang 1/3: Phan Bo Tai San & Thanh Tien Do",
                f"Trang 2/3: Bang Nam Giu Spot ({len(port_data['spot_holdings'])} ma)",
                f"Trang 3/3: Bang Futures ({len(port_data['open_futures'])}) & Keo Bet ({len(port_data['active_bets'])})",
            ]
        else:
            port_tabs = [
                "Page 1/3: Asset Allocation & Progress Bars",
                f"Page 2/3: Spot Holdings Table ({len(port_data['spot_holdings'])} assets)",
                f"Page 3/3: Open Futures ({len(port_data['open_futures'])}) & Sports Bets ({len(port_data['active_bets'])})",
            ]

        # Active chart asset depends on whether user is on App 3 (Crypto) or App 2 (Stocks/Gold)
        grp_key = "crypto" if self.phone_app == 3 else "stocks"
        m_dict = self.crypto_market if self.phone_app == 3 else self.stocks_market
        sel_sym = self.selected_crypto_sym if self.phone_app == 3 else self.selected_stock_sym
        default_sym = "BTC" if self.phone_app == 3 else "XAU"
        cur_asset = m_dict.get(sel_sym, m_dict[default_sym])

        # Market Watch 6-row window for Sub-page 0 of App 2 & App 3
        syms_list = list(m_dict.keys())
        sel_sym_idx = syms_list.index(cur_asset["symbol"]) if cur_asset["symbol"] in syms_list else 0
        win_size = 6
        win_start = max(0, min(sel_sym_idx - 2, max(0, len(syms_list) - win_size)))
        mw_rows = []
        for r_i in range(win_size):
            a_idx = win_start + r_i
            if a_idx < len(syms_list):
                a_obj = m_dict[syms_list[a_idx]]
                p_val = a_obj["price"]
                p_str = f"${p_val:,.2f}" if p_val >= 10 else f"${p_val:.4f}"
                sp_str = f"${int(round(a_obj['spot_val'])):,}" if a_obj["spot_val"] >= 1 else "-"
                mw_rows.append({
                    "sym": f"{a_obj['symbol']}",
                    "name": to_clean_viet_ascii(a_obj["name"])[:14],
                    "price": p_str,
                    "delta": f"{a_obj['delta_pct']:+.2f}%",
                    "pos": "1" if a_obj["delta_pct"] >= 0 else "0",
                    "spot": sp_str,
                    "sel": "1" if a_idx == sel_sym_idx else "0",
                })
            else:
                mw_rows.append({"sym": "", "name": "", "price": "", "delta": "", "pos": "1", "spot": "", "sel": "0"})

        candles = cur_asset["candles"][-18:]
        lows = min(c["l"] for c in candles)
        highs = max(c["h"] for c in candles)
        span = max(highs - lows, 0.0001)
        pts = [str(int(round(((c["c"] - lows) / span) * 86 + 7))) for c in candles]

        grp_futs = [f for f in self.futures if f["market_group"] == grp_key]
        if grp_futs:
            f0 = grp_futs[0]
            fut_str = f"{f0['side']} {f0['leverage']}x {f0['symbol']} ${f0['margin']} (PnL {f0['pnl']:+.0f}$/{f0['roe_pct']:+.0f}%)"
        else:
            fut_str = self._t("No Open Futures (Press F9 to order)", "Chua mo Futures (Bam F9 dat lenh)")

        # App 1 option labels
        if self._is_vi():
            meal_labels = [
                "An Burger -$25 (+35% No, +25 HP)",
                "Uong Tang Luc -$15 (+30% EN, +15 HP)",
                "Ngu Qua Dem (+100% HP/EN, +1 Ngay)",
            ]
            bank_labels = [
                f"Nap ATM vao Bank (+${self.tx_amount:,})",
                f"Rut ATM ra Tien Mat (-${self.tx_amount:,})",
                f"Gui So Tiet Kiem 1.5%/d (+${self.tx_amount:,})",
                f"Rut So Tiet Kiem (-${self.tx_amount:,})",
            ]
            loan_labels = [
                f"Vay Tin Dung (+${self.tx_amount:,}, Lai 3%/d)",
                f"Tra Bot No Vay (-${min(self.tx_amount, max(self.loan, self.tx_amount)):,})",
                f"Tat Toan Het No (-${self.loan:,})",
            ]
        else:
            meal_labels = [
                "Eat Burger -$25 (+35% Hunger, +25 HP)",
                "Energy Drink -$15 (+30% EN, +15 HP)",
                "Sleep Overnight (+100% HP/EN, +1 Day)",
            ]
            bank_labels = [
                f"ATM Deposit to Bank (+${self.tx_amount:,})",
                f"ATM Withdraw to Cash (-${self.tx_amount:,})",
                f"Deposit Savings 1.5%/d (+${self.tx_amount:,})",
                f"Withdraw Savings (-${self.tx_amount:,})",
            ]
            loan_labels = [
                f"Borrow Credit (+${self.tx_amount:,}, 3%/d Interest)",
                f"Repay Loan Part (-${min(self.tx_amount, max(self.loan, self.tx_amount)):,})",
                f"Pay Off Full Loan (-${self.loan:,})",
            ]

        # App 2/3 trade mode label
        t_modes = self._get_trade_modes()
        _, _, trade_mode_lbl = t_modes[self.trade_mode_idx % len(t_modes)]

        # App 4 Multi-Match League Page (5 matches per league!) + Structured 4-Column Scoreboard
        active_lg = LEAGUES[self.selected_league_idx % len(LEAGUES)]
        lg_matches = self._get_active_league_fixtures()
        sel_m_idx = self.sport_match_idx % max(1, len(lg_matches))
        sel_m = lg_matches[sel_m_idx] if lg_matches else None
        s_picks = self._get_sport_picks()
        pick_code, pick_lbl = s_picks[self.sport_pick_idx % len(s_picks)]

        match_rows = []
        sp_table = []
        for i in range(5):
            if i < len(lg_matches):
                mi = lg_matches[i]
                bet_tag = (
                    self._t(f" [BET ${mi['active_bet']['stake']}]", f" [DA CUOC ${mi['active_bet']['stake']}]")
                    if mi.get("active_bet")
                    else ""
                )
                match_rows.append(
                    to_clean_viet_ascii(
                        f"#{i+1} {mi['kickoff']} {mi['home']} vs {mi['away']} (1:{mi['odds'][0]:.2f} X:{mi['odds'][1]:.2f} 2:{mi['odds'][2]:.2f}){bet_tag}"
                    )
                )
                sp_table.append({
                    "time": mi["kickoff"],
                    "match": to_clean_viet_ascii(f"{mi['home'][:10]} v {mi['away'][:10]}"),
                    "odds": f"{mi['odds'][0]:.2f}/{mi['odds'][1]:.2f}/{mi['odds'][2]:.2f}",
                    "ou": self._t(f"O/U {mi['ou_line']}", f"T/X {mi['ou_line']}"),
                    "bet": f"${mi['active_bet']['stake']}" if mi.get("active_bet") else "-",
                })
            else:
                match_rows.append("")
                sp_table.append({"time": "", "match": "", "odds": "", "ou": "", "bet": ""})

        if sel_m:
            odd_v = sel_m["odds"][0] if pick_code == "HOME" else (sel_m["odds"][1] if pick_code == "DRAW" else (sel_m["odds"][2] if pick_code == "AWAY" else 1.90))
            sport_pick_str = self._t(f"Pick: {pick_lbl} @ {odd_v:.2f}x", f"Keo: {pick_lbl} @ {odd_v:.2f}x")
            sel_match_vs = to_clean_viet_ascii(f"{sel_m['home']}  vs  {sel_m['away']}")
            sel_match_meta = to_clean_viet_ascii(
                self._t(
                    f"{active_lg['name']} • Kickoff: {sel_m['kickoff']} • Hcap: {sel_m['hcap']} • O/U: {sel_m['ou_line']}",
                    f"{active_lg['name']} • Gio da: {sel_m['kickoff']} • Chap: {sel_m['hcap']} • T/X: {sel_m['ou_line']}",
                )
            )
            sel_odds = [f"{sel_m['odds'][0]:.2f}", f"{sel_m['odds'][1]:.2f}", f"{sel_m['odds'][2]:.2f}", "1.90", "1.90"]
        else:
            sport_pick_str = self._t("Select Pick", "Chon Keo")
            sel_match_vs = self._t("No match selected", "Chua chon tran")
            sel_match_meta = ""
            sel_odds = ["2.00", "3.20", "2.80", "1.90", "1.90"]

        st_rows = self.standings.get(active_lg["id"], [])[:4]
        st_strs = []
        for idx_s in range(4):
            if idx_s < len(st_rows):
                sr = st_rows[idx_s]
                st_strs.append(
                    to_clean_viet_ascii(
                        self._t(
                            f"#{idx_s+1} {sr['team'][:13]} | P:{sr['p']} | GD:{sr['gd']:+d} | {sr['pts']}pts",
                            f"#{idx_s+1} {sr['team'][:13]} | Tr:{sr['p']} | HS:{sr['gd']:+d} | {sr['pts']}d",
                        )
                    )
                )
            else:
                st_strs.append("")

        # App 5 Lottery labels & 4 Dedicated Sub-pages (Scratch 3x3, XSKT 16:30, Vietlott 18:00, Keno 0s)
        l_modes = self._get_lotto_modes()
        _, _, lotto_mode_lbl = l_modes[self.lotto_mode_idx % len(l_modes)]
        s_tiers = self._get_scratch_tiers()
        _, sc_cost_val, scratch_tier_lbl = s_tiers[self.scratch_tier_idx % len(s_tiers)]
        sc_cells = [
            to_clean_viet_ascii(str(c)).replace("★", "STAR").replace("💎", "GEM").replace("👑", "CROWN")
            for c in (self.lottery.get("scratch_cells") or ["$20"] * 9)[:9]
        ]
        while len(sc_cells) < 9:
            sc_cells.append("$20")

        x_modes = self._get_xskt_modes()
        x_code, _, x_mode_lbl = x_modes[self.xskt_mode_idx % len(x_modes)]
        if x_code == "XSKT_6D":
            xskt_buy_lbl = self._t(
                "4.BUY 6-DIGIT XSKT TICKET ($10) [F9: Buy | F10: Draw 16:30]",
                "4.MUA VE KIEN THIET 6 SO ($10) [F9: Mua | F10: Quay 16:30]",
            )
        else:
            xskt_buy_lbl = self._t(
                f"4.PLACE {x_code} (Stake ${self.tx_amount:,}) [F9: Bet | F10: Draw 16:30]",
                f"4.GHI {x_code} (Von ${self.tx_amount:,}) [F9: Ghi | F10: Quay 16:30]",
            )

        v_modes = self._get_vietlott_modes()
        v_code, _, _, v_cost, v_mode_lbl = v_modes[self.vietlott_mode_idx % len(v_modes)]
        viet_buy_lbl = self._t(
            f"4.BUY TICKET {v_code} (-${v_cost}) [F9: Buy | F10: Draw 18:00]",
            f"4.MUA VE {v_code} (-${v_cost}) [F9: Mua Ve | F10: Quay 18:00]",
        )
        viet_balls_hyphen = self._normalize_vietlott_picks(self.custom_vietlott_str).replace(" ", "-")

        k_modes = self._get_keno_modes()
        _, _, keno_mode_lbl = k_modes[self.keno_mode_idx % len(k_modes)]

        xskt_tks = [t for t in self.lottery["tickets"] if t["type"] in ("XSKT_6D", "LODE_DE", "LODE_LO2", "LODE_3CANG")]
        viet_tks = [t for t in self.lottery["tickets"] if t["type"] in ("MEGA_645", "POWER_655", "MEGA_BAO7", "POWER_BAO7")]
        no_tk_lbl = self._t("None", "Chua co ve")
        xskt_tk_preview = ", ".join(f"{t['type']}[{t['numbers']}]" for t in xskt_tks[-2:]) if xskt_tks else no_tk_lbl
        viet_tk_preview = ", ".join(f"{t['type']}[{t['numbers'].replace(' ', '-')}]" for t in viet_tks[-2:]) if viet_tks else no_tk_lbl

        # App 6 Newspaper: 4 Topic Sub-pages with Anime Header Banners
        sec_Idx4 = self.news_sec_idx % 4
        topic_banners = ["ep_bn_pol", "ep_bn_fin", "ep_bn_wibu", "ep_bn_spt"]
        if self._is_vi():
            topic_titles = [
                "1/4: THE GIOI & CHINH TRI QUOC TE",
                "2/4: THI TRUONG CHUNG KHOAN & VANG",
                "3/4: CRYPTO, CONG NGHE & ANIME WIBU",
                "4/4: TOAN CANH BONG DA & THE THAO",
            ]
            step_names = ["Lui 1 Ngay (-1d)", "Qua 1 Ngay (+1d)", "Tua 1 Tuan (+7d)", "Tua 1 Thang (+30d)"]
        else:
            topic_titles = [
                "1/4: WORLD & GEOPOLITICAL DESK",
                "2/4: WALL STREET, STOCKS & GOLD",
                "3/4: CRYPTO, TECH & ANIME CULTURE",
                "4/4: GLOBAL FOOTBALL & PRO SPORTS",
            ]
            step_names = ["Back 1 Day (-1d)", "Next 1 Day (+1d)", "Skip 1 Week (+7d)", "Skip 1 Month (+30d)"]

        pol_full = self.newspaper.get("pol_lines") or wrap_hud_lines(self.newspaper.get("politics", ""), 54, 5)
        fin_full = self.newspaper.get("fin_lines") or wrap_hud_lines(self.newspaper.get("finance", ""), 54, 5)
        cry_full = self.newspaper.get("cry_lines") or wrap_hud_lines(self.newspaper.get("crypto", ""), 54, 5)
        spt_full = self.newspaper.get("spt_lines") or wrap_hud_lines(self.newspaper.get("sports", ""), 54, 5)

        topic_cards = [pol_full, fin_full, cry_full, spt_full]
        active_card_lines = [to_clean_viet_ascii(ln) for ln in list(topic_cards[sec_Idx4])[:5]]
        while len(active_card_lines) < 5:
            active_card_lines.append("")

        if (self.news_sec_idx % 2) == 0:
            news_lines = list(pol_full[:4]) + list(fin_full[:4])
        else:
            news_lines = list(cry_full[:4]) + list(spt_full[:4])
        while len(news_lines) < 8:
            news_lines.append("")

        # App 7 Portfolio Gauge Bars & 5-row Structured Table
        total_pos_assets = max(
            1.0,
            float(self.cash + self.bank + self.savings)
            + float(port_data["stocks_spot_val"])
            + float(port_data["crypto_spot_val"])
            + float(max(0.0, port_data["fut_equity"]) + port_data["bets_stake"] + port_data["lotto_pending_cost"]),
        )
        cash_bank_val = self.cash + self.bank + self.savings
        stck_val = int(round(port_data["stocks_spot_val"]))
        cryp_val = int(round(port_data["crypto_spot_val"]))
        fut_bet_val = int(round(max(0.0, port_data["fut_equity"]) + port_data["bets_stake"] + port_data["lotto_pending_cost"]))

        pct_cash = min(100, max(0, int(round((cash_bank_val / total_pos_assets) * 100))))
        pct_stck = min(100, max(0, int(round((stck_val / total_pos_assets) * 100))))
        pct_cryp = min(100, max(0, int(round((cryp_val / total_pos_assets) * 100))))
        pct_fut = min(100, max(0, int(round((fut_bet_val / total_pos_assets) * 100))))

        pt_rows = []
        p_tab = self.port_tab_idx % 3
        if p_tab == 1:
            for h in port_data["spot_holdings"][:5]:
                pt_rows.append((
                    h["symbol"],
                    f"{h['qty']:.2f}",
                    f"${int(round(h['val'])):,}",
                    f"{h['pnl_pct']:+.1f}%",
                ))
        elif p_tab == 2:
            for f in port_data["open_futures"][:3]:
                pt_rows.append((
                    f"{f['side'][0]}.{f['leverage']}x {f['symbol']}",
                    f"${f['margin']:,}",
                    f"${f['mark']}",
                    f"{f['roe_pct']:+.0f}%",
                ))
            for b in port_data["active_bets"][: (5 - len(pt_rows))]:
                pt_rows.append((
                    to_clean_viet_ascii(b["match"][:12]),
                    f"${b['stake']:,}",
                    f"{b['odd']:.2f}x",
                    f"+${b['potential_payout']:,}",
                ))
        while len(pt_rows) < 5:
            pt_rows.append(("", "", "", ""))

        # App 8 Structured Suspects Table (5 rows x 4 cols)
        scan_suspects = (bug_data.get("live_scan") or {}).get("suspects") or []
        bg_rows = []
        for s in scan_suspects[:5]:
            bg_rows.append((
                str(s["model_id"]),
                to_clean_viet_ascii(f"{s['dff_name'][:12]}.dff"),
                f"{s['surface_dist']}m",
                f"{s['col_faces']}F/{s['col_boxes']}B",
            ))
        while len(bg_rows) < 5:
            bg_rows.append(("", "", "", ""))

        loan_st = self._t("Safe (No Overdue Debt)", "An Toan (Khong No Qua Han)")
        if self.loan > 0:
            if self.loan_overdue:
                loan_st = self._t("OVERDUE! DRAINING HP (-2 HP)!", "QUA HAN! DANG TRU MAU (-2 HP)!")
            else:
                loan_st = self._t(
                    f"{self.loan_days_left} days left (3%/day interest)",
                    f"Con {self.loan_days_left} ngay (Lai 3%/ngay)",
                )

        now = time.time()
        ev_active = "1" if now < self.event_banner.get("until", 0) else "0"

        h_apps = self._get_home_apps()
        if self.keypad_active:
            if self.keypad_target == "lotto":
                lbl = self._t("TYPING 6-DIGIT XSKT", "GO 6 SO XSKT")
            elif self.keypad_target == "vietlott":
                lbl = self._t("TYPING VIETLOTT BALLS", "GO BO BONG VIETLOTT")
            else:
                lbl = self._t("TYPING AMOUNT ($)", "GO SO TIEN ($)")
            keypad_bar = self._t(
                f"[F6] {lbl}: [ {self.keypad_buffer or '_'} ] (0-9 Type, Backspace Del, F6/F9 Save)",
                f"[F6] DANG {lbl}: [ {self.keypad_buffer or '_'} ] (0-9 Go, Backspace Xoa, F6/F9 Luu)",
            )
        elif self.phone_app == 0:
            _, _, h_name, h_desc = h_apps[self.home_cursor_idx % len(h_apps)]
            keypad_bar = self._t(
                f"[{self.home_cursor_idx+1}/{len(h_apps)}] {h_name}: {h_desc} (I/K/J/L Select | F9 Open App)",
                f"[{self.home_cursor_idx+1}/{len(h_apps)}] {h_name}: {h_desc} (I/K/J/L Chon | F9 Mo App)",
            )
        elif self.phone_app == 10:
            keypad_bar = self._t(
                "GG Map: J/L Tab (10 Tabs) | I/K Select POI | F9 Set GPS | F10 Clear GPS",
                "GG Map: J/L Doi Tab (10 Tab) | I/K Chon Diem | F9 Cam Moc GPS | F10 Huy GPS",
            )
        else:
            keypad_bar = self._t(
                f"Tx Amt: ${self.tx_amount:,} | F6: Keypad | Backspace/F8: Back | Ctrl+F11: Bug",
                f"Von GD: ${self.tx_amount:,} | F6: Go So | Backspace/F8: Quay Lai | Ctrl+F11: Bug",
            )

        telem = bug_data["live_telemetry"]
        safe_r = telem["safe_recall"]

        wp_tex, wp_lbl = WALLPAPER_PRESETS[self.wp_idx % len(WALLPAPER_PRESETS)]
        ms_tex, ms_lbl = MASCOT_PRESETS[self.mascot_idx % len(MASCOT_PRESETS)]
        th_id, th_lbl = THEME_PRESETS[self.theme_idx % len(THEME_PRESETS)]
        cur_sub = self.app_subpage.get(self.phone_app, 0)
        lotto_subs = self._get_lotto_subpages()
        lang_lbl = "TIENG VIET (VI)" if self._is_vi() else "ENGLISH (EN)"

        kv = {
            "open": str(self.phone_open),
            "app": str(self.phone_app),
            "subpage": str(cur_sub),
            "lang": self.lang,
            "lang_lbl": lang_lbl,
            "home_idx": str(self.home_cursor_idx % len(h_apps)),
            "wp_tex": wp_tex,
            "wp_lbl": wp_lbl,
            "mascot_tex": ms_tex,
            "mascot_lbl": ms_lbl,
            "theme_id": th_id,
            "theme_lbl": th_lbl,
            "cur_row": str(self.app_cursor.get(self.phone_app, 0)),
            "tx_amt": f"${self.tx_amount:,}",
            "keypad_active": "1" if self.keypad_active else "0",
            "keypad_bar": to_clean_viet_ascii(keypad_bar),
            "ev_active": ev_active,
            "ev_title": self.event_banner.get("title", ""),
            "ev_sub": self.event_banner.get("sub", ""),
            "ev_kind": self.event_banner.get("kind", "info"),
            "date_str": self.current_date.strftime("%d/%m/%Y"),
            "day_num": str(self.day),
            "bank": f"${self.bank:,}",
            "savings": f"${self.savings:,}",
            "loan": f"${self.loan:,}",
            "loan_status": to_clean_viet_ascii(loan_st),
            "net_worth": f"${net_worth:,}",
            "hunger": str(self.hunger),
            "energy": str(self.energy),
            "atm_dist": self.nearest_atm,
            "life_meal_opt": to_clean_viet_ascii(meal_labels[self.life_meal_idx % 3]),
            "life_bank_opt": to_clean_viet_ascii(bank_labels[self.life_bank_idx % 4]),
            "life_loan_opt": to_clean_viet_ascii(loan_labels[self.life_loan_idx % 3]),
            "ticker": f"{cur_asset['symbol']} - {to_clean_viet_ascii(cur_asset['name'])} ({cur_asset['category']})",
            "sym_short": cur_asset["symbol"],
            "price": f"${cur_asset['price']}",
            "delta": f"{cur_asset['delta_pct']:+.2f}%",
            "delta_pos": "1" if cur_asset["delta_pct"] >= 0 else "0",
            "chart_pts": ",".join(pts),
            "spot_info": f"Spot: {cur_asset['spot_qty']:.3f} {cur_asset['symbol']} (${int(cur_asset['spot_val']):,})",
            "trade_mode_opt": self._t(
                f"{trade_mode_lbl} (Amt ${self.tx_amount:,})",
                f"{trade_mode_lbl} (Von ${self.tx_amount:,})",
            ),
            "fut_info": to_clean_viet_ascii(fut_str),
            "mw_page_info": self._t(
                f"Item {sel_sym_idx+1}/{len(syms_list)} (I/K Select, F9/Enter Open Chart)",
                f"Muc {sel_sym_idx+1}/{len(syms_list)} (I/K Chon Ma, F9/Enter Mo Bieu Do)",
            ),
            "league_page": to_clean_viet_ascii(
                self._t(
                    f"League {self.selected_league_idx+1}/5: {active_lg['name']} ({lg_matches[0]['round_label'] if lg_matches else ''})",
                    f"Giai {self.selected_league_idx+1}/5: {active_lg['name']} ({lg_matches[0]['round_label'] if lg_matches else ''})",
                )
            ),
            "sport_sel_idx": str(sel_m_idx + 1),
            "sport_m1": match_rows[0],
            "sport_m2": match_rows[1],
            "sport_m3": match_rows[2],
            "sport_m4": match_rows[3],
            "sport_m5": match_rows[4],
            "sport_pick_opt": to_clean_viet_ascii(sport_pick_str),
            "sport_pick_idx": str(self.sport_pick_idx % 5),
            "sport_vs": sel_match_vs,
            "sport_meta": sel_match_meta,
            "sp_odd_1": sel_odds[0],
            "sp_odd_2": sel_odds[1],
            "sp_odd_3": sel_odds[2],
            "sp_odd_4": sel_odds[3],
            "sp_odd_5": sel_odds[4],
            "st_r1": st_strs[0],
            "st_r2": st_strs[1],
            "st_r3": st_strs[2],
            "st_r4": st_strs[3],
            "sport_news": to_clean_viet_ascii(self.sport_history[0][:62] if self.sport_history else self._t("Ready", "San sang")),
            "jackpot": f"${self.lottery['jackpot']:,}",
            "jp_mega645": f"${self.lottery['jackpot_mega645']:,}",
            "jp_power655_1": f"${self.lottery['jackpot_power655_jp1']:,}",
            "jp_power655_2": f"${self.lottery['jackpot_power655_jp2']:,}",
            "lotto_page_opt": lotto_subs[self.app_subpage.get(5, 0) % 4],
            "lotto_mode_opt": to_clean_viet_ascii(lotto_mode_lbl),
            "lotto_tier_opt": scratch_tier_lbl,
            "lotto_scratch_cost": f"${sc_cost_val}",
            "lotto_num_opt": self._t(
                f"Pick: [ {self.custom_lotto_str} ] (J/L Cycle | F6 Type 6D)",
                f"So Chon: [ {self.custom_lotto_str} ] (J/L Doi | F6 Go 6 So)",
            ),
            "lotto_my_balls": self.custom_lotto_str,
            "lotto_drawn_balls": self.lottery["last_6d"],
            "lotto_scratch": to_clean_viet_ascii(self.lottery["last_scratch_msg"][:62]),
            "lotto_6d": self._t(
                f"XSKT (16:30): {self.lottery['last_6d']} | 1st: {self.lottery.get('last_xskt_g1', '49201')}",
                f"XSKT (16:30): {self.lottery['last_6d']} | G.Nhat: {self.lottery.get('last_xskt_g1', '49201')}",
            ),
            "lotto_tickets_cnt": self._t(
                f"Pending Tickets: {len(self.lottery['tickets'])} (Press F10 Draw Now)",
                f"Ve Cho Quay: {len(self.lottery['tickets'])} ve (Bam F10 Quay Ngay)",
            ),
            "xskt_mode_opt": x_mode_lbl,
            "xskt_buy_lbl": xskt_buy_lbl,
            "xskt_g1_str": self.lottery.get("last_xskt_g1", "49201"),
            "xskt_lo_str": ", ".join((self.lottery.get("last_xskt_lo18") or [])[:8]),
            "xskt_tickets_str": self._t(
                f"Pending XSKT/2D for 16:30 ({len(xskt_tks)}): {xskt_tk_preview}",
                f"Ve XSKT/Lo De cho 16:30 ({len(xskt_tks)}): {xskt_tk_preview}",
            ),
            "viet_mode_code": v_code,
            "viet_mode_opt": v_mode_lbl,
            "viet_my_balls": viet_balls_hyphen,
            "viet_mega_res": self.lottery.get("last_mega645", "05-12-19-26-38-44"),
            "viet_power_res": self.lottery.get("last_power655", "03-14-22-37-48-54"),
            "viet_power_bonus": self.lottery.get("last_power655_bonus", "18"),
            "viet_buy_lbl": viet_buy_lbl,
            "viet_tickets_str": self._t(
                f"Pending Vietlott for 18:00 ({len(viet_tks)}): {viet_tk_preview}",
                f"Ve Vietlott cho 18:00 ({len(viet_tks)}): {viet_tk_preview}",
            ),
            "keno_mode_opt": keno_mode_lbl,
            "keno_balls_str": self.lottery.get("last_keno_balls", "04-09-15-22-31-38-45-52-67-78"),
            "keno_meta_str": to_clean_viet_ascii(self.lottery.get("last_keno_meta", ""))[:64],
            "keno_msg_str": to_clean_viet_ascii(self.lottery.get("last_keno_msg", ""))[:64],

            "news_banner_tex": topic_banners[sec_Idx4],
            "news_topic_title": topic_titles[sec_Idx4],
            "news_sec_opt": topic_titles[sec_Idx4],
            "news_step_opt": to_clean_viet_ascii(step_names[self.news_step_idx % 4]),
            "news_c1": active_card_lines[0],
            "news_c2": active_card_lines[1],
            "news_c3": active_card_lines[2],
            "news_c4": active_card_lines[3],
            "news_c5": active_card_lines[4],
            "news_l1": news_lines[0],
            "news_l2": news_lines[1],
            "news_l3": news_lines[2],
            "news_l4": news_lines[3],
            "news_l5": news_lines[4],
            "news_l6": news_lines[5],
            "news_l7": news_lines[6],
            "news_l8": news_lines[7],
            "port_tab_idx": str(p_tab),
            "port_tab_opt": to_clean_viet_ascii(port_tabs[p_tab]),
            "port_pct_cash": str(pct_cash),
            "port_pct_stck": str(pct_stck),
            "port_pct_cryp": str(pct_cryp),
            "port_pct_fut": str(pct_fut),
            "port_val_cash": f"${cash_bank_val:,}",
            "port_val_stck": f"${stck_val:,} ({port_data['stocks_spot_pnl']:+.0f}$)",
            "port_val_cryp": f"${cryp_val:,} ({port_data['crypto_spot_pnl']:+.0f}$)",
            "port_val_fut": f"${fut_bet_val:,} (PnL {port_data['fut_pnl']:+.0f}$)",
            "port_l1": port_data["hud_lines"][0],
            "port_l2": port_data["hud_lines"][1],
            "port_l3": port_data["hud_lines"][2],
            "port_l4": port_data["hud_lines"][3],
            "port_l5": port_data["hud_lines"][4],
            "port_l6": port_data["hud_lines"][5],
            "port_l7": port_data["hud_lines"][6],
            "port_l8": port_data["hud_lines"][7],
            "bug_coords": self._t(
                f"X:{telem['x']:.1f}  Y:{telem['y']:.1f}  Z:{telem['z']:.1f}  (Hdg:{telem['heading']:.0f}o)",
                f"X:{telem['x']:.1f}  Y:{telem['y']:.1f}  Z:{telem['z']:.1f}  (Goc:{telem['heading']:.0f}o)",
            ),
            "bug_state": to_clean_viet_ascii(
                self._t(
                    f"Int:{telem['area_code']}/{telem['game_area']} | Vz:{telem['vz']:+.2f} | {'IN VEHICLE' if telem['in_vehicle'] else 'ON FOOT'} | Saved:{bug_data['reports_count']}",
                    f"Int:{telem['area_code']}/{telem['game_area']} | Vz:{telem['vz']:+.2f} | {'LAI XE' if telem['in_vehicle'] else 'DI BO'} | Luu:{bug_data['reports_count']}",
                )
            ),
            "bug_zone": to_clean_viet_ascii(
                self._t(
                    f"Zone: {telem['zone_label']} | Safe (-3s): ({safe_r['x']:.1f}, {safe_r['y']:.1f}, {safe_r['z']:.1f})",
                    f"Khu vuc: {telem['zone_label']} | An toan (-3s): ({safe_r['x']:.1f}, {safe_r['y']:.1f}, {safe_r['z']:.1f})",
                )
            ),
            "bug_trail": to_clean_viet_ascii(telem["trail_str"]),
            "bug_cat_opt": to_clean_viet_ascii(bug_data["selected_category_label"]),
            "bug_unstuck_opt": to_clean_viet_ascii(bug_data["selected_unstuck_label"]),
            "bug_l1": bug_data["hud_lines"][0],
            "bug_l2": bug_data["hud_lines"][1],
            "bug_l3": bug_data["hud_lines"][2],
            "bug_l4": bug_data["hud_lines"][3],
            "bug_l5": bug_data["hud_lines"][4],
            "bug_l6": bug_data["hud_lines"][5],
            "dbg_mode": dbg_proj["mode"],
            "dbg_mode_badge": to_clean_viet_ascii(dbg_proj["mode_badge"]),
            "dbg_probe_active": "1" if dbg_proj["probe_active"] else "0",
            "dbg_suite_opt": to_clean_viet_ascii(dbg_proj["selected_suite_label"]),
            "dbg_l1": to_clean_viet_ascii(dbg_proj["hud_lines"][0]),
            "dbg_l2": to_clean_viet_ascii(dbg_proj["hud_lines"][1]),
            "dbg_l3": to_clean_viet_ascii(dbg_proj["hud_lines"][2]),
            "dbg_l4": to_clean_viet_ascii(dbg_proj["hud_lines"][3]),
            "dbg_l5": to_clean_viet_ascii(dbg_proj["hud_lines"][4]),
            "dbg_l6": to_clean_viet_ascii(dbg_proj["hud_lines"][5]),
            "ggmap_cat_opt": to_clean_viet_ascii(ggmap_data["selected_cat_label"]),
            "ggmap_cat_idx": str(ggmap_data["selected_cat_idx"]),
            "ggmap_count_str": self._t(
                f"{ggmap_data['selected_poi_idx']+1}/{ggmap_data['cat_pois_count']} POIs ({ggmap_data['total_pois']} map-wide)",
                f"{ggmap_data['selected_poi_idx']+1}/{ggmap_data['cat_pois_count']} diem ({ggmap_data['total_pois']} POI toan map)",
            ),
            "ggmap_gps_active": ggmap_data["gps_active_str"],
            "ggmap_gps_bar": ggmap_data["gps_bar"],
            "ggmap_sel_title": ggmap_data["sel_title"],
            "ggmap_sel_coords": ggmap_data["sel_coords"],
            "ggmap_sel_note": ggmap_data["sel_note"],
            "toast": to_clean_viet_ascii(self.last_toast[:66]),
        }

        for idx_g, gr in enumerate(ggmap_data["table_rows"], start=1):
            kv[f"gm_r{idx_g}_name"] = gr["name"]
            kv[f"gm_r{idx_g}_reg"] = gr["region"]
            kv[f"gm_r{idx_g}_dist"] = gr["dist"]
            kv[f"gm_r{idx_g}_dir"] = gr["compass"]
            kv[f"gm_r{idx_g}_sel"] = gr["sel"]
            kv[f"gm_r{idx_g}_gps"] = gr["gps"]

        for idx_r, mr in enumerate(mw_rows, start=1):
            kv[f"mw_r{idx_r}_sym"] = mr["sym"]
            kv[f"mw_r{idx_r}_name"] = mr["name"]
            kv[f"mw_r{idx_r}_price"] = mr["price"]
            kv[f"mw_r{idx_r}_delta"] = mr["delta"]
            kv[f"mw_r{idx_r}_pos"] = mr["pos"]
            kv[f"mw_r{idx_r}_spot"] = mr["spot"]
            kv[f"mw_r{idx_r}_sel"] = mr["sel"]

        for idx_s, sr in enumerate(sp_table, start=1):
            kv[f"sp_r{idx_s}_time"] = sr["time"]
            kv[f"sp_r{idx_s}_match"] = sr["match"]
            kv[f"sp_r{idx_s}_odds"] = sr["odds"]
            kv[f"sp_r{idx_s}_ou"] = sr["ou"]
            kv[f"sp_r{idx_s}_bet"] = sr["bet"]

        for idx_c, cell_v in enumerate(sc_cells, start=1):
            kv[f"sc_c{idx_c}"] = cell_v

        for idx_p, pr in enumerate(pt_rows, start=1):
            kv[f"pt_r{idx_p}_c1"] = pr[0]
            kv[f"pt_r{idx_p}_c2"] = pr[1]
            kv[f"pt_r{idx_p}_c3"] = pr[2]
            kv[f"pt_r{idx_p}_c4"] = pr[3]

        for idx_b, br in enumerate(bg_rows, start=1):
            kv[f"bg_r{idx_b}_c1"] = br[0]
            kv[f"bg_r{idx_b}_c2"] = br[1]
            kv[f"bg_r{idx_b}_c3"] = br[2]
            kv[f"bg_r{idx_b}_c4"] = br[3]

        kv.update(self.paimon.hud())
        vis_sig = "|".join(f"{k}={kv[k]}" for k in sorted(kv.keys()))

        try:
            if force or vis_sig != self._last_lua_payload or not self.hud_lua_path.exists():
                self._last_lua_payload = vis_sig
                lua_lines = ["EaglePhoneState = EaglePhoneState or {}"]
                for k, v in kv.items():
                    safe_v = str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")
                    lua_lines.append(f'EaglePhoneState.{k} = "{safe_v}"')
                lua_payload = "\n".join(lua_lines) + "\n"

                self.state_version += 1
                slot = self.state_version % 2
                slot_path = self.cleo_dir / f"EaglePhoneState_{slot}.lua"
                slot_path.write_text(lua_payload, encoding="utf-8")
                if force or not (self.cleo_dir / f"EaglePhoneState_{1 - slot}.lua").exists():
                    (self.cleo_dir / f"EaglePhoneState_{1 - slot}.lua").write_text(lua_payload, encoding="utf-8")
                self.hud_lua_path.write_text(lua_payload, encoding="utf-8")
                self.hud_dat_path.write_text("\n".join(f"{k}={v}" for k, v in kv.items()) + "\n", encoding="utf-8")

            self._sync_ram_mailbox()
        except Exception as e:
            self.debug_sys.logger.log_exception("EagleCompanion", "_write_hud_dat", e)

    def get_state(self) -> dict:
        port_data = self._build_portfolio_data()
        bug_data = self._build_bug_inspector_data()
        ggmap_data = self._build_ggmap_data()
        dbg_proj = self.debug_sys.build_hud_and_web_projection(self)
        net_worth = port_data["total_net_worth"]
        if self.loan == 0:
            loan_st = self._t("Safe", "An Toàn")
        elif self.loan_overdue:
            loan_st = self._t("🩸 OVERDUE (Draining HP!)", "🩸 QUÁ HẠN (Đang trừ máu!)")
        else:
            loan_st = self._t(f"{self.loan_days_left} days left (3%/day)", f"Còn {self.loan_days_left} ngày (3%/ngày)")
        wp_tex, wp_lbl = WALLPAPER_PRESETS[self.wp_idx % len(WALLPAPER_PRESETS)]
        ms_tex, ms_lbl = MASCOT_PRESETS[self.mascot_idx % len(MASCOT_PRESETS)]
        th_id, th_lbl = THEME_PRESETS[self.theme_idx % len(THEME_PRESETS)]
        h_apps = self._get_home_apps()
        return {
            "paimon": self.paimon.snapshot(),
            "lang": self.lang,
            "player": {
                "date_str": self.current_date.strftime("%d/%m/%Y"),
                "day": self.day,
                "clock": self.clock_str,
                "cash": self.cash,
                "bank": self.bank,
                "savings": self.savings,
                "loan": self.loan,
                "loan_status": loan_st,
                "health": self.health,
                "max_health": self.max_health,
                "armor": self.armor,
                "hunger": self.hunger,
                "energy": self.energy,
                "net_worth": net_worth,
                "ram_attached": self.ram_attached,
                "pos": list(self.player_pos),
                "heading": self.player_heading,
                "velocity": list(self.player_velocity),
                "area_code": self.player_area_code,
                "game_area": self.player_game_area,
                "in_vehicle": self.player_in_vehicle,
            },
            "ui_v5": {
                "lang": self.lang,
                "lang_lbl": "TIENG VIET (VI)" if self._is_vi() else "ENGLISH (EN)",
                "phone_open": self.phone_open,
                "phone_app": self.phone_app,
                "home_cursor_idx": self.home_cursor_idx,
                "app_subpage": {str(k): v for k, v in self.app_subpage.items()},
                "wp_idx": self.wp_idx,
                "wp_tex": wp_tex,
                "wp_lbl": wp_lbl,
                "wp_name": wp_lbl,
                "mascot_idx": self.mascot_idx,
                "mascot_tex": ms_tex,
                "mascot_lbl": ms_lbl,
                "mascot_name": ms_lbl,
                "theme_idx": self.theme_idx,
                "theme_id": th_id,
                "theme_lbl": th_lbl,
                "theme_name": th_lbl,
                "home_apps": [
                    {"id": aid, "tex": tex, "name": name, "sub": sub}
                    for (aid, tex, name, sub) in h_apps
                ],
                "wallpapers": [
                    {"tex": tex, "name": lbl, "sub": "256x512 Anime TXD"}
                    for (tex, lbl) in WALLPAPER_PRESETS
                ],
                "mascot_presets": [
                    {
                        "tex": tex,
                        "name": lbl,
                        "greeting": self._t(
                            "Hi Aether! Wishing you a great cruise & big market wins~",
                            "Chào Aether! Chúc một ngày dạo phố & đầu tư đại thắng~",
                        ),
                    }
                    for (tex, lbl) in MASCOT_PRESETS
                ],
                "theme_presets": [
                    {"id": tid, "name": tlbl}
                    for (tid, tlbl) in THEME_PRESETS
                ],
            },
            "selected_league_idx": self.selected_league_idx,
            "nearest_atm": self.nearest_atm,
            "last_toast": self.last_toast,
            "stocks_market": self.stocks_market,
            "crypto_market": self.crypto_market,
            "futures": self.futures,
            "fixtures": self.fixtures,
            "standings": self.standings,
            "sport_history": self.sport_history[:15],
            "lottery": self.lottery,
            "newspaper": self.newspaper,
            "portfolio": port_data,
            "bug_inspector": bug_data,
            "debug_system": dbg_proj,
            "ggmap": ggmap_data,
            "gg_map": ggmap_data,
        }


ENGINE: EagleCompanionEngine = None


class ExclusiveHTTPServer(HTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        import socket
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class CompanionHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == "/api/state":
            with ENGINE.lock:
                ENGINE.sync_player_state()
                data = json.dumps(ENGINE.get_state()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(data)
        elif self.path.startswith("/assets/"):
            fname = Path(self.path.split("?")[0]).name
            asset_path = ENGINE.base_dir / "ui_assets" / fname
            if not asset_path.exists():
                alt = ENGINE.base_dir.parent.parent / "staging" / "project-eagle" / "gameplay-lab-poc" / "ui_assets" / fname
                if alt.exists():
                    asset_path = alt
            if asset_path.exists() and asset_path.suffix.lower() == ".png":
                raw = asset_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(raw)
            else:
                self.send_response(404)
                self.end_headers()
        else:
            body = EAGLE_PHONE_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)

    def do_POST(self):
        if self.path == "/api/action":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8", errors="ignore")
            payload = json.loads(raw) if raw else {}
            state = ENGINE.handle_action(payload)
            data = json.dumps(state).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(data)


def main():
    global ENGINE
    mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\EaglePhoneOS_SingleInstance_v3")
    if ctypes.windll.kernel32.GetLastError() == 183:
        print("EaglePhone Sidecar is already running (Mutex locked). Exiting duplicate instance.")
        return

    try:
        server = ExclusiveHTTPServer(("127.0.0.1", 8765), wrap_handler(CompanionHTTPHandler, Path(__file__).resolve().parent))
    except OSError:
        print("EaglePhone Sidecar is already running on http://127.0.0.1:8765.")
        return

    base_dir = Path(__file__).resolve().parent
    ENGINE = EagleCompanionEngine(base_dir)

    def sim_worker():
        while True:
            try:
                ENGINE.step_simulation()
            except Exception as e:
                print("Sim error:", e)
                ENGINE.debug_sys.logger.log_exception("EagleCompanion", "sim_worker", e)
            time.sleep(2.0)

    def hotkey_worker():
        while True:
            try:
                ENGINE.poll_ingame_hotkeys()
            except Exception as e:
                ENGINE.debug_sys.logger.log_exception("EagleCompanion", "hotkey_worker", e)
            time.sleep(0.025)

    threading.Thread(target=sim_worker, daemon=True).start()
    threading.Thread(target=hotkey_worker, daemon=True).start()

    print("==================================================================")
    print(" EaglePhone OS v5.0 Running on http://127.0.0.1:8765")
    print(" - Home Screen 3x3 Grid + Anime Textures (.txd) + Sub-pages")
    print(" - Ctrl+F11: Instant Map Bug Report + Auto-Inspector (.ipl/.ide/.img/.col)")
    print(" - Ctrl+Shift+F11: Toggle On-Demand DEEP DEBUG vs LITE (0% Overhead)")
    print(" - F12: Instant Safe Recall / Unstuck (or Abort Auto-Probe Tour)")
    print(" - I/K/J/L: Navigate | F9/Enter: Open/OK | Backspace/F8: Back/Home")
    print("==================================================================")
    server.serve_forever()


if __name__ == "__main__":
    main()
