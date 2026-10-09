from time import time

from django.core.signing import BadSignature, TimestampSigner


class TimestampToken:
	SUPPORT_CONTACT_TOKEN_SALT = 'support-contact-form'
	SUPPORT_CONTACT_MIN_FILL_SECONDS = 5
	SUPPORT_CONTACT_MAX_AGE_SECONDS = 60 * 60

	@classmethod
	def create_support_form_token(cls):
		return TimestampSigner(salt=cls.SUPPORT_CONTACT_TOKEN_SALT).sign(
			str(int(time()))
		)

	@classmethod
	def is_support_form_token_valid(cls, token):
		if not token:
			return False

		try:
			started_at = int(TimestampSigner(
				salt=cls.SUPPORT_CONTACT_TOKEN_SALT
			).unsign(token, max_age=cls.SUPPORT_CONTACT_MAX_AGE_SECONDS))
		except (BadSignature, TypeError, ValueError):
			return False

		elapsed_seconds = time() - started_at
		return (
			cls.SUPPORT_CONTACT_MIN_FILL_SECONDS
			<= elapsed_seconds
			<= cls.SUPPORT_CONTACT_MAX_AGE_SECONDS
		)
