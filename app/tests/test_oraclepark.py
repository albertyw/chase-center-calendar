import datetime
from pathlib import Path
import tempfile
from typing import Optional
import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from app import event, oraclepark


DOTHEBAY_SAMPLE_EVENT_DATA = """<div class="ds-events-group">
<div class="ds-list-break ds-break-date">
<div class="ds-break-left">
<a data-ds-listings-nav-ga="DATE_HEADING" href="/events/2021/10/13">
<span class="ds-list-break-date-english">Wednesday</span>
<span class="ds-list-break-date">Oct 13</span>
</a>
</div>
</div>
<div class="ds-listing event-card ds-event-category-sports" data-ds-ga-label="venue" data-permalink="/events/2021/10/13/san-francisco-giants-vs-los-angeles-dodgers-tickets" itemprop="event" itemscope="" itemtype="http://schema.org/Event">
<div class="ds-cover-image" style="background-image:url('https://assets0.dostuffmedia.com/uploads/aws_asset/aws_asset/8688395/fa1e97f6-da44-4010-9fde-100c991cbd30.jpg');"></div>
<a class="ds-listing-event-title url summary" href="/events/2021/10/13/san-francisco-giants-vs-los-angeles-dodgers-tickets" itemprop="url">
<span class="ds-byline"></span>
<span class="ds-listing-event-title-text" itemprop="name">San Francisco Giants vs. Los Angeles Dodgers</span>
</a>
<div class="ds-listing-details-container">
<div class="ds-listing-details">
<div class="ds-venue-name" itemprop="location" itemscope="" itemtype="http://schema.org/Place">
<span class="ds-icon ds-icon-marker"></span>
<a href="/venues/oracle-park" itemprop="url"><span itemprop="name">Oracle Park</span></a>
<span itemprop="address" itemscope="" itemtype="http://schema.org/PostalAddress">
<meta content="24 Willie Mays Plaza" itemprop="streetAddress">
<meta content="San Francisco" itemprop="addressLocality">
<meta content="CA" itemprop="addressRegion">
<meta content="94107" itemprop="postalCode">
</meta></meta></meta></meta></span>
</div>
<div class="ds-event-time dtstart">
               8:33PM

            </div>
<meta content="2021-10-13T20:33-0700" datetime="2021-10-13T20:33-0700" itemprop="startDate">
</meta></div>
<div class="ds-listing-extra-details">
<div class="ds-table-row-vert-align">
<div class="ds-listing-attendees">
</div>
<div class="ds-listing-actions">
<nav class="ds-utility-nav">
<div class="ds-btn-container-upvote">
<a class="ds-btn stretch ds-btn-large ds-btn-ical" data-ds-id="12554109" href="#">
<span class="ds-upvote-default"><span class="ds-icon ds-icon-arrow-up ds-icon-bg"></span><span class="ds-icon-text">1</span></span>
<span class="ds-upvote-active"><span class="ds-icon ds-icon-check ds-icon-bg"></span><span class="ds-icon-text">1</span></span>
</a>
</div>
<div class="ds-btn-container-buy-tix">
<span itemprop="offers" itemscope="" itemtype="http://schema.org/Offer">
<meta content="https://mpv.tickets.com/?agency=MLB_MPV&amp;orgid=2139&amp;pid=8980073" itemprop="url"/>
<a class="ds-btn ds-btn-large ds-buy-tix" href="https://mpv.tickets.com/?agency=MLB_MPV&amp;orgid=2139&amp;pid=8980073" title="BUY TICKETS"><span class="ds-icon ds-icon-ticket ds-icon-bg"></span>
<span class="ds-icon-text">Buy
                      </span></a></span>
</div>
</nav>
</div>
</div>
</div>
</div>
</div>
</div>
"""  # NOQA

TICKETING_SAMPLE_EVENT_DATA = """START DATE,START TIME,START TIME ET,SUBJECT,LOCATION,DESCRIPTION,END DATE,END DATE ET,END TIME,END TIME ET,REMINDER OFF,REMINDER ON,REMINDER DATE,REMINDER TIME,REMINDER TIME ET,SHOWTIMEAS FREE,SHOWTIMEAS BUSY
02/24/24,01:05 PM,03:05 PM,Cubs at Giants,Scottsdale Stadium - Scottsdale,"Local Radio: KNBR 680",02/24/24,02/24/24,04:05 PM,06:05 PM,FALSE,TRUE,02/24/24,12:05 PM,02:05 PM,FREE,BUSY
03/26/24,05:05 PM,08:05 PM,Athletics at Giants,Oracle Park - San Francisco,"Local TV: NBCS BA ----- Local Radio: KNBR 680",03/26/24,03/26/24,08:05 PM,11:05 PM,FALSE,TRUE,03/26/24,04:05 PM,07:05 PM,FREE,BUSY
""".encode('utf-8') # NOQA


class TestDothebayGetRawEvents(unittest.TestCase):
    @unittest.skip("Requires network access")
    def test_get(self) -> None:
        event_divs = oraclepark.dothebay_get_raw_events(oraclepark.DOTHEBAY_URLS[0])
        self.assertGreater(len(event_divs), 0)
        for event_div in event_divs:
            self.assertGreater(len(event_div), 0)

    @patch('requests.get')
    def test_get_mocked(self, mock_get: MagicMock) -> None:
        mock_get().content = DOTHEBAY_SAMPLE_EVENT_DATA
        event_divs = oraclepark.dothebay_get_raw_events(oraclepark.DOTHEBAY_URLS[0])
        self.assertGreater(len(event_divs), 0)
        for event_div in event_divs:
            self.assertGreater(len(event_div), 0)


class TestDothebayParseEventDiv(unittest.TestCase):
    def setUp(self) -> None:
        self.event_div = BeautifulSoup(DOTHEBAY_SAMPLE_EVENT_DATA, 'html.parser')

    def test_parse_event_div(self) -> None:
        event = oraclepark.dothebay_parse_event_div(self.event_div)
        self.assertEqual(event.id, '12554109')
        self.assertEqual(
            event.title,
            'San Francisco Giants vs. Los Angeles Dodgers',
        )
        self.assertEqual(
            event.slug,
            'san-francisco-giants-vs-los-angeles-dodgers',
        )
        self.assertEqual(event.subtitle, '')
        self.assertEqual(
            event.date,
            datetime.datetime.fromisoformat('2021-10-13T20:33-07:00'),
        )
        self.assertEqual(event.date_string, '2021-10-13T20:33:00-07:00')
        self.assertEqual(event.location_name, 'Oracle Park')
        self.assertEqual(event.location_type, '')
        self.assertEqual(event.duration, 4)


class TestTicketingGetEvents(unittest.TestCase):
    @patch('requests.get')
    def test_get_events(self, mock_get: MagicMock) -> None:
        mock_get().content = TICKETING_SAMPLE_EVENT_DATA
        events = oraclepark.ticketing_get_events()
        self.assertEqual(len(events), 1)
        e = events[0]
        self.assertEqual(e.id, 'athletics-at-giants2024-03-26T17:05:00-07:00')
        self.assertEqual(e.title, 'Athletics at Giants')
        self.assertEqual(e.slug, 'athletics-at-giants')
        self.assertEqual(
            e.subtitle,
            'Local TV: NBCS BA ----- Local Radio: KNBR 680',
        )
        self.assertEqual(
            e.date,
            datetime.datetime(2024, 3, 26, 17, 5, tzinfo=event.TIMEZONE),
        )
        self.assertEqual(e.date_string, '2024-03-26T17:05:00-07:00')
        self.assertEqual(e.location_name, 'Oracle Park - San Francisco')
        self.assertEqual(e.location_type, '')
        self.assertEqual(e.duration, 3)


class TestDeduplicateEvents(unittest.TestCase):
    def test_deduplicate_events(self) -> None:
        def generate_event(
            event_id: str,
            title: Optional[str] = None,
            date: Optional[datetime.datetime] = None,
        ) -> event.Event:
            e = event.Event()
            e.id = event_id
            if title:
                e.title = title
            else:
                e.title = 'Yankees at Giants'
            if date:
                e.date = date
            else:
                e.date = datetime.datetime(2024, 3, 14, 22, 38, 0)
            return e

        ticketing_events = [
            generate_event('0'),
        ]
        dothebay_events = [
            generate_event('0'),
            generate_event('1'),
            generate_event('2', title='asdf'),
            generate_event('3', title='Yankees vs. Giants'),
            generate_event('4', date=datetime.datetime(2024, 3, 14, 8, 38, 0)),
            generate_event('5', date=datetime.datetime(2024, 3, 15, 22, 38, 0)),
            generate_event('6', date=datetime.datetime(2024, 4, 14, 22, 38, 0)),
            generate_event('7', date=datetime.datetime(2025, 3, 14, 22, 38, 0)),
        ]
        events = oraclepark.deduplicate_events(ticketing_events, dothebay_events)
        self.assertIn(ticketing_events[0], events)
        self.assertNotIn(dothebay_events[0], events)
        self.assertNotIn(dothebay_events[1], events)
        self.assertIn(dothebay_events[2], events)
        self.assertNotIn(dothebay_events[3], events)
        self.assertNotIn(dothebay_events[4], events)
        self.assertIn(dothebay_events[5], events)
        self.assertIn(dothebay_events[6], events)
        self.assertIn(dothebay_events[7], events)
        self.assertEqual(len(events), 5)


class TestGetEvents(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_file = tempfile.NamedTemporaryFile()

    def tearDown(self) -> None:
        self.mock_file.close()

    @patch('requests.get')
    @patch('app.cache.get_cache_file')
    def test_get(self, mock_file: MagicMock, mock_get: MagicMock) -> None:
        response1 = MagicMock()
        response1.content = DOTHEBAY_SAMPLE_EVENT_DATA
        response2 = MagicMock()
        response2.content = TICKETING_SAMPLE_EVENT_DATA
        mock_get.side_effect = [response1, response1, response2]
        mock_file.return_value = Path(self.mock_file.name)
        events = oraclepark.get_events()
        self.assertGreater(len(events), 0)
        ids = [e.id for e in events]
        self.assertEqual(len(ids), len(set(ids)))

        new_events = oraclepark.get_events()
        self.assertEqual(len(new_events), len(events))
        self.assertEqual(new_events[0].id, events[0].id)
