# New Wrapper Workflow

This document is the standard workflow for adding a new ProIT AV wrapper. Use it when a new product arrives from the China team with API documentation in PDF, Word, or Excel format.

The goal is to make future conversations simple:

1. Run the scaffold script.
2. Place the raw vendor documentation in the new product `docs/` folder.
3. Ask Cursor to read this workflow and build the wrapper, test, YAML, and exported API document.

## Deliverables

Every new product should produce these files:

- `apiwrappers/<ProductModel>/<ProductModel>.py`
- `apiwrappers/<ProductModel>/test_<ProductModel>_api.py`
- `apiwrappers/<ProductModel>/docs/<product_model>_api.yml`
- `apiwrappers/<ProductModel>/docs/<product_model>_api.md`
- `apiwrappers/<ProductModel>/docs/<product_model>_api.html`
- `apiwrappers/<ProductModel>/docs/<product_model>_api.pdf`

The YAML file is the source of truth for the shareable API documentation.

## Standard Package Layout

For a normal single-model product:

```text
apiwrappers/<ProductModel>/
├── <ProductModel>.py
├── test_<ProductModel>_api.py
└── docs/
    ├── <vendor source files>
    ├── <product_model>_api.yml
    ├── <product_model>_api.md
    ├── <product_model>_api.html
    └── <product_model>_api.pdf
```

## Wrapper Responsibilities

The wrapper file should contain:

- connection and authentication behavior
- debug flag support
- request/response helpers
- one method per device command or command group
- response cleanup/parsing helpers
- optional metadata helpers if a test file needs reusable command descriptions

The wrapper should not contain the full GET-style test runner. That belongs in the standalone `test_<ProductModel>_api.py`.

## Test Responsibilities

Each `test_<ProductModel>_api.py` should be runnable directly from Cursor/VSCode through `__main__`.

At the top of the file keep these variables visible:

```python
DEVICE_IP = "10.0.50.19"
PORT = 23
TIMEOUT = 2.0
DEBUG = False
MARKDOWN_OUTPUT = False
```

The test file should include:

- a `GET_COMMANDS` list for all read-style commands
- response-time measurement for every command
- plain-text report output
- markdown report output when `MARKDOWN_OUTPUT = True`
- setup/teardown hooks for saving and restoring state if required
- a summary section with success, failure, skipped, and success rate

“Get-style” means read-only commands even if the API does not use the literal keyword `GET`.

## YAML Responsibilities

Keep one YAML file per product by default:

- file name: lowercase model-based name such as `mx0404_n301_api.yml`
- top-level keys: `module`, `description`, `schema`, `commands`
- command descriptions normalized into clean English
- parameter names normalized even if the vendor documentation is inconsistent

Use `apiwrappers/SC010/docs/sc010_device.yml` as the style reference.

## Exported API Documentation

After the YAML is complete, generate clean user-facing documentation from it:

- markdown for easy review and editing
- HTML for browser-based sharing
- PDF for the final handoff artifact

Use the root-level script:

- `export_api_docs.py`

The YAML remains the source of truth. Do not hand-edit generated Markdown, HTML, or PDF if the YAML is wrong. Fix the YAML and regenerate.

## Root-Level Automation Scripts

### 1. Scaffold a new wrapper

Run:

```bash
python new_wrapper_scaffold.py
```

The script will prompt for the product model and create the folder, wrapper, test, and YAML skeleton.

### 2. Export shareable API docs

Run:

```bash
python export_api_docs.py
```

If the script needs a dependency that is not installed, it should say so clearly.

## Handling Vendor Docs

Vendor input can arrive in many forms:

- PDF
- `.doc` or `.docx`
- Excel spreadsheets

Recommended workflow:

1. Put the source file into the product `docs/` folder.
2. Ask Cursor to read the vendor file.
3. Extract all commands into the standardized YAML.
4. Implement the wrapper methods from that YAML.
5. Build the standalone test manifest from the read-only commands.
6. Run the test file against the live device.
7. Export the shareable API documentation from the YAML.

## Standard Cursor Prompt

After scaffolding and adding vendor docs, a future prompt can be as short as:

```text
Read docs/NEW_WRAPPER_WORKFLOW.md.
Scaffold <ProductModel> if it does not already exist.
Read the vendor API document in apiwrappers/<ProductModel>/docs/.
Create or update the wrapper, standalone test, YAML, and exported API docs.
Follow the project wrapper conventions and use the shared test/report utilities.
```

## Definition Of Done

A new wrapper is complete only when all of the following exist:

- wrapper file
- standalone test file
- read-style command manifest
- response timing in the report
- plain-text report mode
- markdown report mode
- standardized single-file YAML
- generated Markdown, HTML, and PDF documentation

## Product Families

Families such as `apiwrappers/IP970_Family/` need a slightly different pattern.

Use this rule:

- single model: one normal product package
- product family: shared family base plus thin per-model wrappers

Recommended family structure:

```text
apiwrappers/IP970_Family/
├── base.py
├── discovery.py
├── IPD970/
│   └── IPD970.py
├── IPE970/
│   └── IPE970.py
└── docs/
```

For family products:

- keep common transport and shared commands in `base.py`
- keep model-specific commands and overrides in the model wrapper files
- keep one common strategy for read-style test execution
- if models mostly overlap, define common command metadata once and override only the differences

## Notes

- Prefer readable and maintainable wrappers over trying to over-abstract too early.
- Do not duplicate a whole family wrapper when only a few commands differ.
- If a family becomes too different over time, split it back into independent wrappers.
