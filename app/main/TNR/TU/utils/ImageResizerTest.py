from django.test import TestCase
import unittest
from unittest.mock import mock_open, patch, MagicMock
import os
from PIL import Image
from main.domain.common.utils.ImageResizer import ImageResizer  # Assurez-vous que le fichier s'appelle image_resizer.py

os_path_exist = 'os.path.exists'
class ImageResizerTest(unittest.TestCase):
    def setUp(self):
        self.input_path = "test_input.jpg"
        self.output_path = "test_output.jpg"
        
    def test_init_with_existing_file(self):
        """Test l'initialisation avec un fichier qui existe"""
        with patch(os_path_exist) as mock_exists:
            mock_exists.return_value = True
            resizer = ImageResizer(self.input_path, self.output_path)
            self.assertEqual(resizer.input_path, self.input_path)
            self.assertEqual(resizer.output_path, self.output_path)

    def test_init_with_nonexistent_file(self):
        """Test l'initialisation avec un fichier qui n'existe pas"""
        with patch(os_path_exist) as mock_exists:
            mock_exists.return_value = False
            with self.assertRaises(FileNotFoundError):
                ImageResizer(self.input_path, self.output_path)

    @patch('PIL.Image.open')
    def test_resize_image_smaller(self, mock_image_open):
        """Test le redimensionnement d'une image plus grande que max_size"""
        # Créer une mock image
        mock_img = MagicMock()
        mock_img.width = 400
        mock_img.height = 300
        mock_img.__enter__.return_value = mock_img
        mock_image_open.return_value = mock_img

        with patch(os_path_exist) as mock_exists:
            mock_exists.return_value = True
            resizer = ImageResizer(self.input_path, self.output_path)
            resizer.resize_image(max_size=200)

            # Vérifier que resize a été appelé avec les bonnes dimensions
            mock_img.resize.assert_called_once()
            args = mock_img.resize.call_args[0]
            self.assertEqual(args[0], (200, 150))  # Les nouvelles dimensions attendues

    @patch('PIL.Image.open')
    def test_resize_image_already_small(self, mock_image_open):
        """Test avec une image déjà plus petite que max_size"""
        # Créer une mock image
        mock_img = MagicMock()
        mock_img.width = 100
        mock_img.height = 75
        mock_img.__enter__.return_value = mock_img
        mock_image_open.return_value = mock_img

        with patch(os_path_exist) as mock_exists:
            mock_exists.return_value = True
            resizer = ImageResizer(self.input_path, self.output_path)
            resizer.resize_image(max_size=200)

            # Vérifier que resize n'a pas été appelé
            mock_img.resize.assert_not_called()

    @patch('PIL.Image.open')
    def test_resize_image_error_handling(self, mock_image_open):
        """Test la gestion des erreurs lors du redimensionnement"""
        mock_image_open.side_effect = Exception("Test error")

        with patch(os_path_exist) as mock_exists:
            mock_exists.return_value = True
            resizer = ImageResizer(self.input_path, self.output_path)

            ret = resizer.resize_image()
            self.assertFalse(ret)