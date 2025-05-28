import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import os
from widgets.switch_button import SwitchButton
from pages.simple_page import SimplePage
from pages.index_page import IndexPage
from pages.port_page import PortPage
from pages.anti_afk_page import AntiAfkPage
from pages.stroyka_page import StroykaPage
from pages.tokar_page import TokarPage
from pages.shveika_page import ShveikaPage

class BotMasterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle("BOT [GTA5RP]")
        self.setMinimumSize(800, 680)
        self.resize(800, 600)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.drag_pos = None
        self.current_button = None
        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("""QFrame {
            background-color: rgba(18, 18, 20, 200);
            border-radius: 20px;
        }""")
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = QtWidgets.QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: rgba(18, 18, 20, 220); border-top-left-radius: 20px; border-top-right-radius: 20px;")
        title_bar_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(17, 0, 17, 0)

        icon_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("icon.png")
        icon_label.setPixmap(pixmap.scaled(20, 20, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        icon_label.setFixedSize(20, 20)

        self.title_label = QtWidgets.QLabel("BOT [GTA5RP]")
        self.title_label.setStyleSheet("color: white; font-size: 16px; margin-left: 5px;")

        title_with_icon = QtWidgets.QHBoxLayout()
        title_with_icon.setContentsMargins(0, 0, 0, 0)
        title_with_icon.setSpacing(5)
        title_with_icon.addWidget(icon_label)
        title_with_icon.addWidget(self.title_label)

        title_container = QtWidgets.QWidget()
        title_container.setLayout(title_with_icon)

        title_bar_layout.addWidget(title_container)
        title_bar_layout.addStretch()

        minimize_btn = QtWidgets.QPushButton("-")
        close_btn = QtWidgets.QPushButton("×")
        for btn in (minimize_btn, close_btn):
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("""QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: red;
                border-radius: 12px;
            }""")

        minimize_btn.clicked.connect(self.showMinimized)
        close_btn.clicked.connect(self.close)
        title_bar_layout.addWidget(minimize_btn)
        title_bar_layout.addWidget(close_btn)

        self.title_bar.mousePressEvent = self.title_mouse_press
        self.title_bar.mouseMoveEvent = self.title_mouse_move

        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setContentsMargins(20, 10, 20, 20)
        content_layout.setSpacing(20)

        menu_layout = QtWidgets.QVBoxLayout()
        menu_layout.setSpacing(10)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.setStyleSheet("background-color: rgba(26, 26, 30, 180); border-radius: 10px; color: white;")
        self.menu_buttons = {}

        features = [
            ("Главная", "📇", IndexPage, True),
            ("Токарь", "⛓", TokarPage, False),
            ("Швейка", "👕", ShveikaPage, True),
            ("Качалка", "🏋️", SimplePage, False),
            ("Стройка", "🧱", StroykaPage, True),
            ("Порт", "🚢", PortPage, True),
            ("Шахта", "⛏️", SimplePage, False),
            ("Коровы", "🐄", SimplePage, False),
            ("Анти-АФК", "🎯", AntiAfkPage, True),
        ]

        self.pages = {}

        for name, emoji, page_class, enabled in features:
            btn = QtWidgets.QPushButton(f"{emoji} {name}")
            btn.setFixedHeight(40)
            btn.setCheckable(True)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.menu_buttons[name] = btn

            if enabled:
                btn.setStyleSheet("""
                QPushButton {
                    background-color: #2e2e2e;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
                QPushButton:checked {
                    background-color: #2e2e2e;
                    border-left: 4px solid green;
                    border-radius: 10px;
                    padding-left: 11px;
                }""")
                btn.clicked.connect(self.make_tab_switcher(name, btn))
            else:
                btn.setEnabled(False)
                btn.setStyleSheet("""QPushButton {
                    background-color: #222;
                    color: gray;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    text-align: left;
                    padding-left: 15px;
                }""")

            menu_layout.addWidget(btn)

            if page_class == SimplePage:
                page = page_class(name)
            else:
                page = page_class()

            self.pages[name] = page
            self.stack.addWidget(page)

        menu_layout.addStretch()
        content_layout.addLayout(menu_layout, 1)
        content_layout.addWidget(self.stack, 3)

        container_layout.addWidget(self.title_bar)
        container_layout.addLayout(content_layout)
        main_layout.addWidget(self.container)

        # Установим главную страницу как активную
        self.stack.setCurrentWidget(self.pages["Главная"])
        self.menu_buttons["Главная"].setChecked(True)
        self.current_button = self.menu_buttons["Главная"]

    def title_mouse_press(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def title_mouse_move(self, event):
        if self.drag_pos and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def make_tab_switcher(self, name, button):
        def switch_tab():
            self.stack.setCurrentWidget(self.pages[name])
            if self.current_button and self.current_button != button:
                self.current_button.setChecked(False)
            button.setChecked(True)
            self.current_button = button
        return switch_tab

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BotMasterApp()
    window.show()
    sys.exit(app.exec_())
