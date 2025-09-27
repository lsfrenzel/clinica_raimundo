import requests
import json
import time

# Configurar sessão para manter cookies
session = requests.Session()
base_url = "http://localhost:5000"

def test_complete_chatbot_appointment():
    print("=== Teste Completo de Agendamento via Chatbot ===\n")
    
    try:
        # Passo 1: Iniciar conversa
        print("1. Iniciando conversa...")
        response = session.post(f"{base_url}/api/chatbot", 
                              json={"message": "Olá, gostaria de agendar uma consulta de ginecologia"})
        result = response.json()
        print(f"✓ Ação: {result['response']['action']}")
        print(f"  Mensagem: {result['response']['message'][:80]}...")
        time.sleep(1)
        
        # Passo 2: Escolher médico
        print("\n2. Escolhendo médico...")
        response = session.post(f"{base_url}/api/chatbot", 
                              json={"message": "Dr. Ricardo Mendes"})
        result = response.json()
        print(f"✓ Ação: {result['response']['action']}")
        print(f"  Dados: {len(result['response'].get('data', []))} itens retornados")
        time.sleep(1)
        
        # Passo 3: Escolher horário disponível
        print("\n3. Escolhendo horário...")
        response = session.post(f"{base_url}/api/chatbot", 
                              json={"message": "2025-09-29T14:00:00"})
        result = response.json()
        print(f"✓ Ação: {result['response']['action']}")
        print(f"  Mensagem: {result['response']['message'][:80]}...")
        time.sleep(1)
        
        # Passo 4: Fornecer dados pessoais
        print("\n4. Fornecendo dados pessoais...")
        response = session.post(f"{base_url}/api/chatbot", 
                              json={"message": "Meu nome é Maria Silva Teste, email maria.teste@clinica.com, telefone 11987654321"})
        result = response.json()
        print(f"✓ Ação: {result['response']['action']}")
        print(f"  Mensagem: {result['response']['message'][:80]}...")
        time.sleep(1)
        
        # Passo 5: Confirmar agendamento
        print("\n5. Confirmando agendamento...")
        response = session.post(f"{base_url}/api/chatbot", 
                              json={"message": "Sim, confirmo o agendamento"})
        result = response.json()
        print(f"✓ Ação: {result['response']['action']}")
        print(f"  Mensagem: {result['response']['message'][:80]}...")
        
        # Verificar se tem dados de sucesso
        if result['response'].get('data') and result['response']['data'].get('success'):
            print(f"\n🎉 SUCESSO! Agendamento criado com ID: {result['response']['data'].get('agendamento_id')}")
            return True
        else:
            print(f"\n❌ Agendamento não foi criado. Dados: {result['response'].get('data')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_chatbot_appointment()
    if success:
        print("\n=== Teste concluído com sucesso! ===")
    else:
        print("\n=== Teste falhou ===")
