import wx
import os
import random
import uuid
from . import image_processor
from . import constants

class GeneratePanel(wx.Panel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.source_panel = None

        generate_settings = self.settings.get_generate_settings()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        static_box = wx.StaticBox(self, label="Generate")
        static_box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        # Tiles
        tiles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tiles_label = wx.StaticText(self, label="Tiles:")
        tiles_sizer.Add(tiles_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.tiles_ctrl = wx.SpinCtrl(self, value=str(generate_settings.get('tiles', 1)), min=1, max=9999999)
        self.tiles_ctrl.SetToolTip(constants.TILES_TOOLTIP)
        self.tiles_ctrl.Bind(wx.EVT_SPINCTRL, self.on_setting_changed)
        tiles_sizer.Add(self.tiles_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        static_box_sizer.Add(tiles_sizer, 0, wx.EXPAND | wx.ALL, 5)

        size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        height_label = wx.StaticText(self, label="Height:")
        size_sizer.Add(height_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.height_ctrl = wx.SpinCtrl(self, value=str(generate_settings.get('height', 256)), min=1, max=8192)
        self.height_ctrl.SetToolTip(constants.HEIGHT_TOOLTIP)
        self.height_ctrl.Bind(wx.EVT_SPINCTRL, self.on_setting_changed)
        size_sizer.Add(self.height_ctrl, 0, wx.ALL, 5)

        width_label = wx.StaticText(self, label="Width:")
        size_sizer.Add(width_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.width_ctrl = wx.SpinCtrl(self, value=str(generate_settings.get('width', 256)), min=1, max=8192)
        self.width_ctrl.SetToolTip(constants.WIDTH_TOOLTIP)
        self.width_ctrl.Bind(wx.EVT_SPINCTRL, self.on_setting_changed)
        size_sizer.Add(self.width_ctrl, 0, wx.ALL, 5)
        static_box_sizer.Add(size_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Options Grid
        options_grid_sizer = wx.FlexGridSizer(3, 3, 5, 5)
        options_grid_sizer.AddGrowableCol(1)

        # Rotate
        self.rotate_checkbox = wx.CheckBox(self, label="Rotate")
        self.rotate_checkbox.SetToolTip(constants.ROTATE_CHECKBOX_TOOLTIP)
        self.rotate_checkbox.SetValue(generate_settings.get('rotate', False))
        self.rotate_checkbox.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
        options_grid_sizer.Add(self.rotate_checkbox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.rotate_slider = wx.Slider(self, value=generate_settings.get('rotate_value', 0), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.rotate_slider.SetToolTip(constants.ROTATE_SLIDER_TOOLTIP)
        self.rotate_slider.Bind(wx.EVT_SLIDER, self.on_setting_changed)
        self.rotate_slider.Enable(self.rotate_checkbox.IsChecked())
        options_grid_sizer.Add(self.rotate_slider, 1, wx.ALL | wx.EXPAND, 5)

        self.rotate_value_label = wx.StaticText(self, label=f"{self.rotate_slider.GetValue()}%")
        options_grid_sizer.Add(self.rotate_value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # Flip
        self.flip_checkbox = wx.CheckBox(self, label="Flip")
        self.flip_checkbox.SetToolTip(constants.FLIP_CHECKBOX_TOOLTIP)
        self.flip_checkbox.SetValue(generate_settings.get('flip', False))
        self.flip_checkbox.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
        options_grid_sizer.Add(self.flip_checkbox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.flip_slider = wx.Slider(self, value=generate_settings.get('flip_value', 0), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.flip_slider.SetToolTip(constants.FLIP_SLIDER_TOOLTIP)
        self.flip_slider.Bind(wx.EVT_SLIDER, self.on_setting_changed)
        self.flip_slider.Enable(self.flip_checkbox.IsChecked())
        options_grid_sizer.Add(self.flip_slider, 1, wx.ALL | wx.EXPAND, 5)

        self.flip_value_label = wx.StaticText(self, label=f"{self.flip_slider.GetValue()}%")
        options_grid_sizer.Add(self.flip_value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # Use bigger regions
        self.use_bigger_regions_checkbox = wx.CheckBox(self, label="Use bigger regions")
        self.use_bigger_regions_checkbox.SetToolTip(constants.USE_BIGGER_REGIONS_CHECKBOX_TOOLTIP)
        self.use_bigger_regions_checkbox.SetValue(generate_settings.get('use_bigger_regions', False))
        self.use_bigger_regions_checkbox.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
        options_grid_sizer.Add(self.use_bigger_regions_checkbox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.use_bigger_regions_slider = wx.Slider(self, value=generate_settings.get('bigger_regions_value', 0), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.use_bigger_regions_slider.SetToolTip(constants.USE_BIGGER_REGIONS_SLIDER_TOOLTIP)
        self.use_bigger_regions_slider.Bind(wx.EVT_SLIDER, self.on_setting_changed)
        self.use_bigger_regions_slider.Enable(self.use_bigger_regions_checkbox.IsChecked())
        options_grid_sizer.Add(self.use_bigger_regions_slider, 1, wx.ALL | wx.EXPAND, 5)

        self.use_bigger_regions_value_label = wx.StaticText(self, label=f"{self.use_bigger_regions_slider.GetValue()}%")
        options_grid_sizer.Add(self.use_bigger_regions_value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        static_box_sizer.Add(options_grid_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Output Path
        output_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_path_label = wx.StaticText(self, label="Output Path:")
        output_path_sizer.Add(output_path_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.output_path_ctrl = wx.TextCtrl(self, value=generate_settings.get('output_path', ''))
        self.output_path_ctrl.SetToolTip(constants.OUTPUT_PATH_TOOLTIP)
        self.output_path_ctrl.Bind(wx.EVT_TEXT, self.on_setting_changed)
        output_path_sizer.Add(self.output_path_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        browse_button = wx.Button(self, label="Browse...")
        browse_button.Bind(wx.EVT_BUTTON, self.on_browse)
        output_path_sizer.Add(browse_button, 0, wx.ALL, 5)
        static_box_sizer.Add(output_path_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Export Prefix and Image Type
        export_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        prefix_label = wx.StaticText(self, label="Export Prefix:")
        export_sizer.Add(prefix_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.prefix_ctrl = wx.TextCtrl(self, value=generate_settings.get('export_prefix', 'export_'))
        self.prefix_ctrl.SetToolTip(constants.EXPORT_PREFIX_TOOLTIP)
        self.prefix_ctrl.Bind(wx.EVT_TEXT, self.on_setting_changed)
        export_sizer.Add(self.prefix_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        image_type_label = wx.StaticText(self, label="Image Type:")
        export_sizer.Add(image_type_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.image_type_ctrl = wx.Choice(self, choices=['png', 'jpg', 'bmp'])
        self.image_type_ctrl.SetStringSelection(generate_settings.get('image_type', 'png'))
        self.image_type_ctrl.SetToolTip(constants.IMAGE_TYPE_TOOLTIP)
        self.image_type_ctrl.Bind(wx.EVT_CHOICE, self.on_setting_changed)
        export_sizer.Add(self.image_type_ctrl, 0, wx.ALL, 5)

        static_box_sizer.Add(export_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Generate Button
        self.generate_button = wx.Button(self, label="Generate")
        self.generate_button.SetToolTip(constants.GENERATE_BUTTON_TOOLTIP)
        self.generate_button.Bind(wx.EVT_BUTTON, self.on_generate)
        static_box_sizer.Add(self.generate_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        main_sizer.Add(static_box_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def on_setting_changed(self, event):
        self.rotate_slider.Enable(self.rotate_checkbox.IsChecked())
        self.flip_slider.Enable(self.flip_checkbox.IsChecked())
        self.use_bigger_regions_slider.Enable(self.use_bigger_regions_checkbox.IsChecked())
        self.rotate_value_label.SetLabel(f"{self.rotate_slider.GetValue()}%")
        self.flip_value_label.SetLabel(f"{self.flip_slider.GetValue()}%")
        self.use_bigger_regions_value_label.SetLabel(f"{self.use_bigger_regions_slider.GetValue()}%")

        self.settings.set_setting('Generate', 'tiles', self.tiles_ctrl.GetValue())
        self.settings.set_setting('Generate', 'height', self.height_ctrl.GetValue())
        self.settings.set_setting('Generate', 'width', self.width_ctrl.GetValue())
        self.settings.set_setting('Generate', 'rotate', self.rotate_checkbox.IsChecked())
        self.settings.set_setting('Generate', 'rotate_value', self.rotate_slider.GetValue())
        self.settings.set_setting('Generate', 'flip', self.flip_checkbox.IsChecked())
        self.settings.set_setting('Generate', 'flip_value', self.flip_slider.GetValue())
        self.settings.set_setting('Generate', 'use_bigger_regions', self.use_bigger_regions_checkbox.IsChecked())
        self.settings.set_setting('Generate', 'bigger_regions_value', self.use_bigger_regions_slider.GetValue())
        self.settings.set_setting('Generate', 'output_path', self.output_path_ctrl.GetValue())
        self.settings.set_setting('Generate', 'export_prefix', self.prefix_ctrl.GetValue())
        self.settings.set_setting('Generate', 'image_type', self.image_type_ctrl.GetStringSelection())
        self.update_generate_button_state()

    def on_browse(self, event):
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.output_path_ctrl.SetValue(dirDialog.GetPath())

    def on_generate(self, event):
        if self.source_panel is None:
            wx.MessageBox("Source panel is not set.", "Error", wx.OK | wx.ICON_ERROR)
            return

        source_data = {
            'groups': self.source_panel.group_ctrl.GetValue(),
            'sets': self.source_panel.sets_ctrl.GetValue(),
            'set_names': self.source_panel.set_names,
            'paths': self.source_panel.paths
        }

        generate_settings = {
            'tiles': self.tiles_ctrl.GetValue(),
            'height': self.height_ctrl.GetValue(),
            'width': self.width_ctrl.GetValue(),
            'rotate': self.rotate_checkbox.IsChecked(),
            'rotate_value': self.rotate_slider.GetValue(),
            'flip': self.flip_checkbox.IsChecked(),
            'flip_value': self.flip_slider.GetValue(),
            'use_bigger_regions': self.use_bigger_regions_checkbox.IsChecked(),
            'bigger_regions_value': self.use_bigger_regions_slider.GetValue(),
            'output_path': self.output_path_ctrl.GetValue(),
            'export_prefix': self.prefix_ctrl.GetValue(),
            'image_type': self.image_type_ctrl.GetStringSelection()
        }

        image_processor.generate_images(self, source_data, generate_settings)

    def set_source_panel(self, source_panel):
        self.source_panel = source_panel

    def update_generate_button_state(self):
        all_paths_filled = self.source_panel.are_all_paths_filled() if self.source_panel else False
        output_path_exists = bool(self.output_path_ctrl.GetValue())
        export_prefix_exists = bool(self.prefix_ctrl.GetValue())
        
        if all_paths_filled and output_path_exists and export_prefix_exists:
            self.generate_button.Enable()
        else:
            self.generate_button.Disable()
