"""Core analysis engines for N-Link Basin Analysis.

This package contains reusable logic extracted from the analysis scripts.
These engines can be used by both CLI scripts and the API service layer.

Modules:
    trace_engine: Trace sampling and path following
    basin_engine: Basin mapping via reverse BFS (to be added)
    branch_engine: Branch structure analysis (to be added)
    report_engine: Report and figure generation (to be added)
"""

from _core.trace_engine import (
    SampleRow,
    TraceSampleResult,
    load_successor_arrays,
    sample_traces,
    trace_once,
)

__all__ = [
    "SampleRow",
    "TraceSampleResult",
    "load_successor_arrays",
    "sample_traces",
    "trace_once",
]
