"""Public reconstruction schema based on the historical hackathon workflow.

The 2024 notebooks loaded a wide ``leads.csv`` table and a one-to-many
``lead_notes.csv`` table, then joined ``ObjectID`` to ``ParentObjectID``.  This
module captures only the fields used by that public preprocessing workflow.  It
does not reproduce private records or claim to reproduce the full source schema.
"""

from __future__ import annotations

from typing import Final

ID_COLUMN: Final = "ObjectID"
NOTE_PARENT_COLUMN: Final = "ParentObjectID"
STATUS_COLUMN: Final = "Status_Text"
CONVERTED_STATUS: Final = "Converted"

# Status labels observed in the public 2024 notebook output.  This is a minimal
# reconstruction set, not a claim that the historical system had only these
# statuses.
OBSERVED_STATUS_VALUES: Final[tuple[str, ...]] = (
    "Converted",
    "Unqualified",
    "Closed",
)

# Fields selected by the public make_leads.ipynb preprocessing example after
# joining the lead and note tables.  Note-table fields remain separate below so
# the raw one-to-many relationship can be reconstructed faithfully.
LEAD_COLUMNS: Final[tuple[str, ...]] = (
    ID_COLUMN,
    "Name",
    "Source_Text",
    STATUS_COLUMN,
    "Start_Date",
    "End_Date",
    "Owner_Party_Name",
    "Sales_Unit_Name",
    "Sales_Territory_Name",
    "Note",
)

LEAD_NOTE_COLUMNS: Final[tuple[str, ...]] = (
    NOTE_PARENT_COLUMN,
    "Text",
    "Created_On",
)

# The historical notebook used these fields after the ObjectID/ParentObjectID
# join.  They are documented here for later preprocessing work.
JOINED_WORKFLOW_COLUMNS: Final[tuple[str, ...]] = (
    "Name",
    "Source_Text",
    STATUS_COLUMN,
    "Start_Date",
    "End_Date",
    "Owner_Party_Name",
    "Sales_Unit_Name",
    "Sales_Territory_Name",
    ID_COLUMN,
    "Created_On",
    "Note",
    "Text",
)
