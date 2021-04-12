import re
from kivy.uix.textinput import TextInput

#Class designed to ensure only floats can be used for text input for lat/long values.
#
#Source: https://kivy.org/doc/stable/api_kivy.uix.textinput.html
#
class FloatInput(TextInput):
    
    pat = re.compile('[^-|0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s  in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)
