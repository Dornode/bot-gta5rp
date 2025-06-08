from PyQt5 import QtWidgets, QtCore
from widgets.switch_button import SwitchButton
import pygetwindow as gw
import pyautogui
import time
import keyboard
import os
from widgets.logger import CommonLogger

class GotovkaPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.worker: GotovkaWorker | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        switch_layout = QtWidgets.QHBoxLayout()
        self.switch = SwitchButton()
        self.switch.clicked.connect(self.toggle_script)

        switch_layout.addWidget(CommonLogger._make_label("Готовка", 16))
        switch_layout.addStretch()
        switch_layout.addWidget(self.switch)
        layout.addLayout(switch_layout)

        dish_layout = QtWidgets.QHBoxLayout()
        dish_label = QtWidgets.QLabel("Выберите блюдо:")
        dish_label.setStyleSheet("color: white; font-size: 14px; background: none;")

        self.dish_combo = QtWidgets.QComboBox()
        self.dish_combo.addItems(["Фруктовое смузи", "хуй"])
        self.dish_combo.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
        self.dish_combo.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                min-width: 120px;
                
            }

            QComboBox QAbstractItemView {
                background-color: #333;
                color: white;
            }
        """)

        dish_layout.addWidget(dish_label)
        dish_layout.addWidget(self.dish_combo)
        dish_layout.addStretch()
        layout.addLayout(dish_layout)

        layout.addStretch()
        self.log_output = CommonLogger.create_log_field(layout)

    def toggle_script(self, checked: bool):
        if checked:
            self.log_output.clear()
            self.worker = GotovkaWorker()
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


class GotovkaWorker(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = True

    def stop(self):
        self._running = False

    def log(self, message: str):
        CommonLogger.log(message, self.log_signal)

    def _drag_image(self, image_path, offset_x, offset_y):
        location = pyautogui.locateCenterOnScreen(image_path, confidence=0.85)
        if location:
            self.log(f"[✓] Найдено изображение: {os.path.basename(image_path)} — перемещение.")
            pyautogui.moveTo(location.x, location.y)
            pyautogui.mouseDown()
            pyautogui.moveRel(offset_x, offset_y, duration=0.1)
            pyautogui.mouseUp()
            return True
        else:
            self.log(f"[×] Изображение не найдено: {os.path.basename(image_path)}.")
            return False

    def _click_image(self, image_path):
        location = pyautogui.locateCenterOnScreen(image_path, confidence=0.85)
        if location:
            pyautogui.click(location)
            self.log(f"[✓] Клик по изображению: {os.path.basename(image_path)}.")
            return True
        else:
            self.log(f"[×] Изображение не найдено для клика: {os.path.basename(image_path)}.")
            return False

    def run(self):
        self.log("[→] Скрипт готовки запущен.")
        rage_window_missing = True
        try:
            while self._running:
                if not CommonLogger.is_rage_mp_active():
                    if rage_window_missing:
                        self.log("Окно RAGE Multiplayer не активно. Ожидание...")
                        rage_window_missing = False
                    time.sleep(1)
                    continue

                found1 = self._drag_image("assets/cook/ovoshi.png", -250, 0)
                found2 = self._drag_image("assets/cook/voda2.png", -250, 0)
                found3 = self._drag_image("assets/cook/whisk2.png", 0, -200)
                found4 = self._click_image("assets/cook/startCoocking.png")
                time.sleep(4.5)
                
                if found1 and found2 and found3 and found4:
                    self.log("[✓] Операция готовки завершена.")
                else:
                    self.log("[!] Ожидание появления всех элементов...")

                time.sleep(1.0)

        except Exception as e:
            self.log(f"[Ошибка] {e}")
        finally:
            self.log("[■] Скрипт готовки завершён.")
