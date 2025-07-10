from django.db import models

class DomainBlacklist(models.Model):
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain

    class Meta:
        verbose_name = "Blacklisted Domain"
        verbose_name_plural = "Blacklisted Domains"
