import tkinter as tk
import random

# -------------------------------
# Tree data structure
# -------------------------------
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

# -------------------------------
# Visualizer (layout fixed: PanedWindow)
# -------------------------------
class TreeTraversalVisualizer:
    def __init__(self, root):
        self.root = root
        root.title("Binary Tree Traversal Visualizer — Stack + Pointers (Fixed Layout)")

        # FINAL FIXED WINDOW SIZE
        root.geometry("1650x900")
        root.minsize(1200, 700)
        root.config(bg="#0d0d17")

        # state
        self.tree_root = None
        self.positions = {}   # node -> (x, y)
        self.node_ids = {}
        self.text_ids = {}
        self.edge_ids = {}

        # action list for animation (tuples: ("push"/"visit"/"pop", node))
        self.actions = []
        self.action_index = 0
        self.running = False

        # ---------------- Top Title ----------------
        title = tk.Label(root, text="🌳 Binary Tree Traversal Visualizer",
                         fg="#00eaff", bg="#0d0d17", font=("Segoe UI", 26, "bold"))
        title.pack(pady=8)

        # Controls frame (keeps small height)
        ctrl = tk.Frame(root, bg="#0d0d17")
        ctrl.pack(fill="x", padx=8)

        tk.Button(ctrl, text="Generate Tree", bg="#00eaff", command=self.generate_tree).grid(row=0, column=0, padx=8, pady=6)
        tk.Button(ctrl, text="Load Custom", bg="#60a5fa", command=self.load_from_entry).grid(row=0, column=1, padx=8, pady=6)

        tk.Button(ctrl, text="Inorder", bg="#60a5fa", command=self.prepare_inorder).grid(row=0, column=2, padx=8)
        tk.Button(ctrl, text="Preorder", bg="#34d399", command=self.prepare_preorder).grid(row=0, column=3, padx=8)
        tk.Button(ctrl, text="Postorder", bg="#f87171", command=self.prepare_postorder).grid(row=0, column=4, padx=8)

        tk.Button(ctrl, text="Start", bg="#34d399", command=self.start_animation, width=10).grid(row=0, column=5, padx=8)
        tk.Button(ctrl, text="Stop", bg="#ef4444", command=self.stop_animation, width=10).grid(row=0, column=6, padx=8)

        # Entry field
        tk.Label(ctrl, text="Level-order (space separated):", fg="white", bg="#0d0d17").grid(row=1, column=0, columnspan=2, pady=6, sticky="w")
        self.entry_vals = tk.Entry(ctrl, width=60, bg="#111827", fg="#dbeafe", insertbackground="#dbeafe")
        self.entry_vals.grid(row=1, column=2, columnspan=5, sticky="w", padx=4)
        self.entry_vals.insert(0, "50 30 70 20 40 60 80")

        # Speed slider
        tk.Label(ctrl, text="Speed:", fg="white", bg="#0d0d17").grid(row=2, column=0, pady=6, sticky="w")
        self.speed = tk.DoubleVar(value=0.6)
        tk.Scale(ctrl, from_=0.1, to=2.0, resolution=0.1, orient="horizontal",
                 variable=self.speed, length=360, bg="#0d0d17", fg="white", troughcolor="#111827").grid(row=2, column=1, columnspan=4, padx=4, sticky="w")

        # ------------------- Main Paned Window -------------------
        # left: canvas; right: panel (stack + output)
        self.paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#0d0d17")
        self.paned.pack(fill="both", expand=True, padx=8, pady=8)

        # Left frame (canvas container)
        left_frame = tk.Frame(self.paned, bg="#0b0b17")
        self.canvas = tk.Canvas(left_frame, bg="#0b0b17", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        # add left_frame to paned
        self.paned.add(left_frame, stretch="always")

        # Right panel for stack + output
        panel = tk.Frame(self.paned, bg="#101018", width=340)
        panel.pack_propagate(False)  # keep requested width
        self.paned.add(panel)

        # Panel contents: stack list + output text with scrollbars
        tk.Label(panel, text="Recursion Stack", fg="#00eaff", bg="#101018", font=("Segoe UI", 16, "bold")).pack(pady=(8,6))
        self.stack_box = tk.Listbox(panel, width=32, height=12, bg="#0f1724", fg="#e6eef8", font=("Segoe UI", 11))
        self.stack_box.pack(pady=4, fill="x", padx=8)

        tk.Label(panel, text="Traversal Output", fg="#00eaff", bg="#101018", font=("Segoe UI", 16, "bold")).pack(pady=(12,6))
        # text plus vertical scrollbar
        out_frame = tk.Frame(panel, bg="#101018")
        out_frame.pack(padx=8, pady=4, fill="both", expand=True)
        self.output_box = tk.Text(out_frame, width=40, height=25, bg="#0f1724", fg="#e6eef8", font=("Segoe UI", 13))
        vsb = tk.Scrollbar(out_frame, orient="vertical", command=self.output_box.yview)
        self.output_box.configure(yscrollcommand=vsb.set)
        self.output_box.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # status
        self.status = tk.Label(root, text="Generate a tree or load custom values, then choose a traversal and Start.",
                               fg="white", bg="#0d0d17", font=("Segoe UI", 11))
        self.status.pack(pady=6)

        # Bind resize to recompute positions if needed
        self.canvas.bind("<Configure>", lambda e: self.on_canvas_resize())

        # Generate first tree
        self.generate_tree()

    # ---------------- canvas resize handler ----------------
    def on_canvas_resize(self):
        # When canvas size changes, recompute positions and redraw
        if not self.tree_root:
            return
        # small delay before recompute to avoid thrashing
        self.root.after(50, self.rebuild_canvas)

    # ---------------- Tree Building ----------------
    def generate_tree(self):
        vals = [random.randint(1, 99) for _ in range(7)]
        self.entry_vals.delete(0, tk.END)
        self.entry_vals.insert(0, " ".join(map(str, vals)))
        self.load_from_entry()

    def load_from_entry(self):
        txt = self.entry_vals.get().strip()
        try:
            vals = list(map(int, txt.split()))
        except:
            self.status.config(text="Invalid input")
            return

        nodes = [TreeNode(v) for v in vals]
        for i in range(len(nodes)):
            li = 2*i + 1
            ri = 2*i + 2
            if li < len(nodes):
                nodes[i].left = nodes[li]
            if ri < len(nodes):
                nodes[i].right = nodes[ri]
        self.tree_root = nodes[0] if nodes else None

        self.rebuild_canvas()
        self.status.config(text=f"Loaded tree with {len(nodes)} nodes")

    def rebuild_canvas(self):
        # clear and recompute using current canvas size
        self.positions.clear()
        self.node_ids.clear()
        self.text_ids.clear()
        self.edge_ids.clear()
        self.canvas.delete("all")

        if not self.tree_root:
            return

        # use actual canvas width (responsive)
        cwidth = self.canvas.winfo_width() or 1100
        self.compute_positions(self.tree_root, 0, cwidth, 80)
        self.draw_tree(self.tree_root)

    def compute_positions(self, node, x, width, y):
        if node is None:
            return
        px = x + width // 2
        py = y
        self.positions[node] = (px, py)
        self.compute_positions(node.left, x, width//2, y + 120)
        self.compute_positions(node.right, x + width//2, width//2, y + 120)

    def draw_tree(self, node):
        if node is None:
            return
        x,y = self.positions[node]

        # draw edges first (so nodes are on top)
        if node.left:
            lx, ly = self.positions[node.left]
            self.edge_ids[(node, node.left)] = self.canvas.create_line(x, y, lx, ly, fill="#64748b", width=2)
        if node.right:
            rx, ry = self.positions[node.right]
            self.edge_ids[(node, node.right)] = self.canvas.create_line(x, y, rx, ry, fill="#64748b", width=2)

        # draw node
        self.node_ids[node] = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="#1e293b", outline="#00eaff", width=3)
        self.text_ids[node] = self.canvas.create_text(x, y, text=str(node.val), fill="white", font=("Segoe UI", 14, "bold"))

        self.draw_tree(node.left)
        self.draw_tree(node.right)

    # ---------------- Traversal actions ----------------
    def build_actions_inorder(self, node):
        if node is None: return
        self.actions.append(("push", node))
        self.build_actions_inorder(node.left)
        self.actions.append(("visit", node))
        self.build_actions_inorder(node.right)
        self.actions.append(("pop", node))

    def build_actions_preorder(self, node):
        if node is None: return
        self.actions.append(("push", node))
        self.actions.append(("visit", node))
        self.build_actions_preorder(node.left)
        self.build_actions_preorder(node.right)
        self.actions.append(("pop", node))

    def build_actions_postorder(self, node):
        if node is None: return
        self.actions.append(("push", node))
        self.build_actions_postorder(node.left)
        self.build_actions_postorder(node.right)
        self.actions.append(("visit", node))
        self.actions.append(("pop", node))

    def prepare_inorder(self):
        if not self.tree_root:
            self.status.config(text="No tree loaded")
            return
        self.actions = []
        self.build_actions_inorder(self.tree_root)
        self.action_index = 0
        self.clear_outputs()
        self.status.config(text="Inorder ready — Press Start")

    def prepare_preorder(self):
        if not self.tree_root:
            self.status.config(text="No tree loaded")
            return
        self.actions = []
        self.build_actions_preorder(self.tree_root)
        self.action_index = 0
        self.clear_outputs()
        self.status.config(text="Preorder ready — Press Start")

    def prepare_postorder(self):
        if not self.tree_root:
            self.status.config(text="No tree loaded")
            return
        self.actions = []
        self.build_actions_postorder(self.tree_root)
        self.action_index = 0
        self.clear_outputs()
        self.status.config(text="Postorder ready — Press Start")

    def clear_outputs(self):
        self.output_box.delete("1.0", tk.END)
        self.stack_box.delete(0, tk.END)

    # ---------------- Animation engine ----------------
    def start_animation(self):
        if not self.actions:
            self.status.config(text="Prepare traversal first")
            return
        self.running = True
        self.action_index = 0
        self.clear_outputs()
        self.rebuild_canvas()
        self.status.config(text="Animation started")
        self.root.after(int(700*self.speed.get()), self.step_action)

    def stop_animation(self):
        self.running = False
        self.status.config(text="Animation stopped")

    def step_action(self):
        if not self.running:
            return
        if self.action_index >= len(self.actions):
            self.running = False
            self.status.config(text="Traversal complete")
            return

        typ, node = self.actions[self.action_index]
        x,y = self.positions[node]

        if typ == "push":
            self.stack_box.insert(tk.END, f"{node.val}")
            parent = self.find_parent(self.tree_root, node)
            if parent and (parent,node) in self.edge_ids:
                self.canvas.itemconfig(self.edge_ids[(parent,node)], fill="#facc15", width=4)
            # small pointer dot
            self.canvas.create_oval(x-6, y-46, x+6, y-34, fill="#60a5fa", outline="")

        elif typ == "visit":
            self.output_box.insert(tk.END, f"{node.val}  ")
            self.canvas.create_oval(x-36, y-36, x+36, y+36, outline="#34d399", width=4)

        elif typ == "pop":
            size = self.stack_box.size()
            if size > 0:
                self.stack_box.delete(size-1)
            parent = self.find_parent(self.tree_root, node)
            if parent and (parent,node) in self.edge_ids:
                self.canvas.itemconfig(self.edge_ids[(parent,node)], fill="#64748b", width=2)

        self.action_index += 1
        self.root.after(int(650*self.speed.get()), self.step_action)

    # ---------------- parent search ----------------
    def find_parent(self, root, child):
        if root is None:
            return None
        if root.left == child or root.right == child:
            return root
        left = self.find_parent(root.left, child)
        if left: return left
        return self.find_parent(root.right, child)

# ---------------- Run ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TreeTraversalVisualizer(root)
    root.mainloop()
