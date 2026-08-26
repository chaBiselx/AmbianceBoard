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
            'question': 'Est-ce que c\'est vraiment gratuit ?',
            'answer': (
                'Oui, AmbianceBoard est entièrement gratuit et ça le restera. '
                'Le JDR coûte déjà assez cher, je ne veux pas ajouter de frais supplémentaires pour les maîtres du jeu. '
                'Vous pouvez créer des soundboards, les partager et les utiliser sans aucun coût. '
                'Un compte gratuit vous permet de sauvegarder vos soundboards et de partager l\'écoute avec vos joueurs.'
            ),
        },
        {
            'theme': FAQCategorieEnum.PRESENTATION.value,
            'question': 'Qu\'est-ce qu\'AmbianceBoard ?',
            'answer': (
                'AmbianceBoard est un soundboard en ligne gratuit conçu spécifiquement pour les maîtres du jeu. '
                'Il permet de déclencher des ambiances sonores, des effets instantanés et des playlists musicales '
                'en un clic, sans aucune installation ni abonnement.'
            ),
        },
        {
            'theme': FAQCategorieEnum.PRESENTATION.value,
            'question': 'Comment ça marche ?',
            'answer': (
                'AmbianceBoard fonctionne directement dans votre navigateur web. '
                'Il suffit de créer un soundboard, d\'ajouter vos sons, de les organiser et de commencer à jouer.'
                'Il est possible d\'utiliser des sons de la communauté ou d\'importer vos propres sons. '
            ),
        },
        {
            'theme': FAQCategorieEnum.PRESENTATION.value,
            'question': 'Pourquoi y a-t-il un système Premium ?',
            'answer': (
                'Le système Premium permet de financer le développement d\'AmbianceBoard et de couvrir les coûts associés, tout en offrant '
                'des fonctionnalités avancées aux utilisateurs. '
                'Cela augmente les limites de stockage et offre un accès à des fonctionnalités exclusives.'
                'L\'offre Premium est optionnelle et ne limite pas l\'utilisation de la version gratuite.'
            ),
        },
        {
            'theme': FAQCategorieEnum.PRESENTATION.value,
            'question': 'Quelle est la différence entre un soundboard public et privé ?',
            'answer': (
                'Un soundboard public est accessible à tous les utilisateurs. '
                'Un utilisateur peut consulter, écouter et proposer des sons pour un soundboard public. '
                'Un soundboard privé est réservé à son créateur, garantissant un contrôle total sur le contenu. '
                'Il ne peut pas être consulté par d\'autres utilisateurs.'
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
        {
            'theme': FAQCategorieEnum.MJ.value,
            'question': 'Puis-je autoriser mes joueurs à déclencher certains sons ?',
            'answer': (
                'Oui, vous pouvez autoriser vos joueurs à déclencher certains sons en leur donnant les permissions appropriées sur le soundboard. '
                'Cela permet à chaque joueur de contribuer à l\'ambiance sonore de la partie.'
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
        # ── Droits et license ──────────────────────────────────────
        {
            'theme': FAQCategorieEnum.DROITS.value,
            'question': 'Puis-je importer n\'importe quel son ?',
            'answer': (
                'Vous pouvez importer n\'importe quel son sur AmbianceBoard, mais vous devez respecter les droits d\'auteur. '
                'En cas de doutes garder les boutons non copiables et ne partager pas vos soundboards contenant des sons protégés par le droit d\'auteur. '
            ),
        },
        {
            'theme': FAQCategorieEnum.DROITS.value,
            'question': 'Quels sont les droits d\'utilisation des sons sur AmbianceBoard ?',
            'answer': (
                'Les sons que vous importez sur AmbianceBoard restent sous votre responsabilité en termes de droits d\'auteur. '
                'La modération se réserve le droit de supprimer tout contenu qui enfreint les lois sur les droits d\'auteur. '
            ),
        },
        {
            'theme': FAQCategorieEnum.DROITS.value,
            'question': 'Comment signaler un contenu ?',
            'answer': (
                'Si vous constatez un contenu qui enfreint les droits d\'auteur ou les règles de la communauté,'
                'vous pouvez le signaler via le formulaire de contact sur le site ou en cliquant sur le bouton de signalement'
                'en forme de drapeau dans la barre de navigation sur la soundboard à signaler.'
            ),
        },
        # ── Participation ──────────────────────────────────────
        {
            'theme': FAQCategorieEnum.PARTICIPATION.value,
            'question': 'Comment puis-je contribuer à AmbianceBoard ?',
            'answer': (
                'Vous pouvez contribuer à AmbianceBoard de plusieurs façons : en proposant des sons, en signalant des bugs, '
                'en proposant des idées via le support ou sur le Discord. '
                'Si vous êtes motivé, vous pouvez devenir bêta-testeur et avoir un accès anticipé aux nouvelles fonctionnalités.'
                'Si vous êtes développeur, vous pouvez également contribuer directement sur GitHub. '
            ),
        }

        # ── Autres ──────────────────────────────────────
        {
            'theme': FAQCategorieEnum.OTHER.value,
            'question': 'Pourquoi ça ne fonctionne pas correctement sur Safari/IOS ?',
            'answer': (
                'Safari et IOS utilisent le moteur de rendu Webkit. Celui-ci possède des restrictions spécifiques '
                'concernant la lecture automatique des médias et la gestion des fichiers audio. '
                'Je travaille pour trouver des solutions alternatives. '
                'À ce jour, je n\'ai pas d\'alternative viable pour le moment. '
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