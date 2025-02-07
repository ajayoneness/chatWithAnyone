from django.contrib import admin
from .models import ChatSession,ExPersona,ConversationMemory


admin.site.register(ChatSession)
admin.site.register(ExPersona)
admin.site.register(ConversationMemory)
