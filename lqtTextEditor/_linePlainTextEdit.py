import logging
from typing import Optional

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from lqtTextEditor._lineSideBar import LineSideBarWidget
from lqtTextEditor._jumpToLineDialog import JumpToLineDialog


LOGGER = logging.getLogger(__name__)


class LinePlainTextEdit(QtWidgets.QPlainTextEdit):
    """
    A regular text edit but that display the line number on the left of each line.

    The line number is displayed in a widget called sidebar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._updating_selection: bool = False
        self._left_margin: int = 0
        self._tab_character = " " * 4

        self._sidebar = LineSideBarWidget(self)

        self.updateRequest.connect(self._update_sidebar)
        self.blockCountChanged.connect(self._on_block_count_changed)
        self.cursorPositionChanged.connect(self._on_selection_changed)
        self._sidebar.line_selection_changed.connect(self._on_sidebar_lines_changed)

        self._update_margins()

    @property
    def selected_lines_start(self) -> int:
        """
        Line number of the beginning of the selection
        """
        cursor = self.textCursor()
        start = cursor.selectionStart()
        cursor.setPosition(start)
        return cursor.blockNumber()

    @property
    def selected_lines_end(self) -> int:
        """
        Line number of the end of the selection
        """
        cursor = self.textCursor()
        end = cursor.selectionEnd()
        cursor.setPosition(end)
        return cursor.blockNumber()

    def _on_block_count_changed(self):
        self._update_sidebar_geo()
        self._update_margins()

    def _on_jump_to_line(self):
        dialog = JumpToLineDialog(max_lines=self.blockCount())
        result = dialog.exec_()
        if result != dialog.Accepted:
            return
        self.jump_to_line(dialog.line_number - 1)

    def _on_selection_changed(self):
        """
        Callback when this text cursor change.
        """
        if self._updating_selection:
            return

        self._sidebar.set_selected_lines(
            self.selected_lines_start,
            self.selected_lines_end,
        )

    def _on_sidebar_lines_changed(self):
        """
        Propagate the range of line selected in the sidebar to this text cursor.
        """
        self._updating_selection = True

        selected_lines = self._sidebar.lines_selected_range

        if not selected_lines:
            self._updating_selection = False
            self._on_selection_changed()
            return

        start = min(selected_lines)
        end = max(selected_lines)

        cursor = QtGui.QTextCursor(self.document().findBlockByNumber(start))

        if end > start:
            ntimes = end - cursor.blockNumber()
            cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor, ntimes)

        cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)

        self.setTextCursor(cursor)

        scrollbar_h = self.horizontalScrollBar()
        scrollbar_h.setSliderPosition(scrollbar_h.minimum())

        self._updating_selection = False

    def _update_margins(self):
        current_margins = self.viewportMargins()
        self.setViewportMargins(
            self._sidebar.get_intended_width(self.blockCount()) + self._left_margin,
            current_margins.top(),
            current_margins.right(),
            current_margins.bottom(),
        )

    def _update_sidebar(self):
        """
        Updates lines displayed in the sidebar.
        """
        block = self.firstVisibleBlock()
        # starts at 0
        block_index = block.blockNumber()

        self._sidebar.clear_lines()

        while block.isValid():
            if block.isVisible():
                block_geo = self.blockBoundingGeometry(block)
                block_geo = block_geo.translated(self.contentOffset())
                block_geo.setX(0)

                if block_geo.bottom() > self.viewport().geometry().bottom():
                    break

                self._sidebar.add_line(block_index, block_geo)

            block = block.next()
            block_index += 1

        self._sidebar.update()

    def _update_sidebar_geo(self):
        self._sidebar.setGeometry(
            0,
            0,
            self._sidebar.get_intended_width(self.blockCount()),
            self.height(),
        )

    def _indent_selection(self):
        cursor = self.textCursor()
        if not cursor.selectedText():
            cursor.insertText(self._tab_character)
            self.setTextCursor(cursor)
            return
        for line in range(self.selected_lines_start, self.selected_lines_end + 1):
            block = self.document().findBlockByLineNumber(line)
            cursor = QtGui.QTextCursor(block)
            cursor.insertText(self._tab_character)

    def _unindent_selection(self):
        cursor = self.textCursor()
        cursor.setPosition(
            cursor.position() - len(self._tab_character), cursor.KeepAnchor
        )
        for line in range(self.selected_lines_start, self.selected_lines_end + 1):
            block = self.document().findBlockByLineNumber(line)
            cursor = QtGui.QTextCursor(block)
            cursor.setPosition(
                cursor.position() + len(self._tab_character), cursor.KeepAnchor
            )
            if cursor.selectedText() == self._tab_character:
                cursor.removeSelectedText()

    def jump_to_line(self, line_number: int):
        """
        Set the cursor (and the viewport) active on the given line number.
        """
        block = self.document().findBlockByNumber(line_number)
        if not block.isVisible():
            LOGGER.warning(f"Cannot jump to line {line_number}: line is hided.")
            return
        cursor = QtGui.QTextCursor(block)
        self.setTextCursor(cursor)

    def set_left_margin(self, margin: int):
        """
        Set the margin size for the left side of the viewport.

        Necessary because the teh sidebar already override it.
        """
        self._left_margin = margin
        self._update_margins()

    def set_tab_character(self, character: str):
        """
        Change which characters are used to produce a tabulation when pressing the tab key.

        Args:
            character: anything but usually 4 spaces or the tab character ``\t``
        """
        self._tab_character = character

    def isolate_lines(self, lines: list[int]):
        """
        Make visible only the given lines number.

        Args:
            lines: list of line numbers. starts at 0.
        """
        all_lines = set(range(self.blockCount()))
        lines_to_hide = list(all_lines.difference(set(lines)))
        lines_to_hide.sort()
        self.show_lines(lines)
        self.hide_lines(lines_to_hide)

    def hide_lines(self, lines: Optional[list[int]] = None):
        """
        Hide the given lines number.

        Args:
            lines: list of line numbers. starts at 0.
        """
        lines = lines or range(self.blockCount())

        for line in lines:
            block = self.document().findBlockByNumber(line)
            block.setVisible(False)

        # HACK to trigger a FULL ui refresh, update() doesn't work.
        self.resize(self.width() - 1, self.height())
        self.resize(self.width() + 1, self.height())

    def show_lines(self, lines: Optional[list[int]] = None):
        """
        Make the given lines visible again.

        Pass None to show all lines.
        """
        lines = lines or list(range(self.blockCount()))
        for line in lines:
            block = self.document().findBlockByNumber(line)
            block.setVisible(True)

        # HACK to trigger a FULL ui refresh, update() doesn't work.
        self.resize(self.width() - 1, self.height())
        self.resize(self.width() + 1, self.height())

    # Overrides

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Backtab:
            self._unindent_selection()
            return

        elif event.key() == QtCore.Qt.Key_Tab:
            self._indent_selection()
            return

        elif (
            event.key() == QtCore.Qt.Key_G
            and event.modifiers() & QtCore.Qt.ControlModifier
        ):
            self._on_jump_to_line()

        super().keyPressEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_sidebar_geo()
