# Ported from KoDockWidgetTitleBar.cpp which is part of KOffice
# Copyright (c) 2007 Marijn Kruisselbrink <m.kruisselbrink@student.tue.nl>
# Copyright (C) 2007 Thomas Zander <zander@kde.org>
# The code is distributed under GPL 2 or any later version

from PyQt4.QtCore import *
from PyQt4.QtGui import *


def hasFeature(dockwidget, feature):
    return dockwidget.features() & feature == feature



class DockWidgetTitleBarButton(QAbstractButton):


    def __init__(self, titlebar):
        QAbstractButton.__init__(self, titlebar)
        self.setFocusPolicy(Qt.NoFocus)

    def sizeHint(self):
        self.ensurePolished()
        margin = self.style().pixelMetric(QStyle.PM_DockWidgetTitleBarButtonMargin, None, self)
        if self.icon().isNull():
            return QSize(margin, margin)
        iconSize = self.style().pixelMetric(QStyle.PM_SmallIconSize, None, self)
        pm = self.icon().pixmap(iconSize)
        return QSize(pm.width() + margin, pm.height() + margin)


    def enterEvent(self, event):
        if self.isEnabled():
            self.update()
        QAbstractButton.enterEvent(self, event)


    def leaveEvent(self, event):
        if self.isEnabled():
            self.update()
        QAbstractButton.leaveEvent(self, event)


    def paintEvent(self, event):
        p = QPainter(self)
        r = self.rect()
        opt = QStyleOptionToolButton()
        opt.init(self)
        opt.state |= QStyle.State_AutoRaise
        if self.isEnabled() and self.underMouse() and \
           not self.isChecked() and not self.isDown():
            opt.state |= QStyle.State_Raised
        if self.isChecked():
            opt.state |= QStyle.State_On
        if self.isDown():
            opt.state |= QStyle.State_Sunken
        self.style().drawPrimitive(
            QStyle.PE_PanelButtonTool, opt, p, self)
        opt.icon = self.icon()
        opt.subControls = QStyle.SubControls()
        opt.activeSubControls = QStyle.SubControls()
        opt.features = QStyleOptionToolButton.None
        opt.arrowType = Qt.NoArrow
        size = self.style().pixelMetric(QStyle.PM_SmallIconSize, None, self)
        opt.iconSize = QSize(size, size)
        self.style().drawComplexControl(QStyle.CC_ToolButton, opt, p, self)


import os
__icon_path__ = os.path.dirname(os.path.abspath(__file__))

class DockWidgetTitleBar(QWidget):

    
    def __init__(self, dockWidget):
        QWidget.__init__(self, dockWidget)
        
        self.openIcon = QIcon(os.path.join(__icon_path__, "arrow-down.png"))
        self.closeIcon = QIcon(os.path.join(__icon_path__, "arrow-right.png"))

        q = dockWidget
        self.collapseButton = DockWidgetTitleBarButton(self)
        self.collapseButton.setIcon(self.openIcon)

        ##self.connect(self.floatButton, SIGNAL("clicked()"),
                     ##self.toggleFloating)
        ##self.floatButton.setVisible(True)
        ##self.closeButton = DockWidgetTitleBarButton(self)
        ##self.closeButton.setIcon(q.style().standardIcon(
            ##QStyle.SP_TitleBarCloseButton, None, q))
        ##self.connect(self.closeButton, SIGNAL("clicked()"), dockWidget.close)
        ##self.closeButton.setVisible(True)
        self.collapseButton = DockWidgetTitleBarButton(self)
        self.collapseButton.setIcon(self.openIcon)
        self.connect(self.collapseButton, SIGNAL("clicked()"),
                     self.toggleCollapsed)
        self.collapseButton.setVisible(True)
        #self.connect(dockWidget, SIGNAL("featuresChanged(QDockWidget.DockWidgetFeatures)"), self.featuresChanged)
        #self.featuresChanged(0)


    def minimumSizeHint(self):
        return self.sizeHint()


    def sizeHint(self):
        q = self.parentWidget()
        mw = q.style().pixelMetric(QStyle.PM_DockWidgetTitleMargin, None, q)
        fw = q.style().pixelMetric(QStyle.PM_DockWidgetFrameWidth, None, q)
        closeSize = QSize(0, 0)
        ##if self.closeButton:
            ##closeSize = self.closeButton.sizeHint()
        floatSize = QSize(0, 0)
        ##if self.floatButton:
            ##floatSize = self.floatButton.sizeHint()
        hideSize = QSize(0, 0)
        if self.collapseButton:
            hideSize = self.collapseButton.sizeHint()
        buttonHeight = max(max(closeSize.height(), floatSize.height()),
                            hideSize.height()) + 2
        buttonWidth = closeSize.width() + floatSize.width() + hideSize.width()
        titleFontMetrics = q.fontMetrics()
        fontHeight = titleFontMetrics.lineSpacing() + 2 * mw
        height = max(buttonHeight, fontHeight)
        return QSize(buttonWidth + height + 4 * mw + 2 * fw, height)


    def paintEvent(self, event):
        p = QStylePainter(self)
        q = self.parentWidget()
        fw = q.isFloating() and q.style().pixelMetric(
            QStyle.PM_DockWidgetFrameWidth, None, q) or 0
        mw = q.style().pixelMetric(QStyle.PM_DockWidgetTitleMargin, None, q)
        titleOpt = QStyleOptionDockWidgetV2()
        titleOpt.initFrom(q)
        titleOpt.rect = QRect(
            QPoint(fw + mw + self.collapseButton.size().width(), fw),
            QSize(
               self.geometry().width() - (fw * 2) - \
               mw - self.collapseButton.size().width(),
               self.geometry().height() - (fw * 2)))
        titleOpt.title = q.windowTitle()
        titleOpt.closable = hasFeature(q, QDockWidget.DockWidgetClosable)
        titleOpt.floatable = hasFeature(q, QDockWidget.DockWidgetFloatable)
        p.drawControl(QStyle.CE_DockWidgetTitle, titleOpt)


    def resizeEvent(self, event):
        q = self.parentWidget()
        fw = q.isFloating() and q.style().pixelMetric(
            QStyle.PM_DockWidgetFrameWidth, None, q) or 0
        opt = QStyleOptionDockWidgetV2()
        opt.initFrom(q)
        opt.rect = QRect(
            QPoint(fw, fw),
            QSize(
              self.geometry().width() - (fw * 2),
              self.geometry().height() - (fw * 2)))
        opt.title = q.windowTitle()
        opt.closable = hasFeature(q, QDockWidget.DockWidgetClosable)
        opt.floatable = hasFeature(q, QDockWidget.DockWidgetFloatable)

        floatRect = q.style().subElementRect(
            QStyle.SE_DockWidgetFloatButton, opt, q)
        if not floatRect.isNull():
            self.floatButton.setGeometry(floatRect)
        closeRect = q.style().subElementRect(
        QStyle.SE_DockWidgetCloseButton, opt, q)
        if not closeRect.isNull():
            self.closeButton.setGeometry(closeRect)
        top = fw
        if not floatRect.isNull():
            top = floatRect.y()
        elif not closeRect.isNull():
            top = closeRect.y()
        size = self.collapseButton.size()
        if not closeRect.isNull():
            size = self.closeButton.size()
        elif not floatRect.isNull():
            size = self.floatButton.size()
        collapseRect = QRect(QPoint(fw, top), size)
        self.collapseButton.setGeometry(collapseRect)


    def setCollapsed(self, collapsed):
        q = self.parentWidget()
        if q and q.widget() and q.widget().isHidden() != collapsed:
            self.toggleCollapsed()


    def toggleFloating(self):
        q = self.parentWidget()
        q.setFloating(not q.isFloating())


    def toggleCollapsed(self):
        q = self.parentWidget()
        if not q:
            return
        #q.widget().setVisible(q.widget().isHidden())
        #self.collapseButton.setIcon(q.widget().isHidden() and self.closeIcon or self.openIcon)
        q.toggleCollapsed()
        self.collapseButton.setIcon(q.isCollapsed() and self.openIcon or self.closeIcon)


    ##def featuresChanged(self, features):
        ##q = self.parentWidget()
        ##self.closeButton.setVisible(hasFeature(q, QDockWidget.DockWidgetClosable))
        ##self.floatButton.setVisible(hasFeature(q, QDockWidget.DockWidgetFloatable))
        ###self.resizeEvent(None)


'''
##class DockMainWidgetWrapper(QWidget):
##
##
    ##def __init__(self, dockwidget):
        ##QWidget.__init__(self, dockwidget)
        ##self.widget = None
        ##self.widget_height = 0
        ##self.hlayout = QHBoxLayout(self)
        ##self.setLayout(self.hlayout)
##
        ##
    ##def setWidget(self, widget):
        ##self.widget = widget
        ##self.widget_height = widget.height
        ##self.layout().addWidget(widget)
##
##
    ##def isCollapsed(self):
        ##return self.widget.isVisible()
##
##
    ##def setCollapsed(self, flag):
        ##if not flag:
            ##self.widget_height = self.widget.height()
            ##self.setFixedHeight(0)
            ##self.widget.setVisible(False)
        ##else:
            ##self.setFixedHeight(self.widget_height)            
            ##self.widget.setVisible(True)
            ##self.setMinimumHeight(0)
            ##self.setMaximumHeight(2048)
##
##
    ##def sizeHint(self):
        ##if self.widget:
            ##return self.widget.sizeHint()
        ##else:
            ##return QWidget.sizeHint(self)
'''


class DockWidget(QDockWidget):


    def __init__(self, *args):
        QDockWidget.__init__(self, *args)
        self.titleBar = DockWidgetTitleBar(self)
        self.setTitleBarWidget(self.titleBar)
        self.mainWidget = None


    def setWidget(self, widget):
        self.mainWidget = DockMainWidgetWrapper(self)
        self.mainWidget.setWidget(widget)
        QDockWidget.setWidget(self, self.mainWidget)
    

    def setCollapsed(self, flag):
        self.mainWidget.setCollapsed(flag)


    def isCollapsed(self):
        return self.mainWidget.isCollapsed()


    def toggleCollapsed(self):
        self.setCollapsed(not self.isCollapsed())



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = QMainWindow()
    dock1 = DockWidget("1st dockwidget", win)
#    combo =  QComboBox(dock1)
#    dock1.setWidget(combo)
    win.addDockWidget(Qt.TopDockWidgetArea, dock1)
    dock2 = DockWidget("2nd dockwidget")
#    button = QPushButton("Hello, world!", dock2)
#    dock2.setWidget(button)
    win.addDockWidget(Qt.BottomDockWidgetArea, dock2)
    edit = QTextEdit(win)
    win.setCentralWidget(edit)
    win.resize(640, 480)
    win.show()
    app.exec_()
