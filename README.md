# `veriti`

`veriti` is a verification framework for testing digital hardware designs during pre-silicon validation using software models. 

### Why?

Verification is an important process in the hardware development cycle, and as hardware designs become more complex, being confident the design is free of bugs becomes even more complex. `veriti` looks to reduce the high cost involved with verifying a hardware design during pre-silicon validation by injecting user-defined software models into the validation process.

Any hardware design can be translated behaviorally to software, and by writing the model in software (instead of hardware), it provides an extra level of cross-checking to ensure the design matches specification. Writing the model in software is also typically easier with nicer constructs and an abundance of existing libraries available. With `veriti`, all of the plumbing in setting up tests is minimized so testing the next hardware design only requires focusing on writing the model, not the whole framework.

## Architecture

To achieve this goal, there are 3 main layers:

|   |
|---|
|Software Drivers Layer|
|Raw Data Layer|
|Hardware Drivers Layer|

This separation of functionality is important in terms of modularity. If a model needs to be written in a different language (such as C++), the only layer required to change is the software drivers layer; the raw data layer and hardware driver layer remain untouched. Having well-defined interfaces between these layers allows for the framework to easily expand to new languages.

### Software Drivers Layer

The software drivers implement the low-level functions required to run any form of test. It translates your test cases into the raw data layer represented by a specific file format.

The software drivers layer is responsible for generating test inputs, tracking coverage, and generating test outputs. 

The software drivers layer can also generate HDL code, which is useful to copy/paste when writing the code to connect the hardware design to the raw data layer.

### Raw Data Layer

The raw data layer stores the tests to run during simulation and the expected outputs. This information is typically stored in a specific file format already handled by `veriti`.

Each line in a raw data file is a _transaction_. A transaction in this sense is the combination of complete set of inputs or outputs. For raw data stored in an input file, each transaction is to be the input into the design-under-test on a single clock cycle. For raw data stored in an output file, each transaction is the outputs to be checked against the design-under-test's outputs in the scoreboard. The output transactions do not have to be checked every clock cycle, and may only be cared when a certain condition occurs (such as a valid signal being asserted).

The number of transactions stored as inputs and outputs does not have to be 1-to-1. There may be more input transactions (fed every clock cycle) than output transactions (only checked when valid).

### Hardware Drivers Layer

The hardware drivers implement the low-level functions required to receive data from the raw data layer. This data is read during simulation to run test cases and automatically assert outputs.

The hardware drivers layer is responsible for the timing of the simulation: specifically determining when to drive inputs and monitoring when to check outputs.

## Operation 

The software level and hardware level co-exist. The software level is first executed to make sure the hardware level has everything it needs: namely the input and output test vector files. 

When the software is generating tests, it can also keep track of what test cases are being covered by using _coverage nets_, which are either `Coverpoints` or `Covergroups`.

Once the test files are generated, the simulation can begin at the hardware level in the hardware description language. At the hardware drivers layer, a package of functions exist for clock generation, system reseting, signal driving, signal montioring, and assertions.

## Installing

### Software Drivers
For the Python library, run the following command from this file's directory:
```
pip install ./sw-drivers/python
```
<!-- pip install -e ./sw-drivers/python -->

### Hardware Drivers
For the VHDL packages, run the following command from this file's directory:
```
orbit install --path ./hw-drivers
```