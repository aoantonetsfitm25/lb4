"""Інтерактивний навчальний desktop-застосунок на PyQt6.

Демонструє layouts, віджети, сигнали й слоти, компоненти зі слабким
зв'язуванням, QMainWindow, діалоги та стилізацію Qt Style Sheets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


APP_DIR = Path(__file__).resolve().parent
DEFAULT_NAME = "Арсеній Антонець"
DEFAULT_GROUP = "БІКСб22540"


class ProfileEditor(QWidget):
    """Віджет введення даних, який повідомляє про зміни через сигнали."""

    profileChanged = pyqtSignal(str, str, int, str, str)
    scoreChanged = pyqtSignal(int)
    statusChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Створює форму профілю з адаптивним компонуванням."""
        super().__init__(parent)
        self._signals_blocked = False
        self.setObjectName("profileEditor")
        box = QGroupBox("Дані профілю")
        form = QFormLayout(box)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)

        self.name_edit = QLineEdit(DEFAULT_NAME)
        self.name_edit.setPlaceholderText("Наприклад, Арсеній Антонець")
        self.name_edit.setToolTip("ПІБ має містити хоча б один символ")
        self.name_edit.setClearButtonEnabled(True)

        self.group_edit = QLineEdit(DEFAULT_GROUP)
        self.group_edit.setPlaceholderText("Введіть шифр академічної групи")
        self.group_edit.setToolTip("Наприклад: БІКСб22540")

        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(20)
        self.age_spin.setSuffix(" років")
        self.age_spin.setToolTip("Для демонстрації валідації допустимо 16-100")

        self.program_combo = QComboBox()
        self.program_combo.addItems(["Комп'ютерні науки", "Кібербезпека", "Інженерія ПЗ"])
        self.program_combo.setToolTip("Виберіть освітню програму")

        self.basic_radio = QRadioButton("Базовий")
        self.advanced_radio = QRadioButton("Поглиблений")
        self.advanced_radio.setChecked(True)
        level_row = QWidget()
        level_layout = QHBoxLayout(level_row)
        level_layout.setContentsMargins(0, 0, 0, 0)
        level_layout.addWidget(self.basic_radio)
        level_layout.addWidget(self.advanced_radio)

        self.score_slider = QSlider(Qt.Orientation.Horizontal)
        self.score_slider.setRange(0, 100)
        self.score_slider.setValue(72)
        self.score_slider.setTickInterval(10)
        self.score_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.score_label = QLabel("72 / 100")
        score_row = QWidget()
        score_layout = QHBoxLayout(score_row)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.addWidget(self.score_slider, 1)
        score_layout.addWidget(self.score_label)

        self.agree_check = QCheckBox("Підтверджую правильність даних")
        self.agree_check.setChecked(True)

        form.addRow("ПІБ:", self.name_edit)
        form.addRow("Група:", self.group_edit)
        form.addRow("Вік:", self.age_spin)
        form.addRow("Програма:", self.program_combo)
        form.addRow("Рівень:", level_row)
        form.addRow("Самооцінка:", score_row)
        form.addRow("Підтвердження:", self.agree_check)

        self.feedback = QLabel("Заповніть форму та натисніть «Підтвердити».")
        self.feedback.setWordWrap(True)
        self.feedback.setObjectName("feedback")
        self.submit_button = QPushButton("Підтвердити")
        self.submit_button.setObjectName("primaryButton")
        self.submit_button.setToolTip("Перевірити введені значення")
        self.reset_button = QPushButton("Скинути")
        self.reset_button.setToolTip("Повернути початкові значення")

        actions = QHBoxLayout()
        actions.addWidget(self.submit_button)
        actions.addWidget(self.reset_button)
        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)
        layout.addStretch(1)

        self.name_edit.textChanged.connect(self._publish_profile)
        self.group_edit.textChanged.connect(self._publish_profile)
        self.age_spin.valueChanged.connect(self._publish_profile)
        self.program_combo.currentTextChanged.connect(lambda _text: self._publish_profile())
        self.basic_radio.toggled.connect(self._publish_profile)
        self.advanced_radio.toggled.connect(self._publish_profile)
        self.score_slider.valueChanged.connect(self._score_changed)
        self.agree_check.toggled.connect(self.submit_button.setEnabled)
        self.submit_button.clicked.connect(self.submit)
        self.reset_button.clicked.connect(self.reset)

    def current_level(self) -> str:
        """Повертає назву вибраного рівня."""
        return "Поглиблений" if self.advanced_radio.isChecked() else "Базовий"

    def validate_form(self) -> tuple[bool, str]:
        """Перевіряє ім'я, групу, вік і підтвердження користувача."""
        if not self.name_edit.text().strip():
            return False, "Вкажіть ПІБ - поле не може бути порожнім."
        if not self.group_edit.text().strip():
            return False, "Вкажіть академічну групу."
        if not 16 <= self.age_spin.value() <= 100:
            return False, "Вік має бути в діапазоні від 16 до 100 років."
        if not self.agree_check.isChecked():
            return False, "Потрібно підтвердити правильність даних."
        return True, "Дані пройшли перевірку."

    def _publish_profile(self, *_args: object) -> None:
        """Випромінює знімок стану форми після зміни поля."""
        self.profileChanged.emit(
            self.name_edit.text().strip(),
            self.group_edit.text().strip(),
            self.age_spin.value(),
            self.program_combo.currentText(),
            self.current_level(),
        )

    def _score_changed(self, value: int) -> None:
        """Оновлює локальну мітку та передає числовий сигнал."""
        self.score_label.setText(f"{value} / 100")
        self.scoreChanged.emit(value)
        self.statusChanged.emit(f"Самооцінка оновлена: {value} зі 100")

    def submit(self) -> None:
        """Валідує форму і показує результат без блокування вікна."""
        valid, message = self.validate_form()
        self.feedback.setText(message)
        self.feedback.setProperty("valid", valid)
        self.feedback.style().unpolish(self.feedback)
        self.feedback.style().polish(self.feedback)
        if valid:
            self._publish_profile()
            self.statusChanged.emit("Профіль підтверджено")
        else:
            self.statusChanged.emit("Форму не підтверджено: перевірте поля")

    def reset(self) -> None:
        """Відновлює початковий стан, не створюючи каскад сигналів."""
        self.set_interactions_blocked(True)
        self.name_edit.setText(DEFAULT_NAME)
        self.group_edit.setText(DEFAULT_GROUP)
        self.age_spin.setValue(20)
        self.program_combo.setCurrentIndex(0)
        self.advanced_radio.setChecked(True)
        self.agree_check.setChecked(True)
        self.score_slider.setValue(72)
        self.set_interactions_blocked(False)
        self.feedback.setText("Форму повернуто до початкового стану.")
        self.statusChanged.emit("Початковий стан відновлено")

    def set_interactions_blocked(self, blocked: bool) -> None:
        """Заморожує або відновлює автоматичні сигнали полів.

        Args:
            blocked (bool): Чи блокувати сигнали внутрішніх полів.

        Returns:
            None: Оновлює внутрішній стан форми.

        Raises:
            None.
        """
        self._signals_blocked = blocked
        for widget in (
            self.name_edit,
            self.group_edit,
            self.age_spin,
            self.program_combo,
            self.basic_radio,
            self.advanced_radio,
            self.score_slider,
            self.agree_check,
        ):
            widget.blockSignals(blocked)
        self.feedback.setText(
            "Автооновлення призупинено: змінюйте поля, підсумок заморожено."
            if blocked
            else "Автооновлення відновлено; підсумок синхронізовано."
        )
        if not blocked:
            self._publish_profile()
            self.scoreChanged.emit(self.score_slider.value())

    def set_profile(self, name: str, group: str, age: int) -> None:
        """Встановлює основні поля профілю без проміжних каскадів."""
        self.set_interactions_blocked(True)
        self.name_edit.setText(name)
        self.group_edit.setText(group)
        self.age_spin.setValue(age)
        self.set_interactions_blocked(False)

    def show_notice(self, text: str) -> None:
        """Показує повідомлення, отримане від іншого компонента."""
        self.feedback.setText(text)


class SummaryPanel(QWidget):
    """Компонент підсумку, незалежний від внутрішньої форми."""

    annotationAdded = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Створює попередній перегляд, індикатор і поле примітки."""
        super().__init__(parent)
        self.setObjectName("summaryPanel")
        title = QLabel("Підсумок профілю")
        title.setObjectName("panelTitle")
        self.profile_label = QLabel("Профіль ще не оновлено")
        self.profile_label.setWordWrap(True)
        self.program_label = QLabel("Освітня програма: -")
        self.level_label = QLabel("Рівень: -")
        self.score_label = QLabel("Самооцінка: 0 / 100")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("%p% готовності")

        note_row = QWidget()
        note_layout = QHBoxLayout(note_row)
        note_layout.setContentsMargins(0, 0, 0, 0)
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Коротка примітка...")
        self.note_button = QPushButton("Додати")
        self.note_button.setToolTip("Передати примітку сигналом батьківському вікну")
        note_layout.addWidget(self.note_edit, 1)
        note_layout.addWidget(self.note_button)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Тут з'являться підтвердження та примітки")
        self.log.setMinimumHeight(160)
        self.note_button.clicked.connect(self._emit_annotation)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.profile_label)
        layout.addWidget(self.program_label)
        layout.addWidget(self.level_label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.progress)
        layout.addWidget(QLabel("Примітки"))
        layout.addWidget(note_row)
        layout.addWidget(self.log, 1)

    def update_profile(self, name: str, group: str, age: int, program: str, level: str) -> None:
        """Відображає дані, отримані від ProfileEditor через сигнал."""
        shown_name = name or "(ПІБ не введено)"
        shown_group = group or "(групу не введено)"
        self.profile_label.setText(f"{shown_name}\nГрупа: {shown_group}  |  Вік: {age}")
        self.program_label.setText(f"Освітня програма: {program}")
        self.level_label.setText(f"Рівень: {level}")

    def update_score(self, value: int) -> None:
        """Оновлює індикатор числовим сигналом оцінки."""
        self.score_label.setText(f"Самооцінка: {value} / 100")
        self.progress.setValue(value)

    def _emit_annotation(self) -> None:
        """Надсилає заповнену примітку через кастомний сигнал."""
        text = self.note_edit.text().strip()
        if text:
            self.annotationAdded.emit(text)
            self.note_edit.clear()

    def append_annotation(self, text: str) -> None:
        """Додає повідомлення до журналу взаємодії."""
        self.log.append(f"• {text}")


class ProfileDialog(QDialog):
    """Власний модальний діалог редагування імені, групи та віку."""

    def __init__(self, name: str, group: str, age: int, parent: QWidget | None = None) -> None:
        """Готує поля та кнопки підтвердження або скасування."""
        super().__init__(parent)
        self.setWindowTitle("Параметри профілю")
        self.setModal(True)
        self.name_edit = QLineEdit(name)
        self.group_edit = QLineEdit(group)
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(age)
        form = QFormLayout()
        form.addRow("ПІБ:", self.name_edit)
        form.addRow("Група:", self.group_edit)
        form.addRow("Вік:", self.age_spin)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Зміни буде передано головному вікну після підтвердження."))
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str, int]:
        """Повертає підтверджені значення полів діалогу."""
        return self.name_edit.text().strip(), self.group_edit.text().strip(), self.age_spin.value()


class MainWindow(QMainWindow):
    """Головне вікно з меню, інструментами та слабко зв'язаними компонентами."""

    def __init__(self, themed: bool = True) -> None:
        """Створює структуру QMainWindow та зовнішні з'єднання сигналів."""
        super().__init__()
        self.setWindowTitle("PyQt6 Studio - особистий кабінет студента")
        self.setMinimumSize(980, 650)
        self.resize(1180, 760)
        self.editor = ProfileEditor()
        self.summary = SummaryPanel()
        self._build_central_widget()
        self._build_actions()
        self._build_menus_and_toolbar()

        # Взаємодія між компонентами задається тільки зовні.
        self.editor.profileChanged.connect(self.summary.update_profile)
        self.editor.scoreChanged.connect(self.summary.update_score)
        self.editor.statusChanged.connect(self.statusBar().showMessage)
        self.summary.annotationAdded.connect(self.editor.show_notice)
        self.summary.annotationAdded.connect(self._record_annotation)
        self.summary.log.textChanged.connect(self._update_character_count)
        self.editor._publish_profile()
        self.editor.scoreChanged.emit(self.editor.score_slider.value())
        self.statusBar().showMessage("Готово до роботи", 4000)
        self._apply_theme(themed)

    def _build_central_widget(self) -> None:
        """Розміщує компоненти через вкладені layouts, без координат."""
        central = QWidget()
        outer = QVBoxLayout(central)
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 4)
        hero = QLabel("Кабінет студента")
        hero.setObjectName("heroTitle")
        subtitle = QLabel("Профіль, взаємодія та керування даними")
        subtitle.setWordWrap(True)
        header_layout.addWidget(hero)
        header_layout.addStretch(1)
        header_layout.addWidget(subtitle)

        content = QHBoxLayout()
        content.addWidget(self.editor, 3)
        content.addWidget(self.summary, 2)
        outer.addWidget(header)
        outer.addLayout(content, 1)
        self.setCentralWidget(central)

    def _action(self, label: str, callback, shortcut: str | None = None) -> QAction:
        """Створює QAction з необов'язковим клавіатурним скороченням."""
        action = QAction(label, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        return action

    def _build_actions(self) -> None:
        """Оголошує команди, які повторно використовує меню і toolbar."""
        self.open_action = self._action("Відкрити JSON...", self.open_file, "Ctrl+O")
        self.save_action = self._action("Зберегти JSON...", self.save_file, "Ctrl+S")
        self.exit_action = self._action("Вихід", self.close, "Ctrl+Q")
        self.reset_action = self._action("Скинути форму", self.ask_reset, "Ctrl+R")
        self.profile_action = self._action("Параметри профілю...", self.open_profile_dialog)
        self.note_action = self._action("Швидка примітка...", self.open_input_dialog)
        self.about_action = self._action("Про застосунок", self.show_about)
        self.pause_action = QAction("Блокувати сигнали форми", self)
        self.pause_action.setCheckable(True)
        self.pause_action.toggled.connect(self.toggle_signal_flow)
        self.theme_action = QAction("Тема QSS", self)
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(True)
        self.theme_action.toggled.connect(self._apply_theme)

    def _build_menus_and_toolbar(self) -> None:
        """Створює меню та панель швидких команд QMainWindow."""
        file_menu = self.menuBar().addMenu("Файл")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = self.menuBar().addMenu("Дії")
        edit_menu.addAction(self.reset_action)
        edit_menu.addAction(self.profile_action)
        edit_menu.addAction(self.note_action)
        edit_menu.addAction(self.pause_action)

        view_menu = self.menuBar().addMenu("Вигляд")
        view_menu.addAction(self.theme_action)

        help_menu = self.menuBar().addMenu("Довідка")
        help_menu.addAction(self.about_action)
        help_menu.addAction(QAction("Про сигнали та слоти", self, triggered=self.show_signal_help))

        toolbar = QToolBar("Швидкі дії", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        for action in (self.open_action, self.save_action, self.reset_action, self.profile_action):
            toolbar.addAction(action)

    def _apply_theme(self, enabled: bool) -> None:
        """Застосовує або вимикає глобальний QSS для порівняння вигляду."""
        qss_path = APP_DIR / "theme.qss"
        self.qApp().setStyleSheet(qss_path.read_text(encoding="utf-8") if enabled else "")

    def toggle_signal_flow(self, blocked: bool) -> None:
        """Блокує зміни підсумку або синхронізує його після розблокування."""
        self.editor.set_interactions_blocked(blocked)
        self.statusBar().showMessage(
            "Сигнали заблоковано - підсумок не змінюється" if blocked else "Сигнали відновлено"
        )

    def _record_annotation(self, text: str) -> None:
        """Реєструє примітку та демонструє сигнал від SummaryPanel."""
        self.summary.append_annotation(f"Примітка: {text}")
        self.statusBar().showMessage("Примітку передано сигналом компонента", 5000)

    def _update_character_count(self) -> None:
        """Виводить довжину журналу в рядку стану."""
        count = len(self.summary.log.toPlainText())
        self.statusBar().showMessage(f"Символів у журналі: {count}", 2500)

    def _profile_payload(self) -> dict[str, object]:
        """Формує серіалізований стан для стандартних файлових діалогів."""
        return {
            "name": self.editor.name_edit.text().strip(),
            "group": self.editor.group_edit.text().strip(),
            "age": self.editor.age_spin.value(),
            "program": self.editor.program_combo.currentText(),
            "level": self.editor.current_level(),
            "score": self.editor.score_slider.value(),
        }

    def open_file(self) -> None:
        """Відкриває JSON-файл і завантажує основні дані профілю."""
        path, _filter = QFileDialog.getOpenFileName(
            self, "Відкрити профіль", "", "JSON (*.json);;Усі файли (*)"
        )
        if not path:
            self.statusBar().showMessage("Відкриття скасовано", 3000)
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self.editor.set_profile(str(data["name"]), str(data["group"]), int(data["age"]))
            self.statusBar().showMessage(f"Профіль відкрито: {Path(path).name}", 5000)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            QMessageBox.critical(self, "Не вдалося відкрити файл", str(exc))

    def save_file(self) -> None:
        """Зберігає форму в JSON через стандартний QFileDialog."""
        path, _filter = QFileDialog.getSaveFileName(
            self, "Зберегти профіль", "profile.json", "JSON (*.json)"
        )
        if not path:
            self.statusBar().showMessage("Збереження скасовано", 3000)
            return
        try:
            Path(path).write_text(
                json.dumps(self._profile_payload(), ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            QMessageBox.critical(self, "Не вдалося зберегти файл", str(exc))
            return
        self.statusBar().showMessage(f"Профіль збережено: {Path(path).name}", 5000)

    def open_input_dialog(self) -> None:
        """Запитує примітку через стандартний QInputDialog."""
        text, accepted = QInputDialog.getText(self, "Швидка примітка", "Текст примітки:")
        if accepted and text.strip():
            self.summary.annotationAdded.emit(text.strip())

    def open_profile_dialog(self) -> None:
        """Відкриває власний модальний діалог і приймає його результат."""
        dialog = ProfileDialog(
            self.editor.name_edit.text(), self.editor.group_edit.text(), self.editor.age_spin.value(), self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, group, age = dialog.values()
            self.editor.set_profile(name, group, age)
            self.statusBar().showMessage("Дані отримано з модального діалогу", 5000)

    def ask_reset(self) -> None:
        """Показує стандартне підтвердження перед очищенням форми."""
        answer = QMessageBox.question(
            self,
            "Скинути форму?",
            "Повернути поля до початкових значень?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.editor.reset()

    def show_about(self) -> None:
        """Відкриває стандартний інформаційний QMessageBox."""
        QMessageBox.about(
            self,
            "Про PyQt6 Studio",
            "Навчальний застосунок з layouts, сигналами, діалогами та QSS.",
        )

    def show_signal_help(self) -> None:
        """Пояснює маршрут сигналів між двома власними компонентами."""
        QMessageBox.information(
            self,
            "Сигнали та слоти",
            "ProfileEditor надсилає profileChanged і scoreChanged. "
            "SummaryPanel приймає їх через з'єднання в MainWindow та надсилає annotationAdded назад.",
        )

    def qApp(self) -> QApplication:
        """Повертає поточний QApplication."""
        instance = QApplication.instance()
        if instance is None:
            raise RuntimeError("QApplication ще не створено")
        return instance


def run_capture(window: MainWindow, app: QApplication, destination: Path, scenario: str) -> None:
    """Підготовлює стан демонстрації, захоплює вікно та завершує процес."""
    if scenario == "signals":
        window.editor.set_profile("Демонстраційний профіль", "БІКСб22540", 24)
        window.editor.program_combo.setCurrentText("Кібербезпека")
        window.editor.score_slider.setValue(88)
        window.summary.note_edit.setText("Сигнал компонента отримано")
        window.summary._emit_annotation()
    elif scenario == "resized":
        window.resize(1000, 680)
    app.processEvents()
    destination.parent.mkdir(parents=True, exist_ok=True)
    saved = window.grab().save(str(destination), "PNG")
    print(f"Screenshot saved: {destination} ({'ok' if saved else 'failed'})")
    app.quit()


def main(argv: list[str] | None = None) -> int:
    """Запускає GUI або робить один знімок вказаного сценарію."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plain", action="store_true", help="запустити без QSS для порівняння")
    parser.add_argument("--capture", type=Path, help="зберегти знімок робочого вікна")
    parser.add_argument("--scenario", choices=("default", "signals", "resized"), default="default")
    args, qt_args = parser.parse_known_args(argv)
    app = QApplication([sys.argv[0], *qt_args])
    app.setApplicationName("PyQt6 Studio")
    window = MainWindow(themed=not args.plain)
    window.show()
    if args.capture:
        QTimer.singleShot(900, lambda: run_capture(window, app, args.capture, args.scenario))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
