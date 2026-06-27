from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Categorie
import logging

logger = logging.getLogger(__name__)


def verifier_et_envoyer_alerte_categorie(categorie, user):
    """
    Vérifie si une catégorie est en déficit et envoie une alerte email
    
    Args:
        categorie: Instance de Categorie
        user: Utilisateur concerné
    
    Returns:
        bool: True si l'alerte a été envoyée, False sinon
    """
    # Vérifier si les alertes sont activées pour cette catégorie
    if not categorie.alerte_activee:
        return False
    
    # Vérifier si la catégorie est en déficit
    if not categorie.est_en_deficit(user):
        return False
    
    # Vérifier que l'utilisateur a un email
    if not user.email:
        logger.warning(f"L'utilisateur {user.username} n'a pas d'email configuré")
        return False
    
    # Préparer les données pour l'email
    total_revenus = categorie.get_total_revenus(user)
    total_depenses = categorie.get_total_depenses(user)
    deficit = abs(categorie.get_solde(user))
    pourcentage = categorie.get_pourcentage_utilise(user)
    
    context = {
        'user': user,
        'categorie': categorie,
        'total_revenus': total_revenus,
        'total_depenses': total_depenses,
        'deficit': deficit,
        'pourcentage': pourcentage,
    }
    
    # Créer le message HTML et texte
    subject = f'⚠️ Alerte Budget - Catégorie "{categorie.nom}" en déficit'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                <h2 style="color: #d9534f; border-bottom: 2px solid #d9534f; padding-bottom: 10px;">
                    ⚠️ Alerte Budget Dépassé
                </h2>
                
                <p>Bonjour <strong>{user.username}</strong>,</p>
                
                <p>Nous vous informons que vos dépenses dans la catégorie <strong>"{categorie.nom}"</strong> 
                ont dépassé vos revenus.</p>
                
                <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #d9534f;">
                    <h3 style="margin-top: 0; color: #d9534f;">Résumé de la catégorie</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>💰 Total Revenus:</strong></td>
                            <td style="padding: 8px 0; text-align: right; color: #5cb85c;">{total_revenus:.2f} DT</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>💸 Total Dépenses:</strong></td>
                            <td style="padding: 8px 0; text-align: right; color: #d9534f;">{total_depenses:.2f} DT</td>
                        </tr>
                        <tr style="border-top: 2px solid #ddd;">
                            <td style="padding: 8px 0;"><strong>⚠️ Déficit:</strong></td>
                            <td style="padding: 8px 0; text-align: right; color: #d9534f; font-weight: bold;">-{deficit:.2f} DT</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>📊 Pourcentage utilisé:</strong></td>
                            <td style="padding: 8px 0; text-align: right; color: #d9534f; font-weight: bold;">{pourcentage:.1f}%</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 0;"><strong>💡 Recommandations:</strong></p>
                    <ul style="margin: 10px 0;">
                        <li>Révisez vos dépenses dans cette catégorie</li>
                        <li>Envisagez de réduire certaines dépenses non essentielles</li>
                        <li>Consultez votre budget global pour réallouer des fonds</li>
                    </ul>
                </div>
                
                <p>Connectez-vous à votre compte Smart Budgeting pour consulter le détail de vos transactions.</p>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                    Ceci est un message automatique. Pour désactiver ces alertes, rendez-vous dans les paramètres de vos catégories.
                </p>
            </div>
        </body>
    </html>
    """
    
    text_message = f"""
    Alerte Budget Dépassé
    
    Bonjour {user.username},
    
    Vos dépenses dans la catégorie "{categorie.nom}" ont dépassé vos revenus.
    
    Résumé:
    - Total Revenus: {total_revenus:.2f} DT
    - Total Dépenses: {total_depenses:.2f} DT
    - Déficit: -{deficit:.2f} DT
    - Pourcentage utilisé: {pourcentage:.1f}%
    
    Recommandations:
    - Révisez vos dépenses dans cette catégorie
    - Envisagez de réduire certaines dépenses non essentielles
    - Consultez votre budget global
    
    Connectez-vous à Smart Budgeting pour plus de détails.
    """
    
    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Alerte envoyée à {user.email} pour la catégorie {categorie.nom}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'alerte: {str(e)}")
        return False


def verifier_toutes_categories_utilisateur(user):
    """
    Vérifie toutes les catégories d'un utilisateur et envoie des alertes si nécessaire
    
    Args:
        user: Utilisateur à vérifier
    
    Returns:
        list: Liste des catégories pour lesquelles une alerte a été envoyée
    """
    from django.db.models import Q
    
    # Récupérer les catégories de l'utilisateur (personnelles + globales)
    categories = Categorie.objects.filter(
        Q(utilisateur=user) | Q(est_globale=True)
    )
    
    alertes_envoyees = []
    
    for categorie in categories:
        if verifier_et_envoyer_alerte_categorie(categorie, user):
            alertes_envoyees.append(categorie)
    
    return alertes_envoyees