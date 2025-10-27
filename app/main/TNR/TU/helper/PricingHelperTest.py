from django.test import TestCase, tag
from decimal import Decimal
from unittest.mock import patch
from main.application.helper.PricingHelper import PricingHelper


@tag('unitaire')
class PricingHelperTest(TestCase):
    """Tests pour PricingHelper - conversion HT->TTC et formatage prix"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.default_tva = Decimal('20.0')  # TVA par défaut 20%

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_int(self, mock_tva):
        """Test conversion HT->TTC avec un entier"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc(100)
        
        self.assertEqual(result, Decimal('120.00'))
        self.assertIsInstance(result, Decimal)

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_float(self, mock_tva):
        """Test conversion HT->TTC avec un float"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc(99.99)
        
        self.assertEqual(result, Decimal('119.99'))
        self.assertIsInstance(result, Decimal)

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_string_valid(self, mock_tva):
        """Test conversion HT->TTC avec une string valide"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc("50.50")
        
        self.assertEqual(result, Decimal('60.60'))
        self.assertIsInstance(result, Decimal)

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_string_invalid(self, mock_tva):
        """Test conversion HT->TTC avec une string invalide - ne doit pas crasher"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc("invalid_price")
        
        # Le helper retourne la valeur originale en cas d'erreur
        self.assertEqual(result, "invalid_price")

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_decimal(self, mock_tva):
        """Test conversion HT->TTC avec un Decimal"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc(Decimal('75.25'))
        
        self.assertEqual(result, Decimal('90.30'))
        self.assertIsInstance(result, Decimal)

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_none(self, mock_tva):
        """Test conversion HT->TTC avec None"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc(None)
        
        self.assertIsNone(result)

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_zero(self, mock_tva):
        """Test conversion HT->TTC avec zéro"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc(0)
        
        self.assertEqual(result, Decimal('0.00'))

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_rounding(self, mock_tva):
        """Test que l'arrondi se fait correctement (ROUND_HALF_UP)"""
        mock_tva.return_value = self.default_tva
        
        # 33.33 HT * 1.20 = 39.996 -> devrait arrondir à 40.00
        result = PricingHelper.ht_to_ttc(Decimal('33.33'))
        
        self.assertEqual(result, Decimal('40.00'))

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_with_custom_tva(self, mock_tva):
        """Test conversion avec un taux de TVA personnalisé"""
        custom_tva = Decimal('5.5')  # TVA réduite
        mock_tva.return_value = custom_tva
        
        result = PricingHelper.ht_to_ttc(100)
        
        self.assertEqual(result, Decimal('105.50'))

    @patch('main.application.helper.PricingHelper.PricingHelper.get_tva_rate')
    def test_ht_to_ttc_negative_price(self, mock_tva):
        """Test conversion avec prix négatif (remboursement)"""
        mock_tva.return_value = self.default_tva
        
        result = PricingHelper.ht_to_ttc(-50)
        
        self.assertEqual(result, Decimal('-60.00'))

    # Tests format_price_ttc

    @patch('main.application.helper.PricingHelper.PricingHelper.ht_to_ttc')
    @patch('main.application.helper.PricingHelper.PricingHelper.get_currency_symbol')
    def test_format_price_ttc_with_integer_price(self, mock_symbol, mock_ttc):
        """Test formatage prix entier sans décimales"""
        mock_symbol.return_value = '€'
        mock_ttc.return_value = Decimal('120.00')
        
        result = PricingHelper.format_price_ttc(100)
        
        self.assertEqual(result, "120€ TTC")

    @patch('main.application.helper.PricingHelper.PricingHelper.ht_to_ttc')
    @patch('main.application.helper.PricingHelper.PricingHelper.get_currency_symbol')
    def test_format_price_ttc_with_decimal_price(self, mock_symbol, mock_ttc):
        """Test formatage prix avec décimales"""
        mock_symbol.return_value = '€'
        mock_ttc.return_value = Decimal('119.99')
        
        result = PricingHelper.format_price_ttc(99.99)
        
        self.assertEqual(result, "119.99€ TTC")

    @patch('main.application.helper.PricingHelper.PricingHelper.ht_to_ttc')
    @patch('main.application.helper.PricingHelper.PricingHelper.get_currency_symbol')
    def test_format_price_ttc_with_none(self, mock_symbol, mock_ttc):
        """Test formatage avec None - devrait retourner 'Gratuit'"""
        mock_symbol.return_value = '€'
        
        result = PricingHelper.format_price_ttc(None)
        
        self.assertEqual(result, "Gratuit")
        mock_ttc.assert_not_called()  # Ne devrait pas appeler ht_to_ttc si None

    @patch('main.application.helper.PricingHelper.PricingHelper.ht_to_ttc')
    @patch('main.application.helper.PricingHelper.PricingHelper.get_currency_symbol')
    def test_format_price_ttc_when_conversion_returns_none(self, mock_symbol, mock_ttc):
        """Test formatage quand la conversion retourne None"""
        mock_symbol.return_value = '€'
        mock_ttc.return_value = None
        
        result = PricingHelper.format_price_ttc(100)
        
        self.assertEqual(result, "Gratuit")

    @patch('main.application.helper.PricingHelper.PricingHelper.ht_to_ttc')
    @patch('main.application.helper.PricingHelper.PricingHelper.get_currency_symbol')
    def test_format_price_ttc_with_custom_currency(self, mock_symbol, mock_ttc):
        """Test formatage avec devise personnalisée"""
        mock_symbol.return_value = '$'
        mock_ttc.return_value = Decimal('120.00')
        
        result = PricingHelper.format_price_ttc(100, currency='USD')
        
        self.assertEqual(result, "120$ TTC")

    @patch('main.application.helper.PricingHelper.PricingHelper.ht_to_ttc')
    def test_format_price_ttc_with_error_fallback(self, mock_ttc):
        """Test que le formatage ne crash pas en cas d'erreur"""
        mock_ttc.side_effect = ValueError("Erreur de conversion")
        
        result = PricingHelper.format_price_ttc("invalid")
        
        self.assertEqual(result, "invalid")

    @patch('main.application.helper.PricingHelper.PricingHelper.ht_to_ttc')
    @patch('main.application.helper.PricingHelper.PricingHelper.get_currency_symbol')
    def test_format_price_ttc_with_zero(self, mock_symbol, mock_ttc):
        """Test formatage avec prix 0"""
        mock_symbol.return_value = '€'
        mock_ttc.return_value = Decimal('0.00')
        
        result = PricingHelper.format_price_ttc(0)
        
        self.assertEqual(result, "0€ TTC")

    # Tests get_tva_rate

    @patch('main.application.helper.PricingHelper.Settings.get')
    def test_get_tva_rate_default(self, mock_settings):
        """Test récupération du taux de TVA par défaut"""
        mock_settings.return_value = 20.0
        
        result = PricingHelper.get_tva_rate()
        
        self.assertEqual(result, Decimal('20.0'))
        mock_settings.assert_called_once_with('APP_TVA', 20.0)

    @patch('main.application.helper.PricingHelper.Settings.get')
    def test_get_tva_rate_custom(self, mock_settings):
        """Test récupération d'un taux de TVA personnalisé"""
        mock_settings.return_value = 5.5
        
        result = PricingHelper.get_tva_rate()
        
        self.assertEqual(result, Decimal('5.5'))

    # Tests get_currency_symbol

    @patch('main.application.helper.PricingHelper.DeviseEnum.search')
    def test_get_currency_symbol_with_devise(self, mock_search):
        """Test récupération du symbole de devise spécifique"""
        mock_enum = type('MockEnum', (), {'value': '€'})
        mock_search.return_value = mock_enum
        
        result = PricingHelper.get_currency_symbol('EUR')
        
        self.assertEqual(result, '€')
        mock_search.assert_called_once_with('EUR')

    @patch('main.application.helper.PricingHelper.PricingHelper.get_default_currency')
    def test_get_currency_symbol_without_devise(self, mock_default):
        """Test récupération du symbole de devise par défaut"""
        mock_default.return_value = '€'
        
        result = PricingHelper.get_currency_symbol()
        
        self.assertEqual(result, '€')
        mock_default.assert_called_once()

    # Tests conversion

    def test_conversion_same_devise(self):
        """Test conversion entre même devise - pas de changement"""
        result = PricingHelper.conversion(Decimal('100.00'), 'EUR', 'EUR')
        
        self.assertEqual(result, Decimal('100.00'))

    def test_conversion_placeholder(self):
        """Test conversion entre devises différentes - placeholder pour future implémentation"""
        # Pour l'instant, la conversion retourne le même prix
        result = PricingHelper.conversion(Decimal('100.00'), 'EUR', 'USD')
        
        self.assertEqual(result, Decimal('100.00'))
        # TODO: Implémenter vraie conversion quand disponible
