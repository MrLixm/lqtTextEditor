import copy
import dataclasses
from typing import Optional

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from Qt.QtWidgets import QStyle


class TextLine:
    """
    Mutable object to represent the state of a line in a text document.
    """

    def __init__(
        self,
        number: int,
        geometry: QtCore.QRectF,
        hovered: bool,
        pressed: bool,
        selected: bool,
        position: QtWidgets.QStyleOptionViewItem.ViewItemPosition,
        alternate: bool,
    ):
        super().__init__()
        self.number = number
        self.geometry = geometry
        self.hovered = hovered
        self.pressed = pressed
        self.selected = selected
        self.position = position
        self.alternate = alternate

    def copy(self):
        return self.__class__(
            number=self.number,
            geometry=QtCore.QRectF(self.geometry),
            hovered=self.hovered,
            pressed=self.pressed,
            selected=self.selected,
            position=self.position,
            alternate=self.alternate,
        )

    def apply_on_qstyle_option(self, qstyleoption: QtWidgets.QStyleOptionViewItem):
        """
        Transfer this instance attributes to the given QStyleOptionViewItem.
        """
        qstyleoption.rect = self.geometry.toRect()

        if qstyleoption.state & QStyle.State_MouseOver and not self.hovered:
            qstyleoption.state = qstyleoption.state ^ QStyle.State_MouseOver
        if self.hovered:
            qstyleoption.state = qstyleoption.state | QStyle.State_MouseOver

        # configure :selected selector
        if self.selected:
            qstyleoption.state = qstyleoption.state | QStyle.State_Selected

        # configure :first :last selector:
        qstyleoption.viewItemPosition = self.position

        # configure :pressed selector
        if self.pressed:
            qstyleoption.state = qstyleoption.state | QStyle.State_Sunken

        # configure :alternate selector
        if self.alternate:
            qstyleoption.features = qstyleoption.features | qstyleoption.Alternate


class TextLineBuffer:
    """
    A list of lines with convenient method for manipulation.
    """

    def __init__(self, lines: Optional[list[TextLine]] = None):
        super().__init__()
        self._lines: list[TextLine] = lines or []

    def __iter__(self):
        return self._lines.__iter__()

    @property
    def selected_lines(self) -> list[TextLine]:
        return [line for line in self._lines if line.selected]

    def add_line(self, text_line: TextLine):
        self._lines.append(text_line)

    def clear_all_lines(self):
        """
        Remove all lines stored.
        """
        self._lines = []

    def copy(self):
        return self.__class__(lines=[line.copy() for line in self._lines])

    def keep_only(self, lines_numbers: list[int]):
        """
        Remove all the lines that doesn't have the given line numbers.
        """
        for line in self._lines:
            if line.number not in lines_numbers:
                self.remove_line(line)

    def remove_line(self, text_line: Optional[TextLine]):
        """
        Remove the given line. Will raise if the line was never added previously.
        """
        if text_line:
            self._lines.remove(text_line)

    def get_line_by_number(self, number) -> Optional[TextLine]:
        """
        Get the line object corresponding to the given number, None if not found.
        """
        line = [line for line in self._lines if line.number == number]
        if line:
            return line[0]
        return None

    def get_line_from_position(self, position: QtCore.QPoint) -> Optional[TextLine]:
        """
        Args:
            position: expressed in local widget coordinates.

        Returns:
            text ine instance for the given position
        """
        for line in self._lines:
            if line.geometry.contains(QtCore.QPointF(position)):
                return line
        return None
