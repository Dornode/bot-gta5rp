from PyQt5 import QtWidgets, QtCore
from widgets.switch_button import SwitchButton
import os
import time
import traceback
import pyautogui
import keyboard
from pyautogui import ImageNotFoundException


class StroykaPage(QtWidgets.QWidget):
    """GUI‑страница «Стройка Авто‑Спам»."""

    def __init__(self):
        super().__init__()
        self.worker: StroykaWorker | None = None
        self._init_ui()

    # ---------------- UI ---------------- #
    @staticmethod
    def _make_label(text: str, size: int) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(f"color:white;font-size:{size}px;")
        return lbl

    def _init_ui(self):
        lay = QtWidgets.QVBoxLayout(self)

        head = QtWidgets.QHBoxLayout()
        head.addWidget(self._make_label("Стройка Авто‑Спам", 16))
        head.addStretch()
        self.switch = SwitchButton(); self.switch.clicked.connect(self._toggle)
        head.addWidget(self.switch)
        lay.addLayout(head)

        self.counter = self._make_label("Счётчик: 0", 14)
        lay.addWidget(self.counter); lay.addStretch()

        self.log_field = QtWidgets.QTextEdit(readOnly=True)
        self.log_field.setStyleSheet("background:#000;color:#fff;font-family:monospace;")
        self.log_field.setFixedHeight(240)
        lay.addWidget(self.log_field)

    # ------------- slots -------------- #
    def _toggle(self, checked: bool):
        if checked:
            self.log_field.clear()
            self.worker = StroykaWorker()
            self.worker.log_signal.connect(self.log_field.append)
            self.worker.counter_signal.connect(lambda v: self.counter.setText(f"Счётчик: {v}"))
            self.worker.start()
        else:
            if self.worker:
                self.worker.stop(); self.worker.wait(); self.worker = None
            self.log_field.append("[■] Скрипт остановлен.")
            self.switch.setChecked(False)


class StroykaWorker(QtCore.QThread):
    """Поток: ищет 3 картинки, спамит клавиши и пишет лог в GUI + файл."""

    log_signal = QtCore.pyqtSignal(str)
    counter_signal = QtCore.pyqtSignal(int)

    CONFIDENCE = 0.95
    SPAM_DELAY = 0.03
    LOOP_SLEEP = 0.10

    def __init__(self):
        super().__init__()
        self.running = True; self.count = 0

        try: import cv2; self.cv2_ok = True
        except ImportError: self.cv2_ok = False

        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.img_key = {
            os.path.join(base, "assets", "stroyka", "image1.png"): "e",
            os.path.join(base, "assets", "stroyka", "image2.png"): "y",
            os.path.join(base, "assets", "stroyka", "image3.png"): "f",
        }
        self._shown = {p: False for p in self.img_key}
        self._visible = {p: False for p in self.img_key}

    # ---------- util log (ваша версия) ---------- #
    def log(self, message: str):
        timestamp = time.strftime("[%H:%M:%S]")
        full_message = f"{timestamp} {message}"
        try:
            with open("logs.txt", "a", encoding="utf-8") as fp:
                fp.write(full_message + "\n")
        except OSError:
            pass  # если файл недоступен – выводим только в GUI
        self.log_signal.emit(full_message)

    # -------- безопасный поиск -------- #
    def safe_locate(self, path: str):
        try:
            return pyautogui.locateOnScreen(path, confidence=self.CONFIDENCE)
        except ImageNotFoundException:
            return None
        except Exception:
            self.log(f"[Ошибка] locate {os.path.basename(path)}:\n{traceback.format_exc()}")
            return None

    def stop(self):
        self.running = False

    # ------------- run ------------- #
    def run(self):
        if not self.cv2_ok:
            self.log("[Ошибка] OpenCV не установлен."); return
        for p in self.img_key:
            if not os.path.exists(p):
                self.log(f"[Ошибка] Файл не найден: {p}"); return

        self.log("Скрипт запущен.")
        try:
            while self.running:
                for path, key in self.img_key.items():
                    name = os.path.basename(path)
                    if self.safe_locate(path):
                        if not self._visible[path]:
                            self._visible[path] = True; self._shown[path] = False
                            self.count += 1; self.counter_signal.emit(self.count)
                            self.log(f"[✓] Найдено {name} → спам '{key}'")
                        while self.running and self.safe_locate(path):
                            keyboard.press_and_release(key); time.sleep(self.SPAM_DELAY)
                        self._visible[path] = False
                    else:
                        self._visible[path] = False
                        if not self._shown[path]:
                            self.log(f"Ищу {name} (conf={self.CONFIDENCE})"); self._shown[path] = True
                time.sleep(self.LOOP_SLEEP)
        except Exception:
            self.log(f"[Критическая ошибка]\n{traceback.format_exc()}")
        finally:
            self.running = False
