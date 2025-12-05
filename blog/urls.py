from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView, PostUpdateView,
    ToggleLikeView, PendingPostsView, FeaturedDashboardView,
    SignUpView, LoginView, LogoutView, PostDeleteView,
)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<slug:slug>/like/', ToggleLikeView.as_view(), name='post_like'),
    path('admin/pending/', PendingPostsView.as_view(), name='pending_posts'),
    path('admin/featured/', FeaturedDashboardView.as_view(), name='featured_dashboard'),
]

