# IP970 Family Pattern

This folder demonstrates the recommended structure for product families that
share transport behavior and most commands.

## Structure

- `base.py`: shared telnet/session logic and shared command templates
- `IPD970/IPD970.py`: model-specific wrapper for IPD970
- `IPE970/IPE970.py`: model-specific wrapper for IPE970
- `discovery.py`: shared discovery logic for the family

## Rules

- keep shared connection and response parsing in `base.py`
- add model-specific commands by extending `COMMAND_TEMPLATES`
- avoid copying the whole wrapper when only a few commands differ
- keep shared read-style test patterns and YAML strategy at the family level

## Suggested YAML Strategy

For families, use one of these two approaches:

1. One common YAML source plus model-specific overrides.
2. One generated final YAML per model produced from common data.

For this repository, the preferred implementation pattern is:

- common command definitions once
- thin per-model overrides only where behavior differs
