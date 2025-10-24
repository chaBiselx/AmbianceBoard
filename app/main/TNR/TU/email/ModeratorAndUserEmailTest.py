from django.test import TestCase
from unittest.mock import patch, MagicMock
from main.domain.common.email.ModeratorEmail import ModeratorEmail
from main.domain.common.email.UserMail import UserMail
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.ReportContent import ReportContent


@patch('main.domain.common.email.ModeratorEmail.LoggerFactory.get_default_logger')
class ModeratorEmailTest(TestCase):
    """Tests pour ModeratorEmail - envoi d'emails aux modérateurs"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.from_email = "noreply@test.com"
        self.moderator_emails = ["mod1@test.com", "mod2@test.com"]

    @patch('main.domain.common.email.ModeratorEmail.Settings.get')
    def test_init_loads_settings(self, mock_settings, mock_logger):
        """Test que l'initialisation charge les settings correctement"""
        mock_settings.side_effect = lambda key: {
            'EMAIL_NO_REPLAY': self.from_email,
            'EMAILS_LISTING_MODERATORS': self.moderator_emails
        }.get(key)
        mock_logger.return_value = MagicMock()

        moderator_email = ModeratorEmail()

        self.assertEqual(moderator_email.from_email, self.from_email)
        self.assertEqual(moderator_email.to_emails, self.moderator_emails)

    @patch('main.domain.common.email.ModeratorEmail.EmailSender')
    @patch('main.domain.common.email.ModeratorEmail.render_to_string')
    @patch('main.domain.common.email.ModeratorEmail.Settings.get')
    def test_report_content_reported_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email de signalement avec succès"""
        mock_settings.side_effect = lambda key: {
            'EMAIL_NO_REPLAY': self.from_email,
            'EMAILS_LISTING_MODERATORS': self.moderator_emails
        }.get(key)
        mock_logger.return_value = MagicMock()
        
        mock_render.return_value = "<html>Report content</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer

        report = MagicMock(spec=ReportContent)
        moderator_email = ModeratorEmail()
        moderator_email.report_content_reported(report)

        mock_render.assert_called_once()
        mock_mailer.send_email.assert_called_once_with(
            'Contenu signalé',
            "<html>Report content</html>",
            self.from_email,
            self.moderator_emails
        )

    @patch('main.domain.common.email.ModeratorEmail.Settings.get')
    def test_report_content_no_moderator_email(self, mock_settings, mock_logger):
        """Test que l'envoi est ignoré si aucun email modérateur n'est configuré"""
        mock_settings.side_effect = lambda key: {
            'EMAIL_NO_REPLAY': self.from_email,
            'EMAILS_LISTING_MODERATORS': []  # Pas de modérateurs
        }.get(key)
        mock_logger.return_value = MagicMock()

        report = MagicMock(spec=ReportContent)
        moderator_email = ModeratorEmail()
        
        # Ne devrait pas lever d'exception
        moderator_email.report_content_reported(report)

    @patch('main.domain.common.email.ModeratorEmail.EmailSender')
    @patch('main.domain.common.email.ModeratorEmail.render_to_string')
    @patch('main.domain.common.email.ModeratorEmail.Settings.get')
    def test_report_content_email_send_exception(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test gestion d'erreur lors de l'envoi d'email de signalement"""
        mock_settings.side_effect = lambda key: {
            'EMAIL_NO_REPLAY': self.from_email,
            'EMAILS_LISTING_MODERATORS': self.moderator_emails
        }.get(key)
        mock_logger.return_value = MagicMock()
        
        mock_render.return_value = "<html>Report content</html>"
        mock_mailer = MagicMock()
        mock_mailer.send_email.side_effect = Exception("SMTP Error")
        mock_email_sender.return_value = mock_mailer

        report = MagicMock(spec=ReportContent)
        moderator_email = ModeratorEmail()
        
        # Ne devrait pas lever d'exception (gérée en interne avec log)
        moderator_email.report_content_reported(report)

    @patch('main.domain.common.email.ModeratorEmail.Settings.get')
    def test_has_moderator_email_true(self, mock_settings, mock_logger):
        """Test _has_moderator_email retourne True si configuré"""
        mock_settings.side_effect = lambda key: {
            'EMAIL_NO_REPLAY': self.from_email,
            'EMAILS_LISTING_MODERATORS': self.moderator_emails
        }.get(key)
        mock_logger.return_value = MagicMock()

        moderator_email = ModeratorEmail()
        
        self.assertTrue(moderator_email._has_moderator_email())

    @patch('main.domain.common.email.ModeratorEmail.Settings.get')
    def test_has_moderator_email_false_empty_list(self, mock_settings, mock_logger):
        """Test _has_moderator_email retourne False si liste vide"""
        mock_settings.side_effect = lambda key: {
            'EMAIL_NO_REPLAY': self.from_email,
            'EMAILS_LISTING_MODERATORS': []
        }.get(key)
        mock_logger.return_value = MagicMock()

        moderator_email = ModeratorEmail()
        
        self.assertFalse(moderator_email._has_moderator_email())

    @patch('main.domain.common.email.ModeratorEmail.Settings.get')
    def test_has_moderator_email_false_no_from_email(self, mock_settings, mock_logger):
        """Test _has_moderator_email retourne False si pas de from_email"""
        mock_settings.side_effect = lambda key: {
            'EMAIL_NO_REPLAY': None,
            'EMAILS_LISTING_MODERATORS': self.moderator_emails
        }.get(key)
        mock_logger.return_value = MagicMock()

        moderator_email = ModeratorEmail()
        
        self.assertFalse(moderator_email._has_moderator_email())


@patch('main.domain.common.email.UserMail.LoggerFactory.get_default_logger')
class UserMailTest(TestCase):
    """Tests pour UserMail - envoi d'emails aux utilisateurs"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.user = User(
            username="testuser",
            email="user@test.com",
            first_name="Test",
            last_name="User"
        )
        self.from_email = "noreply@test.com"

    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_init_loads_settings(self, mock_settings, mock_logger):
        """Test que l'initialisation charge les settings correctement"""
        mock_settings.return_value = self.from_email
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)

        self.assertEqual(user_mail.from_email, self.from_email)
        self.assertEqual(user_mail.user, self.user)

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_send_welcome_email_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email de bienvenue"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Welcome</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        user_mail.send_welcome_email()

        mock_render.assert_called_once()
        mock_mailer.send_email.assert_called_once_with(
            'Bienvenue sur notre site',
            "<html>Welcome</html>",
            self.from_email,
            [self.user.email]
        )

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_send_account_confirmation_email_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email de confirmation de compte"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Confirm</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        confirmation_url = "https://test.com/confirm/abc123"
        user_mail.send_account_confirmation_email(confirmation_url)

        mock_render.assert_called_once()
        args = mock_render.call_args
        self.assertIn('url', args[0][1])
        self.assertEqual(args[0][1]['url'], confirmation_url)
        
        mock_mailer.send_email.assert_called_once_with(
            'Confirmation de votre compte',
            "<html>Confirm</html>",
            self.from_email,
            [self.user.email]
        )

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_send_reset_password_email_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email de réinitialisation de mot de passe"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Reset</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        reset_url = "https://test.com/reset/xyz789"
        user_mail.send_reset_password_email(reset_url)

        mock_mailer.send_email.assert_called_once_with(
            'Reinitialisation de votre mot de passe',
            "<html>Reset</html>",
            self.from_email,
            [self.user.email]
        )

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_send_password_changed_email_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email de notification de changement de mot de passe"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Changed</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        user_mail.send_password_changed_email()

        mock_mailer.send_email.assert_called_once_with(
            'Modification de mot de passe',
            "<html>Changed</html>",
            self.from_email,
            [self.user.email]
        )

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_account_auto_deletion_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email de suppression automatique de compte"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Deleted</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        user_mail.account_auto_deletion()

        mock_mailer.send_email.assert_called_once_with(
            'Votre compte a été supprimé',
            "<html>Deleted</html>",
            self.from_email,
            [self.user.email]
        )

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_tiers_downgrade_notification_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email de notification de rétrogradation de tier"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Downgrade</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        user_mail.tiers_downgrade_notification("Free")

        args = mock_render.call_args
        self.assertIn('new_tier', args[0][1])
        self.assertEqual(args[0][1]['new_tier'], "Free")

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_tiers_expiration_warning_success(self, mock_settings, mock_render, mock_email_sender, mock_logger):
        """Test envoi d'email d'avertissement d'expiration de tier"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Warning</html>"
        mock_mailer = MagicMock()
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        user_mail.tiers_expiration_warning(7)

        args = mock_render.call_args
        self.assertIn('days_left', args[0][1])
        self.assertEqual(args[0][1]['days_left'], 7)

    @patch('main.domain.common.email.UserMail.EmailSender')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_send_email_exception_handling(self, mock_settings, mock_email_sender, mock_logger):
        """Test que les exceptions d'envoi sont gérées sans crash"""
        mock_settings.return_value = self.from_email
        mock_mailer = MagicMock()
        mock_mailer.send_email.side_effect = Exception("SMTP Error")
        mock_email_sender.return_value = mock_mailer
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        
        # Ne devrait pas lever d'exception (gérée en interne avec log)
        user_mail.send_welcome_email()

    @patch('main.domain.common.email.UserMail.render_to_string')
    @patch('main.domain.common.email.UserMail.Settings.get')
    def test_template_rendering_with_user_context(self, mock_settings, mock_render, mock_logger):
        """Test que le contexte utilisateur est passé au template"""
        mock_settings.return_value = self.from_email
        mock_render.return_value = "<html>Test</html>"
        mock_logger.return_value = MagicMock()

        user_mail = UserMail(self.user)
        user_mail.send_welcome_email()

        args = mock_render.call_args
        self.assertIn('user', args[0][1])
        self.assertEqual(args[0][1]['user'], self.user)
