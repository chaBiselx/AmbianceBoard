from django.test import TestCase, tag

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardTag import SoundboardTag
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.TagRepository import TagRepository


@tag('unitaire')
class TagRepositoryTest(TestCase):
    def setUp(self):
        self.repository = TagRepository()
        self.user = User.objects.create_user(username='tag-user', password='pw')

        self.tag_active_used = SoundboardTag.objects.create(name='used')
        self.tag_active_unused = SoundboardTag.objects.create(name='unused')
        self.tag_inactive_used = SoundboardTag.objects.create(name='inactive-used', is_active=False)

        board = SoundBoard.objects.create(user=self.user, name='Tagged board')
        board.tags.add(self.tag_active_used)
        board.tags.add(self.tag_inactive_used)

    def test_get_with_uuid_returns_value_or_none(self):
        found = self.repository.get_with_uuid(str(self.tag_active_used.uuid))
        missing = self.repository.get_with_uuid('00000000-0000-0000-0000-000000000000')

        self.assertIsNotNone(found)
        self.assertEqual(found.id, self.tag_active_used.id)
        self.assertIsNone(missing)

    def test_get_all_queryset_orders_by_field(self):
        result = list(self.repository.get_all_queryset(order_by='name'))

        self.assertGreaterEqual(len(result), 3)
        self.assertLessEqual(result[0].name, result[-1].name)

    def test_get_list_active_tags_excludes_inactive(self):
        result = list(self.repository.get_list_active_tags())
        result_ids = {tag.id for tag in result}

        self.assertIn(self.tag_active_used.id, result_ids)
        self.assertIn(self.tag_active_unused.id, result_ids)
        self.assertNotIn(self.tag_inactive_used.id, result_ids)

    def test_get_tag_with_count_returns_only_active_used_tags(self):
        result = self.repository.get_tag_with_count()
        result_ids = {tag.id for tag in result}

        self.assertIn(self.tag_active_used.id, result_ids)
        self.assertNotIn(self.tag_active_unused.id, result_ids)
        self.assertNotIn(self.tag_inactive_used.id, result_ids)
