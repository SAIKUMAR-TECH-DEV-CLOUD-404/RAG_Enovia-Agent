"""
bom_model.py
────────────
Data model for a single BOM relationship.
Keeps the domain object separate from loading / comparison logic.
"""


class BomKey:
    """
    Uniquely identifies a parent→child relationship in a BOM.

    Attributes
    ----------
    parent_type    : e.g. 'VPMReference', 'Part', …
    parent_part    : part number of the parent
    parent_version : version string of the parent
    child_part     : part number of the child component
    """

    __slots__ = ("parent_type", "parent_part", "parent_version", "child_part")

    def __init__(
        self,
        parent_type: str,
        parent_part: str,
        parent_version: str,
        child_part: str,
    ) -> None:
        self.parent_type    = parent_type
        self.parent_part    = parent_part
        self.parent_version = parent_version
        self.child_part     = child_part

    # ── Equality & hashing so BomKey works as a dict key ────────────────────
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, BomKey)
            and self.parent_type    == other.parent_type
            and self.parent_part    == other.parent_part
            and self.parent_version == other.parent_version
            and self.child_part     == other.child_part
        )

    def __hash__(self) -> int:
        return hash(
            (self.parent_type, self.parent_part, self.parent_version, self.child_part)
        )

    def __repr__(self) -> str:
        return (
            f"BomKey(type={self.parent_type!r}, parent={self.parent_part!r},"
            f" ver={self.parent_version!r}, child={self.child_part!r})"
        )
