from itertools import groupby
from main.domain.general.enum.FAQCategorieEnum import FAQCategorieEnum

class FAQService:
    """
    Service class for handling FAQ-related operations.
    """
    HOME_FAQ = [
        # ── Présentation & tarifs ────────────────────────────────────────────
        {
            'theme': FAQCategorieEnum.PRESENTATION.value,
            'question': 'Quel est le meilleur soundboard gratuit pour JDR ?',
            'answer': (
                'AmbianceBoard est un soundboard en ligne gratuit conçu spécifiquement pour les maîtres du jeu. '
                'Il permet de déclencher des ambiances sonores, des effets instantanés et des playlists musicales '
                'en un clic, sans aucune installation ni abonnement.'
            ),
        },
        {
            'theme': FAQCategorieEnum.PRESENTATION.value,
            'question': 'Existe-t-il un outil en ligne pour maître du jeu accessible gratuitement ?',
            'answer': (
                'AmbianceBoard est un outil web 100 % gratuit pour les maîtres du jeu. '
                'Aucune installation n\'est requise : ouvrez le site, créez un soundboard et commencez à jouer. '
                'Un compte gratuit permet de sauvegarder vos boards, de les partager avec vos joueurs '
                'et d\'accéder aux soundboards publics de la communauté.'
            ),
        },
        # ── Maître du Jeu & immersion ────────────────────────────────────────
        {
            'theme': FAQCategorieEnum.MJ.value,
            'question': 'Quels outils sont indispensables pour un Maître du Jeu (MJ) ?',
            'answer': (
                'Pour orchestrer une partie de JDR immersive, un MJ a besoin d\'un soundboard audio pour l\'ambiance, '
                'd\'un outil de partage en temps réel pour les joueurs distants, et d\'une bibliothèque sonore organisée. '
                'AmbianceBoard réunit ces trois besoins dans une seule interface web gratuite.'
            ),
        },
        {
            'theme': FAQCategorieEnum.MJ.value,
            'question': 'Comment créer une ambiance sonore pour une partie de JDR ?',
            'answer': (
                'Créez un soundboard sur AmbianceBoard, ajoutez des playlists par type de scène (taverne, combat, exploration), '
                'puis déclenchez-les d\'un clic pendant la partie. Vous pouvez partager un lien avec vos joueurs pour qu\'ils '
                'entendent la même ambiance en temps réel, que ce soit en présentiel ou en ligne.'
            ),
        },
        {
            'theme': FAQCategorieEnum.MJ.value,
            'question': 'Comment améliorer l\'immersion dans une partie de jeu de rôle ?',
            'answer': (
                'L\'immersion en JDR repose sur trois piliers : le visuel, la narration et le son. '
                'Un soundboard comme AmbianceBoard permet d\'ajouter la couche sonore sans interrompre le jeu : '
                'ambiances en boucle, effets ponctuels et musiques de scène déclenchés au bon moment renforcent '
                'l\'atmosphère et l\'engagement des joueurs.'
            ),
        },
        # ── Comparaisons & alternatives ──────────────────────────────────────
        {
            'theme': FAQCategorieEnum.COMPARAISON.value,
            'question': 'AmbianceBoard est-il une alternative à Syrinscape ?',
            'answer': (
                'Oui. AmbianceBoard est une alternative open source et gratuite à Syrinscape. '
                'Là où Syrinscape propose des packs sonores payants, AmbianceBoard vous laisse importer '
                'vos propres sons, utiliser des liens externes ou des radios en streaming. '
                'La synchronisation en temps réel avec vos joueurs est incluse sans abonnement.'
            ),
        },
    ]

    def get_faqs(self):
        """
        Retrieve all FAQs from the database.

        Returns:
            list: A list of FAQ objects.
        """
        return [
            {'theme': theme, 'items': list(items)}
            for theme, items in groupby(self.HOME_FAQ, key=lambda x: x['theme'])
        ]