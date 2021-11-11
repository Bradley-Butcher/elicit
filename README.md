# Crown-Court Case Extraction

This library (?) intends to automate information extraction from Crown Court Cases. 

Currently, this is only being tested on Sentencing Remarks. This will later be extended to other relevant documents.

## Installation

To install the library, first install poetry via: `pip install poetry`. You may do this on any python version `>= 3.9`. 

Following this, run `poetry install` in the code directory to install the library.

## Usage

The library is currently in very early development. Syntax, features, and functionality are subject to change. If you still wish to use the library however, follow the instructions below.

### Defining a Schema

In order to extract a variable from a transcript, you must define:

- A set of questions to ask in order to extract the information.
- A set categories which the answer can take (alternatively "raw" or "continuous" if the answer is a string or number respectively).

Example below:

**Questions:**
```
offender_confession:
  - Did the offender confess to commiting the crime?
  - Did the offender plead guilty?
  ```
**Categories:**
```
offender_confession:
  - confession
  - no confession
  ```

These are placed into the yaml files "categories.yml" and "questions.yml" respectively.

A basic schema is already defined in the /schemas directory. Modifying these files is currently the easiest way to add new questions and categories.

### Extracting Information

The EASIEST way to extract information from a transcript is to use the `Case` object. However, this currently only works if no new variables have been added to the schema (will be changed in a later version).

This can be done like so:

```
from case_extraction import Case

case = Case.from_filename("path/to/pdf")

print(case.to_dict())
print(case.debug())
```

The case object will contain all extracted information, these can either be accessed directly e.g. `case.offenses` or all at once by printing a dictionary (as seen above). Additionally, one can debug the recieved answers by printing the `debug()` method. More on this later.

**If new variables have been added** then the `Case` object will not work. This is because the `Case` object is (currently) not aware of the new variables. To get around this, you can use the following functions:

```
from case_extraction.loading import pdf_to_plaintext
from case_extraction.extraction import extract_variables

filename = "pdfs/example1.pdf"

doc = pdf_to_plaintext(filename, newlines=False)
variables = extract_variables(doc=doc)

print(variables)
```

Assuming the PDF filename is in the regular `R v. X` format, one can additionally add the defendant information to increase extraction accuracy:

```
from case_extraction.loading import pdf_to_plaintext
from case_extraction.defendants import extract_defendants_filename
from case_extraction.extraction import extract_variables

filename = "pdfs/R v. ExampleName.pdf"

doc = pdf_to_plaintext(filename, newlines=False)
defendant = extract_defendants_filename(filename)
variables = extract_variables(doc=doc, defendant=defendant)

print(variables)
```

There are two hyper-parameters which can be set in both `Case.from_filename` and `extract_variables`. These are `qa_threshold` and `match_threshold`. The former is a value between 0 - 1 which determines the threshold needed to pass the filtering process for extracted answers to the questions asked. The latter is the threshold needed to pass the filtering process for how matched it needs to be to a category.
More on this below.

## How it works

The pipeline is currently:

![](pipeline.png)

## Current Performance
| Case        | Correctly Extracted Variables   |
|:-------------------|:--------------------------------|
|   R v. ben blakeley  | 10/19                           |
|   R v. keith wallis  | 9/19                            |
|  R v. pavlo lapshyn | 16/19                           |