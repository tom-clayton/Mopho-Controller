# Synth-Controller

Universal touchscreen midi controller.

Midi control of hardware synths, soft-synths and midi controlled effects.

Synth Controller runs one 'Setup' at a time.

Setups consist of one or more screens of controllers, activated with tabs in an action bar. 

A Setup for a DSI Mopho is provided as an example, more will follow.

Setups can control up to 16 midi devices in one page simultaneously.

Each controller can control one or more midi paramters, even from different synths. And one parameter can be contolled by multiple controllers.

Various types of controllers exist:

    - Horizontal and vertical slide controllers.
    - Swipe controllers.
    - Toggle buttons.
    - Radio buttons.
    - Dropdown option lists.

Utiliy controllers allow loading, saving, sending and receiving synth patches so it also be used as a patch librarian.

Custom setups can be made easily with kivy's kv language, utilising any kivy widgets for layout.

Completely hackable to allow custom controllers and synths with unique features/options.


 
