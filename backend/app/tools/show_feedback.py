"""List the latest feedback notes: `uv run python -m app.tools.show_feedback [how_many]`."""

from __future__ import annotations

import sys

from sqlalchemy import select

from ..db.models import Feedback, User
from ..db.session import session_factory


def main(limit: int = 30) -> None:
    with session_factory()() as db:
        rows = db.execute(select(Feedback, User.email).join(User, User.id == Feedback.user_id, isouter=True).order_by(Feedback.created_at.desc()).limit(limit)).all()
        if not rows:
            print("No feedback yet.")
        for f, email in rows:
            print(f"[{f.created_at:%Y-%m-%d %H:%M}] {f.kind.upper()} from {email or 'deleted account'} on {f.page or '?'}\n  {f.message}")
            if f.details:
                print("  details: " + f.details.replace("\n", " | ")[:400])


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
