import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"
MIN_LENGTH = 4
MAX_LENGTH = 64

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("550x680")
        self.history = []
        
        self.load_history()
        self.setup_ui()

    # ================== ЗАГРУЗКА / СОХРАНЕНИЕ ИСТОРИИ ==================
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                self.history = []
                messagebox.showwarning("Предупреждение", "Файл истории повреждён. Создана новая история.")

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    # ================== ИНТЕРФЕЙС ==================
    def setup_ui(self):
        padding = {"padx": 10, "pady": 5}
        
        # 1. Ползунок длины
        ttk.Label(self.root, text="Длина пароля:").pack(**padding)
        self.length_var = tk.IntVar(value=12)
        self.scale = ttk.Scale(self.root, from_=MIN_LENGTH, to=MAX_LENGTH, variable=self.length_var, orient="horizontal")
        self.scale.pack(fill="x", **padding)
        self.length_label = ttk.Label(self.root, text="12 символов")
        self.length_label.pack(**padding)
        self.scale.configure(command=self.update_length_label)

        # 2. Чекбоксы символов
        ttk.Label(self.root, text="Набор символов:").pack(**padding)
        frame_checks = ttk.Frame(self.root)
        frame_checks.pack(**padding)

        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)

        ttk.Checkbutton(frame_checks, text="Цифры (0-9)", variable=self.use_digits).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(frame_checks, text="Буквы (a-Z)", variable=self.use_letters).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(frame_checks, text="Спецсимволы (!@#...)", variable=self.use_special).grid(row=1, column=0, sticky="w")

        # 3. Кнопка генерации и поле вывода
        ttk.Button(self.root, text="Сгенерировать пароль", command=self.generate_password).pack(fill="x", **padding)
        
        self.password_var = tk.StringVar()
        self.output_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 14), state="readonly")
        self.output_entry.pack(fill="x", **padding)

        ttk.Button(self.root, text="📋 Копировать в буфер", command=self.copy_to_clipboard).pack(**padding)

        # 4. Таблица истории
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(self.root, text="История генераций:").pack(**padding)

        columns = ("timestamp", "password", "length")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        self.tree.heading("timestamp", text="Время")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.column("timestamp", width=140)
        self.tree.column("password", width=250)
        self.tree.column("length", width=60, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.update_table()

    def update_length_label(self, value):
        self.length_label.config(text=f"{int(value)} символов")

    # ================== ЛОГИКА ==================
    def generate_password(self):
        length = self.length_var.get()
        
        # Валидация длины
        if not (MIN_LENGTH <= length <= MAX_LENGTH):
            messagebox.showerror("Ошибка", f"Длина должна быть от {MIN_LENGTH} до {MAX_LENGTH}.")
            return

        # Валидация чекбоксов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_special.get()):
            messagebox.showwarning("Внимание", "Выберите хотя бы один тип символов!")
            return

        # Формирование пула символов
        chars = ""
        if self.use_digits.get(): chars += string.digits
        if self.use_letters.get(): chars += string.ascii_letters
        if self.use_special.get(): chars += string.punctuation

        # Генерация (используем библиотеку random, как в задании)
        password = "".join(random.choice(chars) for _ in range(length))
        
        # Отображение
        self.password_var.set(password)
        self.output_entry.config(state="normal")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, password)
        self.output_entry.config(state="readonly")

        # Сохранение в историю
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": length
        }
        self.history.insert(0, record)  # Новые сверху
        self.save_history()
        self.update_table()

    def update_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Заполнение
        for rec in self.history:
            self.tree.insert("", "end", values=(rec["timestamp"], rec["password"], rec["length"]))

    def copy_to_clipboard(self):
        pwd = self.password_var.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте пароль.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
