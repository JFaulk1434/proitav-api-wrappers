# API Wrapper Conventions

This document defines conventions for ProIT AV API wrappers. Use it together with `.cursorrules` when adding or updating product wrappers. The goal is consistent structure, testability, and **report-ready output** you can copy-paste into internal reports.

---

## 1. Test report format (exact template)

Every wrapper test must print a report in this structure. Output is plain text, copy-paste friendly for markdown or other reports.

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

```
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
- One YAML per logical module; multiple files OK (e.g. `sc010_device.yml`, `sc010_config.yml`).

---

## 6. Test file layout

- **Path**: `apiwrappers/<ProductName>/test_<ProductName>_api.py`
- **Content**:
  1. Docstring: purpose, usage, example command line.
  2. Imports (including `time` for response-time measurement).
  3. Setup: connect, save settings.
  4. Loop over all GET methods: measure time, run method, record result, print per-command block.
  5. Teardown: restore settings, disconnect.
  6. Summary: counts, success rate, optional table.
  7. `if __name__ == "__main__"`: parse CLI (e.g. device IP, `--debug`), run test, exit with 0/1 based on success rate if desired.

---

## 7. Copy-paste–friendly output

- Use **plain text** and fixed-width separators (`=`, `-`).
- Avoid escape codes or fancy formatting that break when pasted into markdown or email.
- Keep lines reasonably short so they don’t wrap badly in reports.
- Optional: provide a `--markdown` flag that prints the same structure as fenced markdown (e.g. headings, code blocks) for direct paste into Confluence or similar.

---

## 8. Reference implementations

| Item | Location |
|------|----------|
| API YAML style | `apiwrappers/SC010/docs/sc010_device.yml` |
| Wrapper + `test_all_get_commands` | `apiwrappers/SC010/SC010.py` |
| Standalone test script | `apiwrappers/MS0402_N011/test_MS0402_N011_api.py` |
| Debug flag in connection | `apiwrappers/FSC640/FSC640.py`, `apiwrappers/MS0402_N011/MS0402_N011.py` |

When adding a new wrapper, align its structure, YAML, and test report with these references and the templates above.
