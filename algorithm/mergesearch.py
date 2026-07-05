import tkinter as tk
import random

# ---------------- GLOBAL STATE ----------------
CW = 1100
CH = 650
SPACING_Y = 85
COL_LEFT = "#ff9f43"
COL_RIGHT = "#8e44ad"
COL_MERGE = "#2ecc71"
COL_ROOT = "#00eaff"

arr = []
layout = {}
nodes = {}
merge_steps = []
merge_index = 0

running = False       # For animation
paused = False        # For pause/resume
root = canvas = None
entry = None
status_label = None
speed_var = None


# ----------------------------------------------------------
def generate_array():
    """Generate random array into the entry box"""
    data = [random.randint(1, 99) for _ in range(random.randint(6, 10))]
    entry.delete(0, tk.END)
    entry.insert(0, " ".join(map(str, data)))


# ----------------------------------------------------------
def clear_canvas():
    canvas.delete("all")
    nodes.clear()


# ----------------------------------------------------------
def compute_layout(arr):
    """Compute x,y positions for each node in the tree"""
    n = len(arr)
    layout = {}

    start = 80
    gap = (CW - 160) // (n - 1 if n > 1 else 1)

    leaf_x = [start + i * gap for i in range(n)]

    def place(l, r, depth):
        if l == r:
            layout[(l, r)] = (leaf_x[l], 60 + depth * SPACING_Y)
            return

        mid = (l + r) // 2
        place(l, mid, depth + 1)
        place(mid + 1, r, depth + 1)

        lx, _ = layout[(l, l)]
        rx, _ = layout[(r, r)]
        layout[(l, r)] = ((lx + rx) // 2, 60 + depth * SPACING_Y)

    place(0, n - 1, 0)
    return layout


# ----------------------------------------------------------
def draw_node(x, y, text, color):
    canvas.create_rectangle(
        x - 70, y - 32, x + 70, y + 32,
        fill=color, outline="white"
    )
    canvas.create_text(x, y, text=text,
                       fill="black", font=("Segoe UI", 10, "bold"))


def draw_arrow(x1, y1, x2, y2):
    canvas.create_line(
        x1, y1, x2, y2,
        fill="white", width=2, arrow=tk.LAST
    )


# ----------------------------------------------------------
def build_split_tree(l, r):
    """Draw split stage (entire tree)"""
    x, y = layout[(l, r)]
    seg = arr[l:r + 1]
    txt = "[" + " ".join(map(str, seg)) + "]"

    if (l, r) == (0, len(arr) - 1):
        color = COL_ROOT
    else:
        mid = (l + r) // 2
        color = COL_LEFT if r <= mid else COL_RIGHT
        
    draw_node(x, y, txt, color)
    nodes[(l, r)] = (x, y)
    if l == r:
        return

    mid = (l + r) // 2
    build_split_tree(l, mid)
    build_split_tree(mid + 1, r)

    lx, ly = nodes[(l, mid)]
    rx, ry = nodes[(mid + 1, r)]

    draw_arrow(x+10, y+10, lx-10, ly-10)
    draw_arrow(x+10, y+10, rx-10, ry-10)


# ----------------------------------------------------------
def build_merge_steps(l, r):
    """Record merge steps bottom-up"""
    global merge_steps

    if l == r:
        return [arr[l]]

    mid = (l + r) // 2
    left = build_merge_steps(l, mid)
    right = build_merge_steps(mid + 1, r)

    merged = sorted(left + right)
    merge_steps.append((l, r, merged))

    return merged


# ----------------------------------------------------------
def merge_step():
    """Single merge animation step"""
    global merge_index, running, paused

    if not running or paused:
        return

    if merge_index >= len(merge_steps):
        status_label.config(text="✔ Merge complete!")
        return

    l, r, merged = merge_steps[merge_index]
    x, y = layout[(l, r)]
    txt = "[" + " ".join(map(str, merged)) + "]"

    draw_node(x, y, txt, COL_MERGE)

    status_label.config(text=f"Merging segment {l}-{r}")
    merge_index += 1

    delay = int(600 * speed_var.get())
    root.after(delay, merge_step)


# ----------------------------------------------------------
def start_merge():
    """Start auto merge animation"""
    global running, paused

    running = True
    paused = False
    status_label.config(text="▶ Merge running...")
    merge_step()


def pause_merge():
    """Pause the merge animation"""
    global paused
    paused = True
    status_label.config(text="⏸ Paused")


def resume_merge():
    """Resume the merge animation"""
    global paused
    paused = False
    status_label.config(text="▶ Resumed")
    merge_step()


def stop_merge():
    """Completely stop merge animation"""
    global running, paused
    running = False
    paused = False
    status_label.config(text="⏹ Stopped")


# ----------------------------------------------------------
def split_tree_start():
    """Build static split tree + generate merge list"""
    global arr, layout, merge_steps, merge_index

    clear_canvas()

    try:
        arr = list(map(int, entry.get().split()))
    except:
        status_label.config(text="❌ Invalid input")
        return

    if len(arr) > 10:
        status_label.config(text="⚠ Max 10 elements allowed")
        return

    layout = compute_layout(arr)
    status_label.config(text="Building split tree...")

    build_split_tree(0, len(arr) - 1)

    merge_steps.clear()
    merge_index = 0
    build_merge_steps(0, len(arr) - 1)

    status_label.config(text="Split complete. Press Start Merge.")

# ----------------- UI SETUP -------------------------------
root = tk.Tk()
root.title("Merge Sort")
root.geometry("1200x850")
root.config(bg="#121216")

title = tk.Label(root, text="🌳 Merge Sort",
                 fg="#ffd8a6", bg="#121216",
                 font=("Segoe UI", 20, "bold"))
title.pack(pady=10)

ctrl = tk.Frame(root, bg="#121216")
ctrl.pack()

# Buttons
tk.Button(ctrl, text="Generate Array", bg="#ff9f43",
          command=generate_array).grid(row=0, column=0, padx=5)

entry = tk.Entry(ctrl, font=("Segoe UI", 14), width=35)
entry.grid(row=0, column=1, padx=10)

tk.Button(ctrl, text="Split Tree", bg="#00eaff",
          command=split_tree_start).grid(row=0, column=2, padx=5)

tk.Button(ctrl, text="Start", bg="#4aff4a",
          command=start_merge).grid(row=0, column=3, padx=5)

tk.Button(ctrl, text="Pause", bg="#ffaa00",
          command=pause_merge).grid(row=0, column=4, padx=5)

tk.Button(ctrl, text="Resume", bg="#2980b9", fg="white",
          command=resume_merge).grid(row=0, column=5, padx=5)

tk.Button(ctrl, text="Stop", bg="#ff4d4d", fg="white",
          command=stop_merge).grid(row=0, column=6, padx=5)

# Speed Slider
tk.Label(ctrl, text="Speed:", fg="white", bg="#121216").grid(row=1, column=0)
speed_var = tk.DoubleVar(value=0.5)
tk.Scale(ctrl, from_=0.1, to=1.5, resolution=0.1,
         orient="horizontal", variable=speed_var,
         length=350, bg="#121216", fg="white").grid(row=1, column=1, columnspan=5)

# Canvas
canvas = tk.Canvas(root, width=CW, height=CH, bg="#0b0b10")
canvas.pack(pady=10)

status_label = tk.Label(root, text="Ready", fg="white", bg="#121216")
status_label.pack()

root.mainloop()
