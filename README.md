# Crown-Court Case Extraction

This library (?) intends to automate information extraction from Crown Court Cases. 

Currently, this is only being tested on Sentencing Remarks. This will later be extended to other relevant documents.

## Installation

To install the library, first install poetry via: `pip install poetry`. You may do this on any python version `>= 3.7.11`. 

Following this, run `poetry install` in the code directory to install the library.

## Usage

There is little practical use that can be derived from the codebase in it's current state. However, you may look in the `scripts` folder for examples.

## Components

We currently identify six key pieces of information we aim to extract from each case:

- Defendent(s)
- Victim(s)
- Charge(s)
- Outcome(s)
- Mitigating Circumstances
- Aggrevating Circumstances

The code for each of these is contained in their repective python scripts in the `case_extraction` folder.

### Defendent(s)

Currently, the defendents are extracted from the sentencing remarks by leveraging the (relatively) consistent structure of the document titles.
These will generally be some variation of "R v Bob Defendent". 

### Victim(s)

Work is yet to begin on victim extraction.

### Charge(s)

The charges are currently extracted by checking the text for any reference to a list of offenses. 

### Mitigating Circumstances

Work is yet to begin on Mitigating Circumstances.

### Aggrevating Circumstances

Work is yet to begin on Aggrevating Circumstances.


