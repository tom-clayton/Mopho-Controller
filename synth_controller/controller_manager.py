
from controllers import BaseController, RadioController,\
                        RadioButton, TestController,\
                        DropDownController


class ControllerManager(object):
    """Manages controllers"""

    def __init__(self, screens):
        """walk screens widget trees and keep reference of all controllers.""" 
        self.screens = screens
        self.controllers = []
        for screen in self.screens.values():
            print(screen)
            self._walk_tree(screen, self._collect_controllers)
        self._propigate_properties()      

    def _propigate_properties(self):
        """propigate synth and nrpn properties to all widget's children
        who do not have property set"""
        for screen in self.screens.values():
            self._walk_tree(
                        screen,
                        self._propigate_property_if_type,
                        'default',
                        'synth',
                        BaseController
                    )
            self._walk_tree(
                        screen,
                        self._propigate_property_if_type,
                        None,
                        'nrpn',
                        BaseController
                    )

    @property
    def synths(self):
        """return a list of synths controlled by controllers""" 
        return list(set([c.synth for c in self.controllers]))

    def set_channels(self, channels):
        """set channel for each controller acding to its synth as set in
        'channels' dict"""
        for controller in self.controllers:
            controller.channel = channels[controller.synth]
    
    def initialise_controllers(
            self,
            options_lists,
            midi_send_func,
            load_confirm_func
        ):
        """for midi controllers:
        link controllers with same nrpn,
        bind with midi send function,
        add buttons to radio controllers,
        add options to dropdown controllers,
        display selected option for each controller.
        return list of synths found.
        for utility controllers:
        bind to utility functions"""
        print(len(self.controllers))
        
        for controller in self.controllers:
            if isinstance(controller, BaseController):
                # link controllers:
                self._link_controllers(controller)
                
                # bind midi send
                controller.bind(
                    on_send=lambda _, channel, nrpn, value:\
                                midi_send_func(channel, nrpn, value)
                )
                
                # set RadioButtons groups:
                if isinstance(controller, RadioController):
                    self._walk_tree(
                                controller,
                                self._set_property_if_type,
                                controller.group,
                                'group',
                                RadioButton,
                            )

                # set DropDownControllers options:
                if type(controller) == DropDownController:
                    try:
                        controller.add_options(
                            options_lists[controller.synth][controller.option_list]
                        )
                    except (AttributeError, KeyError):
                        pass
                        # log screen error
                        
                # run controller setup and display current value:
                controller.setup()
                controller.display_selected()

            else: # UtilityController
                controller.bind(
                    on_load_unconfirmed=lambda _, data: load_confirm_func(data)
                )


    def _walk_tree(self, widget, func, value=None, *args):
        """traverse widget tree branch from 'widget' onwards, calling 'func'
    on each widget"""
        value = func(widget, value, *args)
        for child in widget.children:
            self._walk_tree(child, func, value, *args)

    def _collect_controllers(self, widget, _):
        """add object to reference list if is of correct type"""
        if isinstance(widget, BaseController):
            self.controllers.append(widget)

    def _set_property_if_type(self, widget, value, prop, w_type):
        """set widgets property 'prop' to 'value' if widget is of type 'w_type'
        and it is not already set."""
        if isinstance(widget, w_type) and not widget.property(prop).get(widget):
            widget.property(prop).set(widget, value)
        return value

    def _propigate_property_if_type(self, widget, value, prop, w_type):
        """set widgets property 'prop' to 'value' if widget is of type 'w_type'
        and it is not already set.
        if property was already set return already set value,
        else return 'value'"""
        try:
            new_value = widget.property(prop).get(widget) or value
        except KeyError:
            new_value = value
           
        if isinstance(widget, w_type) and new_value:
            widget.property(prop).set(widget, new_value)
        #print(widget, value, new_value)
        return new_value
    
    def _link_controllers(self, con_i):
        """link controllers with the same channel and nrpn"""
        for con_j in self.controllers:
            if con_i is not con_j and con_i.channel == con_j.channel\
                and con_i.nrpn == con_j.nrpn:
                    con_i.linked.append(con_j)
        
    def set_controller_value(self, channel, nrpn, value):
        """sets value on given controller"""
        print(f"incoming: {channel} {nrpn} {value}")
        for controller in self.controllers:
            if controller.channel == channel and controller.nrpn == nrpn:
                controller.set_without_sending_midi(value)

    def set_controller_values(self, synth, nrpn_order, data):
        """set each byte in data to corresponding nrpn in nrpn_order if it
        is of given synth"""
        for i, byte in enumerate(data):
            self.set_controller_value(synth, nrpns[i], byte)

    def get_controller_values(self, synth, nrpn_order):
        """return all controller values for synth in order given
           as a tuple of ints"""
        output = []
        for nrpn in nrpn_order:
            for controller in [c for c in self.controllers\
                                if c.synth == synth and c.nrpn == nrpn]:
                output.append(controller.get_value())
        return tuple(output)

    def send_all(self, synth):
        """send value for every controller for given synth"""
        for controller in [c for c in self.controllers if c.synth == synth]:
            controller.send_value()

