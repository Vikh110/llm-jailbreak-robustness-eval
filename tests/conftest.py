"""Shared helpers for the test suite.

The pipeline scripts have numbered file names (``05_analysis.py``) and import
``config`` from their own folder, so they are loaded by path rather than as a
package.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "03_pipeline"

if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))


def load_script(filename: str):
    """Import a pipeline script such as ``07_verify.py`` as a module (without running ``main``)."""
    path = PIPELINE / filename
    name = "pipeline_" + path.stem.replace("-", "_")
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
