from django.contrib import admin

# Register your models here.

from .models import Notice

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'visible', 'expires', 'target', 'user', 'timestamp')
    readonly_fields = ['user']
    list_filter = ('visible', 'user', 'target', 'timestamp', 'priority')
    list_select_related = ('user', 'target')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Notice, NoticeAdmin)
