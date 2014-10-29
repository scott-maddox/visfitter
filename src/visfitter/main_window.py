#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of VisFitter.
#
#   VisFitter is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   VisFitter is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with VisFitter.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#############################################################################

# std lib imports
import os.path
import logging
log = logging.getLogger(__name__)

# third party imports
from PySide import QtGui, QtCore
import numpy
from scipy.optimize import minimize
import pyqtgraph as pg
from pyqtgraph.graphicsItems.PlotItem import PlotItem
# Use black text on white background
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# local imports
from .version import __version__
from . import parser
from . import linear_regression


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize private variables
        self.plot = None

        # Initialize QSettings object
        self.settings = QtCore.QSettings()

        # Initialize GUI stuff
        self.initUI()

    @QtCore.Slot(str)
    def setStatusText(self, status):
        self.statusLabel.setText(status)

    def initUI(self):
        self.aboutAction = QtGui.QAction('&About', self)
        self.aboutAction.triggered.connect(self.about)

        self.openAction = QtGui.QAction('&Open', self)
        self.openAction.setStatusTip('Open a data set')
        self.openAction.setToolTip('Open a data set')
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.triggered.connect(self.openFile)

        self.closeAction = QtGui.QAction('Close &Window', self)
        self.closeAction.setStatusTip('Close the Window')
        self.closeAction.setToolTip('Close the Window')
        self.closeAction.setShortcut('Ctrl+W')
        self.closeAction.triggered.connect(self.close)

        self.fitLSAction = QtGui.QAction('Least Squares', self)
        self.fitLSAction.setStatusTip('Fit using the least squares')
        self.fitLSAction.setToolTip('Fit using the least squares')
        self.fitLSAction.triggered.connect(self.plotLinearLeastSquares)

        self.fitLMSAction = QtGui.QAction('Least Median of Squares', self)
        self.fitLMSAction.setStatusTip('Fit using the least median of squares')
        self.fitLMSAction.setToolTip('Fit using the least median of squares')
        self.fitLMSAction.triggered.connect(self.plotLinearLeastMedianOfSquares)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.closeAction)
        fitMenu = menubar.addMenu('Fi&t')
        fitMenu.addAction(self.fitLSAction)
        fitMenu.addAction(self.fitLMSAction)
        aboutMenu = menubar.addMenu('&About')
        aboutMenu.addAction(self.aboutAction)

        statusBar = self.statusBar()
        self.statusLabel = QtGui.QLabel('')
        statusBar.addWidget(self.statusLabel, stretch=1)

        self.view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.view)
        self.plot = self.view.addPlot()
        self.view.addItem(self.plot, 0, 0)

        self.setWindowTitle('VisFitter')
        from .resources.icons import logoIcon
        self.setWindowIcon(logoIcon)
        self.setMinimumSize(576, 432)
        self.readWindowSettings()

    def fitLS(self):
        pass

    def openFile(self):
        lastOpened = self.settings.value('lastOpened', '')
        filepath, _filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a PL spectrum file',
                                dir=lastOpened)
        if not filepath:
            return
        self.settings.setValue('lastOpened', filepath)

        # Read in the data, and plot it
        self.x, self.y = parser.getXY(filepath)
        self.plot.clearPlots()
        self.plotXY()
#         self.plotLinearLeastSumOfSquares()
#         self.plotLinearLeastMedianOfSquares()

    def plotXY(self):
        self.scatter = self.plot.plot(self.x, self.y,
                                      pen=None, symbol='o')

    def plotLinearLeastSquares(self):
        alpha, beta = linear_regression.leastSquares(self.x, self.y)
        x = numpy.array([self.x.min(), self.x.max()])
        y = alpha + beta * x
        self.scatter = self.plot.plot(x, y, pen=pg.mkPen('r'))

    def plotLinearLeastMedianOfSquares(self):
        alpha, beta = linear_regression.leastMedianOfSquaresCrude(self.x,
                                                                  self.y)
        x = numpy.array([self.x.min(), self.x.max()])
        y = alpha + beta * x
        self.scatter = self.plot.plot(x, y, pen=pg.mkPen('b'))

    def about(self):
        title = 'About VisFitter'
        text = ('VisFitter\n'
                'Version {}\n'
                '\n'
                'Copyright (c) 2013-2014, Scott J Maddox\n'
                '\n'
                'VisFitter is free software: you can redistribute it'
                ' and/or modify it under the terms of the GNU Affero General'
                ' Public License as published by the Free Software Foundation,'
                ' either version 3 of the License, or (at your option) any'
                ' later version.\n'
                '\n'
                'VisFitter is distributed in the hope that it will be'
                ' useful, but WITHOUT ANY WARRANTY; without even the implied'
                ' warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR'
                ' PURPOSE.  See the GNU Affero General Public License for'
                ' more details.\n'
                '\n'
                'You should have received a copy of the GNU Affero General'
                ' Public License along with VisFitter.  If not, see'
                ' <http://www.gnu.org/licenses/>.'
                ''.format(__version__))
        QtGui.QMessageBox.about(self, title, text)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def moveTopLeft(self):
        p = QtGui.QDesktopWidget().availableGeometry().topLeft()
        self.move(p)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit?',
                'Are you sure you want to quit?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.writeWindowSettings()
            event.accept()
        else:
            event.ignore()

    def writeWindowSettings(self):
        self.settings.setValue("MainWindow/size", self.size())
        self.settings.setValue("MainWindow/pos", self.pos())

    def readWindowSettings(self):
        self.resize(self.settings.value("MainWindow/size",
                                         QtCore.QSize(1280, 800)))
        pos = self.settings.value("MainWindow/pos")
        if pos is None:
            self.moveCenter()  # default to centered
        else:
            self.move(pos)
