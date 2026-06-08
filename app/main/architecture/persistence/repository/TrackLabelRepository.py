from typing import Optional
from django.db.models import QuerySet, Avg, Count
from main.architecture.persistence.models.TrackLabel import TrackLabel
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.Playlist import Playlist


class TrackLabelRepository:

    def get_labels_for_track(self, track: Track) -> QuerySet[TrackLabel]:
        return TrackLabel.objects.filter(track=track)

    def save_labels(self, track: Track, labels: list[dict]) -> list[TrackLabel]:
        """
        Sauvegarde les labels pour une track (remplace les existants).
        labels: [{"label": str, "confidence": float, "category": str}, ...]
        """
        TrackLabel.objects.filter(track=track).delete()
        objects = [
            TrackLabel(
                track=track,
                category=lbl["category"],
                label=lbl["label"],
                confidence=lbl["confidence"],
            )
            for lbl in labels
        ]
        return TrackLabel.objects.bulk_create(objects)

    def get_top_labels_for_playlist(self, playlist: Playlist, top_k: int = 10) -> list[dict]:
        """
        Agrège les labels de toutes les tracks d'une playlist.
        Retourne les top labels triés par confiance moyenne pondérée.
        """
        return list(
            TrackLabel.objects.filter(track__playlist=playlist)
            .values('category', 'label')
            .annotate(
                avg_confidence=Avg('confidence'),
                track_count=Count('track', distinct=True),
            )
            .order_by('-avg_confidence')[:top_k]
        )

    def has_labels(self, track: Track) -> bool:
        return TrackLabel.objects.filter(track=track).exists()

    def get_playlist_categories(self, playlist: Playlist) -> list[dict]:
        """
        Retourne les catégories dominantes d'une playlist avec leur confiance moyenne.
        """
        return list(
            TrackLabel.objects.filter(track__playlist=playlist)
            .values('category')
            .annotate(
                avg_confidence=Avg('confidence'),
                label_count=Count('label', distinct=True),
                track_count=Count('track', distinct=True),
            )
            .order_by('-avg_confidence')
        )

    def get_labels_grouped_by_track(self, track_ids: list[int]) -> dict[int, dict]:
        """
        Retourne les labels groupés par track_id au format catégorie.
        Structure: {track_id: {category: {category_confidence, labels: [{label, confidence}]}}}
        """
        labels = TrackLabel.objects.filter(track_id__in=track_ids).order_by('-confidence')
        result: dict[int, dict] = {}
        for lbl in labels:
            track_data = result.setdefault(lbl.track_id, {})
            cat_data = track_data.setdefault(lbl.category, {'category_confidence': 0, 'labels': []})
            cat_data['labels'].append({'label': lbl.label, 'confidence': lbl.confidence})
            if lbl.confidence > cat_data['category_confidence']:
                cat_data['category_confidence'] = lbl.confidence
        return result
