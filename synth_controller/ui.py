
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.actionbar import ActionBar, ActionButton
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder

from controllers import SwipeController

Builder.load_file('ui_elements.kv')

class MainScreen(BoxLayout):
    """The main kivy screen and popups"""
    action_view = ObjectProperty()
    def __init__(self, **kwargs):
        """setup screen"""
        super(MainScreen, self).__init__(**kwargs)
        
        # Register ui events dispatched by popups:
        self.register_event_type('on_load_unconfirmed')
        self.register_event_type('on_load_confirmed')
        self.register_event_type('on_save_unconfirmed')
        self.register_event_type('on_save_confirmed')
        self.register_event_type('on_channel_selection')
        
        self.screens = {'no_screens_label': Label(text='No initial screen set')}
        self.current_screen = 'no_screens_label'
        self.add_widget(self.screens['no_screens_label']) 

    def build_screens(self, filenames):
        """build a dict of widget trees for the screens from the dict of given
        kv files. fill action bar and return the dict"""
        for screen in filenames:
            self.screens[screen] = Builder.load_file(filenames[screen])
        self._fill_action_bar()  
        return self.screens

    def _fill_action_bar(self):
        """create the action_bar and add screens as tabs"""
        self.tabs = []
        for screen in [s for s in self.screens if s != 'no_screens_label']:
            tab = ActionButton(text=screen)
            self.action_view.add_widget(tab, 1)
            tab.bind(on_release=self._on_tab)
            self.tabs.append(tab)
    
    def _on_tab(self, instance):
        """change to new screen acording to tab pressed"""
        if instance.text != self.current_screen:
            self.remove_widget(self.screens[self.current_screen])
            self.add_widget(self.screens[instance.text])
            self.current_screen = instance.text
            self._set_tab_states()

    def set_screen(self, screen):
        """set the current screen"""
        if screen:
            self.remove_widget(self.screens[self.current_screen])
            self.add_widget(self.screens[screen])
            self.current_screen = screen
            self._set_tab_states()
            
    def _set_tab_states(self):
        """set state of tabs"""
        for tab in self.tabs:
            if tab.text == self.current_screen:
                tab.state = 'down'
            else:
                tab.state = 'normal'

    def simple_popup(self, title, message, size=0.5):
        """open a simple one button popup with message and title"""
        content = SimpleDialogue(
                        message=message,
                        confirm=lambda: self.popup.dismiss()
                    )
        self.popup = Popup(
                    title=title,
                    content=content,
                    size_hint=(size, size)
                )
        
        self.popup.open()
        
    def load_dialogue(self, synth):
        """create load dialogue popup"""
        content = LoadDialogue(
                    synth=synth,
                    load=lambda synth, filename:\
                    self.dispatch('on_load_unconfirmed', synth, filename),
                    cancel=lambda: self.popup.dismiss()
                )
        self.popup = Popup(
                    title="Load Patch",
                    content=content,
                    size_hint=(0.9, 0.9)
                )
        
        self.popup.open()

    def save_dialogue(self, synth):
        """create save dialogue popup"""
        content = SaveDialogue(
                    synth=synth,
                    save=lambda synth, filename:\
                    self.dispatch('on_save_unconfirmed', synth, filename),
                    cancel=lambda: self.popup.dismiss()
                )
        self.popup = Popup(
                    title="Save Patch",
                    content=content,
                    size_hint=(0.9, 0.9)
                )
        
        self.popup.open()

    def confirm_popup(self, message, event, data):
        """create confirm dialogue popup with message, event to be triggered
    on confirm and data to be sent on confirm"""
    
        content = ConfirmDialogue(
                    message=message,
                    confirm=lambda: self.dispatch(event, data),
                    cancel=lambda: self.confirm_popup.dismiss()
                )
        self.confirm_popup = Popup(
                    title="Confirm",
                    content=content,
                    size_hint=(0.9, 0.9)
                )
        
        self.confirm_popup.open()

    def channel_selection_popup(self, channels):
        """create a dialogue to select midi channels for each synth"""
        content = ChannelSelectionDialogue(
            channels,
            confirm=lambda channels: self.dispatch('on_channel_selection', channels),
            cancel=lambda: self.confirm_popup.dismiss()
        )
        self.popup = Popup(
                    title="Midi Channel Selection",
                    content=content,
                    size_hint=(0.9, 0.9)
                )
        
        self.popup.open()

  

    def on_load_unconfirmed(self, *args):
        """called when unconfirmed load event dispatched. Dismiss popups"""
        self.popup.dismiss()

    def on_save_unconfirmed(self, *args):
        """called when unconfirmed save event dispatched. Dismiss popups"""
        self.popup.dismiss()

    def on_load_confirmed(self, *args):
        """called when load patch event dispatched. Dismiss popups"""
        self.confirm_popup.dismiss()
        print("loading patch", *args)

    def on_save_confirmed(self, *args):
        """called when save patch event dispatched. Dismiss popups"""
        self.confirm_popup.dismiss()
        print("saving patch", *args)

    def on_channel_selection(self, *args):
        """called when midi selection event dispatched. Dismiss popups"""
        self.popup.dismiss()

class SimpleDialogue(FloatLayout):
    message = StringProperty()
    confirm = ObjectProperty()
                     
class LoadDialogue(FloatLayout):
    load = ObjectProperty()
    cancel = ObjectProperty()
    synth = StringProperty()

class SaveDialogue(FloatLayout):
    save = ObjectProperty()
    cancel = ObjectProperty()
    synth = StringProperty()

class ConfirmDialogue(FloatLayout):
    message = StringProperty()
    confirm = ObjectProperty()
    cancel = ObjectProperty()

class ChannelSelectionDialogue(FloatLayout):
    confirm = ObjectProperty()
    cancel = ObjectProperty()
    box = ObjectProperty()
    def __init__(self, channels, **kwargs):
        """fill dialogue with spinner for each synth"""
        super(ChannelSelectionDialogue, self).__init__(**kwargs)
        self.swipes = {}
        for synth in channels:
            row = BoxLayout(orientation='horizontal')
            row.add_widget(Label(text=synth))
            swipe = SwipeController()
            swipe.property('value').set_min(swipe, 1)
            swipe.property('value').set_max(swipe, 16)
            if channels[synth]:
                swipe.value = channels[synth]
            else:
                swipe.value = 1
            row.add_widget(swipe)
            self.swipes[synth] = swipe
            self.box.add_widget(row, 1)

    def on_confirm_button(self):
        """create dict of results, send to confirm lambda"""
        channels = {}
        for synth in self.swipes:
            channels[synth] = self.swipes[synth].value
        self.confirm(channels)
        print(channels)

