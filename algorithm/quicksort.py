import tkinter as tk
import random
import time
import threading

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = "#1a1a2e"
PANEL    = "#16213e"
CARD     = "#0f3460"
BAR_DEF  = "#4a90d9"          # unsorted – blue
BAR_PIV  = "#e94560"          # pivot    – red
BAR_LESS = "#27ae60"          # smaller  – green
BAR_MORE = "#e67e22"          # bigger   – orange
BAR_SWAP = "#9b59b6"          # swapping – purple
BAR_DONE = "#2ecc71"          # sorted   – bright green
WHITE    = "#ffffff"
GREY     = "#a0aec0"
YELLOW   = "#f6e05e"


class QuickSortVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Sort – Step by Step")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.array   = []
        self.n       = 16           # small default so bars are big & readable
        self.colors  = []
        self.running = False
        self.paused  = False
        self.step    = 0
        self.comparisons = 0
        self.swaps       = 0

        self._build_ui()
        self.generate_array()

    # ─────────────────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Title ──────────────────────────────────────────────────────────
        title_bar = tk.Frame(self.root, bg=CARD, pady=10)
        title_bar.pack(fill="x")

        tk.Label(title_bar,
                 text="Quick Sort Visualizer",
                 font=("Helvetica", 20, "bold"),
                 bg=CARD, fg=WHITE).pack(side="left", padx=20)

        tk.Label(title_bar,
                 text="Watch how Quick Sort works — step by step!",
                 font=("Helvetica", 11),
                 bg=CARD, fg=GREY).pack(side="left", padx=10)

        # ── Explanation card (narrates every step) ─────────────────────────
        # Fixed-height container — prevents layout shift when text changes
        exp_outer = tk.Frame(self.root, bg=PANEL, height=72)
        exp_outer.pack(fill="x", padx=16, pady=(10, 0))
        exp_outer.pack_propagate(False)   # <-- key: never resize to content

        tk.Label(exp_outer, text="What's happening now:",
                 font=("Helvetica", 11, "bold"),
                 bg=PANEL, fg=YELLOW).place(x=12, y=4)

        self.lbl_explain = tk.Label(
            exp_outer,
            text="Press  Start Sorting  to begin!",
            font=("Helvetica", 12, "bold"),
            bg=PANEL, fg=WHITE,
            wraplength=920, justify="left",
            anchor="nw")
        self.lbl_explain.place(x=20, y=26, relwidth=1.0)

        # ── Comparison callout row — fixed height ──────────────────────────
        cmp_outer = tk.Frame(self.root, bg=BG, height=80)
        cmp_outer.pack(fill="x", padx=16, pady=(8, 0))
        cmp_outer.pack_propagate(False)   # <-- never resize

        cmp_frame = tk.Frame(cmp_outer, bg=BG)
        cmp_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        # Pivot box
        pbox = tk.Frame(cmp_frame, bg="#4a0010", relief="ridge", bd=2)
        pbox.pack(side="left", padx=(0, 8), pady=4)
        tk.Label(pbox, text="PIVOT  (reference number)",
                 font=("Helvetica", 10, "bold"), bg="#4a0010",
                 fg=BAR_PIV).pack(padx=10, pady=(4, 0))
        self.lbl_pivot_val = tk.Label(pbox, text="—",
                                      font=("Helvetica", 22, "bold"),
                                      bg="#4a0010", fg=BAR_PIV)
        self.lbl_pivot_val.pack(padx=24, pady=(0, 4))

        tk.Label(cmp_frame, text="vs", font=("Helvetica", 18, "bold"),
                 bg=BG, fg=GREY).pack(side="left", padx=8)

        # Current element box
        ebox = tk.Frame(cmp_frame, bg="#1a3a1a", relief="ridge", bd=2)
        ebox.pack(side="left", padx=8, pady=4)
        tk.Label(ebox, text="CURRENT ELEMENT  (being compared)",
                 font=("Helvetica", 10, "bold"), bg="#1a3a1a",
                 fg="#7dcea0").pack(padx=10, pady=(4, 0))
        self.lbl_curr_val = tk.Label(ebox, text="—",
                                     font=("Helvetica", 22, "bold"),
                                     bg="#1a3a1a", fg=WHITE)
        self.lbl_curr_val.pack(padx=24, pady=(0, 4))

        # Result verdict — fixed width so it never wraps and grows
        self.lbl_verdict = tk.Label(cmp_frame, text="",
                                    font=("Helvetica", 13, "bold"),
                                    bg=BG, fg=WHITE,
                                    width=32, anchor="w", justify="left")
        self.lbl_verdict.pack(side="left", padx=16)

        # ── Canvas ────────────────────────────────────────────────────────
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0,
                                height=240)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=8)

        # ── Stats row ─────────────────────────────────────────────────────
        stats = tk.Frame(self.root, bg=PANEL)
        stats.pack(fill="x", padx=16, pady=(0, 6))

        def stat_lbl(parent, prefix, init, color):
            f = tk.Frame(parent, bg=PANEL)
            f.pack(side="left", padx=18, pady=5)
            lbl = tk.Label(f, text=f"{prefix}{init}",
                           font=("Helvetica", 11, "bold"),
                           bg=PANEL, fg=color)
            lbl.pack()
            return lbl, prefix

        (self.lbl_cmp_count,  self._pre_cmp)  = stat_lbl(stats, "Comparisons: ", "0",     YELLOW)
        (self.lbl_swap_count, self._pre_swp)  = stat_lbl(stats, "Swaps: ",       "0",     BAR_SWAP)
        (self.lbl_step_count, self._pre_stp)  = stat_lbl(stats, "Step: ",        "0",     GREY)
        (self.lbl_status,     self._pre_sta)  = stat_lbl(stats, "",              "READY", BAR_DONE)

        # ── Legend ────────────────────────────────────────────────────────
        leg_outer = tk.Frame(self.root, bg=PANEL)
        leg_outer.pack(fill="x", padx=16, pady=(0, 4))

        tk.Label(leg_outer, text="Colour Guide:",
                 font=("Helvetica", 9, "bold"),
                 bg=PANEL, fg=GREY).pack(side="left", padx=10)

        for color, label in [
            (BAR_DEF,  "Unsorted"),
            (BAR_PIV,  "Pivot (reference)"),
            (BAR_LESS, "Smaller than pivot"),
            (BAR_MORE, "Bigger than pivot"),
            (BAR_SWAP, "Being swapped"),
            (BAR_DONE, "Sorted!"),
        ]:
            dot = tk.Label(leg_outer, text="  ●", font=("Helvetica", 14),
                           bg=PANEL, fg=color)
            dot.pack(side="left")
            tk.Label(leg_outer, text=label, font=("Helvetica", 9),
                     bg=PANEL, fg=WHITE).pack(side="left", padx=(0, 10))

        # ── Controls ──────────────────────────────────────────────────────
        ctrl = tk.Frame(self.root, bg=BG)
        ctrl.pack(fill="x", padx=16, pady=(4, 14))

        left = tk.Frame(ctrl, bg=BG)
        left.pack(side="left")

        def add_slider(parent, label, var, lo, hi, col):
            tk.Label(parent, text=label, font=("Helvetica", 9, "bold"),
                     bg=BG, fg=GREY).grid(row=0, column=col*2,   padx=(16, 4))
            s = tk.Scale(parent, from_=lo, to=hi, orient="horizontal",
                         variable=var, length=130,
                         bg=BG, fg=WHITE, troughcolor=PANEL,
                         highlightthickness=0, activebackground=YELLOW,
                         font=("Helvetica", 8))
            s.grid(row=0, column=col*2+1)

        self.size_var  = tk.IntVar(value=self.n)
        self.speed_var = tk.DoubleVar(value=20)
        add_slider(left, "Number of bars:", self.size_var,  4, 30, 0)
        add_slider(left, "Speed:",          self.speed_var, 1, 100, 1)
        self.size_var.trace_add("write", lambda *_: self._on_size_change())

        right = tk.Frame(ctrl, bg=BG)
        right.pack(side="right")

        def btn(text, cmd, bg_c, fg_c=WHITE):
            b = tk.Button(right, text=text, command=cmd,
                          font=("Helvetica", 11, "bold"),
                          bg=bg_c, fg=fg_c,
                          activebackground=YELLOW, activeforeground=BG,
                          relief="flat", padx=16, pady=8, cursor="hand2")
            b.pack(side="left", padx=5)
            return b

        btn("New Array",      self.generate_array,  CARD)
        btn("Start Sorting",  self.start_sort,       BAR_LESS, BG)
        self.btn_pause = btn("Pause",               self.toggle_pause, CARD)
        btn("Stop",           self.stop_sort,        "#5c1a1a")

    # ─────────────────────────────────────────────────────────────────────────
    # Array helpers
    # ─────────────────────────────────────────────────────────────────────────
    def generate_array(self):
        if self.running:
            return
        self.n = self.size_var.get()
        pool = list(range(5, 100))
        random.shuffle(pool)
        self.array  = pool[:self.n]
        self.colors = [BAR_DEF] * self.n
        self.comparisons = self.swaps = self.step = 0
        self._update_stats()
        self._set_explain("Press  Start Sorting  to watch Quick Sort in action!")
        self._set_status("READY", BAR_DONE)
        self._reset_callout()
        self.draw()

    def _on_size_change(self):
        if not self.running:
            self.root.after(100, self.generate_array)

    # ─────────────────────────────────────────────────────────────────────────
    # Drawing
    # ─────────────────────────────────────────────────────────────────────────
    def draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()  or 900
        h = self.canvas.winfo_height() or 240
        if not self.array:
            return

        n       = len(self.array)
        gap     = 5
        bar_w   = max(12, (w - gap * (n + 1)) / n)
        total_w = (bar_w + gap) * n - gap
        pad_x   = (w - total_w) / 2
        max_val = max(self.array) or 1

        for i, val in enumerate(self.array):
            x0    = pad_x + i * (bar_w + gap)
            x1    = x0 + bar_w
            bh    = max(16, (val / max_val) * (h - 52))
            y0    = h - bh - 30
            y1    = h - 30
            color = self.colors[i]

            self.canvas.create_rectangle(x0, y0, x1, y1,
                                         fill=color, outline="#000000",
                                         width=1)

            # Value label on top of bar
            fs = max(7, min(13, int(bar_w) - 2))
            self.canvas.create_text((x0+x1)/2, y0 - 9,
                                    text=str(val), fill=WHITE,
                                    font=("Helvetica", fs, "bold"))

            # Index label below bar
            if bar_w >= 16:
                self.canvas.create_text((x0+x1)/2, y1 + 12,
                                        text=f"[{i}]", fill=GREY,
                                        font=("Helvetica", 7))

    # ─────────────────────────────────────────────────────────────────────────
    # UI helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _set_explain(self, text, color=WHITE):
        self.lbl_explain.config(text=text, fg=color)

    def _set_status(self, text, color=WHITE):
        self.lbl_status.config(text=text, fg=color)

    def _update_stats(self):
        self.lbl_cmp_count .config(text=f"Comparisons: {self.comparisons}")
        self.lbl_swap_count.config(text=f"Swaps: {self.swaps}")
        self.lbl_step_count.config(text=f"Step: {self.step}")

    def _set_callout(self, pivot, curr, verdict, verdict_color):
        self.lbl_pivot_val.config(text=str(pivot))
        self.lbl_curr_val .config(text=str(curr) if curr != "—" else "—")
        self.lbl_verdict  .config(text=verdict, fg=verdict_color)

    def _reset_callout(self):
        self.lbl_pivot_val.config(text="—")
        self.lbl_curr_val .config(text="—")
        self.lbl_verdict  .config(text="")

    # ─────────────────────────────────────────────────────────────────────────
    # Controls
    # ─────────────────────────────────────────────────────────────────────────
    def start_sort(self):
        if self.running:
            return
        self.running     = True
        self.paused      = False
        self.comparisons = self.swaps = self.step = 0
        self._update_stats()
        self._set_status("SORTING...", YELLOW)
        threading.Thread(target=self._run_sort, daemon=True).start()

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.btn_pause.config(text="Resume")
            self._set_explain("Paused — press Resume to continue.", YELLOW)
            self._set_status("PAUSED", YELLOW)
        else:
            self.btn_pause.config(text="Pause")
            self._set_status("SORTING...", YELLOW)

    def stop_sort(self):
        self.running = False
        self.paused  = False
        self.btn_pause.config(text="Pause")
        self.colors = [BAR_DEF] * self.n
        self._set_explain("Stopped. Press 'New Array' or 'Start Sorting' again.")
        self._set_status("STOPPED", BAR_PIV)
        self._reset_callout()
        self.root.after(0, self.draw)

    # ─────────────────────────────────────────────────────────────────────────
    # Delay
    # ─────────────────────────────────────────────────────────────────────────
    def _wait(self):
        while self.paused and self.running:
            time.sleep(0.05)
        spd = self.speed_var.get()
        time.sleep(max(0.02, 1.1 - spd * 0.01))

    # ─────────────────────────────────────────────────────────────────────────
    # Sort logic
    # ─────────────────────────────────────────────────────────────────────────
    def _run_sort(self):
        arr       = self.array
        stack     = [(0, len(arr) - 1)]
        round_num = 0

        while stack and self.running:
            low, high = stack.pop()
            if low >= high:
                if low == high:
                    self.colors[low] = BAR_DONE
                    self.root.after(0, self.draw)
                continue

            round_num += 1
            self.root.after(0, lambda r=round_num, l=low, h=high:
                self._set_explain(
                    f"Round {r}:  We are looking at positions [{l}] to [{h}].  "
                    f"We will pick the LAST number in this section as our PIVOT (the reference number).",
                    YELLOW))
            self._wait()

            pivot_idx = self._partition(arr, low, high, round_num)
            if pivot_idx is None:
                break

            self.colors[pivot_idx] = BAR_DONE
            self.root.after(0, self.draw)
            self.root.after(0, lambda p=arr[pivot_idx], pi=pivot_idx:
                self._set_explain(
                    f"The pivot  {p}  is now in its CORRECT final position [{pi}]!  "
                    f"All numbers to its left are smaller, all to its right are bigger.",
                    BAR_DONE))
            self._wait()

            stack.append((low,           pivot_idx - 1))
            stack.append((pivot_idx + 1, high))

        if self.running:
            for i in range(len(arr)):
                self.colors[i] = BAR_DONE
                self.root.after(0, self.draw)
                time.sleep(0.03)
            self.root.after(0, lambda:
                self._set_explain(
                    f"All done!  The array is fully sorted!  "
                    f"Total: {self.step} steps,  {self.comparisons} comparisons,  {self.swaps} swaps.",
                    BAR_DONE))
            self.root.after(0, lambda: self._set_status("SORTED!", BAR_DONE))
            self.root.after(0, self._reset_callout)

        self.running = False
        self.root.after(0, lambda: self.btn_pause.config(text="Pause"))

    def _partition(self, arr, low, high, round_num):
        pivot = arr[high]

        # Highlight pivot
        self.colors[high] = BAR_PIV
        self.root.after(0, self.draw)
        self.root.after(0, lambda p=pivot:
            self._set_callout(p, "—",
                              f"This is our PIVOT for Round {round_num}",
                              BAR_PIV))
        self.root.after(0, lambda p=pivot:
            self._set_explain(
                f"PIVOT = {p}  (at position [{high}]).  "
                f"Now we will go through each number from [{low}] to [{high-1}] "
                f"and ask: is it smaller or bigger than {p}?",
                BAR_PIV))
        self._wait()

        i = low - 1

        for j in range(low, high):
            if not self.running:
                return None

            elem = arr[j]
            self.step += 1
            self.root.after(0, self._update_stats)

            if elem <= pivot:
                # ── Smaller or equal ───────────────────────────────────────
                self.colors[j] = BAR_LESS
                self.root.after(0, self.draw)
                self.comparisons += 1
                self.root.after(0, self._update_stats)
                self.root.after(0, lambda e=elem, p=pivot:
                    self._set_callout(p, e,
                                      f"{e} <= {p}\nSMALLER!  Move it to the LEFT side.",
                                      BAR_LESS))
                self.root.after(0, lambda e=elem, p=pivot:
                    self._set_explain(
                        f"GREEN bar  {e}  is SMALLER than (or equal to) the pivot {p}.  "
                        f"It belongs on the LEFT side.  We swap it into the left section.",
                        BAR_LESS))
                self._wait()

                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                self.colors[i] = BAR_SWAP
                self.colors[j] = BAR_SWAP
                self.root.after(0, self.draw)
                self.swaps += 1
                self.root.after(0, self._update_stats)
                self.root.after(0, lambda e=elem, ii=i, jj=j:
                    self._set_explain(
                        f"Swapping positions [{jj}] and [{ii}] — "
                        f"moving {e} further left into the 'smaller' group.",
                        BAR_SWAP))
                self._wait()
                self.colors[i] = BAR_LESS
                self.colors[j] = BAR_DEF
                self.root.after(0, self.draw)

            else:
                # ── Bigger ─────────────────────────────────────────────────
                self.colors[j] = BAR_MORE
                self.root.after(0, self.draw)
                self.comparisons += 1
                self.root.after(0, self._update_stats)
                self.root.after(0, lambda e=elem, p=pivot:
                    self._set_callout(p, e,
                                      f"{e} > {p}\nBIGGER!  Leave it on the RIGHT side.",
                                      BAR_MORE))
                self.root.after(0, lambda e=elem, p=pivot:
                    self._set_explain(
                        f"ORANGE bar  {e}  is BIGGER than the pivot {p}.  "
                        f"It belongs on the RIGHT side.  We leave it where it is.",
                        BAR_MORE))
                self._wait()

        # Place pivot in correct spot
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        self.swaps += 1
        self.root.after(0, self._update_stats)

        # Reset colours for this range
        for k in range(low, high + 1):
            if self.colors[k] in (BAR_LESS, BAR_MORE, BAR_SWAP):
                self.colors[k] = BAR_DEF
        self.root.after(0, self.draw)

        return i + 1


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.geometry("980x700")
    root.minsize(720, 520)
    app = QuickSortVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()