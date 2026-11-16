from django.test import SimpleTestCase, tag
from django.utils.translation import override

from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum


@tag('unitaire')
class ErrorMessageEnumTest(SimpleTestCase):
    def test_all_messages_are_translated_in_french_and_english(self):
        expected = {
            ErrorMessageEnum.METHOD_NOT_SUPPORTED: (
                'error.method_not_supported',
                'Méthode non prise en charge.',
                'Method not supported.',
            ),
        }

        with override('fr'):
            for message, (key, french, _) in expected.items():
                with self.subTest(message=message.name, language='fr'):
                    self.assertEqual(message.value, key)
                    self.assertEqual(message.trad(), french)

        with override('en'):
            for message, (key, _, english) in expected.items():
                with self.subTest(message=message.name, language='en'):
                    self.assertEqual(message.value, key)
                    self.assertEqual(message.trad(), english)
