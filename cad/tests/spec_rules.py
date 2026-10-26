"""The PartSpec kind/bom rule. Run directly: `uv run python cad/tests/spec_rules.py`.

Not named test_*.py: test_checks.py imports every test_*.py as a file of seeds.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # cad/ holds params and parts

from parts.spec import PartSpec, at_origin


def make(**changes) -> PartSpec:
    base = dict(build=lambda c: None, place=at_origin, group="body", kind="printed", color="#000000",
                print_rotation=(0, 0, 0))
    return PartSpec(**{**base, **changes})


def rejects(**changes) -> bool:
    try:
        make(**changes)
    except ValueError:
        return True
    return False


def main() -> int:
    stock = dict(kind="stock", print_rotation=None, bom="1")
    cases = {
        "printed part with a bom row is rejected": rejects(bom="1"),
        "stock part without a bom row is rejected": rejects(**{**stock, "bom": None}),
        "bought part without a bom row is rejected": rejects(**{**stock, "kind": "bought", "bom": None}),
        "stock part with a print rotation is rejected": rejects(**{**stock, "print_rotation": (0, 0, 0)}),
        "printed part without a print rotation is rejected": rejects(print_rotation=None),
        "printed part is accepted": not rejects(),
        "stock part with a bom row is accepted": not rejects(**stock),
        "bought part with a bom row is accepted": not rejects(**{**stock, "kind": "bought", "bom": "7b"}),
        "film that loads into the camera needs no bom row": not rejects(
            **{**stock, "kind": "bought", "bom": None, "inventory": False}),
        "an excluded printed part with no bom row is accepted": not rejects(inventory=False),
    }
    failed = [name for name, ok in cases.items() if not ok]
    for name, ok in cases.items():
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
