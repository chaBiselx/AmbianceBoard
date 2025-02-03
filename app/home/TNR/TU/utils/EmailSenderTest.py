import unittest
from unittest.mock import patch, mock_open, MagicMock
from email.message import EmailMessage
import smtplib
from parameters import settings
from home.exceptions.EmailException import DebugModeActivedWitoutDebugMailException, AttachementException, SendException
from home.utils.EmailSender import EmailSender

class TestEmailSender(unittest.TestCase):
    def setUp(self):
        """Configure les paramètres de base pour les tests"""
        self.smtp_server = "smtp.example.com"
        self.smtp_port = 587
        self.username = "test@example.com"
        self.password = "password123"
        self.use_tls = True  # Nouveau champ
        
    def test_init_normal_mode(self):
        """Test l'initialisation en mode normal"""
        with patch('parameters.settings.DEBUG', False):
            sender = EmailSender(
                self.smtp_server,
                self.smtp_port,
                self.username,
                self.password
            )
            self.assertEqual(sender.smtp_server, self.smtp_server)
            self.assertEqual(sender.smtp_port, self.smtp_port)
            self.assertEqual(sender.username, self.username)
            self.assertEqual(sender.password, self.password)
            self.assertFalse(sender.debug_mode)
            self.assertIsNone(sender.debug_email)
            
    def test_init_normal_mode_with_tls(self):
        """Test l'initialisation en mode normal"""
        with patch('parameters.settings.DEBUG', False):
            sender = EmailSender(
                self.smtp_server,
                self.smtp_port,
                self.username,
                self.password,
                False
            )
            self.assertEqual(sender.smtp_server, self.smtp_server)
            self.assertEqual(sender.smtp_port, self.smtp_port)
            self.assertEqual(sender.username, self.username)
            self.assertEqual(sender.password, self.password)
            self.assertFalse(sender.debug_mode)
            self.assertIsNone(sender.debug_email)

    def test_init_debug_mode(self):
        """Test l'initialisation en mode debug avec email de debug"""
        debug_email = "debug@example.com"
        with patch('parameters.settings.DEBUG', True), \
             patch('parameters.settings.EMAIL_DEBUG', debug_email):
            sender = EmailSender(
                self.smtp_server,
                self.smtp_port,
                self.username,
                self.password
            )
            self.assertTrue(sender.debug_mode)
            self.assertEqual(sender.debug_email, debug_email)

    def test_init_debug_mode_without_email(self):
        """Test l'initialisation en mode debug sans email de debug"""
        with patch('parameters.settings.DEBUG', True), \
             patch('parameters.settings.EMAIL_DEBUG', None):
            sender = EmailSender(
                self.smtp_server,
                self.smtp_port,
                self.username,
                self.password
            )
            self.assertTrue(sender.debug_mode)
            self.assertIsNone(sender.debug_email)

    @patch('smtplib.SMTP')
    def test_send_email_basic(self, mock_smtp):
        """Test l'envoi d'un email basique sans pièce jointe"""
        with patch('parameters.settings.DEBUG', False):
            sender = EmailSender(self.smtp_server, self.smtp_port, self.username, self.password)
            
            # Configure le mock SMTP
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Paramètres de l'email
            subject = "Test Subject"
            body = "Test Body"
            from_email = "sender@example.com"
            to_emails = ["recipient@example.com"]
            
            # Envoie l'email
            result = sender.send_email(subject, body, from_email, to_emails)
            
            # Vérifie que les méthodes SMTP ont été appelées correctement
            self.assertTrue(result)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with(self.username, self.password)
            mock_server.send_message.assert_called_once()
            
            # Vérifie le contenu de l'email
            sent_msg = mock_server.send_message.call_args[0][0]
            self.assertEqual(sent_msg['Subject'], subject)
            self.assertEqual(sent_msg['From'], from_email)
            self.assertEqual(sent_msg['To'], 'recipient@example.com')  # email.message.EmailMessage convertit automatiquement la liste en string

    @patch('smtplib.SMTP')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test file content')
    def test_send_email_with_attachment(self, mock_file, mock_smtp):
        """Test l'envoi d'un email avec pièce jointe"""
        with patch('parameters.settings.DEBUG', False):
            sender = EmailSender(self.smtp_server, self.smtp_port, self.username, self.password)
            
            # Configure le mock SMTP
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Paramètres de l'email
            subject = "Test Subject"
            body = "Test Body"
            from_email = "sender@example.com"
            to_emails = ["recipient@example.com"]
            attachments = ["/path/to/file.txt"]
            
            # Envoie l'email
            result = sender.send_email(subject, body, from_email, to_emails, attachments)
            
            # Vérifie que le fichier a été ouvert et lu
            mock_file.assert_called_once_with("/path/to/file.txt", "rb")
            self.assertTrue(result)
            
            # Vérifie que l'email a été envoyé avec la pièce jointe
            sent_msg = mock_server.send_message.call_args[0][0]
            self.assertEqual(sent_msg['To'], 'recipient@example.com')
            self.assertEqual(len(sent_msg.get_payload()), 2)  # Corps + pièce jointe

    def test_send_email_debug_mode_without_debug_email(self):
        """Test l'envoi d'un email en mode debug sans adresse de debug configurée"""
        with patch('parameters.settings.DEBUG', True), \
             patch('parameters.settings.EMAIL_DEBUG', None):
            
            sender = EmailSender(self.smtp_server, self.smtp_port, self.username, self.password)
            
            with self.assertRaises(DebugModeActivedWitoutDebugMailException):
                sender.send_email(
                    "Test Subject",
                    "Test Body",
                    "sender@example.com",
                    ["recipient@example.com"]
                )

    @patch('smtplib.SMTP')
    def test_send_email_debug_mode_with_debug_email(self, mock_smtp):
        """Test l'envoi d'un email en mode debug avec adresse de debug"""
        debug_email = "debug@example.com"
        with patch('parameters.settings.DEBUG', True), \
             patch('parameters.settings.EMAIL_DEBUG', debug_email):
            
            sender = EmailSender(self.smtp_server, self.smtp_port, self.username, self.password)
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            subject = "Test Subject"
            body = "Test Body"
            from_email = "sender@example.com"
            to_emails = ["recipient1@example.com", "recipient2@example.com"]
            
            result = sender.send_email(subject, body, from_email, to_emails)
            
            self.assertTrue(result)
            sent_msg = mock_server.send_message.call_args[0][0]
            self.assertEqual(sent_msg['To'], debug_email)

    @patch('builtins.open')
    def test_attachment_error(self, mock_open):
        """Test la gestion des erreurs de pièces jointes"""
        with patch('parameters.settings.DEBUG', False):
            sender = EmailSender(self.smtp_server, self.smtp_port, self.username, self.password)
            
            # Simule une erreur lors de l'ouverture du fichier
            mock_open.side_effect = FileNotFoundError("File not found")
            
            with self.assertRaises(AttachementException):
                sender.send_email(
                    "Test Subject",
                    "Test Body",
                    "sender@example.com",
                    ["recipient@example.com"],
                    ["/path/to/nonexistent.txt"]
                )

    @patch('smtplib.SMTP')
    def test_smtp_error(self, mock_smtp):
        """Test la gestion des erreurs SMTP"""
        with patch('parameters.settings.DEBUG', False):
            sender = EmailSender(self.smtp_server, self.smtp_port, self.username, self.password)
            
            # Configure le mock pour lever une exception SMTP
            mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException("SMTP error")
            
            with self.assertRaises(SendException):
                sender.send_email(
                    "Test Subject",
                    "Test Body",
                    "sender@example.com",
                    ["recipient@example.com"]
                )
