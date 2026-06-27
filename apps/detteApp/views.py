# Create your views here.
# gestion_dettes/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.db import transaction
from .models import Debt, Payment, Rappel
from .forms import DebtForm, PaymentForm, RappelForm
from web_project import TemplateLayout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token


class DebtListView(LoginRequiredMixin, ListView):
    model = Debt
    template_name = 'detteApp/debt_list.html'
    context_object_name = 'debts'

    def get_queryset(self):
        # Filtrer uniquement les dettes de l'utilisateur connecté
        return Debt.objects.filter(utilisateur=self.request.user)

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


class DebtDetailView(LoginRequiredMixin, DetailView):
    model = Debt
    template_name = 'detteApp/debt_detail.html'
    context_object_name = 'debt'

    def get_queryset(self):
        # Un utilisateur ne peut voir que ses propres dettes
        return Debt.objects.filter(utilisateur=self.request.user)

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


class DebtCreateView(LoginRequiredMixin, CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'detteApp/debt_form_create.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def form_valid(self, form):
        debt = form.save(commit=False)
        debt.utilisateur = self.request.user  # lier la dette à l'utilisateur connecté
        debt.remaining_amount = debt.original_amount  # initialisation automatique
        debt.save()
        return redirect(debt.get_absolute_url())


class DebtUpdateView(LoginRequiredMixin, UpdateView):
    model = Debt
    form_class = DebtForm
    template_name = 'detteApp/debt_form_update.html'

    def get_queryset(self):
        # Un utilisateur ne peut modifier que ses propres dettes
        return Debt.objects.filter(utilisateur=self.request.user)

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


class DebtDeleteView(LoginRequiredMixin, DeleteView):
    model = Debt
    template_name = 'detteApp/debt_confirm_delete.html'
    success_url = reverse_lazy('detteApp:debt_list')

    def get_queryset(self):
        # Un utilisateur ne peut supprimer que ses propres dettes
        return Debt.objects.filter(utilisateur=self.request.user)

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


# Vue pour ajouter un paiement à une dette existante
class AddPaymentView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'detteApp/add_payment.html'

    def dispatch(self, request, *args, **kwargs):
        # Vérifier que la dette appartient à l'utilisateur connecté
        self.debt = get_object_or_404(
            Debt, 
            pk=kwargs['pk'],
            utilisateur=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.debt = self.debt

        # transactionnel : enregistrer le paiement et mettre à jour la dette
        with transaction.atomic():
            payment.save()
            # recalculer remaining à partir des paiements (robuste)
            self.debt.update_remaining()

        return redirect(self.debt.get_absolute_url())

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['debt'] = self.debt  # Ajouter la dette au contexte
        return context


@login_required
def liste_rappels(request):
    rappels = Rappel.objects.filter(debt__utilisateur=request.user)
    context = {'rappels': rappels}
    # Initialiser le layout si nécessaire
    context = TemplateLayout.init(request, context)
    return render(request, "rappels/liste.html", context)


@login_required
def ajouter_rappel(request):
    if request.method == "POST":
        form = RappelForm(request.POST)
        if form.is_valid():
            rappel = form.save(commit=False)
            # Relier à une dette spécifique de l'utilisateur
            # Note: Il serait mieux de passer l'ID de la dette via le formulaire
            rappel.debt = Debt.objects.filter(utilisateur=request.user).last()
            if rappel.debt is None:
                # Gérer le cas où l'utilisateur n'a pas de dettes
                form.add_error(None, "Vous devez d'abord créer une dette.")
                context = {'form': form}
                context = TemplateLayout.init(request, context)
                return render(request, "rappels/ajouter.html", context)
            rappel.save()
            return redirect('liste_rappels')
    else:
        form = RappelForm()
    
    context = {'form': form}
    context = TemplateLayout.init(request, context)
    return render(request, "rappels/ajouter.html", context)


@login_required
@require_POST
def mark_rappel_seen(request):
    """Mark a Rappel as sent/seen via AJAX. Expects POST['rappel_id']. Returns JSON."""
    rappel_id = request.POST.get('rappel_id')
    if not rappel_id:
        return JsonResponse({'ok': False, 'error': 'missing_id'}, status=400)

    try:
        rappel = Rappel.objects.get(pk=int(rappel_id), debt__utilisateur=request.user)
    except Rappel.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not_found'}, status=404)
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'invalid_id'}, status=400)

    # Mark as seen/sent (this app used 'envoye' to mark sent reminders)
    rappel.envoye = True
    rappel.save()
    return JsonResponse({'ok': True, 'rappel_id': rappel_id})