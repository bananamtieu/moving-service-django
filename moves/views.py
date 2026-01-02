# moves/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils.dateparse import parse_date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import MoveRequest
from .forms import MoveRequestForm

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        user = request.user

        # Default values
        upcoming_moves = []
        assigned_moves = []
        open_move_requests = []

        if user.role == 'customer':
            upcoming_moves = (
                MoveRequest.objects
                .filter(customer=user)
                .exclude(status__in=['completed', 'canceled'])
                .order_by('scheduled_date')[:3]
            )
        elif user.role in ['driver', 'staff']:
            assigned_moves = (
                MoveRequest.objects
                .filter(driver=user)
                .exclude(status__in=['completed', 'canceled'])
                .order_by('scheduled_date')[:3]
            )
            if user.role == 'staff':
                open_move_requests = (
                    MoveRequest.objects
                    .filter(status='pending')
                    .order_by('scheduled_date')[:5]
                )
        
        context = {
            'user_role': user.role,
            'upcoming_moves': upcoming_moves,
            'assigned_moves': assigned_moves,
            'open_move_requests': open_move_requests,
        }
    else:
        context = {}
    return render(request, 'home.html', context)

@login_required
def move_list(request):
    user = request.user
    qs = MoveRequest.objects.all().select_related("customer", "driver")  # JOINs

    # Role scoping
    if user.role == 'customer':
        qs = qs.filter(customer=user)
    elif user.role == 'driver':
        qs = qs.filter(driver=user)   # drivers see assigned moves only
    # staff sees all

    # ---- Filters from query params ----
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(pickup_address__icontains=q) |
            Q(dropoff_address__icontains=q) |
            Q(customer__username__icontains=q) |
            Q(driver__username__icontains=q)
        )
    
    start = parse_date(request.GET.get('start', ''))
    end = parse_date(request.GET.get('end', ''))
    if start:
        qs = qs.filter(scheduled_date__gte=start)
    if end:
        qs = qs.filter(scheduled_date__lte=end)
    
    qs = qs.order_by("-scheduled_date", "-created_at")

    # Annotations: counts by status for the filtered queryset
    summary = qs.values('status').annotate(total=Count('id')).order_by('status')

    context = {
        'moves': qs,
        'summary': summary,
        'status': status,
        'q': q,
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
    }
    return render(request, 'moves/move_list.html', context)

@login_required
def move_detail(request, pk):
    move = get_object_or_404(MoveRequest, pk=pk)

    # Simple permission check:
    if not (move.customer == request.user or request.user.role in ['driver', 'staff']):
        return HttpResponseForbidden('You do not have permission to view this move.')
    
    context = {'move': move}
    return render(request, 'moves/move_detail.html', context)

@login_required
def move_create(request):
    if request.user.role != 'customer':
        return HttpResponseForbidden('Only customers can book moves right now.')
    
    if request.method == 'POST':
        form = MoveRequestForm(request.POST)
        if form.is_valid():
            move = form.save(commit=False)
            move.customer = request.user
            move.status = 'pending'
            move.save()
            return redirect('moves:detail', pk=move.pk)
    else:
        form = MoveRequestForm()
    
    context = {
        'form': form,
        'title': 'Book a New Move',
    }
    return render(request, 'moves/move_form.html', context)

@login_required
def move_update(request, pk):
    move = get_object_or_404(MoveRequest, pk=pk)

    # Only customer who owns it OR staff can edit for now
    if not (move.customer == request.user or request.user.role == 'staff'):
        return HttpResponseForbidden('You do not have permission to edit this move.')
    
    # Optional: limit editing if already completed/cancelled
    if move.status in ['completed', 'cancelled']:
        return HttpResponseForbidden('Completed or cancelled moves cannot be edited.')
    
    if request.method == 'POST':
        form = MoveRequestForm(request.POST, instance=move)
        if form.is_valid():
            form.save()
            return redirect('moves:detail', pk=move.pk)
    else:
        form = MoveRequestForm(instance=move)
    
    context = {
        'form': form,
        'title': 'Edit Move',
    }
    return render(request, 'moves/move_form.html', context)

@login_required
def move_cancel(request, pk):
    move = get_object_or_404(MoveRequest, pk=pk)

    # Only customer who owns it OR staff can cancel
    if not (move.customer == request.user or request.user.role == 'staff'):
        return HttpResponseForbidden('You do not have permission to cancel this move.')
    
    if request.method == 'POST':
        # soft cancel
        move.status = 'cancelled'
        move.save()
        return redirect('moves:list')
    
    context = {'move': move}
    return render(request, 'moves/move_cancel_confirm.html', context)
