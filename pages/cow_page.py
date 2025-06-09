from PyQt5 import QtWidgets, QtCore
from widgets.switch_button import SwitchButton
import time
import keyboard
import pyautogui
from widgets.logger import CommonLogger


class CowPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.worker: CowWorker | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        switch_layout = QtWidgets.QHBoxLayout()
        self.switch = SwitchButton()
        self.switch.clicked.connect(self.toggle_script)

        switch_layout.addWidget(CommonLogger._make_label("Коровы", 16))
        switch_layout.addStretch()
        switch_layout.addWidget(self.switch)
        layout.addLayout(switch_layout)

        hotkey_layout = QtWidgets.QHBoxLayout()
        self.hotkey_input = QtWidgets.QLineEdit("f6")
        self.hotkey_input.setMaxLength(20)
        self.hotkey_input.setFixedWidth(100)
        self.hotkey_input.setStyleSheet("background-color: #222; color: white;")

        hotkey_layout.addWidget(CommonLogger._make_label("Горячая клавиша:", 14))
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_layout.addStretch()
        layout.addLayout(hotkey_layout)

        hotkey_description = QtWidgets.QLabel("— вкл/выкл скрипта")
        hotkey_description.setStyleSheet("color: white; font-size: 12px; padding-right:150px;background: none;")
        hotkey_layout.addWidget(hotkey_description)

        self.counter_label = QtWidgets.QLabel("Счётчик: 0")
        self.counter_label.setStyleSheet("color: white; font-size: 14px;background: none;")
        layout.addWidget(self.counter_label)
        layout.addStretch()

        self.log_output = CommonLogger.create_log_field(layout)

    def toggle_script(self, checked: bool):
        if checked:
            self.log_output.clear()
            self.worker = CowWorker(self.hotkey_input.text())
            self.worker.log_signal.connect(self._append_log)
            self.worker.counter_signal.connect(self._update_counter)
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

    def _update_counter(self, value: int):
        self.counter_label.setText(f"Счётчик: {value}")


class CowWorker(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    counter_signal = QtCore.pyqtSignal(int)

    def __init__(self, hotkey: str = "f6"):
        super().__init__()
        self._running = True
        self._count = 0
        self._active = False
        self._toggle_requested = False
        self.hotkey = hotkey.lower().strip() or "f6"

        try:
            keyboard.add_hotkey(self.hotkey, self._request_toggle)
        except Exception as e:
            self.log(f"[!] Ошибка при назначении горячей клавиши '{self.hotkey}': {str(e)}")

    def log(self, message: str):
        CommonLogger.log(message, self.log_signal)

    def stop(self):
        self._running = False
        keyboard.unhook_all_hotkeys()
        self._active = False
        self.log("[■] Скрипт остановлен")

    def _request_toggle(self):
        self._toggle_requested = True

    def run(self):
        self.log("Скрипт коров запущен. Нажми ESC для остановки или используй переключатель.")
        rage_logged = False

        try:
            while self._running:
                # Проверка окна
                try:
                    if not CommonLogger.is_rage_mp_active():
                        if self._active:
                            self._active = False
                            self.log("[■] Скрипт приостановлен (RAGE не активно)")
                        if not rage_logged:
                            self.log("Окно RAGE Multiplayer не активно. Ожидание...")
                            rage_logged = True
                        time.sleep(1.0)
                        continue
                    else:
                        if rage_logged:
                            self.log("Окно RAGE Multiplayer найдено.")
                            rage_logged = False
                except Exception as e:
                    self.log(f"[!] Ошибка при проверке окна RAGE: {e}")
                    time.sleep(1.0)
                    continue

                # ESC для выхода
                if keyboard.is_pressed("esc"):
                    self.log("Получен ESC. Останавливаемся...")
                    self.stop()
                    break

                # Переключение скрипта
                if self._toggle_requested:
                    self._active = not self._active
                    self.log(f"[→] Скрипт {'активирован' if self._active else 'деактивирован'}")
                    self._toggle_requested = False

                if not self._active:
                    time.sleep(0.1)
                    continue

                # Поиск A и D с высоким confidence
                try:
                    a_pos = pyautogui.locateOnScreen('assets/cow/a.png', confidence=0.99)
                    if a_pos:
                        keyboard.send('a')
                        self._count += 1
                        self.log(f"[A] Найдена A - нажата (#{self._count})")
                        self.counter_signal.emit(self._count)
                        # pyautogui.screenshot("debug_a.png", region=a_pos)  # <- Включи, если нужно
                        time.sleep(0.3)

                    d_pos = pyautogui.locateOnScreen('assets/cow/d.png', confidence=0.99)
                    if d_pos:
                        keyboard.send('d')
                        self._count += 1
                        self.log(f"[D] Найдена D - нажата (#{self._count})")
                        self.counter_signal.emit(self._count)
                        # pyautogui.screenshot("debug_d.png", region=d_pos)  # <- Включи, если нужно
                        time.sleep(0.3)

                except Exception as e:
                    self.log(f"[!] Ошибка поиска изображений: {str(e)}")
                    time.sleep(1.0)

                time.sleep(0.05)

        except Exception as exc:
            self.log(f"[Ошибка потока] {exc}")
            self.stop()
