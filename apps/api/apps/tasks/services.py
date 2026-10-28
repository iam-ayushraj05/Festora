from typing import List, Dict, Any
from .models import ScheduleItem
from apps.events.models import Event

def find_schedule_conflicts(event: Event) -> List[Dict[str, Any]]:
    """Detect overlapping schedule items for the given event."""
    items = list(event.schedule_items.order_by('start_time'))
    conflicts = []

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            item_a = items[i]
            item_b = items[j]

            # If item_b starts after or at item_a ends, and items are sorted by start_time,
            # item_b won't conflict with item_a, but subsequent items might still conflict if item_a spans long.
            # So check overlap:
            if item_a.start_time < item_b.end_time and item_b.start_time < item_a.end_time:
                conflicts.append({
                    'item_a': {
                        'id': str(item_a.id),
                        'title': item_a.title,
                        'start_time': item_a.start_time.isoformat(),
                        'end_time': item_a.end_time.isoformat(),
                        'location': item_a.location
                    },
                    'item_b': {
                        'id': str(item_b.id),
                        'title': item_b.title,
                        'start_time': item_b.start_time.isoformat(),
                        'end_time': item_b.end_time.isoformat(),
                        'location': item_b.location
                    },
                    'conflict_type': 'overlap'
                })

    return conflicts
