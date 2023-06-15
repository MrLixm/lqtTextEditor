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


app = QtWidgets.QApplication()

widget_main = QtWidgets.QWidget()
layout_main = QtWidgets.QVBoxLayout()
layout_header = QtWidgets.QHBoxLayout()
widget = lqtTextEditor.LineNumberedTextEditor()
widget2 = lqtTextEditor.LineNumberedTextEditor()
widget3 = lqtTextEditor.LineNumberedTextEditor()
btn_hide = QtWidgets.QPushButton("Hide")
btn_show = QtWidgets.QPushButton("Show")

widget_main.setLayout(layout_main)
layout_main.addLayout(layout_header)
layout_main.addWidget(widget)
layout_main.addWidget(widget2)
layout_main.addWidget(widget3)
layout_header.addWidget(btn_hide)
layout_header.addWidget(btn_show)

for _widget in [widget, widget2]:
    _widget.setPlainText(demoText)
    _widget.setStyleSheet(
        "QWidget.LineNumberedTextEditor{background-color: rgb(180,180,180);}"
        "QWidget.NumberedSideBarWidget{border-right: 1px solid rgba(255,255,255, 0.5);}"
    )

widget2.setLineWrapMode(widget2.NoWrap)
widget3.setPlainText(demoText * 10000)


def callback1():
    widget.hide_lines(list(range(8, 16)))


def callback2():
    widget.show_lines()


btn_hide.clicked.connect(callback1)
btn_show.clicked.connect(callback2)


stime = time.time()
widget3.hide_lines(list(range(25, 100000)))
print(time.time() - stime)

stime = time.time()
widget3.show_lines()
print(time.time() - stime)

stime = time.time()
widget3.isolate_lines(list(range(5, 90000)))
print(time.time() - stime)

widget_main.resize(500, 300)
widget_main.show()

sys.exit(app.exec_())
