"""Generate Markdown, HTML, and PDF API documentation from a wrapper YAML file."""

from pathlib import Path
import html
import re


REPO_ROOT = Path(__file__).resolve().parent
TERMS_FILE = REPO_ROOT / "docs" / "API_EXPORT_TERMS.yml"


def require_yaml():
    """Import PyYAML with a clear message if it is missing."""
    try:
        import yaml
    except Exception as exc:
        raise SystemExit(
            "PyYAML is required to export API docs. Install it with "
            "`pip install pyyaml` in your project environment."
        ) from exc
    return yaml


def optional_reportlab():
    """Import ReportLab if available."""
    try:
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer
    except Exception:
        return None
    return {
        "ParagraphStyle": ParagraphStyle,
        "getSampleStyleSheet": getSampleStyleSheet,
        "inch": inch,
        "Paragraph": Paragraph,
        "Preformatted": Preformatted,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Spacer": Spacer,
    }


def load_export_terms() -> dict:
    """Load terminology overrides used for generated docs."""
    if not TERMS_FILE.exists():
        return {"phrase_overrides": {}, "token_overrides": {}}

    yaml = require_yaml()
    data = yaml.safe_load(TERMS_FILE.read_text()) or {}
    return {
        "phrase_overrides": {
            str(key).strip().lower(): str(value)
            for key, value in data.get("phrase_overrides", {}).items()
        },
        "token_overrides": {
            str(key).strip().lower(): str(value)
            for key, value in data.get("token_overrides", {}).items()
        },
    }


EXPORT_TERMS = load_export_terms()


def is_command_leaf(node: dict) -> bool:
    """Return True when a mapping looks like one command entry."""
    return isinstance(node, dict) and {"command", "syntax", "description", "response"}.issubset(node.keys())


def prettify_name(name: str) -> str:
    """Convert identifiers into readable headings."""
    raw = str(name).strip()
    normalized = raw.lower()

    phrase_override = EXPORT_TERMS["phrase_overrides"].get(normalized)
    if phrase_override:
        return phrase_override

    tokens = [token for token in re.split(r"[_\-\s]+", raw) if token]
    pretty_tokens = []
    for token in tokens:
        token_lower = token.lower()
        phrase_override = EXPORT_TERMS["phrase_overrides"].get(token_lower)
        if phrase_override:
            pretty_tokens.append(phrase_override)
            continue

        token_override = EXPORT_TERMS["token_overrides"].get(token_lower)
        if token_override:
            pretty_tokens.append(token_override)
            continue

        pretty_tokens.append(token.title())

    return " ".join(pretty_tokens)


def make_anchor_id(path: list[str]) -> str:
    """Create a stable internal anchor for one command path."""
    joined = "-".join(path).lower()
    joined = re.sub(r"[^a-z0-9]+", "-", joined).strip("-")
    return joined or "command"


def iter_command_entries(mapping: dict, path: list[str] | None = None):
    """Flatten nested command groups while keeping their path."""
    path = path or []

    for name, node in mapping.items():
        if not isinstance(node, dict):
            continue

        if is_command_leaf(node):
            yield path + [name], node
            continue

        handled_variant = False
        for variant in ("get", "set", "save", "restore", "connection", "signal", "format"):
            if variant in node and isinstance(node[variant], dict) and is_command_leaf(node[variant]):
                handled_variant = True
                yield path + [name, variant], node[variant]

        if handled_variant:
            for child_name, child_node in node.items():
                if child_name not in {"get", "set", "save", "restore", "connection", "signal", "format"}:
                    if isinstance(child_node, dict):
                        yield from iter_command_entries({child_name: child_node}, path + [name])
            continue

        yield from iter_command_entries(node, path + [name])


def command_markdown(path: list[str], command: dict) -> str:
    """Render one command entry as Markdown."""
    heading_level = min(6, 2 + max(0, len(path) - 1))
    heading = "#" * heading_level
    anchor_id = make_anchor_id(path)
    parameters = command.get("parameters", [])
    response = command.get("response", {})

    lines = [
        f'<a id="{anchor_id}"></a>',
        "",
        f"{heading} {' / '.join(prettify_name(part) for part in path)}",
        "",
        f"- **Command**: `{command.get('command', '')}`",
        f"- **Syntax**: `{command.get('syntax', '')}`",
        f"- **Description**: {command.get('description', '')}",
        f"- **Parameters**: {', '.join(parameters) if parameters else 'None'}",
        f"- **Response Type**: {response.get('type', 'string')}",
    ]

    schema = response.get("schema")
    if schema:
        lines.extend(["", "```yaml", dump_simple_yaml(schema).strip(), "```"])
    lines.append("")
    return "\n".join(lines)


def dump_simple_yaml(value, indent: int = 0) -> str:
    """Render small schema snippets without depending on PyYAML output formatting."""
    prefix = " " * indent
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(dump_simple_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {item}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(dump_simple_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}- {item}")
        return "\n".join(lines)
    return f"{prefix}{value}"


def build_markdown(data: dict) -> str:
    """Build the full Markdown document from the loaded YAML."""
    module = data.get("module", "device")
    description = data.get("description", "")
    commands = data.get("commands", {})
    command_entries = list(iter_command_entries(commands))

    lines = [
        f"# {module.upper()} API Reference",
        "",
        description,
        "",
        "## Table of Contents",
        "",
    ]

    for path, _command in command_entries:
        pretty_path = " / ".join(prettify_name(part) for part in path)
        lines.append(f"- [{pretty_path}](#{make_anchor_id(path)})")

    lines.extend(
        [
            "",
        "## Command Reference",
        "",
        ]
    )

    for path, command in command_entries:
        lines.append(command_markdown(path, command))

    return "\n".join(lines).rstrip() + "\n"


def render_inline_markdown_html(text: str) -> str:
    """Render simple inline Markdown into HTML."""
    safe = html.escape(text)
    safe = re.sub(r"\[([^\]]+)\]\(#([^)]+)\)", r'<a href="#\2">\1</a>', safe)
    safe = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
    return safe


def render_inline_markdown_pdf(text: str) -> str:
    """Render simple inline Markdown into ReportLab paragraph markup."""
    safe = html.escape(text)
    safe = re.sub(r"\[([^\]]+)\]\(#([^)]+)\)", r'<link href="#\2">\1</link>', safe)
    safe = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", safe)
    safe = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', safe)
    return safe


def markdown_to_html(markdown_text: str, title: str) -> str:
    """Convert the generated Markdown to simple HTML."""
    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{html.escape(title)}</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 2rem auto; max-width: 960px; line-height: 1.5; color: #222; }",
        "code, pre { font-family: Menlo, Consolas, monospace; }",
        "pre { background: #f5f5f5; padding: 1rem; overflow-x: auto; }",
        "h1, h2, h3, h4 { margin-top: 1.5rem; }",
        "ul { padding-left: 1.5rem; }",
        "</style>",
        "</head>",
        "<body>",
    ]

    in_code = False
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            close_list()
            if not in_code:
                html_lines.append("<pre><code>")
                in_code = True
            else:
                html_lines.append("</code></pre>")
                in_code = False
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        anchor_match = re.fullmatch(r'<a id="([^"]+)"></a>', line.strip())
        if anchor_match:
            close_list()
            html_lines.append(f'<div id="{html.escape(anchor_match.group(1))}"></div>')
        elif line.startswith("# "):
            close_list()
            heading_text = line[2:]
            html_lines.append(f'<h1 id="{make_anchor_id([heading_text])}">{html.escape(heading_text)}</h1>')
        elif line.startswith("## "):
            close_list()
            heading_text = line[3:]
            html_lines.append(f'<h2 id="{make_anchor_id([heading_text])}">{html.escape(heading_text)}</h2>')
        elif line.startswith("### "):
            close_list()
            heading_text = line[4:]
            html_lines.append(f'<h3 id="{make_anchor_id([heading_text])}">{html.escape(heading_text)}</h3>')
        elif line.startswith("#### "):
            close_list()
            heading_text = line[5:]
            html_lines.append(f'<h4 id="{make_anchor_id([heading_text])}">{html.escape(heading_text)}</h4>')
        elif line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{render_inline_markdown_html(line[2:])}</li>")
        elif line == "":
            close_list()
            html_lines.append("")
        else:
            close_list()
            safe_line = render_inline_markdown_html(line)
            html_lines.append(f"<p>{safe_line}</p>")

    close_list()

    html_lines.extend(["</body>", "</html>"])
    return "\n".join(html_lines)


def write_pdf(markdown_text: str, pdf_path: Path, title: str) -> bool:
    """Write a simple PDF if ReportLab is available."""
    reportlab = optional_reportlab()
    if reportlab is None:
        return False

    doc = reportlab["SimpleDocTemplate"](str(pdf_path))
    styles = reportlab["getSampleStyleSheet"]()
    code_style = reportlab["ParagraphStyle"](
        "ApiCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=10,
        leftIndent=12,
    )
    toc_style = reportlab["ParagraphStyle"](
        "ApiToc",
        parent=styles["BodyText"],
        leftIndent=14,
        spaceAfter=4,
    )
    story = [reportlab["Paragraph"](html.escape(title), styles["Title"]), reportlab["Spacer"](1, 0.2 * reportlab["inch"])]
    in_code = False
    code_lines = []
    pending_anchor = None

    def flush_code():
        nonlocal code_lines
        if code_lines:
            story.append(reportlab["Preformatted"]("\n".join(code_lines), code_style))
            story.append(reportlab["Spacer"](1, 0.08 * reportlab["inch"]))
            code_lines = []

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                flush_code()
            continue

        if in_code:
            code_lines.append(line)
            continue

        anchor_match = re.fullmatch(r'<a id="([^"]+)"></a>', stripped)
        if anchor_match:
            pending_anchor = anchor_match.group(1)
            continue

        if not stripped:
            story.append(reportlab["Spacer"](1, 0.08 * reportlab["inch"]))
            continue
        if stripped.startswith("# "):
            heading_text = html.escape(stripped[2:])
            if pending_anchor:
                heading_text = f'<a name="{pending_anchor}"/>{heading_text}'
                pending_anchor = None
            story.append(reportlab["Paragraph"](heading_text, styles["Heading1"]))
        elif stripped.startswith("## "):
            heading_text = html.escape(stripped[3:])
            if pending_anchor:
                heading_text = f'<a name="{pending_anchor}"/>{heading_text}'
                pending_anchor = None
            story.append(reportlab["Paragraph"](heading_text, styles["Heading2"]))
        elif stripped.startswith("### "):
            heading_text = html.escape(stripped[4:])
            if pending_anchor:
                heading_text = f'<a name="{pending_anchor}"/>{heading_text}'
                pending_anchor = None
            story.append(reportlab["Paragraph"](heading_text, styles["Heading3"]))
        elif stripped.startswith("#### "):
            heading_text = html.escape(stripped[5:])
            if pending_anchor:
                heading_text = f'<a name="{pending_anchor}"/>{heading_text}'
                pending_anchor = None
            story.append(reportlab["Paragraph"](heading_text, styles["Heading4"]))
        elif stripped.startswith("- "):
            line_markup = render_inline_markdown_pdf(stripped[2:])
            link_match = re.fullmatch(r'\[([^\]]+)\]\(#([^)]+)\)', stripped[2:])
            if link_match:
                line_markup = f'<link href="#{link_match.group(2)}">{html.escape(link_match.group(1))}</link>'
                story.append(reportlab["Paragraph"](line_markup, toc_style, bulletText=u"\u2022"))
            else:
                story.append(
                    reportlab["Paragraph"](
                        line_markup,
                        styles["BodyText"],
                        bulletText=u"\u2022",
                    )
                )
        else:
            story.append(reportlab["Paragraph"](render_inline_markdown_pdf(stripped), styles["BodyText"]))

    doc.build(story)
    return True


def choose_yaml_file() -> Path:
    """Prompt for a YAML path if one was not provided."""
    user_input = input("Enter the path to the product YAML file: ").strip()
    yaml_path = Path(user_input)
    if not yaml_path.is_absolute():
        yaml_path = (REPO_ROOT / yaml_path).resolve()
    return yaml_path


def main():
    yaml = require_yaml()
    yaml_path = choose_yaml_file()
    if not yaml_path.exists():
        raise SystemExit(f"YAML file not found: {yaml_path}")

    data = yaml.safe_load(yaml_path.read_text()) or {}
    markdown_text = build_markdown(data)
    title = data.get("description") or yaml_path.stem

    markdown_path = yaml_path.with_suffix(".md")
    html_path = yaml_path.with_suffix(".html")
    pdf_path = yaml_path.with_suffix(".pdf")

    markdown_path.write_text(markdown_text)
    html_path.write_text(markdown_to_html(markdown_text, title))

    wrote_pdf = write_pdf(markdown_text, pdf_path, title)

    print(f"Wrote {markdown_path}")
    print(f"Wrote {html_path}")
    if wrote_pdf:
        print(f"Wrote {pdf_path}")
    else:
        print(
            "Skipped PDF output because ReportLab is not installed. "
            "Install it with `pip install reportlab` and run the exporter again."
        )


if __name__ == "__main__":
    main()
