.. _interface:

User Interface
==============

The viewers are highly customizable:

* All panels can be hidden, undocked, stacked, or repositioned on the fly.
* Right-click (Control-click on Mac) on the title bar of a visible panel to
  restore hidden panels.
* Double-click in the plotting region of many viewers to open an options window
  with additional customization controls.

Time is easy and intuitive to navigate:

* Pressing the play button will scroll through data and video in real time, or
  at a higher or lower rate if the speed parameter is changed.
* The arrow/WASD keys allow you to step through time in variable increments.
* Dragging the horizontal slider along the top moves through time quickly.
* Jump to a time by clicking on an event in the event list or on an arrow
  button in the epoch encoder's data table.

It is also easy to quickly adjust scale and placement:

* To show more or less time at once, right-click (Control-click on Mac) and
  drag right or left to contract or expand time.
* Press the auto scale button to automatically scale signals and color maps.
* Scroll the mouse wheel to zoom in a trace viewer or a video viewer, or to
  rescale the color map in a time-frequency viewer.
* Scroll the mouse wheel on a trace label to adjust the scale of an individual
  trace (``by_channel`` scale mode only).
* Left-click and drag on a trace label to adjust its vertical offset, or in a
  video viewer to reposition the video frame.
* Adjust scale mode (real vs arbitrary units) and individual signal gains and
  offsets in the detailed options window of the trace viewer (double click to
  open).

The epoch encoder has many modes of interaction as well:

* Click "Time range selector" (shortcut: ``r``) to toggle the display of a
  rectangle which can be positioned with the mouse or by using dedicated
  buttons ("Set start >" and "Set stop >"; shortcuts: ``[`` and ``]``).
* Customizable key bindings (default: number keys) allow you to fill the
  selected time range with an epoch if the selector is enabled, or to place new
  epochs of a fixed (and adjustable) duration at the current time if it is
  disabled. Key bindings are displayed to the left of each epoch label.
* Click on an epoch to select the corresponding entry in the epoch encoder's
  data table, where you can change the times or label associated with it.
* Buttons in each row of the data table allow you to jump to, split, duplicate,
  or delete the epoch.
* Double-click on an existing epoch to enable the time range selector and
  position it on that epoch.
* Toggle between epoch insertion modes using the "Allow overlap" button or by
  modifying shortcut key presses with the Shift key:

    * "Allow overlaps" disabled: Placing an epoch where there is already one will
      delete the overlapping portion of the old epoch.
    * "Allow overlaps" enabled: Epochs are permitted to overlap.

* Create new possible epoch labels with the "New label" button.
* Merge overlapping and adjacent epochs of the same type with the "Merge
  neighbors" button.
* Fill gaps between epochs using the "Fill blank" button.
* Click "Save" (shortcut: ``Ctrl+s``, or ``Cmd+s`` on Mac) to write the epochs
  to a file.
* Click "Undo"/"Redo" (shortcuts: ``Ctrl+z``/``Ctrl+y``, or ``Cmd+z``/``Cmd+y``
  on Mac) to move through the history of recent changes made during the current
  session.
