from datetime import date

from django.test import TestCase

from sales.models import Quotation, QuotationDailySequence


class QuotationNumberGenerationTests(TestCase):
    def test_generate_number_uses_expected_format(self):
        generated = Quotation.generate_number(date(2026, 5, 4))
        self.assertEqual(generated, 'E0426-1.1')

    def test_generate_number_increments_daily_sequence(self):
        first = Quotation.generate_number(date(2026, 5, 4))
        second = Quotation.generate_number(date(2026, 5, 4))

        self.assertEqual(first, 'E0426-1.1')
        self.assertEqual(second, 'E0426-2.1')

    def test_generate_number_resets_sequence_on_next_day(self):
        day_one = Quotation.generate_number(date(2026, 5, 4))
        day_two = Quotation.generate_number(date(2026, 5, 5))

        self.assertEqual(day_one, 'E0426-1.1')
        self.assertEqual(day_two, 'E0526-1.1')

    def test_daily_sequence_records_are_updated(self):
        Quotation.generate_number(date(2026, 5, 4))
        Quotation.generate_number(date(2026, 5, 4))

        sequence = QuotationDailySequence.objects.get(sequence_date=date(2026, 5, 4))
        self.assertEqual(sequence.last_sequence, 2)
