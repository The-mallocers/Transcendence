from django.db import models

class Rights(models.Model):
    #Primary key
    id = models.AutoField(primary_key=True, null=False, editable=False)

    #Secondary key
    is_admin = models.BooleanField(default=False, null=False, editable=True)

    # Grafana
    grafana_token = models.CharField(max_length=100, null=True, blank=True)
    grafana_id = models.IntegerField(default=0)
    grafana_dashboard = models.URLField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'client_rights'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return "Client is admin" if self.is_admin else "Client isn't admin"

    def save(self, *args, **kargs):
        super().save(*args, **kargs)

    def delete(self, *args, **kargs):
        super().delete(*args, **kargs)
