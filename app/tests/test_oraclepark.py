import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from app import oraclepark


SAMPLE_EVENT_DATA = """<div class="ds-events-group">
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


class TestGetRawEvents(unittest.TestCase):
    def test_get(self) -> None:
        event_divs = oraclepark.get_raw_events(oraclepark.URLS[0])
        self.assertGreater(len(event_divs), 0)
        for event_div in event_divs:
            self.assertGreater(len(event_div), 0)


class TestParseEventDiv(unittest.TestCase):
    def setUp(self) -> None:
        self.event_div = BeautifulSoup(SAMPLE_EVENT_DATA, 'html.parser')

    def test_parse_event_div(self) -> None:
        event = oraclepark.parse_event_div(self.event_div)
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
        self.assertEqual(event.ticket_required, True)
        self.assertEqual(event.ticket_available, True)
        self.assertEqual(event.ticket_sold_out, False)
        self.assertEqual(event.hide_road_game, False)
        self.assertEqual(event.duration, 4)


class TestGetEvents(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_file = tempfile.NamedTemporaryFile()

    def tearDown(self) -> None:
        self.mock_file.close()

    @patch('app.cache.get_cache_file')
    def test_get(self, mock_file: MagicMock) -> None:
        mock_file.return_value = Path(self.mock_file.name)
        events = oraclepark.get_events()
        self.assertGreater(len(events), 1)
        ids = [e.id for e in events]
        self.assertEqual(len(ids), len(set(ids)))

        new_events = oraclepark.get_events()
        self.assertEqual(len(new_events), len(events))
        self.assertEqual(new_events[0].id, events[0].id)
