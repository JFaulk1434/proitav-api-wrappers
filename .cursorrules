# ProIT AV API Wrappers – Project Rules

This project contains Python API wrappers for ProIT AV products. When adding or modifying a product wrapper, follow these rules so wrappers stay consistent and testable.

**Quick reference**: Full templates, report format, and examples → `docs/WRAPPER_CONVENTIONS.md`.  
**API YAML style** → `apiwrappers/SC010/docs/sc010_device.yml`.

---

## 1. Project layout

Each product wrapper lives in its own package under `apiwrappers/`:

- **Package**: `apiwrappers/<ProductName>/` (e.g. `apiwrappers/SC010/`, `apiwrappers/CAM600/`)
- **Wrapper**: `apiwrappers/<ProductName>/<ProductName>.py` (main device class)
- **Docs**: `apiwrappers/<ProductName>/docs/` (API YAML, PDFs, etc.)
- **Tests**: `apiwrappers/<ProductName>/test_<ProductName>_api.py` (or `test_<product>_api.py` matching the module name)

---

## 2. Connection / debug flag

Every wrapper’s connection logic (e.g. `_connect`, `connect`) **must** support a `debug` flag:

- Add `debug: bool = False` to `__init__` (or the relevant connect API).
- When establishing the telnet (or other) connection, **only** call `tn.set_debuglevel(1)` if `debug` is `True`.
- **Default is `False`** (debug off). Do not enable debug by default.

Example:

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

Use `set_debuglevel(1)` (not 2) so telnet traffic is visible but not overly verbose.

---

## 3. API YAML file (SC010-style)

Each wrapper **must** have an API YAML file in `apiwrappers/<ProductName>/docs/`.

- **Path**: `apiwrappers/<ProductName>/docs/<product>_api.yml` or `<product>_device.yml` (match existing project naming).
- **Style**: Follow `apiwrappers/SC010/docs/sc010_device.yml`.

Required structure:

```yaml
module: <module_name>
description: <short description of this API scope>

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
  <command_name>:
    command: "<exact CLI command>"
    syntax: "<syntax with placeholders>"
    description: "<what it does>"
    parameters: []   # or list of param names
    response:
      type: json | string | confirmation
      schema: { ... }

  # For get/set pairs:
  <name>:
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

- Use the same layout and keys as `sc010_device.yml` (module, description, schema, commands with command/syntax/description/parameters/response).
- Document all commands the wrapper exposes. Split into multiple YAML files by module if needed, but keep the same structure.

---

## 4. Test file requirements

Each wrapper **must** have a dedicated test file:  
`apiwrappers/<ProductName>/test_<ProductName>_api.py` (or equivalent).

### 4.1 Setup / teardown – save and restore settings

- **Before** running GET tests:  
  - Identify any settings that tests will **change** (e.g. via SET commands or side effects).  
  - **Save** those settings (e.g. current value of each relevant setting).
- **After** all tests (in teardown / `finally`):  
  - **Restore** saved settings so the device is left in its original state.

Use `try` / `finally` (or pytest `setup_function`/`teardown_function` / `fixture`) so teardown always runs, even on failure.

### 4.2 What to test

- Test **all** GET (read-only) commands/methods exposed by the wrapper.
- Do **not** require modifying device state for GET tests; use saved state or default/minimal setup only.

### 4.3 Response time

- For **each** GET test, measure **response time** (e.g. `time.time()` before/after the call).
- **Include** that timing in the test output (e.g. per-command and optionally in the summary).

### 4.4 Report format

The test script **must** print a report that matches this structure. Output should be **plain text, easy to copy-paste** into reports (e.g. markdown or email).

```
{model} Device Wrapper API Test

================================================================================

DEVICE INFORMATION
================================================================================

<Print: firmware version, API version, model, MAC, and any other useful info the API provides.>

Testing {len(get_methods)} get methods...
================================================================================

{method_name}: {description}
Command: {command}
------------------------------------------------------------
<per-command result, status, and response time>
------------------------------------------------------------
... (repeat for each GET method)
```

- **Title**: `{model} Device Wrapper API Test` (e.g. `SC010 Device Wrapper API Test`).
- **Section headers**: `DEVICE INFORMATION`, then the list of GET methods.
- **For each GET**: `{method_name}: {description}`, `Command: {command}`, then result, status, and **response time**.
- Use `"=" * 80` and `"-" * 60` (or equivalent) for separators as shown.
- Keep the output **clean and report-ready** (no noisy debug logs unless `--debug` or similar is used).

---

## 5. Test output and reports

- All tests **must** track and **print** response time for each GET command.
- The printed report **must** follow the format in section 4.4.
- Prefer **markdown-friendly** or **plain-text** output so it can be copy-pasted into internal reports (markdown, Confluence, etc.) without extra editing.
- Optionally support a `--markdown` (or similar) flag that emits the same report as markdown (headings, code blocks) for direct paste into docs.

---

## 6. Checklist for a new wrapper

When adding a new product wrapper:

1. [ ] Create `apiwrappers/<ProductName>/` and `apiwrappers/<ProductName>/docs/`.
2. [ ] Implement the wrapper with a **debug** flag in the connection (default `False`), using `tn.set_debuglevel(1)` only when enabled.
3. [ ] Add `apiwrappers/<ProductName>/docs/<product>_api.yml` (or `_device.yml`) in **SC010 style** (see `apiwrappers/SC010/docs/sc010_device.yml`).
4. [ ] Add `apiwrappers/<ProductName>/test_<ProductName>_api.py` that:
   - Saves relevant settings before GET tests and restores them in teardown.
   - Tests **all** GET commands.
   - Measures and prints **response time** for each GET.
   - Prints the **report** in the exact format from section 4.4.
5. [ ] Ensure test output is **copy-paste friendly** for reports.

---

## 7. Reference files

- **API YAML style**: `apiwrappers/SC010/docs/sc010_device.yml`
- **Test + report examples**: `apiwrappers/SC010/SC010.py` (`test_all_get_commands`), `apiwrappers/MS0402_N011/test_MS0402_N011_api.py`
- **Conventions doc**: `docs/WRAPPER_CONVENTIONS.md` (templates, examples, report format)

When in doubt, match the structure and behavior of the SC010 wrapper and its test/report output.
