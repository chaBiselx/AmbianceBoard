"""
Integration tests for route: moderator playlist tags listing (/moderator/playlist-tags/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@tag("integration")
class ModeratorListingPlaylistTagsRouteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="moderator_playlist_tag_user",
            email="moderator_playlist_tag_user@example.com",
            password="testpass123",
        )
        role_group, _ = Group.objects.get_or_create(name="ROLE_MODERATOR")
        self.user.groups.add(role_group)

    def test_route_accessible_when_authenticated(self):
        self.client.login(username="moderator_playlist_tag_user", password="testpass123")
        response = self.client.get(reverse("moderatorListingPlaylistTags"))
        self.assertIn(response.status_code, [200, 302])

    def test_route_requires_role(self):
        _ = User.objects.create_user(
            username="normal_user_playlist_tag",
            email="normal_user_playlist_tag@example.com",
            password="normalpass123",
        )
        self.client.login(username="normal_user_playlist_tag", password="normalpass123")
        response = self.client.get(reverse("moderatorListingPlaylistTags"))
        self.assertIn(response.status_code, [302, 403, 404])
