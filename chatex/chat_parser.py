# chat_parser.py (updated)
import re
from datetime import datetime
from collections import defaultdict

def parse_whatsapp_chat(chat_text):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2} [ap]m) - (.*?): (.*)'
    conversations = []
    lines = chat_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(pattern, line)
        if match:
            date_str, time_str, sender, message = match.groups()
            try:
                timestamp = datetime.strptime(
                    f'{date_str} {time_str}', 
                    '%d/%m/%y %I:%M %p'
                )
                conversations.append({
                    'sender': sender.strip(),
                    'message': message.strip(),
                    'timestamp': timestamp
                })
            except ValueError:
                continue
                
    return conversations

def extract_persona(conversations, ex_name):
    persona = {
        'common_phrases': defaultdict(int),
        'emojis': [],
        'response_time_avg': 0,
        'unique_words': set(),
        'message_lengths': []
    }
    
    prev_timestamp = None
    ex_messages = [msg for msg in conversations if msg['sender'] == ex_name]
    
    for msg in ex_messages:
        # Phrase analysis
        words = msg['message'].split()
        persona['unique_words'].update(words)
        persona['message_lengths'].append(len(words))
        
        # Extract 3-word phrases
        if len(words) >= 3:
            for i in range(len(words)-2):
                phrase = ' '.join(words[i:i+3])
                persona['common_phrases'][phrase] += 1
                
        # Emoji extraction
        persona['emojis'].extend(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]', msg['message']))
        
        # Response time calculation
        if prev_timestamp:
            time_diff = (msg['timestamp'] - prev_timestamp).total_seconds()
            if time_diff > 0:  # Only count valid time differences
                persona['response_time_avg'] += time_diff
        prev_timestamp = msg['timestamp']
    
    # Calculate averages
    if len(ex_messages) > 0:
        persona['response_time_avg'] = persona['response_time_avg'] / len(ex_messages)
        persona['avg_message_length'] = sum(persona['message_lengths']) / len(ex_messages)
        
    # Keep only top 50 phrases
    persona['common_phrases'] = dict(sorted(
        persona['common_phrases'].items(),
        key=lambda item: item[1],
        reverse=True
    )[:50])
    
    return persona