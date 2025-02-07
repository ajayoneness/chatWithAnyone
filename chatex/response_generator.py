from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re

class ExChatGenerator:
    def __init__(self, persona):
        self.persona = persona
        self.retriever = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.generator_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.generator_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        self.generator_tokenizer.pad_token = self.generator_tokenizer.eos_token
        
        # Initialize FAISS index
        self.index = self._initialize_faiss_index()
        self.historical_chats = self._load_chat_history()

    def _initialize_faiss_index(self):
        try:
            if self.persona.chat_embeddings:
                return faiss.deserialize_index(
                    np.frombuffer(self.persona.chat_embeddings, dtype=np.float32)
                )
            return None
        except Exception as e:
            print(f"Error initializing FAISS index: {e}")
            return None

    def _load_chat_history(self):
        try:
            return [
                {"user": msg.user_input, "ex": msg.bot_response}
                for msg in ConversationMemory.objects.filter(persona=self.persona)
            ]
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return []

    def _truncate_prompt(self, prompt, max_tokens=900):
        tokens = self.generator_tokenizer.tokenize(prompt)
        if len(tokens) > max_tokens:
            tokens = tokens[-max_tokens:]
        return self.generator_tokenizer.convert_tokens_to_string(tokens)

    def generate_response(self, user_input):
        try:
            # Construct prompt
            prompt = f"[Ex Name: {self.persona.ex_name}]\n"
            prompt += f"[Style: {', '.join(self.persona.persona_data.get('common_phrases', []))}]\n"
            prompt += f"[Common Emojis: {''.join(set(self.persona.persona_data.get('emojis', [])))}]\n"
            
            # Add context from FAISS index
            if self.index and self.index.ntotal > 0:
                query_embedding = self.retriever.encode([user_input])
                _, indices = self.index.search(query_embedding, min(3, self.index.ntotal))
                for idx in indices[0]:
                    if idx < len(self.historical_chats):
                        chat = self.historical_chats[idx]
                        prompt += f"User: {chat['user']}\nEx: {chat['ex']}\n"

            prompt += f"User: {user_input}\nEx:"
            
            # Truncate prompt to model's max length
            truncated_prompt = self._truncate_prompt(prompt)
            
            # Tokenize with attention mask
            inputs = self.generator_tokenizer(
                truncated_prompt,
                return_tensors='pt',
                max_length=1024,
                truncation=True
            )

            # Generate response
            outputs = self.generator_model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=100,
                top_p=0.95,
                temperature=0.7,
                repetition_penalty=1.2,
                pad_token_id=self.generator_tokenizer.eos_token_id
            )

            # Decode and clean response
            full_response = self.generator_tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = full_response.split("Ex:")[-1].strip()
            response = re.sub(r'\[.*?\]', '', response)  # Remove any remaining metadata tags
            
            return response

        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm having trouble responding right now. Please try again later."