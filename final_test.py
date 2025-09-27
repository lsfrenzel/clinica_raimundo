import requests
import json
import time

session = requests.Session()
base_url = "http://localhost:5000"

def final_chatbot_test():
    print("🚀 === TESTE FINAL DO CHATBOT - FLUXO COMPLETO ===\n")
    
    # Passo 1: Solicitar agendamento
    print("1️⃣ Solicitando agendamento de ginecologia...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Gostaria de agendar uma consulta de ginecologia"})
    result = response.json()
    print(f"   ✓ Ação: {result['response']['action']}")
    time.sleep(1)
    
    # Passo 2: Escolher médico
    print("\n2️⃣ Escolhendo Dr. Ricardo Mendes...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Dr. Ricardo Mendes"})
    result = response.json()
    print(f"   ✓ Ação: {result['response']['action']}")
    print(f"   ✓ Dados: {len(result['response'].get('data', []))} horários disponíveis")
    time.sleep(1)
    
    # Passo 3: Escolher horário  
    print("\n3️⃣ Escolhendo horário...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "2025-09-30T09:00:00"})
    result = response.json()
    print(f"   ✓ Ação: {result['response']['action']}")
    time.sleep(1)
    
    # Passo 4: Dados pessoais
    print("\n4️⃣ Fornecendo dados pessoais...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Meu nome é Ana Teste Final, email ana.final@test.com, telefone 11999888777"})
    result = response.json()
    print(f"   ✓ Ação: {result['response']['action']}")
    time.sleep(1)
    
    # Passo 5: Confirmar agendamento
    print("\n5️⃣ Confirmando agendamento...")
    response = session.post(f"{base_url}/api/chatbot", 
                          json={"message": "Sim, confirmo e quero agendar"})
    result = response.json()
    print(f"   ✓ Ação: {result['response']['action']}")
    
    # Verificar se criou agendamento
    if result['response'].get('data') and result['response']['data'].get('success'):
        print(f"\n🎉 SUCESSO! Agendamento ID: {result['response']['data']['agendamento_id']}")
        return result['response']['data']['agendamento_id']
    else:
        print(f"\n❌ Agendamento não criado. Ação final: {result['response']['action']}")
        return None

if __name__ == "__main__":
    agendamento_id = final_chatbot_test()
    
    if agendamento_id:
        print(f"\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print(f"   📋 Agendamento criado: ID {agendamento_id}")
        print(f"   🔍 Verificar no painel admin: /admin")
    else:
        print(f"\n❌ TESTE FALHOU - Agendamento não foi criado via chatbot")
