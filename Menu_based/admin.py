from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # Import UserAdmin
from django.contrib.auth.models import User, Group  # Import User and Group models
from django.utils.translation import gettext_lazy as _
from .models import Category, FAQ

# Custom Admin Site
class MyAdminSite(admin.AdminSite):
    site_header = _("UE Chatbot")  # Change this to your project name
    site_title = _("UE Chatbot Admin")  # Change this as well
    index_title = _("Welcome to UE Chatbot Admin Panel")  # Title for the index page

# Create an instance of your custom admin site
admin_site = MyAdminSite(name='myadmin')

# Inline and ModelAdmin configurations
class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1  # Allows adding FAQs directly within Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_number', 'name', 'parent_category')
    search_fields = ('name', 'category_number', 'parent_category__name')
    list_filter = ('parent_category',)
    inlines = [FAQInline]

class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'category')
    search_fields = ('question_text', 'answer_text', 'category__name')
    list_filter = ('category',)

# Register your models with the custom admin site
admin_site.register(Category, CategoryAdmin)
admin_site.register(FAQ, FAQAdmin)

# Register the User and Group models with UserAdmin to get the default admin features
admin_site.register(User, UserAdmin)
admin_site.register(Group)
