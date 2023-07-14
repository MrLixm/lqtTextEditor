import logging
import sys
from pathlib import Path

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import lqtTextEditor


logging.basicConfig(
    level=logging.DEBUG,
    format="{levelname: <7} | {asctime} [{name: >30}]{message}",
    style="{",
)

demoText = """Fluke belaying pin hang the jib hearties brigantine. Lanyard smartly ho dead men tell no tales clap of thunder.
Rope's end chantey wherry gangway Pieces of Eight. Shrouds lookout jib matey coffer.
Cable prow Barbary Coast brigantine crack Jennys tea cup. Strike colors clap of thunder dance the hempen jig hearties Sink me.

Tackle gaff broadside Sea Legs hearties. Rigging square-rigged cackle fruit tackle measured fer yer chains.

Driver weigh anchor run a rig hail-shot case shot. Line coffer rope's end lateen sail topgallant.
Pirate pillage black jack yawl carouser. Mizzenmast yard crack Jennys tea cup.
Transom marooned hempen halter loot fire in the hole. Furl long clothes Pieces of Eight Spanish Main case shot.

Cat o'nine tails crack Jennys tea cup Blimey chase guns strike colors. Black jack Blimey driver.

Fire ship gally trysail furl lookout. Gabion aft landlubber or just lubber yard scourge of the seven seas.
Man-of-war cog weigh anchor to go on account hogshead. Capstan hulk spirits lass barque.
Clipper no prey, no pay spanker gunwalls black jack. Avast spyglass yo-ho-ho chase guns Jack Tar.
Stern Sea Legs grog marooned blow the man down. Handsomely long boat snow jack quarterdeck.
Heave to crack Jennys tea cup loot belaying pin keel. Hogshead spike cable to go on account Jack Tar.

Black jack crimp transom provost Jack Ketch. Tack man-of-war bucko knave Chain Shot.

Galleon Blimey topsail cable parley. """

app = QtWidgets.QApplication()

widget_main = QtWidgets.QWidget()
widget_main.setWindowTitle("lqtTextEditor")
layout_main = QtWidgets.QVBoxLayout()
widget_main.setLayout(layout_main)

widget = lqtTextEditor.LinePlainTextEdit()
widget.setPlainText(demoText * 1000)
layout_main.addWidget(widget)

widget_main.resize(500, 300)
widget_main.show()

sys.exit(app.exec_())
