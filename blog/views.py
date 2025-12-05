from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Post, Tag, Like
from .forms import PostForm, CommentForm, SignUpForm, LoginForm


class IsAuthorMixin(UserPassesTestMixin):
	def test_func(self):
		user = getattr(self.request, 'user', None)
		return bool(user and hasattr(user, 'profile') and user.profile.role == 'author')


class PostListView(ListView):
	model = Post
	paginate_by = 10
	template_name = 'blog/post_list.html'

	def get_queryset(self):
		qs = Post.objects.filter(status='approved')
		q = self.request.GET.get('q')
		tag = self.request.GET.get('tag')
		if q:
			qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(tags__name__icontains=q)).distinct()
		if tag:
			qs = qs.filter(tags__name=tag)
		return qs


class PostDetailView(DetailView):
	model = Post
	slug_field = 'slug'
	template_name = 'blog/post_detail.html'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['comment_form'] = CommentForm()
		ctx['liked'] = self.request.user.is_authenticated and self.object.likes.filter(user=self.request.user).exists()
		return ctx

	def post(self, request, *args, **kwargs):
		# handle comment submission
		self.object = self.get_object()
		if not request.user.is_authenticated:
			return redirect('login')
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = self.object
			comment.user = request.user
			comment.save()
		return redirect(self.object.get_absolute_url())


class PostCreateView(LoginRequiredMixin, IsAuthorMixin, CreateView):
	model = Post
	form_class = PostForm
	template_name = 'blog/post_form.html'

	def form_valid(self, form):
		# Set author before saving and handle tags
		form.instance.author = self.request.user
		form.save(commit=True, author=self.request.user)
		return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, IsAuthorMixin, UpdateView):
	model = Post
	form_class = PostForm
	template_name = 'blog/post_form.html'

	def get_object(self, queryset=None):
		obj = super().get_object(queryset)
		if obj.author != self.request.user:
			raise PermissionDenied
		return obj


class PostDeleteView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
	model = Post
	template_name = 'blog/post_confirm_delete.html'
	success_url = reverse_lazy('post_list')

	def get_object(self, queryset=None):
		obj = super().get_object(queryset)
		if obj.author != self.request.user:
			raise PermissionDenied
		return obj


class ToggleLikeView(LoginRequiredMixin, View):
	def post(self, request, slug):
		# allow toggling likes for posts regardless of approval status
		post = get_object_or_404(Post, slug=slug)
		like, created = Like.objects.get_or_create(post=post, user=request.user)
		if not created:
			like.delete()
		return redirect(post.get_absolute_url())


@method_decorator(staff_member_required, name='dispatch')
class PendingPostsView(ListView):
	template_name = 'blog/pending_posts.html'
	model = Post

	def get_queryset(self):
		return Post.objects.filter(status='pending')


@method_decorator(staff_member_required, name='dispatch')
class FeaturedDashboardView(ListView):
	template_name = 'blog/dashboard_featured.html'

	def get_queryset(self):
		return Post.objects.filter(featured=True, status='approved')


class SignUpView(View):
	def get(self, request):
		form = SignUpForm()
		return render(request, 'blog/signup.html', {'form': form})

	def post(self, request):
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('post_list')
		return render(request, 'blog/signup.html', {'form': form})


class LoginView(View):
	def get(self, request):
		form = LoginForm()
		return render(request, 'blog/login.html', {'form': form})

	def post(self, request):
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('post_list')
			else:
				form.add_error(None, 'Invalid username or password')
		return render(request, 'blog/login.html', {'form': form})


class LogoutView(View):
	def get(self, request):
		logout(request)
		return redirect('login')

