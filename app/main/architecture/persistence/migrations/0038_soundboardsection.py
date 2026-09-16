from django.db import migrations, models
import django.db.models.deletion


def migrate_section_data(apps, schema_editor):
    sound_board = apps.get_model("main", "SoundBoard")
    soundboard_playlist = apps.get_model("main", "SoundboardPlaylist")
    soundboard_section = apps.get_model("main", "SoundboardSection")

    for soundboard in sound_board.objects.all():
        sections_by_number = {}
        for old_section in soundboard_playlist.objects.filter(soundBoard=soundboard).values_list("section", flat=True).distinct():
            if old_section is None:
                old_section = 1
            section_obj, _ = soundboard_section.objects.get_or_create(
                soundBoard=soundboard,
                section=int(old_section),
                defaults={"name": f"Section {old_section}", "order": int(old_section)},
            )
            sections_by_number[int(old_section)] = section_obj

        for playlist in soundboard_playlist.objects.filter(soundBoard=soundboard):
            section_number = int(playlist.section) if playlist.section is not None else 1
            playlist.section_ref = sections_by_number.get(section_number)
            playlist.save(update_fields=["section_ref"])


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0037_soundboardscript_soundboardscriptstep"),
    ]

    operations = [
        migrations.CreateModel(
            name="SoundboardSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, default="", max_length=255)),
                ("section", models.PositiveIntegerField(default=1)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "SoundBoard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sections",
                        to="main.soundboard",
                    ),
                ),
            ],
            options={
                "ordering": ["section", "order", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="soundboardsection",
            constraint=models.UniqueConstraint(fields=("SoundBoard", "section"), name="unique_soundboard_section_number"),
        ),
        migrations.AddField(
            model_name="soundboardplaylist",
            name="section_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="playlists",
                to="main.soundboardsection",
            ),
        ),
        migrations.RunPython(migrate_section_data, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="soundboardplaylist",
            name="section",
        ),
        migrations.RenameField(
            model_name="soundboardplaylist",
            old_name="section_ref",
            new_name="section",
        ),
    ]
