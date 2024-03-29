from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail.message import EmailMultiAlternatives
from django.template import loader, Context
from django.contrib.auth import get_user_model

from taggit.models import Tag

from .models import Problem
from .forms import ProblemModelForm
from comments.models import Comment
from comments.forms import CommentForm
from django.conf import settings

class ProblemListView(LoginRequiredMixin,ListView):
    model = Problem
    context_object_name = 'problems'
    login_url = 'account_login'
    template_name = 'Problems/list_problems.html'

    def get_queryset(self):
        print(settings.ENVIRONMENT)
        return Problem.objects.filter(status='published').order_by('-published')
    

class ProblemCreateView(LoginRequiredMixin,CreateView):
    form_class = ProblemModelForm
    login_url = 'account_login'
    template_name = 'Problems/create_problem.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ProbelmDetailView(LoginRequiredMixin,DetailView):
    template_name = 'Problems/detail_problem.html'
    login_url = 'account_login'

    def get_object(self, **kwargs):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Problem, id=id_)
    
    def get_context_data(self, **kwargs):
        problem_object = self.get_object()
        kwargs['problem'] = problem_object
        kwargs['comments'] = Comment.objects.filter(problem=problem_object)
        if 'comment_form' not in kwargs:
            kwargs['comment_form'] = CommentForm()
        return kwargs

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'body' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = Comment()
                new_comment.problem = self.get_object()
                new_comment.commenter = self.request.user
                new_comment.body = comment_form.cleaned_data['body']
                new_comment.save()

                from_email = 'mhisajib@myseneca.ca'
                text_template = loader.get_template('emails/comment_notification.txt')
                html_template = loader.get_template('emails/comment_notification.html')
                to_users = Comment.objects.filter(problem=new_comment.problem).values_list('problem__author', flat=True).distinct()
                print(to_users)
                for receiver in to_users:
                    subject = f'New Comment in { new_comment.problem.title }'
                    receiver = get_user_model().objects.get(id=receiver)
                    context = { 'new_comment': new_comment, 'receiver': receiver }
                    text_content = text_template.render(context)
                    html_content = html_template.render(context)
                    email = EmailMultiAlternatives(subject, text_content, from_email, [receiver.email])
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                return HttpResponseRedirect(reverse_lazy('detail_problem', kwargs={'pk': self.get_object().id}))
            else:
                ctxt['comment_form'] = comment_form
        return render(request, self.template_name, self.get_context_data(**ctxt))
    


class ProblemUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Problem
    form_class = ProblemModelForm
    login_url = 'account_login'
    template_name = 'Problems/update_problem.html'

    def test_func(self):
        problem = self.get_object()
        return problem.author == self.request.user


class ProblemDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Problem
    success_url = reverse_lazy('list_problems')
    login_url = 'account_login'
    template_name = 'Problems/delete_problem.html'


    def test_func(self):
        problem = self.get_object()
        return problem.author == self.request.user

class TaggedItemListView(LoginRequiredMixin,ListView):
    context_object_name = 'problems'
    login_url = 'account_login'
    template_name = 'Problems/list_problems.html'

    def get_queryset(self):
        tag = Tag.objects.get(slug=self.kwargs['slug'])
        problems = Problem.objects.filter(tags__name__icontains=tag).filter(status='published')
        return problems

    def get_context_data(self, **kwargs):
        context = super(TaggedItemListView, self).get_context_data(**kwargs)
        context["tag"] = Tag.objects.get(slug=self.kwargs['slug'])
        return context

class ProblemSearchListView(LoginRequiredMixin, ListView):
    context_object_name = 'problems'
    login_url = 'account_login'
    template_name = 'Problems/list_problems.html'

    def get_queryset(self):
        query_string = self.request.GET['query']
        problems = Problem.objects.filter(title__icontains=query_string)
        return problems

    def get_context_data(self, **kwargs):
        context = super(ProblemSearchListView, self).get_context_data(**kwargs)
        context["query"] = self.request.GET['query']
        return context
    