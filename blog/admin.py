from django.contrib import admin
from .models import Profile, Tag, Post, Comment, Like


@admin.action(description='Mark selected posts as approved')
def make_approved(modeladmin, request, queryset):
	queryset.update(status='approved')


@admin.action(description='Toggle featured flag')
def toggle_featured(modeladmin, request, queryset):
	for obj in queryset:
		obj.featured = not obj.featured
		obj.save()


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'status', 'featured', 'created_at')
	list_filter = ('status', 'featured', 'author')
	search_fields = ('title', 'body')
	actions = (make_approved, toggle_featured)


admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Like)
