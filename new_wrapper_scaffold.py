"""Create the standard file structure for a new wrapper package."""

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = REPO_ROOT / "templates"
APIWRAPPERS_DIR = REPO_ROOT / "apiwrappers"


def sanitize_yaml_name(product_model: str) -> str:
    """Convert a product model into the standard YAML file name."""
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", product_model).strip("_").lower()
    return f"{normalized}_api.yml"


def build_class_name(product_model: str) -> str:
    """Convert a product model into a valid Python class name."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", product_model).strip("_")
    return f"{cleaned}_Device"


def render_template(template_name: str, replacements: dict[str, str]) -> str:
    """Load and fill a template file."""
    template_path = TEMPLATES_DIR / template_name
    content = template_path.read_text()
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def write_file(path: Path, contents: str):
    """Write one file and report what happened."""
    path.write_text(contents)
    print(f"Created {path.relative_to(REPO_ROOT)}")


def main():
    print("ProIT AV Wrapper Scaffold")
    print("=" * 40)
    product_model = input("Enter the product model / part number: ").strip()

    if not product_model:
        raise SystemExit("Product model is required.")

    product_dir = APIWRAPPERS_DIR / product_model
    docs_dir = product_dir / "docs"

    if product_dir.exists():
        raise SystemExit(f"{product_dir} already exists. Aborting.")

    product_dir.mkdir(parents=True)
    docs_dir.mkdir()

    replacements = {
        "PRODUCT_MODEL": product_model,
        "CLASS_NAME": build_class_name(product_model),
        "YAML_FILE_NAME": sanitize_yaml_name(product_model),
    }

    write_file(
        product_dir / f"{product_model}.py",
        render_template("wrapper.py.tmpl", replacements),
    )
    write_file(
        product_dir / f"test_{product_model}_api.py",
        render_template("test_api.py.tmpl", replacements),
    )
    write_file(
        docs_dir / sanitize_yaml_name(product_model),
        render_template("api.yml.tmpl", replacements),
    )

    print()
    print("Next steps:")
    print("1. Place the vendor API document in the new docs folder.")
    print("2. Ask Cursor to read docs/NEW_WRAPPER_WORKFLOW.md.")
    print("3. Ask Cursor to build the wrapper, standalone test, YAML, and exported API docs.")


if __name__ == "__main__":
    main()
