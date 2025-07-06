from matplotlib import colormaps
import matplotlib.colors
import numpy as np
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_MultiChannel_ParamController
from .datasource import (
    AnalogSignalFromNeoRawIOSource,
)
from .myqt import QT

default_params = [
    {"name": "xsize", "type": "float", "value": 3.0, "step": 0.1},
    {"name": "xratio", "type": "float", "value": 0.3, "step": 0.1, "limits": (0, 1)},
    {"name": "vline_color", "type": "color", "value": "#FFFFFFAA"},
    {"name": "label_fill_color", "type": "color", "value": "#222222DD"},
    {"name": "label_size", "type": "int", "value": 8, "limits": (1, np.inf)},
    {"name": "display_labels", "type": "bool", "value": False},
    {
        "name": "decimation_method",
        "type": "list",
        "value": "min_max",
        "limits": [
            "min_max",
            "mean",
            "pure_decimate",
        ],
    },
    {
        "name": "colormap",
        "type": "list",
        "value": "viridis",
        "limits": [
            "inferno",
            "viridis",
            "jet",
            "gray",
            "hot",
        ],
    },
]

default_by_channel_params = [
    {"name": "color", "type": "color", "value": "#55FF00"},
    {"name": "gain", "type": "float", "value": 1, "step": 0.1, "decimals": 8},
    {"name": "visible", "type": "bool", "value": True},
]


class TraceImageViewer_ParamController(Base_MultiChannel_ParamController):
    def __init__(self, parent=None, viewer=None):
        Base_MultiChannel_ParamController.__init__(
            self, parent=parent, viewer=viewer, with_visible=True, with_color=False
        )

        # raw_gains and raw_offsets are distinguished from adjustable gains and
        # offsets associated with this viewer because it makes placement of the
        # baselines and labels very easy for both raw and in-memory sources
        if isinstance(self.viewer.source, AnalogSignalFromNeoRawIOSource):
            # use raw_gains and raw_offsets from the raw source
            self.raw_gains = self.viewer.source.get_gains()
        else:
            # use 1 and 0 for in-memory sources, which have already been scaled
            # properly
            self.raw_gains = np.ones(self.viewer.source.nb_channel)

    @property
    def selected(self):  # Is this ever used? Safe to remove?
        selected = np.ones(self.viewer.source.nb_channel, dtype=bool)
        if self.viewer.source.nb_channel > 1:
            selected[:] = False
            selected[[ind.row() for ind in self.qlist.selectedIndexes()]] = True
        return selected

    @property
    def visible_channels(self):
        visible = [
            self.viewer.by_channel_params["ch{}".format(i), "visible"]
            for i in range(self.source.nb_channel)
        ]
        return np.array(visible, dtype="bool")

    @property
    def gains(self):
        gains = [
            self.viewer.by_channel_params["ch{}".format(i), "gain"]
            for i in range(self.source.nb_channel)
        ]
        return np.array(gains)

    @gains.setter
    def gains(self, val):
        for c, v in enumerate(val):
            self.viewer.by_channel_params["ch{}".format(c), "gain"] = v

    @property
    def total_gains(self):
        # compute_rescale sets adjustable gains and offsets such that
        #     data_curves = (chunk * raw_gains + raw_offsets) * gains + offsets
        #                 = chunk * (raw_gains * gains) + (raw_offsets * gains + offsets)
        #                 = chunk * total_gains + total_offsets
        return self.raw_gains * self.gains

    def on_channel_visibility_changed(self):
        pass
        self.viewer.refresh()

    def on_but_ygain_zoom(self):
        factor = self.sender().factor
        self.apply_ygain_zoom(factor)

    def apply_ygain_zoom(self, factor_ratio):
        self.viewer.all_params.blockSignals(True)
        self.gains = self.gains * factor_ratio
        self.viewer.all_params.blockSignals(False)
        self.viewer.refresh()


class DataGrabber(QT.QObject):
    data_ready = QT.pyqtSignal(float, float, float, object, object)

    def __init__(self, source, viewer, parent=None):
        QT.QObject.__init__(self, parent)
        self.source = source
        self.viewer = viewer
        self._max_point = 3000

    def get_data(
        self,
        t,
        t_start,
        t_stop,
        total_gains,
        visibles,
        decimation_method,
    ):
        i_start, i_stop = (
            self.source.time_to_index(t_start),
            self.source.time_to_index(t_stop) + 2,
        )

        ds_ratio = (i_stop - i_start) // self._max_point + 1

        if ds_ratio > 1:
            i_start = i_start - (i_start % ds_ratio)
            i_stop = i_stop - (i_stop % ds_ratio)

        # clip it
        i_start = max(0, i_start)
        i_start = min(i_start, self.source.get_length())
        i_stop = max(0, i_stop)
        i_stop = min(i_stop, self.source.get_length())
        if ds_ratio > 1:
            # after clip
            i_start = i_start - (i_start % ds_ratio)
            i_stop = i_stop - (i_stop % ds_ratio)

        sigs_chunk = self.source.get_chunk(i_start=i_start, i_stop=i_stop)

        data_curves = sigs_chunk[:, visibles].T.copy()
        if data_curves.dtype != "float32":
            data_curves = data_curves.astype("float32")

        if ds_ratio > 1:
            small_size = data_curves.shape[1] // ds_ratio
            if decimation_method == "min_max":
                small_size *= 2

            small_arr = np.empty(
                (data_curves.shape[0], small_size), dtype=data_curves.dtype
            )

            if decimation_method == "min_max" and data_curves.size > 0:
                full_arr = data_curves.reshape(data_curves.shape[0], -1, ds_ratio)
                small_arr[:, ::2] = full_arr.max(axis=2)
                small_arr[:, 1::2] = full_arr.min(axis=2)
            elif decimation_method == "mean" and data_curves.size > 0:
                full_arr = data_curves.reshape(data_curves.shape[0], -1, ds_ratio)
                small_arr[:, :] = full_arr.mean(axis=2)
            elif decimation_method == "pure_decimate":
                small_arr[:, :] = data_curves[:, ::ds_ratio]
            elif data_curves.size == 0:
                pass

            data_curves = small_arr

        data_curves *= total_gains[visibles, None]

        return (
            t,
            t_start,
            t_stop,
            visibles,
            data_curves,
        )

    def on_request_data(
        self,
        t,
        t_start,
        t_stop,
        total_gains,
        visibles,
        decimation_method,
    ):
        if self.viewer.t != t:
            return

        (
            t,
            t_start,
            t_stop,
            visibles,
            data_curves,
        ) = self.get_data(t, t_start, t_stop, total_gains, visibles, decimation_method)

        self.data_ready.emit(
            t,
            t_start,
            t_stop,
            visibles,
            data_curves,
        )


class TraceImageLabelItem(pg.TextItem):
    label_dragged = QT.pyqtSignal(float)
    label_ygain_zoom = QT.pyqtSignal(float)

    def __init__(self, **kwargs):
        pg.TextItem.__init__(self, **kwargs)

        self.dragOffset = None

    def mouseDragEvent(self, ev):
        """Emit the new y-coord of the label as it is dragged"""

        if ev.button() != QT.LeftButton:
            ev.ignore()
            return
        else:
            ev.accept()

        if ev.isStart():
            # To avoid snapping the label to the mouse cursor when the drag
            # starts, we determine the offset of the position where the button
            # was first pressed down relative to the label's origin/anchor, in
            # plot coordinates
            self.dragOffset = self.mapToParent(ev.buttonDownPos()) - self.pos()

        # The new y-coord for the label is the mouse's current position during
        # the drag with the initial offset removed
        new_y = (self.mapToParent(ev.pos()) - self.dragOffset).y()
        self.label_dragged.emit(new_y)

    def wheelEvent(self, ev):
        """Emit a yzoom factor for the associated trace"""
        if ev.modifiers() == QT.Qt.ControlModifier:
            z = 5.0 if ev.delta() > 0 else 1 / 5.0
        else:
            z = 1.1 if ev.delta() > 0 else 1 / 1.1
        self.label_ygain_zoom.emit(z)
        ev.accept()


class TraceImageViewer(BaseMultiChannelViewer):
    _default_params = default_params
    _default_by_channel_params = default_by_channel_params

    _ControllerClass = TraceImageViewer_ParamController

    request_data = QT.pyqtSignal(float, float, float, object, object, object)

    def __init__(self, useOpenGL=None, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)

        self.make_params()

        # Is there any advantage to using OpenGL for this viewer?
        self.set_layout(useOpenGL=useOpenGL)

        self.make_param_controller()

        self.viewBox.doubleclicked.connect(self.show_params_controller)

        self.change_color_scale()
        self.initialize_plot()

        self.thread = QT.QThread(parent=self)
        self.datagrabber = DataGrabber(source=self.source, viewer=self)
        self.datagrabber.moveToThread(self.thread)
        self.thread.start()

        self.datagrabber.data_ready.connect(self.on_data_ready)
        self.request_data.connect(self.datagrabber.on_request_data)

        self.params.param("xsize").setLimits((0, np.inf))

    def closeEvent(self, event):
        event.accept()
        self.thread.quit()
        self.thread.wait()

    def change_color_scale(self):
        N = 512
        cmap_name = self.params["colormap"]
        cmap = colormaps.get_cmap(cmap_name).resampled(N)
        lut = []
        for i in range(N):
            r, g, b, _ = matplotlib.colors.ColorConverter().to_rgba(cmap(i))
            lut.append([r * 255, g * 255, b * 255])
        self.lut = np.array(lut, dtype="uint8")

    def initialize_plot(self):
        self.vline = pg.InfiniteLine(
            angle=90, movable=False, pen=self.params["vline_color"]
        )
        self.vline.setZValue(1)  # ensure vline is above plot elements
        self.plot.addItem(self.vline)

        self.image = pg.ImageItem()
        self.plot.addItem(self.image)

        self.channel_labels = []
        for c in range(self.source.nb_channel):
            color = self.by_channel_params["ch{}".format(c), "color"]
            ch_name = "{}: {}".format(c, self.source.get_channel_name(chan=c))
            label = TraceImageLabelItem(
                text=ch_name,
                color=color,
                anchor=(0, 0.5),
                border=None,
                fill=self.params["label_fill_color"],
            )
            label.setZValue(2)  # ensure labels are drawn above scatter
            font = label.textItem.font()
            font.setPointSize(self.params["label_size"])
            label.setFont(font)

            self.plot.addItem(label)
            self.channel_labels.append(label)

        self.viewBox.xsize_zoom.connect(self.params_controller.apply_xsize_zoom)
        self.viewBox.ygain_zoom.connect(self.params_controller.apply_ygain_zoom)

    def on_param_change(self, params=None, changes=None):
        for param, change, data in changes:
            if change != "value":
                continue
            if param.name() == "vline_color":
                self.vline.setPen(self.params["vline_color"])
            if param.name() == "label_fill_color":
                for label in self.channel_labels:
                    label.fill = pg.mkBrush(self.params["label_fill_color"])
            if param.name() == "label_size":
                for label in self.channel_labels:
                    font = label.textItem.font()
                    font.setPointSize(self.params["label_size"])
                    label.setFont(font)
            if param.name() == "colormap":
                self.change_color_scale()

        self.refresh()

    def refresh(self):
        # ~ print('TraceViewer.refresh', 't', self.t)
        xsize = self.params["xsize"]
        xratio = self.params["xratio"]
        t_start, t_stop = self.t - xsize * xratio, self.t + xsize * (1 - xratio)
        (visibles,) = np.nonzero(self.params_controller.visible_channels)
        total_gains = self.params_controller.total_gains

        self.request_data.emit(
            self.t,
            t_start,
            t_stop,
            total_gains,
            visibles,
            self.params["decimation_method"],
        )

    def on_data_ready(
        self,
        t,
        t_start,
        t_stop,
        visibles,
        data_curves,
    ):
        if self.t != t:  # Under what circumstances can this happen?
            return

        self.image.show()  # Why does this happen before the data are set?
        self.image.setImage(data_curves.T, lut=self.lut)  # Ought to set clims?
        n_ch = data_curves.shape[0]
        self.image.setRect(QT.QRectF(t_start, 0, t_stop - t_start, n_ch))

        for i, c in enumerate(visibles):
            color = self.by_channel_params["ch{}".format(c), "color"]
            if self.params["display_labels"]:
                self.channel_labels[c].show()
                self.channel_labels[c].setPos(t_start, c)
                self.channel_labels[c].setColor(color)
            else:
                self.channel_labels[c].hide()

        for c in range(self.source.nb_channel):
            if c not in visibles:
                self.channel_labels[c].hide()

        self.vline.setPos(self.t)
        self.plot.setXRange(t_start, t_stop, padding=0.0)
        self.plot.setYRange(0, n_ch, padding=0.0)
