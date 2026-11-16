from django.test import SimpleTestCase, tag
from django.utils.translation import override

from main.domain.general.service.FAQService import FAQService


@tag('unitaire')
class FAQServiceTest(SimpleTestCase):
    def test_get_faqs_returns_explicit_french_content(self):
        service = FAQService()

        with override('en'):
            faqs = service.get_faqs('fr')

        self.assertEqual(
            [group['theme'] for group in faqs],
            [
                'Présentation & tarifs',
                'Maître du Jeu & immersion',
                'Comparaisons & alternatives',
                'Droits et licence',
                'Participation',
                'Technique',
                'Autres questions',
            ],
        )
        self.assertEqual(faqs[0]['items'][0]['question'], 'Est-ce que c\'est vraiment gratuit ?')
        self.assertTrue(all(group['items'] for group in faqs))

    def test_get_faqs_returns_explicit_english_content(self):
        service = FAQService()

        with override('fr'):
            faqs = service.get_faqs('en')

        self.assertEqual(
            [group['theme'] for group in faqs],
            [
                'About & pricing',
                'Game mastering & immersion',
                'Comparisons & alternatives',
                'Copyright & licensing',
                'Contributing',
                'Technical',
                'Other questions',
            ],
        )
        self.assertEqual(faqs[0]['items'][0]['question'], 'Is it really free?')
        self.assertIn('completely free', faqs[0]['items'][0]['answer'])
        self.assertTrue(all(group['items'] for group in faqs))

    def test_each_faq_has_french_and_english_question_and_answer(self):
        for item in FAQService.HOME_FAQ:
            with self.subTest(label=item['label']):
                for field in ('question_fr', 'question_en', 'answer_fr', 'answer_en'):
                    self.assertTrue(item[field])
