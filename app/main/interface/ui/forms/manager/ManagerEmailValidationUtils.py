from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email


class ManagerEmailValidationUtils:
    @staticmethod
    def parse_and_validate_external_emails(external_emails_raw: str) -> list[str]:
        emails = ManagerEmailValidationUtils._parse_external_emails(external_emails_raw)
        ManagerEmailValidationUtils._raise_if_invalid_emails(emails)
        return emails

    @staticmethod
    def _parse_external_emails(external_emails_raw: str) -> list[str]:
        if not external_emails_raw:
            return []

        normalized = external_emails_raw
        for separator in [',', ';', '\n', '\t']:
            normalized = normalized.replace(separator, ' ')

        emails: list[str] = []
        seen: set[str] = set()
        for candidate in normalized.split(' '):
            email = candidate.strip()
            if not email:
                continue
            lowered_email = email.lower()
            if lowered_email in seen:
                continue
            seen.add(lowered_email)
            emails.append(email)

        return emails

    @staticmethod
    def _raise_if_invalid_emails(emails: list[str]) -> None:
        invalid_emails: list[str] = []
        for email in emails:
            try:
                validate_email(email)
            except DjangoValidationError:
                invalid_emails.append(email)

        if invalid_emails:
            raise forms.ValidationError(
                f"Adresse(s) email invalide(s) : {', '.join(invalid_emails)}"
            )
