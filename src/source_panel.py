import wx
import os
from wx.lib.scrolledpanel import ScrolledPanel

class ImagePopup(wx.PopupWindow):
    def __init__(self, parent, image, original_size):
        super().__init__(parent)
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.BLACK)
        sizer = wx.BoxSizer(wx.VERTICAL)

        size_label = wx.StaticText(panel, label=f"{original_size[0]}x{original_size[1]}")
        size_label.SetForegroundColour(wx.WHITE)
        sizer.Add(size_label, 0, wx.CENTER | wx.ALL, 2)

        image.Rescale(256, 256, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(image)
        bitmap_ctrl = wx.StaticBitmap(panel, bitmap=wx.BitmapBundle(bmp))
        sizer.Add(bitmap_ctrl, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 1)

        panel.SetSizerAndFit(sizer)
        self.SetSize(panel.GetSize())

class SourcePanel(wx.Panel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.generate_panel = None

        self.paths = [["" for _ in range(2)] for _ in range(2)]
        self.set_names = self.settings.get_set_names()
        self.previews: list[list[wx.StaticBitmap | None]] = [[None for _ in range(2)] for _ in range(2)]
        self.popup = None

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        static_box = wx.StaticBox(self, label="Source")
        static_box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        group_label = wx.StaticText(self, label="Groups:")
        controls_sizer.Add(group_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.group_ctrl = wx.SpinCtrl(self, value="2", min=1, max=100)
        self.group_ctrl.Bind(wx.EVT_SPINCTRL, self.on_update_layout)
        controls_sizer.Add(self.group_ctrl, 0, wx.ALL, 5)

        sets_label = wx.StaticText(self, label="Sets:")
        controls_sizer.Add(sets_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.sets_ctrl = wx.SpinCtrl(self, value="2", min=1, max=6)
        self.sets_ctrl.Bind(wx.EVT_SPINCTRL, self.on_update_layout)
        controls_sizer.Add(self.sets_ctrl, 0, wx.ALL, 5)

        clear_button = wx.Button(self, label="Clear All")
        clear_button.Bind(wx.EVT_BUTTON, self.on_clear_all)
        controls_sizer.Add(clear_button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        static_box_sizer.Add(controls_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.set_names_panel = wx.Panel(self)
        static_box_sizer.Add(self.set_names_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.paths_panel = ScrolledPanel(self)
        self.paths_panel.SetupScrolling()
        static_box_sizer.Add(self.paths_panel, 1, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(static_box_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)

        self.update_layout()

    def set_generate_panel(self, generate_panel):
        self.generate_panel = generate_panel

    def are_all_paths_filled(self):
        for group in self.paths:
            for path in group:
                if not path or not os.path.exists(path):
                    return False
        return True

    def on_update_layout(self, event):
        self.update_layout()

    def update_layout(self):
        groups = self.group_ctrl.GetValue()
        sets = self.sets_ctrl.GetValue()

        # Preserve existing set names
        old_set_names = self.set_names
        self.set_names = ["" for _ in range(sets)]
        for i in range(min(sets, len(old_set_names))):
            self.set_names[i] = old_set_names[i]
        self.settings.set_set_count(sets)

        # Update set names panel
        self.set_names_panel.DestroyChildren()
        set_names_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for s in range(sets):
            set_name_sizer = wx.BoxSizer(wx.VERTICAL)
            label = wx.StaticText(self.set_names_panel, label=f"Set {s+1} Name:")
            set_name_sizer.Add(label, 0, wx.ALL, 5)
            
            name_ctrl = wx.TextCtrl(self.set_names_panel, value=self.set_names[s])
            name_ctrl.Bind(wx.EVT_TEXT, lambda event, index=s: self.on_set_name_changed(event, index))
            set_name_sizer.Add(name_ctrl, 0, wx.EXPAND | wx.ALL, 5)
            
            set_names_sizer.Add(set_name_sizer, 1, wx.EXPAND)

        self.set_names_panel.SetSizer(set_names_sizer)
        self.set_names_panel.Layout()

        # Preserve existing paths
        old_paths = self.paths
        self.paths = [["" for _ in range(sets)] for _ in range(groups)]
        self.previews = [[None for _ in range(sets)] for _ in range(groups)]
        for g in range(min(groups, len(old_paths))):
            for s in range(min(sets, len(old_paths[g]))):
                self.paths[g][s] = old_paths[g][s]

        self.paths_panel.DestroyChildren()
        paths_sizer = wx.BoxSizer(wx.VERTICAL)

        for g in range(groups):
            if g > 0:
                paths_sizer.Add(wx.StaticLine(self.paths_panel), 0, wx.EXPAND | wx.ALL, 5)

            for s in range(sets):
                row_sizer = wx.BoxSizer(wx.HORIZONTAL)
                path_ctrl = wx.TextCtrl(self.paths_panel, value=self.paths[g][s])
                path_ctrl.Bind(wx.EVT_TEXT, lambda event, g=g, s=s: self.on_path_changed(event, g, s))
                row_sizer.Add(path_ctrl, 1, wx.ALL | wx.EXPAND, 5)
                
                browse_button = wx.Button(self.paths_panel, label="Browse...")
                browse_button.Bind(wx.EVT_BUTTON, lambda event, g=g, s=s: self.on_browse(event, g, s))
                row_sizer.Add(browse_button, 0, wx.ALL, 5)

                preview_bitmap = wx.StaticBitmap(self.paths_panel, size=wx.Size(64, 64))
                preview_bitmap.Bind(wx.EVT_ENTER_WINDOW, lambda event, g=g, s=s: self.on_hover_preview(event, g, s))
                preview_bitmap.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_preview)
                row_sizer.Add(preview_bitmap, 0, wx.ALL, 5)
                self.previews[g][s] = preview_bitmap
                self.update_preview(g, s)

                paths_sizer.Add(row_sizer, 0, wx.EXPAND)

        self.paths_panel.SetSizer(paths_sizer)
        self.paths_panel.Layout()
        self.Layout()

        if self.generate_panel:
            self.generate_panel.update_generate_button_state()

    def on_clear_all(self, event):
        groups = self.group_ctrl.GetValue()
        sets = self.sets_ctrl.GetValue()
        self.paths = [["" for _ in range(sets)] for _ in range(groups)]
        self.update_layout()
        if self.generate_panel:
            self.generate_panel.update_generate_button_state()

    def on_set_name_changed(self, event, index):
        self.set_names[index] = event.GetString()
        self.settings.set_set_name(index, event.GetString())

    def on_path_changed(self, event, group_index, set_index):
        self.paths[group_index][set_index] = event.GetString()
        self.update_preview(group_index, set_index)
        if self.generate_panel:
            self.generate_panel.update_generate_button_state()

    def on_browse(self, event, group_index, set_index):
        with wx.FileDialog(self, "Open file", wildcard="All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.paths[group_index][set_index] = pathname
            
            button = event.GetEventObject()
            row_sizer = button.GetContainingSizer()
            text_ctrl = row_sizer.GetChildren()[0].GetWindow()
            text_ctrl.SetValue(pathname)
            self.update_preview(group_index, set_index)
            if self.generate_panel:
                self.generate_panel.update_generate_button_state()

    def update_preview(self, group_index, set_index):
        path = self.paths[group_index][set_index]
        preview_ctrl = self.previews[group_index][set_index]

        if preview_ctrl and os.path.exists(path):
            image = wx.Image(path, wx.BITMAP_TYPE_ANY)
            if image.IsOk():
                image.Rescale(64, 64, wx.IMAGE_QUALITY_HIGH)
                bitmap = wx.Bitmap(image)
                preview_ctrl.SetBitmap(wx.BitmapBundle(bitmap))
            else:
                preview_ctrl.SetBitmap(wx.NullBitmap)
        elif preview_ctrl:
            preview_ctrl.SetBitmap(wx.NullBitmap)

    def on_hover_preview(self, event, group_index, set_index):
        path = self.paths[group_index][set_index]
        if os.path.exists(path):
            image = wx.Image(path, wx.BITMAP_TYPE_ANY)
            if image.IsOk():
                original_size = (image.GetWidth(), image.GetHeight())
                self.popup = ImagePopup(self, image.Copy(), original_size)
                pos = event.GetEventObject().ClientToScreen((0, 0))
                size = event.GetEventObject().GetSize()
                self.popup.Position(pos, wx.Size(0, size.y))
                self.popup.Show(True)

    def on_leave_preview(self, event):
        if self.popup:
            self.popup.Destroy()
            self.popup = None
