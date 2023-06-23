import contextlib
import sys
import time

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import lqtTextEditor


demoText = """one barbatus, fortis frondators virtualiter anhelare de rusticus, azureus castor.
two messis cito ducunt ad clemens visus.
three fidelis, clemens amors recte locus de pius, brevis navis.
four trabem cito ducunt ad altus cursus.
magnum, secundus homos aliquando prensionem de placidus, bi-color magister.
cum rumor tolerare, omnes cottaes pugna noster, albus brabeutaes.
ubi est azureus pes?
resistere patienter ducunt ad flavum adiurator.
brevis, secundus eleatess callide imitari de emeritis, dexter sensorem.
placidus, salvus candidatuss una prensionem de varius, fatalis nixus.
historias sunt guttuss de lotus abaculus.
clemens orgia aliquando apertos olla est.
cum deus assimilant, omnes decores gratia domesticus, regius fermiumes.
magnum, fidelis repressors saepe reperire de camerarius, alter assimilatio.
exemplar de bi-color ausus, perdere axona!
sunt tumultumquees imperium bassus, peritus cottaes.
dexter, alter cursuss grauiter reperire de velox, gratis sensorem.
"""


@contextlib.contextmanager
def time_it(op_name=""):
    start_time = time.time()
    try:
        yield
    finally:
        print(f"{op_name} finished in {round(time.time() - start_time, 6)}s")


@contextlib.contextmanager
def temporary_qapp():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def callback():
        QtWidgets.QApplication.instance().exit()

    timer = QtCore.QTimer()
    timer.timeout.connect(callback)
    try:
        yield
    finally:
        timer.start(1)
        app.exec_()


@temporary_qapp()
def test_main():
    widget_main = QtWidgets.QWidget()
    layout_main = QtWidgets.QVBoxLayout()
    widget_main.setLayout(layout_main)

    layout_header = QtWidgets.QHBoxLayout()
    widget = lqtTextEditor.LinePlainTextEdit()
    widget2 = lqtTextEditor.LinePlainTextEdit()
    widget3 = lqtTextEditor.LinePlainTextEdit()
    btn_hide = QtWidgets.QPushButton("Hide")
    btn_show = QtWidgets.QPushButton("Show")

    layout_main.addLayout(layout_header)
    layout_main.addWidget(widget)
    layout_main.addWidget(widget2)
    layout_main.addWidget(widget3)
    layout_header.addWidget(btn_hide)
    layout_header.addWidget(btn_show)

    for _widget in [widget, widget2]:
        _widget.setPlainText(demoText)
        _widget.setStyleSheet(
            f"QWidget.{lqtTextEditor.LinePlainTextEdit.__name__}{{background-color: rgb(180,180,180);}}"
            f"QWidget.{lqtTextEditor.LineSideBarWidget.__name__}{{border-right: 1px solid rgba(255,255,255, 0.5);}}"
        )

    widget2.setLineWrapMode(widget2.NoWrap)
    widget2.set_left_margin(15)

    widget3text = demoText * 100000
    size = len(widget3text.encode("utf-8")) / 1024**2
    print(f"about to load {size}Mb in widget3")

    with time_it("setPlainText"):
        widget3.setPlainText(widget3text)

    def callback1():
        widget.hide_lines(list(range(8, 16)))

    def callback2():
        widget.show_lines()

    btn_hide.clicked.connect(callback1)
    btn_show.clicked.connect(callback2)

    with time_it("hide_lines"):
        widget3.hide_lines(list(range(25, 100000)))

    with time_it("show_lines"):
        widget3.show_lines()

    with time_it("isolate_lines"):
        widget3.isolate_lines(list(range(5, 90000)))

    widget_main.resize(500, 300)
    widget_main.show()


@temporary_qapp()
def test_qtwidgets():
    widget_main = QtWidgets.QWidget()
    layout_main = QtWidgets.QVBoxLayout()
    widget_main.setLayout(layout_main)

    widget = QtWidgets.QPlainTextEdit()
    layout_main.addWidget(widget)

    heavy_text = demoText * 100000
    size = len(heavy_text.encode("utf-8")) / 1024**2
    print(f"about to load {size}Mb in QPlainTextEdit")

    with time_it("setPlainText"):
        widget.setPlainText(heavy_text)

    widget_main.resize(500, 300)
    widget_main.show()


def main():
    test_main()
    test_qtwidgets()


if __name__ == "__main__":
    main()
