# uncompyle6 version 3.9.1
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (default, Apr 18 2024, 23:37:34) 
# [GCC 13.2.0]
# Embedded file name: event_extractor/Action.py
NilViewID = -1
ActionFromScreenAnalysis = 'Screen'
ActionFromSystem = 'System'

class Action:

    def __init__(self):
        self.debug_string = '[Action] '
        self.click = 'click'
        self.textClick = 'click'
        self.textViewClickByIndex = 'clickTextViewByIndex'
        self.longClick = 'clickLong'
        self.scroll = 'scroll'
        self.textViewLongClickByIndex = 'clickLongTextViewByIndex'
        self.editText = 'edit'
        self.imageBtnClick = 'clickImgBtn'
        self.imageViewClick = 'clickImgView'
        self.menuItemClick = 'clickMenuItem'
        self.checkboxClick = 'clickCheckBox'
        self.radiobuttonClick = 'clickRadioButton'
        self.togglebuttonClick = 'clickToggleButton'
        self.buttonClick = ''
        self.textViewClick = 'clickIdx'
        self.editTextClick = 'key_event'
        self.tap = 'tap'
        self.actionFromStaticAnalysis = 'Static'
        self.actionFromScreenAnalysis = 'Screen'
        self.actionFromSystem = 'System'
        self.action_id = 0
        self.view_id = 0
        self.view_cis = ''
        self.view_component = None
        self.view_text = ''
        self.action_type = ''
        self.action_cmd = ''
        self.activity_name = ''
        self.action_source = ''
        return

    def set_action_property(self, action_id, view_cis, view_text, action_type, activity_name):
        self.action_id = action_id
        self.view_cis = view_cis
        self.view_text = view_text
        self.action_type = action_type
        self.activity_name = activity_name
        self.action_source = ActionFromScreenAnalysis

    def set_system_action_property(self, action_id, view_cis, action_cmd, activity_name):
        self.action_id = action_id
        self.view_cis = view_cis
        self.action_cmd = action_cmd
        self.activity_name = activity_name
        self.view_id = NilViewID
        self.action_source = ActionFromSystem

    def set_action_cmd(self, action_cmd, view_type):
        if self.view_text is not None:
            sanitized_view_text = self.view_text.replace('\n', '').replace(';', '')
            cmd_tag = view_type + '@"' + sanitized_view_text + '"'
        else:
            cmd_tag = view_type + '@null'
        if view_type == '':
            self.action_cmd = action_cmd
        else:
            self.action_cmd = action_cmd.strip('\n') + ':' + cmd_tag + '\n'
        return
