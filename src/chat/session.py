from google.genai.types import GenerateContentConfig


def initialize_chat_session(client, model_config):
    """Initialize a new chat session"""
    config = GenerateContentConfig(
        temperature=model_config['temperature'],
        top_k=model_config['top_k'],
        top_p=model_config['top_p']
    )
    
    return client.chats.create(
        model=model_config['model'],
        config=config
    )