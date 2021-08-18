import dataclasses
from typing import List, Tuple
import os
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import spym
from plotly.missing_ipywidgets import FigureWidget
from plotly.subplots import make_subplots
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset


@dataclasses.dataclass
class Plotter:

    display_flag: bool
    path_dir: str
    file_prefix: str
    file_prefix_STS: str
    file_index: int = dataclasses.field(init=False, default=None)
    path_file: str = dataclasses.field(init=False, default=None)
    data_image: Dataset = dataclasses.field(init=False, default=None)
    data_line: Dataset = dataclasses.field(init=False, default=None)
    data_topo: DataArray = dataclasses.field(init=False, default=None)
    data_didv: DataArray = dataclasses.field(init=False, default=None)
    data_spec: DataArray = dataclasses.field(init=False, default=None)
    spec_list: list = dataclasses.field(init=False, default_factory=list)
    attrs_image: dict = dataclasses.field(init=False, default_factory=dict)
    attrs_spec: dict = dataclasses.field(init=False, default_factory=dict)
    bias_image: float = dataclasses.field(init=False, default=None)
    bias_mod_image: float = dataclasses.field(init=False, default=None)
    current_image: float = dataclasses.field(init=False, default=None)
    xaxis_image: dict = dataclasses.field(init=False, default_factory=dict)
    yaxis_image: dict = dataclasses.field(init=False, default_factory=dict)
    xaxis_spec: dict = dataclasses.field(init=False, default_factory=dict)
    yaxis_spec: dict = dataclasses.field(init=False, default_factory=dict)
    colorbar_topo: dict = dataclasses.field(init=False, default_factory=dict)
    colorbar_didv: dict = dataclasses.field(init=False, default_factory=dict)
    spec_num: int = dataclasses.field(init=False, default=None)
    spec_average_num: int = dataclasses.field(init=False, default=None)
    trace_topo: FigureWidget = dataclasses.field(init=False, default=None)
    trace_didv: FigureWidget = dataclasses.field(init=False, default=None)
    trace_spec: List[FigureWidget] = dataclasses.field(init=False, default_factory=list)
    trace_spec_location: List[FigureWidget] = dataclasses.field(init=False, default_factory=list)

    spec_location_x: np.ndarray = dataclasses.field(init=False, default=None)
    spec_location_y: np.ndarray = dataclasses.field(init=False, default=None)
    width_single = 600
    width_double = 1250
    height = 600

    def __post_init__(self) -> None:
        if not os.path.exists(self.path_dir):
            raise ValueError('No such directory')
        else:
            return

    def load_file(self, data_index: int) -> tuple:
        self.file_index = data_index
        self.path_file = os.path.join(self.path_dir, self.file_prefix + str(self.file_index).zfill(4) + '.sm4')
        if not os.path.exists(self.path_file):
            raise ValueError('No such data file')
        self.data_image, self.data_line = spym.load(self.path_file, datatype_separate=True)
        return self.data_image, self.data_line

    def load_file_STS(self, data_index: int) -> tuple:
        self.file_index = data_index
        self.path_file = os.path.join(self.path_dir, self.file_prefix_STS + str(self.file_index).zfill(4) + '.sm4')
        if not os.path.exists(self.path_file):
            raise ValueError('No such data file')
        self.data_line = spym.load(self.path_file, datatype_separate=False)
        return self.data_line

    def load_image(self) -> None:
        self.data_topo = self.data_image.Topography_Forward
        self.data_topo.spym.align()
        self.data_topo.spym.plane()
        self.data_topo.spym.fixzero()

        self.data_didv = self.data_image.LIA_Current_Forward

        self.attrs_image = self.data_topo.spym._dr.attrs
        self.bias_image = self.attrs_image['bias']
        self.bias_mod_image = self.attrs_image['bias_modulation']
        self.current_image = self.attrs_image['setpoint']

        self.xaxis_image = dict(
            title='x (nm)',
            ticks='outside',
            linewidth=1,
            range=(self.data_topo.x.min(), self.data_topo.x.max()),
            linecolor='Black',
            mirror=True
        )
        self.yaxis_image = dict(
            title='y (nm)',
            ticks='outside',
            linewidth=1,
            range=(self.data_topo.y.min(), self.data_topo.y.max()),
            linecolor='Black',
            mirror=True
        )
        self.colorbar_topo = dict(
            title='Height (pm)',
            titleside='top',
            tickmode='array',
            ticks='outside',
            len=1,
            thickness=10,
            outlinecolor='Black',
            outlinewidth=2,
        )
        self.colorbar_didv = dict(
            title='LIA Current (pA)',
            titleside='top',
            tickmode='array',
            ticks='outside',
            len=1,
            thickness=10,
            outlinecolor='Black',
            outlinewidth=2,
        )

        self.title = ""
        if "filename" in self.attrs_image:
            self.title += self.attrs_image["filename"] + "<br>"
        self.title += "V={:.2f} {}, I={:.2f} {}, Vm={:.2f} {}".format(
            self.attrs_image["bias"],
            self.attrs_image["bias_units"],
            self.attrs_image["setpoint"],
            self.attrs_image["setpoint_units"],
            self.attrs_image["bias_modulation"],
            self.attrs_image["bias_modulation_units"])
        return

    def load_spec(self) -> None:
        self.data_spec = self.data_line.LIA_Current_Spec
        self.spec_num = int(len(self.data_spec.values) / self.spec_average_num)
        self.spec_list = []
        for i in range(self.spec_num):
            self.spec_list.append(self.data_spec.values[i * self.spec_average_num:(i + 1) * self.spec_average_num - 1].mean(axis=0))

        self.attrs_spec = self.data_spec.spym._dr.attrs
        self.bias_spec = self.attrs_spec['bias']
        self.bias_mod_spec = self.attrs_spec['bias_modulation']
        self.current_spec = self.attrs_spec['setpoint']
        self.spec_location_x = np.array(self.attrs_spec['RHK_SpecDrift_Xcoord'])[0::self.spec_average_num] * 1e9
        self.spec_location_y = np.array(self.attrs_spec['RHK_SpecDrift_Ycoord'])[0::self.spec_average_num] * 1e9
        self.xaxis_spec = dict(
            title='Voltage (V)',
            ticks='outside',
            linewidth=1,
            linecolor='Black',
            mirror=True
        )
        self.yaxis_spec = dict(
            title='LIA Current (pA)',
            ticks='outside',
            linewidth=1,
            linecolor='Black',
            mirror=True
        )
        self.title = ""
        if "filename" in self.attrs_spec:
            self.title += self.attrs_spec["filename"] + "<br>"
        self.title += "V={:.2f} {}, I={:.2f} {}, Vm={:.2f} {}".format(
            self.attrs_spec["bias"],
            self.attrs_spec["bias_units"],
            self.attrs_spec["setpoint"],
            self.attrs_spec["setpoint_units"],
            self.attrs_spec["bias_modulation"],
            self.attrs_spec["bias_modulation_units"])
        return

    def get_trace_topo(self, offset: bool = False) -> None:
        self.load_image()
        if offset:
            self.trace_topo = go.Heatmap(
                x=self.data_topo.x + self.data_topo.x.offset - (self.data_topo.x.max() - self.data_topo.x.min()) / 2,
                y=self.data_topo.y + self.data_topo.y.offset - (self.data_topo.y.max() - self.data_topo.y.min()) / 2,
                z=self.data_topo.values,
                colorscale="Solar",
                name='Topography',
                zsmooth='best'
            )
            self.xaxis_image['range'] = (self.data_topo.x.min() + self.data_topo.x.offset - (self.data_topo.x.max() - self.data_topo.x.min()) / 2, self.data_topo.x.max() + self.data_topo.x.offset - (self.data_topo.x.max() - self.data_topo.x.min()) / 2)
            self.yaxis_image['range'] = (self.data_topo.y.min() + self.data_topo.y.offset - (self.data_topo.y.max() - self.data_topo.y.min()) / 2, self.data_topo.y.max() + self.data_topo.y.offset - (self.data_topo.y.max() - self.data_topo.y.min()) / 2)
        else:
            self.trace_topo = go.Heatmap(
                x=self.data_topo.x,
                y=self.data_topo.y,
                z=self.data_topo.values,
                colorscale="Solar",
                name='Topography',
                zsmooth='best'
            )
        return

    def get_trace_didv(self) -> None:
        self.load_image()
        self.trace_didv = go.Heatmap(
            x=self.data_didv.x,
            y=self.data_didv.y,
            z=self.data_didv.values,
            colorscale="Gray",
            name='dI/dV',
            zsmooth='best'
        )
        return

    def get_trace_spec(self, average_num: int) -> None:
        self.spec_average_num = average_num
        self.load_spec()
        self.trace_spec = []
        self.trace_spec_location = []
        for i in range(self.spec_num):
            self.trace_spec.append(go.Scatter(
                x=self.data_spec.x.values,
                y=self.spec_list[i],
                mode='lines',
                name="Point" + str(i),
                marker_color=str(px.colors.qualitative.Plotly[i]),
                showlegend=True,
            ))

            self.trace_spec_location.append(go.Scatter(
                x=[self.spec_location_x[i]],
                y=[self.spec_location_y[i]],
                mode='markers+text',
                text=['Point' + str(i)],
                textposition="middle right",
                name="Point" + str(i),
                marker=dict(
                    color=str(px.colors.qualitative.Plotly[i]),
                    size=15,
                    line=dict(
                        width=2
                    ),
                ),
                showlegend=False))
        return

    def get_trace_spec2(self, average_num: int, index_ext: int) -> None:
        self.spec_average_num = average_num
        self.load_spec()
        self.trace_spec = []
        self.trace_spec_location = []
        for i in range(self.spec_num):
            self.trace_spec.append(go.Scatter(
                x=self.data_spec.x.values,
                y=self.spec_list[i],
                mode='lines',
                name="Point" + str(index_ext),
                marker_color=str(px.colors.qualitative.Plotly[index_ext]),
                showlegend=True,
            ))

            self.trace_spec_location.append(go.Scatter(
                x=[self.spec_location_x[i]],
                y=[self.spec_location_y[i]],
                mode='markers+text',
                text=['Point' + str(index_ext)],
                textposition="middle right",
                name="Point" + str(index_ext),
                marker=dict(
                    color=str(px.colors.qualitative.Plotly[index_ext]),
                    size=15,
                    line=dict(
                        width=2
                    ),
                ),
                showlegend=False))
        return

    def fig_topo(self, data_index: int) -> FigureWidget:
        fig = make_subplots(rows=1, cols=1,)
        self.load_file(data_index)
        self.get_trace_topo()
        fig.add_trace(self.trace_topo, row=1, col=1,)
        fig.update_layout(title_text=self.title, xaxis=self.xaxis_image, yaxis=self.yaxis_image, height=self.height, width=self.width_single,)
        fig.update_traces(colorbar=self.colorbar_topo, row=1, col=1)
        if self.display_flag:
            fig.show()
        return fig

    def fig_topo_and_didv(self, data_index: int) -> FigureWidget:
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Topography', 'dI/dV'), horizontal_spacing=0.15)
        self.load_file(data_index)
        self.get_trace_topo()
        fig.add_trace(self.trace_topo, row=1, col=1,)
        self.get_trace_didv()
        fig.add_trace(self.trace_didv, row=1, col=2,)
        fig.update_layout(title_text=self.title, xaxis=self.xaxis_image, yaxis=self.yaxis_image, xaxis2=self.xaxis_image, yaxis2=self.yaxis_image, height=self.height, width=self.width_double,)
        self.colorbar_topo['x'] = 0.44
        fig.update_traces(colorbar=self.colorbar_topo, row=1, col=1)
        fig.update_traces(colorbar=self.colorbar_didv, row=1, col=2)
        if self.display_flag:
            fig.show()
        return fig

    def fig_spectrum(self, data_index_spec: int, data_index_image: int, average_num: int) -> FigureWidget:
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Location', 'dI/dV'), horizontal_spacing=0.15)
        self.load_file(data_index_image)
        self.get_trace_topo(offset=True)
        fig.add_trace(self.trace_topo, row=1, col=1,)
        self.colorbar_topo['x'] = 0.44
        fig.update_traces(colorbar=self.colorbar_topo, row=1, col=1)
        self.load_file(data_index_spec)
        self.get_trace_spec(average_num)
        for i in range(self.spec_num):
            fig.add_trace(self.trace_spec_location[i], row=1, col=1,)
            fig.add_trace(self.trace_spec[i], row=1, col=2,)
        fig.update_layout(title_text=self.title, xaxis=self.xaxis_image, yaxis=self.yaxis_image, xaxis2=self.xaxis_spec, yaxis2=self.yaxis_spec, height=self.height, width=self.width_double, template='plotly_white')
        if self.display_flag:
            fig.show()
        return fig

    def fig_multi_spectra(self, data_index_spec_list: list, data_index_image: int, average_num: int) -> FigureWidget:
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Location', 'dI/dV'), horizontal_spacing=0.15)
        self.load_file(data_index_image)
        self.get_trace_topo(offset=True)
        fig.add_trace(self.trace_topo, row=1, col=1,)
        self.colorbar_topo['x'] = 0.44
        fig.update_traces(colorbar=self.colorbar_topo, row=1, col=1)
        for i, data_index_spec in enumerate(data_index_spec_list):
            self.load_file_STS(data_index_spec)
            self.get_trace_spec2(average_num, i)
            fig.add_trace(self.trace_spec_location[0], row=1, col=1,)
            fig.add_trace(self.trace_spec[0], row=1, col=2,)
        fig.update_layout(title_text=self.title, xaxis=self.xaxis_image, yaxis=self.yaxis_image, xaxis2=self.xaxis_spec, yaxis2=self.yaxis_spec, height=self.height, width=self.width_double, template='plotly_white')
        if self.display_flag:
            fig.show()
        return fig
