from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from apps.categorieApp.models import Categorie

class Revenue(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='revenues'
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revenues",
        verbose_name="Catégorie"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Garder category pour compatibilité ou supprimer si migration possible
    category = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Revenu"
        verbose_name_plural = "Revenus"

    def __str__(self):
        cat_name = self.categorie.nom if self.categorie else self.category or "Sans catégorie"
        return f"{cat_name} - {self.amount} DT - {self.date}"