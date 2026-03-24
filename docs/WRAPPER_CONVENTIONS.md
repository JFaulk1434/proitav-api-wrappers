# API Wrapper Conventions

This document defines the repository-level conventions for ProIT AV API wrappers.

For the full step-by-step process for new products, start with `docs/NEW_WRAPPER_WORKFLOW.md`.

Use this file as the compact rules reference and formatting standard.

---

## 1. Test report format (exact template)

Every standalone wrapper test file must print a report in this structure. Output is plain text, copy-paste friendly for markdown or other reports.

```python
model = "SC010"  # or your product model

print(f"\n{model} Device Wrapper API Test\n")
print("=" * 80)
print()
print("DEVICE INFORMATION")
print("=" * 80)
print()
# Print: firmware version, API version, model, MAC, and any other useful info the API provides
# Example:
# print(f"API Version: {version_info.get('API version', 'Unknown')}")
# print(f"System Version: {version_info.get('System version', 'Unknown')}")
# print(f"Model: {model}")
# print(f"MAC: {mac_address}")
print()
print(f"\nTesting {len(get_methods)} get methods...")
for method_name, description, command in get_methods:
    print(f"\n{method_name}: {description}")
    print(f"Command: {command}")
    print("-" * 60)
    # Then print: status, response, response time (see below)
```

### Per-command output

For each GET method, include:

- **Status**: SUCCESS / FAILED / SKIPPED (and brief reason if failed)
- **Response**: The actual return value (or a truncated summary if huge)
- **Response time**: e.g. `Response time: 0.042s`

Example:

```text
get_version: Get API and system version information
Command: config get version
------------------------------------------------------------
Status: SUCCESS
Response: {'API version': '1.0', 'System version': '1.0.6'}
Response time: 0.042s
------------------------------------------------------------
```

### Summary section

After all GET tests, print a short summary:

- Total methods tested
- Successful / Failed / Skipped counts
- Success rate (percentage)
- Optional: table of `Command | Status | Time | Result` for easy scanning

---

## 2. Response time tracking

- **Measure** elapsed time for each GET call (e.g. `time.time()` before and after).
- **Store** the value (e.g. in a `results` list) and **print** it in the per-command output and in any summary table.
- Use a consistent unit (seconds) and precision (e.g. 3 decimal places: `0.042s`).

```python
start_time = time.time()
result = method(*args, **kwargs)
elapsed = round(time.time() - start_time, 3)
# Include elapsed in output and in results
```

---

## 3. Setup / teardown – save and restore settings

- **Before** running GET tests:
  - Determine which settings the test will **change** (e.g. via SET commands or side effects).
  - **Save** current values (e.g. in a dict or list).
- **After** tests (in `finally` or teardown):
  - **Restore** saved values so the device is unchanged.

Use `try` / `finally` so teardown always runs, even on exceptions:

```python
saved = {}

try:
    # Save any settings we might change
    saved["alias"] = device.get_alias("hostname1")
    # ... optionally change settings for specific tests ...

    # Run all GET tests
    for method_name, description, command in get_methods:
        ...
finally:
    # Restore settings
    if "alias" in saved:
        device.set_alias("hostname1", saved["alias"])
    device.disconnect()
```

If a wrapper has **no** settable state used by GET tests, document that explicitly (e.g. “No settings altered; nothing to restore”) and still use `try`/`finally` for connection cleanup.

---

## 4. Debug flag in connection

- Add `debug: bool = False` to the wrapper `__init__`.
- In the connection method, call `tn.set_debuglevel(1)` **only** when `debug=True`.
- Default is **disabled** (`False`).

```python
def __init__(self, host, timeout=5, debug=False, ...):
    self.debug = debug
    ...

def _connect(self):
    ...
    self.tn = telnetlib.Telnet(self.host, port=self.port, timeout=self.timeout)
    if self.debug:
        self.tn.set_debuglevel(1)
    ...
```

Use `set_debuglevel(1)` (not 2) for telnet verbosity.

---

## 5. API YAML layout (SC010-style)

Use `apiwrappers/SC010/docs/sc010_device.yml` as the reference. Required layout:

```yaml
module: <module_name>
description: <short description>

schema:
  command:
    required:
      - command
      - syntax
      - description
      - response
    properties:
      command: string
      syntax: string
      description: string
      parameters: list
      response:
        type: string
        schema: object

commands:
  <name>:
    command: "<exact CLI command>"
    syntax: "<syntax>"
    description: "<description>"
    parameters: []
    response:
      type: json | string | confirmation
      schema: { ... }

  <name_with_get_set>:
    get:
      command: "..."
      syntax: "..."
      description: "..."
      parameters: []
      response: { type: ..., schema: ... }
    set:
      command: "..."
      ...
```

- Same top-level keys and nesting as `sc010_device.yml`.
- Default to one YAML file per product in `docs/`.
- Only split into multiple YAML files when a product is unusually large or there is a strong reason to separate modules.

---

## 6. Test file layout

- **Path**: `apiwrappers/<ProductName>/test_<ProductName>_api.py`
- **Do not** put the full GET-style test runner inside the wrapper class for new wrappers.
- **Top-of-file settings** should be obvious when the file is opened:
  - `DEVICE_IP`
  - `PORT`
  - `TIMEOUT`
  - `DEBUG`
  - `MARKDOWN_OUTPUT`
- **Content**:
  1. Docstring describing purpose and usage.
  2. Imports and repository-root helper import setup if needed.
  3. Visible device configuration variables near the top.
  4. `GET_COMMANDS` or equivalent read-style command manifest.
  5. Setup: connect, save settings if needed.
  6. Loop over all read-style commands: measure time, run method, record result, print per-command block.
  7. Teardown: restore settings, disconnect.
  8. Summary: counts, success rate, optional table.
  9. `if __name__ == "__main__"`: run directly in Cursor/VSCode without requiring CLI arguments.

---

## 7. Copy-paste–friendly output

- Use **plain text** and fixed-width separators (`=`, `-`).
- Avoid escape codes or fancy formatting that break when pasted into markdown or email.
- Keep lines reasonably short so they don’t wrap badly in reports.
- Provide a clearly visible markdown mode toggle in the test file, such as `MARKDOWN_OUTPUT = True`.
- Tests may still support CLI overrides, but they should run cleanly from `__main__` without requiring CLI input.

---

## 8. Shared Automation

- Use `new_wrapper_scaffold.py` to create a new wrapper package skeleton.
- Use `templates/` for maintainable wrapper, test, and YAML templates.
- Use `test_report_utils.py` for shared report rendering and GET-style command execution.
- Use `export_api_docs.py` to generate Markdown, HTML, and PDF documentation from the YAML source file.

## 9. Product Families

For products that share a common API with small model-specific differences:

- keep a family folder
- move shared transport and common commands into a family base module
- keep thin model-specific wrappers for overrides and additions
- avoid duplicating nearly identical wrappers per model

Example target structure:

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

## 10. Reference implementations

| Item | Location |
| ------ | ---------- |
| API YAML style | `apiwrappers/SC010/docs/sc010_device.yml` |
| Full workflow guide | `docs/NEW_WRAPPER_WORKFLOW.md` |
| Standalone test script direction | `apiwrappers/MX0404_N301/test_MX0404_N301_api.py` |
| Legacy embedded test reference | `apiwrappers/SC010/SC010.py` |
| Debug flag in connection | `apiwrappers/FSC640/FSC640.py`, `apiwrappers/MS0402_N011/MS0402_N011.py` |
| Family-style shared base example | `apiwrappers/IP5100/IP5100.py` |

When adding a new wrapper, align its structure, YAML, standalone test, and generated API docs with these references and the shared templates.
