.. _interface:

User Interface
==============

The viewers are highly customizable:

* All panels can be hidden, undocked, stacked, or repositioned on the fly.
* Right-click on the title bar of a visible panel to restore hidden panels.
* Double-click in the plotting region of many viewers to open an options window
  with additional customization controls.

Time is easy and intuitive to navigate:

* Pressing the play button will scroll through data and video in real time, or
  at a higher or lower rate if the speed parameter is changed.
* The arrow/WASD keys allow you to step through time in variable increments.
* Dragging the horizontal slider moves through time quickly.
* Jump to a time by clicking on an event in the event list or a table entry in
  the epoch encoder.

It is also easy to quickly adjust scale:

* To show more or less time at once, right-click and drag right or left to
  contract or expand time.
* Scroll the mouse wheel to zoom in a trace viewer or a video viewer, or to
  rescale the color map in a time-frequency viewer.
* Press the auto scale button to automatically scale signals and color maps.
* Adjust scale mode (real vs arbitrary units) and individual signal gains and
  offsets in the detailed options window of the trace viewer (double click to
  open).

The epoch encoder has many modes of interaction as well:

* Click "Show/hide range" to toggle the display of a time range selector, which
  can be positioned with the mouse or by using dedicated buttons (">").
* Customizable key bindings (default: number keys) allow you to fill the
  selected time range with an epoch if the selector is enabled, or to place new
  epochs of a fixed (and adjustable) duration at the current time if it is
  disabled.
* Click on an epoch to select the corresponding entry in the epoch encoder's
  data table, where you can change the label associated with it.
* Click on a row in the data table to jump to the start of that epoch.
* Double-click on an existing epoch to enable the time range selector and
  position it on that epoch.
* Toggle between epoch insertion modes using the radio buttons or modifying
  shortcut key presses with the Shift key:

    * Mutually exclusive mode: Placing an epoch where there is already one will
      delete the overlapping portion of the old epoch.
    * Overlapping mode: Epochs are permitted to overlap.

* Merge overlapping and adjacent epochs of the same type with the "Merge
  neighbors" button.
* Fill gaps between epochs using the "Fill blank" button.
