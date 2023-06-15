import sys

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import lqtTextEditor


demoText = """barbatus, fortis frondators virtualiter anhelare de rusticus, azureus castor.
messis cito ducunt ad clemens visus.
fidelis, clemens amors recte locus de pius, brevis navis.
trabem cito ducunt ad altus cursus.
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
dexter, alter cursuss grauiter reperire de velox, gratis sensorem."""


app = QtWidgets.QApplication()

widget_main = QtWidgets.QWidget()
layout_main = QtWidgets.QVBoxLayout()
widget = lqtTextEditor.LineNumberedTextEditor()
widget2 = lqtTextEditor.LineNumberedTextEditor()

widget_main.setLayout(layout_main)
layout_main.addWidget(widget)
layout_main.addWidget(widget2)

for _widget in [widget, widget2]:
    _widget.setPlainText(demoText)
    _widget.setStyleSheet(
        "QWidget.LineNumberedTextEditor{background-color: rgb(180,180,180);}"
        "QWidget.NumberedSideBarWidget{border-right: 1px solid rgba(255,255,255, 0.5);}"
    )

widget2.setLineWrapMode(widget2.NoWrap)

widget_main.resize(500, 300)
widget_main.show()

sys.exit(app.exec_())
