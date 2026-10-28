from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from .models import AIRequest


def check_and_record_rate_limit(user, request_type: str, prompt_summary: str) -> bool:
    """Check if user has exceeded max daily AI requests (default 50/day)."""
    max_requests = getattr(settings, "AI_MAX_REQUESTS_PER_USER_PER_DAY", 50)
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = AIRequest.objects.filter(user=user, created_at__gte=today_start).count()

    if today_count >= max_requests:
        AIRequest.objects.create(
            user=user,
            request_type=request_type,
            prompt_summary=prompt_summary[:250],
            status="rate_limited",
        )
        return False

    AIRequest.objects.create(
        user=user,
        request_type=request_type,
        prompt_summary=prompt_summary[:250],
        status="success",
    )
    return True


def generate_personalized_ideas(
    event_type: str,
    vibe: str = "elegant",
    guest_count: int = 50,
    budget_level: str = "moderate",
) -> dict:
    """Generate curated themes, color palettes, decor concepts, and invitation wording."""
    themes_db = {
        "wedding": [
            {
                "theme_title": "Ethereal Garden Bloom",
                "palette": ["Champagne Gold", "Sage Green", "Dusty Rose", "Ivory"],
                "decor_concept": "Cascading eucalyptus arches, warm fairy light canopies, floating glass orb candles, and raw linen table runners.",
                "signature_cocktails": [
                    "Blushing Bride Bellini (Prosecco, peach puree, rose water)",
                    "Elderflower Gin Spritz",
                ],
                "entertainment": [
                    "Acoustic cello & violin duo for ceremony",
                    "Live brass funk band for reception dancing",
                ],
                "invitation_copy": "Together with their families, invite you to celebrate a lifetime of love and joyous revelry under starlit skies.",
                "cost_saving_tip": "Repurpose ceremony floral urns as reception head table centerpieces.",
            },
            {
                "theme_title": "Royal Velvet & Golden Starlight",
                "palette": [
                    "Deep Obsidian",
                    "Royal Violet",
                    "Burnished Gold",
                    "Crimson",
                ],
                "decor_concept": "Dramatic velvet drapery, crystal candelabras, warm amber uplighting, and gold-rimmed glassware.",
                "signature_cocktails": [
                    "Midnight Sparkler (Blackberry liqueur, bourbon, sparkling cider)",
                    "Golden Saffron Elixir",
                ],
                "entertainment": [
                    "Aerial silk performer",
                    "High-energy live DJ with synchronized lighting",
                ],
                "invitation_copy": "You are cordially invited to an unforgettable evening of opulence, dance, and lifelong celebration.",
                "cost_saving_tip": "Focus opulent decor on focal photo backdrop and head table rather than every peripheral corner.",
            },
        ],
        "birthday": [
            {
                "theme_title": "Neon Starlight Glow & Cocktail Soirée",
                "palette": [
                    "Electric Indigo",
                    "Neon Coral",
                    "Luminous Gold",
                    "Midnight Black",
                ],
                "decor_concept": "Custom neon signage, interactive LED photo booth, geometric metallic table centerpieces, and floating balloons with micro-lights.",
                "signature_cocktails": [
                    "Electric Sunset Punch",
                    "Smoky Mezcal Paloma with rosemary smoke",
                ],
                "entertainment": [
                    "Silent disco headset battle",
                    "Interactive molecular mixology pop-up bar",
                ],
                "invitation_copy": "Cheers to another chapter! Join us for a night of vibrant beats, signature drinks, and endless memories.",
                "cost_saving_tip": "Opt for a dessert & taco grazing station instead of formal 3-course plated dinner.",
            },
            {
                "theme_title": "Boho Sunset Picnic & Acoustic Jam",
                "palette": ["Terracotta", "Warm Mustard", "Sand Beige", "Peach"],
                "decor_concept": "Low wooden pallet tables, layered Moroccan rugs, oversized floor cushions, dried pampas grass, and rattan lanterns.",
                "signature_cocktails": [
                    "Sun-drenched Aperol Spritz",
                    "Hibiscus Mint Cooler (mocktail)",
                ],
                "entertainment": [
                    "Campfire acoustic guitar set",
                    "Polaroid guestbook signing station",
                ],
                "invitation_copy": "Golden hour vibes, good friends, and heartfelt toasts. Let's celebrate life together!",
                "cost_saving_tip": "Host in an outdoor scenic public park or backyard to eliminate venue rental fees.",
            },
        ],
        "community": [
            {
                "theme_title": "Unity Horizon: Cultural Street Fair & Harvest Fest",
                "palette": [
                    "Vibrant Marigold",
                    "Teal Blue",
                    "Emerald Green",
                    "Warm Terracotta",
                ],
                "decor_concept": "Festive bunting overhead, artisan wooden food stalls, community art canvas wall, and solar fairy lights.",
                "signature_cocktails": [
                    "Artisan Spiced Cider",
                    "Citrus Mint Refresher",
                ],
                "entertainment": [
                    "Local school marching band",
                    "Multicultural dance showcase",
                    "Open-mic storytelling stage",
                ],
                "invitation_copy": "Bringing our neighborhood together! Come for the flavors, stay for the music, and celebrate community spirit.",
                "cost_saving_tip": "Partner with local vendors for co-sponsored equipment rentals and volunteer support.",
            }
        ],
    }

    category = event_type if event_type in themes_db else "community"
    options = themes_db[category]
    selected = options[0]

    return {
        "is_suggestion": True,
        "event_type": event_type,
        "guest_count": guest_count,
        "theme": selected,
        "alternative_themes": ([opt["theme_title"] for opt in options[1:]] if len(options) > 1 else []),
    }


def generate_budget_allocation(total_budget: Decimal, event_type: str = "wedding") -> dict:
    """Generate sensible percentage budget allocation tailored to event type."""
    splits = {
        "wedding": [
            ("Venue & Hall", Decimal("0.30")),
            ("Catering & Bar", Decimal("0.30")),
            ("Photography & Video", Decimal("0.15")),
            ("Decor, Lighting & Floral", Decimal("0.10")),
            ("Music, DJ & Audio", Decimal("0.07")),
            ("Invitations & Favors", Decimal("0.03")),
            ("Emergency Buffer / Misc", Decimal("0.05")),
        ],
        "birthday": [
            ("Venue & Rentals", Decimal("0.25")),
            ("Food & Drinks", Decimal("0.35")),
            ("Decor & Theme Accents", Decimal("0.15")),
            ("DJ & Entertainment", Decimal("0.15")),
            ("Cake & Desserts", Decimal("0.05")),
            ("Buffer & Supplies", Decimal("0.05")),
        ],
        "community": [
            ("Permits & Venue Security", Decimal("0.20")),
            ("Sound, Stage & Lighting", Decimal("0.25")),
            ("Food Stalls & Refreshments", Decimal("0.25")),
            ("Signage, Banners & Promotion", Decimal("0.15")),
            ("Waste Management & First Aid", Decimal("0.10")),
            ("Contingency Reserve", Decimal("0.05")),
        ],
    }

    allocations = splits.get(event_type, splits["community"])
    categories = []
    total_allocated = Decimal("0.00")

    for name, pct in allocations:
        amount = round(total_budget * pct, 2)
        total_allocated += amount
        categories.append(
            {
                "name": name,
                "percentage": float(pct * 100),
                "estimated_amount": str(amount),
            }
        )

    return {
        "is_suggestion": True,
        "total_budget": str(total_budget),
        "categories": categories,
        "confidence_score": 0.96,
        "note": "These allocations reflect standard industry celebration cost distributions.",
    }


def generate_timeline_run_of_show(start_time_iso: str = None, event_type: str = "wedding") -> dict:
    """Generate detailed minute-by-minute day-of timeline."""
    timelines = {
        "wedding": [
            (
                "09:00 AM - 11:30 AM",
                "Bridal Party & Groom Hair & Makeup",
                "Bridal Suite",
            ),
            (
                "11:30 AM - 12:30 PM",
                "First Look & Couple Portraits",
                "Courtyard Garden",
            ),
            (
                "12:30 PM - 02:00 PM",
                "Vendor Arrival & Floral / Audio Setup",
                "Main Ballroom",
            ),
            (
                "02:30 PM - 03:00 PM",
                "Guest Arrival & Welcome Mocktails",
                "Foyer & Terrace",
            ),
            ("03:00 PM - 03:45 PM", "Ceremony & Exchange of Vows", "Grand Pavilion"),
            (
                "03:45 PM - 05:00 PM",
                "Cocktail Hour & Passed Hors d’Oeuvres",
                "Garden Terrace",
            ),
            ("05:15 PM - 05:30 PM", "Grand Entrance & Welcome Toasts", "Main Ballroom"),
            (
                "05:30 PM - 07:00 PM",
                "Dinner Service & Heartfelt Speeches",
                "Main Ballroom",
            ),
            (
                "07:00 PM - 07:30 PM",
                "First Dance & Cake Cutting Ceremony",
                "Dance Floor",
            ),
            ("07:30 PM - 10:30 PM", "Open Dance Floor & Dessert Buffet", "Dance Floor"),
            (
                "10:30 PM - 11:00 PM",
                "Sparkler Send-off & Grand Farewell",
                "Main Entrance",
            ),
        ],
        "birthday": [
            ("02:00 PM - 04:00 PM", "Host & Decor Team Setup", "Party Lounge"),
            ("04:00 PM - 04:30 PM", "DJ Audio Check & Bartender Prep", "Bar & Stage"),
            (
                "04:30 PM - 05:15 PM",
                "Guest Arrival, Photo Ops & Welcome Drinks",
                "Welcome Arch",
            ),
            ("05:15 PM - 06:15 PM", "Party Games & Interactive Trivia", "Main Stage"),
            (
                "06:15 PM - 07:30 PM",
                "Dinner Buffet & Grazing Tables Open",
                "Dining Area",
            ),
            (
                "07:30 PM - 08:00 PM",
                "Birthday Cake Ceremony & Video Tribute",
                "Main Stage",
            ),
            ("08:00 PM - 10:30 PM", "Dance Floor Open & Cocktails", "Dance Floor"),
            ("10:30 PM - 11:00 PM", "Wrap-up & Favor Handout", "Exit Lounge"),
        ],
        "community": [
            (
                "07:00 AM - 09:00 AM",
                "Vendor Stall Setup & Stage Rigging",
                "Festival Grounds",
            ),
            ("09:00 AM - 09:30 AM", "Safety Inspection & Sound Check", "Main Stage"),
            (
                "09:30 AM - 10:00 AM",
                "Gates Open to Public & Welcome Address",
                "Main Gate",
            ),
            (
                "10:00 AM - 01:00 PM",
                "Morning Workshops & Live Cultural Demos",
                "Pavilion Area",
            ),
            (
                "01:00 PM - 02:30 PM",
                "Community Lunch & Food Truck Showcase",
                "Food Boulevard",
            ),
            (
                "02:30 PM - 05:00 PM",
                "Music Showcase & Talent Competition",
                "Main Stage",
            ),
            ("05:00 PM - 05:30 PM", "Awards Ceremony & Closing Remarks", "Main Stage"),
            (
                "05:30 PM - 07:00 PM",
                "Site Cleanup & Vendor Pack-down",
                "Festival Grounds",
            ),
        ],
    }

    schedule_data = timelines.get(event_type, timelines["community"])
    items = []
    for time_range, title, loc in schedule_data:
        items.append(
            {
                "time_range": time_range,
                "title": title,
                "location": loc,
                "buffer_minutes": 15,
            }
        )

    return {
        "is_suggestion": True,
        "event_type": event_type,
        "items": items,
        "total_run_hours": 12 if event_type == "wedding" else 7,
    }


def generate_vendor_checklist(event_type: str = "wedding") -> dict:
    """Generate targeted checklist questions and milestones for vendors."""
    checklists = {
        "wedding": [
            {
                "category": "Venue",
                "task": "Verify noise curfew regulations and alcohol licensing requirements.",
                "priority": "critical",
            },
            {
                "category": "Catering",
                "task": "Schedule menu taste test and confirm dietary requirements (vegan/halal/allergies).",
                "priority": "high",
            },
            {
                "category": "Photography",
                "task": "Draft & share must-have family group shot list with the lead photographer.",
                "priority": "high",
            },
            {
                "category": "Music / DJ",
                "task": 'Submit "Must Play" and strict "Do Not Play" song lists 3 weeks prior.',
                "priority": "medium",
            },
            {
                "category": "Florist",
                "task": "Confirm delivery time and designate a recipient for boutonnieres and bouquets.",
                "priority": "medium",
            },
            {
                "category": "Transportation",
                "task": "Confirm guest shuttle schedules between host hotels and venue.",
                "priority": "low",
            },
        ],
        "birthday": [
            {
                "category": "Venue",
                "task": "Verify outside catering and decoration tape/hanging policies.",
                "priority": "high",
            },
            {
                "category": "Bakery",
                "task": "Finalize custom cake design, flavor, and delivery window.",
                "priority": "high",
            },
            {
                "category": "Entertainment",
                "task": "Confirm microphone and Bluetooth audio hookup with the venue.",
                "priority": "medium",
            },
            {
                "category": "Party Favors",
                "task": "Assemble customized favor bags with personalized thank you tags.",
                "priority": "low",
            },
        ],
        "community": [
            {
                "category": "Permits",
                "task": "Obtain city park permit, fire marshal clearance, and noise exemption.",
                "priority": "critical",
            },
            {
                "category": "Sanitation",
                "task": "Arrange portable restrooms and recycling/trash bins collection schedule.",
                "priority": "critical",
            },
            {
                "category": "Emergency",
                "task": "Reserve certified on-site First Aid responders and emergency vehicle lane.",
                "priority": "high",
            },
            {
                "category": "Power / Audio",
                "task": "Book outdoor generators and weatherproof cable ramps for stage wiring.",
                "priority": "high",
            },
        ],
    }
    return {
        "is_suggestion": True,
        "checklist": checklists.get(event_type, checklists["community"]),
    }
