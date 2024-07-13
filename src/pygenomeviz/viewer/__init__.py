from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pygenomeviz


def _concat_target_files_contents(files: list[Path], target_ext: str) -> str:
    """Concatenate target extension files contents"""
    contents = "\n"
    target_files = [file for file in files if file.suffix == target_ext]
    for target_file in target_files:
        with open(target_file) as f:
            contents += f.read() + "\n"
    return contents


_viewer_dir = Path(__file__).parent
_assets_dir = _viewer_dir / "assets"
_assets_files = [
    "lib/spectrum.min.css",
    "lib/tabulator.min.css",
    "lib/micromodal.css",
    "lib/jquery.min.js",
    "lib/spectrum.min.js",
    "lib/panzoom.min.js",
    "lib/tabulator.min.js",
    "lib/micromodal.min.js",
    "lib/popper.min.js",
    "lib/tippy-bundle.umd.min.js",
    "pgv-viewer.js",
]
_assets_files = [_assets_dir / f for f in _assets_files]

TEMPLATE_HTML_FILE = _viewer_dir / "pgv-viewer-template.html"
CSS_CONTENTS = _concat_target_files_contents(_assets_files, ".css")
JS_CONTENTS = _concat_target_files_contents(_assets_files, ".js")


def setup_viewer_html(
    svg_figure: str,
    gid2feature_dict: dict[str, dict[str, Any]],
    gid2link_dict: dict[str, dict[str, Any]],
) -> str:
    """Setup viewer html (Embed SVG figure, CSS & JS assets)

    Parameters
    ----------
    svg_figure : str
        SVG figure strings
    gid2feature_dict : dict[str, dict[str, Any]]
        GID(Group ID) & feature dict
    gid2link_dict : dict[str, dict[str, Any]]
        GID(Group ID) & link dict

    Returns
    -------
    viewer_html : str
        Viewer html strings
    """
    # Check if figure is valid for save as HTML
    feature_gid_list = list(gid2feature_dict.keys())
    if len(feature_gid_list) > 0:
        check_feature_gid = feature_gid_list[0]
        if check_feature_gid not in svg_figure:
            err_msg = "Failed to save HTML viewer. Check if target figure is generated by 'gv.plotfig(fast_render=False)' method call."  # noqa: E501
            raise ValueError(err_msg)
    # Read template html file
    with open(TEMPLATE_HTML_FILE) as f:
        viewer_html = f.read()
    # Replace template strings
    return (
        viewer_html.replace("$PGV_SVG_FIG", f"\n{svg_figure}")
        .replace("$VERSION", pygenomeviz.__version__)
        .replace("$DATETIME_NOW", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        .replace("/*$CSS_CONTENTS*/", CSS_CONTENTS)
        .replace(
            "/*$JS_CONTENTS*/",
            re.sub("^import ", "// import ", JS_CONTENTS, flags=(re.MULTILINE))
            .replace(
                "FEATURES_JSON = {}",
                f"FEATURES_JSON = {json.dumps(gid2feature_dict, indent=4)}",
            )
            .replace(
                "LINKS_JSON = {}",
                f"LINKS_JSON = {json.dumps(gid2link_dict, indent=4)}",
            ),
        )
    )