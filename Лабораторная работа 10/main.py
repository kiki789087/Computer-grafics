import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms import (
    bezier_point, bezier_curve, bezier_levels,
    chaikin_once, chaikin_curve,
    doo_sabin, make_grid,
)


class CurvesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1400x820")
        self.minsize(1100, 650)


        self.bezier_points = []
        self.chaikin_points = []
        self.doo_grid = make_grid(3, 3, 0, 0, 2, 2)  # сетка по умолчанию 3x3

        self._build_ui()
        self._draw_empty()

    def _build_ui(self):

        left = tk.Frame(self, width=380, bg="#f4f4f4")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left.pack_propagate(False)


        nb = ttk.Notebook(left)
        nb.pack(fill=tk.BOTH, expand=True)
        self.notebook = nb

        self.tab_bezier = tk.Frame(nb, bg="#f4f4f4")
        self.tab_chaikin = tk.Frame(nb, bg="#f4f4f4")
        self.tab_doo = tk.Frame(nb, bg="#f4f4f4")
        nb.add(self.tab_bezier, text="Безье")
        nb.add(self.tab_chaikin, text="Чайкин")
        nb.add(self.tab_doo, text="Ду-Сабин")

        self._build_bezier_tab(self.tab_bezier)
        self._build_chaikin_tab(self.tab_chaikin)
        self._build_doo_tab(self.tab_doo)


        tk.Button(left, text="▶  Построить и отрисовать",
                  command=self._draw,
                  bg="#b0ffb0", font=("Arial", 11, "bold")).pack(fill=tk.X, pady=(8, 4))
        tk.Button(left, text="Очистить всё", command=self._clear_all,
                  bg="#ffb0b0").pack(fill=tk.X)


        right = tk.Frame(self, bg="white")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig = Figure(figsize=(9, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


        self.info_var = tk.StringVar(value="Заполните параметры и нажмите «Построить»")
        tk.Label(right, textvariable=self.info_var, bg="white",
                 justify="left", font=("Arial", 9)).pack(fill=tk.X)


    def _build_bezier_tab(self, parent):
        tk.Label(parent, text="Квадратичная кривая Безье",
                 font=("Arial", 11, "bold"), bg="#f4f4f4").pack(anchor="w", pady=(4, 4))

        tk.Label(parent, text="Введите точки (x,y через запятую, по одной на строку):",
                 bg="#f4f4f4", wraplength=360, justify="left").pack(anchor="w")
        self.bezier_text = tk.Text(parent, height=7, width=42)
        self.bezier_text.insert("1.0", "0,0\n2,3\n5,1\n6,4")
        self.bezier_text.pack(fill=tk.X, pady=4)

        row = tk.Frame(parent, bg="#f4f4f4")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Точка (x, y):", bg="#f4f4f4").pack(side=tk.LEFT)
        self.new_bx = tk.Entry(row, width=6)
        self.new_bx.insert(0, "3")
        self.new_bx.pack(side=tk.LEFT, padx=2)
        self.new_by = tk.Entry(row, width=6)
        self.new_by.insert(0, "3")
        self.new_by.pack(side=tk.LEFT, padx=2)
        tk.Button(row, text="+", command=self._add_bezier_point,
                  bg="#d0e0ff", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(row, text="Случайно 4", command=self._random_bezier,
                  bg="#e0e0e0").pack(side=tk.LEFT, padx=2)

        row2 = tk.Frame(parent, bg="#f4f4f4")
        row2.pack(fill=tk.X, pady=4)
        tk.Label(row2, text="Параметр t:", bg="#f4f4f4").pack(side=tk.LEFT)
        self.t_var = tk.DoubleVar(value=0.5)
        self.t_slider = tk.Scale(row2, from_=0.0, to=1.0, resolution=0.01,
                                  orient=tk.HORIZONTAL, variable=self.t_var,
                                  bg="#f4f4f4", length=180)
        self.t_slider.pack(side=tk.LEFT, padx=4)

        row3 = tk.Frame(parent, bg="#f4f4f4")
        row3.pack(fill=tk.X, pady=2)
        tk.Label(row3, text="Шагов кривой:", bg="#f4f4f4").pack(side=tk.LEFT)
        self.bezier_steps = tk.Entry(row3, width=6)
        self.bezier_steps.insert(0, "60")
        self.bezier_steps.pack(side=tk.LEFT, padx=4)

        self.show_bezier_levels = tk.BooleanVar(value=True)
        tk.Checkbutton(parent, text="Показывать промежуточные вершины",
                       variable=self.show_bezier_levels,
                       bg="#f4f4f4").pack(anchor="w", pady=2)

    def _add_bezier_point(self):
        try:
            x = float(self.new_bx.get())
            y = float(self.new_by.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные x и y")
            return
        self.bezier_text.insert(tk.END, f"\n{x},{y}")

    def _random_bezier(self):
        self.bezier_text.delete("1.0", tk.END)
        pts = []
        for _ in range(4):
            x = random.uniform(0, 8)
            y = random.uniform(0, 8)
            pts.append(f"{x:.2f},{y:.2f}")
        self.bezier_text.insert("1.0", "\n".join(pts))

    def _build_chaikin_tab(self, parent):
        tk.Label(parent, text="Кривая Чайкина",
                 font=("Arial", 11, "bold"), bg="#f4f4f4").pack(anchor="w", pady=(4, 4))

        tk.Label(parent, text="Точки контрольного полигона (x,y через запятую, по строкам):",
                 bg="#f4f4f4", wraplength=360, justify="left").pack(anchor="w")
        self.chaikin_text = tk.Text(parent, height=8, width=42)
        self.chaikin_text.insert("1.0", "0,0\n3,4\n5,1\n8,5\n10,2")
        self.chaikin_text.pack(fill=tk.X, pady=4)

        row = tk.Frame(parent, bg="#f4f4f4")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Точка (x, y):", bg="#f4f4f4").pack(side=tk.LEFT)
        self.new_cx = tk.Entry(row, width=6)
        self.new_cx.insert(0, "2")
        self.new_cx.pack(side=tk.LEFT, padx=2)
        self.new_cy = tk.Entry(row, width=6)
        self.new_cy.insert(0, "2")
        self.new_cy.pack(side=tk.LEFT, padx=2)
        tk.Button(row, text="+", command=self._add_chaikin_point,
                  bg="#d0e0ff", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(row, text="Случайно 5", command=self._random_chaikin,
                  bg="#e0e0e0").pack(side=tk.LEFT, padx=2)

        row2 = tk.Frame(parent, bg="#f4f4f4")
        row2.pack(fill=tk.X, pady=4)
        tk.Label(row2, text="Количество разбиений:", bg="#f4f4f4").pack(side=tk.LEFT)
        self.chaikin_iter = tk.Entry(row2, width=5)
        self.chaikin_iter.insert(0, "5")
        self.chaikin_iter.pack(side=tk.LEFT, padx=4)

        self.show_chaikin_steps = tk.BooleanVar(value=True)
        tk.Checkbutton(parent, text="Показывать все промежуточные полигоны",
                       variable=self.show_chaikin_steps,
                       bg="#f4f4f4").pack(anchor="w", pady=2)

    def _add_chaikin_point(self):
        try:
            x = float(self.new_cx.get())
            y = float(self.new_cy.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные x и y")
            return
        self.chaikin_text.insert(tk.END, f"\n{x},{y}")

    def _random_chaikin(self):
        self.chaikin_text.delete("1.0", tk.END)
        pts = []
        for _ in range(5):
            x = random.uniform(0, 10)
            y = random.uniform(0, 8)
            pts.append(f"{x:.2f},{y:.2f}")
        self.chaikin_text.insert("1.0", "\n".join(pts))

    def _build_doo_tab(self, parent):
        tk.Label(parent, text="Поверхность Ду-Сабина",
                 font=("Arial", 11, "bold"), bg="#f4f4f4").pack(anchor="w", pady=(4, 4))

        row = tk.Frame(parent, bg="#f4f4f4")
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Строк (N):", bg="#f4f4f4").pack(side=tk.LEFT)
        self.doo_rows = tk.Entry(row, width=5)
        self.doo_rows.insert(0, "3")
        self.doo_rows.pack(side=tk.LEFT, padx=2)
        tk.Label(row, text="Столбцов (M):", bg="#f4f4f4").pack(side=tk.LEFT)
        self.doo_cols = tk.Entry(row, width=5)
        self.doo_cols.insert(0, "3")
        self.doo_cols.pack(side=tk.LEFT, padx=2)

        tk.Button(parent, text="Сгенерировать сетку вершин",
                  command=self._gen_doo_grid,
                  bg="#d0e0ff").pack(fill=tk.X, pady=2)

        row2 = tk.Frame(parent, bg="#f4f4f4")
        row2.pack(fill=tk.X, pady=4)
        tk.Label(row2, text="Количество итераций:", bg="#f4f4f4").pack(side=tk.LEFT)
        self.doo_iter = tk.Entry(row2, width=5)
        self.doo_iter.insert(0, "2")
        self.doo_iter.pack(side=tk.LEFT, padx=4)

        self.show_doo_faces = tk.BooleanVar(value=True)
        tk.Checkbutton(parent, text="Показывать грани (полигоны)",
                       variable=self.show_doo_faces,
                       bg="#f4f4f4").pack(anchor="w", pady=2)

        self.show_doo_points = tk.BooleanVar(value=True)
        tk.Checkbutton(parent, text="Показывать новые точки (вершины, рёбра, грани)",
                       variable=self.show_doo_points,
                       bg="#f4f4f4").pack(anchor="w", pady=2)

        self.doo_text = tk.Text(parent, height=6, width=42, state="disabled")
        self.doo_text.pack(fill=tk.X, pady=4)

    def _gen_doo_grid(self):
        try:
            r = int(self.doo_rows.get())
            c = int(self.doo_cols.get())
            if r < 2 or c < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Размеры сетки должны быть >= 2")
            return
        verts = []
        faces = []
        for ri in range(r):
            for ci in range(c):
                x = ci * 2.0 + random.uniform(-0.4, 0.4)
                y = ri * 2.0 + random.uniform(-0.4, 0.4)
                verts.append((x, y))
        for ri in range(r - 1):
            for ci in range(c - 1):
                i = ri * c + ci
                faces.append([i, i + 1, i + 1 + c, i + c])
        self.doo_grid = {"vertices": verts, "faces": faces}
        self.doo_text.config(state="normal")
        self.doo_text.delete("1.0", tk.END)
        self.doo_text.insert("1.0", f"Сетка {r}x{c}: {len(verts)} вершин, {len(faces)} граней")
        self.doo_text.config(state="disabled")
        self._draw()

    def _clear_all(self):
        self.bezier_text.delete("1.0", tk.END)
        self.chaikin_text.delete("1.0", tk.END)
        self.doo_grid = make_grid(3, 3, 0, 0, 2, 2)
        self.doo_text.config(state="normal")
        self.doo_text.delete("1.0", tk.END)
        self.doo_text.config(state="disabled")
        self.ax.clear()
        self.ax.set_xlim(-1, 12)
        self.ax.set_ylim(-1, 12)
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.canvas.draw()
        self.info_var.set("Очищено")

    def _parse_points(self, text):
        pts = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            sep = "," if "," in line else (";" if ";" in line else None)
            if sep is None:
                continue
            try:
                a, b = line.split(sep)
                pts.append((float(a), float(b)))
            except ValueError:
                continue
        return pts

    def _draw(self):
        self.ax.clear()
        self.ax.set_aspect("equal")
        self.ax.grid(True, linestyle="--", alpha=0.4)

        tab = self.notebook.index(self.notebook.select())

        if tab == 0:
            self._draw_bezier()
        elif tab == 1:
            self._draw_chaikin()
        else:
            self._draw_doo()

        self.canvas.draw()

    def _draw_empty(self):
        self.ax.clear()
        self.ax.set_aspect("equal")
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.ax.set_xlim(-1, 12)
        self.ax.set_ylim(-1, 12)
        self.canvas.draw()
        self.info_var.set("")

    def _draw_bezier(self):
        pts = self._parse_points(self.bezier_text.get("1.0", tk.END))
        if len(pts) < 2:
            self.info_var.set("Безье: нужно минимум 2 точки")
            self.ax.set_xlim(-1, 10)
            self.ax.set_ylim(-1, 10)
            return

        try:
            steps = int(self.bezier_steps.get())
            if steps < 2:
                raise ValueError
        except ValueError:
            steps = 60

        t = self.t_var.get()

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.ax.plot(xs, ys, "o--", color="gray", linewidth=1.0,
                     markersize=6, label="Контрольный полигон")

        for i, (x, y) in enumerate(pts):
            self.ax.text(x + 0.08, y + 0.08, f"P{i}", fontsize=9)

        curve = bezier_curve(pts, steps)
        cx = [p[0] for p in curve]
        cy = [p[1] for p in curve]
        self.ax.plot(cx, cy, color="blue", linewidth=2.2, label="Кривая Безье")

        if self.show_bezier_levels.get() and 0 < t < 1:
            levels = bezier_levels(pts, t)
            colors = ["#ff8800", "#cc4400", "#880088", "#008888"]
            for li in range(1, len(levels)):
                lx = [p[0] for p in levels[li]]
                ly = [p[1] for p in levels[li]]
                col = colors[(li - 1) % len(colors)]
                self.ax.plot(lx, ly, "o-", color=col, linewidth=1.0,
                             markersize=5, alpha=0.85,
                             label=f"Уровень {li}")
            pt = bezier_point(pts, t)
            self.ax.plot(pt[0], pt[1], "o", color="red", markersize=9,
                         label=f"t={t:.2f} → B(t)")

        self.ax.set_title(f"Квадратичная кривая Безье ({len(pts)} вершин)")
        self.info_var.set(
            f"Безье: {len(pts)} контрольных точек, t={t:.2f}, шагов={steps}\n"
            f"Промежуточные уровни: {'вкл' if self.show_bezier_levels.get() else 'выкл'}"
        )

    def _draw_chaikin(self):
        pts = self._parse_points(self.chaikin_text.get("1.0", tk.END))
        if len(pts) < 2:
            self.info_var.set("Чайкин: нужно минимум 2 точки")
            self.ax.set_xlim(-1, 12)
            self.ax.set_ylim(-1, 12)
            return

        try:
            iters = int(self.chaikin_iter.get())
            if iters < 0:
                raise ValueError
        except ValueError:
            iters = 5

        result = chaikin_curve(pts, iters)

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.ax.plot(xs, ys, "o--", color="gray", linewidth=1.0,
                     markersize=6, label="Исходный полигон")
        if self.show_chaikin_steps.get():
            cmap = matplotlib.colormaps["viridis"].resampled(max(iters + 1, 2))
            for i in range(1, len(result)):
                p = result[i]
                col = cmap(i / max(iters, 1))
                px = [q[0] for q in p]
                py = [q[1] for q in p]
                if i == len(result) - 1:
                    self.ax.plot(px, py, color="blue", linewidth=2.2,
                                 label=f"Кривая (итерация {i})")
                else:
                    self.ax.plot(px, py, "o-", color=col, linewidth=0.8,
                                 markersize=3, alpha=0.7, label=f"Итерация {i}")
        else:
            p = result[-1]
            px = [q[0] for q in p]
            py = [q[1] for q in p]
            self.ax.plot(px, py, color="blue", linewidth=2.2, label="Кривая")
        last = result[-1]
        for (x, y) in last:
            self.ax.plot(x, y, "o", color="blue", markersize=2.5, alpha=0.6)

        self.ax.set_title(f"Кривая Чайкина ({iters} разбиений)")
        self.info_var.set(
            f"Чайкин: {len(pts)} исходных точек, {iters} разбиений, "
            f"{len(result[-1])} точек в финальном полигоне"
        )

    def _draw_doo(self):
        try:
            iters = int(self.doo_iter.get())
            if iters < 0:
                raise ValueError
        except ValueError:
            iters = 2
        states = doo_sabin(self.doo_grid, iters)
        final = states[-1]
        orig = self.doo_grid
        for fi, f in enumerate(orig["faces"]):
            quad = [orig["vertices"][i] for i in f]
            quad.append(quad[0])
            xs = [p[0] for p in quad]
            ys = [p[1] for p in quad]
            self.ax.plot(xs, ys, "o-", color="gray", linewidth=0.9,
                         markersize=4, alpha=0.7)

        if self.show_doo_faces.get():
            for f in final["faces"]:
                if len(f) >= 3:
                    quad = list(f) + [f[0]]
                    xs = [p[0] for p in quad]
                    ys = [p[1] for p in quad]
                    self.ax.plot(xs, ys, "-", color="blue", linewidth=0.9)

        if self.show_doo_points.get() and final["new_points"]:
            nx = [p[0] for p in final["new_points"]]
            ny = [p[1] for p in final["new_points"]]
            self.ax.plot(nx, ny, "o", color="red", markersize=3,
                         label="Новые точки граней/рёбер/вершин")

        vx = [p[0] for p in final["vertices"]]
        vy = [p[1] for p in final["vertices"]]
        self.ax.plot(vx, vy, "o", color="darkgreen", markersize=4, label="Вершины сетки")
        self.ax.set_title(f"Поверхность Ду-Сабина ({iters} итераций)")
        self.info_var.set(
            f"Ду-Сабин: {len(orig['vertices'])} исходных вершин, "
            f"{len(orig['faces'])} граней → {iters} итераций → "
            f"{len(final['vertices'])} вершин, {len(final['faces'])} граней"
        )
if __name__ == "__main__":
    app = CurvesApp()
    app.mainloop()