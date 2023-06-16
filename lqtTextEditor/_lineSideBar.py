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

        self._lines_numbers: list[int] = []
        """
        Ordered list of all the line numbers.
        
        Mainly to keep compatibility with python 2 which have unordered dicts.
        """

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

    def add_line(self, number: int, dimension: QtCore.QRectF):
        dimension.setWidth(self.width())
        self._lines[number] = dimension
        self._lines_numbers.append(number)
        self._lines_numbers.sort()

    def clear_lines(self):
        self._lines = {}
        self._lines_numbers = []

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
        self._mouse_pressed = False
        self.line_selection_changed.emit()
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)
        qpainter = QtGui.QPainter(self)
        cursor_position = self.mapFromGlobal(self.cursor().pos())

        # draw the whole sidebar background as regular QWidget
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

            qstyleoption = QtWidgets.QStyleOptionViewItem()
            qstyleoption.initFrom(self)
            qstyleoption.rect = line_geo.toRect()

            # configure for :hover
            line_has_focus = line_geo.contains(cursor_position)
            if (
                qstyleoption.state & QtWidgets.QStyle.State_MouseOver
                and not line_has_focus
            ):
                qstyleoption.state = (
                    qstyleoption.state ^ QtWidgets.QStyle.State_MouseOver
                )
            if line_has_focus:
                qstyleoption.state = (
                    qstyleoption.state | QtWidgets.QStyle.State_MouseOver
                )
            # configure for :first and :last
            if line_number == self._lines_numbers[0]:
                qstyleoption.viewItemPosition = QtWidgets.QStyleOptionViewItem.Beginning
            elif line_number == self._lines_numbers[-1]:
                qstyleoption.viewItemPosition = QtWidgets.QStyleOptionViewItem.End
            else:
                qstyleoption.viewItemPosition = QtWidgets.QStyleOptionViewItem.Invalid
            # configure for :pressed
            if line_has_focus and self._mouse_pressed:
                qstyleoption.state = qstyleoption.state | QtWidgets.QStyle.State_Sunken
            # configure for :selected
            if line_number in self.lines_selected_range:
                qstyleoption.state = (
                    qstyleoption.state | QtWidgets.QStyle.State_Selected
                )
                # we draw first using the palette so if no stylesheet, we still
                # have an effect visible
                highlight_color = self.palette().text()
                highlight_color.setColor(
                    QtGui.QColor(*highlight_color.color().toTuple()[:-1], 30)
                )
                qpainter.fillRect(line_geo, highlight_color)
                color_role = QtGui.QPalette.ColorRole.HighlightedText

            # draw line's cell
            self.style().drawPrimitive(
                QtWidgets.QStyle.PE_PanelItemViewItem,
                qstyleoption,
                qpainter,
                self,
            )

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
