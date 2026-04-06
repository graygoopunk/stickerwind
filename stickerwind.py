#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Многослойная наклейка на рабочий стол (GNOME)
Поддерживает:
- Сохранение состояния после перезагрузки
- Настройки: папки по умолчанию, выбор языка
- Drag-and-drop перемещение и масштабирование
- Многослойность
"""

import os
import sys
import json
import platform
import tempfile
import subprocess
import urllib.parse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import ctypes  # для Windows

# Определяем директорию для конфигурации в зависимости от ОС
if platform.system() == 'Windows':
    # Windows: используем %APPDATA%\Stickerd
    base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
    CONFIG_DIR = os.path.join(base_dir, 'Stickerd')
else:
    # Linux и другие Unix-подобные: ~/.config/sticker_app
    CONFIG_DIR = os.path.expanduser('~/.config/sticker_app')

# Полные пути к файлам
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
WALLPAPER_FILE = os.path.join(CONFIG_DIR, 'current_wallpaper.png')

# ==================== Работа с обоями ====================
def get_current_wallpaper():
    """Возвращает путь к текущим обоям (только для Linux GNOME)."""
    if platform.system() != "Linux":
        return None
    try:
        uri = subprocess.check_output(
            ['gsettings', 'get', 'org.gnome.desktop.background', 'picture-uri'],
            text=True
        ).strip().strip("'")
        if uri.startswith('file://'):
            return urllib.parse.unquote(uri[7:])
        return uri
    except Exception as e:
        print(f"Ошибка получения обоев: {e}", file=sys.stderr)
        return None

def set_wallpaper_linux(image_path):
    """Устанавливает обои в Linux (GNOME)."""
    uri = f"file://{urllib.parse.quote(image_path)}"
    try:
        subprocess.run(
            ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', uri],
            check=True
        )
        subprocess.run(
            ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', uri],
            check=True
        )
        return True
    except Exception as e:
        print(f"Ошибка установки обоев (Linux): {e}", file=sys.stderr)
        return False

def set_wallpaper_windows(image_path):
    """Устанавливает обои в Windows."""
    if not os.path.exists(image_path):
        print(f"Файл не найден: {image_path}")
        return False
    abs_path = os.path.abspath(image_path)
    # SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, путь, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
    return result != 0

def set_wallpaper_crossplatform(image_path):
    """Кросс-платформенная установка обоев."""
    system = platform.system()
    if system == "Linux":
        return set_wallpaper_linux(image_path)
    elif system == "Windows":
        return set_wallpaper_windows(image_path)
    else:
        print(f"Установка обоев не поддерживается на {system}")
        return False
# ==================== Локализация ====================
class I18n:
    _translations = {
        'ru': {
            'window_title': "Наклейки на рабочий стол",
            'select_bg': "Выбрать фон",
            'current_bg': "Текущие обои",
            'add_sticker': "Добавить наклейку",
            'delete_sticker': "Удалить выбранную",
            'apply': "Применить",
            'settings': "Настройки",
            'sticker_list': "Список наклеек",
            'move_up': "▲ Вверх",
            'move_down': "▼ Вниз",
            'settings_window': "Настройки",
            'default_sticker_folder': "Папка для наклеек по умолчанию:",
            'default_bg_folder': "Папка для фонов по умолчанию:",
            'browse': "Обзор",
            'language': "Язык интерфейса:",
            'russian': "Русский",
            'english': "English",
            'save': "Сохранить",
            'cancel': "Отмена",
            'error_title': "Ошибка",
            'info_title': "Готово",
            'apply_success': "Наклейки применены к рабочему столу!",
            'no_bg': "Нет фонового изображения.",
            'failed_bg_load': "Не удалось загрузить фон: {}",
            'failed_bg_find': "Не удалось найти текущие обои.\nВыберите фон вручную.",
            'select_sticker_file': "Выберите наклейку",
            'select_bg_file': "Выберите фоновое изображение",
            'png_filter': "PNG с прозрачностью",
            'all_images_filter': "Все изображения",
            'sticker_loaded': "{}: {} ({}x{})",
            'error_sticker_load': "Не удалось загрузить наклейку: {}",
            'error_save_result': "Не удалось сохранить результат: {}",
            'error_set_wallpaper': "Не удалось установить обои.",
            'config_saved': "Настройки сохранены.",
        },
        'en': {
            'window_title': "Stickers on Desktop",
            'select_bg': "Select Background",
            'current_bg': "Current Wallpaper",
            'add_sticker': "Add Sticker",
            'delete_sticker': "Delete Selected",
            'apply': "Apply",
            'settings': "Settings",
            'sticker_list': "Sticker List",
            'move_up': "▲ Up",
            'move_down': "▼ Down",
            'settings_window': "Settings",
            'default_sticker_folder': "Default sticker folder:",
            'default_bg_folder': "Default background folder:",
            'browse': "Browse",
            'language': "Interface language:",
            'russian': "Русский",
            'english': "English",
            'save': "Save",
            'cancel': "Cancel",
            'error_title': "Error",
            'info_title': "Success",
            'apply_success': "Stickers applied to desktop!",
            'no_bg': "No background image.",
            'failed_bg_load': "Failed to load background: {}",
            'failed_bg_find': "Could not find current wallpaper.\nPlease select background manually.",
            'select_sticker_file': "Select Sticker",
            'select_bg_file': "Select Background Image",
            'png_filter': "PNG with transparency",
            'all_images_filter': "All images",
            'sticker_loaded': "{}: {} ({}x{})",
            'error_sticker_load': "Failed to load sticker: {}",
            'error_save_result': "Failed to save result: {}",
            'error_set_wallpaper': "Failed to set wallpaper.",
            'config_saved': "Settings saved.",
        }
    }
    current_lang = 'ru'

    @classmethod
    def set_language(cls, lang):
        if lang in cls._translations:
            cls.current_lang = lang

    @classmethod
    def get(cls, key):
        return cls._translations[cls.current_lang].get(key, key)

# ==================== Класс наклейки ====================
class Sticker:
    def __init__(self, img_path, x, y, width, height):
        self.img_path = img_path
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.pil_img = Image.open(img_path).convert('RGBA')
        self.update_resized()

    def update_resized(self):
        if self.width <= 0 or self.height <= 0:
            self.resized = None
        else:
            w = int(round(self.width))
            h = int(round(self.height))
            if w > 0 and h > 0:
                self.resized = self.pil_img.resize((w, h), Image.Resampling.LANCZOS)
            else:
                self.resized = None

    def draw_on(self, canvas_img, scale=1.0):
        if self.resized is None:
            return
        x = int(self.x * scale)
        y = int(self.y * scale)
        w = int(self.width * scale)
        h = int(self.height * scale)
        if w <= 0 or h <= 0:
            return
        if scale == 1.0:
            sticker_to_paste = self.resized
        else:
            sticker_to_paste = self.pil_img.resize((w, h), Image.Resampling.LANCZOS)
        canvas_img.paste(sticker_to_paste, (x, y), sticker_to_paste)

    def to_dict(self):
        return {
            'img_path': self.img_path,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['img_path'], data['x'], data['y'], data['width'], data['height'])

# ==================== Конфигурация ====================
CONFIG_DIR = os.path.expanduser("~/.config/sticker_app")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
WALLPAPER_FILE = os.path.join(CONFIG_DIR, "current_wallpaper.png")

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_config():
    ensure_config_dir()
    default_config = {
        'sticker_folder': os.path.expanduser("~/Изображения"),
        'bg_folder': os.path.expanduser("~/Изображения"),
        'language': 'ru',
        'stickers': [],
        'bg_path': None
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in default_config:
                    if key not in data:
                        data[key] = default_config[key]
                return data
        except:
            return default_config
    return default_config

def save_config(config):
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# ==================== Основное приложение ====================
class StickerApp:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        I18n.set_language(self.config['language'])

        self.root.title(I18n.get('window_title'))
        self.root.geometry("1200x800")
        self.root.configure(bg='#2e2e2e')

        # Данные
        self.stickers = []
        self.current_sticker_index = None
        self.bg_image_path = self.config.get('bg_path')
        self.full_bg = None
        self.preview_bg = None
        self.preview_scale = 1.0

        # Drag & drop
        self.drag_type = None
        self.drag_sticker_idx = None
        self.drag_corner = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_initial_x = 0
        self.drag_initial_y = 0
        self.drag_initial_w = 0
        self.drag_initial_h = 0

        self.canvas = None
        self.canvas_img = None
        self.resize_handles = {}

        # Восстанавливаем наклейки из конфига
        for sdata in self.config.get('stickers', []):
            try:
                sticker = Sticker.from_dict(sdata)
                self.stickers.append(sticker)
            except:
                pass

        self.setup_ui()
        if self.bg_image_path and os.path.exists(self.bg_image_path):
            self._load_and_display_bg()
        else:
            self.load_background()  # попробуем текущие обои

        # Обновить список после загрузки
        self.update_listbox()
        self.refresh_preview()

    def setup_ui(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg='#3c3c3c', pady=5)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_select_bg = tk.Button(top_frame, text=I18n.get('select_bg'),
                                       command=self.select_background,
                                       bg='#5a5a5a', fg='white')
        self.btn_select_bg.pack(side=tk.LEFT, padx=5)

        self.btn_current_bg = tk.Button(top_frame, text=I18n.get('current_bg'),
                                        command=self.load_background,
                                        bg='#5a5a5a', fg='white')
        self.btn_current_bg.pack(side=tk.LEFT, padx=5)

        self.btn_add_sticker = tk.Button(top_frame, text=I18n.get('add_sticker'),
                                         command=self.add_sticker,
                                         bg='#5a5a5a', fg='white')
        self.btn_add_sticker.pack(side=tk.LEFT, padx=5)

        self.btn_delete = tk.Button(top_frame, text=I18n.get('delete_sticker'),
                                    command=self.delete_selected,
                                    bg='#5a5a5a', fg='white')
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.btn_settings = tk.Button(top_frame, text=I18n.get('settings'),
                                      command=self.open_settings,
                                      bg='#5a5a5a', fg='white')
        self.btn_settings.pack(side=tk.LEFT, padx=5)

        self.btn_apply = tk.Button(top_frame, text=I18n.get('apply'),
                                   command=self.apply_to_wallpaper,
                                   bg='#5a5a5a', fg='white')
        self.btn_apply.pack(side=tk.RIGHT, padx=5)

        # Левая панель
        left_frame = tk.Frame(self.root, bg='#2e2e2e', width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)

        self.lbl_sticker_list = tk.Label(left_frame, text=I18n.get('sticker_list'),
                                         bg='#2e2e2e', fg='white')
        self.lbl_sticker_list.pack()
        self.listbox = tk.Listbox(left_frame, bg='#3c3c3c', fg='white', selectbackground='#0078d7')
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_sticker)

        order_frame = tk.Frame(left_frame, bg='#2e2e2e')
        order_frame.pack(fill=tk.X)
        self.btn_up = tk.Button(order_frame, text=I18n.get('move_up'),
                                command=self.move_up, bg='#5a5a5a', fg='white')
        self.btn_up.pack(side=tk.LEFT, padx=2)
        self.btn_down = tk.Button(order_frame, text=I18n.get('move_down'),
                                  command=self.move_down, bg='#5a5a5a', fg='white')
        self.btn_down.pack(side=tk.LEFT, padx=2)

        # Холст
        canvas_frame = tk.Frame(self.root, bg='#1e1e1e')
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas = tk.Canvas(canvas_frame, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def update_ui_language(self):
        """Обновляет тексты всех элементов интерфейса"""
        self.root.title(I18n.get('window_title'))
        self.btn_select_bg.config(text=I18n.get('select_bg'))
        self.btn_current_bg.config(text=I18n.get('current_bg'))
        self.btn_add_sticker.config(text=I18n.get('add_sticker'))
        self.btn_delete.config(text=I18n.get('delete_sticker'))
        self.btn_settings.config(text=I18n.get('settings'))
        self.btn_apply.config(text=I18n.get('apply'))
        self.lbl_sticker_list.config(text=I18n.get('sticker_list'))
        self.btn_up.config(text=I18n.get('move_up'))
        self.btn_down.config(text=I18n.get('move_down'))

    def load_background(self):
        path = get_current_wallpaper()
        if not path or not os.path.exists(path):
            messagebox.showerror(I18n.get('error_title'), I18n.get('failed_bg_find'))
            return
        self.bg_image_path = path
        self.config['bg_path'] = path
        self._save_config()
        self._load_and_display_bg()

    def select_background(self):
        initial_dir = self.config.get('bg_folder', os.path.expanduser("~"))
        path = filedialog.askopenfilename(
            title=I18n.get('select_bg_file'),
            initialdir=initial_dir,
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
        )
        if path:
            self.bg_image_path = path
            self.config['bg_path'] = path
            self._save_config()
            self._load_and_display_bg()

    def _load_and_display_bg(self):
        try:
            self.full_bg = Image.open(self.bg_image_path).convert('RGBA')
        except Exception as e:
            messagebox.showerror(I18n.get('error_title'),
                                 I18n.get('failed_bg_load').format(str(e)))
            return

        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 1000
        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 700
        scale_w = canvas_width / self.full_bg.width
        scale_h = canvas_height / self.full_bg.height
        self.preview_scale = min(scale_w, scale_h)
        preview_size = (int(self.full_bg.width * self.preview_scale),
                        int(self.full_bg.height * self.preview_scale))
        self.preview_bg = self.full_bg.resize(preview_size, Image.Resampling.LANCZOS)
        self.refresh_preview()

    def refresh_preview(self):
        if self.preview_bg is None:
            return
        preview_img = self.preview_bg.copy()
        for sticker in self.stickers:
            sticker.draw_on(preview_img, scale=self.preview_scale)
        self.canvas_img = ImageTk.PhotoImage(preview_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_img)
        self.canvas.config(scrollregion=(0, 0, preview_img.width, preview_img.height))
        self.draw_handles()
        self.canvas.update_idletasks()

    def draw_handles(self):
        for _, ids in self.resize_handles.items():
            for hid in ids:
                self.canvas.delete(hid)
        self.resize_handles.clear()
        if self.current_sticker_index is None:
            return
        sticker = self.stickers[self.current_sticker_index]
        x1 = sticker.x * self.preview_scale
        y1 = sticker.y * self.preview_scale
        x2 = (sticker.x + sticker.width) * self.preview_scale
        y2 = (sticker.y + sticker.height) * self.preview_scale
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2)
        size = 8
        handles = []
        for cx, cy in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
            h = self.canvas.create_rectangle(cx - size//2, cy - size//2,
                                             cx + size//2, cy + size//2,
                                             fill='white', outline='black')
            handles.append(h)
        self.resize_handles[self.current_sticker_index] = handles + [rect]

    def add_sticker(self):
        initial_dir = self.config.get('sticker_folder', os.path.expanduser("~"))
        path = filedialog.askopenfilename(
            title=I18n.get('select_sticker_file'),
            initialdir=initial_dir,
            filetypes=[(I18n.get('png_filter'), "*.png"), (I18n.get('all_images_filter'), "*.*")]
        )
        if not path:
            return
        try:
            img = Image.open(path).convert('RGBA')
        except Exception as e:
            messagebox.showerror(I18n.get('error_title'),
                                 I18n.get('error_sticker_load').format(str(e)))
            return

        orig_w, orig_h = img.size
        target_w = 200
        target_h = int(orig_h * (target_w / orig_w))
        if self.full_bg:
            x = (self.full_bg.width - target_w) // 2
            y = (self.full_bg.height - target_h) // 2
        else:
            x, y = 100, 100
        sticker = Sticker(path, x, y, target_w, target_h)
        self.stickers.append(sticker)
        self.current_sticker_index = len(self.stickers) - 1
        self.update_listbox()
        self.refresh_preview()
        self._save_stickers_to_config()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, st in enumerate(self.stickers):
            name = os.path.basename(st.img_path)
            self.listbox.insert(tk.END, f"{i+1}: {name} ({int(st.width)}x{int(st.height)})")
        if self.current_sticker_index is not None:
            self.listbox.selection_set(self.current_sticker_index)

    def on_select_sticker(self, event):
        sel = self.listbox.curselection()
        if sel:
            self.current_sticker_index = sel[0]
            self.refresh_preview()

    def delete_selected(self):
        if self.current_sticker_index is not None:
            del self.stickers[self.current_sticker_index]
            if self.stickers:
                self.current_sticker_index = min(self.current_sticker_index, len(self.stickers)-1)
            else:
                self.current_sticker_index = None
            self.update_listbox()
            self.refresh_preview()
            self._save_stickers_to_config()

    def move_up(self):
        if self.current_sticker_index is not None and self.current_sticker_index > 0:
            idx = self.current_sticker_index
            self.stickers[idx], self.stickers[idx-1] = self.stickers[idx-1], self.stickers[idx]
            self.current_sticker_index = idx-1
            self.update_listbox()
            self.refresh_preview()
            self._save_stickers_to_config()

    def move_down(self):
        if self.current_sticker_index is not None and self.current_sticker_index < len(self.stickers)-1:
            idx = self.current_sticker_index
            self.stickers[idx], self.stickers[idx+1] = self.stickers[idx+1], self.stickers[idx]
            self.current_sticker_index = idx+1
            self.update_listbox()
            self.refresh_preview()
            self._save_stickers_to_config()

    # ========== Drag & Drop ==========
    def on_canvas_click(self, event):
        x, y = event.x, event.y
        # Проверка маркеров
        for idx, handles in self.resize_handles.items():
            for i, hid in enumerate(handles[:4]):
                bbox = self.canvas.bbox(hid)
                if bbox and bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                    self.drag_type = 'resize'
                    self.drag_sticker_idx = idx
                    self.drag_corner = i
                    self.drag_start_x = x
                    self.drag_start_y = y
                    sticker = self.stickers[idx]
                    self.drag_initial_x = sticker.x
                    self.drag_initial_y = sticker.y
                    self.drag_initial_w = sticker.width
                    self.drag_initial_h = sticker.height
                    self.current_sticker_index = idx
                    self.update_listbox()
                    self.refresh_preview()
                    return
        # Проверка наклейки
        for i, st in enumerate(self.stickers):
            x1 = st.x * self.preview_scale
            y1 = st.y * self.preview_scale
            x2 = (st.x + st.width) * self.preview_scale
            y2 = (st.y + st.height) * self.preview_scale
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.drag_type = 'move'
                self.drag_sticker_idx = i
                self.drag_start_x = x
                self.drag_start_y = y
                self.drag_initial_x = st.x
                self.drag_initial_y = st.y
                self.current_sticker_index = i
                self.update_listbox()
                self.refresh_preview()
                return

    def on_drag(self, event):
        if self.drag_type is None or self.drag_sticker_idx is None:
            return
        x, y = event.x, event.y
        sticker = self.stickers[self.drag_sticker_idx]

        if self.drag_type == 'move':
            dx_preview = x - self.drag_start_x
            dy_preview = y - self.drag_start_y
            dx_full = dx_preview / self.preview_scale
            dy_full = dy_preview / self.preview_scale
            sticker.x = self.drag_initial_x + dx_full
            sticker.y = self.drag_initial_y + dy_full
            self.refresh_preview()
            self.drag_start_x = x
            self.drag_start_y = y
            self.drag_initial_x = sticker.x
            self.drag_initial_y = sticker.y
            self._save_stickers_to_config()

        elif self.drag_type == 'resize':
            dx = x - self.drag_start_x
            dy = y - self.drag_start_y
            dx_full = dx / self.preview_scale
            dy_full = dy / self.preview_scale
            corner = self.drag_corner
            if corner == 0:  # верхний левый
                new_x = self.drag_initial_x + dx_full
                new_y = self.drag_initial_y + dy_full
                new_w = self.drag_initial_w - dx_full
                new_h = self.drag_initial_h - dy_full
            elif corner == 1:  # верхний правый
                new_x = self.drag_initial_x
                new_y = self.drag_initial_y + dy_full
                new_w = self.drag_initial_w + dx_full
                new_h = self.drag_initial_h - dy_full
            elif corner == 2:  # нижний левый
                new_x = self.drag_initial_x + dx_full
                new_y = self.drag_initial_y
                new_w = self.drag_initial_w - dx_full
                new_h = self.drag_initial_h + dy_full
            else:  # нижний правый
                new_x = self.drag_initial_x
                new_y = self.drag_initial_y
                new_w = self.drag_initial_w + dx_full
                new_h = self.drag_initial_h + dy_full

            # Ограничения
            if new_w < 5:
                new_w = 5
                if corner in (0, 2):
                    new_x = self.drag_initial_x + self.drag_initial_w - 5
            if new_h < 5:
                new_h = 5
                if corner in (0, 1):
                    new_y = self.drag_initial_y + self.drag_initial_h - 5

            sticker.x = new_x
            sticker.y = new_y
            sticker.width = new_w
            sticker.height = new_h
            sticker.update_resized()
            self.refresh_preview()
            self.drag_start_x = x
            self.drag_start_y = y
            self.drag_initial_x = sticker.x
            self.drag_initial_y = sticker.y
            self.drag_initial_w = sticker.width
            self.drag_initial_h = sticker.height
            self._save_stickers_to_config()

    def on_release(self, event):
        self.drag_type = None
        self.drag_sticker_idx = None
        self.drag_corner = None

    # ========== Сохранение конфигурации ==========
    def _save_stickers_to_config(self):
        self.config['stickers'] = [st.to_dict() for st in self.stickers]
        self._save_config()

    def _save_config(self):
        self.config['bg_path'] = self.bg_image_path
        save_config(self.config)

    # ========== Применение к рабочим обоям ==========
    def apply_to_wallpaper(self):
        if self.full_bg is None:
            messagebox.showerror(I18n.get('error_title'), I18n.get('no_bg'))
            return
        result = self.full_bg.copy()
        for sticker in self.stickers:
            sticker.draw_on(result, scale=1.0)
        ensure_config_dir()
        try:
            result.save(WALLPAPER_FILE, 'PNG')
        except Exception as e:
            messagebox.showerror(I18n.get('error_title'),
                                 I18n.get('error_save_result').format(str(e)))
            return
        if set_wallpaper_crossplatform(WALLPAPER_FILE):
            messagebox.showinfo(I18n.get('info_title'), I18n.get('apply_success'))
        else:
            messagebox.showerror(I18n.get('error_title'), I18n.get('error_set_wallpaper'))

    # ========== Окно настроек ==========
    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title(I18n.get('settings_window'))
        settings_win.geometry("500x350")
        settings_win.configure(bg='#2e2e2e')
        settings_win.transient(self.root)
        settings_win.grab_set()

        # Папка для наклеек
        tk.Label(settings_win, text=I18n.get('default_sticker_folder'),
                 bg='#2e2e2e', fg='white').pack(pady=(10,0))
        sticker_frame = tk.Frame(settings_win, bg='#2e2e2e')
        sticker_frame.pack(fill=tk.X, padx=20, pady=5)
        sticker_entry = tk.Entry(sticker_frame, width=40)
        sticker_entry.insert(0, self.config.get('sticker_folder', ''))
        sticker_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        def browse_sticker():
            d = filedialog.askdirectory(initialdir=sticker_entry.get())
            if d:
                sticker_entry.delete(0, tk.END)
                sticker_entry.insert(0, d)
        tk.Button(sticker_frame, text=I18n.get('browse'), command=browse_sticker,
                  bg='#5a5a5a', fg='white').pack(side=tk.RIGHT, padx=(5,0))

        # Папка для фонов
        tk.Label(settings_win, text=I18n.get('default_bg_folder'),
                 bg='#2e2e2e', fg='white').pack(pady=(10,0))
        bg_frame = tk.Frame(settings_win, bg='#2e2e2e')
        bg_frame.pack(fill=tk.X, padx=20, pady=5)
        bg_entry = tk.Entry(bg_frame, width=40)
        bg_entry.insert(0, self.config.get('bg_folder', ''))
        bg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        def browse_bg():
            d = filedialog.askdirectory(initialdir=bg_entry.get())
            if d:
                bg_entry.delete(0, tk.END)
                bg_entry.insert(0, d)
        tk.Button(bg_frame, text=I18n.get('browse'), command=browse_bg,
                  bg='#5a5a5a', fg='white').pack(side=tk.RIGHT, padx=(5,0))

        # Язык
        tk.Label(settings_win, text=I18n.get('language'),
                 bg='#2e2e2e', fg='white').pack(pady=(10,0))
        lang_var = tk.StringVar(value=self.config.get('language', 'ru'))
        lang_frame = tk.Frame(settings_win, bg='#2e2e2e')
        lang_frame.pack(pady=5)
        tk.Radiobutton(lang_frame, text=I18n.get('russian'), variable=lang_var,
                       value='ru', bg='#2e2e2e', fg='white', selectcolor='#2e2e2e').pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(lang_frame, text=I18n.get('english'), variable=lang_var,
                       value='en', bg='#2e2e2e', fg='white', selectcolor='#2e2e2e').pack(side=tk.LEFT, padx=10)

        def save_settings():
            self.config['sticker_folder'] = sticker_entry.get()
            self.config['bg_folder'] = bg_entry.get()
            new_lang = lang_var.get()
            if new_lang != self.config.get('language'):
                self.config['language'] = new_lang
                I18n.set_language(new_lang)
                self.update_ui_language()
            self._save_config()
            settings_win.destroy()
            messagebox.showinfo(I18n.get('info_title'), I18n.get('config_saved'))

        btn_frame = tk.Frame(settings_win, bg='#2e2e2e')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text=I18n.get('save'), command=save_settings,
                  bg='#5a5a5a', fg='white').pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text=I18n.get('cancel'), command=settings_win.destroy,
                  bg='#5a5a5a', fg='white').pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = tk.Tk(className='Stickerd')
    root.title("Stickerd")
    app = StickerApp(root)
    root.mainloop()
