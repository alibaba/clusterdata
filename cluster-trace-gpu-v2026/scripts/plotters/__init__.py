"""Registry for one-figure plotting modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from . import asw_available_slots
from . import compare_frac_gpu
from . import cpu_gpu_ratio
from . import gpu_cpu_request_num_box_plot
from . import gpu_spec_alloc_ratio
from . import gpu_spec_distribution
from . import gpu_spec_hourly_req_trend
from . import gpu_spec_priority_distribution
from . import idle_gpu_fragmentation
from . import job_type_distribution
from . import job_type_model_type_execution_time_cdf
from . import job_type_priority_distribution
from . import model_type_distribution
from . import pod_resource_util_cdf
from . import server_network_cdf
from . import standby_temporal
from . import temporal_gpu_req_sm_util
from . import common


@dataclass(frozen=True)
class Plotter:
    name: str
    output: str
    module: str
    plot: Callable[[], None]
    optional: bool = False
    available: Callable[[], bool] | None = None

    def is_available(self) -> bool:
        return True if self.available is None else self.available()


PLOTTERS = [
    Plotter("job_type_distribution", "job_type_distribution.pdf", "plotters/job_type_distribution.py", job_type_distribution.plot),
    Plotter(
        "job_type_priority_distribution",
        "job_type_priority_distribution.pdf",
        "plotters/job_type_priority_distribution.py",
        job_type_priority_distribution.plot,
    ),
    Plotter("gpu_spec_distribution", "gpu_spec_distribution.pdf", "plotters/gpu_spec_distribution.py", gpu_spec_distribution.plot),
    Plotter(
        "gpu_spec_priority_distribution",
        "gpu_spec_priority_distribution.pdf",
        "plotters/gpu_spec_priority_distribution.py",
        gpu_spec_priority_distribution.plot,
    ),
    Plotter(
        "gpu_spec_hourly_req_trend",
        "gpu_spec_hourly_req_trend.pdf",
        "plotters/gpu_spec_hourly_req_trend.py",
        gpu_spec_hourly_req_trend.plot,
    ),
    Plotter("model_type_distribution", "model_type_distribution.pdf", "plotters/model_type_distribution.py", model_type_distribution.plot),
    Plotter(
        "temporal_gpu_req_sm_util",
        "temporal_gpu_req_sm_util.pdf",
        "plotters/temporal_gpu_req_sm_util.py",
        temporal_gpu_req_sm_util.plot,
    ),
    Plotter("gpu_spec_alloc_ratio", "gpu_spec_alloc_ratio.pdf", "plotters/gpu_spec_alloc_ratio.py", gpu_spec_alloc_ratio.plot),
    Plotter("idle_gpu_fragmentation", "idle_gpu_fragmentation.pdf", "plotters/idle_gpu_fragmentation.py", idle_gpu_fragmentation.plot),
    Plotter("standby_temporal", "standby_temporal.pdf", "plotters/standby_temporal.py", standby_temporal.plot),
    Plotter("asw_available_slots", "asw_available_slots.pdf", "plotters/asw_available_slots.py", asw_available_slots.plot),
    Plotter("compare_frac_gpu", "compare_frac_gpu.pdf", "plotters/compare_frac_gpu.py", compare_frac_gpu.plot),
    Plotter("cpu_gpu_ratio", "cpu_gpu_ratio.pdf", "plotters/cpu_gpu_ratio.py", cpu_gpu_ratio.plot),
    Plotter("pod_resource_util_cdf", "pod_resource_util_cdf.pdf", "plotters/pod_resource_util_cdf.py", pod_resource_util_cdf.plot),
    Plotter(
        "server_network_cdf",
        "server_network_cdf.pdf",
        "plotters/server_network_cdf.py",
        server_network_cdf.plot,
        optional=True,
        available=lambda: common.csv_path("server_network_samples").is_file(),
    ),
    Plotter(
        "job_type_model_type_execution_time_cdf",
        "job_type_model_type_execution_time_cdf.pdf",
        "plotters/job_type_model_type_execution_time_cdf.py",
        job_type_model_type_execution_time_cdf.plot,
    ),
    Plotter(
        "gpu_cpu_request_num_box_plot",
        "gpu_cpu_request_num_box_plot.eps",
        "plotters/gpu_cpu_request_num_box_plot.py",
        gpu_cpu_request_num_box_plot.plot,
    ),
]


PLOTTER_BY_NAME = {plotter.name: plotter for plotter in PLOTTERS}
