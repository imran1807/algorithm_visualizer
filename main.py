import tkinter as tk
import subprocess
import os
#  Neon Button Class
class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=200, height=55,
                 bg_color="#0a0a0f", neon_color="#0ff", **kwargs):

        super().__init__(parent, width=width, height=height, bg=bg_color,
                         highlightthickness=0, bd=0)

        self.command = command
        self.text = text
        self.neon_color = neon_color

        # Rounded rectangle
        self.rect = self.create_round_rect(5, 5, width-5, height-5, 18,
                                           outline=neon_color, width=2)

        #  text
        self.label = self.create_text(width/2, height/2, text=text,
                                      fill=neon_color,
                                      font=("Orbitron", 13, "bold"))

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_click(self, e):
        if self.command:
            self.command()

    def on_hover(self, e):
        self.itemconfig(self.rect, outline="cyan", width=4)
        self.itemconfig(self.label, fill="cyan")

    def on_leave(self, e):
        self.itemconfig(self.rect, outline=self.neon_color, width=2)
        self.itemconfig(self.label, fill=self.neon_color)

#  Main Launcher (3x3 MATRIX)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Your EXACT files from your folder:
ALGO_FILES = [
    ("Binary Search", "binarysearch.py"),
    ("Binary Tree Traversal", "bt_transversal.py"),
    ("Bubble Sort", "bubblesortoriginal.py"),
    ("DFS + BFS", "dfs+bfs.py"),
    ("Dijkstra", "dijkestra.py"),
    ("Linear Search", "LINEAR.py"),
    ("Merge Sort", "mergesearch.py"),
    ("Selection Sort", "selection_sort.py"),
    ("quicksort", "tracker.py")  # extra slot to complete 3×3
]

def run_file(filename):
    if filename:
        subprocess.Popen(["python", os.path.join(BASE_DIR, filename)])


root = tk.Tk()
root.title("Algorithm Visualizer - Neon Edition")
root.geometry("750x750")
root.configure(bg="#05050a")
root.resizable(True, True)

# Title
tk.Label(root,
         text="ALGORITHM VISUALIZER",
         font=("Orbitron", 24, "bold"),
         fg="#0ff",
         bg="#05050a"
         ).pack(pady=20)

# Create a frame for the 3×3 grid
grid_frame = tk.Frame(root, bg="#05050a")
grid_frame.pack(expand=True)

# Configure 3 rows & 3 columns to expand evenly
for i in range(3):
    grid_frame.grid_columnconfigure(i, weight=1)
    grid_frame.grid_rowconfigure(i, weight=1)

# Place neon buttons in 3×3 positions
index = 0
for r in range(3):
    for c in range(3):
        text, file = ALGO_FILES[index]
        btn = NeonButton(
            grid_frame,
            text=text,
            command=(lambda f=file: run_file(f)),
            width=200,
            height=60
        )
        btn.grid(row=r, column=c, padx=20, pady=20)
        index += 1

# Footer
tk.Label(root,
         text="for better understanding ",
         font=("Orbitron", 12),
         fg="#088",
         bg="#05050a"
         ).pack(pady=15)

root.mainloop()
