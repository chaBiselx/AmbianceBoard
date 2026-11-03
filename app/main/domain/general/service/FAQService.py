from itertools import groupby
from main.domain.general.enum.FAQCategorieEnum import FAQCategorieEnum
from main.domain.common.utils.settings import Settings

class FAQService:
    """
    Service class for handling FAQ-related operations.
    """
    HOME_FAQ = [
        # ── Présentation & tarifs ────────────────────────────────────────────
        {
            'label': 'presentation-free',
            'theme': FAQCategorieEnum.PRESENTATION,
            'question_fr': 'Est-ce que c\'est vraiment gratuit ?',
            'question_en': 'Is it really free?',
            'answer_fr': (
                'Oui, AmbianceBoard est entièrement gratuit et ça le restera. '
                'Le JDR coûte déjà assez cher, je ne veux pas ajouter de frais supplémentaires pour les maîtres du jeu. '
                'Vous pouvez créer des soundboards, les partager et les utiliser sans aucun coût. '
                'Un compte gratuit vous permet de sauvegarder vos soundboards et de partager l\'écoute avec vos joueurs.'
            ),
            'answer_en': (
                'Yes, AmbianceBoard is completely free, and it will stay that way. '
                'Tabletop role-playing games are already expensive enough; I do not want to add extra costs for game masters. '
                'You can create soundboards, share them, and use them at no cost. '
                'A free account lets you save your soundboards and share playback with your players.'
            ),
        },
        {
            'label': 'presentation-what-is-ambianceboard',
            'theme': FAQCategorieEnum.PRESENTATION,
            'question_fr': 'Qu\'est-ce qu\'AmbianceBoard ?',
            'question_en': 'What is AmbianceBoard?',
            'answer_fr': (
                'AmbianceBoard est un soundboard en ligne gratuit conçu spécifiquement pour les maîtres du jeu. '
                'Il permet de déclencher des ambiances sonores, des effets instantanés et des playlists musicales '
                'en un clic, sans aucune installation ni abonnement.'
            ),
            'answer_en': (
                'AmbianceBoard is a free online soundboard designed specifically for game masters. '
                'It lets you trigger soundscapes, instant sound effects, and music playlists with one click, '
                'without any installation or subscription.'
            ),
        },
        {
            'label': 'presentation-how-it-works',
            'theme': FAQCategorieEnum.PRESENTATION,
            'question_fr': 'Comment ça marche ?',
            'question_en': 'How does it work?',
            'answer_fr': (
                'AmbianceBoard fonctionne directement dans votre navigateur web. '
                'Il suffit de créer un soundboard, d\'ajouter vos sons, de les organiser et de commencer à jouer.'
                'Il est possible d\'utiliser des sons de la communauté ou d\'importer vos propres sons. '
            ),
            'answer_en': (
                'AmbianceBoard runs directly in your web browser. '
                'Simply create a soundboard, add and organize your sounds, and start playing. '
                'You can use sounds from the community or upload your own.'
            ),
        },
        {
            'label': 'presentation-premium-system',
            'theme': FAQCategorieEnum.PRESENTATION,
            'question_fr': 'Pourquoi y a-t-il un système Premium ?',
            'question_en': 'Why is there a Premium plan?',
            'answer_fr': (
                'Le système Premium permet de financer le développement d\'AmbianceBoard et de couvrir les coûts associés, tout en offrant '
                'des fonctionnalités avancées aux utilisateurs. '
                'Cela augmente les limites de stockage et offre un accès à des fonctionnalités exclusives.'
                'L\'offre Premium est optionnelle et ne limite pas l\'utilisation de la version gratuite.'
            ),
            'answer_en': (
                'The Premium plan helps fund AmbianceBoard’s development and operating costs while offering advanced features. '
                'It increases storage limits and provides access to exclusive features. '
                'Premium is optional and does not restrict use of the free version.'
            ),
        },
        {
            'label': 'presentation-public-vs-private',
            'theme': FAQCategorieEnum.PRESENTATION,
            'question_fr': 'Quelle est la différence entre un soundboard public et privé ?',
            'question_en': 'What is the difference between a public and a private soundboard?',
            'answer_fr': (
                'Un soundboard public est accessible à tous les utilisateurs. '
                'Un utilisateur peut consulter, écouter et proposer des sons pour un soundboard public. '
                'Un soundboard privé est réservé à son créateur, garantissant un contrôle total sur le contenu. '
                'Il ne peut pas être consulté par d\'autres utilisateurs.'
            ),
            'answer_en': (
                'A public soundboard is accessible to everyone. Users can browse, listen to, and suggest sounds for it. '
                'A private soundboard is reserved for its creator, who has full control over its content. '
                'Other users cannot access it.'
            ),
        },
        # ── Maître du Jeu & immersion ────────────────────────────────────────
        {
            'label': 'gamemaster-tools',
            'theme': FAQCategorieEnum.MJ,
            'question_fr': 'Quels outils sont indispensables pour un Maître du Jeu (MJ) ?',
            'question_en': 'What tools does a game master need?',
            'answer_fr': (
                'Pour orchestrer une partie de JDR immersive, un MJ a besoin d\'un soundboard audio pour l\'ambiance, '
                'd\'un outil de partage en temps réel pour les joueurs distants, et d\'une bibliothèque sonore organisée. '
                'AmbianceBoard réunit ces trois besoins dans une seule interface web gratuite.'
            ),
            'answer_en': (
                'To run an immersive tabletop role-playing game, a game master needs an audio soundboard for atmosphere, '
                'a real-time sharing tool for remote players, and an organized sound library. '
                'AmbianceBoard brings all three together in one free web interface.'
            ),
        },
        {
            'label': 'gamemaster-create-ambiance',
            'theme': FAQCategorieEnum.MJ,
            'question_fr': 'Comment créer une ambiance sonore pour une partie de JDR ?',
            'question_en': 'How can I create a soundscape for a role-playing game?',
            'answer_fr': (
                'Créez un soundboard sur AmbianceBoard, ajoutez des playlists par type de scène (taverne, combat, exploration), '
                'puis déclenchez-les d\'un clic pendant la partie. Vous pouvez partager un lien avec vos joueurs pour qu\'ils '
                'entendent la même ambiance en temps réel, que ce soit en présentiel ou en ligne.'
            ),
            'answer_en': (
                'Create a soundboard on AmbianceBoard, add playlists for different scenes (tavern, combat, exploration), '
                'then trigger them with one click during your game. Share a link with your players so they can hear '
                'the same soundscape in real time, whether you are playing in person or online.'
            ),
        },
        {
            'label': 'gamemaster-improve-immersion',
            'theme': FAQCategorieEnum.MJ,
            'question_fr': 'Comment améliorer l\'immersion dans une partie de jeu de rôle ?',
            'question_en': 'How can I make a role-playing game more immersive?',
            'answer_fr': (
                'L\'immersion en JDR repose sur trois piliers : le visuel, la narration et le son. '
                'Un soundboard comme AmbianceBoard permet d\'ajouter la couche sonore sans interrompre le jeu : '
                'ambiances en boucle, effets ponctuels et musiques de scène déclenchés au bon moment renforcent '
                'l\'atmosphère et l\'engagement des joueurs.'
            ),
            'answer_en': (
                'Immersion in a role-playing game rests on three pillars: visuals, storytelling, and sound. '
                'A soundboard like AmbianceBoard adds sound without interrupting the game: looping soundscapes, '
                'one-shot effects, and scene music triggered at the right moment all strengthen the atmosphere '
                'and keep players engaged.'
            ),
        },
        {
            'label': 'gamemaster-allow-players',
            'theme': FAQCategorieEnum.MJ,
            'question_fr': 'Puis-je autoriser mes joueurs à déclencher certains sons ?',
            'question_en': 'Can I let my players trigger certain sounds?',
            'answer_fr': (
                'Oui, vous pouvez autoriser vos joueurs à déclencher certains sons en leur donnant les permissions appropriées sur le soundboard. '
                'Cela permet à chaque joueur de contribuer à l\'ambiance sonore de la partie.'
            ),
            'answer_en': (
                'Yes. You can let your players trigger certain sounds by giving them the appropriate permissions on the soundboard. '
                'This lets everyone contribute to the game’s soundscape.'
            ),
        },
        # ── Comparaisons & alternatives ──────────────────────────────────────
        {
            'label': 'comparison-syrinscape',
            'theme': FAQCategorieEnum.COMPARAISON,
            'question_fr': 'AmbianceBoard est-il une alternative à Syrinscape ?',
            'question_en': 'Is AmbianceBoard an alternative to Syrinscape?',
            'answer_fr': (
                'Oui. AmbianceBoard est une alternative open source et gratuite à Syrinscape. '
                'Là où Syrinscape propose des packs sonores payants, AmbianceBoard vous laisse importer '
                'vos propres sons, utiliser des liens externes ou des radios en streaming. '
                'La synchronisation en temps réel avec vos joueurs est incluse sans abonnement.'
            ),
            'answer_en': (
                'Yes. AmbianceBoard is a free, open-source alternative to Syrinscape. '
                'While Syrinscape offers paid sound packs, AmbianceBoard lets you upload your own sounds, '
                'use external links, or stream radio stations. Real-time synchronization with your players '
                'is included at no cost.'
            ),
        },
        # ── Droits et license ──────────────────────────────────────
        {
            'label': 'copyright-any-sound',
            'theme': FAQCategorieEnum.DROITS,
            'question_fr': 'Puis-je importer n\'importe quel son ?',
            'question_en': 'Can I upload any sound?',
            'answer_fr': (
                'Vous pouvez importer n\'importe quel son sur AmbianceBoard, mais vous devez respecter les droits d\'auteur. '
                'En cas de doutes garder les boutons non copiables et ne partager pas vos soundboards contenant des sons protégés par le droit d\'auteur. '
            ),
            'answer_en': (
                'You can upload any sound to AmbianceBoard, but you must respect copyright. '
                'If you are unsure about a sound’s rights, disable copying on its button and do not share soundboards '
                'that contain copyrighted material.'
            ),
        },
        {
            'label': 'copyright-usage-rights',
            'theme': FAQCategorieEnum.DROITS,
            'question_fr': 'Quels sont les droits d\'utilisation des sons sur AmbianceBoard ?',
            'question_en': 'What are the rules for using sounds on AmbianceBoard?',
            'answer_fr': (
                'Les sons que vous importez sur AmbianceBoard restent sous votre responsabilité en termes de droits d\'auteur. '
                'La modération se réserve le droit de supprimer tout contenu qui enfreint les lois sur les droits d\'auteur. '
            ),
            'answer_en': (
                'You are responsible for ensuring that you have the right to use any sounds you upload to AmbianceBoard. '
                'The moderation team reserves the right to remove content that violates copyright law.'
            ),
        },
        {
            'label': 'copyright-report-content',
            'theme': FAQCategorieEnum.DROITS,
            'question_fr': 'Comment signaler un contenu ?',
            'question_en': 'How can I report content?',
            'answer_fr': (
                'Si vous constatez un contenu qui enfreint les droits d\'auteur ou les règles de la communauté,'
                'vous pouvez le signaler via le formulaire de contact sur le site ou en cliquant sur le bouton de signalement'
                'en forme de drapeau dans la barre de navigation sur la soundboard à signaler.'
            ),
            'answer_en': (
                'If you find content that violates copyright or community rules, report it using the contact form '
                'on the website or by clicking the flag-shaped report button in the navigation bar of the soundboard.'
            ),
        },
        # ── Participation ──────────────────────────────────────
        {
            'label': 'contribution-how',
            'theme': FAQCategorieEnum.PARTICIPATION,
            'question_fr': 'Comment puis-je contribuer à AmbianceBoard ?',
            'question_en': 'How can I contribute to AmbianceBoard?',
            'answer_fr': (
                'Vous pouvez contribuer à AmbianceBoard de plusieurs façons : en proposant des sons, en signalant des bugs, '
                'en proposant des idées via le support ou sur le Discord. '
                'Si vous êtes motivé, vous pouvez devenir bêta-testeur et avoir un accès anticipé aux nouvelles fonctionnalités.'
                'Si vous êtes développeur, vous pouvez également contribuer directement sur GitHub. '
            ),
            'answer_en': (
                'There are several ways to contribute to AmbianceBoard: suggest sounds, report bugs, or share ideas '
                'through support or Discord. If you are interested, you can become a beta tester and get early access '
                'to new features. Developers can also contribute directly on GitHub.'
            ),
        },
        # ── Technique ──────────────────────────────────────
        {
            'label': 'technical-labeling',
            'theme': FAQCategorieEnum.TECHNICAL,
            'question_fr': 'Comment fonctionne la labellisation des sons ?',
            'question_en': 'How does sound labeling work?',
            'answer_fr': (
                'La labellisation des sons est un processus automatisé qui analyse les pistes audio via une IA multi-modal en local. '
                'Ce n\'est pas un LLM, mais un modèle de classification audio qui identifie les types de sons pour les labeliser. '  
                'Les labels seront ensuite utilisés pour m\'aider a faciliter la mise les tags sur les boutons. '
            ),
            'answer_en': (
                'Sound labeling is an automated process that analyzes audio tracks locally using multimodal AI. '
                'It is not an LLM, but an audio classification model that identifies sound types. '
                'The labels will then help make it easier to add tags to buttons.'
            ),
        },
        # ── Autres ──────────────────────────────────────
        {
            'label': 'other-safari',
            'theme': FAQCategorieEnum.OTHER,
            'question_fr': 'Pourquoi ça ne fonctionne pas correctement sur Safari/IOS ?',
            'question_en': 'Why does it not work properly on Safari/iOS?',
            'answer_fr': (
                'Safari et IOS utilisent le moteur de rendu Webkit. Celui-ci possède des restrictions spécifiques '
                'concernant la lecture automatique des médias et la gestion des fichiers audio. '
                'Je travaille pour trouver des solutions alternatives. '
                'À ce jour, je n\'ai pas d\'alternative viable pour le moment. '
            ),
            'answer_en': (
                'Safari and iOS use the WebKit browser engine, which has specific restrictions on media autoplay '
                'and audio file handling. I am working on alternative solutions, but at the moment I do not have '
                'a viable workaround.'
            ),
        },
    ]

    def get_faqs(self, language: str = 'fr'):
        """
        Return FAQ groups localized from their explicit French and English content.

        Returns:
            list: A list of FAQ groups with a localized theme, question, and answer.
        """
        language_code = language.lower().split('-', 1)[0]
        if language_code not in ('fr', 'en'):
            language_code = Settings.get('LANGUAGE_CODE', 'fr').lower()

        return [
            {
                'theme': theme.trad(),
                'items': [
                    {
                        'label': item['label'],
                        'question': item[f'question_{language_code}'],
                        'answer': item[f'answer_{language_code}'],
                    }
                    for item in items
                ],
            }
            for theme, items in groupby(self.HOME_FAQ, key=lambda x: x['theme'])
        ]