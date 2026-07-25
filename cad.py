# enter the following in the command prompt to draw a line: 
#   draw_line -100 -100 150 120


import sys

from PySide6.QtCore import QLineF
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DrawingView(QGraphicsView):
    """Main 2D drawing canvas."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)
        
        self.graphics_scene.setBackgroundBrush(QColor(40, 40, 40))

        self.setSceneRect(-500, -500, 1000, 1000)

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )

        self.pen = QPen(QColor(255, 255, 255))
        self.pen.setWidth(2)

    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ):
        """Draw a line on the canvas."""

        line = QLineF(x1, y1, x2, y2)

        graphics_item = self.graphics_scene.addLine(
            line,
            self.pen,
        )

        graphics_item.setFlag(
            graphics_item.GraphicsItemFlag.ItemIsSelectable,
            True,
        )

        return graphics_item

    def wheelEvent(self, event):
        """Zoom in and out using the mouse wheel."""

        zoom_factor = 1.15

        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Drafting")
        self.resize(1100, 750)

        self.drawing_view = DrawingView()

        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText(
            "Try: draw_line 0 0 200 100"
        )
        self.prompt_input.returnPressed.connect(self.handle_prompt)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_prompt)

        prompt_layout = QHBoxLayout()
        prompt_layout.addWidget(QLabel("Command:"))
        prompt_layout.addWidget(self.prompt_input)
        prompt_layout.addWidget(self.send_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.drawing_view)
        main_layout.addLayout(prompt_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

        self.statusBar().showMessage("Ready")

        self.available_functions = {
            "draw_line": self.drawing_view.draw_line,
        }

        # # Initial example lines.
        # self.execute_function(
        #     "draw_line",
        #     x1=-200,
        #     y1=0,
        #     x2=200,
        #     y2=0,
        # )

        # self.execute_function(
        #     "draw_line",
        #     x1=0,
        #     y1=-200,
        #     x2=0,
        #     y2=200,
        # )

    def execute_function(self, function_name: str, **arguments):
        """
        Execute one approved drafting function.

        The AI will eventually call this method with a function name
        and structured arguments.
        """

        function = self.available_functions.get(function_name)

        if function is None:
            raise ValueError(
                f"Unknown function: {function_name}"
            )

        return function(**arguments)

    def handle_prompt(self):
        """
        Temporary text-command parser.

        Later, an AI model will turn natural language into a function
        name and arguments.
        """

        prompt = self.prompt_input.text().strip()

        if not prompt:
            self.statusBar().showMessage("Enter a command first.")
            return

        try:
            self.execute_text_command(prompt)
        except ValueError as error:
            self.statusBar().showMessage(str(error))
            return

        self.prompt_input.clear()
        self.statusBar().showMessage("Command completed.")

    def execute_text_command(self, command_text: str):
        parts = command_text.split()

        if not parts:
            raise ValueError("Command is empty.")

        function_name = parts[0]

        if function_name == "draw_line":
            if len(parts) != 5:
                raise ValueError(
                    "Usage: draw_line x1 y1 x2 y2"
                )

            try:
                x1, y1, x2, y2 = map(float, parts[1:])
            except ValueError as error:
                raise ValueError(
                    "Line coordinates must be numbers."
                ) from error

            self.execute_function(
                "draw_line",
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
            )

            return

        raise ValueError(
            f"Unsupported command: {function_name}"
        )


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()