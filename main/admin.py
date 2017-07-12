from django.contrib import admin
from .models import *

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'post_by', 'comment_count')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_by', 'comment_made', 'post')
# Minimal registration of Models.
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Section)
admin.site.register(UserExtend)
admin.site.register(Attachment)
#admin.site.register(Like)
#admin.site.register(Quote)