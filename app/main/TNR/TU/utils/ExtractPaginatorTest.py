from django.test import TestCase
from django.core.paginator import Paginator
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator

class ExtractPaginatorTest(TestCase):
    def setUp(self):
        """Initialisation des données de test"""
        # Créer une liste de 100 éléments pour les tests
        self.test_data = list(range(100))
        self.items_per_page = 10
        self.paginator = Paginator(self.test_data, self.items_per_page)

    def test_first_page(self):
        """Test le contexte pour la première page"""
        context = extract_context_to_paginator(self.paginator, 1)
        
        self.assertEqual(context['paginator']['page_number'], 1)
        self.assertTrue(context['paginator']['is_first_page'])
        self.assertFalse(context['paginator']['is_last_page'])
        self.assertEqual(context['paginator']['previous_page_number'], '0')
        self.assertEqual(context['paginator']['next_page_number'], '2')
        
        # Vérifier le page_range pour la première page
        expected_range = [1, 2, 3, 4, 5, 10]  # 1-4 (groupe), 5 et 10 (step)
        self.assertEqual(sorted(context['paginator']['page_range']), expected_range)

    def test_middle_page(self):
        """Test le contexte pour une page au milieu"""
        context = extract_context_to_paginator(self.paginator, 5)
        
        self.assertEqual(context['paginator']['page_number'], 5)
        self.assertFalse(context['paginator']['is_first_page'])
        self.assertFalse(context['paginator']['is_last_page'])
        self.assertEqual(context['paginator']['previous_page_number'], '4')
        self.assertEqual(context['paginator']['next_page_number'], '6')
        
        # Vérifier le page_range pour une page du milieu
        expected_range = [2, 3, 4, 5, 6, 7, 8, 10]  # 2-8 (groupe), 5, 10 (step)
        self.assertEqual(sorted(context['paginator']['page_range']), expected_range)

    def test_last_page(self):
        """Test le contexte pour la dernière page"""
        last_page = self.paginator.num_pages
        context = extract_context_to_paginator(self.paginator, last_page)
        
        self.assertEqual(context['paginator']['page_number'], last_page)
        self.assertFalse(context['paginator']['is_first_page'])
        self.assertTrue(context['paginator']['is_last_page'])
        self.assertEqual(context['paginator']['previous_page_number'], str(last_page - 1))
        self.assertEqual(context['paginator']['next_page_number'], str(last_page + 1))
        
        # Vérifier le page_range pour la dernière page
        expected_range = [5, 7, 8, 9, 10]  # 7-10 (groupe),  5, 10 (step)
        self.assertEqual(sorted(context['paginator']['page_range']), expected_range)

    def test_invalid_page(self):
        """Test le contexte avec un numéro de page invalide"""
        # Test avec une page négative
        context = extract_context_to_paginator(self.paginator, -1)
        self.assertEqual(context['paginator']['page_number'], 1)  # Devrait retourner la première page
        
        # Test avec une page trop grande
        context = extract_context_to_paginator(self.paginator, 999)
        self.assertEqual(context['paginator']['page_number'], self.paginator.num_pages)  # Devrait retourner la dernière page

    def test_small_dataset(self):
        """Test avec un petit ensemble de données"""
        small_data = list(range(3))
        paginator = Paginator(small_data, 2)
        context = extract_context_to_paginator(paginator, 1)
        
        self.assertEqual(context['paginator']['page_number'], 1)
        self.assertTrue(context['paginator']['is_first_page'])
        
        # Vérifier le page_range pour un petit dataset
        expected_range = [1, 2]  # Seulement 2 pages
        self.assertEqual(sorted(context['paginator']['page_range']), expected_range)

    def test_page_objects_content(self):
        """Test le contenu des objets de la page"""
        context = extract_context_to_paginator(self.paginator, 2)
        page_objects = context['page_objects']
        
        # Vérifier que nous avons le bon nombre d'objets
        self.assertEqual(len(list(page_objects)), self.items_per_page)
        
        # Vérifier que nous avons les bons objets
        expected_objects = list(range(10, 20))  # Page 2 devrait avoir les éléments 10-19
        self.assertEqual(list(page_objects), expected_objects)

    def test_single_page(self):
        """Test avec un dataset qui tient sur une seule page"""
        single_page_data = list(range(5))
        paginator = Paginator(single_page_data, 10)  # Plus grand que le dataset
        context = extract_context_to_paginator(paginator, 1)
        
        self.assertTrue(context['paginator']['is_first_page'])
        self.assertTrue(context['paginator']['is_last_page'])
        self.assertEqual(context['paginator']['page_range'], [1])