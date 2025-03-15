"""
Import as:

import misc.HelpersTask57_Extract_cells_from_a_notebook_as_png as mhecfanap
"""

import logging
import os
import re
from typing import Dict

# TODO(gp): no need to abbreviate
import nbconvert as nbc
import nbformat
# TODO(gp): do we need to abbreviate?
import playwright.sync_api as psi

_LOG = logging.getLogger(__name__)

# TODO(gp): Let's convert this into a Class called NotebookImageExtractor,
# so we keep the related functions together.

def extract_regions_from_notebook(notebook_path: str) -> Tuple[str, str, str]:
    """
    Extract regions from a notebook based on extraction markers.

    This function reads a Jupyter notebook and searches for all regions
    indicated by the markers inside cells:
    ```
    # start_extract(mode)=<output_filename>
    ...
    # end_extract
    ```
    For each region found, it collects the cells between these markers. Each
    region is returned as a tuple containing the extraction mode, the output
    filename (as specified in the marker), and the list of cells for that
    region.

    :param notebook_path: The path to the Jupyter notebook.
    :return: tuples (mode, out_filename, region_cells) for each
        extraction region.
    # TODO: Add some examples of outputs
    """
    # Read notebook.
    nb = nbformat.read(notebook_path, as_version=4)
    # TODO(Shaunak): Add examples of text to parse.
    # TODO: -> start_marker_regex
    start_re = re.compile(
        r"#\s*start_extract\(\s*(only_input|only_output|all)\s*\)\s*=\s*(\S+)"
    )
    # TODO: -> end_marker_regex
    end_re = re.compile(r"#\s*end_extract")
    #
    regions = []
    # TODO: let's call it state="look_for_start_extract", "look_for_end_extract".
    in_extract = False
    current_mode = None
    current_out_filename = None
    current_cells = []
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        if not in_extract:
            # Look for a start marker in the cell.
            hdbg.dassert(not end_re.search(cell.source),
                         "Found an end marker not paired with a start marketi at: %s",
                         str(cell.source))
            m = start_re.search(cell.source)
            if m:
                current_mode = m.group(1)
                current_out_filename = m.group(2)
                in_extract = True
                # Remove the start marker from the cell.
                cell.source = start_re.sub("", cell.source).strip()
                # If the end marker exists in the same cell, remove it and finish the region.
                # TODO: How can this happen? For me this is an error.
                if end_re.search(cell.source):
                    cell.source = end_re.sub("", cell.source).strip()
                    current_cells.append(cell)
                    regions.append(
                        (current_mode, current_out_filename, current_cells)
                    )
                    current_cells = []
                    in_extract = False
                else:
                    current_cells.append(cell)
        else:
            # Look for an end marker in the cell.
            if end_re.search(cell.source):
                cell.source = end_re.sub("", cell.source).strip()
                current_cells.append(cell)
                regions.append(
                    (current_mode, current_out_filename, current_cells)
                )
                current_cells = []
                in_extract = False
            else:
                current_cells.append(cell)
    if not regions:
        raise ValueError("No extraction markers found in the notebook.")
    return regions


# output_html_file
def convert_notebook_to_html(nb: nbformat.NotebookNode, output_html: str) -> None:
    """
    Convert a notebook object to an HTML file using `nbconvert`.

    :param nb: notebook object containing the extracted cells.
    :param output_html: filename for the temporary HTML output.
    """
    html_exporter = nbc.HTMLExporter()
    body, _ = html_exporter.from_notebook_node(nb)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(body)


# -> timeout_in_msec
def capture_screenshot(
    html_file: str, screenshot_path: str, *, timeout: int = 2000
) -> None:
    """
    Capture a screenshot of an HTML file using Playwright.

    This function launches a headless Chromium browser, opens the
    provided HTML file, waits for a specified timeout to ensure the page
    is fully rendered, and then takes a screenshot saving it to the
    provided screenshot path.

    :param html_file: path to the HTML file.
    :param screenshot_path: path where the screenshot will be saved.
    :param timeout: time in milliseconds to wait for the page to render.
    """
    file_url = "file:///" + os.path.abspath(html_file)
    with psi.sync_playwright() as p:
        # Launch a headless Chromium browser.
        browser = p.chromium.launch(headless=True)
        # Open the HTML file.
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        page.goto(file_url)
        # Wait for a specified timeout to ensure the page.
        page.wait_for_timeout(timeout)
        # Take a screenshot, saving to file.
        page.screenshot(path=screenshot_path)
        browser.close()


def extract_and_capture(notebook_path: str) -> list:
    """
    Extract notebook regions, convert each to HTML, and capture separate
    screenshots.

    The function orchestrates the extraction of all marked regions from a
    Jupyter notebook. It processes each region independently: adjusting cells
    according to its extraction mode, converting the region to an HTML file,
    capturing a screenshot using Playwright, and then cleaning up the temporary
    HTML file. Screenshots are saved in the "screenshots" folder with filenames
    based on the name provided in the extraction marker. If a name is repeated,
    a counter suffix (_1, _2, etc.) is appended to ensure unique filenames. A
    list of screenshot file paths is returned.

    :param notebook_path: path to the Jupyter notebook.
    :return: list of paths to the screenshot files.
    """
    regions = extract_regions_from_notebook(notebook_path)
    screenshot_files = []
    # Create screenshots folder if it doesn't exist.
    screenshots_folder = "screenshots"
    os.makedirs(screenshots_folder, exist_ok=True)
    # Keep track of filename usage to handle duplicates.
    filename_counter: Dict[str, int] = {}
    # Process each region.
    for mode, out_filename, cells in regions:
        # Adjust each cell in the region according to the extraction mode.
        for cell in cells:
            if mode == "only_input":
                cell.outputs = []
            elif mode == "only_output":
                cell.source = ""
        # Create a new notebook for the region.
        new_nb = nbformat.v4.new_notebook(cells=cells)
        temp_html = "temp_extract.html"
        convert_notebook_to_html(new_nb, temp_html)
        # Determine the final screenshot filename.
        base, ext = os.path.splitext(out_filename)
        if ext == "":
            ext = ".png"
        final_name = out_filename
        if final_name in filename_counter:
            filename_counter[final_name] += 1
            final_name = f"{base}_{filename_counter[out_filename]}{ext}"
        else:
            filename_counter[final_name] = 1
        screenshot_path = os.path.join(screenshots_folder, final_name)
        capture_screenshot(temp_html, screenshot_path)
        os.remove(temp_html)
        screenshot_files.append(screenshot_path)
        _LOG.info("Saved screenshot to %s", screenshot_path)
    return screenshot_files
