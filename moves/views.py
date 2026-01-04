# moves/views.py
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.utils.dateparse import parse_date
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

from .models import MoveRequest
from .forms import MoveRequestForm, StaffAssignDriverForm, DriverStatusForm

# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # Default values
        ctx['user_role'] = None
        ctx['upcoming_moves'] = []
        ctx['assigned_moves'] = []
        ctx['open_move_requests'] = []

        if user.is_authenticated:
            ctx['user_role'] = user.role
            if user.role == 'customer':
                ctx['upcoming_moves'] = (
                    MoveRequest.objects
                    .filter(customer=user)
                    .exclude(status__in=['completed', 'cancelled'])
                    .order_by('scheduled_date')[:3]
                )
            if user.role == 'driver':
                ctx['assigned_moves'] = (
                    MoveRequest.objects
                    .filter(driver=user)
                    .exclude(status__in=['completed', 'cancelled'])
                    .order_by('scheduled_date')[:3]
                )
            if user.role == 'staff':
                ctx['open_move_requests'] = (
                    MoveRequest.objects
                    .filter(status='pending')
                    .order_by('scheduled_date')
                )
        
        return ctx

class RoleRequiredMixin(UserPassesTestMixin):
    required_roles = ()

    def role_test(self):
        return getattr(self.request.user, 'role', None) in self.required_roles

    def test_func(self):
        return self.role_test()

class MoveListView(LoginRequiredMixin, ListView):
    model = MoveRequest
    template_name = 'moves/move_list.html'
    context_object_name = 'moves'
    
    def get_queryset(self):
        '''
        Enforce object-level authorization:
        - customer: can only view their own moves
        - driver: can only view assigned moves
        - staff: can view all moves
        '''
        qs = MoveRequest.objects.select_related('customer', 'driver')
        user = self.request.user

        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(pickup_address__icontains=q) |
                Q(dropoff_address__icontains=q) |
                Q(customer__username__icontains=q) |
                Q(driver__username__icontains=q)
            )
        
        start = parse_date(self.request.GET.get('start', ''))
        end = parse_date(self.request.GET.get('end', ''))
        if start:
            qs = qs.filter(scheduled_date__gte=start)
        if end:
            qs = qs.filter(scheduled_date__lte=end)
        
        qs = qs.order_by('-scheduled_date', '-created_at')
        if user.role == 'customer':
            return qs.filter(customer=user)
        if user.role == 'driver':
            return qs.filter(driver=user)  # only assigned moves
        
        # staff can view all
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = ctx['moves']
        ctx['summary'] = qs.values('status').annotate(total=Count('id')).order_by('status')

        # persist form fields
        ctx['status'] = self.request.GET.get('status', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['start'] = self.request.GET.get('start', '')
        ctx['end'] = self.request.GET.get('end', '')
        return ctx

class MoveDetailView(LoginRequiredMixin, DetailView):
    model = MoveRequest
    template_name = 'moves/move_detail.html'
    context_object_name = 'move'

    def get_queryset(self):
        qs = MoveRequest.objects.select_related('customer', 'driver')
        user = self.request.user

        if user.role == 'customer':
            return qs.filter(customer=user)
        if user.role == 'driver':
            return qs.filter(driver=user)
        
        return qs

class MoveCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = MoveRequest
    form_class = MoveRequestForm
    template_name = 'moves/move_form.html'
    required_roles = ('customer',)

    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.status = 'pending'
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('moves:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Book a New Move'
        return ctx

class MoveUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = MoveRequest
    form_class = MoveRequestForm
    template_name = 'moves/move_form.html'
    required_roles = ('customer', 'staff')

    def test_func(self):
        if not self.role_test():
            return False
        
        move = self.get_object()
        user = self.request.user

        # Only customer who owns it OR staff can edit
        return (move.customer == user) or (user.role == 'staff')
    
    def dispatch(self, request, *args, **kwargs):
        # Block editing in_progress/completed/cancelled moves
        self.object = self.get_object()
        if self.object.status in ['in_progress', 'completed', 'cancelled']:
            return HttpResponseForbidden('This move can no longer be edited.')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('moves:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Move'
        return ctx

class StaffAssignDriverView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = MoveRequest
    form_class = StaffAssignDriverForm
    template_name = 'moves/staff_assign_driver.html'
    required_roles = ('staff',)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status in ['in_progress', 'completed', 'cancelled']:
            return HttpResponseForbidden('Driver assignment is not allowed for this move’s status.')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        resp = super().form_valid(form)

        # Optional: auto-mark as accepted when assigned
        if self.object.status == 'pending':
            self.object.status = 'accepted'
            self.object.save(update_fields=['status'])
        
        return resp
    
    def get_success_url(self):
        return reverse_lazy('moves:detail', kwargs={'pk': self.object.pk})

class DriverStatusUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = MoveRequest
    form_class = DriverStatusForm
    template_name = 'moves/move_driver_update.html'
    required_roles = ('driver',)
    
    def get_queryset(self):
        # Driver can update only their assigned moves
        return MoveRequest.objects.filter(driver=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status == 'cancelled':
            return HttpResponseForbidden('This move can no longer be edited.')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('moves:detail', kwargs={'pk': self.object.pk})

class MoveCancelView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = MoveRequest
    fields = []  # no editable fields shown
    template_name = 'moves/move_cancel_confirm.html'
    context_object_name = 'move'
    required_roles = ('customer', 'staff')

    def test_func(self):
        if not self.role_test():
            return False

        move = self.get_object()
        user = self.request.user

        # Only customer who owns it OR staff can cancel
        return (move.customer == user) or (user.role == 'staff')
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status in ['in_progress', 'completed', 'cancelled']:
            return HttpResponseForbidden('This move can no longer be cancelled.')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # soft cancel on POST
        self.object = self.get_object()
        self.object.status = 'cancelled'
        self.object.save(update_fields=['status'])
        return redirect('moves:list')
