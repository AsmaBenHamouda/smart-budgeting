from django import forms
from .models import Revenue
from django.db.models import Q
from apps.categorieApp.models import Categorie

class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ["amount", "date", "categorie", "description"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Ex: 1500.00",
                    "step": "0.01"
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control form-control-lg"
                },
                format='%Y-%m-%d'
            ),
            "categorie": forms.Select(
                attrs={
                    "class": "form-select form-select-lg"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Ex: Salaire du mois de novembre"
                }
            ),
        }
        labels = {
            "amount": "💰 Montant (DT)",
            "date": "📅 Date",
            "categorie": "🏷️ Catégorie",
            "description": "📝 Description (optionnel)",
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        
        # Activer le format de date pour l'input HTML5
        self.fields['date'].input_formats = ['%Y-%m-%d']
        
        # Filtrer les catégories : globales + celles de l'utilisateur
        if "categorie" in self.fields and user is not None:
            self.fields["categorie"].queryset = Categorie.objects.filter(
                Q(est_globale=True) | Q(utilisateur=user)
            ).order_by("nom")
            
            # Message si aucune catégorie disponible
            if not self.fields["categorie"].queryset.exists():
                self.fields["categorie"].help_text = (
                    "Aucune catégorie disponible. Veuillez créer une catégorie d'abord."
                )