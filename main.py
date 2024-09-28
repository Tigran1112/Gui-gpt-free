import sys
import g4f
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QFile, QTextStream

class Worker(QThread):
    response_received = pyqtSignal(str)

    def __init__(self, history):
        super().__init__()
        self.history = history

    def run(self):
        # Здесь выполняем вызов API
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": "\n".join(self.history)}],
        )
        self.response_received.emit(response)

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Chat GPT GUI")
        self.setGeometry(100, 100, 400, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Добро пожаловать. Для помощи нажми '!help'.")
        self.layout.addWidget(self.label)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)  # Делаем текстовое поле только для чтения
        self.layout.addWidget(self.text_area)

        self.input_area = QTextEdit(self)
        self.input_area.setPlaceholderText("Введите сообщение...")
        self.input_area.setFixedHeight(50)
        self.layout.addWidget(self.input_area)

        # Индикатор загрузки
        self.loading_label = QLabel("", self)
        self.layout.addWidget(self.loading_label)

        # Создаем горизонтальный layout для кнопок
        button_layout = QHBoxLayout()

        self.send_button = QPushButton("Отправить", self)
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        self.clear_button = QPushButton("Очистить (!clear)", self)
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)

        self.help_button = QPushButton("Помощь (!help)", self)
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        # Добавляем кнопку layout под полем ввода
        self.layout.addLayout(button_layout)

        # Загружаем стили из файла
        self.load_stylesheet("styles.css")

    def load_stylesheet(self, filepath):
        file = QFile(filepath)
        if file.open(QFile.ReadOnly):
            stylesheet = QTextStream(file).readAll()
            self.setStyleSheet(stylesheet)
        else:
            print(f"Не удалось открыть файл стилей: {filepath}")

    def send_message(self):
        prompt = self.input_area.toPlainText().strip()
        if prompt:
            self.history.append(prompt)
            self.text_area.append(f"Вы: {prompt}")
            self.input_area.clear()
            self.loading_label.setText("Загрузка...")  # Показываем индикатор загрузки

            # Запускаем поток для вызова API
            self.worker = Worker(self.history)
            self.worker.response_received.connect(self.display_response)
            self.worker.start()

    def display_response(self, response):
        self.history.append(response)
        self.text_area.append(f"Ответ: {response}")
        self.loading_label.setText("")  # Убираем индикатор загрузки

    def clear_chat(self):
        self.history.clear()
        self.text_area.clear()
        self.input_area.clear()
        self.loading_label.setText("")  # Убираем индикатор загрузки

    def show_help(self):
        help_text = "!clear - очистка чата\n!exit - выход из программы\n!help - помощь"
        self.text_area.append(help_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())
