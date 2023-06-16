import logging

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets


LOGGER = logging.getLogger(__name__)


class JumpToLineDialog(QtWidgets.QDialog):
    """
    A small dialog that prompt the user a line number to jump to.

    Args:
        max_lines: maximal number of lines in the parent editor
    """

    def __init__(self, max_lines: int, parent=None):
        super().__init__(parent=parent)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout_center = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel("Line Number:")
        validator = QtGui.QIntValidator(1, max_lines, self)
        self.line_edit = QtWidgets.QLineEdit()
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )

        self.setLayout(self.layout)
        self.layout.addLayout(self.layout_center)
        self.layout.addWidget(self.buttons)
        self.layout_center.addWidget(self.label)
        self.layout_center.addWidget(self.line_edit)

        self.setWindowTitle("Jump To Line")
        self.line_edit.setValidator(validator)
        self.line_edit.setText(str(max_lines))
        self.line_edit.setFocus(QtCore.Qt.PopupFocusReason)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    @property
    def line_number(self) -> int:
        return int(self.line_edit.text() or "1")
