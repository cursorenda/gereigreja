from datetime import date

from django.test import SimpleTestCase

from core.utils import get_weekday_label


class WeekdayLabelTests(SimpleTestCase):
    def test_label_portuguese_by_default(self):
        self.assertEqual(get_weekday_label(date(2024, 8, 5)), 'SEG')

    def test_label_can_be_generated_for_other_languages(self):
        self.assertEqual(get_weekday_label(date(2024, 8, 5), language='en'), 'MON')
