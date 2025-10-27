from django.test import TestCase, tag
from unittest.mock import patch, MagicMock, mock_open
from main.domain.common.utils.EmailSender import EmailSender
from main.domain.common.exceptions.EmailException import AttachementException, SendException
import smtplib


@tag('unitaire')
class EmailSenderTest(TestCase):
    """Tests pour EmailSender - envoi d'emails avec gestion SMTP"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.smtp_server = "smtp.test.com"
        self.smtp_port = 587
        self.username = "test@test.com"
        self.password = "password123"
        self.use_tls = True

    def test_init_with_custom_params(self):
        """Test initialisation avec paramètres personnalisés"""
        sender = EmailSender(
            smtp_server="custom.smtp.com",
            smtp_port=465,
            username="custom@test.com",
            password="custompass",
            use_tls=False
        )

        self.assertEqual(sender.smtp_server, "custom.smtp.com")
        self.assertEqual(sender.smtp_port, 465)
        self.assertEqual(sender.username, "custom@test.com")
        self.assertEqual(sender.password, "custompass")
        self.assertFalse(sender.use_tls)

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_html_success(self, mock_smtp_class):
        """Test envoi d'email HTML avec succès"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        result = sender.send_email(
            subject="Test Subject",
            body="<h1>Test HTML Body</h1>",
            from_email="sender@test.com",
            to_emails=["recipient@test.com"],
            is_html=True
        )

        self.assertTrue(result)
        mock_smtp_class.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(self.username, self.password)
        mock_server.send_message.assert_called_once()

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_plain_text(self, mock_smtp_class):
        """Test envoi d'email en texte brut"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        result = sender.send_email(
            subject="Plain Text Test",
            body="This is plain text",
            from_email="sender@test.com",
            to_emails=["recipient@test.com"],
            is_html=False
        )

        self.assertTrue(result)
        mock_server.send_message.assert_called_once()

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_without_tls(self, mock_smtp_class):
        """Test envoi d'email sans TLS"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=False
        )

        result = sender.send_email(
            subject="Test",
            body="Test body",
            from_email="sender@test.com",
            to_emails=["recipient@test.com"]
        )

        self.assertTrue(result)
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_called_once()

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_without_authentication(self, mock_smtp_class):
        """Test envoi d'email sans authentification (username/password None)"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=None,
            password=None,
            use_tls=False
        )

        result = sender.send_email(
            subject="Test",
            body="Test body",
            from_email="sender@test.com",
            to_emails=["recipient@test.com"]
        )

        self.assertTrue(result)
        mock_server.login.assert_not_called()  # Pas de login si pas d'identifiants

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_multiple_recipients(self, mock_smtp_class):
        """Test envoi d'email à plusieurs destinataires"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        recipients = ["user1@test.com", "user2@test.com", "user3@test.com"]
        result = sender.send_email(
            subject="Test",
            body="Test body",
            from_email="sender@test.com",
            to_emails=recipients
        )

        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open, read_data=b'file content')
    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_with_attachment_success(self, mock_smtp_class, mock_file):
        """Test envoi d'email avec pièce jointe réussie"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        result = sender.send_email(
            subject="Test with attachment",
            body="Email with file",
            from_email="sender@test.com",
            to_emails=["recipient@test.com"],
            attachments=["/path/to/file.pdf"]
        )

        self.assertTrue(result)
        mock_file.assert_called_once_with("/path/to/file.pdf", 'rb')

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_send_email_with_attachment_failure(self, mock_file):
        """Test envoi d'email avec pièce jointe inexistante - doit lever AttachementException"""
        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        with self.assertRaises(AttachementException) as context:
            sender.send_email(
                subject="Test",
                body="Test body",
                from_email="sender@test.com",
                to_emails=["recipient@test.com"],
                attachments=["/nonexistent/file.pdf"]
            )

        self.assertIn("File not found", str(context.exception))

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_smtp_connection_error(self, mock_smtp_class):
        """Test gestion erreur de connexion SMTP"""
        mock_smtp_class.side_effect = smtplib.SMTPConnectError(421, "Cannot connect")

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        with self.assertRaises(SendException) as context:
            sender.send_email(
                subject="Test",
                body="Test body",
                from_email="sender@test.com",
                to_emails=["recipient@test.com"]
            )

        self.assertIn("Cannot connect", str(context.exception))

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_smtp_authentication_error(self, mock_smtp_class):
        """Test gestion erreur d'authentification SMTP"""
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        with self.assertRaises(SendException):
            sender.send_email(
                subject="Test",
                body="Test body",
                from_email="sender@test.com",
                to_emails=["recipient@test.com"]
            )

    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_smtp_send_error(self, mock_smtp_class):
        """Test gestion erreur lors de l'envoi du message"""
        mock_server = MagicMock()
        mock_server.send_message.side_effect = smtplib.SMTPException("Send failed")
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        with self.assertRaises(SendException) as context:
            sender.send_email(
                subject="Test",
                body="Test body",
                from_email="sender@test.com",
                to_emails=["recipient@test.com"]
            )

        self.assertIn("Send failed", str(context.exception))

    @patch('builtins.open', new_callable=mock_open, read_data=b'file1 content')
    @patch('main.domain.common.utils.EmailSender.smtplib.SMTP')
    def test_send_email_with_multiple_attachments(self, mock_smtp_class, mock_file):
        """Test envoi d'email avec plusieurs pièces jointes"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )

        attachments = ["/path/to/file1.pdf", "/path/to/file2.doc"]
        result = sender.send_email(
            subject="Test with attachments",
            body="Email with files",
            from_email="sender@test.com",
            to_emails=["recipient@test.com"],
            attachments=attachments
        )

        self.assertTrue(result)
        self.assertEqual(mock_file.call_count, 2)
