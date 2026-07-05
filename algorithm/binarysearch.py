import tkinter as tk
import random
import time

# ---------------- GLOBAL VARIABLES ---------------- #

BOX_W = 90
BOX_H = 90
GAP = 20

BG_COLOR = "#003366"     # Dark blue
BUTTON_COLOR = "#ffeb3b"  # Yellow buttons

data = []
steps = []
curr_step = 0
running = False
canvas_y = 80
speed_delay = 0.5

root = None
canvas = None
length_var = None
target_entry = None


# ---------------- UI SETUP ---------------- #

def setup_window():
    global root, canvas

    root = tk.Tk()
    root.title("Binary Search Visualizer — Neon Mode (No Threading)")
    root.configure(bg=BG_COLOR)

    create_ui()

    canvas = tk.Canvas(root, width=1400, height=900, bg="#040756")
    canvas.pack(pady=10)

    root.mainloop()


def create_ui():
    global length_var, target_entry, speed_slider

    ui = tk.Frame(root, bg=BG_COLOR)
    ui.pack(pady=10)

    label_style = {"bg": BG_COLOR, "fg": "white", "font": ("Arial", 12, "bold")}

    tk.Label(ui, text="Array Length:", **label_style).grid(row=0, column=0)

    length_var = tk.StringVar()
    length_var.set("7")
    length_menu = tk.OptionMenu(ui, length_var, *[str(i) for i in range(1, 11)])
    length_menu.config(width=5, font=("Arial", 12))
    length_menu.grid(row=0, column=1, padx=10)

    bstyle = {"bg": BUTTON_COLOR, "font": ("Arial", 12, "bold"), "width": 12, "height": 1}

    tk.Button(ui, text="Generate Array", command=generate_array, **bstyle).grid(row=0, column=2, padx=8)
    tk.Button(ui, text="Start", command=start_search, **bstyle).grid(row=0, column=3, padx=8)
    tk.Button(ui, text="Reset", command=reset_canvas, **bstyle).grid(row=0, column=4, padx=8)

    tk.Label(ui, text="Element:", **label_style).grid(row=0, column=6)
    target_entry = tk.Entry(ui, width=8, font=("Arial", 12))
    target_entry.grid(row=0, column=7, padx=10)

    tk.Label(ui, text="Delay (s):", **label_style).grid(row=0, column=8)
    speed_slider = tk.Scale(
        ui, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
        bg=BG_COLOR, fg="white", font=("Arial", 10),
        command=update_speed
    )
    speed_slider.set(0.5)
    speed_slider.grid(row=0, column=9, padx=10)


# ---------------- CONTROL FUNCTIONS ---------------- #

def update_speed(val):
    global speed_delay
    speed_delay = float(val)


def reset_canvas():
    global steps, curr_step, canvas_y, running
    running = False
    canvas.delete("all")
    steps = []
    curr_step = 0
    canvas_y = 80


# ---------------- ARRAY & DRAW ---------------- #

def generate_array():
    global data

    reset_canvas()
    size = int(length_var.get())
    data = sorted(random.sample(range(10, 100), size))
    draw_initial()


def draw_initial():
    global canvas_y
    canvas.delete("all")
    canvas_y = 80
    mid = (len(data) - 1) // 2
    draw_segment(0, len(data) - 1, mid)


# Clean square box (equal size)
def draw_box(x, y):
    """Draw a clean equal-sized white box."""
    canvas.create_rectangle(
        x, y,
        x + BOX_W, y + BOX_H,
        outline="white", width=4, fill="white"
    )


# ★ Neon expanding rings effect ★
def draw_green_oval(cx, cy):
    """Simple clean oval highlight around the mid element."""
    r = 40   # size of oval highlight

    canvas.create_oval(
        cx - r, cy - r,
        cx + r, cy + r,
        outline="yellow",fill="orange",
        width=6
    )



# ---------------- BINARY SEARCH LOGIC ---------------- #

def start_search():
    global running, steps, curr_step, canvas_y

    if not data:
        return

    try:
        int(target_entry.get())
    except:
        return

    canvas.delete("all")
    canvas_y = 80
    curr_step = 0
    running = True
    steps = []

    compute_steps()
    auto_mode()


def compute_steps():
    global steps

    target = int(target_entry.get())
    steps.clear()

    l, r = 0, len(data) - 1

    while l <= r:
        m = (l + r) // 2
        steps.append((l, r, m))

        if data[m] == target:
            break
        elif data[m] < target:
            l = m + 1
        else:
            r = m - 1


def auto_mode():
    global curr_step, running

    if not running:
        return

    if curr_step < len(steps):
        show_step()
        root.after(int(speed_delay * 1000), auto_mode)
    else:
        end_message()


def end_message():
    _, _, m = steps[-1]
    target = int(target_entry.get())

    if data[m] == target:
        msg = f"✔ Element {target} found at index {m}"
        color = "yellow"
    else:
        msg = f"✘ Element {target} not found"
        color = "red"

    canvas.create_text(
        500, canvas_y + 20,
        text=msg,
        font=("Arial", 22, "bold"),
        fill=color
    )


# ---------------- VISUALIZATION ---------------- #

def show_step():
    global curr_step

    l, r, m = steps[curr_step]
    target = int(target_entry.get())

    if target > data[m]:
        compare = f"{target} > {data[m]} — check right"
    elif target < data[m]:
        compare = f"{target} < {data[m]} — check left"
    else:
        compare = f"found {data[m]}"

    draw_segment(l, r, m, compare)
    curr_step += 1


def draw_segment(l, r, m, compare_text=None):
    global canvas_y

    x = 40
    y = canvas_y

    # Draw row boxes
    for i in range(l, r + 1):
        num_x = x + BOX_W / 2
        num_y = y + BOX_H / 2

        if i == m:
            draw_green_oval(num_x, num_y)
            canvas.create_text(num_x, num_y, text=str(data[i]),
                               fill="black", font=("Arial", 20, "bold"))
        else:
            draw_box(x, y)
            canvas.create_text(num_x, num_y, text=str(data[i]),
                               fill="black", font=("Arial", 18))

        x += BOX_W + GAP

    # Mid arrow + text
    mid_x = 40 + (m - l) * (BOX_W + GAP) + BOX_W / 2
    canvas.create_text(mid_x, y - 20, text="↓", font=("Arial", 22), fill="white")
    canvas.create_text(mid_x, y + BOX_H + 25, text="mid", font=("Arial", 14), fill="white")

    # Comparison text
    if compare_text:
        canvas.create_text(350, y + BOX_H + 50,
                           text=compare_text, font=("Arial", 16), fill="white")

    canvas_y += 160


# ---------------- START PROGRAM ---------------- #

setup_window()
