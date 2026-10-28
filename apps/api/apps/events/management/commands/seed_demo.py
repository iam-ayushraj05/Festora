from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.events.models import Event, EventMember, EventMemberRole, EventType, EventStatus
from apps.guests.models import Guest, RSVP, InviteToken, RSVPStatus
from apps.budget.models import BudgetCategory, Expense
from apps.tasks.models import Task, TaskPriority, TaskStatus, ScheduleItem
from apps.vendors.models import Vendor, VendorCategory, QuoteRequest, QuoteStatus, Booking, BookingStatus
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = 'Seeds initial demo accounts, events, budget, vendors, timeline, and RSVPs for Festora'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Festora demo data...")

        # 1. Users
        organizer, _ = User.objects.get_or_create(
            email='demo@festora.test',
            defaults={
                'first_name': 'Ayush',
                'last_name': 'Raj',
                'is_staff': True
            }
        )
        organizer.set_password('FestoraDemo2024!')
        organizer.save()

        cohost, _ = User.objects.get_or_create(
            email='cohost@festora.test',
            defaults={
                'first_name': 'Elena',
                'last_name': 'Vance'
            }
        )
        cohost.set_password('FestoraDemo2024!')
        cohost.save()

        # 2. Vendors
        v_venue, _ = Vendor.objects.get_or_create(
            name='The Grand Celestial Ballroom & Gardens',
            defaults={
                'category': VendorCategory.VENUE,
                'contact_email': 'concierge@celestialballroom.com',
                'phone': '+1 (555) 234-5678',
                'rating': Decimal('4.95'),
                'price_range': '$$$',
                'description': 'Opulent glasshouse ballroom with lush private botanical gardens and full AV production rigging.'
            }
        )

        v_cater, _ = Vendor.objects.get_or_create(
            name='Golden Saffron & Silk Artisan Catering',
            defaults={
                'category': VendorCategory.CATERING,
                'contact_email': 'chef@saffronandsilk.com',
                'phone': '+1 (555) 345-6789',
                'rating': Decimal('4.90'),
                'price_range': '$$$',
                'description': 'Award-winning farm-to-table gourmet dining specializing in multi-course tasting menus and signature mixology.'
            }
        )

        v_photo, _ = Vendor.objects.get_or_create(
            name='Lumina Aperture Cinematography',
            defaults={
                'category': VendorCategory.PHOTOGRAPHY,
                'contact_email': 'info@luminafilms.com',
                'phone': '+1 (555) 456-7890',
                'rating': Decimal('4.88'),
                'price_range': '$$',
                'description': 'Editorial documentary-style wedding and celebration photography with same-day sneak peek reels.'
            }
        )

        v_dj, _ = Vendor.objects.get_or_create(
            name='Rhythm & Pulse Sound Collective',
            defaults={
                'category': VendorCategory.MUSIC_DJ,
                'contact_email': 'bookings@rhythmpulse.com',
                'phone': '+1 (555) 567-8901',
                'rating': Decimal('4.92'),
                'price_range': '$$',
                'description': 'Premier celebration DJs and hybrid live percussionists bringing contagious energy to the dance floor.'
            }
        )

        v_decor, _ = Vendor.objects.get_or_create(
            name='Velvet Petals & Gilded Light Floral Co.',
            defaults={
                'category': VendorCategory.DECOR_FLORAL,
                'contact_email': 'hello@velvetpetals.com',
                'phone': '+1 (555) 678-9012',
                'rating': Decimal('4.85'),
                'price_range': '$$',
                'description': 'Custom floral arches, romantic candle installations, and celestial ceiling draping.'
            }
        )

        # 3. Primary Event: Anya's 30th Birthday
        now = timezone.now()
        event_date = now + timedelta(days=21)

        event1, _ = Event.objects.get_or_create(
            name="Anya's 30th Birthday Soirée",
            defaults={
                'description': 'Milestone 30th celebration featuring rooftop cocktails, artisan taco grazing stations, and live jazz-funk fusion.',
                'event_type': EventType.BIRTHDAY,
                'venue': 'The Sky Lounge at Hudson Yards',
                'start_date': event_date.replace(hour=18, minute=0, second=0),
                'end_date': event_date.replace(hour=23, minute=30, second=0),
                'timezone': 'America/New_York',
                'budget': Decimal('8500.00'),
                'currency': 'USD',
                'status': EventStatus.CONFIRMED,
            }
        )

        EventMember.objects.get_or_create(event=event1, user=organizer, defaults={'role': EventMemberRole.OWNER})
        EventMember.objects.get_or_create(event=event1, user=cohost, defaults={'role': EventMemberRole.COHOST})

        # Budget categories and expenses for Event 1
        cat_venue, _ = BudgetCategory.objects.get_or_create(
            event=event1, name='Venue & Lounge Rental',
            defaults={'estimated_amount': Decimal('3000.00')}
        )
        cat_catering, _ = BudgetCategory.objects.get_or_create(
            event=event1, name='Catering & Signature Cocktails',
            defaults={'estimated_amount': Decimal('2800.00')}
        )
        cat_music, _ = BudgetCategory.objects.get_or_create(
            event=event1, name='DJ & Acoustic Band',
            defaults={'estimated_amount': Decimal('1200.00')}
        )
        cat_decor, _ = BudgetCategory.objects.get_or_create(
            event=event1, name='Neon Backdrop & Floral Accents',
            defaults={'estimated_amount': Decimal('1000.00')}
        )
        cat_misc, _ = BudgetCategory.objects.get_or_create(
            event=event1, name='Contingency & Custom Favors',
            defaults={'estimated_amount': Decimal('500.00')}
        )

        Expense.objects.get_or_create(
            category=cat_venue, description='Deposit on Sky Lounge terrace',
            defaults={'amount': Decimal('1500.00'), 'currency': 'USD', 'paid': True}
        )
        Expense.objects.get_or_create(
            category=cat_catering, description='Tasting session and bar setup deposit',
            defaults={'amount': Decimal('1200.00'), 'currency': 'USD', 'paid': True}
        )
        Expense.objects.get_or_create(
            category=cat_music, description='DJ booking retainer',
            defaults={'amount': Decimal('600.00'), 'currency': 'USD', 'paid': True}
        )

        # Guests & RSVPs for Event 1
        demo_guests = [
            ('Maya Lin', 'maya@example.com', 1, 'Vegetarian', RSVPStatus.ATTENDING),
            ('Liam Gallagher', 'liam@example.com', 0, 'Gluten-Free', RSVPStatus.ATTENDING),
            ('Sophia Rodriguez', 'sophia@example.com', 1, '', RSVPStatus.ATTENDING),
            ('David Kim', 'david@example.com', 0, 'No Shellfish', RSVPStatus.DECLINED),
            ('Zara Patel', 'zara@example.com', 2, 'Vegan', RSVPStatus.ATTENDING),
            ('Ethan Brooks', 'ethan@example.com', 0, '', RSVPStatus.TENTATIVE),
            ('Chloe Dubois', 'chloe@example.com', 1, 'Nut Allergy', RSVPStatus.ATTENDING),
            ('Marcus Sterling', 'marcus@example.com', 0, '', RSVPStatus.ATTENDING),
        ]

        for g_name, g_email, plus_ones, dietary, rsvp_status in demo_guests:
            guest, _ = Guest.objects.get_or_create(
                event=event1,
                name=g_name,
                defaults={
                    'email': g_email,
                    'plus_ones': plus_ones,
                    'dietary_requirements': dietary
                }
            )
            token_obj, _ = InviteToken.create_for_guest(guest)
            RSVP.objects.get_or_create(
                guest=guest,
                defaults={'response': rsvp_status, 'notes': 'Excited to celebrate with you!'}
            )

        # Tasks for Event 1
        tasks_data = [
            ('Finalize craft cocktail menu with caterer', TaskPriority.HIGH, TaskStatus.COMPLETED),
            ('Confirm neon "Cheers to 30" photo backdrop delivery', TaskPriority.HIGH, TaskStatus.IN_PROGRESS),
            ('Send song preference playlist to DJ', TaskPriority.MEDIUM, TaskStatus.TODO),
            ('Order customized golden matchbox party favors', TaskPriority.LOW, TaskStatus.COMPLETED),
            ('Review guest dietary restrictions with chef', TaskPriority.CRITICAL, TaskStatus.TODO),
        ]
        for t_title, t_priority, t_status in tasks_data:
            Task.objects.get_or_create(
                event=event1,
                title=t_title,
                defaults={'priority': t_priority, 'status': t_status, 'assigned_to': organizer}
            )

        # Day-of Timeline for Event 1
        schedule_data = [
            ('Vendor & Bartender Setup', 'Sky Lounge Bar', 16, 0, 17, 30),
            ('VIP Early Arrival & Golden Hour Photos', 'Terrace Lookout', 17, 30, 18, 15),
            ('Doors Open & Welcome Prosecco', 'Main Foyer', 18, 15, 19, 0),
            ('Artisan Grazing Buffet & Cocktail Hour', 'Dining Pavilion', 19, 0, 20, 30),
            ('Birthday Toast & Champagne Fountain', 'Main Stage', 20, 30, 21, 0),
            ('Dance Floor & Late Night Tacos', 'Ballroom & Terrace', 21, 0, 23, 30),
        ]
        for s_title, s_loc, s_h1, s_m1, s_h2, s_m2 in schedule_data:
            ScheduleItem.objects.get_or_create(
                event=event1,
                title=s_title,
                defaults={
                    'location': s_loc,
                    'start_time': event_date.replace(hour=s_h1, minute=s_m1, second=0),
                    'end_time': event_date.replace(hour=s_h2, minute=s_m2, second=0)
                }
            )

        # Bookings & Quotes for Event 1
        Booking.objects.get_or_create(
            event=event1,
            vendor=v_venue,
            defaults={
                'start_time': event_date.replace(hour=15, minute=0, second=0),
                'end_time': event_date.replace(hour=23, minute=59, second=0),
                'status': BookingStatus.CONFIRMED,
                'total_cost': Decimal('3000.00'),
                'deposit_paid': Decimal('1500.00'),
            }
        )

        QuoteRequest.objects.get_or_create(
            event=event1,
            vendor=v_cater,
            defaults={
                'status': QuoteStatus.ACCEPTED,
                'estimated_cost': Decimal('2800.00'),
                'message': 'Gourmet cocktail tasting menu for 30 guests.'
            }
        )

        # 4. Secondary Event: Marcus & Elena's Royal Wedding
        event2_date = now + timedelta(days=90)
        event2, _ = Event.objects.get_or_create(
            name="Marcus & Elena's Royal Wedding",
            defaults={
                'description': 'A breathtaking celebration of love featuring candlelight ceremony, 5-course banquet, and starlight dancing.',
                'event_type': EventType.WEDDING,
                'venue': 'The Grand Celestial Ballroom & Gardens',
                'start_date': event2_date.replace(hour=15, minute=0, second=0),
                'end_date': event2_date.replace(hour=23, minute=0, second=0),
                'timezone': 'America/New_York',
                'budget': Decimal('42000.00'),
                'currency': 'USD',
                'status': EventStatus.PLANNING,
            }
        )
        EventMember.objects.get_or_create(event=event2, user=organizer, defaults={'role': EventMemberRole.OWNER})

        # 5. In-App Notifications
        Notification.objects.get_or_create(
            user=organizer,
            event=event1,
            title='RSVP Update',
            defaults={
                'message': 'Zara Patel accepted your invitation (+2 guests, Vegan diet specified).',
                'read': False
            }
        )
        Notification.objects.get_or_create(
            user=organizer,
            event=event1,
            title='Vendor Confirmed',
            defaults={
                'message': 'The Grand Celestial Ballroom deposit payment has been verified.',
                'read': True
            }
        )

        self.stdout.write(self.style.SUCCESS("Festora demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("Demo login: demo@festora.test / FestoraDemo2024!"))
