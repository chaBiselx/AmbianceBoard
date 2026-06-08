from django import forms
from django.test import SimpleTestCase, tag

from main.interface.ui.forms.manager.ManagerEmailValidationUtils import ManagerEmailValidationUtils


@tag('unit')
class ManagerEmailValidationUtilsTest(SimpleTestCase):
    def test_parse_and_validate_external_emails_returns_empty_list_when_input_is_empty(self):
        self.assertEqual([], ManagerEmailValidationUtils.parse_and_validate_external_emails(''))
        self.assertEqual([], ManagerEmailValidationUtils.parse_and_validate_external_emails(None))

    def test_parse_and_validate_external_emails_parses_multiple_separators_and_deduplicates(self):
        raw = 'first@example.com; second@example.com\nThird@example.com\tfirst@example.com third@example.com'

        emails = ManagerEmailValidationUtils.parse_and_validate_external_emails(raw)

        self.assertEqual(
            ['first@example.com', 'second@example.com', 'Third@example.com'],
            emails,
        )

    def test_parse_and_validate_external_emails_raises_validation_error_for_invalid_email(self):
        with self.assertRaises(forms.ValidationError) as ctx:
            ManagerEmailValidationUtils.parse_and_validate_external_emails(
                'valid@example.com, invalid-email, another-invalid'
            )

        message = str(ctx.exception)
        self.assertIn('Adresse(s) email invalide(s)', message)
        self.assertIn('invalid-email', message)
        self.assertIn('another-invalid', message)
