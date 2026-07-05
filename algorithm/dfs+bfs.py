import tkinter as tk
import random
from collections import deque

graph = {}
pos = {}
node_ids = {}
edge_ids = {}
steps = []
start_node = None
step_index = 0
visited_order = []
mode = "DFS"   # current mode = DFS or BFS


# SIMPLE RANDOM GRAPH (TREE)

def generate_graph(n):
    global graph
    graph = {i: [] for i in range(n)}

    for i in range(1, n):
        parent = random.randint(max(0, i - 3), i - 1)
        graph[parent].append(i)
        graph[i].append(parent)

    for u in graph:
        graph[u] = sorted(graph[u])

# AUTO RESIZE + CENTER THE GRAP

def scale_and_center():
    xs = [pos[n][0] for n in pos]
    ys = [pos[n][1] for n in pos]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    graph_w = max_x - min_x
    graph_h = max_y - min_y

    CANVAS_W = 600
    CANVAS_H = 550

    pad = 50
    scale_x = (CANVAS_W - pad) / graph_w if graph_w else 1
    scale_y = (CANVAS_H - pad) / graph_h if graph_h else 1
    scale = min(scale_x, scale_y)

    # scale positions
    for n in pos:
        x, y = pos[n]
        pos[n] = ((x - min_x) * scale, (y - min_y) * scale)

    # recalc bounding
    xs = [pos[n][0] for n in pos]
    ys = [pos[n][1] for n in pos]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    graph_w = max_x - min_x
    graph_h = max_y - min_y

    shift_x = (CANVAS_W - graph_w) / 2 - min_x
    shift_y = (CANVAS_H - graph_h) / 2 - min_y

    for n in pos:
        x, y = pos[n]
        pos[n] = (x + shift_x, y + shift_y)


# BFS LAYOUT (LEVEL BASED)
def generate_positions():
    global pos
    pos = {} # empty dictionary to store position

    q = deque([(0, 0)])
    visited = {0}  #set to store visited nodes
    levels = {0: [0]} # level dictionary to store level with its nodes

    while q:
        node, lvl = q.popleft()
        for nb in graph[node]:
            if nb not in visited:
                visited.add(nb)
                levels.setdefault(lvl + 1, []).append(nb)
                q.append((nb, lvl + 1))

    y_step = 120
    x_step = 120

    for lvl, nodes in levels.items():
        for i, nd in enumerate(nodes): # index and node value
            pos[nd] = (i * x_step, lvl * y_step)

    scale_and_center()


# --------------------------------------------------------
# DRAW GRAPH
# --------------------------------------------------------
def draw_graph():
    canvas.delete("all")
    node_ids.clear()
    edge_ids.clear()

    for u in graph:
        for v in graph[u]:
            if u < v: # to avoid duplication of  edge drawn as graph is undirected
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                edge_ids[(u, v)] = canvas.create_line(x1, y1, x2, y2, width=2)

    for nd, (x, y) in pos.items():
        r = 20
        node_ids[nd] = canvas.create_oval(x-r, y-r, x+r, y+r, fill="#F4DCA4")
        canvas.create_text(x, y, text=str(nd),font=("Arial",16,"bold"))


# --------------------------------------------------------
# BUILD DFS STEPS
# --------------------------------------------------------
def build_dfs_steps(start):
    global steps
    steps = []
    visited = set()

    stack = [(start, 0)]
    visited.add(start)
    steps.append(("visit", start))

    while stack:
        node, idx = stack[-1]

        if idx >= len(graph[node]):
            steps.append(("back", node))
            stack.pop()
            continue

        nb = graph[node][idx]
        stack[-1] = (node, idx + 1)

        if nb not in visited:
            visited.add(nb)
            steps.append(("edge", node, nb))
            steps.append(("visit", nb))
            stack.append((nb, 0))


# --------------------------------------------------------
# BUILD BFS STEPS
# --------------------------------------------------------
def build_bfs_steps(start):
    global steps
    steps = []
    visited = {start}

    q = deque([start])
    steps.append(("visit", start))

    while q:
        node = q.popleft()

        for nb in graph[node]:
            if nb not in visited:
                visited.add(nb)
                steps.append(("edge", node, nb))
                steps.append(("visit", nb))
                q.append(nb)


# --------------------------------------------------------
# RUN ONE STEP (DFS / BFS)
# --------------------------------------------------------
def next_step():
    global step_index, visited_order

    if start_node is None:
        status_label.config(text="Select a start node")
        return

    if step_index >= len(steps):
        status_label.config(text=f"{mode} Completed")
        return

    action = steps[step_index]
    step_index += 1

    if action[0] == "visit":
        n = action[1]
        canvas.itemconfig(node_ids[n], fill="yellow")
        visited_order.append(n)

    if action[0] == "edge":
        u, v = action[1], action[2]
        key = (u, v) if u < v else (v, u)
        canvas.itemconfig(edge_ids[key], fill="red", width=3)

    if action[0] == "back":
        canvas.itemconfig(node_ids[action[1]], fill="lightgreen")

    order_label.config(text=f"{mode} Order: {visited_order}")
    stack_label.config(text=f"Steps Left: {len(steps) - step_index}")


# --------------------------------------------------------
# CLICK TO SELECT START
# --------------------------------------------------------
def select_start(event):
    global start_node, step_index, visited_order

    for nd in node_ids:
        x, y = pos[nd]
        if (event.x - x)**2 + (event.y - y)**2 <= 20**2:

            start_node = nd
            step_index = 0
            visited_order = []

            draw_graph()
            canvas.itemconfig(node_ids[nd], fill="lightblue")

            # build steps based on mode
            if mode == "DFS":
                build_dfs_steps(nd)
            else:
                build_bfs_steps(nd)

            status_label.config(text=f"Start = {nd} ({mode})")
            order_label.config(text=f"{mode} Order: []")
            stack_label.config(text=f"Steps Left: {len(steps)}")
            return


# --------------------------------------------------------
# GENERATE NEW GRAPH
# --------------------------------------------------------
def generate_action():
    global start_node, step_index, visited_order

    n = int(node_entry.get())

    generate_graph(n)
    generate_positions()
    draw_graph()

    start_node = None
    step_index = 0
    visited_order = []

    status_label.config(text="Click a node to start")
    order_label.config(text=f"{mode} Order: []")
    stack_label.config(text="Steps Left: --")


# --------------------------------------------------------
# SET MODE DFS
# --------------------------------------------------------
def set_dfs():
    global mode
    mode = "DFS"
    status_label.config(text="Mode set to DFS")


# --------------------------------------------------------
# SET MODE BFS
# --------------------------------------------------------
def set_bfs():
    global mode
    mode = "BFS"
    status_label.config(text="Mode set to BFS")


# --------------------------------------------------------
# RESET ONLY TRAVERSAL
# --------------------------------------------------------
def reset_action():
    global step_index, visited_order
    if start_node is None:
        return

    draw_graph()
    canvas.itemconfig(node_ids[start_node], fill="lightblue")

    if mode == "DFS":
        build_dfs_steps(start_node)
    else:
        build_bfs_steps(start_node)

    step_index = 0
    visited_order = []

    order_label.config(text=f"{mode} Order: []")
    stack_label.config(text=f"Steps Left: {len(steps)}")
    status_label.config(text="Reset complete")


# --------------------------------------------------------
# GUI
# --------------------------------------------------------
window = tk.Tk()
window.title("DFS + BFS Visualizer (Simple + Auto Resize)")
window.config(bg="#C4C4F1")
canvas = tk.Canvas(window, width=600, height=550,bg="#E0B9B6")
canvas.pack(pady=10)
canvas.bind("<Button-1>", select_start)

panel = tk.Frame(window,bg="#C4C4F1")
panel.pack()

tk.Label(panel, text="Nodes:", font=("Arial", 14)).grid(row=0, column=0)
node_entry = tk.Entry(panel, width=8, font=("Arial", 14))
node_entry.grid(row=0, column=1)
node_entry.insert(0, "6")

btn_font = ("Arial", 12, "bold")

tk.Button(panel, text="Generate", width=12, height=2,
          font=btn_font, command=generate_action).grid(row=0, column=2, padx=10)

tk.Button(panel, text="DFS Mode", width=12, height=2,
          font=btn_font, bg="purple", fg="white",
          command=set_dfs).grid(row=0, column=3, padx=10)

tk.Button(panel, text="BFS Mode", width=12, height=2,
          font=btn_font, bg="orange", fg="white",
          command=set_bfs).grid(row=0, column=4, padx=10)

tk.Button(panel, text="Next Step", width=12, height=2,
          font=btn_font, bg="green", fg="white",
          command=next_step).grid(row=0, column=5, padx=10)

tk.Button(panel, text="Reset", width=12, height=2,
          font=btn_font, command=reset_action).grid(row=0, column=6, padx=10)

order_label = tk.Label(window, text="DFS/BFS Order:", font=("Arial", 14),bg="#C4C4F1")
order_label.pack()

stack_label = tk.Label(window, text="Steps Left:", font=("Arial", 14),bg="#C4C4F1")
stack_label.pack()

status_label = tk.Label(window, text="", font=("Arial", 14), fg="blue",bg="#C4C4F1")
status_label.pack(pady=10)

generate_action()
window.mainloop()
