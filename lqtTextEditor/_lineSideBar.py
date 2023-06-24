import logging
from typing import Optional

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from lqtTextEditor._line import TextLine
from lqtTextEditor._line import TextLineBuffer


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

        self._lines: TextLineBuffer = TextLineBuffer()

        self._mouse_pressed: bool = False

        self.margins_side = 8

        self._line_selected_start: Optional[int] = None
        self._line_selected_end: Optional[int] = None

        self.setAttribute(QtCore.Qt.WA_Hover, True)

    @property
    def lines_selected_range(self) -> list[int]:
        """
        Sequence of line numbers that are selected.

        Can be ascending or descending order. Example : [5,4,3,2].
        """
        if self._line_selected_start is None and self._line_selected_end is None:
            return []
        elif self._line_selected_start is None and self._line_selected_end is not None:
            return [self._line_selected_end]
        elif self._line_selected_end is None and self._line_selected_start is not None:
            return [self._line_selected_start]

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

    def set_line_buffer(self, buffer: TextLineBuffer):
        self._lines = buffer
        self.repaint()

    # Overrides

    def event(self, event: QtCore.QEvent) -> bool:
        # HACK: we draw each line as an individual item in paintEvent but events are
        # still triggered on the global parent widget. So repaint more often.
        if event.type() in (QtCore.QEvent.HoverMove, QtCore.QEvent.HoverLeave):
            self.repaint()
        return super().event(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        super().mousePressEvent(event)
        self._mouse_pressed = True
        pos = self.mapFromGlobal(self.cursor().pos())
        self._line_selected_end = None

        self._line_selected_start = self._lines.get_line_from_position(pos)
        if self._line_selected_start:
            self._line_selected_start = self._line_selected_start.number

        self.line_selection_changed.emit()
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        pos = self.mapFromGlobal(self.cursor().pos())

        self._line_selected_end = self._lines.get_line_from_position(pos)
        if self._line_selected_end:
            self._line_selected_end = self._line_selected_end.number

        self.line_selection_changed.emit()
        self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        super().mouseReleaseEvent(event)
        self._mouse_pressed = False
        self.line_selection_changed.emit()
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)
        qpainter = QtGui.QPainter(self)

        # draw the whole sidebar background as regular QWidget
        qstyleoption = QtWidgets.QStyleOption()
        qstyleoption.initFrom(self)
        self.style().drawPrimitive(
            QtWidgets.QStyle.PE_Widget,
            qstyleoption,
            qpainter,
            self,
        )

        for line in self._lines:
            color_role = QtGui.QPalette.ColorRole.Text

            qstyleoption = QtWidgets.QStyleOptionViewItem()
            qstyleoption.initFrom(self)
            line.apply_on_qstyle_option(qstyleoption)

            if line.selected:
                # we draw first using the palette so if no stylesheet, we still
                # have an effect visible
                highlight_color = self.palette().text()
                highlight_color.setColor(
                    QtGui.QColor(*highlight_color.color().toTuple()[:-1], 30)
                )
                qpainter.fillRect(line.geometry, highlight_color)
                color_role = QtGui.QPalette.ColorRole.HighlightedText

            # draw line's cell
            self.style().drawPrimitive(
                QtWidgets.QStyle.PE_PanelItemViewItem,
                qstyleoption,
                qpainter,
                self,
            )

            text_geo = line.geometry.adjusted(
                self.margins_side,
                0,
                -self.margins_side,
                0,
            )

            self.style().drawItemText(
                qpainter,
                text_geo.toRect(),
                QtCore.Qt.AlignRight,
                self.palette(),
                True,
                str(line.number + 1),
                color_role,
            )
