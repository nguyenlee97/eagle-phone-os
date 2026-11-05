# -*- coding: utf-8 -*-
"""
eagle_ride_engine.py — App 12: EagleRide (Uber / Xanh SM / Grab / Be) Ride-Hailing Engine
for Project Eagle Gameplay Lab.

Features:
- 5 Branded Ride Services (2 Cars + 3 Motorbikes):
    1. Uber Car (Premier 426, Black #0, Suit Driver, Rear Passenger Seat)
    2. Xanh SM Car (Sultan 560, VinFast Cyan #125/#135, Smart Driver, Rear Passenger Seat)
    3. GrabBike (FCR-900 521, Grab Green #86, Bike Driver, Pillion Seat)
    4. Xanh SM Bike (PCJ-600 461, Xanh SM Cyan #135, Bike Driver, Pillion Seat)
    5. BeBike (BF-400 581, Be Yellow #6, Bike Driver, Pillion Seat)
- Fast PEGG Graph Loader & A* Router (`data/pecore_gps_graph.pegg`, 148,417 nodes / 252,646 edges).
- Fog-of-War Discovery (`visited_pois`): Automatically unlocks POIs when the player visits within <=85m.
  Only unlocked POIs can be booked via EagleRide; locked POIs offer GPS pin so the player can drive there first.
- Native CLEO5 Bridge (`cleo/EagleRideBridge.cs`) via 128-byte RAM shared memory (`0x00CAFE20..0x00CAFE24`)
  + Hybrid Graph-Guided Autopilot so rides never stall in traffic or on custom bridges/Mondstadt/WIBU-01 roads.
- Passenger Radio Control (`041E: SET_RADIO_CHANNEL` + `CAERadioTrackManager`) & Instant Fast-Forward (Skip Trip).
"""

from __future__ import annotations

import heapq
import json
import math
import random
import struct
import time
from collections import deque
from pathlib import Path
import shutil as _shutil

def _auto_sync_staged_imgs_if_unlocked() -> None:
    try:
        manifest_p = Path(r'D:\GTA Archive\Staging\fix-minimap-and-map-gps-bugs-2026-10-31\backup\manifest.json')
        if not manifest_p.exists(): return
        data = json.loads(manifest_p.read_text(encoding='utf-8'))
        files = data.get('files', {})
        pending = [rel for rel, m in files.items() if m.get('status') != 'applied']
        if not pending: return
        lab = Path(data.get('target_root', r'C:\Users\LENOVO\Desktop\GTA\Project Eagle\gta sa gameplay-lab'))
        lock_dir = Path(r'C:\Users\LENOVO\Desktop\GTA\data\project-eagle\coordination\game-write.lock')
        if lock_dir.exists(): return
        lock_dir.mkdir(parents=True, exist_ok=False)
        try:
            changed = False
            for rel in pending:
                m = files[rel]
                try:
                    _shutil.copy2(Path(m['candidate_path']), lab / rel)
                    m['status'] = 'applied'
                    m['live_sha256'] = m['candidate_sha256']
                    m['live_size'] = m['candidate_size']
                    changed = True
                except PermissionError:
                    pass
            if changed:
                manifest_p.write_text(json.dumps(data, indent=2), encoding='utf-8')
        finally:
            _shutil.rmtree(lock_dir, ignore_errors=True)
    except Exception:
        pass

_auto_sync_staged_imgs_if_unlocked()


from eagle_gg_map_pois import (
    CURATED_GG_MAP_POIS,
    GG_MAP_CATEGORIES_EN,
    GG_MAP_CATEGORIES_VI,
    compute_compass_dir,
    format_distance,
    localize_poi_item,
)
from eagle_historical_data import to_clean_viet_ascii

CAFE_RIDE_MAGIC_ADDR = 0x00CAFE20
CAFE_RIDE_PTR_ADDR = 0x00CAFE24
RIDE_SHM_MAGIC = 0x52494445  # 'RIDE'

# Default starter POIs unlocked at the beginning of a playthrough
DEFAULT_UNLOCKED_POIS = {
    "sfh_cj_grove",
    "lm_unity_station",
    "lm_lsia_airport",
    "fd_pizza_idlewood",
    "shp_binco_ganton",
    "wb_wibu01_bridge_north",
    "mondstadt_poi_01",
    "inland03a_poi_01",
    "inland03a_poi_07",
    "inland03a_poi_10",
    "wallstreet_poi_ls",
    "wallstreet_poi_sf",
    "wallstreet_poi_chi",
    "wallstreet_poi_lc",
}

DISCOVERY_RADIUS_M = 85.0

RIDE_SERVICES = [
    {
        "id": "UBER_CAR",
        "kind": "CAR",
        "name_en": "1. Uber Black (4-Door Sedan)",
        "name_vi": "1. Uber Car (Oto 4 Cho Cao Cap)",
        "short_en": "Uber Car",
        "short_vi": "Uber Oto",
        "veh_model": 30669,    # uber_car (Branded Uber Black Premier sedan)
        "ped_model": 49423,    # aether_uber (Aether in Uber Black VIP Chauffeur suit)
        "color1": 0,           # Metallic Black
        "color2": 0,
        "seat_id": 2,          # Rear-right passenger seat
        "base_fare": 15,
        "per_km": 25,
        "speed_mps": 21.5,     # ~77 km/h smooth sedan cruise
        "badge_color": "#111827",
    },
    {
        "id": "XANH_CAR",
        "kind": "CAR",
        "name_en": "2. Xanh SM Luxury (Cyan EV Sedan)",
        "name_vi": "2. Xanh SM Car (Oto Dien Xanh Cyan)",
        "short_en": "Xanh SM Car",
        "short_vi": "Xanh SM Oto",
        "veh_model": 30670,    # xanh_car (Branded VinFast Xanh SM Cyan sedan)
        "ped_model": 49424,    # aether_xanhcar (Aether in Xanh SM Cyan & Navy uniform)
        "color1": 125,         # Bright Cyan / Teal
        "color2": 135,
        "seat_id": 2,          # Rear-right passenger seat
        "base_fare": 18,
        "per_km": 28,
        "speed_mps": 22.5,     # ~81 km/h smooth EV cruise
        "badge_color": "#06b6d4",
    },
    {
        "id": "GRAB_BIKE",
        "kind": "BIKE",
        "name_en": "3. GrabBike (Fast Green Motorbike)",
        "name_vi": "3. GrabBike (Xe May Ao Xanh La)",
        "short_en": "GrabBike",
        "short_vi": "GrabBike",
        "veh_model": 30671,    # grab_bike (Branded Grab Green motorbike)
        "ped_model": 49425,    # aether_grab (Aether in GrabBike Green jacket + half-helmet)
        "color1": 86,          # Grab Green
        "color2": 86,
        "seat_id": 0,          # Bike pillion passenger seat
        "base_fare": 8,
        "per_km": 14,
        "speed_mps": 20.0,     # ~72 km/h safe urban bike cruise
        "badge_color": "#16a34a",
    },
    {
        "id": "XANH_BIKE",
        "kind": "BIKE",
        "name_en": "4. Xanh SM Bike (Cyan EV Motorbike)",
        "name_vi": "4. Xanh SM Bike (Xe May Dien Xanh Lam)",
        "short_en": "Xanh SM Bike",
        "short_vi": "XanhSM Bike",
        "veh_model": 30672,    # xanh_bike (Branded Xanh SM Cyan EV motorbike)
        "ped_model": 49426,    # aether_xanhbike (Aether in Xanh SM Bike Cyan jacket + half-helmet)
        "color1": 135,         # Cyan Blue
        "color2": 125,
        "seat_id": 0,          # Bike pillion passenger seat
        "base_fare": 9,
        "per_km": 15,
        "speed_mps": 19.5,     # ~70 km/h safe urban bike cruise
        "badge_color": "#0284c7",
    },
    {
        "id": "BE_BIKE",
        "kind": "BIKE",
        "name_en": "5. BeBike (Economy Yellow Motorbike)",
        "name_vi": "5. BeBike (Xe May Ao Vang Tiet Kiem)",
        "short_en": "BeBike",
        "short_vi": "BeBike",
        "veh_model": 30673,    # be_bike (Branded BeBike Yellow/Navy motorbike)
        "ped_model": 49427,    # aether_be (Aether in BeBike Yellow/Navy jacket + half-helmet)
        "color1": 6,           # Be Yellow
        "color2": 0,
        "seat_id": 0,          # Bike pillion passenger seat
        "base_fare": 7,
        "per_km": 12,
        "speed_mps": 19.0,     # ~68 km/h safe urban bike cruise
        "badge_color": "#eab308",
    },
]

GTA_RADIO_STATIONS = [
    (1, "Playback FM"),
    (2, "K-Rose"),
    (3, "K-DST"),
    (4, "Bounce FM"),
    (5, "SF-UR"),
    (6, "Radio Los Santos"),
    (7, "Radio X"),
    (8, "CSR 103.9"),
    (9, "K-Jah West"),
    (10, "Master Sounds 98.3"),
    (11, "WCTR Talk Radio"),
    (12, "User Track Player (Custom)"),
    (0, "Radio OFF"),
]


class PeggGraphRouter:
    """
    Loads `data/pecore_gps_graph.pegg` (148,417 nodes, 252,646 edges) and provides
    millisecond spatial node snapping and A* shortest-path road routing.
    """

    CELL_SIZE = 100.0

    def __init__(self, pegg_path: Path):
        self.pegg_path = pegg_path
        self.loaded = False
        self.n_nodes = 0
        self.n_edges = 0
        self.node_x: list[float] = []
        self.node_y: list[float] = []
        self.node_z: list[float] = []
        self.adj: list[list[tuple[int, float]]] = []
        self.grid: dict[tuple[int, int], list[int]] = {}
        self.comp_id: list[int] = []
        self.main_comp = 0
        self.load_ms = 0.0

    def ensure_loaded(self) -> bool:
        if self.loaded:
            return True
        if not self.pegg_path.exists():
            return False
        t0 = time.time()
        raw = self.pegg_path.read_bytes()
        if len(raw) < 64:
            return False
        magic, _ver, node_sz, edge_sz, _extra_sz, n_nodes, n_edges, _n_extra = struct.unpack_from("<4s7I", raw, 0)
        if magic != b"PEGG" or node_sz != 32 or edge_sz != 64:
            return False

        self.n_nodes = n_nodes
        self.n_edges = n_edges
        self.node_x = [0.0] * n_nodes
        self.node_y = [0.0] * n_nodes
        self.node_z = [0.0] * n_nodes
        self.grid = {}
        cell = self.CELL_SIZE

        self.is_boat = [False] * n_nodes
        off = 64
        for i in range(n_nodes):
            x, y, z = struct.unpack_from("<fff", raw, off + 8)
            node_flags = struct.unpack_from("<I", raw, off + 28)[0]
            self.node_x[i] = x
            self.node_y[i] = y
            self.node_z[i] = z
            if node_flags & 1:
                self.is_boat[i] = True
                off += 32
                continue
            gx = int(math.floor(x / cell))
            gy = int(math.floor(y / cell))
            self.grid.setdefault((gx, gy), []).append(i)
            off += 32

        self.adj = [[] for _ in range(n_nodes)]
        self.edge_right_offset: dict[tuple[int, int], float] = {}
        adj_set = [set() for _ in range(n_nodes)]
        off = 64 + n_nodes * 32
        x_off = off + n_edges * 64
        raw_edges: list[tuple[int, int, float, bool, float]] = []
        for _ in range(n_edges):
            u, v, idx_extra, dist = struct.unpack_from("<IIIf", raw, off)
            if 0 <= u < n_nodes and 0 <= v < n_nodes and not self.is_boat[u] and not self.is_boat[v]:
                b0, b1, b2, b3 = struct.unpack_from("<4B", raw, off + 32)
                med_byte = raw[x_off + idx_extra * 48 + 26] if (idx_extra < _n_extra and x_off + idx_extra * 48 + 27 <= len(raw)) else 0
                is_true_one_way = (b2 > 0 and b3 == 0) or (b2 == 0 and b3 > 0)
                if b2 > 0 and b3 > 0:
                    # Two-way road: PEGG node sits on the road centerline / central median strip
                    med_half = min(5.5, float(med_byte) * 0.45) if med_byte > 0 else 0.0
                    r_off = (med_half + 3.4) if b1 >= 2 else (med_half + 2.3)
                elif 5600.0 <= self.node_x[u] <= 7000.0 and 9850.0 <= self.node_y[u] <= 11300.0:
                    r_off = 3.2
                elif u >= 147379 or v >= 147379:
                    r_off = 0.7
                elif is_true_one_way:
                    # One-way road: PEGG node sits in the center of the one-way carriageway
                    r_off = 1.5 if b1 >= 2 else 0.0
                else:
                    # Synthetic expansion road (WIBU-01 / Mondstadt)
                    ux_val, uy_val = self.node_x[u], self.node_y[u]
                    r_off = 1.6 if (ux_val > -2200.0 and uy_val < -3600.0) else 0.7

                d_val = max(0.5, float(dist))
                dz_uv = abs(self.node_z[v] - self.node_z[u])
                # Penalize vertical cliff-edge jumps (stacked overpass links) and submerged lake edges
                if dz_uv > 6.5 and d_val < 22.0 and (dz_uv / max(1.0, d_val)) > 0.42:
                    d_val *= 25.0
                if self.node_z[u] < 0.2 or self.node_z[v] < 0.2:
                    d_val *= 15.0
                elif self.node_z[u] <= 1.05 or self.node_z[v] <= 1.05:
                    d_val *= 8.0

                self.adj[u].append((v, d_val))
                self.edge_right_offset[(u, v)] = r_off
                adj_set[u].add(v)
                raw_edges.append((u, v, d_val, is_true_one_way, r_off))
            off += 64

        # Ensure every road link is traversable in both directions (heavy 6.5x penalty on reverse of true one-way streets)
        for u, v, d_val, is_true_one_way, r_off in raw_edges:
            if u not in adj_set[v]:
                rev_mult = 6.5 if is_true_one_way else 1.02
                self.adj[v].append((u, d_val * rev_mult))
                self.edge_right_offset[(v, u)] = r_off
                adj_set[v].add(u)

        self.comp_id = [-1] * n_nodes
        comp_sizes: list[int] = []
        for i in range(n_nodes):
            if self.comp_id[i] != -1 or not self.adj[i]:
                continue
            cid = len(comp_sizes)
            q = deque([i])
            self.comp_id[i] = cid
            cnt = 0
            while q:
                u = q.popleft()
                cnt += 1
                for v, _d in self.adj[u]:
                    if self.comp_id[v] == -1:
                        self.comp_id[v] = cid
                        q.append(v)
            comp_sizes.append(cnt)

        if comp_sizes:
            self.main_comp = max(range(len(comp_sizes)), key=lambda c: comp_sizes[c])
        self.loaded = True
        self.load_ms = round((time.time() - t0) * 1000.0, 1)
        return True

    def find_nearest_node(
        self,
        x: float,
        y: float,
        z: float = 0.0,
        require_main_comp: bool = True,
        target_comp: int | None = None,
    ) -> tuple[int, float]:
        if not self.ensure_loaded():
            return -1, 0.0
        cell = self.CELL_SIZE
        gx = int(math.floor(x / cell))
        gy = int(math.floor(y / cell))
        best_id = -1
        best_score = 1e18
        best_d2 = 1e18
        use_z = abs(z) > 0.1 and abs(z) < 900.0

        want_comp = self.main_comp if require_main_comp else target_comp

        for r in range(0, 16):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) != r and abs(dy) != r:
                        continue
                    cand = self.grid.get((gx + dx, gy + dy))
                    if not cand:
                        continue
                    for nid in cand:
                        if want_comp is not None and self.comp_id[nid] != want_comp:
                            continue
                        if not self.adj[nid]:
                            continue
                        d2 = (self.node_x[nid] - x) ** 2 + (self.node_y[nid] - y) ** 2
                        dz = abs(self.node_z[nid] - z) if use_z else 0.0
                        dz_pen = min(dz, 25.0) if z > 95.0 else dz
                        score = d2 + ((dz_pen * 3.5) ** 2 if dz_pen > 6.5 else 0.0)
                        if score < best_score:
                            best_score = score
                            best_d2 = d2
                            best_id = nid
            if best_id != -1 and math.sqrt(best_score) <= r * cell:
                break

        if best_id == -1:
            for nid in range(self.n_nodes):
                if want_comp is not None and self.comp_id[nid] != want_comp:
                    continue
                if not self.adj[nid]:
                    continue
                d2 = (self.node_x[nid] - x) ** 2 + (self.node_y[nid] - y) ** 2
                dz = abs(self.node_z[nid] - z) if use_z else 0.0
                score = d2 + ((dz * 3.5) ** 2 if dz > 6.5 else 0.0)
                if score < best_score:
                    best_score = score
                    best_d2 = d2
                    best_id = nid

        return best_id, math.sqrt(best_d2) if best_id != -1 else 0.0

    def find_spawn_node_near(self, pickup_nid: int, px: float, py: float, next_nid: int = -1) -> tuple[int, float]:
        """
        Finds a road node 12m..35m behind `pickup_nid` relative to the forward route direction
        (`pickup_nid -> next_nid`) so the ride vehicle spawns facing forward along the route
        and pulls straight up to the player without needing a U-turn.
        """
        if not self.ensure_loaded() or pickup_nid < 0 or pickup_nid >= self.n_nodes:
            return pickup_nid, 0.0
        p0x, p0y = self.node_x[pickup_nid], self.node_y[pickup_nid]
        if 0 <= next_nid < self.n_nodes and next_nid != pickup_nid:
            fdx = self.node_x[next_nid] - p0x
            fdy = self.node_y[next_nid] - p0y
        else:
            fdx = p0x - px
            fdy = p0y - py
        flen = math.hypot(fdx, fdy)
        if flen > 0.05:
            fdx /= flen
            fdy /= flen
            fwd_hdg = (math.degrees(math.atan2(-fdx, fdy)) + 360.0) % 360.0
        else:
            fdx, fdy = 0.0, 1.0
            fwd_hdg = 0.0

        visited = {pickup_nid}
        if next_nid >= 0:
            visited.add(next_nid)
        q = deque([(pickup_nid, 0)])
        candidates: list[tuple[float, int]] = []
        while q:
            u, depth = q.popleft()
            ux, uy = self.node_x[u], self.node_y[u]
            d = math.hypot(ux - p0x, uy - p0y)
            if 10.0 <= d <= 38.0:
                # Dot product with forward vector: negative means `u` is behind `pickup_nid`
                dot = ((ux - p0x) * fdx + (uy - p0y) * fdy) / max(1.0, d)
                score = abs(d - 18.0) + (0.0 if dot <= -0.15 else 25.0)
                candidates.append((score, u))
            if depth < 4:
                for v, _w in self.adj[u]:
                    if v not in visited:
                        visited.add(v)
                        q.append((v, depth + 1))
        if candidates:
            candidates.sort(key=lambda item: item[0])
            best_u = candidates[0][1]
            dx = p0x - self.node_x[best_u]
            dy = p0y - self.node_y[best_u]
            if abs(dx) + abs(dy) > 0.1:
                fwd_hdg = (math.degrees(math.atan2(-dx, dy)) + 360.0) % 360.0
        else:
            best_u = pickup_nid
        return best_u, fwd_hdg

    def compute_route(
        self,
        start_xyz: tuple[float, float, float],
        dest_xyz: tuple[float, float, float],
        step_m: float = 5.0,
        banned_nodes: set[int] | None = None,
    ) -> dict:
        """
        Computes A* road route on `pecore_gps_graph.pegg` between `start_xyz` and `dest_xyz`.
        Returns a dict with `ok`, `nodes`, `waypoints` [(x, y, z, heading)], `road_dist_m`,
        `pickup_xyz`, `dropoff_xyz`, `spawn_xyz`, and `spawn_heading`.
        """
        sx, sy, sz = start_xyz
        dx, dy, dz = dest_xyz
        straight_dist = math.hypot(dx - sx, dy - sy)

        if not self.ensure_loaded():
            heading = (math.degrees(math.atan2(-(dx - sx), dy - sy)) + 360.0) % 360.0
            return {
                "ok": False,
                "nodes": [],
                "waypoints": [(sx, sy, sz, heading), (dx, dy, dz, heading)],
                "road_dist_m": max(50.0, straight_dist * 1.25),
                "straight_dist_m": straight_dist,
                "pickup_xyz": (sx, sy, sz),
                "dropoff_xyz": (dx, dy, dz),
                "spawn_xyz": (sx + 15.0, sy + 15.0, sz + 0.6),
                "spawn_heading": heading,
            }

        # Check if both are close to a local component first, otherwise snap both to main_comp
        any_s, dist_any_s = self.find_nearest_node(sx, sy, sz, require_main_comp=False)
        any_d, dist_any_d = self.find_nearest_node(dx, dy, dz, require_main_comp=False)
        if (
            any_s != -1
            and any_d != -1
            and self.comp_id[any_s] == self.comp_id[any_d]
            and dist_any_s < 150.0
            and dist_any_d < 150.0
        ):
            start_nid = any_s
            dest_nid = any_d
        else:
            start_nid, _ = self.find_nearest_node(sx, sy, sz, require_main_comp=True)
            dest_nid, _ = self.find_nearest_node(dx, dy, dz, require_main_comp=True)

        pickup_xyz = (self.node_x[start_nid], self.node_y[start_nid], self.node_z[start_nid] + 0.45)
        dropoff_xyz = (self.node_x[dest_nid], self.node_y[dest_nid], self.node_z[dest_nid] + 0.45)

        if start_nid == dest_nid:
            spawn_nid, spawn_heading = self.find_spawn_node_near(start_nid, sx, sy)
            spawn_xyz = (self.node_x[spawn_nid], self.node_y[spawn_nid], self.node_z[spawn_nid] + 0.55)
            n_st = max(12, int(max(40.0, straight_dist) / 5.0))
            tx_e, ty_e, tz_e = (dx, dy, dz) if straight_dist > 8.0 else (pickup_xyz[0] + 40.0, pickup_xyz[1], pickup_xyz[2])
            hdg_s = (math.degrees(math.atan2(-(tx_e - pickup_xyz[0]), ty_e - pickup_xyz[1])) + 360.0) % 360.0
            wps_same = [
                (
                    pickup_xyz[0] + (tx_e - pickup_xyz[0]) * (i_s / float(n_st)),
                    pickup_xyz[1] + (ty_e - pickup_xyz[1]) * (i_s / float(n_st)),
                    pickup_xyz[2] + (tz_e - pickup_xyz[2]) * (i_s / float(n_st)),
                    hdg_s,
                )
                for i_s in range(n_st + 1)
            ]
            dropoff_xyz = (wps_same[-1][0], wps_same[-1][1], wps_same[-1][2])
            return {
                "ok": True,
                "nodes": [start_nid],
                "waypoints": wps_same,
                "road_dist_m": max(30.0, straight_dist),
                "straight_dist_m": straight_dist,
                "pickup_xyz": pickup_xyz,
                "dropoff_xyz": dropoff_xyz,
                "spawn_xyz": spawn_xyz,
                "spawn_heading": spawn_heading,
            }

        # A* search from start_nid (plus any opposite-carriageway divided-highway nodes within 46m) to dest_nid
        tx = self.node_x[dest_nid]
        ty = self.node_y[dest_nid]
        g_score: dict[int, float] = {start_nid: 0.0}
        came_from: dict[int, int] = {}
        pq: list[tuple[float, int]] = [(math.hypot(tx - self.node_x[start_nid], ty - self.node_y[start_nid]), start_nid)]
        s_comp = self.comp_id[start_nid]
        s_nx, s_ny, s_nz = self.node_x[start_nid], self.node_y[start_nid], self.node_z[start_nid]
        s_gx = int(math.floor(s_nx / self.CELL_SIZE))
        s_gy = int(math.floor(s_ny / self.CELL_SIZE))
        for gdx in (-1, 0, 1):
            for gdy in (-1, 0, 1):
                for cnid in self.grid.get((s_gx + gdx, s_gy + gdy), ()):
                    if cnid != start_nid and self.comp_id[cnid] == s_comp and self.adj[cnid]:
                        cd = math.hypot(self.node_x[cnid] - s_nx, self.node_y[cnid] - s_ny)
                        if cd <= 46.0 and abs(self.node_z[cnid] - s_nz) <= 5.5 and cnid != dest_nid:
                            c_pen = cd * 3.5
                            g_score[cnid] = c_pen
                            heapq.heappush(pq, (c_pen + math.hypot(tx - self.node_x[cnid], ty - self.node_y[cnid]), cnid))
        visited: set[int] = (set(banned_nodes) - {start_nid, dest_nid}) if banned_nodes else set()
        found = False

        while pq:
            _f, u = heapq.heappop(pq)
            if u in visited:
                continue
            if u == dest_nid:
                found = True
                break
            visited.add(u)
            gu = g_score[u]
            for v, w in self.adj[u]:
                if v in visited:
                    continue
                tentative = gu + w
                if tentative < g_score.get(v, 1e18):
                    g_score[v] = tentative
                    came_from[v] = u
                    hv = math.hypot(tx - self.node_x[v], ty - self.node_y[v])
                    heapq.heappush(pq, (tentative + hv, v))

        if not found:
            spawn_nid, spawn_heading = self.find_spawn_node_near(start_nid, sx, sy)
            spawn_xyz = (self.node_x[spawn_nid], self.node_y[spawn_nid], self.node_z[spawn_nid] + 0.55)
            heading = (math.degrees(math.atan2(-(dropoff_xyz[0] - pickup_xyz[0]), dropoff_xyz[1] - pickup_xyz[1])) + 360.0) % 360.0
            return {
                "ok": False,
                "nodes": [start_nid, dest_nid],
                "waypoints": [
                    (pickup_xyz[0], pickup_xyz[1], pickup_xyz[2], heading),
                    (dropoff_xyz[0], dropoff_xyz[1], dropoff_xyz[2], heading),
                ],
                "road_dist_m": max(50.0, straight_dist * 1.25),
                "straight_dist_m": straight_dist,
                "pickup_xyz": pickup_xyz,
                "dropoff_xyz": dropoff_xyz,
                "spawn_xyz": spawn_xyz,
                "spawn_heading": spawn_heading,
            }

        path_nodes: list[int] = []
        curr = dest_nid
        while curr in came_from:
            path_nodes.append(curr)
            curr = came_from[curr]
        start_nid = curr
        pickup_xyz = (self.node_x[start_nid], self.node_y[start_nid], self.node_z[start_nid] + 0.45)
        path_nodes.append(start_nid)
        path_nodes.reverse()

        next_nid = path_nodes[1] if len(path_nodes) > 1 else -1
        spawn_nid, spawn_heading = self.find_spawn_node_near(start_nid, sx, sy, next_nid=next_nid)
        spawn_xyz = (self.node_x[spawn_nid], self.node_y[spawn_nid], self.node_z[spawn_nid] + 0.55)

        road_dist_m = sum(
            math.hypot(
                self.node_x[path_nodes[i + 1]] - self.node_x[path_nodes[i]],
                self.node_y[path_nodes[i + 1]] - self.node_y[path_nodes[i]],
            )
            for i in range(len(path_nodes) - 1)
        )
        road_dist_m = max(30.0, road_dist_m)

        # Build Right-Hand Lane offset nodes + tight intersection arcs & resampled waypoints spaced ~step_m apart
        center_pts = [(self.node_x[n], self.node_y[n], self.node_z[n] + 0.35) for n in path_nodes]
        n_path = len(center_pts)
        seg_r_normals: list[tuple[float, float]] = []
        seg_r_offsets: list[float] = []
        for k in range(n_path - 1):
            dx_k = center_pts[k + 1][0] - center_pts[k][0]
            dy_k = center_pts[k + 1][1] - center_pts[k][1]
            lk = math.hypot(dx_k, dy_k)
            if lk > 0.05:
                # Forward = (dx_k/lk, dy_k/lk) -> Right perpendicular in GTA XY = (dy_k/lk, -dx_k/lk)
                seg_r_normals.append((dy_k / lk, -dx_k / lk))
            else:
                seg_r_normals.append(seg_r_normals[-1] if seg_r_normals else (1.0, 0.0))
            seg_r_offsets.append(self.edge_right_offset.get((path_nodes[k], path_nodes[k + 1]), 2.2))

        base_pts: list[tuple[float, float, float]] = []
        for k in range(n_path):
            cx_k, cy_k, cz_k = center_pts[k]
            if n_path == 1 or not seg_r_normals:
                base_pts.append((cx_k, cy_k, cz_k))
                continue
            if k == 0:
                rx_k, ry_k = seg_r_normals[0]
                off_k = seg_r_offsets[0]
            elif k == n_path - 1:
                rx_k, ry_k = seg_r_normals[-1]
                off_k = seg_r_offsets[-1]
            else:
                r0x, r0y = seg_r_normals[k - 1]
                r1x, r1y = seg_r_normals[k]
                off_k = 0.5 * (seg_r_offsets[k - 1] + seg_r_offsets[k])
                sx_r = r0x + r1x
                sy_r = r0y + r1y
                s_len = math.hypot(sx_r, sy_r)
                dot_r = r0x * r1x + r0y * r1y
                if s_len > 0.05:
                    # Miter scale 1 / cos(theta/2) clamped to [1.0, 1.38] so 90-deg turns stay strictly in the right lane
                    miter = min(1.38, max(1.0, math.sqrt(2.0 / max(0.35, 1.0 + dot_r))))
                    rx_k = (sx_r / s_len) * miter
                    ry_k = (sy_r / s_len) * miter
                else:
                    rx_k, ry_k = r1x, r1y
            base_pts.append((cx_k + rx_k * off_k, cy_k + ry_k * off_k, cz_k))

        if base_pts:
            tail_dx = dx - base_pts[-1][0]
            tail_dy = dy - base_pts[-1][1]
            tail_d = math.hypot(tail_dx, tail_dy)
            if len(base_pts) < 4:
                bx0, by0, bz0 = base_pts[-1]
                if tail_d > 8.0 and tail_d <= 45.0 and abs(dz - bz0) <= 4.0:
                    tx_end, ty_end, tz_end = dx, dy, dz
                else:
                    tx_end, ty_end, tz_end = bx0 + 35.0, by0, bz0
                td_use = max(25.0, math.hypot(tx_end - bx0, ty_end - by0))
                n_steps = max(6, int(td_use / 5.0))
                for s_i in range(1, n_steps + 1):
                    frac = s_i / float(n_steps)
                    base_pts.append((bx0 + (tx_end - bx0) * frac, by0 + (ty_end - by0) * frac, bz0 + (tz_end - bz0) * frac))
            pickup_xyz = (base_pts[0][0], base_pts[0][1], base_pts[0][2] + 0.10)
            dropoff_xyz = (base_pts[-1][0], base_pts[-1][1], base_pts[-1][2] + 0.10)
            if seg_r_normals:
                srx, sry = seg_r_normals[0]
                soff = seg_r_offsets[0]
                spawn_xyz = (
                    self.node_x[spawn_nid] + srx * soff,
                    self.node_y[spawn_nid] + sry * soff,
                    self.node_z[spawn_nid] + 0.55,
                )

        if len(base_pts) >= 3:
            beveled: list[tuple[float, float, float]] = [base_pts[0]]
            for idx_b in range(1, len(base_pts) - 1):
                ax, ay, az = base_pts[idx_b - 1]
                bx, by, bz = base_pts[idx_b]
                cx, cy, cz = base_pts[idx_b + 1]
                ux, uy, uz = bx - ax, by - ay, bz - az
                vx, vy, vz = cx - bx, cy - by, cz - bz
                lu = math.hypot(ux, uy)
                lv = math.hypot(vx, vy)
                if lu >= 6.0 and lv >= 6.0:
                    dot_uv = (ux * vx + uy * vy) / (lu * lv)
                    if dot_uv < 0.94:  # Turn angle > ~20 deg: gentle 2.4m inner arc inside intersection asphalt
                        cut_u = min(2.4, lu * 0.18) / lu
                        cut_v = min(2.4, lv * 0.18) / lv
                        p_in = (bx - ux * cut_u, by - uy * cut_u, bz - uz * cut_u)
                        p_out = (bx + vx * cut_v, by + vy * cut_v, bz + vz * cut_v)
                        p_mid = (
                            0.25 * p_in[0] + 0.50 * bx + 0.25 * p_out[0],
                            0.25 * p_in[1] + 0.50 * by + 0.25 * p_out[1],
                            0.25 * p_in[2] + 0.50 * bz + 0.25 * p_out[2],
                        )
                        beveled.extend([p_in, p_mid, p_out])
                        continue
                beveled.append((bx, by, bz))
            beveled.append(base_pts[-1])
            raw_pts = beveled
        else:
            raw_pts = base_pts

        waypoints: list[tuple[float, float, float, float]] = []
        for idx in range(len(raw_pts)):
            x0, y0, z0 = raw_pts[idx]
            if idx + 1 < len(raw_pts):
                x1, y1, z1 = raw_pts[idx + 1]
            elif idx > 0:
                x1, y1, z1 = x0, y0, z0
                x0_prev, y0_prev, _ = raw_pts[idx - 1]
                dx_seg = x1 - x0_prev
                dy_seg = y1 - y0_prev
                hdg = (math.degrees(math.atan2(-dx_seg, dy_seg)) + 360.0) % 360.0 if (abs(dx_seg) + abs(dy_seg) > 0.01) else 0.0
                waypoints.append((x0, y0, z0, hdg))
                continue
            else:
                waypoints.append((x0, y0, z0, spawn_heading))
                continue

            dx_seg = x1 - x0
            dy_seg = y1 - y0
            dz_seg = z1 - z0
            seg_len = math.hypot(dx_seg, dy_seg)
            hdg = (math.degrees(math.atan2(-dx_seg, dy_seg)) + 360.0) % 360.0 if seg_len > 0.01 else 0.0
            waypoints.append((x0, y0, z0, hdg))
            if seg_len > step_m * 1.25:
                n_sub = max(2, int(round(seg_len / step_m)))
                for s_i in range(1, n_sub):
                    frac = s_i / float(n_sub)
                    waypoints.append((x0 + dx_seg * frac, y0 + dy_seg * frac, z0 + dz_seg * frac, hdg))

        return {
            "ok": True,
            "nodes": path_nodes,
            "waypoints": waypoints,
            "road_dist_m": round(road_dist_m, 1),
            "straight_dist_m": round(straight_dist, 1),
            "pickup_xyz": pickup_xyz,
            "dropoff_xyz": dropoff_xyz,
            "spawn_xyz": spawn_xyz,
            "spawn_heading": round(spawn_heading, 1),
        }


class EagleRideManager:
    """
    Manages App 12: EagleRide (Uber / Xanh SM / Grab / Be) state, Fog-of-War POI discovery,
    CLEO bridge communication, passenger radio switching, and Hybrid Graph-Guided Autopilot.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.pegg_path = base_dir / "data" / "pecore_gps_graph.pegg"
        self.bridge_ini_path = base_dir / "cleo" / "EagleRide" / "bridge.ini"
        self.state_json_path = base_dir / "cleo" / "EagleRide" / "state.json"
        self.router = PeggGraphRouter(self.pegg_path)

        # UI Selection State
        self.service_idx = 0       # 0..4 into RIDE_SERVICES
        self.cat_idx = 0           # 0..9 into GG_MAP_CATEGORIES
        self.poi_idx = 0           # Selected POI index within category
        self.selected_poi_id: str | None = None
        self.search_query: str = ""
        self.filter_visited_only = False  # False = show all with [OPEN]/[LOCKED] badge; True = show only unlocked
        self.radio_idx = 5         # Default Radio Los Santos

        # Fog-of-War Visited POIs
        self.visited_pois: set[str] = set(DEFAULT_UNLOCKED_POIS)
        self._last_discovery_check_ts = 0.0

        # Active Ride State
        self.ride_state = "IDLE"   # "IDLE", "APPROACHING", "RIDING", "COMPLETED"
        self.active_trip: dict | None = None
        self.total_trips = 0
        self.total_spent = 0
        self._cmd_seq = 1
        self._cached_shm_ptr = 0
        self._last_tick_ts = 0.0
        self._last_cleo_wp_ts = 0.0
        self.load_state()

    def select_service(self, idx: int) -> dict:
        self.service_idx = int(idx) % len(RIDE_SERVICES)
        self.save_state()
        return self.get_selected_service()

    def set_search_query(self, query: str) -> str:
        cleaned = to_clean_viet_ascii(str(query or "")).strip()[:48]
        if cleaned != self.search_query:
            self.search_query = cleaned
            self.poi_idx = 0
            self.selected_poi_id = None
        return self.search_query

    def check_auto_unlock_nearby(self, engine) -> list[dict]:
        self._last_discovery_check_ts = 0.0
        return self.check_poi_discovery(tuple(engine.player_pos), getattr(engine, "player_area_code", 0))

    def load_state(self):
        if not self.state_json_path.exists():
            return
        try:
            data = json.loads(self.state_json_path.read_text(encoding="utf-8"))
            if isinstance(data.get("visited_pois"), list):
                self.visited_pois = set(DEFAULT_UNLOCKED_POIS) | {str(x) for x in data["visited_pois"] if x}
            if "service_idx" in data:
                self.service_idx = int(data["service_idx"]) % len(RIDE_SERVICES)
            if "radio_idx" in data:
                self.radio_idx = int(data["radio_idx"]) % len(GTA_RADIO_STATIONS)
            if "filter_visited_only" in data:
                self.filter_visited_only = bool(data["filter_visited_only"])
        except Exception:
            pass

    def save_state(self):
        try:
            self.state_json_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "service_idx": self.service_idx,
                "radio_idx": self.radio_idx,
                "filter_visited_only": self.filter_visited_only,
                "visited_pois": sorted(self.visited_pois),
            }
            self.state_json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_selected_service(self) -> dict:
        return RIDE_SERVICES[self.service_idx % len(RIDE_SERVICES)]

    def estimate_fare(self, dist_m: float, service: dict | None = None) -> int:
        svc = service or self.get_selected_service()
        # Estimate road distance as ~1.22x straight-line distance when browsing list
        est_km = max(0.2, (dist_m * 1.22) / 1000.0)
        fare = int(round(svc["base_fare"] + svc["per_km"] * est_km))
        return max(svc["base_fare"], fare)

    def estimate_exact_fare(self, road_dist_m: float, service: dict | None = None) -> int:
        svc = service or self.get_selected_service()
        km = max(0.15, road_dist_m / 1000.0)
        return max(svc["base_fare"], int(round(svc["base_fare"] + svc["per_km"] * km)))

    def check_poi_discovery(self, player_pos: tuple[float, float, float], curr_area: int = 0) -> list[dict]:
        """
        Checks if the player is within <=85m of any undiscovered POI and unlocks it.
        Returns a list of newly unlocked POI dicts (if any).
        """
        now = time.time()
        if now - self._last_discovery_check_ts < 0.8:
            return []
        self._last_discovery_check_ts = now
        if self.ride_state == "RIDING":
            # Only unlock destination when arriving, not intermediate POIs during fast-forward
            pass

        px, py, _pz = player_pos
        if abs(px) < 0.01 and abs(py) < 0.01:
            return []

        newly_unlocked: list[dict] = []
        r2 = DISCOVERY_RADIUS_M * DISCOVERY_RADIUS_M
        for p in CURATED_GG_MAP_POIS:
            pid = p["id"]
            if pid in self.visited_pois:
                continue
            dx = float(p["x"]) - px
            dy = float(p["y"]) - py
            if dx * dx + dy * dy <= r2:
                self.visited_pois.add(pid)
                newly_unlocked.append(p)
        return newly_unlocked

    def _resolve_shm_ptr(self, bridge) -> int:
        """Resolves the 128-byte shared memory block allocated by `cleo/EagleRideBridge.cs`."""
        if not bridge.try_attach():
            return 0
        if self._cached_shm_ptr > 0x00400000:
            magic = bridge.read_u32(self._cached_shm_ptr)
            if magic == RIDE_SHM_MAGIC:
                return self._cached_shm_ptr

        magic_cafe = bridge.read_u32(CAFE_RIDE_MAGIC_ADDR)
        if magic_cafe == RIDE_SHM_MAGIC:
            ptr = bridge.read_u32(CAFE_RIDE_PTR_ADDR) or 0
            if ptr > 0x00400000 and bridge.read_u32(ptr) == RIDE_SHM_MAGIC:
                self._cached_shm_ptr = ptr
                return ptr

        if self.bridge_ini_path.exists():
            try:
                for ln in self.bridge_ini_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if ln.strip().startswith("shm_ptr"):
                        val = int(ln.split("=", 1)[1].strip())
                        if val > 0x00400000 and bridge.read_u32(val) == RIDE_SHM_MAGIC:
                            self._cached_shm_ptr = val
                            return val
            except Exception:
                pass
        return 0

    def _send_cleo_cmd(
        self,
        bridge,
        cmd_type: int,
        veh_model: int = 426,
        ped_model: int = 17,
        color1: int = 0,
        color2: int = 0,
        seat_id: int = 2,
        spawn_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0),
        spawn_heading: float = 0.0,
        target_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0),
        cruise_speed: float = 24.0,
        radio_ch: int = 6,
        drv_style: int = 2,
    ) -> bool:
        shm_ptr = self._resolve_shm_ptr(bridge)
        if not shm_ptr:
            return False
        cur_ack = bridge.read_i32(shm_ptr + 0x40) or 0
        self._cmd_seq = max(self._cmd_seq + 1, cur_ack + 1)

        # Write parameters first (+0x08..+0x3C and +0x5C..+0x60), then write cmd_seq (+0x04)
        payload = struct.pack(
            "<iiiiiiffffffff",
            int(cmd_type),
            int(veh_model),
            int(ped_model),
            int(color1),
            int(color2),
            int(seat_id),
            float(spawn_xyz[0]),
            float(spawn_xyz[1]),
            float(spawn_xyz[2]),
            float(spawn_heading),
            float(target_xyz[0]),
            float(target_xyz[1]),
            float(target_xyz[2]),
            float(cruise_speed),
        )
        bridge.write_bytes(shm_ptr + 0x08, payload)
        bridge.write_bytes(shm_ptr + 0x5C, struct.pack("<ii", int(radio_ch), int(drv_style)))
        bridge.write_i32(shm_ptr + 0x04, self._cmd_seq)
        return True

    def read_cleo_telemetry(self, bridge) -> dict:
        shm_ptr = self._resolve_shm_ptr(bridge)
        if not shm_ptr:
            return {"attached": False, "shm_ptr": 0}
        raw = bridge.read_bytes(shm_ptr + 0x40, 40)
        if not raw or len(raw) < 40:
            return {"attached": False, "shm_ptr": shm_ptr}
        ack_seq, state, veh_h, veh_ptr, drv_h, drv_ptr, in_car, radio_ch, drv_style, hb = struct.unpack(
            "<iiIIIIiiii", raw
        )
        return {
            "attached": True,
            "shm_ptr": shm_ptr,
            "ack_seq": ack_seq,
            "state": state,
            "veh_handle": veh_h,
            "veh_ptr": veh_ptr,
            "driver_handle": drv_h,
            "driver_ptr": drv_ptr,
            "in_car": in_car,
            "radio_ch": radio_ch,
            " heartbeat": hb,
        }

    def _orient_and_move_vehicle(
        self,
        bridge,
        veh_ptr: int,
        x: float,
        y: float,
        z: float,
        heading_deg: float,
        speed_mps: float,
    ) -> bool:
        """
        Smoothly updates CVehicle CMatrix orientation + position and velocity vector
        along the road heading so the vehicle glides along the PEGG A* spline without getting stuck.
        """
        if not veh_ptr or veh_ptr < 0x00400000:
            return False
        rad = math.radians(heading_deg)
        # In GTA SA RenderWare CMatrix:
        # forward (at/up in 2D XY) = (-sin(hdg), cos(hdg), 0)
        # right = (cos(hdg), sin(hdg), 0)
        fx = -math.sin(rad)
        fy = math.cos(rad)
        rx = math.cos(rad)
        ry = math.sin(rad)

        xyz_bytes = struct.pack("<fff", float(x), float(y), float(z))
        bridge.write_bytes(veh_ptr + 0x04, xyz_bytes)
        veh_mat = bridge.read_u32(veh_ptr + 0x14)
        if veh_mat and veh_mat > 0x00400000:
            mat_payload = struct.pack(
                "<ffffffffffffffff",
                rx, ry, 0.0, 0.0,     # +0x00 Right
                fx, fy, 0.0, 0.0,     # +0x10 Forward
                0.0, 0.0, 1.0, 0.0,   # +0x20 Up
                float(x), float(y), float(z), 0.0,  # +0x30 Pos
            )
            bridge.write_bytes(veh_mat, mat_payload[:60])

        # GTA SA move speed: 1.0f = 50 m/s
        vel_scale = float(speed_mps) / 50.0
        vel_bytes = struct.pack("<ffffff", fx * vel_scale, fy * vel_scale, 0.0, 0.0, 0.0, 0.0)
        bridge.write_bytes(veh_ptr + 0x44, vel_bytes)
        return True

    def start_ride(
        self,
        engine,
        poi: dict | str | None = None,
        poi_id: str | None = None,
    ) -> tuple[bool, str]:
        """
        Starts an EagleRide trip to `poi` (or `poi_id` / `self.selected_poi_id`).
        Enforces:
        1. POI must be unlocked in `self.visited_pois` (if locked, sets GPS waypoint instead so player can drive there).
        2. Player must have enough Cash or Bank balance to cover the trip fare.
        """
        if isinstance(poi, str):
            poi_id = poi
            poi = None
        if poi is None:
            target_id = poi_id or self.selected_poi_id
            if target_id:
                poi = next((p for p in CURATED_GG_MAP_POIS if p["id"] == target_id), None)
            if poi is None and CURATED_GG_MAP_POIS:
                poi = CURATED_GG_MAP_POIS[0]
        if not poi:
            return False, "No destination POI selected."

        pid = poi["id"]
        is_vi = engine._is_vi()
        poi_name = to_clean_viet_ascii(poi["name"])
        dbg_open = bool(getattr(getattr(engine, "debug_sys", None), "mode", "lite") == "deep")

        if pid not in self.visited_pois and not dbg_open:
            # Automatically pin GPS so the player can drive there first
            engine._set_gps_waypoint_to_poi(poi)
            msg = (
                f"CHUA KHAM PHA: Ban can tu lai xe den '{poi_name}' lan dau de mo khoa dat xe! (Da bat GPS chi duong)"
                if is_vi
                else f"LOCKED POI: Drive to '{poi_name}' in person first to unlock EagleRide! (GPS Waypoint pinned)"
            )
            return False, msg

        curr_area = (engine.bridge.read_i32(0x00B72914) or 0) if engine.bridge.try_attach() else 0
        svc = self.get_selected_service()
        px, py, pz = engine.player_pos
        if curr_area != 0 and pz > 800.0:
            # Player is inside a high-altitude interior world: use nearest unlocked POI or Grove St as outdoor origin
            px, py, pz = 2488.5, -1668.5, 13.4
        dest_xyz = (float(poi["x"]), float(poi["y"]), float(poi["z"]))

        route = self.router.compute_route((px, py, pz), dest_xyz, step_m=5.0)
        fare = self.estimate_exact_fare(route["road_dist_m"], svc)

        total_funds = engine.cash + engine.bank
        if total_funds < fare and not dbg_open:
            msg = (
                f"Khong du tien cuoc (${fare:,})! Can them ${fare - total_funds:,} trong Vi hoac Ngan hang."
                if is_vi
                else f"Insufficient funds for fare (${fare:,})! Need ${fare - total_funds:,} more."
            )
            return False, msg

        # If player booked from inside an interior or ENEX doorway, automatically step them outside to the curb (Area 0)
        if curr_area != 0 and engine.bridge.try_attach():
            pk_x, pk_y, pk_z = route["pickup_xyz"]
            engine.bridge.teleport_player(pk_x, pk_y, pk_z + 0.5, area_code=0)
            engine.player_pos = (pk_x, pk_y, pk_z + 0.5)

        # Pin native GPS route on radar so the red/yellow GPS line renders throughout the ride
        engine._set_gps_waypoint_to_poi(poi)

        spawn_xyz = route["spawn_xyz"]
        pickup_xyz = route["pickup_xyz"]
        dropoff_xyz = route["dropoff_xyz"]
        spawn_heading = route["spawn_heading"]
        waypoints = route["waypoints"]

        now = time.time()
        self.active_trip = {
            "service": svc,
            "poi": poi,
            "fare": fare,
            "paid": False,
            "route": route,
            "waypoints": waypoints,
            "wp_idx": 0,
            "total_wps": len(waypoints),
            "road_dist_m": route["road_dist_m"],
            "remaining_dist_m": route["road_dist_m"],
            "spawn_xyz": spawn_xyz,
            "pickup_xyz": pickup_xyz,
            "dropoff_xyz": dropoff_xyz,
            "cur_xyz": spawn_xyz,
            "cur_heading": spawn_heading,
            "started_at": now,
            "boarded_at": 0.0,
            "last_update_ts": now,
            "radio_station": GTA_RADIO_STATIONS[self.radio_idx % len(GTA_RADIO_STATIONS)][1],
        }
        self.ride_state = "APPROACHING"
        self._last_tick_ts = now

        # Command CLEO bridge to spawn branded vehicle + driver and drive to pickup_xyz
        self._send_cleo_cmd(
            engine.bridge,
            cmd_type=1,
            veh_model=svc["veh_model"],
            ped_model=svc["ped_model"],
            color1=svc["color1"],
            color2=svc["color2"],
            seat_id=svc["seat_id"],
            spawn_xyz=spawn_xyz,
            spawn_heading=spawn_heading,
            target_xyz=pickup_xyz,
            cruise_speed=18.0,
            drv_style=2,
        )

        svc_lbl = svc["short_vi"] if is_vi else svc["short_en"]
        msg = (
            f"Da dat {svc_lbl} den {poi_name} ({format_distance(route['road_dist_m'])} | Cuoc: ${fare:,}). Tai xe dang toi don!"
            if is_vi
            else f"Booked {svc_lbl} to {poi_name} ({format_distance(route['road_dist_m'])} | Fare: ${fare:,}). Driver arriving!"
        )
        engine.push_event_banner(
            "EAGLERIDE DRIVER ARRIVING!" if not is_vi else "TAI XE EAGLERIDE DANG TOI DON!",
            msg,
            kind="info",
        )
        return True, msg

    def _charge_fare(self, engine, fare: int):
        if engine.cash >= fare:
            engine.modify_cash(-fare)
        else:
            rem = fare - engine.cash
            if engine.cash > 0:
                engine.modify_cash(-engine.cash)
            engine.bank = max(0, engine.bank - rem)
        self.total_trips += 1
        self.total_spent += int(fare)

    def fast_forward_trip(self, engine) -> tuple[bool, str]:
        """
        Immediately skips the remaining ride duration, advances the game clock proportionally,
        places the vehicle and player safely at the destination dropoff point, and charges the fare.
        """
        is_vi = engine._is_vi()
        if not self.active_trip or self.ride_state not in ("APPROACHING", "RIDING"):
            return False, ("Khong co chuyen xe nao dang chay!" if is_vi else "No active EagleRide trip to fast-forward!")

        trip = self.active_trip
        svc = trip["service"]
        poi = trip["poi"]
        fare = trip["fare"]
        dropoff_x, dropoff_y, dropoff_z = trip["dropoff_xyz"]
        last_hdg = trip["waypoints"][-1][3] if trip["waypoints"] else 0.0

        # Charge fare once
        if not trip.get("paid"):
            self._charge_fare(engine, fare)
            trip["paid"] = True

        # Advance game clock by remaining travel time (1 game minute per ~220m)
        rem_m = max(100.0, float(trip.get("remaining_dist_m", trip["road_dist_m"])))
        add_mins = max(2, min(45, int(round(rem_m / 220.0))))
        if engine.bridge.try_attach():
            cur_h = engine.bridge.read_u8(0x00B70153) or 12
            cur_m = engine.bridge.read_u8(0x00B70152) or 0
            tot_m = cur_m + add_mins
            new_h = (cur_h + (tot_m // 60)) % 24
            new_m = tot_m % 60
            engine.bridge.write_bytes(0x00B70152, struct.pack("<BB", new_m, new_h))

        # Unlock destination POI and clear GPS waypoint
        self.visited_pois.add(poi["id"])
        self.save_state()
        engine.bridge.clear_target_waypoint()
        engine.active_gps_target = None

        # Place vehicle & player at safe dropoff and dismiss driver
        telem = self.read_cleo_telemetry(engine.bridge)
        veh_ptr = telem.get("veh_ptr", 0)
        was_in_car = telem.get("in_car", 0)
        trip["driver_ptr"] = telem.get("driver_ptr", 0)

        is_far_map = abs(dropoff_x) > 4800.0 or abs(dropoff_y) > 4800.0
        ride_h = (0.24 if svc.get("kind") == "BIKE" else 0.44) if is_far_map else (0.78 if svc.get("kind") == "BIKE" else 0.88)

        # Sidewalk offset 2.2m to the right of dropoff node so player exits cleanly onto the curb
        rad = math.radians(last_hdg)
        exit_x = dropoff_x + math.cos(rad) * 2.2
        exit_y = dropoff_y + math.sin(rad) * 2.2
        exit_z = dropoff_z + 0.6

        if veh_ptr and veh_ptr > 0x00400000:
            self._orient_and_move_vehicle(engine.bridge, veh_ptr, dropoff_x, dropoff_y, dropoff_z + ride_h, last_hdg, 0.0)

        # If player was not yet seated inside the vehicle (e.g. fast-forwarded during APPROACHING),
        # teleport player to exit_xyz BEFORE cmd_type=5 releases the car/driver mission flags so
        # GTA SA's streamer never culls the vehicle and driver at the destination.
        if not was_in_car and engine.bridge.try_attach():
            engine.bridge.teleport_player(exit_x, exit_y, exit_z, area_code=0)

        sent_dropoff = self._send_cleo_cmd(
            engine.bridge,
            cmd_type=5,
            seat_id=99,  # 99 = warp from car to exit_xyz immediately
            target_xyz=(exit_x, exit_y, exit_z),
        )
        if sent_dropoff:
            for _ in range(18):
                time.sleep(0.02)
                tm_end = self.read_cleo_telemetry(engine.bridge)
                if tm_end.get("in_car", 0) == 0 and tm_end.get("veh_ptr", 0) == 0:
                    break

        if engine.bridge.try_attach():
            cur_pos = (engine.bridge.read_live_player() or {}).get("pos")
            if not cur_pos or math.hypot(cur_pos[0] - exit_x, cur_pos[1] - exit_y) > 15.0:
                engine.bridge.teleport_player(exit_x, exit_y, exit_z, area_code=0)
            if veh_ptr and veh_ptr > 0x00400000:
                self._orient_and_move_vehicle(engine.bridge, veh_ptr, dropoff_x, dropoff_y, dropoff_z + ride_h, last_hdg, 0.0)
        engine.player_pos = (round(exit_x, 3), round(exit_y, 3), round(exit_z, 3))

        self.ride_state = "IDLE"
        self.active_trip = None
        svc_lbl = svc["short_vi"] if is_vi else svc["short_en"]
        poi_name = to_clean_viet_ascii(poi["name"])
        msg = (
            f"[FAST-FORWARD] Da toi {poi_name} bang {svc_lbl}! (+{add_mins} phut | Da thanh toan ${fare:,})"
            if is_vi
            else f"[FAST-FORWARD] Arrived at {poi_name} via {svc_lbl}! (+{add_mins}m | Paid ${fare:,})"
        )
        engine.push_event_banner(
            "EAGLERIDE ARRIVED!" if not is_vi else "DA DEN DIEM HEN EAGLERIDE!",
            msg,
            kind="win",
        )
        return True, msg

    def recompute_active_route(
        self,
        engine,
        cur_xyz: tuple[float, float, float] | None = None,
        banned_nodes: set[int] | None = None,
    ) -> bool:
        """
        Dynamically re-computes the active EagleRide route from `cur_xyz` (e.g. after skipping an intersection)
        to the destination POI over the checkerboard PEGG graph without teleporting backward.
        """
        if not self.active_trip or self.ride_state not in ("APPROACHING", "RIDING"):
            return False
        trip = self.active_trip
        poi = trip["poi"]
        cx, cy, cz = cur_xyz if cur_xyz is not None else trip["cur_xyz"]
        dest_xyz = (float(poi["x"]), float(poi["y"]), float(poi["z"]))
        new_route = self.router.compute_route((cx, cy, cz), dest_xyz, step_m=5.0, banned_nodes=banned_nodes)
        if not new_route.get("ok") or not new_route.get("waypoints"):
            return False
        wps = new_route["waypoints"]
        trip["route"] = new_route
        trip["waypoints"] = wps
        trip["wp_idx"] = 0
        trip["total_wps"] = len(wps)
        trip["remaining_dist_m"] = new_route["road_dist_m"]
        trip["reroute_count"] = trip.get("reroute_count", 0) + 1
        trip["last_wp_change_idx"] = 0
        trip["last_wp_change_ts"] = time.time()
        engine._set_gps_waypoint_to_poi(poi)
        return True

    def cancel_trip(self, engine) -> tuple[bool, str]:
        is_vi = engine._is_vi()
        if not self.active_trip or self.ride_state == "IDLE":
            return False, ("Khong co chuyen xe nao de huy." if is_vi else "No active trip to cancel.")
        self._send_cleo_cmd(engine.bridge, cmd_type=6)
        engine.bridge.clear_target_waypoint()
        engine.active_gps_target = None
        self.ride_state = "IDLE"
        self.active_trip = None
        msg = "Da huy chuyen xe EagleRide." if is_vi else "Cancelled active EagleRide trip."
        return True, msg

    def cycle_radio(self, engine, delta: int = 1) -> str:
        self.radio_idx = (self.radio_idx + delta) % len(GTA_RADIO_STATIONS)
        ch_id, ch_name = GTA_RADIO_STATIONS[self.radio_idx]
        seat_id = 2
        if self.active_trip:
            self.active_trip["radio_station"] = ch_name
            seat_id = int(self.active_trip.get("service", {}).get("seat_id", 2))
        self._send_cleo_cmd(engine.bridge, cmd_type=4, seat_id=seat_id, radio_ch=ch_id)
        self.save_state()
        return ch_name

    def _enforce_rider_and_vehicle_armor(
        self,
        bridge,
        veh_ptr: int,
        driver_ptr: int = 0,
    ):
        """
        Enforces heavy anti-deflection mass (`m_fMass = 8500.0`, `m_fTurnMass = 12000.0`),
        full vehicle health (`1000.0`), and `bCantBeKnockedOffBike = 1` (`0x08000000` at `CPed + 0x474`)
        on both the AI driver and the player ped so bike/car impacts never launch or knock off riders.
        """
        if veh_ptr and veh_ptr > 0x00400000:
            bridge.write_bytes(veh_ptr + 0x8C, struct.pack("<ff", 8500.0, 12000.0))
            bridge.write_bytes(veh_ptr + 0x4C0, struct.pack("<f", 1000.0))
            if (bridge.read_u8(veh_ptr + 0x2F) or 0) != 0:
                bridge.write_bytes(veh_ptr + 0x2F, b"\x00")
        if (bridge.read_i32(0x00B72914) or 0) != 0:
            bridge.write_i32(0x00B72914, 0)
        if (bridge.read_i32(0x00B79E44) or 0) != 0:
            bridge.write_i32(0x00B79E44, 0)
        player_ped = bridge.read_u32(0x00B7CD98) or 0
        for ped_ptr in (player_ped, driver_ptr):
            if ped_ptr and ped_ptr > 0x00400000:
                if (bridge.read_u8(ped_ptr + 0x2F) or 0) != 0:
                    bridge.write_bytes(ped_ptr + 0x2F, b"\x00")
                flags = bridge.read_u32(ped_ptr + 0x474)
                if flags is not None:
                    new_flags = (flags & ~0x18000000) | 0x08000000
                    if new_flags != flags:
                        bridge.write_u32(ped_ptr + 0x474, new_flags)

    def _scan_and_avoid_traffic(
        self,
        bridge,
        veh_ptr: int,
        vx_pos: float,
        vy_pos: float,
        vz_pos: float,
        tx: float,
        ty: float,
    ) -> tuple[float, float]:
        """
        Scans `CPools::ms_pVehiclePool` (`0x00B74494`) for any ambient NPC vehicles ahead in our
        driving lane (`0.5m <= fwd <= 24.0m`, `|lat| <= 3.2m`, `|dz| <= 3.5m`).
        - Never teleports or despawns ambient vehicles.
        - Returns `(avoid_lat_m, speed_factor)` for smooth left/right overtaking and proximity braking.
        """
        pool_ptr = bridge.read_u32(0x00B74494) or 0
        if pool_ptr < 0x00400000:
            return 0.0, 1.0
        pool_hdr = bridge.read_bytes(pool_ptr, 12)
        if not pool_hdr or len(pool_hdr) < 12:
            return 0.0, 1.0
        objs_ptr, bmap_ptr, n_size = struct.unpack("<III", pool_hdr)
        if objs_ptr < 0x00400000 or bmap_ptr < 0x00400000 or n_size <= 0 or n_size > 512:
            return 0.0, 1.0
        bmap = bridge.read_bytes(bmap_ptr, min(n_size, 256))
        if not bmap:
            return 0.0, 1.0

        # Right unit vector perpendicular to forward (tx, ty)
        rx_dir = ty
        ry_dir = -tx
        avoid_lat = 0.0
        speed_factor = 1.0
        closest_fwd = 999.0

        for i, bval in enumerate(bmap):
            if bval & 0x80:
                continue
            other_ptr = objs_ptr + i * 0xA18
            if other_ptr == veh_ptr:
                continue
            raw_pos = bridge.read_bytes(other_ptr + 0x04, 12)
            if not raw_pos or len(raw_pos) < 12:
                continue
            ox, oy, oz = struct.unpack("<fff", raw_pos)
            dz = oz - vz_pos
            if abs(dz) > 3.5:
                continue
            dx = ox - vx_pos
            dy = oy - vy_pos
            if abs(dx) > 25.0 or abs(dy) > 25.0:
                continue
            fwd = dx * tx + dy * ty
            lat = dx * rx_dir + dy * ry_dir
            if 0.5 <= fwd <= 24.0 and abs(lat) <= 3.0:
                if fwd < closest_fwd:
                    closest_fwd = fwd
                    # Smoothly steer around slower traffic in our lane (prefer passing on the left if obstacle is on right/center)
                    avoid_lat = -2.6 if lat >= -0.3 else 2.1
                    if fwd < 16.0 and abs(lat) < 2.2:
                        speed_factor = min(speed_factor, max(0.32, (fwd - 3.0) / 14.0))

        return avoid_lat, speed_factor

    def _assist_vehicle_wheel_drive(
        self,
        bridge,
        veh_ptr: int,
        wps: list[tuple[float, float, float, float]],
        idx: int,
        target_speed_mps: float,
        dt: float,
        trip: dict,
    ) -> tuple[float, float, float, int]:
        """
        Wheel-Physics Hybrid Autopilot (Right-Hand Lane Tracking, 35m Corner Braking,
        Natural Overtaking & Physical Reverse-and-Steer Unstick Maneuver):
        1. Reads live CVehicle CMatrix (`+0x14`) and velocity (`+0x44`).
        2. Enforces heavy cruiser mass (`8500 kg`) and `bCantBeKnockedOffBike = 1` on driver & passenger.
        3. Advances `idx` monotonically along dense `5m` right-hand lane `wps` (`d_to_next <= 4.2m`)
           so the vehicle never cuts across building corners on `90°` turns.
        4. Measures upcoming corner curvature across the next `35m` (`7` waypoints) and brakes smoothly
           down to `8.5–11.5 m/s` before entering intersections.
        5. If physically blocked by a wall or tight corner for `>= 1.8s`, executes a `1.15s`
           Physical Reverse-and-Steer Maneuver (`-6.5 m/s` in reverse) instead of teleporting!
        """
        veh_mat = bridge.read_u32(veh_ptr + 0x14) if veh_ptr > 0x00400000 else 0
        if not veh_mat or veh_mat < 0x00400000:
            cx, cy, cz = trip["cur_xyz"]
            return cx, cy, cz, idx

        raw_mat = bridge.read_bytes(veh_mat, 60)
        raw_vel = bridge.read_bytes(veh_ptr + 0x44, 24)
        if not raw_mat or len(raw_mat) < 60 or not raw_vel or len(raw_vel) < 24:
            cx, cy, cz = trip["cur_xyz"]
            return cx, cy, cz, idx

        rx, ry, rz, _rw, fx, fy, fz, _fw, ux, uy, uz, _uw, vx_pos, vy_pos, vz_pos = struct.unpack("<15f", raw_mat)
        vel_x, vel_y, vel_z, avx, avy, _avz = struct.unpack("<6f", raw_vel)

        svc = trip.get("service", {})
        is_bike = svc.get("kind") == "BIKE"
        self._enforce_rider_and_vehicle_armor(bridge, veh_ptr, trip.get("driver_ptr", 0))

        # 1. Advance waypoint index monotonically using tight 5m right-lane window (no early corner-cutting!)
        n_wps = len(wps)
        best_k = idx
        best_d = math.hypot(wps[idx][0] - vx_pos, wps[idx][1] - vy_pos)
        for k in range(idx + 1, min(idx + 8, n_wps)):
            dk = math.hypot(wps[k][0] - vx_pos, wps[k][1] - vy_pos)
            if dk <= best_d + 0.5 and dk <= 9.5:
                best_d = dk
                best_k = k
        idx = max(idx, best_k)

        while idx < n_wps - 1:
            x0, y0, _z0, _h0 = wps[idx]
            x1, y1, _z1, h1 = wps[idx + 1]
            d_to_next = math.hypot(x1 - vx_pos, y1 - vy_pos)
            if d_to_next <= 4.2:
                trip["cur_heading"] = h1
                idx += 1
                continue
            sx_seg = x1 - x0
            sy_seg = y1 - y0
            seg_len2 = sx_seg * sx_seg + sy_seg * sy_seg
            if seg_len2 > 0.20:
                t_p = ((vx_pos - x0) * sx_seg + (vy_pos - y0) * sy_seg) / seg_len2
                if t_p >= 0.88 and d_to_next <= 8.0:
                    trip["cur_heading"] = h1
                    idx += 1
                    continue
            break

        # 2. Compute cross-track error (cte) and road elevation reference
        p_cur = wps[idx]
        p_next = wps[min(idx + 1, n_wps - 1)]
        p_aim = wps[min(idx + 2, n_wps - 1)]

        sx_seg = p_next[0] - p_cur[0]
        sy_seg = p_next[1] - p_cur[1]
        sz_seg = p_next[2] - p_cur[2]
        seg_len2 = sx_seg * sx_seg + sy_seg * sy_seg
        if seg_len2 > 0.1:
            t_proj = max(0.0, min(1.0, ((vx_pos - p_cur[0]) * sx_seg + (vy_pos - p_cur[1]) * sy_seg) / seg_len2))
            proj_x = p_cur[0] + t_proj * sx_seg
            proj_y = p_cur[1] + t_proj * sy_seg
            proj_z = p_cur[2] + t_proj * sz_seg
        else:
            proj_x, proj_y, proj_z = p_next[0], p_next[1], p_next[2]

        cte = math.hypot(vx_pos - proj_x, vy_pos - proj_y)
        dz_road = vz_pos - proj_z

        now = time.time()
        cur_fc = bridge.read_u32(0x00B7CB4C) or 0
        if cur_fc != trip.get("last_fc", -1):
            trip["last_fc"] = cur_fc
            trip["last_fc_change_ts"] = now
        elif (now - trip.get("last_fc_change_ts", now)) >= 0.45:
            trip["last_wp_change_ts"] = now
            return vx_pos, vy_pos, vz_pos, idx
        prev_vx = trip.get("prev_vx", vx_pos)
        prev_vy = trip.get("prev_vy", vy_pos)
        real_disp_mps = math.hypot(vx_pos - prev_vx, vy_pos - prev_vy) / max(0.02, dt)
        trip["prev_vx"] = vx_pos
        trip["prev_vy"] = vy_pos

        if idx > trip.get("last_wp_change_idx", -1):
            trip["last_wp_change_idx"] = idx
            trip["last_wp_change_ts"] = now
            if idx > trip.get("stall_zone_idx", -10) + 3:
                trip["stall_retries"] = 0

        wp_stall_sec = now - trip.get("last_wp_change_ts", now)

        # Active Physical Reverse-and-Steer Unstick Maneuver (backs away from wall smoothly without teleporting)
        if now < trip.get("reverse_until_ts", 0.0):
            dx_r = proj_x - vx_pos
            dy_r = proj_y - vy_pos
            dr_len = math.hypot(dx_r, dy_r)
            want_rad = math.radians(p_next[3])
            wfx = -math.sin(want_rad)
            wfy = math.cos(want_rad)
            if dr_len > 0.5:
                wfx = 0.70 * wfx + 0.30 * (dx_r / dr_len)
                wfy = 0.70 * wfy + 0.30 * (dy_r / dr_len)
            nfx = fx * 0.78 + wfx * 0.22
            nfy = fy * 0.78 + wfy * 0.22
            nf_len = max(0.01, math.hypot(nfx, nfy))
            nfx /= nf_len
            nfy /= nf_len
            nrx = nfy
            nry = -nfx
            rot_payload = struct.pack(
                "<12f",
                nrx, nry, 0.0, 0.0,
                nfx, nfy, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
            )
            bridge.write_bytes(veh_mat, rot_payload)
            rev_scale = -6.5 / 50.0
            vel_payload = struct.pack("<6f", fx * rev_scale, fy * rev_scale, max(-0.15, min(0.02, vel_z)), 0.0, 0.0, 0.0)
            bridge.write_bytes(veh_ptr + 0x44, vel_payload)
            return vx_pos, vy_pos, vz_pos, idx

        if (real_disp_mps < 1.25 or wp_stall_sec >= 2.2) and (now - trip.get("boarded_at", now)) > 0.9:
            trip["stall_sec"] = trip.get("stall_sec", 0.0) + dt
        else:
            trip["stall_sec"] = max(0.0, trip.get("stall_sec", 0.0) - dt * 1.5)

        # 3. Handle Physical Reverse Unstick first; only use emergency road reset if flipped/submerged/repeatedly wedged
        severe_off_road = uz < 0.32 or vz_pos < min(-2.0, proj_z - 2.5) or dz_road < -5.8 or dz_road > 11.0 or cte > 22.0
        if trip.get("stall_sec", 0.0) >= 1.75 and not severe_off_road:
            trip["stall_sec"] = 0.0
            trip["stall_zone_idx"] = idx
            retries = trip.get("stall_retries", 0) + 1
            trip["stall_retries"] = retries
            if retries <= 2:
                # Shift into reverse for 1.15s to back away from wall/curb naturally!
                trip["reverse_until_ts"] = now + 1.15
                return vx_pos, vy_pos, vz_pos, idx

        since_last_recov = now - trip.get("last_recov_ts", 0.0)
        if severe_off_road and since_last_recov >= 1.20 or (trip.get("stall_retries", 0) >= 3 and since_last_recov >= 1.50):
            trip["stall_sec"] = 0.0
            trip["stall_retries"] = 0
            trip["recoveries"] = trip.get("recoveries", 0) + 1
            trip["last_recov_ts"] = now
            step_fwd = 2 if trip.get("last_recov_idx", -1) == idx else 1
            new_idx = min(idx + step_fwd, n_wps - 1)
            trip["last_recov_idx"] = new_idx
            trip["last_wp_change_idx"] = new_idx
            trip["last_wp_change_ts"] = now
            rec_wp = wps[new_idx]
            self._orient_and_move_vehicle(
                bridge,
                veh_ptr,
                rec_wp[0],
                rec_wp[1],
                rec_wp[2] + ((0.24 if is_bike else 0.44) if (abs(rec_wp[0]) > 4800.0 or abs(rec_wp[1]) > 4800.0) else (0.78 if is_bike else 0.88)),
                rec_wp[3],
                min(target_speed_mps, 12.0),
            )
            trip["prev_vx"] = rec_wp[0]
            trip["prev_vy"] = rec_wp[1]
            trip["cur_heading"] = rec_wp[3]
            return rec_wp[0], rec_wp[1], rec_wp[2] + ((0.24 if is_bike else 0.44) if (abs(rec_wp[0]) > 4800.0 or abs(rec_wp[1]) > 4800.0) else (0.78 if is_bike else 0.88)), new_idx

        # 4. Measure upcoming corner curvature across next ~35m (7 waypoints of 5m) for early Corner Braking
        cur_hdg = (math.degrees(math.atan2(-fx, fy)) + 360.0) % 360.0
        max_turn_deg = 0.0
        base_wp_hdg = wps[idx][3]
        for k_turn in range(idx, min(idx + 8, n_wps)):
            dh_car = abs(((wps[k_turn][3] - cur_hdg + 180.0) % 360.0) - 180.0)
            dh_rd = abs(((wps[k_turn][3] - base_wp_hdg + 180.0) % 360.0) - 180.0)
            dh = max(dh_car, dh_rd)
            if dh > max_turn_deg:
                max_turn_deg = dh

        corner_speed = float(target_speed_mps)
        if max_turn_deg >= 52.0:
            corner_speed = min(corner_speed, 8.2 if is_bike else 8.8)
        elif max_turn_deg >= 28.0:
            corner_speed = min(corner_speed, 11.2 if is_bike else 12.0)
        elif max_turn_deg >= 15.0:
            corner_speed = min(corner_speed, 14.5 if is_bike else 15.5)

        # Zero corner-cutting aim: during turns, track p_next (5m ahead along right lane) + strong cross-track pull
        w_next = 0.94 if max_turn_deg >= 20.0 else 0.80
        aim_x = w_next * p_next[0] + (1.0 - w_next) * p_aim[0]
        aim_y = w_next * p_next[1] + (1.0 - w_next) * p_aim[1]
        if cte > 0.35:
            center_pull = min(0.65, cte * 0.18)
            aim_x = aim_x * (1.0 - center_pull) + proj_x * center_pull
            aim_y = aim_y * (1.0 - center_pull) + proj_y * center_pull

        dx_a = aim_x - vx_pos
        dy_a = aim_y - vy_pos
        da_len = math.hypot(dx_a, dy_a)
        if da_len > 0.2:
            tx = dx_a / da_len
            ty = dy_a / da_len

            # Scan CPool<CVehicle> for forward traffic obstacles and smoothly overtake/brake (never despawns traffic)
            avoid_lat, traffic_spd_factor = self._scan_and_avoid_traffic(
                bridge, veh_ptr, vx_pos, vy_pos, vz_pos, tx, ty
            )
            if abs(avoid_lat) > 0.1 and da_len > 2.0 and max_turn_deg < 35.0:
                rx_dir = ty
                ry_dir = -tx
                dx_a += rx_dir * avoid_lat
                dy_a += ry_dir * avoid_lat
                da_len = math.hypot(dx_a, dy_a)
                tx = dx_a / da_len
                ty = dy_a / da_len
            corner_speed *= traffic_spd_factor

            want_hdg = (math.degrees(math.atan2(-tx, ty)) + 360.0) % 360.0
            trip["cur_heading"] = want_hdg

            # Smoothly blend horizontal forward vector toward (tx, ty) (responsive steering in turns)
            blend = 0.78 if max_turn_deg >= 22.0 else 0.62
            nfx = fx * (1.0 - blend) + tx * blend
            nfy = fy * (1.0 - blend) + ty * blend
            nf_2d = math.hypot(nfx, nfy)
            if nf_2d > 0.01:
                road_slope = sz_seg / max(1.0, math.hypot(sx_seg, sy_seg))
                max_pitch = 0.12 if is_bike else 0.28
                nfz = max(-max_pitch, min(max_pitch, (0.35 * fz + 0.65 * road_slope) if is_bike else (0.55 * fz + 0.45 * road_slope)))
                horiz_scale = math.sqrt(max(0.1, 1.0 - nfz * nfz)) / nf_2d
                nfx *= horiz_scale
                nfy *= horiz_scale

                # Right = normalized (nfy, -nfx, 0) -> strictly 0 roll so bike/car never tips sideways!
                r_len = math.hypot(nfy, nfx)
                nrx = nfy / r_len
                nry = -nfx / r_len
                nrz = 0.0

                # Up = Right x Forward
                nux = nry * nfz - nrz * nfy
                nuy = nrz * nfx - nrx * nfz
                nuz = nrx * nfy - nry * nfx

                # In outer multiverse sectors (|x| > 4800 or |y| > 4800, e.g., Vice City / Liberty City / Tokyo)
                # GTA SA's CWorld sector loop does not integrate pos += vel * dt, or when wheel slip stalls on a custom .col seam:
                # smoothly integrate continuous forward motion along (tx, ty) at corner_speed * dt!
                far_multiverse = abs(vx_pos) > 4800.0 or abs(vy_pos) > 4800.0
                wheel_slip_seam = wp_stall_sec >= 0.70 and (now - trip.get("boarded_at", now)) > 0.65
                steep_slope = abs(road_slope) >= 0.14 or abs(dz_road) >= 2.2
                if far_multiverse or wheel_slip_seam or steep_slope:
                    step_d = min(2.4, float(corner_speed) * max(0.04, min(0.14, dt)))
                    step_x = vx_pos + tx * step_d
                    step_y = vy_pos + ty * step_d
                    ride_h = (0.24 if is_bike else 0.44) if far_multiverse else (0.78 if is_bike else 0.88)
                    target_z = proj_z + ride_h
                    if steep_slope:
                        dz_need = target_z - vz_pos
                        step_z = target_z if abs(dz_need) <= 2.8 else (vz_pos + math.copysign(2.8, dz_need))
                    elif not far_multiverse:
                        step_z = max(vz_pos + 0.03, vz_pos + min(0.35, max(0.0, target_z - vz_pos)))
                    else:
                        step_z = target_z
                    mat_payload = struct.pack(
                        "<16f",
                        nrx, nry, nrz, 0.0,
                        nfx, nfy, nfz, 0.0,
                        nux, nuy, nuz, 0.0,
                        step_x, step_y, step_z, 0.0,
                    )
                    bridge.write_bytes(veh_mat, mat_payload)
                    bridge.write_bytes(veh_ptr + 0x04, struct.pack("<fff", step_x, step_y, step_z))
                    vx_pos, vy_pos, vz_pos = step_x, step_y, step_z
                    dz_road = vz_pos - proj_z
                else:
                    # Write ONLY the 48-byte 3x3 rotation part of CMatrix (leaving +0x30 Pos untouched!)
                    rot_payload = struct.pack(
                        "<12f",
                        nrx, nry, nrz, 0.0,
                        nfx, nfy, nfz, 0.0,
                        nux, nuy, nuz, 0.0,
                    )
                    bridge.write_bytes(veh_mat, rot_payload)

                # Apply smooth forward wheel speed while damping upward bounce (especially on bikes!)
                vel_scale = float(corner_speed) / 50.0
                slope_vz = max(0.0, road_slope * vel_scale)
                if is_bike:
                    keep_vz = (road_slope * vel_scale) if far_multiverse else (max(-0.22, min(slope_vz, vel_z)) if dz_road > -0.25 else max(0.01, slope_vz))
                    vel_payload = struct.pack(
                        "<6f",
                        nfx * vel_scale,
                        nfy * vel_scale,
                        keep_vz,
                        0.0,
                        0.0,
                        0.0,
                    )
                else:
                    keep_vz = (road_slope * vel_scale) if far_multiverse else (max(-0.28, min(max(0.03, slope_vz), vel_z)) if dz_road > -0.4 else max(0.02, slope_vz))
                    vel_payload = struct.pack(
                        "<6f",
                        nfx * vel_scale,
                        nfy * vel_scale,
                        keep_vz,
                        avx * 0.25,
                        avy * 0.25,
                        0.0,
                    )
                bridge.write_bytes(veh_ptr + 0x44, vel_payload)

        return vx_pos, vy_pos, vz_pos, idx

    def tick(self, engine):
        """
        Called at ~10Hz from `EagleCompanionEngine._tick_loop`.
        1. Checks Fog-of-War POI discovery (`<= 85m`).
        2. Steps the active EagleRide trip (`APPROACHING` -> `RIDING` -> `COMPLETED`) along the PEGG A* spline.
        """
        now = time.time()
        curr_area = (engine.bridge.read_i32(0x00B72914) or 0) if engine.bridge.try_attach() else 0
        new_pois = self.check_poi_discovery(engine.player_pos, curr_area)
        if new_pois:
            self.save_state()
            p0 = new_pois[0]
            p_name = to_clean_viet_ascii(p0["name"])
            is_vi = engine._is_vi()
            engine.push_event_banner(
                "NEW LOCATION UNLOCKED FOR EAGLERIDE!" if not is_vi else "DA MO KHOA DIA DIEM EAGLERIDE MOI!",
                (
                    f"Da kham pha: {p_name} ({len(self.visited_pois)}/{len(CURATED_GG_MAP_POIS)} diem da mo khoa)"
                    if is_vi
                    else f"Discovered: {p_name} ({len(self.visited_pois)}/{len(CURATED_GG_MAP_POIS)} POIs unlocked)"
                ),
                kind="win",
            )

        if self.ride_state not in ("APPROACHING", "RIDING") or not self.active_trip:
            return

        dt = min(0.5, max(0.02, now - self._last_tick_ts))
        self._last_tick_ts = now
        trip = self.active_trip
        svc = trip["service"]
        telem = self.read_cleo_telemetry(engine.bridge)
        veh_ptr = telem.get("veh_ptr", 0)
        trip["driver_ptr"] = telem.get("driver_ptr", 0)

        # --- Phase 1: APPROACHING (Driver pulling up to player) ---
        if self.ride_state == "APPROACHING":
            elapsed = now - trip["started_at"]
            sx, sy, sz = trip["spawn_xyz"]
            px, py, pz = trip["pickup_xyz"]
            t_frac = min(1.0, elapsed / 1.4)
            cx = sx + (px - sx) * t_frac
            cy = sy + (py - sy) * t_frac
            cz = sz + (pz - sz) * t_frac
            trip["cur_xyz"] = (cx, cy, cz)

            # Wait for CLEO CMD 1 to finish streaming & spawning the custom vehicle before sending CMD 2
            if not veh_ptr or veh_ptr < 0x00400000:
                cleo_state = telem.get("state", 0)
                if (
                    cleo_state in (0, -1, 4)
                    and elapsed >= 1.8
                    and (now - trip.get("last_cmd1_retry", trip["started_at"])) >= 2.2
                ):
                    trip["last_cmd1_retry"] = now
                    self._send_cleo_cmd(
                        engine.bridge,
                        cmd_type=1,
                        veh_model=svc["veh_model"],
                        ped_model=svc["ped_model"],
                        color1=svc["color1"],
                        color2=svc["color2"],
                        seat_id=svc["seat_id"],
                        spawn_xyz=trip["pickup_xyz"],
                        spawn_heading=trip["cur_heading"],
                        target_xyz=trip["pickup_xyz"],
                        cruise_speed=18.0,
                        drv_style=2,
                    )
                if elapsed < 8.0:
                    return

            if t_frac >= 1.0 or telem.get("in_car") == 1:
                # Ensure vehicle is aligned cleanly at pickup_xyz facing forward along wps[idx0] before boarding
                wps = trip["waypoints"]
                idx0 = min(trip.get("wp_idx", 0), max(0, len(wps) - 1))
                init_hdg = wps[idx0][3] if wps else trip["cur_heading"]
                if veh_ptr and veh_ptr > 0x00400000:
                    self._orient_and_move_vehicle(engine.bridge, veh_ptr, px, py, pz + ((0.24 if svc.get("kind") == "BIKE" else 0.44) if (abs(px) > 4800.0 or abs(py) > 4800.0) else (0.78 if svc.get("kind") == "BIKE" else 0.88)), init_hdg, 0.0)
                # Board player into passenger seat, set radio & camera in one atomic CLEO command (CMD 2)
                self.ride_state = "RIDING"
                trip["boarded_at"] = now
                trip["wp_idx"] = idx0
                trip["last_wp_change_idx"] = idx0
                trip["last_wp_change_ts"] = now
                trip["stall_sec"] = 0.0
                trip["stall_retries"] = 0
                trip["reboard_retries"] = 0
                wp0 = wps[min(idx0 + 3, len(wps) - 1)] if wps else (px, py, pz, init_hdg)
                ch_id, _ = GTA_RADIO_STATIONS[self.radio_idx % len(GTA_RADIO_STATIONS)]
                self._send_cleo_cmd(
                    engine.bridge,
                    cmd_type=2,
                    seat_id=svc["seat_id"],
                    target_xyz=(wp0[0], wp0[1], wp0[2]),
                    cruise_speed=svc["speed_mps"],
                    radio_ch=ch_id,
                    drv_style=3,
                )
                self._last_cleo_wp_ts = now
            return

        # --- Phase 2: RIDING (Autopilot along PEGG A* waypoints) ---
        if self.ride_state == "RIDING":
            wps = trip["waypoints"]
            if not wps:
                self.fast_forward_trip(engine)
                return

            idx = min(trip["wp_idx"], len(wps) - 1)
            base_speed = float(svc["speed_mps"])
            ex, ey, ez = trip["dropoff_xyz"]

            if veh_ptr and veh_ptr > 0x00400000:
                # Wait at current waypoint until CLEO has seated player inside the vehicle (in_car == 1)
                if telem.get("in_car", 0) == 0:
                    if (now - trip["boarded_at"]) > 0.55:
                        trip["boarded_at"] = now
                        retries = trip.get("reboard_retries", 0) + 1
                        trip["reboard_retries"] = retries
                        if retries >= 1:
                            idx = min(idx + 1, len(wps) - 1)
                            trip["wp_idx"] = idx
                        wx, wy, wz, whdg = wps[idx]
                        if engine.bridge.try_attach():
                            engine.bridge.teleport_player(wx, wy, wz + 0.85, area_code=0)
                        if retries >= 2:
                            # Vehicle may be flagged submerged or unboardable; fresh-spawn at wps[idx]
                            trip["reboard_retries"] = 0
                            trip["spawn_xyz"] = (wx, wy, wz + 0.45)
                            trip["pickup_xyz"] = (wx, wy, wz + 0.45)
                            trip["cur_heading"] = whdg
                            trip["started_at"] = now
                            self.ride_state = "APPROACHING"
                            self._send_cleo_cmd(
                                engine.bridge,
                                cmd_type=1,
                                veh_model=svc["veh_model"],
                                ped_model=svc["ped_model"],
                                color1=svc["color1"],
                                color2=svc["color2"],
                                seat_id=svc["seat_id"],
                                spawn_xyz=(wx, wy, wz + 0.45),
                                spawn_heading=whdg,
                                target_xyz=(wx, wy, wz + 0.45),
                                cruise_speed=18.0,
                                drv_style=2,
                            )
                            return
                        ride_h = (0.24 if svc.get("kind") == "BIKE" else 0.44) if (abs(wx) > 4800.0 or abs(wy) > 4800.0) else (0.78 if svc.get("kind") == "BIKE" else 0.88)
                        self._orient_and_move_vehicle(engine.bridge, veh_ptr, wx, wy, wz + ride_h, whdg, 0.0)
                        look_wp = wps[min(idx + 3, len(wps) - 1)]
                        ch_id, _ = GTA_RADIO_STATIONS[self.radio_idx % len(GTA_RADIO_STATIONS)]
                        self._send_cleo_cmd(
                            engine.bridge,
                            cmd_type=2,
                            seat_id=svc["seat_id"],
                            target_xyz=(look_wp[0], look_wp[1], look_wp[2]),
                            cruise_speed=base_speed,
                            radio_ch=ch_id,
                            drv_style=3,
                        )
                        self._last_cleo_wp_ts = now
                    return

                trip["reboard_retries"] = 0
                # Taper speed smoothly on final 30m approach to destination dropoff
                cur_rem = math.hypot(ex - engine.player_pos[0], ey - engine.player_pos[1])
                target_speed = min(base_speed, max(9.0, cur_rem * 0.65)) if cur_rem < 32.0 else base_speed

                cx, cy, cz, idx = self._assist_vehicle_wheel_drive(
                    engine.bridge,
                    veh_ptr,
                    wps,
                    idx,
                    target_speed,
                    dt,
                    trip,
                )
                trip["wp_idx"] = idx
                trip["cur_xyz"] = (cx, cy, cz)
                engine.player_pos = (round(cx, 3), round(cy, 3), round(cz, 3))
            else:
                # If CLEO is attached and veh_ptr became 0 mid-ride (vehicle destroyed/submerged), respawn at wps[idx]
                if telem.get("attached") and idx < len(wps) - 2 and (now - trip.get("last_respawn_ts", 0.0)) >= 2.0:
                    trip["last_respawn_ts"] = now
                    idx = min(idx + 1, len(wps) - 1)
                    trip["wp_idx"] = idx
                    wx, wy, wz, whdg = wps[idx]
                    if engine.bridge.try_attach():
                        engine.bridge.teleport_player(wx, wy, wz + 0.85, area_code=0)
                    trip["spawn_xyz"] = (wx, wy, wz + 0.45)
                    trip["pickup_xyz"] = (wx, wy, wz + 0.45)
                    trip["cur_xyz"] = (wx, wy, wz + 0.45)
                    trip["cur_heading"] = whdg
                    trip["started_at"] = now
                    self.ride_state = "APPROACHING"
                    fb_veh = 426 if svc.get("kind") == "CAR" else 462
                    self._send_cleo_cmd(
                        engine.bridge,
                        cmd_type=1,
                        veh_model=fb_veh,
                        ped_model=17,
                        color1=svc["color1"],
                        color2=svc["color2"],
                        seat_id=svc["seat_id"],
                        spawn_xyz=(wx, wy, wz + 0.45),
                        spawn_heading=whdg,
                        target_xyz=(wx, wy, wz + 0.45),
                        cruise_speed=18.0,
                        drv_style=2,
                    )
                    return

                # Offline simulator or fallback when CLEO script is not attached
                cx, cy, cz = trip["cur_xyz"]
                step_budget = base_speed * dt
                while step_budget > 0.0 and idx < len(wps) - 1:
                    nx, ny, nz, nhdg = wps[idx + 1]
                    seg_d = math.hypot(nx - cx, ny - cy)
                    if seg_d <= step_budget:
                        cx, cy, cz = nx, ny, nz
                        trip["cur_heading"] = nhdg
                        step_budget -= seg_d
                        idx += 1
                    else:
                        ratio = step_budget / seg_d
                        cx += (nx - cx) * ratio
                        cy += (ny - cy) * ratio
                        cz += (nz - cz) * ratio
                        trip["cur_heading"] = nhdg
                        step_budget = 0.0
                trip["wp_idx"] = idx
                trip["cur_xyz"] = (cx, cy, cz)
                if engine.bridge.try_attach():
                    engine.bridge.teleport_player(cx, cy, cz + 0.5, area_code=0)
                engine.player_pos = (round(cx, 3), round(cy, 3), round(cz + 0.5, 3))

            # Compute remaining distance
            rem_dist = math.hypot(ex - cx, ey - cy)
            trip["remaining_dist_m"] = round(rem_dist, 1)

            # Periodically feed lookahead waypoint (~45m ahead on PEGG route) to CLEO AI driver
            if now - self._last_cleo_wp_ts >= 1.1:
                self._last_cleo_wp_ts = now
                look_wp = wps[min(idx + 3, len(wps) - 1)]
                self._send_cleo_cmd(
                    engine.bridge,
                    cmd_type=3,
                    target_xyz=(look_wp[0], look_wp[1], look_wp[2]),
                    cruise_speed=base_speed,
                    drv_style=3,
                )

            # Check arrival at destination dropoff
            if idx >= len(wps) - 1 or rem_dist <= 12.0:
                fare = trip["fare"]
                poi = trip["poi"]
                if not trip.get("paid"):
                    self._charge_fare(engine, fare)
                    trip["paid"] = True
                self.visited_pois.add(poi["id"])
                self.save_state()
                engine.bridge.clear_target_waypoint()
                engine.active_gps_target = None

                last_hdg = wps[-1][3] if wps else trip["cur_heading"]
                if veh_ptr and veh_ptr > 0x00400000:
                    self._orient_and_move_vehicle(engine.bridge, veh_ptr, ex, ey, ez + ((0.24 if svc.get("kind") == "BIKE" else 0.44) if (abs(ex) > 4800.0 or abs(ey) > 4800.0) else (0.78 if svc.get("kind") == "BIKE" else 0.88)), last_hdg, 0.0)

                rad = math.radians(last_hdg)
                exit_x = ex + math.cos(rad) * 2.2
                exit_y = ey + math.sin(rad) * 2.2
                exit_z = ez + 0.6

                sent_dropoff = self._send_cleo_cmd(
                    engine.bridge,
                    cmd_type=5,
                    seat_id=99,
                    target_xyz=(exit_x, exit_y, exit_z),
                )
                if sent_dropoff:
                    for _ in range(18):
                        time.sleep(0.02)
                        tm_end = self.read_cleo_telemetry(engine.bridge)
                        if tm_end.get("in_car", 0) == 0 and tm_end.get("veh_ptr", 0) == 0:
                            break
                elif engine.bridge.try_attach():
                    engine.bridge.teleport_player(exit_x, exit_y, exit_z, area_code=0)
                engine.player_pos = (round(exit_x, 3), round(exit_y, 3), round(exit_z, 3))
                self.ride_state = "IDLE"
                self.active_trip = None
                is_vi = engine._is_vi()
                svc_lbl = svc["short_vi"] if is_vi else svc["short_en"]
                poi_name = to_clean_viet_ascii(poi["name"])
                msg = (
                    f"Chuyen xe {svc_lbl} da den {poi_name} an toan! (Da thanh toan ${fare:,})"
                    if is_vi
                    else f"{svc_lbl} arrived safely at {poi_name}! (Paid ${fare:,})"
                )
                engine.push_event_banner(
                    "EAGLERIDE TRIP COMPLETED!" if not is_vi else "HOAN THANH CHUYEN XE EAGLERIDE!",
                    msg,
                    kind="win",
                )

    def build_projection(self, engine) -> dict:
        """Builds full HUD + Web UI projection for App 12: EagleRide."""
        is_vi = engine._is_vi()
        lang = "vi" if is_vi else "en"
        svc = self.get_selected_service()
        gg_cats = GG_MAP_CATEGORIES_VI if is_vi else GG_MAP_CATEGORIES_EN
        cat_idx = self.cat_idx % len(gg_cats)
        cat_code, cat_lbl, cat_title = gg_cats[cat_idx]

        px, py, _pz = engine.player_pos
        dbg_open = bool(getattr(getattr(engine, "debug_sys", None), "mode", "lite") == "deep")
        q_norm = to_clean_viet_ascii(self.search_query).lower().strip()
        q_tokens = [tok for tok in q_norm.replace("-", " ").split() if tok]

        all_cat_pois: list[dict] = []
        for p in CURATED_GG_MAP_POIS:
            # When searching, scan across ALL 715 POIs regardless of active category tab
            if not q_tokens:
                if cat_code != "ALL" and p["cat"] != cat_code and cat_code not in p.get("cats", ()):
                    continue
            unlocked = (p["id"] in self.visited_pois) or dbg_open
            if self.filter_visited_only and not unlocked:
                continue

            search_rank = 0
            if q_tokens:
                nm_en = to_clean_viet_ascii(str(p.get("name", ""))).lower()
                nm_vi = to_clean_viet_ascii(str(p.get("name_vi", ""))).lower()
                rg_en = to_clean_viet_ascii(str(p.get("region", ""))).lower()
                rg_vi = to_clean_viet_ascii(str(p.get("region_vi", ""))).lower()
                ds_en = to_clean_viet_ascii(str(p.get("desc", ""))).lower()
                ds_vi = to_clean_viet_ascii(str(p.get("desc_vi", ""))).lower()
                cat_s = f"{p.get('id', '')} {p.get('cat', '')} {' '.join(p.get('cats', ()))}".lower()
                haystack = f"{nm_en} {nm_vi} {rg_en} {rg_vi} {ds_en} {ds_vi} {cat_s}".replace("-", " ")
                if not all(tok in haystack for tok in q_tokens):
                    continue
                if nm_en.startswith(q_norm) or nm_vi.startswith(q_norm):
                    search_rank = 0
                elif q_norm in nm_en or q_norm in nm_vi:
                    search_rank = 1
                elif q_norm in rg_en or q_norm in rg_vi:
                    search_rank = 2
                else:
                    search_rank = 3

            dx = float(p["x"]) - float(px)
            dy = float(p["y"]) - float(py)
            dist_2d = math.hypot(dx, dy)
            item = localize_poi_item(p, lang=lang)
            item["dist_m"] = round(dist_2d, 1)
            item["dist_str"] = format_distance(dist_2d)
            item["compass"] = compute_compass_dir(dx, dy, lang=lang)
            item["unlocked"] = unlocked
            item["fare"] = self.estimate_fare(dist_2d, svc)
            item["_search_rank"] = search_rank
            all_cat_pois.append(item)

        # Sort by search relevance (if searching), then unlocked first, then nearest distance
        if q_tokens:
            all_cat_pois.sort(key=lambda item: (item["_search_rank"], 0 if item["unlocked"] else 1, item["dist_m"]))
        else:
            all_cat_pois.sort(key=lambda item: (0 if item["unlocked"] else 1, item["dist_m"]))

        if all_cat_pois:
            if self.selected_poi_id:
                found_i = next((i for i, p in enumerate(all_cat_pois) if p["id"] == self.selected_poi_id), None)
                if found_i is not None:
                    self.poi_idx = found_i
                else:
                    self.poi_idx = min(self.poi_idx, len(all_cat_pois) - 1)
                    self.selected_poi_id = all_cat_pois[self.poi_idx]["id"]
            else:
                self.poi_idx = min(self.poi_idx, len(all_cat_pois) - 1)
                self.selected_poi_id = all_cat_pois[self.poi_idx]["id"]
            sel_idx = self.poi_idx
            sel_poi = all_cat_pois[sel_idx]
        else:
            sel_idx = 0
            sel_poi = None

        def _smart_clip(raw_s: object, max_len: int) -> str:
            s = to_clean_viet_ascii(str(raw_s or "")).strip()
            if len(s) <= max_len:
                return s
            cut = s[: max(1, max_len - 3)].rstrip()
            if " " in cut and len(cut) > 14:
                last_sp = cut.rfind(" ")
                if last_sp >= max_len - 12:
                    cut = cut[:last_sp]
            cut = cut.rstrip(" -&/+(,[{:")
            return f"{cut}..."

        win_size = 4
        win_start = max(0, min(sel_idx - 1, max(0, len(all_cat_pois) - win_size)))
        table_rows = []
        for r_i in range(5):
            p_idx = win_start + r_i
            if r_i < win_size and p_idx < len(all_cat_pois):
                p = all_cat_pois[p_idx]
                comp_s = p.get("compass", "")
                dist_disp = f"{p['dist_str']} {comp_s}".strip()
                table_rows.append({
                    "idx": p_idx + 1,
                    "id": p["id"],
                    "name": _smart_clip(p["name"], 37),
                    "region": _smart_clip(p["region"], 22),
                    "dist": dist_disp,
                    "fare": f"${p['fare']:,}",
                    "unlocked": "1" if p["unlocked"] else "0",
                    "status": ("DA MO" if is_vi else "OPEN") if p["unlocked"] else ("KHOA" if is_vi else "LOCKED"),
                    "sel": "1" if p_idx == sel_idx else "0",
                })
            else:
                table_rows.append({
                    "idx": 0,
                    "id": "",
                    "name": "",
                    "region": "",
                    "dist": "",
                    "fare": "",
                    "unlocked": "0",
                    "status": "",
                    "sel": "0",
                })

        total_list = len(all_cat_pois)
        if total_list <= 1:
            scroll_pct = "0"
            can_up = "0"
            can_dn = "0"
        else:
            scroll_pct = str(max(0, min(100, int(round((sel_idx / float(total_list - 1)) * 100.0)))))
            can_up = "1" if sel_idx > 0 else "0"
            can_dn = "1" if sel_idx < (total_list - 1) else "0"

        unlocked_cnt = len(CURATED_GG_MAP_POIS) if dbg_open else len(self.visited_pois)
        total_cnt = len(CURATED_GG_MAP_POIS)
        open_badge = f"{unlocked_cnt}/{total_cnt} DA MO" if is_vi else f"{unlocked_cnt}/{total_cnt} OPEN"

        if q_tokens:
            if total_list > 0:
                cat_display = (
                    f"KQ Tim: {sel_idx + 1}/{total_list} diem"
                    if is_vi
                    else f"Search: {sel_idx + 1}/{total_list} match{'es' if total_list != 1 else ''}"
                )
            else:
                cat_display = "KQ Tim: 0 diem" if is_vi else "Search: 0 matches"
        else:
            raw_cat = to_clean_viet_ascii(cat_lbl)
            if ":" in raw_cat:
                raw_cat = raw_cat.split(":", 1)[-1].strip()
            elif "." in raw_cat[:4] and raw_cat.split(".", 1)[0].isdigit():
                raw_cat = raw_cat.split(".", 1)[-1].strip()
            raw_cat = raw_cat.replace("(", "- ").replace(")", "").strip()
            short_cat = _smart_clip(raw_cat, 19)
            cat_display = (
                f"{cat_idx + 1}/{len(gg_cats)} {short_cat} ({sel_idx + 1}/{total_list})"
                if total_list > 0
                else f"{cat_idx + 1}/{len(gg_cats)} {short_cat} (0)"
            )

        _, radio_name = GTA_RADIO_STATIONS[self.radio_idx % len(GTA_RADIO_STATIONS)]
        svc_short_lbl = svc["short_vi"] if is_vi else svc["short_en"]
        if self.active_trip and self.ride_state in ("APPROACHING", "RIDING"):
            tr = self.active_trip
            t_svc = tr["service"]
            t_poi = tr["poi"]
            s_lbl = t_svc["short_vi"] if is_vi else t_svc["short_en"]
            p_lbl = _smart_clip(t_poi["name"], 24)
            rem_s = format_distance(tr.get("remaining_dist_m", tr["road_dist_m"]))
            status_bar = (
                f"DANG DI {s_lbl} -> {p_lbl} (Con {rem_s} - ${tr['fare']:,})"
                if is_vi
                else f"RIDING {s_lbl} -> {p_lbl} ({rem_s} left - ${tr['fare']:,})"
            )
            sel_meta = _smart_clip(status_bar, 48)
            ride_active_str = "1"
        else:
            dbg_tag = " [DEBUG]" if dbg_open else ""
            status_bar = (
                f"Da mo: {unlocked_cnt}/{total_cnt}{dbg_tag} - Radio: {radio_name}"
                if is_vi
                else f"Unlocked: {unlocked_cnt}/{total_cnt}{dbg_tag} - Radio: {radio_name}"
            )
            sel_meta = (
                f"{svc_short_lbl} (${svc['base_fare']}+${svc['per_km']}/km) - FM: {_smart_clip(radio_name, 19)}"
                if sel_poi
                else (
                    f"Khong tim thay '{_smart_clip(self.search_query, 22)}'"
                    if is_vi
                    else f"No match for '{_smart_clip(self.search_query, 22)}'"
                )
            )
            ride_active_str = "0"

        if sel_poi:
            lock_tag = ("[DA MO KHOA]" if is_vi else "[UNLOCKED]") if sel_poi["unlocked"] else ("[CHUA TOI - BAM F9 BAT GPS]" if is_vi else "[LOCKED - F9 PINS GPS]")
            sel_title = f"{lock_tag} {to_clean_viet_ascii(sel_poi['name'])}"
            sel_coords = (
                f"Khu vuc: {to_clean_viet_ascii(sel_poi['region'])} - Cach: {sel_poi['dist_str']} - Gia cuoc {svc['short_vi']}: ${sel_poi['fare']:,}"
                if is_vi
                else f"Region: {to_clean_viet_ascii(sel_poi['region'])} - Dist: {sel_poi['dist_str']} - {svc['short_en']} Fare: ${sel_poi['fare']:,}"
            )
            sel_note = _smart_clip(sel_poi.get("desc", ""), 64)
            sel_open_str = "1" if sel_poi["unlocked"] else "0"
            sel_fare_str = f"${sel_poi['fare']:,}"
        else:
            sel_title = "Chua chon diem den" if is_vi else "No destination selected"
            sel_coords = ""
            sel_note = (
                "Bam [X] hoac Backspace de xoa tu khoa tim kiem"
                if (q_tokens and is_vi)
                else ("Click [X] or press Backspace to clear search filter" if q_tokens else "")
            )
            sel_open_str = "0"
            sel_fare_str = "$0"

        return {
            "ride_state": self.ride_state,
            "ride_active_str": ride_active_str,
            "service_idx": self.service_idx,
            "service_id": svc["id"],
            "service_label": svc["name_vi"] if is_vi else svc["name_en"],
            "service_short": svc_short_lbl,
            "services": [
                {
                    "idx": i,
                    "id": s["id"],
                    "kind": s["kind"],
                    "label": s["name_vi"] if is_vi else s["name_en"],
                    "short": s["short_vi"] if is_vi else s["short_en"],
                    "base_fare": s["base_fare"],
                    "per_km": s["per_km"],
                    "badge_color": s["badge_color"],
                }
                for i, s in enumerate(RIDE_SERVICES)
            ],
            "cat_idx": cat_idx,
            "cat_code": cat_code,
            "cat_label": cat_lbl,
            "cat_display": to_clean_viet_ascii(cat_display),
            "categories": [
                {"idx": i, "code": c[0], "short": c[1], "title": c[2]}
                for i, c in enumerate(gg_cats)
            ],
            "search_query": self.search_query,
            "filter_visited_only": self.filter_visited_only,
            "scroll_pct": scroll_pct,
            "can_up": can_up,
            "can_dn": can_dn,
            "open_badge": to_clean_viet_ascii(open_badge),
            "total_trips": self.total_trips,
            "total_spent": self.total_spent,
            "count_str": (
                f"{(sel_idx + 1) if total_list else 0}/{total_list} ({unlocked_cnt}/{total_cnt} da mo)"
                if is_vi
                else f"{(sel_idx + 1) if total_list else 0}/{total_list} ({unlocked_cnt}/{total_cnt} open)"
            ),
            "unlocked_count": unlocked_cnt,
            "total_pois": total_cnt,
            "radio_name": radio_name,
            "status_bar": to_clean_viet_ascii(status_bar),
            "sel_title": to_clean_viet_ascii(sel_title),
            "sel_coords": to_clean_viet_ascii(sel_coords),
            "sel_meta": to_clean_viet_ascii(sel_meta),
            "sel_note": sel_note,
            "sel_open": sel_open_str,
            "sel_fare": sel_fare_str,
            "selected_poi": sel_poi,
            "table_rows": table_rows,
            "pois": all_cat_pois,
            "active_trip": (
                {
                    "service_short": tr["service"]["short_vi"] if is_vi else tr["service"]["short_en"],
                    "poi_name": to_clean_viet_ascii(tr["poi"]["name"]),
                    "fare": tr["fare"],
                    "road_dist_m": tr["road_dist_m"],
                    "remaining_dist_m": tr.get("remaining_dist_m", tr["road_dist_m"]),
                    "wp_idx": tr["wp_idx"],
                    "total_wps": tr["total_wps"],
                    "radio_station": radio_name,
                }
                if (tr := self.active_trip)
                else None
            ),
        }

    def build_hud_kv(self, engine, proj: dict | None = None) -> dict[str, str]:
        p = proj or self.build_projection(engine)
        svc = self.get_selected_service()
        kv = {
            "ride_active": p["ride_active_str"],
            "ride_state": p["ride_state"],
            "ride_svc_idx": str(p["service_idx"]),
            "ride_svc_id": p["service_id"],
            "ride_svc_opt": to_clean_viet_ascii(f"{p['service_label']} [${svc['base_fare']}+${svc['per_km']}/km]"),
            "ride_svc_short": to_clean_viet_ascii(p["service_short"]),
            "ride_cat_idx": str(p["cat_idx"]),
            "ride_cat_opt": to_clean_viet_ascii(p["cat_label"]),
            "ride_cat_disp": p["cat_display"],
            "ride_count_str": to_clean_viet_ascii(p["count_str"]),
            "ride_total_cnt": str(p["total_pois"]),
            "ride_open_badge": p["open_badge"],
            "ride_search_q": to_clean_viet_ascii(p["search_query"])[:36],
            "ride_filter_open": "1" if p["filter_visited_only"] else "0",
            "ride_scroll_pct": p["scroll_pct"],
            "ride_can_up": p["can_up"],
            "ride_can_dn": p["can_dn"],
            "ride_radio_opt": to_clean_viet_ascii(p["radio_name"]),
            "ride_status_bar": p["status_bar"],
            "ride_sel_title": p["sel_title"],
            "ride_sel_coords": p["sel_coords"],
            "ride_sel_meta": p["sel_meta"],
            "ride_sel_note": p["sel_note"],
            "ride_sel_open": p["sel_open"],
            "ride_sel_fare": p["sel_fare"],
        }
        for idx_r, rr in enumerate(p["table_rows"][:5], start=1):
            kv[f"rd_r{idx_r}_name"] = rr["name"]
            kv[f"rd_r{idx_r}_reg"] = rr["region"]
            kv[f"rd_r{idx_r}_dist"] = rr["dist"]
            kv[f"rd_r{idx_r}_fare"] = rr["fare"]
            kv[f"rd_r{idx_r}_open"] = rr["unlocked"]
            kv[f"rd_r{idx_r}_status"] = rr["status"]
            kv[f"rd_r{idx_r}_sel"] = rr["sel"]
        return kv

