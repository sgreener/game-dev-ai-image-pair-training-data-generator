import configparser
import os

class AppSettings:
    def __init__(self, file_path='settings.ini'):
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.file_path):
            self._create_default_settings()
        else:
            self.config.read(self.file_path)

    def _create_default_settings(self):
        self.config['Window'] = {
            'x': '100',
            'y': '100',
            'width': '800',
            'height': '600'
        }
        self.config['Panels'] = {
            'sash_position': '400'
        }
        self.config['SetNames'] = {
            'count': '2',
            'set_1_name': '',
            'set_2_name': ''
        }
        self.config['Generate'] = {
            'tiles': '1',
            'height': '256',
            'width': '256',
            'rotate': 'False',
            'rotate_value': '0',
            'flip': 'False',
            'flip_value': '0',
            'use_bigger_regions': 'False',
            'bigger_regions_value': '0',
            'output_path': '',
            'export_prefix': 'export_',
            'image_type': 'png'
        }
        self.config['Sets'] = {
            'count': '2',
            'set_1': '',
            'set_2': ''
        }
        self.save_settings()

    def get_setting(self, section, key):
        return self.config.get(section, key)

    def get_window_pos(self):
        x = self.config.getint('Window', 'x')
        y = self.config.getint('Window', 'y')
        return x, y

    def get_window_size(self):
        width = self.config.getint('Window', 'width')
        height = self.config.getint('Window', 'height')
        return width, height

    def get_sash_position(self):
        return self.config.getint('Panels', 'sash_position', fallback=400)

    def get_set_names(self):
        count = self.config.getint('SetNames', 'count', fallback=2)
        names = []
        for i in range(count):
            names.append(self.config.get('SetNames', f'set_{i+1}_name', fallback=''))
        return names
 
    def set_set_name(self, index, name):
        if not self.config.has_section('SetNames'):
            self.config.add_section('SetNames')
        self.config.set('SetNames', f'set_{index+1}_name', name)

    def set_set_count(self, count):
        if not self.config.has_section('SetNames'):
            self.config.add_section('SetNames')
        self.config.set('SetNames', 'count', str(count))

    def get_generate_settings(self):
        settings = {}
        if self.config.has_section('Generate'):
            settings['tiles'] = self.config.getint('Generate', 'tiles', fallback=1)
            settings['height'] = self.config.getint('Generate', 'height', fallback=256)
            settings['width'] = self.config.getint('Generate', 'width', fallback=256)
            settings['rotate'] = self.config.getboolean('Generate', 'rotate', fallback=False)
            settings['rotate_value'] = self.config.getint('Generate', 'rotate_value', fallback=0)
            settings['flip'] = self.config.getboolean('Generate', 'flip', fallback=False)
            settings['flip_value'] = self.config.getint('Generate', 'flip_value', fallback=0)
            settings['use_bigger_regions'] = self.config.getboolean('Generate', 'use_bigger_regions', fallback=False)
            settings['bigger_regions_value'] = self.config.getint('Generate', 'bigger_regions_value', fallback=0)
            settings['output_path'] = self.config.get('Generate', 'output_path', fallback='')
            settings['export_prefix'] = self.config.get('Generate', 'export_prefix', fallback='export_')
            settings['image_type'] = self.config.get('Generate', 'image_type', fallback='png')
        return settings

    def get_set_count(self):
        return self.config.getint('Sets', 'count', fallback=2)

    def get_set_paths(self):
        names = []
        count = self.get_set_count()
        for i in range(count):
            names.append(self.config.get('Sets', f'set_{i+1}', fallback=''))
        return names

    def set_setting(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

    def save_settings(self):
        with open(self.file_path, 'w') as configfile:
            self.config.write(configfile)
