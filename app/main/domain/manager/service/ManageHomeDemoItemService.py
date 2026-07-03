from typing import Tuple, Optional, Dict, Any
from django.http import HttpRequest
from django.contrib import messages
from main.architecture.persistence.models.HomeDemoItem import HomeDemoItem
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.repository.HomeDemoItemRepository import HomeDemoItemRepository
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.interface.ui.forms.manager.HomeDemoItemForm import HomeDemoItemForm
from main.domain.common.utils.logger import logger


class ManageHomeDemoItemService:
    """
    Service pour gérer la création et modification d'éléments Home Demo.
    
    Encapsule toute la logique métier de validation et traitement,
    permettant à la vue d'être simple et lisible.
    """

    def __init__(self):
        self.item_repository = HomeDemoItemRepository()
        self.soundboard_repository = SoundBoardRepository()

    def get_initial_data(
        self, 
        uuid: Optional[str] = None, 
        soundboard_uuid: Optional[str] = None
    ) -> Tuple[Optional[HomeDemoItem], Optional[SoundBoard], bool, Optional[str]]:
        """
        Récupère et valide les données initiales pour la vue.
        
        Returns:
            Tuple[item, selected_soundboard, is_update, error_message]
            - item: HomeDemoItem pour une mise à jour, None sinon
            - selected_soundboard: SoundBoard sélectionné pour une création, None sinon
            - is_update: bool indiquant si c'est une mise à jour
            - error_message: message d'erreur si validation échouée, None sinon
        """
        is_update = uuid is not None

        if is_update:
            return self._get_existing_item(uuid)
        else:
            return self._get_new_item_soundboard(soundboard_uuid)

    def _get_existing_item(self, uuid: str) -> Tuple[Optional[HomeDemoItem], Optional[SoundBoard], bool, Optional[str]]:
        """Récupère et valide un item existant pour mise à jour."""
        item = self.item_repository.get_item_by_uuid(uuid)
        if item is None:
            return None, None, True, "Élément introuvable."
        return item, None, True, None

    def _get_new_item_soundboard(self, soundboard_uuid: Optional[str]) -> Tuple[Optional[HomeDemoItem], Optional[SoundBoard], bool, Optional[str]]:
        """Récupère et valide le soundboard pour création."""
        if soundboard_uuid is None:
            return None, None, False, "Veuillez d'abord choisir un soundboard public."

        soundboard = self.soundboard_repository.get(soundboard_uuid)
        
        if soundboard is None or not soundboard.is_public:
            return None, None, False, "Soundboard public introuvable ou non autorisé."
        
        if soundboard.id in self.item_repository.get_used_soundboard_ids():
            return None, None, False, "Ce soundboard est déjà utilisé dans la démo."

        return None, soundboard, False, None

    def process_form_submission(
        self,
        request_post: Dict[str, Any],
        item: Optional[HomeDemoItem],
        selected_soundboard: Optional[SoundBoard]
    ) -> Tuple[bool, Optional[HomeDemoItem], HomeDemoItemForm]:
        """
        Traite la soumission du formulaire.
        
        Returns:
            Tuple[is_valid, saved_item, form]
            - is_valid: bool indiquant si le formulaire était valide
            - saved_item: l'item sauvegardé si valide, None sinon
            - form: le formulaire (avec erreurs si invalide)
        """
        form = HomeDemoItemForm(request_post, instance=item, selected_soundboard=selected_soundboard)
        if form.is_valid():
            saved_item = form.save()
            return True, saved_item, form
        return False, None, form

    def get_form(
        self,
        item: Optional[HomeDemoItem] = None,
        selected_soundboard: Optional[SoundBoard] = None
    ) -> HomeDemoItemForm:
        """
        Crée une instance du formulaire (vide, pour GET).
        
        Args:
            item: l'item existant pour mise à jour (optionnel)
            selected_soundboard: le soundboard sélectionné (optionnel)
        """
        return HomeDemoItemForm(
            instance=item,
            selected_soundboard=selected_soundboard
        )

    def get_context(
        self,
        form: HomeDemoItemForm,
        item: Optional[HomeDemoItem],
        selected_soundboard: Optional[SoundBoard],
        is_update: bool
    ) -> Dict[str, Any]:
        """
        Prépare le contexte pour le rendu du template.
        
        Returns:
            Dict avec les données pour le template
        """
        return {
            'title': "Modifier un élément Home Demo" if is_update else "Créer un élément Home Demo",
            'form': form,
            'item': item,
            'selected_soundboard': selected_soundboard,
            'action': 'update' if is_update else 'create',
        }

    def log_item_action(
        self,
        item: HomeDemoItem,
        is_update: bool,
        username: str
    ) -> None:
        """Enregistre l'action effectuée sur l'item."""
        action = 'modifié' if is_update else 'créé'
        logger.info(f"Home demo item {action}: {item.uuid} par {username}")

    def get_success_message(self, is_update: bool) -> str:
        """Retourne le message de succès approprié."""
        action = 'modifié' if is_update else 'créé'
        return f"Élément {action} avec succès."
