from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from .forms import CustomUserCreationForm, ProgrammingLanguageForm, CustomUserChangeForm, UserLoginForm
from .models import ProgrammingLanguage
from problems.models import Problem
from comments.models import Comment

class SignupView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('account_login')
    template_name = 'signup.html'

class UserLoginView(LoginView):
    authentication_form = UserLoginForm
    redirect_field_name = reverse_lazy('home')
    template_name = 'account/login.html'
    redirect_authenticated_user = True

class ProfileView(LoginRequiredMixin,DetailView):
    model = get_user_model()
    context_object_name = 'user'
    login_url = 'account_login'
    template_name = 'users/current_profile.html'

    def get_object(self):
        return get_user_model().objects.get(username=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_problems = Problem.objects.filter(author=self.get_object())
        context["published_problems"] = all_problems.filter(status='published')
        context["draft_problems"] = all_problems.filter(status="draft")
        commented_problems = Comment.objects.filter(commenter=self.get_object()).values_list('problem__id').distinct()
        context["commented"] = Problem.objects.filter(id__in=commented_problems)
        return context
    
class OtherProfileDetailView(DetailView):
    model = get_user_model()
    context_object_name = 'other_user'
    template_name = 'users/user_profile.html'

    def get_object(self):
        return get_user_model().objects.get(id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["problems"] = Problem.objects.filter(author=self.get_object())
        
        return context
    


class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    form_class = CustomUserChangeForm
    context_object_name = 'user'
    success_url = reverse_lazy('profile')
    login_url = 'account_login'
    template_name = 'users/update_profile.html'

    def get_object(self, queryset=None):
        return get_user_model().objects.get(username=self.request.user)

class ProgrammingLanguageListView(LoginRequiredMixin,ListView):
    model = ProgrammingLanguage
    context_object_name = 'languages'
    login_url = 'account_login'
    template_name = 'ProgrammingLanguage/list_pl.html'

class ProgrammingLanguageDetailView(LoginRequiredMixin,DetailView):
    model = ProgrammingLanguage
    context_object_name = 'language'
    login_url = 'account_login'
    template_name = 'ProgrammingLanguage/detail_pl.html'

class ProgrammingLanguageCreate(LoginRequiredMixin,CreateView):
    form_class = ProgrammingLanguageForm
    login_url = 'account_login'
    template_name = 'ProgrammingLanguage/create_pl.html'

class ProgrammingLanguageUpdateView(LoginRequiredMixin,UpdateView):
    model = ProgrammingLanguage
    form_class = ProgrammingLanguageForm
    context_object_name = 'language'
    success_url = reverse_lazy('languages')
    login_url = 'account_login'
    template_name = 'ProgrammingLanguage/update_pl.html'

class ProgrammingLanguageDeleteView(LoginRequiredMixin,DeleteView):
    model = ProgrammingLanguage
    success_url = reverse_lazy('languages')
    context_object_name = 'language'
    login_url = 'account_login'
    template_name = 'ProgrammingLanguage/delete_pl.html'