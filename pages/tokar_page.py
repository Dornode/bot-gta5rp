# -------------------------------------------------------------
#  Tokar Autofollow — отслеживает указанный предмет по шаблону
# -------------------------------------------------------------
import time
import traceback
import os

import cv2
import numpy as np
from mss import mss
import win32api
import win32con
import keyboard
import pygetwindow as gw

from PyQt5 import QtWidgets, QtCore

# -------------------------------------------------------------
#                         Детект по шаблону
# -------------------------------------------------------------
def detect_template_center(template_img, monitor_index: int = 1, threshold: float = 0.85):
    try:
        with mss() as sct:
            screenshot = np.array(sct.grab(sct.monitors[monitor_index]))

        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)
        template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            h, w = template_gray.shape
            cx, cy = max_loc[0] + w // 2, max_loc[1] + h // 2
            if cx < 300 and cy < 300:
                return None
            return cx, cy
        return None

    except Exception:
        print("[Ошибка detect_template_center]:", traceback.format_exc())
        return None

def move_cursor_to(x: int, y: int):
    win32api.SetCursorPos((x, y))

# -------------------------------------------------------------
#                       QThread‑worker для GUI
# -------------------------------------------------------------
class TokarWorker(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    counter_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True
        self.frames = 0

        # Загружаем шаблон
        self.template = cv2.imread("assets\demorgan\i3.png")
        if self.template is None:
            raise FileNotFoundError("Файл шаблона 'template.png' не найден рядом со скриптом.")

    def log(self, msg: str):
        ts = time.strftime("[%H:%M:%S]")
        self.log_signal.emit(f"{ts} {msg}")

    def stop(self):
        self.running = False

    def run(self):
        self.log("Скрипт запущен. Нажми F10 для остановки.")
        try:
            while self.running:
                if keyboard.is_pressed("f10"):
                    self.log("F10 — остановка.")
                    break

                if not _is_rage_mp_active():
                    self.log("Окно RAGE MP не активно — пауза.")
                    time.sleep(0.3)
                    continue

                pos = detect_template_center(self.template)
                if pos:
                    move_cursor_to(*pos)
                    self.log(f"→ курсор перемещён в {pos}")
                else:
                    self.log("шаблон не найден")

                self.frames += 1
                if self.frames % 10 == 0:
                    self.counter_signal.emit(self.frames)

                time.sleep(0.03)

        except Exception:
            self.log("[Критическая ошибка]\n" + traceback.format_exc())
        finally:
            self.running = False
            self.log("Поток завершён.")

# -------------------------------------------------------------
#                 Проверка активности окна RAGE MP
# -------------------------------------------------------------
def _is_rage_mp_active() -> bool:
    active = gw.getActiveWindow()
    if not active:
        return False

    replacements = {
        "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
        "м": "m", "т": "t", "н": "h", "в": "b", "к": "k",
    }
    normalized = "".join(replacements.get(ch, ch) for ch in active.title.casefold())
    return "multi" in normalized

# -------------------------------------------------------------
#                        Простое GUI‑окно
# -------------------------------------------------------------
class TokarPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.worker: TokarWorker | None = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Токарь — авто‑слежение по шаблону")
        self.resize(420, 350)
        self.setStyleSheet("background:#212121;color:white;")

        vbox = QtWidgets.QVBoxLayout(self)

        # header
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Токарь: автонаведение на предмет")
        title.setStyleSheet("font-size:16px;")
        header.addWidget(title)
        header.addStretch()

        self.toggle_btn = QtWidgets.QPushButton("Старт / Стоп")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self._toggle)
        header.addWidget(self.toggle_btn)
        vbox.addLayout(header)

        self.counter_lbl = QtWidgets.QLabel("Кадров обработано: 0")
        self.counter_lbl.setStyleSheet("font-size:14px;")
        vbox.addWidget(self.counter_lbl)

        self.log_field = QtWidgets.QTextEdit(readOnly=True)
        self.log_field.setStyleSheet("background:#000;color:#0f0;font-family:monospace;font-size:12px;")
        self.log_field.setFixedHeight(220)
        vbox.addWidget(self.log_field)
        vbox.addStretch()

    def _toggle(self, checked: bool):
        if checked:
            self.log_field.clear()
            try:
                self.worker = TokarWorker()
                self.worker.log_signal.connect(self.log_field.append)
                self.worker.counter_signal.connect(lambda n: self.counter_lbl.setText(f"Кадров обработано: {n}"))
                self.worker.start()
            except Exception as e:
                self.log_field.append(f"[Ошибка запуска] {e}")
                self.toggle_btn.setChecked(False)
        else:
            if self.worker:
                self.worker.stop()
                self.worker.wait()
                self.worker = None
            self.log_field.append("[■] Остановлено.")
            self.toggle_btn.setChecked(False)

# -------------------------------------------------------------
#                                MAIN
# -------------------------------------------------------------
if __name__ == "__main__":
    os.environ["QT_FONT_DPI"] = "96"
    app = QtWidgets.QApplication([])
    win = TokarPage()
    win.show()
    app.exec_()
