import argparse, csv, heapq, math, time, os, glob
from collections import deque

# ---------- Core search algorithms ----------
MOVES = [(1,0),(-1,0),(0,1),(0,-1)]

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def neighbors(node, grid):
    x, y = node
    h = len(grid)
    w = len(grid[0])
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 0:
            yield (nx, ny)

def reconstruct(came, start, goal):
    if goal not in came:
        return []
    cur = goal
    path = [cur]
    while cur != start:
        cur = came.get(cur)
        if cur is None:
            return []
        path.append(cur)
    path.reverse()
    return path

def precompute_risk_map(grid, depth=2):
    h = len(grid)
    w = len(grid[0])
    risk = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if grid[y][x] == 1:
                risk[y][x] = 0
                continue
            score = 0
            for dy in range(-depth, depth+1):
                for dx in range(-depth, depth+1):
                    ny, nx = y + dy, x + dx
                    if not (0 <= ny < h and 0 <= nx < w) or grid[ny][nx] == 1:
                        score += 1
            risk[y][x] = score
    return risk

def astar_search(grid, start, goal, cap, risk_map=None):
    t0 = time.perf_counter()
    pq = [(manhattan(start, goal), 0, start)]
    g = {start: 0}
    came = {start: None}
    visited = set()
    expansions = 0
    while pq:
        f, cost, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            ng = cost + 1
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                came[nb] = cur
                heapq.heappush(pq, (ng + manhattan(nb, goal), ng, nb))
        if expansions > cap:
            break
    return 0, expansions, 0, 0, (time.perf_counter()-t0)*1000, 0

def weighted_astar_search(grid, start, goal, cap, risk_map=None, weight=1.5):
    t0 = time.perf_counter()
    pq = [(manhattan(start, goal)*weight, 0, start)]
    g = {start: 0}
    came = {start: None}
    visited = set()
    expansions = 0
    while pq:
        f, cost, cur = heapq.heappop(pq)
        if cur in visited: continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            ng = cost + 1
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                came[nb] = cur
                heapq.heappush(pq, (ng + weight*manhattan(nb, goal), ng, nb))
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

def dijkstra_search(grid, start, goal, cap, risk_map=None):
    t0 = time.perf_counter()
    pq = [(0, start)]
    dist = {start: 0}
    came = {start: None}
    visited = set()
    expansions = 0
    while pq:
        d, cur = heapq.heappop(pq)
        if cur in visited: continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            nd = d + 1
            if nb not in dist or nd < dist[nb]:
                dist[nb] = nd
                came[nb] = cur
                heapq.heappush(pq, (nd, nb))
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

def greedy_search(grid, start, goal, cap, risk_map=None):
    t0 = time.perf_counter()
    pq = [(manhattan(start, goal), start)]
    came = {start: None}
    visited = set()
    seen = {start}
    expansions = 0
    while pq:
        _, cur = heapq.heappop(pq)
        if cur in visited: continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            if nb not in seen:
                seen.add(nb)
                came[nb] = cur
                heapq.heappush(pq, (manhattan(nb, goal), nb))
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

def risk_aware_astar_search(grid, start, goal, cap, risk_map=None, risk_weight=0.75):
    t0 = time.perf_counter()
    pq = [(manhattan(start, goal) + (risk_map[start[1]][start[0]] * risk_weight if risk_map else 0), 0, start)]
    g = {start: 0}
    came = {start: None}
    visited = set()
    expansions = 0
    while pq:
        f, cost, cur = heapq.heappop(pq)
        if cur in visited: continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            step_cost = 1 + (risk_weight * (risk_map[nb[1]][nb[0]] if risk_map else 0))
            ng = cost + step_cost
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                came[nb] = cur
                heapq.heappush(pq, (ng + manhattan(nb, goal), ng, nb))
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

def chance_constrained_astar_search(grid, start, goal, cap, risk_map=None, risk_budget=None):
    t0 = time.perf_counter()
    if risk_map is None:
        return astar_search(grid, start, goal, cap, risk_map)
    if risk_budget is None:
        risk_budget = len(grid) * 30
    start_risk = risk_map[start[1]][start[0]]
    pq = [(manhattan(start, goal), 0, start, start_risk)]
    best = {(start, start_risk): 0}
    came = {(start, start_risk): None}
    expansions = 0
    def reconstruct_state(came, state):
        path = []
        while state is not None:
            node, _ = state
            path.append(node)
            state = came[state]
        path.reverse()
        return path
    while pq:
        f, cost, cur, risk = heapq.heappop(pq)
        state = (cur, risk)
        if best.get(state, float('inf')) < cost:
            continue
        expansions += 1
        if cur == goal:
            path = reconstruct_state(came, state)
            path_risk = sum(risk_map[y][x] for x, y in path)
            return len(path), expansions, 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            new_risk = risk + risk_map[nb[1]][nb[0]]
            if new_risk > risk_budget:
                continue
            ng = cost + 1
            new_state = (nb, new_risk)
            if ng < best.get(new_state, float('inf')):
                best[new_state] = ng
                came[new_state] = state
                heapq.heappush(pq, (ng + manhattan(nb, goal), ng, nb, new_risk))
        if expansions > cap: break
    return 0, expansions, 0, 0, (time.perf_counter()-t0)*1000, 0

def cvar_astar_search(grid, start, goal, cap, risk_map=None, risk_weight=0.5, risk_threshold=None):
    t0 = time.perf_counter()
    if risk_map is None:
        return astar_search(grid, start, goal, cap, risk_map)
    if risk_threshold is None:
        risk_threshold = len(grid) * 15
    start_risk = risk_map[start[1]][start[0]]
    pq = [(manhattan(start, goal) + risk_weight * max(0, start_risk - risk_threshold), 0, start, start_risk)]
    best = {(start, start_risk): 0}
    came = {(start, start_risk): None}
    expansions = 0
    def reconstruct_state(came, state):
        path = []
        while state is not None:
            node, _ = state
            path.append(node)
            state = came[state]
        path.reverse()
        return path
    while pq:
        f, cost, cur, risk = heapq.heappop(pq)
        state = (cur, risk)
        if best.get(state, float('inf')) < cost:
            continue
        expansions += 1
        if cur == goal:
            path = reconstruct_state(came, state)
            path_risk = sum(risk_map[y][x] for x, y in path)
            return len(path), expansions, 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            new_risk = risk + risk_map[nb[1]][nb[0]]
            ng = cost + 1
            penalty = risk_weight * max(0, new_risk - risk_threshold)
            new_state = (nb, new_risk)
            if ng < best.get(new_state, float('inf')):
                best[new_state] = ng
                came[new_state] = state
                heapq.heappush(pq, (ng + manhattan(nb, goal) + penalty, ng, nb, new_risk))
        if expansions > cap: break
    return 0, expansions, 0, 0, (time.perf_counter()-t0)*1000, 0

def zen_path_search_optimized(grid, start, goal, cap, risk_map, prefer='local', base_thr=None):
    h = len(grid)
    w = len(grid[0])
    sx, sy = start
    gx, gy = goal
    if grid[sy][sx] != 0 or grid[gy][gx] != 0:
        return 0, 0, 0, 0, 0.0, 0.0
    t0 = time.perf_counter()
    g = {start: 0.0}
    risk_so_far = {start: 0.0}
    came = {start: None}
    closed = set()
    expansions = 0
    def get_priority(node):
        f = g[node] + (abs(node[0] - gx) + abs(node[1] - gy))
        if prefer == 'path':
            risk_key = risk_so_far[node]
        else:
            risk_key = risk_map[node[1]][node[0]]
        if base_thr is not None:
            risk_key = 1 if risk_key > base_thr else 0
        return (f, risk_key)
    pq = [(get_priority(start), start)]
    while pq and expansions < cap:
        _, cur = heapq.heappop(pq)
        if cur in closed:
            continue
        closed.add(cur)
        expansions += 1
        if cur == goal:
            path = []
            v = cur
            while v is not None:
                path.append(v)
                v = came[v]
            path.reverse()
            path_risk = sum(risk_map[y][x] for x, y in path)
            runtime = (time.perf_counter() - t0) * 1000
            return len(path), expansions, 1, 0, runtime, path_risk
        x, y = cur
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 0:
                nb = (nx, ny)
                ng = g[cur] + 1.0
                if nb not in g or ng < g[nb]:
                    g[nb] = ng
                    came[nb] = cur
                    if prefer == 'path':
                        risk_so_far[nb] = risk_so_far[cur] + risk_map[ny][nx]
                    heapq.heappush(pq, (get_priority(nb), nb))
    runtime = (time.perf_counter() - t0) * 1000
    return 0, expansions, 0, 0, runtime, 0.0

def rest_astar_search(grid, start, goal, cap, risk_map=None, alpha=2.0, beta=0.5):
    t0 = time.perf_counter()
    if risk_map is None:
        return astar_search(grid, start, goal, cap, risk_map)
    # BFS to compute shortest path length Lmin
    q = deque([start])
    dist = {start: 0}
    while q:
        cur = q.popleft()
        if cur == goal:
            Lmin = dist[cur]
            break
        for nb in neighbors(cur, grid):
            if nb not in dist:
                dist[nb] = dist[cur] + 1
                q.append(nb)
    else:
        h = len(grid)
        w = len(grid[0])
        Lmin = w * h
    # Main search
    pq = [(manhattan(start, goal), 0, start)]
    g = {start: 0.0}
    came = {start: None}
    visited = set()
    expansions = 0
    while pq:
        f, cost, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path)
            runtime = (time.perf_counter() - t0) * 1000
            return len(path), expansions, 1, 0, runtime, path_risk
        x, y = cur
        extra = max(0, g[cur] - Lmin)
        T = alpha / (1.0 + beta * extra)
        for nb in neighbors(cur, grid):
            nx, ny = nb
            step_cost = 1.0 + risk_map[ny][nx] * T
            ng = g[cur] + step_cost
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                came[nb] = cur
                heapq.heappush(pq, (ng + manhattan(nb, goal), ng, nb))
        if expansions > cap:
            break
    runtime = (time.perf_counter() - t0) * 1000
    return 0, expansions, 0, 0, runtime, 0.0

def bra_star_search(grid, start, goal, cap, risk_map=None, eps=0.1, use_heuristic=True, best_known_risk=None):
    """
    Improved Bounded Risk A* (BRA*).
    Uses a risk heuristic (Dijkstra from goal) to guide the search.
    If best_known_risk is provided (e.g., from ZEN), we can prune states whose lower bound
    already exceeds this value, making the search much faster.
    """
    t0 = time.perf_counter()
    if risk_map is None:
        return astar_search(grid, start, goal, cap, risk_map)

    h = len(grid)
    w = len(grid[0])

    # ---------- Precompute risk heuristic (lower bound of remaining risk) ----------
    risk_heuristic = None
    if use_heuristic:
        # Dijkstra from goal on the risk map (ignoring obstacles? Actually we need to avoid obstacles)
        # We'll compute the minimal risk to reach goal from any cell using Dijkstra.
        # Since risk is non‑negative, we can run Dijkstra on the graph.
        import heapq as hq
        dist = [[float('inf')] * w for _ in range(h)]
        dist[goal[1]][goal[0]] = risk_map[goal[1]][goal[0]]
        pq = [(risk_map[goal[1]][goal[0]], goal[0], goal[1])]
        while pq:
            d, x, y = hq.heappop(pq)
            if d != dist[y][x]:
                continue
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 0:
                    nd = d + risk_map[ny][nx]
                    if nd < dist[ny][nx]:
                        dist[ny][nx] = nd
                        hq.heappush(pq, (nd, nx, ny))
        # dist now holds the minimal additional risk from that cell to goal
        risk_heuristic = dist

    # Compute L_min (shortest path length ignoring risk) using BFS
    from collections import deque
    q = deque([start])
    dist_len = {start: 0}
    Lmin = None
    while q:
        cur = q.popleft()
        if cur == goal:
            Lmin = dist_len[cur]
            break
        for nb in neighbors(cur, grid):
            if nb not in dist_len:
                dist_len[nb] = dist_len[cur] + 1
                q.append(nb)
    if Lmin is None:
        return 0, 0, 0, 0, 0.0, 0.0

    max_len = int((1.0 + eps) * Lmin)

    # If no risk heuristic, fall back to original implementation (but we will use it)
    if risk_heuristic is None:
        # use a default zero heuristic
        risk_heuristic = [[0]*w for _ in range(h)]

    # If best_known_risk is not provided, we can run ZEN quickly to get an upper bound
    if best_known_risk is None:
        # Run ZEN (or A*) to get a feasible risk (could be a simple call)
        # But to save time, we can use a large number.
        best_known_risk = float('inf')
    else:
        best_known_risk = best_known_risk  # user provided

    # Priority queue: (risk_so_far + risk_heuristic, steps, risk_so_far, node)
    # We want to expand low total risk first, but also respect steps constraint.
    start_risk = risk_map[start[1]][start[0]]
    pq = [(start_risk + risk_heuristic[start[1]][start[0]], 0, start_risk, start)]
    # For each cell, we keep the best risk achieved for each step count.
    # We'll use a dict of dicts: best[cell] = {steps: risk}
    best = {start: {0: start_risk}}
    came = {(start, 0): (None, None)}
    expansions = 0

    while pq:
        f, steps, risk, cur = heapq.heappop(pq)
        # Prune if lower bound already exceeds best known risk
        if f >= best_known_risk:
            continue
        if cur not in best or steps not in best[cur] or risk > best[cur][steps]:
            continue
        expansions += 1

        if cur == goal:
            # Reconstruct path
            path = []
            state = (cur, steps)
            while state[0] is not None:
                node, _ = state
                path.append(node)
                state = came[state]
            path.reverse()
            path_risk = sum(risk_map[y][x] for x, y in path)
            runtime = (time.perf_counter() - t0) * 1000
            return len(path), expansions, 1, 0, runtime, path_risk

        if steps >= max_len:
            continue

        x, y = cur
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 0:
                nb = (nx, ny)
                new_steps = steps + 1
                new_risk = risk + risk_map[ny][nx]
                # Lower bound for the total risk if we go through this neighbour
                lb = new_risk + risk_heuristic[ny][nx]
                if lb >= best_known_risk:
                    continue
                # Check dominance: if the neighbour already has a state with
                # steps <= new_steps and risk <= new_risk, skip
                if nb in best:
                    dominated = False
                    for s, r in best[nb].items():
                        if s <= new_steps and r <= new_risk:
                            dominated = True
                            break
                    if dominated:
                        continue
                    # Remove any states that are dominated by this new one
                    to_remove = [s for s, r in best[nb].items() if s >= new_steps and r >= new_risk]
                    for s in to_remove:
                        del best[nb][s]
                else:
                    best[nb] = {}
                best[nb][new_steps] = new_risk
                came[(nb, new_steps)] = (cur, steps)
                heapq.heappush(pq, (lb, new_steps, new_risk, nb))

        if expansions > cap:
            break

    runtime = (time.perf_counter() - t0) * 1000
    return 0, expansions, 0, 0, runtime, 0.0

def original_zen_path_search(grid, start, goal, cap, risk_map=None, risk_weight=0.5, dynamic=False, delta=0.2):
    """
    Original ZEN-Path algorithm from the paper.
    f(n) = g(n) + h(n) + lambda * R(n)
    If dynamic=True, risk is updated online using R_t = (1-delta)*R_{t-1} + delta*R_obs
    """
    t0 = time.perf_counter()
    if risk_map is None:
        return astar_search(grid, start, goal, cap, risk_map)

    h = len(grid)
    w = len(grid[0])
    risk = [row[:] for row in risk_map]  # copy for potential dynamic updates

    pq = [(manhattan(start, goal) + risk_weight * risk[start[1]][start[0]], 0, start)]
    g = {start: 0}
    came = {start: None}
    visited = set()
    expansions = 0

    while pq:
        f, cost, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path)
            runtime = (time.perf_counter() - t0) * 1000
            return len(path), expansions, 1, 0, runtime, path_risk

        if expansions > cap:
            break

        x, y = cur
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 0:
                nb = (nx, ny)
                ng = g[cur] + 1
                # Dynamic risk update: simulate observation of risk at nb
                if dynamic:
                    # new observation = risk_map[ny][nx] (true risk)
                    # update stored risk at nb
                    risk[ny][nx] = (1 - delta) * risk[ny][nx] + delta * risk_map[ny][nx]
                nb_risk = risk[ny][nx]
                new_f = ng + manhattan(nb, goal) + risk_weight * nb_risk
                if nb not in g or ng < g[nb]:
                    g[nb] = ng
                    came[nb] = cur
                    heapq.heappush(pq, (new_f, ng, nb))

    runtime = (time.perf_counter() - t0) * 1000
    return 0, expansions, 0, 0, runtime, 0.0

def bfs_search(grid, start, goal, cap, risk_map=None):
    t0 = time.perf_counter()
    q = deque([start])
    came = {start: None}
    visited = set([start])
    expansions = 0
    while q:
        cur = q.popleft()
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            if nb not in visited:
                visited.add(nb)
                came[nb] = cur
                q.append(nb)
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

def dfs_search(grid, start, goal, cap, risk_map=None):
    t0 = time.perf_counter()
    stack = [start]
    came = {start: None}
    visited = set([start])
    expansions = 0
    while stack:
        cur = stack.pop()
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            if nb not in visited:
                visited.add(nb)
                came[nb] = cur
                stack.append(nb)
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

def risk_aware_dijkstra_search(grid, start, goal, cap, risk_map=None, risk_weight=0.75):
    t0 = time.perf_counter()
    pq = [(0, start)]
    dist = {start: 0}
    came = {start: None}
    visited = set()
    expansions = 0
    while pq:
        d, cur = heapq.heappop(pq)
        if cur in visited: continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            step_cost = 1 + (risk_weight * (risk_map[nb[1]][nb[0]] if risk_map else 0))
            nd = d + step_cost
            if nb not in dist or nd < dist[nb]:
                dist[nb] = nd
                came[nb] = cur
                heapq.heappush(pq, (nd, nb))
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

def risk_greedy_search(grid, start, goal, cap, risk_map=None, risk_weight=0.5):
    t0 = time.perf_counter()
    start_risk = risk_map[start[1]][start[0]] if risk_map else 0
    pq = [(manhattan(start, goal) + risk_weight * start_risk, start)]
    came = {start: None}
    visited = set()
    seen = {start}
    expansions = 0
    while pq:
        _, cur = heapq.heappop(pq)
        if cur in visited: continue
        visited.add(cur)
        expansions += 1
        if cur == goal:
            path = reconstruct(came, start, goal)
            path_risk = sum(risk_map[y][x] for x, y in path) if risk_map else 0
            return len(path), len(visited), 1, 0, (time.perf_counter()-t0)*1000, path_risk
        for nb in neighbors(cur, grid):
            if nb not in seen:
                seen.add(nb)
                came[nb] = cur
                heuristic = manhattan(nb, goal) + (risk_weight * (risk_map[nb[1]][nb[0]] if risk_map else 0))
                heapq.heappush(pq, (heuristic, nb))
        if expansions > cap: break
    return 0, len(visited), 0, 0, (time.perf_counter()-t0)*1000, 0

# ---------- Map loading ----------
def load_map(filepath):
    """Load Moving AI .map file. Returns grid (list of list of int: 0 free, 1 obstacle)."""
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    height = width = None
    grid_lines = []
    reading_map = False
    for line in lines:
        if line.startswith('height'):
            height = int(line.split()[1])
        elif line.startswith('width'):
            width = int(line.split()[1])
        elif line.startswith('map'):
            reading_map = True
            continue
        elif reading_map:
            # '.' = free, anything else = obstacle
            row = [0 if ch == '.' else 1 for ch in line]
            grid_lines.append(row)
    if height is None or width is None:
        raise ValueError(f"Missing height/width in {filepath}")
    if len(grid_lines) != height:
        print(f"Warning: expected {height} rows, got {len(grid_lines)} in {filepath}. Truncating/padding.")
        grid_lines = grid_lines[:height]
    for i in range(len(grid_lines)):
        if len(grid_lines[i]) != width:
            print(f"Warning: row {i} length {len(grid_lines[i])}, expected {width}. Adjusting.")
            if len(grid_lines[i]) < width:
                grid_lines[i].extend([1] * (width - len(grid_lines[i])))
            else:
                grid_lines[i] = grid_lines[i][:width]
    return grid_lines

# ---------- Main benchmark ----------
ALGO_FUNCS = [
    ("ZEN", zen_path_search_optimized),
    ("A*", astar_search),
    ("Weighted A*", weighted_astar_search),
    ("Chance-Constrained A*", chance_constrained_astar_search),
    ("CVaR A*", cvar_astar_search),
    ("Risk-Penalized A*", risk_aware_astar_search),
    ("Risk-Penalized Dijkstra", risk_aware_dijkstra_search),
    ("Risk-Penalized Greedy", risk_greedy_search),
    ("REST A*", rest_astar_search),
    ("BRA*", bra_star_search),
    ("BFS", bfs_search),
    ("DFS", dfs_search),
    ("Dijkstra", dijkstra_search),
    ("Original ZEN-Path", original_zen_path_search),
    ("Greedy", greedy_search),
]

def run_benchmark_on_maps(map_dir, output_csv="street_map_results.csv"):
    map_dir = os.path.abspath(map_dir)
    map_files = glob.glob(os.path.join(map_dir, "*.map"))
    print(f"Found {len(map_files)} map files.")
    all_rows = []
    for map_path in map_files:
        map_name = os.path.splitext(os.path.basename(map_path))[0]
        print(f"Processing {map_name}...")
        try:
            grid = load_map(map_path)
        except Exception as e:
            print(f"  Failed to load {map_name}: {e}")
            continue
        h = len(grid)
        w = len(grid[0])
        risk_map = precompute_risk_map(grid)
        start = (0, 0)
        goal = (w-1, h-1)
        if grid[start[1]][start[0]] != 0 or grid[goal[1]][goal[0]] != 0:
            print(f"  Start or goal blocked on {map_name}, skipping.")
            continue
        cap = w * h * 4
        for name, func in ALGO_FUNCS:
            # Initialize default values
            path_len = visited = success = hes = 0
            tms = 0.0
            path_risk = 0
            try:
                if name == "REST A*":
                    res = func(grid, start, goal, cap, risk_map=risk_map, alpha=2.0, beta=0.5)
                elif name == "BRA*":
                    res = func(grid, start, goal, cap, risk_map=risk_map, eps=0.1)
                else:
                    res = func(grid, start, goal, cap, risk_map=risk_map)
                path_len, visited, success, hes, tms, path_risk = res
            except Exception as e:
                print(f"  Error in {name} on {map_name}: {e}")
                # keep defaults
            all_rows.append({
                "Algorithm": name,
                "Map": map_name,
                "Path_Length": int(path_len),
                "Visited": int(visited),
                "Success": int(bool(success)),
                "Hesitations": int(hes),
                "Time_ms": float(tms),
                "Path_Risk_Score": float(path_risk)
            })
    with open(output_csv, 'w', newline='') as f:
        fieldnames = ["Algorithm","Map","Path_Length","Visited","Success","Hesitations","Time_ms","Path_Risk_Score"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Results saved to {output_csv}")
    return all_rows

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        map_dir = sys.argv[1]
    else:
        map_dir = "street-map"
    run_benchmark_on_maps(map_dir)