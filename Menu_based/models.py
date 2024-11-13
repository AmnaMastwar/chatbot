from django.db import models

# Create your models here.
# faq/models.py
class Category(models.Model):
    category_number = models.CharField(max_length=50, primary_key=True)  # e.g., "1", "1.1", "1.1.1"
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name
# model for FAQ
class FAQ(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='faqs')
    question_text = models.TextField()
    answer_text = models.TextField()

    def __str__(self):
        return self.question_text


