from PyQt5 import QtWidgets, QtCore
from widgets.switch_button import SwitchButton
import time
import keyboard
import pyautogui
import os
import pygetwindow as gw

class CowPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.worker: CowWorker | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        switch_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Авто‑Коровы")
        label.setStyleSheet("color: white; font-size: 16px;background: none;")
        self.switch = SwitchButton()
        self.switch.clicked.connect(self.toggle_script)

        switch_layout.addWidget(label)
        switch_layout.addStretch()
        switch_layout.addWidget(self.switch)
        layout.addLayout(switch_layout)

        layout.addStretch()

        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: black; color: white; font-family: monospace;")
        self.log_output.setFixedHeight(200)
        layout.addWidget(self.log_output)

    def toggle_script(self, checked: bool):
        if checked:
            self.log_output.clear()
            self.worker = CowWorker()
            self.worker.log_signal.connect(self._append_log)
            self.worker.start()
        else:
            self._stop_worker()

    def _stop_worker(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
            self._append_log("[■] Скрипт остановлен.")
            self.switch.setChecked(False)

    def _append_log(self, text: str):
        self.log_output.append(text)


class CowWorker(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = True

    def stop(self):
        self._running = False

    def log(self, message: str):
        timestamp = time.strftime("[%H:%M:%S]")
        full_message = f"{timestamp} {message}"
        try:
            with open("logs.txt", "a", encoding="utf-8") as fp:
                fp.write(full_message + "\n")
        except OSError:
            pass
        self.log_signal.emit(full_message)

    def _image_visible(self, filename: str, confidence: float = 0.95) -> bool:
        try:
            return pyautogui.locateOnScreen(filename, confidence=confidence) is not None
        except Exception as e:
            self.log(f"[Ошибка] Не удалось найти {filename}: {e}")
            return False

    def _pixel_color_visible(self, target_rgb: tuple[int, int, int], tolerance: int = 10) -> bool:
        try:
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size
            pixels = screenshot.load()

            for y in range(0, height, 10):  # шаг 10 пикселей по вертикали
                for x in range(0, width, 10):  # шаг 10 пикселей по горизонтали
                    r, g, b = pixels[x, y]
                    if (
                        abs(r - target_rgb[0]) <= tolerance and
                        abs(g - target_rgb[1]) <= tolerance and
                        abs(b - target_rgb[2]) <= tolerance
                    ):
                        return True
            return False
        except Exception as e:
            self.log(f"[Ошибка] Не удалось просканировать экран на цвет: {e}")
            return False

    @staticmethod
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

    def run(self):
        self.log("Скрипт коровы запущен (быстрый режим)")

        while self._running:
            # Быстрая проверка активности окна RAGE
            if not self._is_rage_mp_active():
                time.sleep(0.5)  # Короткая пауза, если окно не активно
                continue

            # Ускоренная проверка A и D (без лишних задержек)
            a_visible = self._image_visible("assets/cow/aForCow.png")
            d_visible = self._image_visible("assets/cow/dForCow.png")

            if a_visible:
                #keyboard.press("a")
                keyboard.release("a")  # Максимально быстрое нажатие
                self.log("НАЖАЛ A")
                time.sleep(0.1)  # Минимальная задержка
            elif d_visible:
                #keyboard.press("d")
                keyboard.release("d")
                self.log("НАЖАЛ d")
                time.sleep(0.1)
            else:
                # Если ничего не найдено — жмём E очень быстро
                keyboard.press("e")
                keyboard.release("e")
                time.sleep(0.1)  # Чуть больше, чтобы игра успела обработать


        self.log("Скрипт коровы завершён")