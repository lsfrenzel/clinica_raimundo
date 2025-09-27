import requests
import json

# Configurar sessão para manter cookies
session = requests.Session()
base_url = "http://localhost:5000"

def debug_session_storage():
    print("=== Debug de Armazenamento de Sessão ===\n")
    
    # Passo 1: Iniciar conversa e verificar resposta
    print("1. Iniciando conversa...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Gostaria de agendar uma consulta de ginecologia"})
    result = response.json()
    print(f"Ação: {result['response']['action']}")
    print(f"Headers de resposta: {dict(response.headers)}")
    
    # Extrair cookies da sessão
    print(f"Cookies atuais: {session.cookies}")
    print()
    
    # Passo 2: Segunda mensagem
    print("2. Enviando segunda mensagem...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Dr. Ricardo Mendes"})
    result = response.json()
    print(f"Ação: {result['response']['action']}")
    print(f"Dados: {len(result['response'].get('data', []))} itens")
    print(f"Cookies atuais: {session.cookies}")
    print()
    
    # Passo 3: Terceira mensagem
    print("3. Enviando terceira mensagem...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Segunda-feira às 14:00"})
    result = response.json()
    print(f"Ação: {result['response']['action']}")
    print(f"Mensagem: {result['response']['message'][:150]}...")
    
    return result

if __name__ == "__main__":
    debug_session_storage()
