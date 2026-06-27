from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum
from decimal import Decimal

class Categorie(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    est_globale = models.BooleanField(default=False, verbose_name="Catégorie globale")
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='categories',
        verbose_name="Créateur"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    # Nouveau champ pour activer/désactiver les alertes
    alerte_activee = models.BooleanField(default=True, verbose_name="Activer les alertes email")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['-date_creation']
        unique_together = [['nom', 'utilisateur']]

    def __str__(self):
        if self.est_globale:
            return f"{self.nom} (Globale)"
        display = getattr(self.utilisateur, "username", None) or getattr(self.utilisateur, "email", None) or str(self.utilisateur)
        return f"{self.nom} ({display})"

    def peut_etre_modifiee_par(self, user):
        """Vérifie si l'utilisateur peut modifier cette catégorie"""
        if user.is_staff:
            return True
        return self.utilisateur == user and not self.est_globale

    def peut_etre_supprimee_par(self, user):
        """Vérifie si l'utilisateur peut supprimer cette catégorie"""
        if user.is_staff and self.est_globale:
            return True
        return self.utilisateur == user and not self.est_globale
    
    def get_total_revenus(self, user=None):
        """Calcule le total des revenus pour cette catégorie"""
        from apps.revenueApp.models import Revenue
        
        query = Revenue.objects.filter(categorie=self)
        if user:
            query = query.filter(user=user)
        
        total = query.aggregate(total=Sum('amount'))['total']
        return total or Decimal('0.00')
    
    def get_total_depenses(self, user=None):
        """Calcule le total des dépenses pour cette catégorie"""
        from apps.depenseApp.models import Depense
        
        query = Depense.objects.filter(categorie=self)
        if user:
            query = query.filter(user=user)
        
        total = query.aggregate(total=Sum('amount'))['total']
        return total or Decimal('0.00')
    
    def get_solde(self, user=None):
        """Calcule le solde (revenus - dépenses)"""
        return self.get_total_revenus(user) - self.get_total_depenses(user)
    
    def est_en_deficit(self, user=None):
        """Vérifie si les dépenses dépassent les revenus"""
        return self.get_solde(user) < 0
    
    def get_pourcentage_utilise(self, user=None):
        """Calcule le pourcentage de revenus utilisé par les dépenses"""
        revenus = self.get_total_revenus(user)
        if revenus == 0:
            return 0
        depenses = self.get_total_depenses(user)
        return float((depenses / revenus) * 100)