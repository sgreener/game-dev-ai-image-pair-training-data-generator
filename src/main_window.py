import wx
from .constants import APP_TITLE
from .settings import AppSettings
from .source_panel import SourcePanel
from .generate_panel import GeneratePanel


class MainWindow(wx.Frame):
    def __init__(self):
        self.settings = AppSettings()

        pos = self.settings.get_window_pos()
        size = self.settings.get_window_size()
        sash_position = self.settings.get_sash_position()

        super().__init__(None, title=APP_TITLE, pos=wx.Point(pos[0], pos[1]), size=wx.Size(size[0], size[1]))
        self.SetMinSize(wx.Size(600, 400))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        source_panel = SourcePanel(splitter, self.settings)
        generate_panel = GeneratePanel(splitter, self.settings)

        source_panel.set_generate_panel(generate_panel)
        generate_panel.set_source_panel(source_panel)

        splitter.SplitVertically(source_panel, generate_panel, sash_position)
        main_sizer.Add(splitter, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.splitter = splitter

        generate_panel.update_generate_button_state()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_MOVE, self.on_move)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_sash_changed, splitter)

    def on_close(self, event):
        self.settings.save_settings()
        self.Destroy()

    def on_move(self, event):
        pos = self.GetPosition()
        self.settings.set_setting('Window', 'x', pos.x)
        self.settings.set_setting('Window', 'y', pos.y)
        event.Skip()

    def on_size(self, event):
        size = self.GetSize()
        self.settings.set_setting('Window', 'width', size.width)
        self.settings.set_setting('Window', 'height', size.height)
        event.Skip()

    def on_sash_changed(self, event):
        sash_position = self.splitter.GetSashPosition()
        self.settings.set_setting('Panels', 'sash_position', sash_position)
        event.Skip()
