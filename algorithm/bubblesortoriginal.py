import tkinter as tk
import random

# --- Create Main Window ---  
window = tk.Tk()
window.title("Algorithm Visualizer - Bubble Sort")
window.geometry("850x650")
window.config(bg="#0f0f23")

# Global variables
data = []
is_sorting = False
is_paused = False
comparisons = 0
swaps = 0
current_step = None

# --- Header Frame ---
header_frame = tk.Frame(window, bg="#1a1a3e", height=100)
header_frame.pack(fill=tk.X, pady=(0, 15))

title_label = tk.Label(
    header_frame,
    text="🔵 Bubble Sort Visualizer",
    font=("Segoe UI", 24, "bold"),
    bg="#1a1a3e",
    fg="#00d4ff"
)
title_label.pack(side=tk.LEFT, padx=20, pady=20)

# --- Canvas for Drawing Bars ---
canvas_frame = tk.Frame(window, bg="#0f0f23")
canvas_frame.pack(pady=10)

canvas = tk.Canvas(canvas_frame, width=720, height=340, bg="#1a1a2e", highlightthickness=2, highlightbackground="#00d4ff")
canvas.pack()

# --- Stats Frame ---
stats_frame = tk.Frame(window, bg="#0f0f23")
stats_frame.pack(pady=10)

comparisons_label = tk.Label(stats_frame, text="Comparisons: 0", font=("Arial", 11), bg="#0f0f23", fg="#00ff88")
comparisons_label.grid(row=0, column=0, padx=20)

swaps_label = tk.Label(stats_frame, text="Swaps: 0", font=("Arial", 11), bg="#0f0f23", fg="#ff6b9d")
swaps_label.grid(row=0, column=1, padx=20)

# --- Draw Function ---
def draw_array(arr, color_array):
    canvas.delete("all")
    c_height = 340
    c_width = 720
    x_width = c_width / (len(arr) + 1)
    offset = 15
    spacing = 3
    
    if not arr:
        return
    
    normalized_data = [i / max(arr) for i in arr]
    
    for i, height in enumerate(normalized_data):
        x0 = i * x_width + offset + spacing
        y0 = c_height - height * 300
        x1 = (i + 1) * x_width + offset
        y1 = c_height
        
        canvas.create_rectangle(x0, y0, x1, y1, fill=color_array[i], outline="#ffffff", width=1)
    
    window.update_idletasks()

# --- Bubble Sort with Generator ---
def bubble_sort_generator():
    global data, comparisons, swaps
    
    for i in range(len(data) - 1):
        for j in range(len(data) - i - 1):
            # Highlight comparison
            comparisons += 1
            comparisons_label.config(text=f"Comparisons: {comparisons}")
            
            colors = ["#00d4ff" if x < len(data) - i else "#00ff88" for x in range(len(data))]
            colors[j] = "#ff6b9d"
            colors[j + 1] = "#ff6b9d"
            draw_array(data, colors)
            
            yield  # Pause here
            
            if data[j] > data[j + 1]:
                # Swap
                data[j], data[j + 1] = data[j + 1], data[j]
                swaps += 1
                swaps_label.config(text=f"Swaps: {swaps}")
                
                colors[j] = "#ffaa00"
                colors[j + 1] = "#ffaa00"
                draw_array(data, colors)
                
                yield  # Pause here
    
    # Sorted array
    draw_array(data, ["#00ff88" for _ in range(len(data))])

# --- Animation Loop ---
def animate_sort():
    global is_sorting, is_paused, current_step
    
    if is_paused or not is_sorting:
        return
    
    try:
        next(current_step)
        delay = int(speed.get())  # Use speed value directly as milliseconds
        window.after(delay, animate_sort)
    except StopIteration:
        # Sorting complete
        is_sorting = False
        is_paused = False
        start_button.config(state=tk.NORMAL, text="▶️ Start")
        pause_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)
        generate_button.config(state=tk.NORMAL)

# --- Generate Random Array ---
def generate_array():
    global data, comparisons, swaps, is_sorting, is_paused
    if is_sorting:
        return
    
    size = int(size_slider.get())
    data = [random.randint(10, 100) for _ in range(size)]
    comparisons = 0
    swaps = 0
    is_paused = False
    comparisons_label.config(text=f"Comparisons: {comparisons}")
    swaps_label.config(text=f"Swaps: {swaps}")
    draw_array(data, ["#00d0f0" for _ in range(size)])

# --- Start Sorting ---
def start_sort():
    global is_sorting, is_paused, current_step, comparisons, swaps
    
    # If paused, resume
    if is_paused:
        is_paused = False
        start_button.config(state=tk.DISABLED)
        pause_button.config(state=tk.NORMAL)
        animate_sort()
        return
    
    # If already sorting, do nothing
    if is_sorting:
        return
    
    # Start new sort
    is_sorting = True
    is_paused = False
    comparisons = 0
    swaps = 0
    comparisons_label.config(text=f"Comparisons: {comparisons}")
    swaps_label.config(text=f"Swaps: {swaps}")
    
    start_button.config(state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.NORMAL)
    generate_button.config(state=tk.DISABLED)
    
    current_step = bubble_sort_generator()
    animate_sort()

# --- Pause Sorting ---
def pause_sort():
    global is_paused
    if is_sorting and not is_paused:
        is_paused = True
        pause_button.config(state=tk.DISABLED)
        start_button.config(state=tk.NORMAL, text="▶️ Resume")

# --- Stop Sorting ---
def stop_sort():
    global is_sorting, is_paused
    is_sorting = False
    is_paused = False
    
    start_button.config(state=tk.NORMAL, text="▶️ Start")
    pause_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    generate_button.config(state=tk.NORMAL)

# --- Buttons in header (top right) ---
header_button_frame = tk.Frame(header_frame, bg="#1a1a3e")
header_button_frame.pack(side=tk.RIGHT, padx=20, pady=20)

generate_button = tk.Button(
    header_button_frame,
    text="🔄 Generate",
    command=generate_array,
    bg="#00d4ff",
    fg="black",
    font=("Arial", 10, "bold"),
    width=12,
    height=1,
    relief=tk.FLAT,
    cursor="hand2"
)
generate_button.grid(row=0, column=0, padx=4)

start_button = tk.Button(
    header_button_frame,
    text="▶️ Start",
    command=start_sort,
    bg="#00ff88",
    fg="black",
    font=("Arial", 10, "bold"),
    width=12,
    height=1,
    relief=tk.FLAT,
    cursor="hand2"
)
start_button.grid(row=0, column=1, padx=4)

pause_button = tk.Button(
    header_button_frame,
    text="⏸️ Pause",
    command=pause_sort,
    bg="#ffaa00",
    fg="black",
    font=("Arial", 10, "bold"),
    width=12,
    height=1,
    relief=tk.FLAT,
    cursor="hand2",
    state=tk.DISABLED
)
pause_button.grid(row=0, column=2, padx=4)

stop_button = tk.Button(
    header_button_frame,
    text="⏹️ Stop",
    command=stop_sort,
    bg="#ff6b9d",
    fg="black",
    font=("Arial", 10, "bold"),
    width=12,
    height=1,
    relief=tk.FLAT,
    cursor="hand2",
    state=tk.DISABLED
)
stop_button.grid(row=0, column=3, padx=4)

# --- Control Panel Frame ---
control_frame = tk.Frame(window, bg="#1a1a3e", padx=20, pady=15)
control_frame.pack(fill=tk.X, pady=10)

# Speed Control
speed_frame = tk.Frame(control_frame, bg="#1a1a3e")
speed_frame.grid(row=0, column=0, padx=15)

speed_label = tk.Label(speed_frame, text="⚡ Speed (10-500ms)", bg="#1a1a3e", fg="#00d4ff", font=("Arial", 11, "bold"))
speed_label.pack()

speed = tk.DoubleVar()
speed_scale = tk.Scale(
    speed_frame,
    from_=10,
    to=500,
    length=150,
    orient=tk.HORIZONTAL,
    variable=speed,
    bg="#2d2d5e",
    fg="white",
    troughcolor="#0f0f23",
    highlightthickness=0
)
speed_scale.set(100)
speed_scale.pack(pady=5)

# Array Size Control
size_frame = tk.Frame(control_frame, bg="#1a1a3e")
size_frame.grid(row=0, column=1, padx=15)

size_label = tk.Label(size_frame, text="📊 Array Size", bg="#1a1a3e", fg="#00d4ff", font=("Arial", 11, "bold"))
size_label.pack()

size_slider = tk.Scale(
    size_frame,
    from_=10,
    to=60,
    length=150,
    orient=tk.HORIZONTAL,
    bg="#2d2d5e",
    fg="white",
    troughcolor="#0f0f23",
    highlightthickness=0,
    command=lambda x: generate_array() if not is_sorting else None
)
size_slider.set(30)
size_slider.pack(pady=5)

# --- Color Legend ---
legend_frame = tk.Frame(window, bg="#0f0f23")
legend_frame.pack(pady=10)

tk.Label(legend_frame, text="🔵 Unsorted", bg="#0f0f23", fg="#00d4ff", font=("Arial", 9)).grid(row=0, column=0, padx=10)
tk.Label(legend_frame, text="🔴 Comparing", bg="#0f0f23", fg="#ff6b9d", font=("Arial", 9)).grid(row=0, column=1, padx=10)
tk.Label(legend_frame, text="🟠 Swapping", bg="#0f0f23", fg="#ffaa00", font=("Arial", 9)).grid(row=0, column=2, padx=10)
tk.Label(legend_frame, text="🟢 Sorted", bg="#0f0f23", fg="#00ff88", font=("Arial", 9)).grid(row=0, column=3, padx=10)

# --- Initialize ---
generate_array()
window.mainloop()