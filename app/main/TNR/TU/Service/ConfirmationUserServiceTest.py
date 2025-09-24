# app/main/service/tests/test_ConfirmationUserService.py

import unittest
from unittest.mock import Mock, patch
from django.test import TestCase
from main.architecture.persistence.models.User import User
from main.domain.common.service.ConfirmationUserService import ConfirmationUserService
from main.domain.common.exceptions.SecurityException import SecurityException
from django.utils import timezone
from datetime import datetime, timedelta


class ConfirmationUserServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword') # NOSONAR
        self.confirmation_service = ConfirmationUserService(self.user)

    def test_generation_uri(self):
        uri = self.confirmation_service.generation_uri()
        self.assertIsNotNone(uri)
        self.assertIn('/confirm/', uri)
        self.assertIn(str(self.user.uuid), uri)
        self.assertIn(str(self.user.get_confirmation_token()), uri)
        
    def test_generation_uri_user_already_confirmed(self):
        self.user.isConfirmed = True
        self.user.save()
        
        with self.assertRaises(SecurityException):
            self.confirmation_service.generation_uri()

    def test_verification_token_success(self):
        confirmation_token = self.confirmation_service.generation_uri().split('/')[-1]
        self.assertIsNotNone(confirmation_token)
        self.assertEqual(confirmation_token, self.user.get_confirmation_token())
        self.assertTrue(self.confirmation_service.verification_token(confirmation_token))
        self.assertTrue(self.user.isConfirmed)
        self.assertIsNone(self.user.get_confirmation_token())  
        self.assertIsNotNone(self.user.demandeConfirmationDate)
        
    def test_update_confirmation_token(self):
        base_timezone = timezone.now() - timedelta(days=5)
        self.user.demandeConfirmationDate = base_timezone
        self.user.confirmationToken = 'test_token'
        self.user.save()
        confirmation_token = self.confirmation_service.generation_uri().split('/')[-1]
        self.assertIsNotNone(confirmation_token)
        self.assertNotEqual(confirmation_token, 'test_token')
        self.assertFalse(base_timezone == self.user.demandeConfirmationDate)
    
    def test_update_confirmation_token_witout_modification_date(self):
        base_timezone = timezone.now() - timedelta(days=5)
        self.user.demandeConfirmationDate = base_timezone
        self.user.confirmationToken = 'test_token'
        self.user.save()
        confirmation_token = self.confirmation_service.generation_uri(False).split('/')[-1]
        self.assertIsNotNone(confirmation_token)
        self.assertNotEqual(confirmation_token, 'test_token')
        self.assertTrue(base_timezone == self.user.demandeConfirmationDate)
        
        
    def test_verification_token_failure_user_not_found(self):
        self.confirmation_service.user = None
        with self.assertRaises(SecurityException):
            self.confirmation_service.verification_token('user_not_found')

    def test_verification_token_failure_confirmation_token_not_found(self):
        self.confirmation_service.user.confirmationToken = None
        with self.assertRaises(SecurityException):
            self.confirmation_service.verification_token('empty_token')
            
    def test_verification_token_failure_confirmation_demande_confirmation_date_not_found(self):
        self.confirmation_service.user.demandeConfirmationDate = None
        self.confirmation_service.user.confirmationToken = 'token_valid'
        with self.assertRaises(SecurityException):
            self.confirmation_service.verification_token('token_valid')
            
    def test_verification_token_failure_confirmation_demande_confirmation_date_expired(self):
        self.confirmation_service.user.demandeConfirmationDate = timezone.now() - timedelta(days=2)
        self.confirmation_service.user.confirmationToken = 'token_valid'
        with self.assertRaises(SecurityException):
            self.confirmation_service.verification_token('token_valid')

    def test_verification_token_failure_token_mismatch(self):
        self.confirmation_service.generation_uri()
        with self.assertRaises(SecurityException):
            self.confirmation_service.verification_token('invalid_token')

    @patch('main.domain.common.service.ConfirmationUserService.reverse')
    def test_generation_uri_reverse_called(self, mock_reverse):
        self.confirmation_service.generation_uri()
        mock_reverse.assert_called_once_with('confirm_account', kwargs={'uuid_user': self.user.uuid, 'confirmation_token': self.user.confirmationToken})

if __name__ == '__main__':
    unittest.main()