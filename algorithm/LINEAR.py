import tkinter as tk
import random

# ---------------- GLOBAL VARIABLES ----------------
arr = []
key = None
current_index = 0
running = False
pointer = None
box_positions = []

# UI will be initialized later
root = tk.Tk()
root.title("Linear Search — Neon Visualizer (Functions Version)")
root.geometry("1200x700")
root.config(bg="#0d0d17")


# ---------------- HELPER FUNCTION ----------------
def neon_glow(x, y, color, rings=6):
    """Creates glowing effect around a box."""
    for i in range(rings, 0, -1):
        canvas.create_oval(
            x - 40 - i * 6, y - 30 - i * 4,
            x + 40 + i * 6, y + 30 + i * 4,
            outline="#00eaff"

        )


# ---------------- ACTION FUNCTIONS ----------------
def generate_array():
    """Generate random array and update input field."""
    global arr
    arr = [random.randint(1, 50) for _ in range(random.randint(5, 10))]
    entry_arr.delete(0, tk.END)
    entry_arr.insert(0, " ".join(map(str, arr)))
    status.config(text="Generated random array")


def draw_array():
    """Draws array with neon style boxes."""
    global box_positions, pointer

    canvas.delete("all")
    box_positions = []

    if not arr:
        return

    start_x = 80
    gap = 120

    for i, val in enumerate(arr):
        x = start_x + i * gap
        y = 160

        canvas.create_oval(x - 60, y - 50, x + 60, y + 50, fill="#002233", outline="")
        canvas.create_rectangle(x - 40, y - 30, x + 40, y + 30,
                                fill="#1f1f2e", outline="#00eaff", width=3)
        canvas.create_text(x, y, text=str(val), fill="#00eaff",
                           font=("Segoe UI", 16, "bold"))

        box_positions.append((x, y))

    if box_positions:
        px, _ = box_positions[0]

        if pointer is None:
            set_pointer(px)
        else:
            canvas.coords(pointer, px, 240)


def set_pointer(x):
    """Create pointer arrow."""
    global pointer
    pointer = canvas.create_text(x, 240, text="⬆",
                                 fill="#ff9f43", font=("Segoe UI", 28, "bold"))


def start_search():
    """Starts linear search animation."""
    global arr, key, current_index, running

    try:
        arr[:] = list(map(int, entry_arr.get().strip().split()))
    except:
        status.config(text="Invalid array")
        return

    try:
        key = int(entry_key.get().strip())
    except:
        status.config(text="Invalid key")
        return

    if len(arr) == 0:
        status.config(text="Array is empty")
        return

    current_index = 0
    running = True
    draw_array()
    status.config(text="Searching...")
    root.after(200, animate_step)


def stop_search():
    """Pause animation."""
    global running
    running = False
    status.config(text="Paused")


def animate_step():
    """Search animation frame."""
    global current_index, running

    if not running:
        return

    if current_index >= len(arr):
        status.config(text="❌ Not Found")
        running = False
        return

    x, y = box_positions[current_index]
    value = arr[current_index]

    draw_array()
    canvas.coords(pointer, x, 240)

    canvas.create_rectangle(x - 40, y - 30, x + 40, y + 30,
                            fill="#ffee88", outline="#000", width=2)
    canvas.create_text(x, y, text=str(value), fill="black",
                       font=("Segoe UI", 16, "bold"))

    if value == key:
        canvas.create_rectangle(x - 40, y - 30, x + 40, y + 30,
                                fill="#00ff7f", outline="#fff", width=3)
        canvas.create_text(x, y, text=str(value), fill="black",
                           font=("Segoe UI", 16, "bold"))
        neon_glow(x, y, "#d8f809")
        status.config(text=f"✔ Found at index {current_index}")
        running = False
        return

    current_index += 1
    root.after(int(700 * speed.get()), animate_step)


# --------------- UI DESIGN ----------------
title = tk.Label(root, text="✨ Linear Search ✨",
                 fg="#00f2ff", bg="#0d0d17", font=("Segoe UI", 24, "bold"))
title.pack(pady=10)

control = tk.Frame(root, bg="#0d0d17")
control.pack()

tk.Button(control, text="Generate", bg="#ff9f43", fg="black",
          font=("Segoe UI", 11, "bold"),
          command=generate_array).grid(row=0, column=0, padx=5)

entry_arr = tk.Entry(control, font=("Segoe UI", 14), width=30,
                     bg="#1b1b2f", fg="#00eaff", insertbackground="#00eaff")
entry_arr.grid(row=0, column=1)
entry_arr.insert(0, "4 7 2 9 1 6")

tk.Label(control, text="Key:", fg="#00eaff", bg="#0d0d17",
         font=("Segoe UI", 13, "bold")).grid(row=0, column=2)
entry_key = tk.Entry(control, font=("Segoe UI", 14), width=8,
                     bg="#1b1b2f", fg="#00eaff", insertbackground="#00eaff")
entry_key.grid(row=0, column=3)
entry_key.insert(0, "9")

tk.Button(control, text="Start", bg="#00ff7f", width=10,
          font=("Segoe UI", 12, "bold"),
          command=start_search).grid(row=0, column=4, padx=5)

tk.Button(control, text="Stop", bg="#ff4d4d", fg="white",
          font=("Segoe UI", 12, "bold"), width=10,
          command=stop_search).grid(row=0, column=5)

tk.Label(control, text="Speed:", fg="#00eaff", bg="#0d0d17",
         font=("Segoe UI", 12, "bold")).grid(row=1, column=0)

speed = tk.DoubleVar(value=0.5)
tk.Scale(control, from_=0.1, to=1.5, resolution=0.1,
         orient="horizontal", variable=speed,
         length=250, bg="#0d0d17", fg="#00eaff",
         troughcolor="#14213d", highlightthickness=0).grid(row=1, column=1, columnspan=3)

canvas = tk.Canvas(root, width=1100, height=450,
                   bg="#0b0b17", highlightthickness=0)
canvas.pack(pady=20)

status = tk.Label(root, text="Ready", fg="#00eaff", bg="#0d0d17",
                  font=("Segoe UI", 13, "bold"))
status.pack()

root.mainloop()
