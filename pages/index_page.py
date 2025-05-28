from PyQt5 import QtWidgets, QtCore

class IndexPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgba(26, 26, 30, 180);")
        
        layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("📇 Главная")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;background: none;")
        layout.addWidget(title)
        layout.addSpacing(10)

        description = QtWidgets.QLabel(
            "🎮 Добро пожаловать в BOT [GTA5RP]!\n\n"
            "🔨 Этот инструмент предназначен для автоматизации задач в игре GTA5RP на платформе RAGE Multiplayer.\n"
            "📁 Выберите нужный модуль из меню слева.\n\n"
            "⚠️ Использование данного ПО может нарушать правила сервера. Используйте на свой страх и риск.\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            "🌐 Discord - dornode"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: lightgray; font-size: 14px;background: none;")
        layout.addWidget(description)

        layout.addStretch()

        version_label = QtWidgets.QLabel("Версия: 1.0.0")
        version_label.setStyleSheet("color: gray; font-size: 12px;background: none;")
        version_label.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(version_label)
        self.setLayout(layout)
