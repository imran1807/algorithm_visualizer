import tkinter as tk
import random

# -------------------- GLOBALS --------------------
data = []
original_array = []      
current_min_node = None

i = 0
j = 1
min_idx = 0
stage = "select_min"
array_size = 5

CELL_W = 100
CELL_H = 100


# -------------------- DRAW ARRAY --------------------
def draw_array(message=""):
    canvas.delete("all")

    for idx, val in enumerate(data):
        x0 = 50 + idx * CELL_W
        y0 = 80
        x1 = x0 + CELL_W
        y1 = y0 + CELL_H

        if idx == i:
            color = "yellow"
        elif idx == j:
            color = "red"
        elif idx == min_idx:
            color = "orange"
        elif idx < i:
            color = "lightgreen"
        else:
            color = "white"

        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")
        canvas.create_text((x0+x1)//2, (y0+y1)//2, text=str(val),
                           font=("Arial", 18, "bold"))
        canvas.create_text((x0+x1)//2, y1+20, text=str(idx),
                           font=("Arial", 12, "bold"), fill="white")

    draw_arrows()
    draw_minimum_nodes()
    status.config(text=message)


# -------------------- DRAW ARROWS --------------------
def draw_arrows():
    x_i = 50 + i * CELL_W + CELL_W // 2
    canvas.create_text(x_i, 50, text="i", font=("Arial", 16, "bold"), fill="blue")
    canvas.create_line(x_i, 60, x_i, 80, arrow=tk.LAST, width=3, fill="blue")

    if j < len(data):
        x_j = 50 + j * CELL_W + CELL_W // 2
        canvas.create_text(x_j, 30, text="j", font=("Arial", 16, "bold"), fill="green")
        canvas.create_line(x_j, 50, x_j, 80, arrow=tk.LAST, width=3, fill="red")

    x_m = 50 + min_idx * CELL_W + CELL_W // 2
    canvas.create_text(x_m, 260, text="min", font=("Arial", 16, "bold"), fill="orange")
    canvas.create_line(x_m, 250, x_m, 220, arrow=tk.LAST, width=3, fill="orange")


# -------------------- DRAW CURRENT MINIMUM --------------------
def draw_minimum_nodes():
    min_canvas.delete("all")
    text = f"Current Minimum Node:  {current_min_node}"
    min_canvas.create_text(10, 20, text=text, anchor="w",
                           fill="white", font=("Arial", 16, "bold"))


# ---------------- FINAL DISPLAY --------------------
def draw_final():
    canvas.delete("all")

    for k in range(len(data)):
        x0 = 50 + k * CELL_W
        y0 = 80
        x1 = x0 + CELL_W
        y1 = y0 + CELL_H

        canvas.create_rectangle(x0, y0, x1, y1, fill="lightgreen", outline="black")
        canvas.create_text((x0+x1)//2, (y0+y1)//2, text=str(data[k]),
                           font=("Arial", 18, "bold"))
        canvas.create_text((x0+x1)//2, y1+20, text=str(k),
                           font=("Arial", 12, "bold"), fill="white")

    status.config(text="Sorting Completed!")
    draw_minimum_nodes()


# ---------------- STEP LOGIC --------------------
def next_step():
    global i, j, min_idx, stage, data, current_min_node

    n = len(data)

    # ---- FINAL ----
    if i >= n - 1:
        draw_final()
        return

    # ---- SELECT MIN ----
    if stage == "select_min":
        draw_array(f"Comparing data[{j}] with data[{min_idx}]")

        # Update minimum immediately
        if data[j] < data[min_idx]:
            min_idx = j
            current_min_node = data[min_idx]
            draw_array(f"New minimum found at index {min_idx}")
            draw_minimum_nodes()

        j += 1

        if j == n:
            stage = "swap"
        return

    # ---- SWAP ----
    if stage == "swap":
        data[i], data[min_idx] = data[min_idx], data[i]
        draw_array(f"Swapping index {i} and {min_idx}")

        i += 1
        min_idx = i
        j = i + 1
        stage = "select_min"

        draw_array(f"Moving to next index i = {i}")


# ---------------- RESET TO ORIGINAL ARRAY --------------------
def reset_step():
    global data, i, j, min_idx, stage, current_min_node

    data = original_array.copy()     # ⭐ Restore original array
    i = 0
    j = 1
    min_idx = 0
    stage = "select_min"
    current_min_node = None

    draw_array("Reset to original array.")
    draw_minimum_nodes()


# ---------------- GENERATE ARRAY --------------------
def generate_array():
    global data, original_array
    global i, j, min_idx, stage, current_min_node

    data = random.sample(range(5, 60), array_size)
    original_array = data.copy()     # ⭐ Save original array

    i = 0
    min_idx = 0
    j = 1
    stage = "select_min"
    current_min_node = None

    draw_array("New array generated. Press NEXT to start.")
    draw_minimum_nodes()


# -------------------- UI SETUP --------------------
root = tk.Tk()
root.configure(bg="#050545")
root.title("Selection Sort – Array + Arrows + Step-by-Step")
root.geometry("1400x800")

canvas = tk.Canvas(root, width=1200, height=350, bg="#101947",highlightthickness=.5)
canvas.pack(pady=40, padx=20)

min_canvas = tk.Canvas(root, width=1200, height=60, bg="#050545", highlightthickness=0)
min_canvas.pack()

status = tk.Label(root, text="", font=("Arial", 16), bg="#050545", fg="white")
status.pack()

btn_frame = tk.Frame(root, bg="#050545")
btn_frame.pack(pady=20)

# ---- Array Size ----
size_label = tk.Label(btn_frame, text="Array Size", font=("Arial", 12, "bold"),
                      width=15, height=3, bg="white", fg="black",
                      relief="ridge", bd=3)
size_label.grid(row=0, column=0, padx=8, pady=5)

size_var = tk.StringVar()
size_var.set("5")

size_menu = tk.OptionMenu(btn_frame, size_var,
                          "5", "6", "7", "8", "9", "10")
size_menu.config(width=15, height=3, font=("Arial", 12),
                 bg="white", fg="black", relief="ridge", bd=3)
size_menu.grid(row=0, column=1, padx=8, pady=5)


def update_size():
    global array_size
    array_size = int(size_var.get())
    generate_array()


tk.Button(btn_frame, text="Generate Array", width=15, height=3,
          font=("Arial", 12), command=update_size,
          bg="#DFDF0F", border=4).grid(row=0, column=2, padx=15)

tk.Button(btn_frame, text="Next Step →", width=15, height=3,
          font=("Arial", 12), command=next_step,
          bg="#ED1919", border=4).grid(row=0, column=3, padx=15)

tk.Button(btn_frame, text="Reset Step", width=15, height=3,
          font=("Arial", 12), command=reset_step,
          bg="#1F7896", border=4).grid(row=0, column=4, padx=15)

generate_array()
root.mainloop()
