from typing import Optional

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets


class NumberedSideBarWidget(QtWidgets.QWidget):
    """
    A vertical widget displaying a sequence of numbers, where one numeber is associated
    to a "line".

    Made to work with :class:`LineNumberedTextEditor`
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lines: dict[int, QtCore.QRectF] = {}
        """
        List of line with its respective dimension for each
        """

        self.active_lines: list[int] = []
        """
        List of line index that are selected.
        """

        self.margins_side = 8

        self._line_selected_start: Optional[int] = None
        self._line_selected_end: Optional[int] = None

    @property
    def lines_selected_range(self) -> list[int]:
        """
        Sequence of line numbers that are selected.

        Can be ascending or descending order. Example : [5,4,3,2]
        """
        if self._line_selected_start is None or self._line_selected_end is None:
            return [self._line_selected_start or -1, self._line_selected_end or -1]

        direction = 1 if self._line_selected_end > self._line_selected_start else -1
        return list(
            range(
                self._line_selected_start,
                self._line_selected_end + direction,
                direction,
            )
        )

    def width(self) -> int:
        width = self.fontMetrics().boundingRect("9")
        # hack to take in account font bearing
        width = self.fontMetrics().boundingRect(width, 0, "9").width()
        max_lines = list(self._lines)[-1] if self._lines else 0
        max_lines = max(max_lines, 9999)
        width = width * len(str(max_lines))
        return width + (self.margins_side * 2)

    def add_line(self, number: int, dimension: QtCore.QRectF):
        dimension.setWidth(self.width())
        self._lines[number] = dimension

    def clear_lines(self):
        self._lines = {}

    def get_line_from_pos(self, position: QtCore.QPoint) -> Optional[int]:
        """
        Args:
            position: expressed in local widget coordinates.

        Returns:
            line number for the gicne position
        """
        for line_number, line_geo in self._lines.items():
            if line_geo.contains(QtCore.QPointF(position)):
                return line_number
        return None

    # Overrides

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        super().mousePressEvent(event)
        pos = self.mapFromGlobal(self.cursor().pos())
        self._line_selected_start = self.get_line_from_pos(pos)
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        pos = self.mapFromGlobal(self.cursor().pos())
        self._line_selected_end = self.get_line_from_pos(pos)
        self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        super().mouseReleaseEvent(event)
        self._line_selected_start = None
        self._line_selected_end = None
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)
        qpainter = QtGui.QPainter(self)

        qstyleoption = QtWidgets.QStyleOption()
        qstyleoption.initFrom(self)
        self.style().drawPrimitive(
            QtWidgets.QStyle.PE_Widget,
            qstyleoption,
            qpainter,
            self,
        )

        for line_number, line_geo in self._lines.items():
            color_role = QtGui.QPalette.ColorRole.Text

            if (
                line_number in self.lines_selected_range
                or line_number in self.active_lines
            ):
                qpainter.fillRect(line_geo, self.palette().foreground())
                color_role = QtGui.QPalette.ColorRole.HighlightedText

            text_geo = line_geo.adjusted(self.margins_side, 0, -self.margins_side, 0)

            self.style().drawItemText(
                qpainter,
                text_geo.toRect(),
                QtCore.Qt.AlignRight,
                self.palette(),
                True,
                str(line_number + 1),
                color_role,
            )


class LineNumberedTextEditor(QtWidgets.QPlainTextEdit):
    """
    A regular text edit but that display the line number on the left of each line.

    The line number is displayed in a widget called sidebar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sidebar = NumberedSideBarWidget(self)

        self.updateRequest.connect(self._update_sidebar)
        self.blockCountChanged.connect(self._update_sidebar_geo)
        self.cursorPositionChanged.connect(self._on_selection_changed)

        self.setViewportMargins(0, 0, 0, 0)

    @property
    def sidebar(self) -> NumberedSideBarWidget:
        return self._sidebar

    @property
    def selected_lines(self) -> list[int]:
        """
        List of lines number selected.
        """
        start = self.textCursor().selectionStart()
        end = self.textCursor().selectionEnd()
        cursor = self.textCursor()
        cursor.setPosition(start)
        start_line = cursor.blockNumber()
        cursor.setPosition(end)
        end_line = cursor.blockNumber()
        active_lines = list(range(start_line, end_line + 1))
        return active_lines

    def _on_selection_changed(self):
        self.sidebar.active_lines = self.selected_lines

    def _update_sidebar(self):
        block_count = self.blockCount()
        block = self.firstVisibleBlock()
        block_index = block.blockNumber()

        self.sidebar.clear_lines()

        while block.isValid() and block_index <= block_count:
            block_geo = self.blockBoundingGeometry(block)
            block_geo = block_geo.translated(self.contentOffset())
            block_geo.setX(0)
            self.sidebar.add_line(block_index, block_geo)
            block = block.next()
            block_index += 1

        self.sidebar.update()

    def _update_sidebar_geo(self):
        self.sidebar.setGeometry(0, 0, self.sidebar.width(), self.height())

    # Overrides

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        super().mousePressEvent(event)
        print(self.cursor().pos())

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_sidebar_geo()

    def setViewportMargins(self, left: int, top: int, right: int, bottom: int):
        super().setViewportMargins(left + self.sidebar.width(), top, right, bottom)
