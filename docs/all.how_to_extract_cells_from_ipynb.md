<!-- toc -->

- [Notebook Extractor Module Documentation](#notebook-extractor-module-documentation)
  * [Overview](#overview)
  * [Features](#features)
  * [Workflow](#workflow)
  * [Usage Instructions](#usage-instructions)
  * [Adding Extraction Markers in Notebooks](#adding-extraction-markers-in-notebooks)
  * [Examples](#examples)
    + [Example 1: Single Extraction Region](#example-1-single-extraction-region)
    + [Example 2: Multiple Extraction Regions with Same Base Name](#example-2-multiple-extraction-regions-with-same-base-name)
  * [Conclusion](#conclusion)

<!-- tocstop -->

# Notebook Extractor Module Documentation

This document explains the workflow and usage of the
`HelpersTask57_Extract_cells_from_a_notebook_as_png.py` module. The module is
designed to extract code cells (or outputs) from a `Jupyter Notebook` based on
specially formatted comments and then capture separate screenshots for each
extraction region using `Playwright`.

## Overview

The `HelpersTask57_Extract_cells_from_a_notebook_as_png.py` module is built to:

- Extract multiple regions from a Jupyter Notebook where each region is
  delimited by markers
- Adjust the extracted cells based on the specified extraction mode
  (`only code`, `only output`, or `all`)
- Convert each extraction region into an HTML file
- Use Playwright to capture a screenshot of the rendered HTML
- Saving screenshots in a dedicated folder using filenames based on the
  marker-provided name

## Features

- Multiple Extraction Regions:

  The module can extract several regions from a `notebook`. Each region is
  defined by a pair of comments, so you can have separate sections in the same
  notebook.

- Custom Extraction Modes:

  Each region can specify a mode:
  - `only_input`: Only the code (cell input) is retained
  - `only_output`: Only the outputs are retained
  - `all`: Both code and outputs are included

- Custom and Unique Output Filenames::

  Each extraction region uses the output filename provided in the start marker.
  If the same filename is specified for multiple regions, a counter suffix
  (e.g., \_1, \_2, etc.) is automatically appended to ensure that each
  screenshot file is unique..

- Automated HTML Conversion:

  Uses `nbconvert's HTMLExporter` to convert the extracted notebook cells to
  HTML before capturing a screenshot.

- Playwright Integration:

  The module uses `Playwright` to launch a headless browser, render the HTML
  file, and capture high-quality screenshots.

## Workflow

1. Notebook Parsing:

   The module reads a notebook file using nbformat and searches for extraction
   regions defined by:
   ```
   # start_extract(mode)=<output_filename>
   ```
   ```
   # end_extract
   ```

2. Extraction of Regions:

   Each region is extracted as a list of cells. The extraction mode and an
   intended output filename are recorded (although the final screenshot
   filenames are generated sequentially).

3. HTML Conversion:

   For each extraction region, the cells are assembled into a new notebook and
   converted into an `HTML file` using `nbconvert`.

4. Screenshot Capture:

   The `HTML` file is loaded by `Playwright`, which captures a screenshot of the
   rendered page. Screenshots are saved in a folder named `screenshots`.

5. Cleanup:

   Temporary `HTML` files are removed after screenshots are taken.

## Usage Instructions

1. Ensure Requirements Are Installed:
   - Install Playwright and initialize the browsers:

   ```bash
   pip install playwright nbconvert nbformat
   playwright install
   ```

2. Prepare Your Notebook
   - Add extraction markers to your ipynb files.

3. Run the Module
   ```
   import xyz

   screenshot_files = xyz.extract_and_capture("test.ipynb")
   ```

4. Check the Screenshots Folder:
   - The screenshots will be saved in the screenshots folder with filenames like
     section_1.png, section_2.png, etc.

## Adding Extraction Markers in Notebooks

To enable extraction, add markers in your code cells:

- Start Marker

  Place the start marker at the beginning of a cell:
  ```
  # start_extract(only_input)=my_screenshot.png
  ```

  Replace only_input with only_output or all as needed. The filename
  `(my_screenshot.png)` is used as the base name for the output screenshot.

- End Marker

  Mark the end of the extraction region with:
  ```
  # end_extract
  ```

These markers can reside in the same cell or in different cells. If multiple
regions specify the same filename, the module appends `_1`, `_2`, etc.

## Examples

### Example 1: Single Extraction Region
```
# start_extract(only_input)=example.png
print("This is an example extraction region.")
# end_extract
```

Result: The module extracts the region, retains only the code, and saves the
screenshot as `screenshots/example.png`.

## Example 2: Multiple Extraction Regions with Same Base Name
```
# start_extract(all)=shared_name.png
print("Region 1: Showing both input and output.")
# end_extract
```
```
# start_extract(only_output)=shared_name.png
print("Region 2: Showing only output.")
# end_extract
```

Result: The first region will be saved as `screenshots/shared_name.png` and the
second as `screenshots/shared_name_1`.png.

## Conclusion

The `HelpersTask57_Extract_cells_from_a_notebook_as_png.py` module simplifies
the extraction and visualization of specific notebook sections. By using custom
markers, you can tailor which parts of your notebook are captured, select
between code and outputs, and automatically generate uniquely named screenshots.
This makes it an excellent tool for documentation, presentations, or automated
reporting.
