import tkinter as tk
import heapq
import random

# ---------------------------
# Option B graph (9 nodes)
# ---------------------------
BASE_PAIRS = [
    (0, 1), (0, 4),
    (1, 2), (1, 3),
    (2, 3),
    (3, 5), (3, 7),
    (4, 5),
    (5, 6), (5, 7),
    (6, 8),
    (7, 8)
]

NODE_COUNT = 9
NODE_RADIUS = 26

NODE_POS = {
    0: (220, 70),
    1: (120, 150),
    4: (320, 150),
    2: (80, 260),
    3: (180, 260),
    5: (260, 260),
    6: (360, 260),
    7: (230, 340),
    8: (330, 360),
}

# ===========================
# Globals and UI handles
# ===========================
root = None
canvas = None
pq_listbox = None
dist_text = None
status_label = None
target_var = None
target_dropdown = None
show_path_button = None
highlight_neighbors_button = None

# Canvas item ids so we can recolor in-place
node_circle_id = {}   # node -> canvas oval id
node_text_id = {}     # node -> canvas text id
edge_id = {}          # (min,max) -> canvas line id
dist_canvas_text_id = {}  # node -> canvas text id for dist under canvas (optional)

# Algorithm state
edges = {}        # (a,b) -> weight both directions
adj = {}          # adjacency list: node -> [neighbor nodes]
actions = []      # recorded actions
action_index = 0
display_pq = []
distances = {}
prev_map = {}
started = False
finished = False

# Utility: initialize edges & adjacency
def generate_weights():
    global edges, adj
    edges.clear()
    adj = {i: [] for i in range(NODE_COUNT)}
    for a, b in BASE_PAIRS:
        w = random.randint(1, 10)
        edges[(a, b)] = w
        edges[(b, a)] = w
        adj[a].append(b)
        adj[b].append(a)

# Record Dijkstra (step actions)
def record_dijkstra_steps(start=0):
    local_actions = []
    dist = {i: float('inf') for i in range(NODE_COUNT)}
    dist[start] = 0
    prev_local = {i: None for i in range(NODE_COUNT)}
    heap = []
    heapq.heappush(heap, (0, start))
    local_actions.append(("push", (0, start)))

    while heap:
        d, u = heapq.heappop(heap)
        # skip stale
        if d != dist[u]:
            continue
        local_actions.append(("pop", (d, u)))
        for v in adj[u]:
            w = edges[(u, v)]
            local_actions.append(("consider", (u, v, w)))
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev_local[v] = u
                heapq.heappush(heap, (dist[v], v))
                local_actions.append(("update", (v, dist[v], u)))
                local_actions.append(("push", (dist[v], v)))
    return local_actions, prev_local

# ===========================
# Drawing (create items once)
# ===========================
BASE_NODE_FILL = "#0b1220"
BASE_NODE_OUTLINE = "#0ee7ff"
BASE_EDGE_COLOR = "#777"
BASE_DIST_BG = "#07111a"

def create_graph_items():
    """Create lines and nodes once and store their ids for in-place recolor."""
    canvas.delete("all")
    edge_id.clear()
    node_circle_id.clear()
    node_text_id.clear()
    dist_canvas_text_id.clear()

    # draw edges (only once per undirected pair)
    seen = set()
    for (a, b), w in edges.items():
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        x1, y1 = NODE_POS[a]
        x2, y2 = NODE_POS[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        cx, cy = mx - dy * 0.06, my + dx * 0.06
        lid = canvas.create_line(x1, y1, cx, cy, x2, y2, fill=BASE_EDGE_COLOR, width=2, smooth=True)
        edge_id[key] = lid
        tx, ty = (mx + cx) / 2, (my + cy) / 2
        canvas.create_text(tx, ty, text=str(w), fill="#ffd580", font=("Consolas", 11, "bold"))
        seen.add(key)

    # draw nodes
    for n in range(NODE_COUNT):
        x, y = NODE_POS[n]
        oid = canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS,
                                 fill=BASE_NODE_FILL, outline=BASE_NODE_OUTLINE, width=3)
        tid = canvas.create_text(x, y, text=str(n), fill="white", font=("Segoe UI", 14, "bold"))
        node_circle_id[n] = oid
        node_text_id[n] = tid

    # dist texts under canvas (we create but will update values via itemconfig)
    y = 420
    start_x = 60
    box_w = 72
    box_h = 36
    canvas.create_text(40, y - 22, text="dist[] =", fill="white", anchor="w", font=("Consolas", 12, "bold"))
    for i in range(NODE_COUNT):
        x = start_x + i * (box_w + 6)
        # draw rectangle background (not stored)
        canvas.create_rectangle(x, y, x + box_w, y + box_h, outline="#888", fill=BASE_DIST_BG, width=2)
        txt_id = canvas.create_text(x + box_w / 2, y + box_h / 2, text="∞", fill="white", font=("Consolas", 12, "bold"))
        dist_canvas_text_id[i] = txt_id
        # index label
        canvas.create_text(x + box_w / 2, y + box_h + 14, text=str(i), fill="#aaa")

# ===========================
# In-place recolor helpers
# ===========================
def set_node_color(n, fill=None, outline=None, text_color=None):
    """Change node circle and text colors without redrawing everything."""
    if n not in node_circle_id:
        return
    if fill is not None:
        canvas.itemconfig(node_circle_id[n], fill=fill)
    if outline is not None:
        canvas.itemconfig(node_circle_id[n], outline=outline)
    if text_color is not None:
        canvas.itemconfig(node_text_id[n], fill=text_color)

def set_edge_color(u, v, color=None, width=None):
    key = (min(u, v), max(u, v))
    lid = edge_id.get(key)
    if not lid:
        return
    if color is not None:
        canvas.itemconfig(lid, fill=color)
    if width is not None:
        canvas.itemconfig(lid, width=width)

def update_dist_canvas(i):
    txt_id = dist_canvas_text_id.get(i)
    if txt_id:
        d = distances.get(i, float('inf'))
        canvas.itemconfig(txt_id, text=("∞" if d == float('inf') else str(d)))

# reset visuals to base
def reset_visuals():
    for n in range(NODE_COUNT):
        set_node_color(n, fill=BASE_NODE_FILL, outline=BASE_NODE_OUTLINE, text_color="white")
    for (a, b) in edge_id.keys():
        set_edge_color(a, b, color=BASE_EDGE_COLOR, width=2)

# Apply recorded actions
def apply_action(act):
    typ, data = act
    if typ == "push":
        d, u = data
        display_pq.append((d, u))
        display_pq.sort()
        refresh_pq()
        status_label.config(text=f"PUSH {d, u} into PQ")
    elif typ == "pop":
        d, u = data
        try:
            display_pq.remove((d, u))
        except ValueError:
            if display_pq:
                display_pq.pop(0)
        # color node as finalized (green)
        set_node_color(u, fill="#10b981", outline="#ffffff", text_color="black")
        refresh_pq()
        status_label.config(text=f"POP {d, u} from PQ (finalized)")
    elif typ == "consider":
        u, v, w = data
        # mark edge and node being considered (cyan)
        set_node_color(v, fill="#60a5fa", text_color="black")
        set_edge_color(u, v, color="#60a5fa", width=3)
        status_label.config(text=f"Consider edge {u} → {v} (w={w})")
    elif typ == "update":
        v, newd, frm = data
        distances[v] = newd
        prev_map[v] = frm
        update_dist_canvas(v)
        set_node_color(v, fill="#fb923c", text_color="black")  # orange for update
        status_label.config(text=f"Update: dist[{v}] = {newd}")
# Controls: start/next/run/reset/show path/highlight neighbors
def on_start():
    global actions, action_index, display_pq, prev_map, started, finished
    generate_weights()
    actions, prev_map_local = record_dijkstra_steps(0)
    prev_map.clear()
    prev_map.update(prev_map_local)

    # reset states
    action_index = 0
    display_pq.clear()
    for i in range(NODE_COUNT):
        distances[i] = float('inf')
        update_dist_canvas(i)
    distances[0] = 0
    update_dist_canvas(0)

    reset_visuals()
    refresh_pq()
    draw_graph_items_once()
    started = True
    finished = False

    # disable target controls until finished
    target_dropdown.config(state="disabled")
    show_path_button.config(state="disabled")
    highlight_neighbors_button.config(state="disabled")
    status_label.config(text="Started. Use NEXT (step) or RUN TO END.")

def run_step():
    global action_index
    if action_index >= len(actions):
        return
    act = actions[action_index]
    # for update actions, update dist before applying visual so canvas dist syncs
    if act[0] == "update":
        v, newd, frm = act[1]
        distances[v] = newd
        update_dist_canvas(v)
        prev_map[v] = frm
    apply_action(act)
    action_index += 1

def on_next():
    global finished, started
    if not started:
        status_label.config(text="Press START first.")
        return
    run_step()
    if action_index >= len(actions):
        finish_algorithm()

def on_run_all():
    global started
    if not started:
        status_label.config(text="Press START first.")
        return
    while action_index < len(actions):
        run_step()
    finish_algorithm()

def finish_algorithm():
    global finished
    finished = True
    # re-enable target controls
    target_dropdown.config(state="normal")
    show_path_button.config(state="normal")
    highlight_neighbors_button.config(state="normal")
    status_label.config(text="Dijkstra finished — choose target and SHOW PATH or HIGHLIGHT NEIGHBORS.")

def on_show_path():
    try:
        t = int(target_var.get())
    except Exception:
        status_label.config(text="Select a valid target.")
        return
    # reconstruct path
    path = []
    cur = t
    # if unreachable, prev_map may be None; still show single node
    while cur is not None:
        path.append(cur)
        cur = prev_map.get(cur, None)
    path.reverse()
    # recolor path edges and nodes (modify in place)
    for n in path:
        set_node_color(n, fill="#ffd700", text_color="black")   # gold
    for i in range(len(path)-1):
        set_edge_color(path[i], path[i+1], color="#ff4444", width=5)
    status_label.config(text=f"Shortest path 0 → {t}: {' → '.join(map(str, path))}")

def on_highlight_neighbors():
    try:
        t = int(target_var.get())
    except Exception:
        status_label.config(text="Select a valid target.")
        return
    # recolor selected node & its neighbors + edges
    set_node_color(t, fill="#ffd700", text_color="black")
    for nbr in adj.get(t, []):
        set_node_color(nbr, fill="#61c0ff", text_color="black")
        set_edge_color(t, nbr, color="#ff4444", width=5)
    status_label.config(text=f"Neighbors of {t} highlighted.")

def on_reset():
    global started, finished, action_index, actions
    started = False
    finished = False
    actions = []
    action_index = 0
    display_pq.clear()
    for i in range(NODE_COUNT):
        distances[i] = float('inf')
        prev_map[i] = None
        update_dist_canvas(i)
    reset_visuals()
    refresh_pq()
    draw_graph_items_once()
    # disable target controls
    target_dropdown.config(state="disabled")
    show_path_button.config(state="disabled")
    highlight_neighbors_button.config(state="disabled")
    status_label.config(text="Reset. Press START.")

# ===========================
# Create / redraw utility
# ===========================
def draw_graph_items_once():
    # Create items once (if already created, keep existing ids)
    # To simplify, recreate everything fresh then re-store ids.
    create_graph_items()
    # update canvas dist texts
    for i in range(NODE_COUNT):
        update_dist_canvas(i)

# ===========================
# PQ & dist text refresh
# ===========================
def refresh_pq():
    pq_listbox.delete(0, tk.END)
    for d, u in sorted(display_pq):
        pq_listbox.insert(tk.END, f"({d}, {u})")

def refresh_dist_text_widget():
    dist_text.delete("1.0", tk.END)
    for i in range(NODE_COUNT):
        d = distances.get(i, float('inf'))
        dist_text.insert(tk.END, f"{i}: {'∞' if d == float('inf') else d}\n")

# ===========================
# Build UI
# ===========================
def build_ui():
    global root, canvas, pq_listbox, dist_text
    global status_label, target_var, target_dropdown
    global show_path_button, highlight_neighbors_button

    root = tk.Tk()
    root.title("Dijkstra Visualization — In-place recolor (persistent)")
    root.geometry("1120x720")
    root.config(bg="#10131a")

    top = tk.Frame(root, bg="#10131a")
    top.pack(pady=6)

    tk.Button(top, text="START", width=10, bg="#34d399", command=on_start).grid(row=0, column=0, padx=4)
    tk.Button(top, text="NEXT", width=10, bg="#60a5fa", command=on_next).grid(row=0, column=1, padx=4)
    tk.Button(top, text="RUN TO END", width=12, bg="#fbbf24", command=on_run_all).grid(row=0, column=2, padx=4)
    tk.Button(top, text="RESET", width=10, bg="#ef4444", command=on_reset).grid(row=0, column=3, padx=4)

    status_label = tk.Label(top, text="Press START.", bg="#10131a", fg="white")
    status_label.grid(row=0, column=4, padx=8)

    main = tk.Frame(root, bg="#10131a")
    main.pack(fill="both", expand=True)

    # left canvas area
    left = tk.Frame(main, bg="#10131a")
    left.pack(side="left", fill="both", expand=True)

    # canvas
    global canvas
    canvas = tk.Canvas(left, bg="#0b1220", width=720, height=480, highlightthickness=0)
    canvas.pack(padx=10, pady=10, fill="both", expand=True)

    # right side panel
    right = tk.Frame(main, bg="#0d1116", width=350)
    right.pack(side="right", fill="y")

    # top of right panel: dropdown / path buttons (moved up)
    right_top = tk.Frame(right, bg="#0d1116")
    right_top.pack(pady=6)
    tk.Label(right_top, text="Select Target Node:", bg="#0d1116", fg="#7ee3ff").pack()
    target_var = tk.StringVar(value="0")
    target_dropdown = tk.OptionMenu(right_top, target_var, *list(range(NODE_COUNT)))
    target_dropdown.config(bg="#394457", fg="white", width=10)
    target_dropdown.pack(pady=2)
    target_dropdown.config(state="disabled")

    show_path_button = tk.Button(right_top, text="SHOW PATH", width=15, bg="#ffd700", command=on_show_path)
    show_path_button.pack(pady=3)
    show_path_button.config(state="disabled")

    highlight_neighbors_button = tk.Button(right_top, text="HIGHLIGHT NEIGHBORS", width=18, bg="#4cc9ff",
                                           command=on_highlight_neighbors)
    highlight_neighbors_button.pack(pady=3)
    highlight_neighbors_button.config(state="disabled")

    # PQ display
    tk.Label(right, text="Priority Queue", bg="#0d1116", fg="#7ee3ff").pack(pady=4)
    global pq_listbox
    pq_listbox = tk.Listbox(right, bg="#06121a", fg="white", width=26, height=10)
    pq_listbox.pack(padx=8, pady=4)

    # dist[] text widget
    tk.Label(right, text="dist[]", bg="#0d1116", fg="#7ee3ff").pack(pady=4)
    global dist_text
    dist_text = tk.Text(right, bg="#06121a", fg="white", width=26, height=12)
    dist_text.pack(padx=8, pady=4)

    # initialize
    generate_weights()
    for i in range(NODE_COUNT):
        distances[i] = float('inf')
        prev_map[i] = None

    draw_graph_items_once()
    refresh_dist_text_widget()
    refresh_pq()

    root.mainloop()

if __name__ == "__main__":
    build_ui()
