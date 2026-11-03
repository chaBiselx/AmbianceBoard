from django.utils.translation import gettext, gettext_noop

from main.domain.common.enum.BaseEnum import BaseEnum


class FAQCategorieEnum(BaseEnum):
    PRESENTATION = gettext_noop('faq.category.presentation')
    MJ = gettext_noop('faq.category.game_master')
    COMPARAISON = gettext_noop('faq.category.comparison')
    DROITS = gettext_noop('faq.category.copyright')
    PARTICIPATION = gettext_noop('faq.category.participation')
    TECHNICAL = gettext_noop('faq.category.technical')
    OTHER = gettext_noop('faq.category.other')

    def trad(self) -> str:
        """Retourne la traduction de la catégorie FAQ dans la langue active."""
        return gettext(self.value)
