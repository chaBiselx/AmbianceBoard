import json
from urllib.parse import urlencode

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from main.domain.general.service.FAQService import FAQService


register = template.Library()

SCHEMA_ORG_CONTEXT = 'https://schema.org'
ROBOTS_INDEX_FOLLOW = 'index,follow'
ROBOTS_NOINDEX_FOLLOW = 'noindex,follow'

DEFAULT_LISTING_KEYWORDS = [
    'soundboard',
    'soundboard public',
    'ambiance jdr',
    'jeux de role',
    'playlist ambiance',
    'ambiance musicale',
]


def _unique_keep_order(values: list[str]) -> list[str]:
    """Normalise et dedoublonne une liste en preservant l'ordre d'origine."""
    unique_values: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized_value = str(value).strip()
        if not normalized_value:
            continue
        if normalized_value not in seen:
            seen.add(normalized_value)
            unique_values.append(normalized_value)
    return unique_values


def _build_absolute_url(request, route_name: str, query_params: dict | None = None, **kwargs) -> str:
    """Construit une URL absolue a partir d'une route Django et de parametres optionnels."""
    base_url = request.build_absolute_uri(reverse(route_name, kwargs=kwargs if kwargs else None))
    if not query_params:
        return base_url
    return f"{base_url}?{urlencode(query_params)}"


def _fallback_og_image(request) -> str:
    """Retourne l'image Open Graph par defaut utilisee en absence d'icone specifique."""
    return request.build_absolute_uri(static('img/logo.png'))


def _get_available_languages() -> list[str]:
    """Retourne les langues configurees au format attendu par les moteurs de recherche."""
    return [language_code.replace('_', '-') for language_code, _ in settings.LANGUAGES]


def _build_json_ld(json_ld_type: str, name: str, description: str, canonical: str, keywords: list[str], image: str | None = None, about: list[str] | None = None) -> dict:
    """Assemble la structure JSON-LD commune des pages SEO."""
    json_ld = {
        '@context': SCHEMA_ORG_CONTEXT,
        '@type': json_ld_type,
        'name': name,
        'description': description,
        'url': canonical,
        'inLanguage': 'fr-FR',
        'keywords': ', '.join(keywords),
    }
    if image:
        json_ld['image'] = image
    if about:
        json_ld['about'] = about
    return json_ld


def _build_seo_payload(title: str, description: str, keywords: list[str], canonical: str, og_image: str, robots: str, json_ld: dict) -> dict:
    """Centralise la composition des metadonnees SEO/OG/Twitter exposees au template."""
    keywords_str = ', '.join(keywords)
    # Escape script-sensitive characters so JSON-LD remains safe even when marked safe in templates.
    json_ld_json = (
        json.dumps(json_ld)
        .replace('<', '\\u003c')
        .replace('>', '\\u003e')
        .replace('&', '\\u0026')
        .replace('\u2028', '\\u2028')
        .replace('\u2029', '\\u2029')
    )
    return {
        'title': title,
        'description': description,
        'keywords': keywords_str,
        'og_title': title,
        'og_description': description,
        'og_type': 'website',
        'og_url': canonical,
        'og_image': og_image,
        'twitter_card': 'summary_large_image',
        'twitter_title': title,
        'twitter_description': description,
        'twitter_image': og_image,
        'canonical': canonical,
        'available_languages': _get_available_languages(),
        'robots': robots,
        'json_ld_json': json_ld_json,
    }


def _build_listing_seo_context(request, selected_tag, list_tags, current_page: int, total_results: int) -> dict:
    """Calcule les metadonnees SEO pour la page de listing public des soundboards."""
    top_tags = [tag.name for tag in list_tags if getattr(tag, 'name', None)]
    keywords = _unique_keep_order(([selected_tag] if selected_tag else []) + top_tags + DEFAULT_LISTING_KEYWORDS)[:8]

    title = 'Soundboards publics | AmbianceBoard'
    if selected_tag:
        title = f'Soundboards publics - Tag {selected_tag} | AmbianceBoard'
    if current_page > 1:
        title = f'{title} - Page {current_page}'

    if total_results == 0:
        description = 'Aucun soundboard public ne correspond a cette recherche pour le moment sur AmbianceBoard.'
    elif selected_tag:
        description = f'Decouvrez des soundboards publics pour le tag {selected_tag} sur AmbianceBoard.'
    else:
        description = 'Decouvrez des soundboards publics pour vos parties JDR et jeux de societe sur AmbianceBoard.'

    canonical_query = {'tag': selected_tag} if selected_tag else None
    canonical = _build_absolute_url(request, 'publicListingSoundboard', query_params=canonical_query)
    robots = ROBOTS_NOINDEX_FOLLOW if current_page > 1 or total_results == 0 else ROBOTS_INDEX_FOLLOW
    json_ld_type = 'WebPage' if total_results == 0 else 'CollectionPage'
    json_ld = _build_json_ld(
        json_ld_type=json_ld_type,
        name=title,
        description=description,
        canonical=canonical,
        keywords=keywords,
    )
    og_image = _fallback_og_image(request)
    return _build_seo_payload(
        title=title,
        description=description,
        keywords=keywords,
        canonical=canonical,
        og_image=og_image,
        robots=robots,
        json_ld=json_ld,
    )


def _resolve_listing_seo_context(request, context) -> dict:
    """Extrait les donnees utiles du contexte template puis delegue au builder listing."""
    paginator_context = context.get('paginator') or {}
    try:
        page_number = int(paginator_context.get('page_number', 1))
    except (TypeError, ValueError):
        page_number = 1
    page_objects = context.get('page_objects')
    total_results = 0
    if page_objects is not None and getattr(page_objects, 'paginator', None):
        total_results = int(page_objects.paginator.count)

    return _build_listing_seo_context(
        request,
        selected_tag=context.get('selected_tag'),
        list_tags=context.get('listTags') or [],
        current_page=page_number,
        total_results=total_results,
    )


def _build_read_seo_context(request, soundboard) -> dict:
    """Calcule les metadonnees SEO pour la page detail d'un soundboard public."""
    tags = [tag.name for tag in soundboard.get_tags_list()]
    soundboard_name = (soundboard.name or 'Soundboard').strip()

    description_seo = (soundboard.descriptionSEO or '').strip()
    if description_seo:
        description = description_seo
    elif tags:
        description = f"{soundboard_name} - Soundboard public avec les tags: {', '.join(tags[:5])}."
    else:
        description = f'{soundboard_name} - Soundboard public sur AmbianceBoard pour creer une ambiance musicale en jeu.'

    keywords = _unique_keep_order([
        soundboard_name,
        *tags,
        'soundboard public',
        'ambiance jdr',
        'playlist ambiance',
    ])[:8]

    title = f'{soundboard_name} | Soundboard public | AmbianceBoard'
    canonical = _build_absolute_url(request, 'publicReadSoundboard', soundboard_uuid=soundboard.uuid)
    og_image = _fallback_og_image(request)
    if soundboard.icon:
        og_image = request.build_absolute_uri(soundboard.icon.url)

    json_ld = _build_json_ld(
        json_ld_type='CreativeWork',
        name=soundboard_name,
        description=description,
        canonical=canonical,
        keywords=keywords,
        image=og_image,
        about=tags or None,
    )

    return _build_seo_payload(
        title=title,
        description=description,
        keywords=keywords,
        canonical=canonical,
        og_image=og_image,
        robots=ROBOTS_INDEX_FOLLOW,
        json_ld=json_ld,
    )


def _build_default_seo_context(request, _context) -> dict:
    """Fournit un SEO generique lorsque la route n'a pas de resolver specifique."""
    title = 'AmbianceBoard'
    description = (
        'Soundboard JDR gratuit en ligne pour maitres du jeu. '
        'Declenchez ambiances, effets sonores et musiques en un clic.'
    )
    keywords = _unique_keep_order([
        'soundboard',
        'soundboard jdr gratuit',
        'maitre du jeu',
        'ambiance sonore jdr',
        'playlist ambiance',
    ])
    canonical = request.build_absolute_uri()
    og_image = _fallback_og_image(request)
    json_ld = _build_json_ld(
        json_ld_type='WebPage',
        name=title,
        description=description,
        canonical=canonical,
        keywords=keywords,
        image=og_image,
    )
    return _build_seo_payload(
        title=title,
        description=description,
        keywords=keywords,
        canonical=canonical,
        og_image=og_image,
        robots=ROBOTS_INDEX_FOLLOW,
        json_ld=json_ld,
    )


def _resolve_read_seo_context(request, context):
    """Recupere le soundboard depuis le contexte et retourne son SEO si disponible."""
    soundboard = context.get('soundboard')
    if soundboard:
        return _build_read_seo_context(request, soundboard)
    return None


def _build_home_seo_context(request, _context) -> dict:
    """Calcule les metadonnees SEO/GEO pour la page d'accueil avec schema FAQPage."""
    title = 'AmbianceBoard — Soundboard JDR gratuit pour Maître du Jeu'
    description = (
        'Soundboard JDR gratuit en ligne pour maîtres du jeu. '
        'Déclenchez ambiances, effets sonores et musiques en un clic. '
        'Alternative open source à Syrinscape, sans installation, avec partage en temps réel.'
    )
    keywords = _unique_keep_order([
        'soundboard jdr gratuit',
        'soundboard maître du jeu',
        'outil MJ jeu de rôle',
        'ambiance sonore jdr',
        'alternative syrinscape',
        'soundboard en ligne jdr',
        'améliorer immersion jdr',
        'playlist ambiance jdr',
        'outils maître du jeu',
        'soundboard',
        'jeux de rôle',
    ])
    canonical = _build_absolute_url(request, 'home')
    og_image = _fallback_og_image(request)

    json_ld = {
        '@context': SCHEMA_ORG_CONTEXT,
        '@type': 'WebApplication',
        'name': 'AmbianceBoard',
        'alternateName': ['Soundboard JDR', 'Soundboard Ambiance'],
        'url': canonical,
        'description': description,
        'applicationCategory': 'MultimediaApplication',
        'operatingSystem': 'Web Browser',
        'inLanguage': 'fr-FR',
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
        'keywords': ', '.join(keywords),
        'audience': {'@type': 'Audience', 'audienceType': 'Maîtres du jeu et joueurs de jeux de rôle'},
    }
    return _build_seo_payload(
        title=title,
        description=description,
        keywords=keywords,
        canonical=canonical,
        og_image=og_image,
        robots=ROBOTS_INDEX_FOLLOW,
        json_ld=json_ld,
    )





def _build_faq_seo_context(request, _context) -> dict:
    """Calcule les metadonnees SEO pour la page FAQ avec schema FAQPage."""
    title = 'FAQ — Soundboard JDR & outils pour Maître du Jeu | AmbianceBoard'
    description = (
        'Toutes les réponses sur AmbianceBoard : soundboard JDR gratuit, alternative à Syrinscape, '
        'outils pour maître du jeu, immersion en jeu de rôle et partage en temps réel.'
    )
    keywords = _unique_keep_order([
        'faq soundboard jdr',
        'questions soundboard maître du jeu',
        'alternative syrinscape gratuit',
        'comment créer ambiance jdr',
        'outils maître du jeu',
        'soundboard jdr gratuit',
        'améliorer immersion jdr',
        'jeu de rôle ambiance sonore',
    ])
    canonical = _build_absolute_url(request, 'faq')
    og_image = _fallback_og_image(request)
    HOME_FAQ = FAQService().HOME_FAQ
    faq_entities = [
        {
            '@type': 'Question',
            'name': item['question'],
            'acceptedAnswer': {'@type': 'Answer', 'text': item['answer']},
        }
        for item in HOME_FAQ
    ]
    json_ld = {
        '@context': SCHEMA_ORG_CONTEXT,
        '@type': 'FAQPage',
        'mainEntity': faq_entities,
    }
    return _build_seo_payload(
        title=title,
        description=description,
        keywords=keywords,
        canonical=canonical,
        og_image=og_image,
        robots=ROBOTS_INDEX_FOLLOW,
        json_ld=json_ld,
    )


@register.simple_tag(takes_context=True)
def resolve_page_seo(context):
    """Resout le SEO d'une page en fonction de la route courante et du contexte template."""
    request = context.get('request')
    if request is None:
        return context.get('seo')

    # Backward compatibility for pages that still set SEO in views.
    existing_seo = context.get('seo')
    if existing_seo:
        return existing_seo

    route_name = getattr(getattr(request, 'resolver_match', None), 'url_name', '')
    resolver = _get_route_resolvers().get(route_name)
    if resolver is None:
        return _build_default_seo_context(request, context)
    return resolver(request, context)


@register.simple_tag(takes_context=True)
def get_current_seo(context):
    """Retourne le SEO deja resolu, sinon la valeur legacy stockee dans le contexte."""
    resolved_seo = context.get('resolved_seo')
    if resolved_seo:
        return resolved_seo
    return context.get('seo')


def _get_route_resolvers() -> dict:
    """Retourne la table de resolvers SEO par route apres definition des fonctions."""
    return {
        'home': _build_home_seo_context,
        'faq': _build_faq_seo_context,
        'publicListingSoundboard': _resolve_listing_seo_context,
        'publicReadSoundboard': _resolve_read_seo_context,
    }