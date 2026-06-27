from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Revenue
from .forms import RevenueForm
from django.db.models import Sum
from web_project import TemplateLayout
from apps.notificationApp.services import create_due_soon_epargne_notifications

# Create ONE instance you can reuse
layout = TemplateLayout()


@login_required
def revenue_list(request):
    # ✅ Filtrer par utilisateur
    revenues = Revenue.objects.filter(user=request.user)
    total_revenue = revenues.aggregate(Sum('amount'))['amount__sum']

    if total_revenue is None:
        total_revenue = 0

    context = {
        'revenues': revenues,
        'total_revenue': total_revenue,
    }

    context = layout.init(context)

    # fallback if layout_path is still empty
    if not context.get("layout_path"):
        context["layout_path"] = "layout_vertical.html"
    
    create_due_soon_epargne_notifications(request.user)
    return render(request, 'revenue/revenue_list.html', context)


@login_required
def revenue_create(request):
    if request.method == 'POST':
        form = RevenueForm(request.POST, user=request.user)
        if form.is_valid():
            revenue = form.save(commit=False)
            revenue.user = request.user
            
            # Pour compatibilité avec l'ancien champ category
            if revenue.categorie:
                revenue.category = revenue.categorie.nom
            
            revenue.save()
            messages.success(request, 'Revenu ajouté avec succès!')
            return redirect('revenueApp:revenue_list')
    else:
        form = RevenueForm(user=request.user)

    context = {'form': form}
    context = layout.init(context)

    if not context.get("layout_path"):
        context["layout_path"] = "layout_vertical.html"

    return render(request, 'revenue/revenue_form.html', context)


@login_required
def revenue_update(request, pk):
    # ✅ Vérifier que le revenu appartient à l'utilisateur
    revenue = get_object_or_404(Revenue, pk=pk, user=request.user)

    if request.method == 'POST':
        form = RevenueForm(request.POST, instance=revenue, user=request.user)
        if form.is_valid():
            revenue = form.save(commit=False)
            
            # Pour compatibilité avec l'ancien champ category
            if revenue.categorie:
                revenue.category = revenue.categorie.nom
            
            revenue.save()
            messages.success(request, 'Revenu modifié avec succès!')
            return redirect('revenueApp:revenue_list')
    else:
        form = RevenueForm(instance=revenue, user=request.user)

    context = {'form': form, 'revenue': revenue}
    context = layout.init(context)

    if not context.get("layout_path"):
        context["layout_path"] = "layout_vertical.html"

    return render(request, 'revenue/revenue_form.html', context)


@login_required
def revenue_delete(request, pk):
    # ✅ Vérifier que le revenu appartient à l'utilisateur
    revenue = get_object_or_404(Revenue, pk=pk, user=request.user)

    if request.method == 'POST':
        revenue.delete()
        messages.success(request, 'Revenu supprimé avec succès!')
        return redirect('revenueApp:revenue_list')

    context = {'revenue': revenue}
    context = layout.init(context)

    if not context.get("layout_path"):
        context["layout_path"] = "layout_vertical.html"

    return render(request, 'revenue/revenue_confirm_delete.html', context)