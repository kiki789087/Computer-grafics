import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import re
import os

def sign(x):
    if x > 0: return 1
    if x < 0: return -1
    return 0

def dda(x1, y1, x2, y2, draw_pixel):
    if x1 == x2 and y1 == y2:
        draw_pixel(x1, y1)
        return
    L = max(abs(x2 - x1), abs(y2 - y1))
    dx = (x2 - x1) / L
    dy = (y2 - y1) / L
    x = x1 + 0.5 * sign(dx)
    y = y1 + 0.5 * sign(dy)
    for _ in range(int(L) + 1):
        draw_pixel(int(math.floor(x)), int(math.floor(y)))
        x += dx
        y += dy

def bresenham_float(x1, y1, x2, y2, draw_pixel):
    if x1 == x2 and y1 == y2:
        draw_pixel(x1, y1)
        return
    dx = x2 - x1
    dy = y2 - y1
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)
    swap = False
    if dy > dx:
        dx, dy = dy, dx
        swap = True
    f = dy / dx - 0.5
    x, y = x1, y1
    for _ in range(int(dx) + 1):
        draw_pixel(x, y)
        if f >= 0:
            if swap: x += sx
            else:    y += sy
            f -= 1.0
        if swap: y += sy
        else:    x += sx
        f += dy / dx

def bresenham_int(x1, y1, x2, y2, draw_pixel):
    if x1 == x2 and y1 == y2:
        draw_pixel(x1, y1)
        return
    dx = x2 - x1
    dy = y2 - y1
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)
    swap = False
    if dy > dx:
        dx, dy = dy, dx
        swap = True
    e = 2 * dy - dx
    x, y = x1, y1
    for _ in range(dx + 1):
        draw_pixel(x, y)
        if e >= 0:
            if swap: x += sx
            else:    y += sy
            e -= 2 * dx
        if swap: y += sy
        else:    x += sx
        e += 2 * dy

class PBMImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = [[0] * width for _ in range(height)]

    def clear(self):
        for row in self.pixels:
            for i in range(len(row)):
                row[i] = 0

    def set_pixel(self, x, y, color=1):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def save_pbm(self, filename):
        with open(filename, 'w') as f:
            f.write("P1\n")
            f.write(f"{self.width} {self.height}\n")
            for row in self.pixels:
                f.write(" ".join(map(str, row)) + "\n")

    def save_bmp(self, filename):
        width, height = self.width, self.height
        row_bytes = ((width + 31) // 32) * 4
        image_size = row_bytes * height
        file_size = 14 + 40 + 8 + image_size
        with open(filename, 'wb') as f:
            f.write(b'BM')
            f.write((file_size).to_bytes(4, 'little'))
            f.write((0).to_bytes(2, 'little'))
            f.write((0).to_bytes(2, 'little'))
            f.write((14 + 40 + 8).to_bytes(4, 'little'))
            f.write((40).to_bytes(4, 'little'))
            f.write((width).to_bytes(4, 'little', signed=True))
            f.write((height).to_bytes(4, 'little', signed=True))
            f.write((1).to_bytes(2, 'little'))
            f.write((1).to_bytes(2, 'little'))
            f.write((0).to_bytes(4, 'little'))
            f.write((image_size).to_bytes(4, 'little'))
            f.write((2835).to_bytes(4, 'little'))
            f.write((2835).to_bytes(4, 'little'))
            f.write((2).to_bytes(4, 'little'))
            f.write((2).to_bytes(4, 'little'))
            f.write(b'\x00\x00\x00\x00')
            f.write(b'\xff\xff\xff\x00')
            for y in range(height - 1, -1, -1):
                row_data = bytearray(row_bytes)
                for x in range(width):
                    if self.pixels[y][x] == 0:
                        row_data[x // 8] |= (1 << (7 - (x % 8)))
                f.write(bytes(row_data))

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def get_bisector_base(A, B, C):
    ab = distance(A, B)
    ac = distance(A, C)
    if ab + ac == 0:
        return B
    lx = (B[0] * ac + C[0] * ab) / (ab + ac)
    ly = (B[1] * ac + C[1] * ab) / (ab + ac)
    return (round(lx), round(ly))

def parse_svg_vertices(filename):
    with open(filename, 'rb') as f:
        raw = f.read()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    try:
        content = raw.decode('utf-8')
    except UnicodeDecodeError:
        content = raw.decode('cp1251', errors='replace')

    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    tag_pattern = r'<line\b([^>]*?)/?>'
    attr_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'

    points = []
    for tag_match in re.finditer(tag_pattern, content, flags=re.IGNORECASE | re.DOTALL):
        attrs_str = tag_match.group(1)
        attrs = dict(re.findall(attr_pattern, attrs_str))

        if not all(k in attrs for k in ['x1', 'y1', 'x2', 'y2']):
            continue

        try:
            x1 = int(float(attrs['x1']))
            y1 = int(float(attrs['y1']))
            x2 = int(float(attrs['x2']))
            y2 = int(float(attrs['y2']))
        except ValueError:
            continue

        if x1 == x2 and y1 == y2:
            points.append((x1, y1))

    if len(points) < 3:
        raise ValueError(
            f"В файле найдено {len(points)} вершин, нужно 3.\n"
            "Проверьте, что в SVG есть три отрезка нулевой длины:\n"
            '<line x1="..." y1="..." x2="..." y2="..." />\n'
            "где x1==x2 и y1==y2."
        )
    return points

class Lab3App:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №3 — Вариант 20")
        self.root.geometry("900x900")
        self.root.configure(bg="#f0f0f0")

        self.image = None
        self.canvas_width = 800
        self.canvas_height = 500

        self.A = self.B = self.C = None
        self.La = self.Lb = self.Lc = None

        self.current_method = "dda"

        self._build_ui()

    def _build_ui(self):
        f1 = tk.LabelFrame(self.root, text="Параметры холста", bg="#f0f0f0", padx=5, pady=5)
        f1.pack(fill=tk.X, padx=10, pady=(10, 5))
        tk.Label(f1, text="Ширина:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.entry_w = tk.Entry(f1, width=6)
        self.entry_w.insert(0, "800")
        self.entry_w.pack(side=tk.LEFT, padx=5)
        tk.Label(f1, text="Высота:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.entry_h = tk.Entry(f1, width=6)
        self.entry_h.insert(0, "500")
        self.entry_h.pack(side=tk.LEFT, padx=5)

        tk.Button(f1, text="Создать холст", command=self.create_canvas,
                  bg="#e0e0ff", width=15).pack(side=tk.LEFT, padx=10)

        f2 = tk.LabelFrame(self.root, text="Загрузка SVG", bg="#f0f0f0", padx=5, pady=5)
        f2.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(f2, text="Загрузить SVG", command=self.load_svg,
                  bg="#ffe0e0", width=15).pack(side=tk.LEFT, padx=5)

        self.label_svg_status = tk.Label(f2, text="SVG не загружен",
                                          bg="#f0f0f0", fg="red")
        self.label_svg_status.pack(side=tk.LEFT, padx=10)

        f3 = tk.LabelFrame(self.root, text="Вершины треугольника", bg="#f0f0f0", padx=5, pady=5)
        f3.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(f3, text="X1:", bg="#f0f0f0").grid(row=0, column=0, padx=3)
        self.e_x1 = tk.Entry(f3, width=6); self.e_x1.insert(0, "100"); self.e_x1.grid(row=0, column=1, padx=3)
        tk.Label(f3, text="Y1:", bg="#f0f0f0").grid(row=0, column=2, padx=3)
        self.e_y1 = tk.Entry(f3, width=6); self.e_y1.insert(0, "100"); self.e_y1.grid(row=0, column=3, padx=3)

        tk.Label(f3, text="X2:", bg="#f0f0f0").grid(row=0, column=4, padx=3)
        self.e_x2 = tk.Entry(f3, width=6); self.e_x2.insert(0, "400"); self.e_x2.grid(row=0, column=5, padx=3)
        tk.Label(f3, text="Y2:", bg="#f0f0f0").grid(row=0, column=6, padx=3)
        self.e_y2 = tk.Entry(f3, width=6); self.e_y2.insert(0, "150"); self.e_y2.grid(row=0, column=7, padx=3)

        tk.Label(f3, text="X3:", bg="#f0f0f0").grid(row=1, column=0, padx=3)
        self.e_x3 = tk.Entry(f3, width=6); self.e_x3.insert(0, "200"); self.e_x3.grid(row=1, column=1, padx=3)
        tk.Label(f3, text="Y3:", bg="#f0f0f0").grid(row=1, column=2, padx=3)
        self.e_y3 = tk.Entry(f3, width=6); self.e_y3.insert(0, "400"); self.e_y3.grid(row=1, column=3, padx=3)

        f4 = tk.LabelFrame(self.root, text="Алгоритм растеризации (нажмите для отрисовки)",
                            bg="#f0f0f0", padx=5, pady=5)
        f4.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(f4, text="ЦДА", command=lambda: self.draw_with("dda"),
                  bg="#d0e8ff", width=16, height=2).pack(side=tk.LEFT, padx=8, pady=3)
        tk.Button(f4, text="Брезенхем", command=lambda: self.draw_with("bres_float"),
                  bg="#d0ffd0", width=16, height=2).pack(side=tk.LEFT, padx=8, pady=3)
        tk.Button(f4, text="Целочисленный", command=lambda: self.draw_with("bres_int"),
                  bg="#fff0c0", width=16, height=2).pack(side=tk.LEFT, padx=8, pady=3)
        tk.Button(f4, text="Встроенные средства", command=lambda: self.draw_with("builtin"),
                  bg="#ffd0e8", width=18, height=2).pack(side=tk.LEFT, padx=8, pady=3)

        f5 = tk.LabelFrame(self.root, text="Управление", bg="#f0f0f0", padx=5, pady=5)
        f5.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(f5, text="Нарисовать SVG", command=self.draw_current,
                  bg="#d0ffd0", width=18, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(f5, text="Сохранить BMP", command=self.save_bmp,
                  bg="#ffffe0", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(f5, text="Сохранить PBM", command=self.save_pbm,
                  bg="#ffffe0", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(f5, text="Очистить", command=self.clear_canvas,
                  bg="#ffd0d0", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(f5, text="Выход", command=self.root.destroy,
                  bg="#e0e0e0", width=15).pack(side=tk.RIGHT, padx=5)

        self.canvas = tk.Canvas(self.root, width=self.canvas_width,
                                 height=self.canvas_height,
                                 bg="white", highlightthickness=1,
                                 highlightbackground="#888")
        self.canvas.pack(padx=10, pady=10)

        self.status = tk.Label(self.root,
                                text="Создайте холст, загрузите SVG и нажмите одну из кнопок алгоритма.",
                                bg="#d0d0d0", anchor="w", padx=10)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, text):
        self.status.config(text=text)
        self.root.update_idletasks()

    def create_canvas(self):
        try:
            self.canvas_width = int(self.entry_w.get())
            self.canvas_height = int(self.entry_h.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Ширина и высота должны быть числами")
            return
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.delete("all")
        self.image = PBMImage(self.canvas_width, self.canvas_height)
        self.set_status(f"Холст {self.canvas_width}x{self.canvas_height} создан")

    def load_svg(self):
        filename = filedialog.askopenfilename(
            title="Выберите SVG-файл",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            points = parse_svg_vertices(filename)
            if len(points) < 3:
                raise ValueError("Найдено меньше 3 вершин.")
            self.A, self.B, self.C = points[0], points[1], points[2]

            self.e_x1.delete(0, tk.END); self.e_x1.insert(0, str(self.A[0]))
            self.e_y1.delete(0, tk.END); self.e_y1.insert(0, str(self.A[1]))
            self.e_x2.delete(0, tk.END); self.e_x2.insert(0, str(self.B[0]))
            self.e_y2.delete(0, tk.END); self.e_y2.insert(0, str(self.B[1]))
            self.e_x3.delete(0, tk.END); self.e_x3.insert(0, str(self.C[0]))
            self.e_y3.delete(0, tk.END); self.e_y3.insert(0, str(self.C[1]))

            self.label_svg_status.config(
                text=f"SVG загружен: {os.path.basename(filename)}", fg="green")
            self.set_status(f"Загружено: A={self.A}, B={self.B}, C={self.C}")
        except Exception as e:
            self.label_svg_status.config(text="SVG не загружен", fg="red")
            messagebox.showerror("Ошибка", f"Не удалось прочитать SVG:\n{e}")

    def _get_vertices(self):
        try:
            A = (int(self.e_x1.get()), int(self.e_y1.get()))
            B = (int(self.e_x2.get()), int(self.e_y2.get()))
            C = (int(self.e_x3.get()), int(self.e_y3.get()))
            return A, B, C
        except ValueError:
            messagebox.showerror("Ошибка", "Координаты должны быть целыми числами")
            return None

    def draw_with(self, method):
        self.current_method = method

        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала нажмите 'Создать холст'")
            return

        verts = self._get_vertices()
        if verts is None:
            return

        A, B, C = verts
        self.A, self.B, self.C = A, B, C

        self.La = get_bisector_base(A, B, C)
        self.Lb = get_bisector_base(B, A, C)
        self.Lc = get_bisector_base(C, A, B)

        self.canvas.delete("all")
        self.image.clear()

        method_name = {
            "dda": "ЦДА",
            "bres_float": "Брезенхем (вещ.)",
            "bres_int": "Брезенхем (цел.)",
            "builtin": "Встроенные средства"
        }[method]

        segments = [
            (A, B, "#000000"),
            (B, C, "#000000"),
            (C, A, "#000000"),
            (self.La, self.Lb, "#0000cc"),
            (self.Lb, self.Lc, "#0000cc"),
            (self.Lc, self.La, "#0000cc"),
        ]
        for p1, p2, color in segments:
            self._draw_segment(p1, p2, method, color)

        for p, label in zip([A, B, C], ["A", "B", "C"]):
            self.canvas.create_oval(p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3,
                                     fill="green", outline="darkgreen")
            self.canvas.create_text(p[0] + 8, p[1] - 8, text=label,
                                     fill="darkgreen", font=("Arial", 10, "bold"))

        for p, label in zip([self.La, self.Lb, self.Lc], ["La", "Lb", "Lc"]):
            self.canvas.create_oval(p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3,
                                     fill="red", outline="darkred")
            self.canvas.create_text(p[0] + 8, p[1] - 8, text=label,
                                     fill="darkred", font=("Arial", 10, "bold"))

        self.set_status(f"Метод: {method_name}. "
                        f"A={A}, B={B}, C={C}; La={self.La}, Lb={self.Lb}, Lc={self.Lc}")

    def draw_current(self):
        self.draw_with(self.current_method)

    def _draw_segment(self, p1, p2, method, color="#000000"):
        x1, y1 = p1
        x2, y2 = p2

        def pixel(x, y):
            if self.image:
                self.image.set_pixel(x, y, 1)
            self.canvas.create_rectangle(x, y, x + 1, y + 1,
                                          fill=color, outline=color)

        if method == "dda":
            dda(x1, y1, x2, y2, pixel)
        elif method == "bres_float":
            bresenham_float(x1, y1, x2, y2, pixel)
        elif method == "bres_int":
            bresenham_int(x1, y1, x2, y2, pixel)
        elif method == "builtin":
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1)
            bresenham_int(x1, y1, x2, y2,
                          lambda x, y: self.image.set_pixel(x, y, 1) if self.image else None)

    def clear_canvas(self):
        self.canvas.delete("all")
        if self.image:
            self.image.clear()
        self.set_status("Холст очищен")

    def save_pbm(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала создайте холст")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".pbm", initialfile="output.pbm",
            filetypes=[("PBM files", "*.pbm"), ("All files", "*.*")])
        if not filename:
            return
        try:
            self.image.save_pbm(filename)
            messagebox.showinfo("Успех", f"Сохранено:\n{filename}")
            self.set_status(f"PBM сохранён: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def save_bmp(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала создайте холст")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".bmp", initialfile="output.bmp",
            filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")])
        if not filename:
            return
        try:
            self.image.save_bmp(filename)
            messagebox.showinfo("Успех", f"Сохранено:\n{filename}")
            self.set_status(f"BMP сохранён: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

def main():
    root = tk.Tk()
    app = Lab3App(root)
    root.mainloop()

if __name__ == "__main__":
    main()