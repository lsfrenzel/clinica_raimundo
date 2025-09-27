import requests
import json

# Configurar sessão para manter cookies
session = requests.Session()
base_url = "http://localhost:5000"

def test_chatbot_flow():
    print("=== Teste Completo do Chatbot ===\n")
    
    # Passo 1: Iniciar conversa
    print("1. Iniciando conversa...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Olá, gostaria de agendar uma consulta"})
    result = response.json()
    print(f"Resposta: {result['response']['message'][:100]}...")
    print(f"Ação: {result['response']['action']}\n")
    
    # Passo 2: Solicitar ginecologia
    print("2. Solicitando ginecologia...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Ginecologia"})
    result = response.json()
    print(f"Resposta: {result['response']['message'][:100]}...")
    print(f"Ação: {result['response']['action']}")
    print(f"Dados: {len(result['response']['data'])} médicos encontrados\n")
    
    # Passo 3: Escolher médico
    print("3. Escolhendo Dr. Ricardo Mendes...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Dr. Ricardo Mendes"})
    result = response.json()
    print(f"Resposta: {result['response']['message'][:100]}...")
    print(f"Ação: {result['response']['action']}")
    print(f"Dados: {len(result['response'].get('data', []))} horários encontrados\n")
    
    # Passo 4: Escolher horário
    print("4. Escolhendo horário...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "29 de setembro às 14:00"})
    result = response.json()
    print(f"Resposta: {result['response']['message'][:100]}...")
    print(f"Ação: {result['response']['action']}\n")
    
    # Passo 5: Fornecer dados pessoais
    print("5. Fornecendo dados pessoais...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Meu nome é Maria Silva, email maria@email.com, telefone 11999999999"})
    result = response.json()
    print(f"Resposta: {result['response']['message'][:100]}...")
    print(f"Ação: {result['response']['action']}\n")
    
    return result

if __name__ == "__main__":
    test_chatbot_flow()
