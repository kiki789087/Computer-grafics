import math
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
class ImageTransformApp:
  def __init__(self, root):
    self.root = root
    self.root.title("ЛР №6: Геометрические преобразования (Вариант 20)")
    self.root.geometry("1050x680")
    self.root.configure(bg="#f0f0f0")
    self.img_original = None
    self.img_affine_direct = None
    self.img_affine_restored = None
    self.img_func = None
    self.frame_orig = tk.Frame(
        root,
        bg="white",
        width=300,
        height=240,
        highlightbackground="gray",
        highlightthickness=1,
    )
    self.frame_orig.place(x=20, y=50)
    self.frame_orig.pack_propagate(False)
    tk.Label(
        root, text="1. Оригинал", bg="#f0f0f0", font=("Arial", 10, "bold")
    ).place(x=110, y=20)
    self.frame_aff = tk.Frame(
        root,
        bg="white",
        width=300,
        height=240,
        highlightbackground="gray",
        highlightthickness=1,
    )
    self.frame_aff.place(x=360, y=50)
    self.frame_aff.pack_propagate(False)
    tk.Label(
        root,
        text="2. Прямое аффинное (Отражение + Скос)",
        bg="#f0f0f0",
        font=("Arial", 10, "bold"),
    ).place(x=385, y=20)
    self.frame_rest = tk.Frame(
        root,
        bg="white",
        width=300,
        height=240,
        highlightbackground="gray",
        highlightthickness=1,
    )
    self.frame_rest.place(x=700, y=50)
    self.frame_rest.pack_propagate(False)
    tk.Label(
        root,
        text="3. Обратное аффинное (Восстановление)",
        bg="#f0f0f0",
        font=("Arial", 10, "bold"),
    ).place(x=715, y=20)
    self.frame_func = tk.Frame(
        root,
        bg="white",
        width=300,
        height=240,
        highlightbackground="gray",
        highlightthickness=1,
    )
    self.frame_func.place(x=360, y=370)
    self.frame_func.pack_propagate(False)
    tk.Label(
        root,
        text="4. Функциональное (i = x² / y', j = y')",
        bg="#f0f0f0",
        font=("Arial", 10, "bold"),
    ).place(x=380, y=345)
    self.btn_open = tk.Button(
        root,
        text="Загрузить изображение",
        width=25,
        bg="#e0e0e0",
        command=self.load_image,
    )
    self.btn_open.place(x=50, y=370)

    self.btn_affine = tk.Button(
        root,
        text="Прямое аффинное",
        width=25,
        bg="#e0e0e0",
        command=self.apply_affine_direct,
    )
    self.btn_affine.place(x=50, y=420)

    self.btn_restore = tk.Button(
        root,
        text="Обратное (Восстановить)",
        width=25,
        bg="#e0e0e0",
        command=self.apply_affine_inverse,
    )
    self.btn_restore.place(x=50, y=470)
    self.btn_func = tk.Button(
        root,
        text="Функциональное преобр.",
        width=25,
        bg="#e0e0e0",
        command=self.apply_functional,
    )
    self.btn_func.place(x=50, y=520)
    self.btn_save = tk.Button(
        root,
        text="Сохранить активный результат",
        width=28,
        bg="#d0f0d0",
        command=self.save_image,
    )
    self.btn_save.place(x=700, y=520)
    tk.Label(root, text="Коэффициент скоса (k):", bg="#f0f0f0").place(
        x=50, y=580
    )
    self.entry_k = tk.Entry(root, width=10)
    self.entry_k.insert(0, "0.5")
    self.entry_k.place(x=190, y=580)
  def show_image(self, img, frame):
    if not img:
      return
    try:
      img_copy = img.copy()
      img_copy.thumbnail((290, 230), Image.Resampling.LANCZOS)
      tk_img = ImageTk.PhotoImage(img_copy)
      for widget in frame.winfo_children():
        widget.destroy()
      lbl = tk.Label(frame, image=tk_img, bg="white")
      lbl.image = tk_img
      lbl.pack(expand=True)
    except Exception as e:
      messagebox.showerror("Ошибка", f"Ошибка отображения: {e}")
  def load_image(self):
    path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.ppm *.png *.jpg *.jpeg *.bmp"),
            ("All Files", "*.*"),
        ]
    )
    if path:
      self.img_original = Image.open(path).convert("RGB")
      self.show_image(self.img_original, self.frame_orig)
      self.img_affine_direct = None
      self.img_affine_restored = None
      self.img_func = None
      for f in [self.frame_aff, self.frame_rest, self.frame_func]:
        for widget in f.winfo_children():
          widget.destroy()
  def apply_affine_direct(self):
    if not self.img_original:
      messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
      return
    try:
      k = float(self.entry_k.get())
    except ValueError:
      messagebox.showerror(
          "Ошибка", "Коэффициент скоса должен быть числовым значением!"
      )
      return
    w, h = self.img_original.size
    new_w, new_h = int(w * 1.6), int(
        h * 1.4
    )
    src_pixels = self.img_original.load()
    res_img = Image.new("RGB", (new_w, new_h), "white")
    res_pixels = res_img.load()
    cx_src, cy_src = w / 2.0, h / 2.0
    cx_res, cy_res = new_w / 2.0, new_h / 2.0
    for x_src in range(w):
      for y_src in range(h):
        x_c = x_src - cx_src
        y_c = y_src - cy_src
        X_res = -x_c + k * y_c
        Y_res = y_c
        x_res = int(X_res + cx_res)
        y_res = int(Y_res + cy_res)
        if 0 <= x_res < new_w and 0 <= y_res < new_h:
          res_pixels[x_res, y_res] = src_pixels[x_src, y_src]
    self.img_affine_direct = res_img
    self.show_image(self.img_affine_direct, self.frame_aff)
  def apply_affine_inverse(self):
    if not self.img_affine_direct:
      messagebox.showwarning(
          "Внимание", "Сначала выполните прямое аффинное преобразование!"
      )
      return
    try:
      k = float(self.entry_k.get())
    except ValueError:
      messagebox.showerror("Ошибка", "Введите корректный коэффициент скоса!")
      return
    w_res, h_res = self.img_affine_direct.size
    src_pixels = self.img_affine_direct.load()
    w_orig, h_orig = self.img_original.size
    res_img = Image.new("RGB", (w_orig, h_orig), "white")
    res_pixels = res_img.load()
    cx_src, cy_src = w_res / 2.0, h_res / 2.0
    cx_res, cy_res = w_orig / 2.0, h_orig / 2.0
    for x_res in range(w_orig):
      for y_res in range(h_orig):
        X = x_res - cx_res
        Y = y_res - cy_res
        y_c = Y
        x_c = -X + k * y_c
        x_src = int(x_c + cx_src)
        y_src = int(y_c + cy_src)
        if 0 <= x_src < w_res and 0 <= y_src < h_res:
          res_pixels[x_res, y_res] = src_pixels[x_src, y_src]
    self.img_affine_restored = res_img
    self.show_image(self.img_affine_restored, self.frame_rest)
  def apply_functional(self):
    if not self.img_original:
      messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
      return
    w, h = self.img_original.size
    src_pixels = self.img_original.load()
    new_w, new_h = w * 2, h * 2
    res_img = Image.new("RGB", (new_w, new_h), "white")
    res_pixels = res_img.load()
    cx_src, cy_src = w / 2.0, h / 2.0
    cx_res, cy_res = new_w / 2.0, new_h / 2.0
    for i in range(new_w):
      for j in range(new_h):
        I_c = i - cx_res
        J_c = j - cy_res
        y_orig = J_c
        val = I_c * y_orig
        if val >= 0:
          x_orig = math.sqrt(val)
          for x_sign in [1, -1]:
            x_s = int(x_sign * x_orig + cx_src)
            y_s = int(y_orig + cy_src)

            if 0 <= x_s < w and 0 <= y_s < h:
              res_pixels[i, j] = src_pixels[x_s, y_s]
              break
    self.img_func = res_img
    self.show_image(self.img_func, self.frame_func)
  def save_image(self):
    img_to_save = self.img_func or self.img_affine_restored or self.img_affine_direct
    if not img_to_save:
      messagebox.showwarning("Внимание", "Нет готового изображения для сохранения!")
      return
    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png"),
            ("Netpbm PPM", "*.ppm"),
            ("JPEG Image", "*.jpg"),
        ],
    )
    if path:
      img_to_save.save(path)
      messagebox.showinfo("Успех", "Изображение успешно сохранено!")
if __name__ == "__main__":
  root = tk.Tk()
  app = ImageTransformApp(root)
  root.mainloop()