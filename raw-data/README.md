# `/raw-data`

This directory holds valid examples of files for storing the raw data between the
software drivers layer and hardware drivers layer.

## Traces

The file format is kept very simple and easy for both layers to read and write. Files are given the `.trace` file extension.

- Parsed lines consist of a series of `0`, `1`, `,` or `\n` characters
- Each parsed line for an input file represents the input signals being driven each clock cycle
- Each parsed line for an output file represents the output signals being monitored

```
SIGNAL_1,SIGNAL_2,...,SIGNAL_N,
```

```
11000101,11010,000,11,001,
01001010,10101,010,01,000,
```

## Logs

The file format is specified to provide meaningful recordings of what happened, when it happened, why it happened, and how it happened. This is the artifact produced by a hardware simulation using the `veriti` framework. Files are given the `.log` file extension.

Logs directly produced by the hardware simulation may provide too much information and may not be formatted for easy readability. This is way it is recommendended to process the log through `veriti` to allow for filtering, better formatting, and analysis.
 
```
[TIMESTAMP] LEVEL TOPIC "CAUSE"
```

```
[320 ns         ] INFO     TIMEOUT      "done being asserted - required 5 cycles"
[320 ns         ] INFO     ASSERTION    "result - received 00000011 matches expected 00000011"
[320 ns         ] INFO     ASSERTION    "overflow - received 0 matches expected 0"
[320 ns         ] INFO     ASSERTION    "done - received 1 matches expected 1"
[420 ns         ] INFO     STABILITY    "result depending on done - maintained stability at 00000011"
[560 ns         ] INFO     TIMEOUT      "done being asserted - required 5 cycles"
[560 ns         ] INFO     ASSERTION    "result - received 00000000 matches expected 00000000"
```