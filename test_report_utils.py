"""Shared helpers for standalone GET-style wrapper tests."""

from dataclasses import dataclass
from typing import Any, Callable
import time


EQUALS = "=" * 80
DASHES = "-" * 60
DEFAULT_MARKDOWN_TABLE_RESULT_LIMIT = 56
DEFAULT_MARKDOWN_TABLE_COMMAND_LIMIT = 32


@dataclass
class CommandResult:
    method: str
    description: str
    command: str
    status: str
    success: bool
    execution_time: float
    result: str


def summarize_response(response: Any, limit: int = 240) -> str:
    """Shorten verbose responses for terminal-friendly reports."""
    if response is None:
        return "(no data)"

    text = " ".join(str(response).replace("\r", " ").replace("\n", " ").split())
    if not text:
        return "(no data)"
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def truncate_for_table(text: str, limit: int) -> str:
    """Shorten one value specifically for compact summary tables."""
    compact = " ".join(str(text).replace("\r", " ").replace("\n", " ").split())
    if len(compact) > limit:
        return compact[: limit - 3] + "..."
    return compact


def classify_result(result: Any) -> tuple[str, bool]:
    """Classify one command result."""
    if result is None or not str(result).strip():
        return "SKIPPED (no response)", False

    upper_result = str(result).upper()
    if any(token in upper_result for token in ("ERROR", "INVALID", "UNKNOWN", "FAILED")):
        return "FAILED (device error)", False

    return "SUCCESS", True


def resolve_info_value(value: Any) -> str:
    """Resolve header values that may be callables."""
    try:
        resolved = value() if callable(value) else value
    except Exception as exc:
        resolved = f"Unavailable ({exc})"
    return summarize_response(resolved, limit=160)


def render_plain_text_report(
    model: str,
    info_queries: list[tuple[str, Any]],
    results: list[CommandResult],
    state_note: str,
) -> str:
    """Render the standard plain-text wrapper test report."""
    lines = [f"{model} Device Wrapper API Test", "", EQUALS, "", "DEVICE INFORMATION", EQUALS, ""]

    for label, value in info_queries:
        lines.append(f"{label}: {resolve_info_value(value)}")

    lines.extend(["", state_note, "", f"Testing {len(results)} get methods...", EQUALS])

    for result in results:
        lines.extend(
            [
                "",
                f"{result.method}: {result.description}",
                f"Command: {result.command}",
                DASHES,
                f"Status: {result.status}",
                f"Response: {result.result}",
                f"Response time: {result.execution_time:.3f}s",
                DASHES,
            ]
        )

    success_count = sum(1 for result in results if result.status == "SUCCESS")
    failure_count = sum(1 for result in results if result.status.startswith("FAILED"))
    skipped_count = sum(1 for result in results if result.status.startswith("SKIPPED"))
    success_rate = (success_count / len(results) * 100) if results else 0.0

    lines.extend(
        [
            "",
            EQUALS,
            "TEST SUMMARY",
            EQUALS,
            f"Total methods tested: {len(results)}",
            f"Successful: {success_count}",
            f"Failed: {failure_count}",
            f"Skipped: {skipped_count}",
            f"Success rate: {success_rate:.1f}%",
            "",
            "-" * 80,
            "DETAILED RESULTS",
            "-" * 80,
            f"{'Command':<34} {'Status':<22} {'Time':<10} Result",
            "-" * 80,
        ]
    )

    for result in results:
        lines.append(
            f"{result.command:<34} {result.status[:22]:<22} {result.execution_time:.3f}s   {result.result}"
        )

    return "\n".join(lines)


def render_markdown_report(
    model: str,
    info_queries: list[tuple[str, Any]],
    results: list[CommandResult],
    state_note: str,
    table_command_limit: int = DEFAULT_MARKDOWN_TABLE_COMMAND_LIMIT,
    table_result_limit: int = DEFAULT_MARKDOWN_TABLE_RESULT_LIMIT,
) -> str:
    """Render a markdown report for copying into external reports."""
    success_count = sum(1 for result in results if result.status == "SUCCESS")
    failure_count = sum(1 for result in results if result.status.startswith("FAILED"))
    skipped_count = sum(1 for result in results if result.status.startswith("SKIPPED"))
    success_rate = (success_count / len(results) * 100) if results else 0.0

    lines = [f"# {model} Device Wrapper API Test", "", "## Device Information", ""]
    for label, value in info_queries:
        lines.append(f"- **{label}**: {resolve_info_value(value)}")

    lines.extend(["", f"- **Notes**: {state_note}", "", f"## Testing {len(results)} get methods", ""])

    for result in results:
        lines.extend(
            [
                f"### {result.method}",
                "",
                f"- **Description**: {result.description}",
                f"- **Command**: `{result.command}`",
                f"- **Status**: {result.status}",
                f"- **Response time**: {result.execution_time:.3f}s",
                "",
                "```text",
                result.result,
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Summary",
            "",
            f"- **Total methods tested**: {len(results)}",
            f"- **Successful**: {success_count}",
            f"- **Failed**: {failure_count}",
            f"- **Skipped**: {skipped_count}",
            f"- **Success rate**: {success_rate:.1f}%",
            "",
            "## Detailed Results",
            "",
            "| Command | Status | Time | Result |",
            "|---|---|---:|---|",
        ]
    )

    for result in results:
        safe_command = truncate_for_table(result.command, table_command_limit).replace("|", "\\|")
        safe_result = truncate_for_table(result.result, table_result_limit).replace("|", "\\|")
        lines.append(
            f"| `{safe_command}` | {result.status} | {result.execution_time:.3f}s | {safe_result} |"
        )

    return "\n".join(lines)


def run_get_style_tests(
    *,
    device: Any,
    model: str,
    get_commands: list[dict[str, Any]],
    info_queries: list[tuple[str, Any]],
    markdown_output: bool = False,
    markdown_table_command_limit: int = DEFAULT_MARKDOWN_TABLE_COMMAND_LIMIT,
    markdown_table_result_limit: int = DEFAULT_MARKDOWN_TABLE_RESULT_LIMIT,
    setup_hook: Callable[[Any], Any] | None = None,
    teardown_hook: Callable[[Any, Any], Any] | None = None,
) -> dict[str, Any]:
    """Execute the standard read-only wrapper test suite and print a report."""
    results: list[CommandResult] = []
    saved_state = None
    opened_here = False
    state_note = "No settings altered; nothing to restore after GET-style validation."

    if getattr(device, "tn", None) is None and hasattr(device, "connect"):
        if not device.connect():
            failure_report = {
                "success": 0,
                "failure": 1,
                "skipped": 0,
                "total": 0,
                "success_rate": 0.0,
                "results": [],
            }
            print(f"{model} Device Wrapper API Test")
            print()
            print("Failed to establish connection.")
            return failure_report
        opened_here = True

    try:
        if setup_hook is not None:
            saved_state = setup_hook(device)
            if isinstance(saved_state, dict) and saved_state.get("note"):
                state_note = str(saved_state["note"])

        for command_spec in get_commands:
            method_name = command_spec["method"]
            description = command_spec["description"]
            command = command_spec["command"]
            kwargs = command_spec.get("kwargs", {})

            try:
                method = getattr(device, method_name)
                start_time = time.time()
                raw_result = method(**kwargs)
                execution_time = round(time.time() - start_time, 3)
                status, success = classify_result(raw_result)
                results.append(
                    CommandResult(
                        method=method_name,
                        description=description,
                        command=command,
                        status=status,
                        success=success,
                        execution_time=execution_time,
                        result=summarize_response(raw_result),
                    )
                )
            except Exception as exc:
                results.append(
                    CommandResult(
                        method=method_name,
                        description=description,
                        command=command,
                        status=f"FAILED (Exception: {exc})",
                        success=False,
                        execution_time=0.0,
                        result="(exception)",
                    )
                )
    finally:
        if teardown_hook is not None:
            teardown_hook(device, saved_state)
        if opened_here and hasattr(device, "disconnect"):
            device.disconnect()

    report_text = (
        render_markdown_report(
            model,
            info_queries,
            results,
            state_note,
            table_command_limit=markdown_table_command_limit,
            table_result_limit=markdown_table_result_limit,
        )
        if markdown_output
        else render_plain_text_report(model, info_queries, results, state_note)
    )
    print(report_text)

    success_count = sum(1 for result in results if result.status == "SUCCESS")
    failure_count = sum(1 for result in results if result.status.startswith("FAILED"))
    skipped_count = sum(1 for result in results if result.status.startswith("SKIPPED"))
    success_rate = (success_count / len(results) * 100) if results else 0.0

    return {
        "success": success_count,
        "failure": failure_count,
        "skipped": skipped_count,
        "total": len(results),
        "success_rate": round(success_rate, 1),
        "results": [result.__dict__ for result in results],
        "markdown_output": markdown_output,
        "markdown_table_command_limit": markdown_table_command_limit,
        "markdown_table_result_limit": markdown_table_result_limit,
        "report_text": report_text,
    }
