from django.db import models
from django.utils import timezone

class ChatSession(models.Model):
    user_identifier = models.CharField(max_length=100)
    ex_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    persona = models.ForeignKey('ExPersona', on_delete=models.CASCADE, null=True)

class ExPersona(models.Model):
    user_identifier = models.CharField(max_length=100)
    ex_name = models.CharField(max_length=100)
    persona_data = models.JSONField()
    chat_embeddings = models.BinaryField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ConversationMemory(models.Model):
    persona = models.ForeignKey(ExPersona, on_delete=models.CASCADE)
    user_input = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)