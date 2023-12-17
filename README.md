# `veriti`

`veriti` is a verification framework for testing digital hardware designs during pre-silicon validation using software models. 

### Why?

Verification is an important process in the hardware development cycle, and as hardware designs become more complex, being confident the design is free of bugs becomes even more complex. `veriti` looks to reduce the high cost involved with verifying a hardware design during pre-silicon validation by injecting user-defined software models into the validation process.

Any hardware design can be translated behaviorally to software, and by writing the model in software (instead of hardware), it provides an extra level of cross-checking to ensure the design matches specification. Writing the model in software is also typically easier with nicer constructs and an abundance of existing libraries available. With `veriti`, all of the plumbing in setting up tests is minimized so testing the next hardware design only requires focusing on writing the model, not the whole framework.

## Architecture

To achieve this goal, there are 3 main layers:

|   |
|---|
|Software Drivers Layer*|
|Raw Data Layer|
|Hardware Drivers Layer**|

\* Supported Software Driver Layers: Python  
\** Supported Hardware Driver Layers: VHDL

### Software Drivers Layer

The software drivers implement the low-level functions required to run any form of test. It translates your test cases into the raw data layer represented by a specific file format.

### Raw Data Layer

The raw data layer stores the tests to run during simulation and the expected outputs. This information is typically stored in a specific file format already handled by `veriti`.

### Hardware Drivers Layer

The hardware drivers implement the low-level functions required to receive data from the raw data layer. This data is read during simulation to run test cases and automatically assert outputs.

