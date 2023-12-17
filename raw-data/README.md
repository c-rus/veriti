# `/raw-data`

This directory holds valid examples of files for storing the raw data between the
software drivers layer and hardware drivers layer.

## Specification

The file format is kept very simple and easy for both layers to read and write. Files are given the `.dat` file extension.

- Ignored Lines start with a `#` character
- Parsed lines consist of a series of `0`, `1`, `,` or `\n` characters
- Each parsed line for an input file represents the input signals being driven each clock cycle
- Each parsed line for an output file represents the output signals being monitored