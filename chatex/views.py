from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ExPersona, ChatSession, ConversationMemory
from .chat_parser import parse_whatsapp_chat, extract_persona
from .response_generator import ExChatGenerator
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class UploadChatAPI(APIView):
    def post(self, request):
        try:
            # Validate input
            file = request.FILES.get('chat_file')
            user_id = request.data.get('user_id')
            ex_name = request.data.get('ex_name')
            
            if not all([file, user_id, ex_name]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            # Save and parse chat
            chat_text = file.read().decode('utf-8')
            conversations = parse_whatsapp_chat(chat_text)
            
            # Extract persona and filter messages
            persona_data = extract_persona(conversations, ex_name)
            ex_messages = [
                msg['message'] for msg in conversations 
                if msg['sender'] == ex_name and 
                len(msg['message']) > 3 and 
                not msg['message'].startswith('<Media omitted>')
            ]

            # Create embeddings with chunking
            encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            embeddings = encoder.encode(ex_messages)
            
            # Handle empty embeddings
            if len(ex_messages) == 0:
                return Response({'error': 'No valid messages found for ex'}, status=status.HTTP_400_BAD_REQUEST)

            # Create and save FAISS index
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings.astype('float32'))  # Important: use float32
            
            # Create Persona
            persona = ExPersona.objects.create(
                user_identifier=user_id,
                ex_name=ex_name,
                persona_data=persona_data,
                chat_embeddings=faiss.serialize_index(index).tobytes()
            )

            # Create initial chat session
            ChatSession.objects.create(
                user_identifier=user_id,
                ex_name=ex_name,
                persona=persona
            )

            return Response({
                'persona_id': persona.id,
                'stats': {
                    'total_messages': len(conversations),
                    'ex_messages': len(ex_messages),
                    'common_phrases': list(persona_data['common_phrases'].keys())[:5]
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatAPI(APIView):
    def post(self, request):
        try:
            persona_id = request.data.get('persona_id')
            user_input = request.data.get('message')
            
            if not persona_id or not user_input:
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            persona = ExPersona.objects.get(id=persona_id)
            generator = ExChatGenerator(persona)
            
            response = generator.generate_response(user_input)
            
            # Save conversation
            ConversationMemory.objects.create(
                persona=persona,
                user_input=user_input,
                bot_response=response
            )
            
            return Response({
                'response': response,
                'persona_traits': {
                    'common_phrases': list(persona.persona_data.get('common_phrases', {}).keys())[:5],
                    'frequent_emojis': list(set(persona.persona_data.get('emojis', [])))[:5]
                }
            })
        
        except ExPersona.DoesNotExist:
            return Response({'error': 'Persona not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)