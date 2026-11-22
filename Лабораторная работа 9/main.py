import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from algorithms import clip_segment
class ClippingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Алгоритмы отсечения отрезков")
        self.geometry("1300x780")
        self.resizable(True, True)
        self.segments = []
        self.clipped = []
        self._build_ui()
        self._draw()
    def _build_ui(self):
        left = tk.Frame(self, width=340, bg="#f0f0f0")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left.pack_propagate(False)
        tk.Label(left, text="Алгоритмы отсечения",
                 font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(5, 2))
        tk.Label(left, text="Выбор алгоритма", bg="#f0f0f0").pack(anchor="w")
        self.algo_var = tk.StringVar(value="Сазерленда-Коэна")
        for name in ["Сазерленда-Коэна", "Простой алгоритм", "Алгоритм средней точки"]:
            tk.Radiobutton(left, text=name, variable=self.algo_var,
                           value=name, bg="#f0f0f0").pack(anchor="w")
        tk.Label(left, text="Параметры окна отсечения",
                 bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        win_frame = tk.Frame(left, bg="#f0f0f0")
        win_frame.pack(fill=tk.X)
        self.win_entries = {}
        for i, (label, default) in enumerate([
            ("Xmin", "200"), ("Xmax", "600"),
            ("Ymin", "150"), ("Ymax", "450"),
        ]):
            row, col = divmod(i, 2)
            tk.Label(win_frame, text=label, bg="#f0f0f0").grid(row=row, column=col*2, sticky="w", padx=2)
            e = tk.Entry(win_frame, width=7)
            e.insert(0, default)
            e.grid(row=row, column=col*2+1, padx=2, pady=2)
            self.win_entries[label] = e

        tk.Button(left, text="Обновить окно", command=self._update_window,
                  bg="#d0e0ff").pack(fill=tk.X, pady=4)

        tk.Label(left, text="Добавление отрезков",
                 bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))

        seg_frame = tk.Frame(left, bg="#f0f0f0")
        seg_frame.pack(fill=tk.X)
        self.seg_entries = {}
        for i, (label, default) in enumerate([
            ("X1", "50"), ("Y1", "50"),
            ("X2", "450"), ("Y2", "450"),
        ]):
            row, col = divmod(i, 2)
            tk.Label(seg_frame, text=label, bg="#f0f0f0").grid(row=row, column=col*2, sticky="w", padx=2)
            e = tk.Entry(seg_frame, width=7)
            e.insert(0, default)
            e.grid(row=row, column=col*2+1, padx=2, pady=2)
            self.seg_entries[label] = e

        tk.Button(left, text="Добавить отрезок", command=self._add_segment,
                  bg="#d0e0ff").pack(fill=tk.X, pady=2)
        tk.Button(left, text="Добавить 5 случайных отрезков", command=self._add_random,
                  bg="#e0e0e0").pack(fill=tk.X, pady=2)

        tk.Button(left, text="Выполнить отсечение", command=self._do_clip,
                  bg="#b0ffb0", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(10, 2))
        tk.Button(left, text="Очистить всё", command=self._clear_all,
                  bg="#ffb0b0").pack(fill=tk.X, pady=2)

        tk.Label(left, text="Информация", bg="#f0f0f0",
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.info_var = tk.StringVar(value="Выберите алгоритм и нажмите «Выполнить отсечение»")
        tk.Label(left, textvariable=self.info_var, bg="#f0f0f0",
                 wraplength=320, justify="left").pack(anchor="w")

        tk.Label(left, text="Список отрезков", bg="#f0f0f0",
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        list_frame = tk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True)
        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scroll.set, height=6)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.listbox.yview)
        right = tk.Frame(self, bg="white")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fig = Figure(figsize=(9, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        legend_frame = tk.Frame(right)
        legend_frame.pack(fill=tk.X)
        tk.Label(legend_frame, text="Окно отсечения:", bg="white").pack(side=tk.LEFT)
        tk.Label(legend_frame, text="  ", bg="red").pack(side=tk.LEFT, padx=(2, 10))
        tk.Label(legend_frame, text="Исходный отрезок:", bg="white").pack(side=tk.LEFT)
        tk.Label(legend_frame, text="  ", bg="gray").pack(side=tk.LEFT, padx=(2, 10))
        tk.Label(legend_frame, text="Отсечённая часть:", bg="white").pack(side=tk.LEFT)
        tk.Label(legend_frame, text="  ", bg="blue").pack(side=tk.LEFT, padx=(2, 10))
    def _get_window(self):
        try:
            return (float(self.win_entries["Xmin"].get()),
                    float(self.win_entries["Ymin"].get()),
                    float(self.win_entries["Xmax"].get()),
                    float(self.win_entries["Ymax"].get()))
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные координаты окна")
            return None
    def _update_window(self):
        if self._get_window() is not None:
            self._draw()
            self.info_var.set("Окно отсечения обновлено")

    def _add_segment(self):
        try:
            x1 = float(self.seg_entries["X1"].get())
            y1 = float(self.seg_entries["Y1"].get())
            x2 = float(self.seg_entries["X2"].get())
            y2 = float(self.seg_entries["Y2"].get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные координаты отрезка")
            return
        self.segments.append((x1, y1, x2, y2))
        self._refresh_listbox()
        self._draw()
    def _add_random(self):
        for _ in range(5):
            x1 = random.randint(-100, 700)
            y1 = random.randint(-100, 700)
            x2 = random.randint(-100, 700)
            y2 = random.randint(-100, 700)
            self.segments.append((x1, y1, x2, y2))
        self._refresh_listbox()
        self._draw()
    def _refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, (x1, y1, x2, y2) in enumerate(self.segments, 1):
            self.listbox.insert(tk.END, f"{i}: ({x1:.0f},{y1:.0f}) → ({x2:.0f},{y2:.0f})")
    def _do_clip(self):
        win = self._get_window()
        if win is None:
            return
        xmin, ymin, xmax, ymax = win
        algo = self.algo_var.get()
        self.clipped = []
        visible_count = 0
        for (x1, y1, x2, y2) in self.segments:
            cx1, cy1, cx2, cy2, vis = clip_segment(
                algo, x1, y1, x2, y2, xmin, ymin, xmax, ymax, eps=0.5
            )
            self.clipped.append((cx1, cy1, cx2, cy2, vis))
            if vis:
                visible_count += 1
        self.info_var.set(
            f"Алгоритм: {algo}\n"
            f"Всего отрезков: {len(self.segments)}\n"
            f"Полностью/частично видимых: {visible_count}\n"
            f"Полностью невидимых: {len(self.segments) - visible_count}"
        )
        self._draw(show_clipped=True)
    def _clear_all(self):
        self.segments.clear()
        self.clipped.clear()
        self._refresh_listbox()
        self.info_var.set("Список отрезков очищен")
        self._draw()
    def _draw(self, show_clipped=False):
        self.ax.clear()
        win = self._get_window()
        if win is None:
            return
        xmin, ymin, xmax, ymax = win
        all_x = [xmin, xmax]
        all_y = [ymin, ymax]
        for (x1, y1, x2, y2) in self.segments:
            all_x += [x1, x2]
            all_y += [y1, y2]
        pad = 50
        self.ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
        self.ax.set_ylim(min(all_y) - pad, max(all_y) + pad)
        self.ax.set_aspect("equal")
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.ax.set_title("Отсечение отрезков")
        rect = matplotlib.patches.Rectangle(
            (xmin, ymin), xmax - xmin, ymax - ymin,
            linewidth=2, edgecolor="red", facecolor="none", label="Окно"
        )
        self.ax.add_patch(rect)
        self.ax.text(xmin, ymax, f"({xmin:.0f},{ymax:.0f})", color="red", fontsize=8)
        self.ax.text(xmax, ymin, f"({xmax:.0f},{ymin:.0f})", color="red", fontsize=8)
        for (x1, y1, x2, y2) in self.segments:
            self.ax.plot([x1, x2], [y1, y2], color="gray", linewidth=1.2,
                         linestyle="-", alpha=0.7)
        if show_clipped:
            for (x1, y1, x2, y2, vis) in self.clipped:
                if vis:
                    self.ax.plot([x1, x2], [y1, y2], color="blue", linewidth=2.5)
        self.canvas.draw()
if __name__ == "__main__":
    app = ClippingApp()
    app.mainloop()