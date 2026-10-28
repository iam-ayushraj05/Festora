from typing import Any

from apps.events.models import Event


def find_schedule_conflicts(event: Event) -> list[dict[str, Any]]:
    """Detect overlapping schedule items for the given event using interval sweep line with early termination."""
    items = list(event.schedule_items.only("id", "title", "start_time", "end_time", "location").order_by("start_time"))
    conflicts = []
    n = len(items)

    for i in range(n):
        item_a = items[i]
        for j in range(i + 1, n):
            item_b = items[j]

            # Since items are ordered by start_time:
            # If item_b starts at or after item_a ends, all subsequent items will also start
            # at or after item_a ends and cannot overlap item_a.
            if item_b.start_time >= item_a.end_time:
                break

            if item_b.start_time < item_a.end_time and item_a.start_time < item_b.end_time:
                conflicts.append(
                    {
                        "item_a": {
                            "id": str(item_a.id),
                            "title": item_a.title,
                            "start_time": item_a.start_time.isoformat(),
                            "end_time": item_a.end_time.isoformat(),
                            "location": item_a.location,
                        },
                        "item_b": {
                            "id": str(item_b.id),
                            "title": item_b.title,
                            "start_time": item_b.start_time.isoformat(),
                            "end_time": item_b.end_time.isoformat(),
                            "location": item_b.location,
                        },
                        "conflict_type": "overlap",
                    }
                )

    return conflicts
