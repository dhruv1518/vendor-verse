from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

class VendorRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is a vendor."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if getattr(request.user, 'role', '') != 'VENDOR':
            return redirect('/') # Redirect to home or show 403
            
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an admin."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if getattr(request.user, 'role', '') != 'ADMIN':
            return redirect('/')
            
        return super().dispatch(request, *args, **kwargs)
