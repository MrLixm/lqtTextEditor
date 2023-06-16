import logging
from typing import Optional

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

LOGGER = logging.getLogger(__name__)


class LineSideBarWidget(QtWidgets.QWidget):
    """
    A vertical widget displaying a sequence of numbers, where one numeber is associated
    to a "line".

    Made to work with :class:`LineNumberedTextEditor`

    Line are internally stored as starting from 0 but are displaying as starting from 1.
    """

    line_selection_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lines: dict[int, QtCore.QRectF] = {}
        """
        List of line with its respective dimension for each.

        Line number starts at 0.
        """

        self.margins_side = 8

        self._line_selected_start: Optional[int] = None
        self._line_selected_end: Optional[int] = None

    @property
    def lines_selected_range(self) -> list[int]:
        """
        Sequence of line numbers that are selected.

        Can be ascending or descending order. Example : [5,4,3,2].
        """
        if self._line_selected_start is None or self._line_selected_end is None:
            # noinspection PyTypeChecker
            return list(
                filter(None, [self._line_selected_start, self._line_selected_end])
            )

        direction = 1 if self._line_selected_end > self._line_selected_start else -1
        return list(
            range(
                self._line_selected_start,
                self._line_selected_end + direction,
                direction,
            )
        )

    def get_intended_width(self, max_line) -> int:
        width = self.fontMetrics().boundingRect("9")
        # hack to take in account font bearing
        width = self.fontMetrics().boundingRect(width, 0, "9").width()
        max_lines = max(max_line, 9999)
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

    def set_selected_lines(self, line_start, line_end):
        self._line_selected_start = line_start
        self._line_selected_end = line_end
        self.update()

    # Overrides

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        super().mousePressEvent(event)
        pos = self.mapFromGlobal(self.cursor().pos())
        self._line_selected_end = None
        self._line_selected_start = self.get_line_from_pos(pos)
        self.line_selection_changed.emit()
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        pos = self.mapFromGlobal(self.cursor().pos())
        self._line_selected_end = self.get_line_from_pos(pos)
        self.line_selection_changed.emit()
        self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        super().mouseReleaseEvent(event)
        self.line_selection_changed.emit()
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

            if line_number in self.lines_selected_range:
                highlight_color = self.palette().foreground()
                highlight_color.setColor(
                    QtGui.QColor(*highlight_color.color().toTuple()[:-1], 20)
                )
                qpainter.fillRect(line_geo, highlight_color)
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
