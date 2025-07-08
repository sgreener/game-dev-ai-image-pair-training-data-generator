import wx
from .main_window import MainWindow

class App(wx.App):
    def OnInit(self):
        self.frame = MainWindow()
        self.frame.Show()
        return True

    def OnExit(self):
        return 0
