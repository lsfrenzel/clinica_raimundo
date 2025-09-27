import sys
sys.path.append('.')
from main import app
from chatbot_service import ChatbotService
import json

# Testar criação direta de agendamento com contexto da aplicação
with app.app_context():
    chatbot = ChatbotService()
    
    # Dados para teste de agendamento
    booking_data = {
        'medico_id': 3,  # Dr. Ricardo Mendes
        'especialidade_id': 7,  # PTGI
        'data_hora': '2025-09-30T15:00:00',
        'nome': 'Teste Chatbot Direto',
        'email': 'teste.chatbot@email.com',
        'telefone': '11999887766'
    }
    
    context = {
        'authenticated': False,
        'user_name': 'Visitante'
    }
    
    print("=== Teste Direto de Criação de Agendamento ===")
    print(f"Dados do agendamento: {json.dumps(booking_data, indent=2, ensure_ascii=False)}")
    
    # Tentar criar agendamento
    result = chatbot.create_appointment(booking_data, context)
    print(f"\nResultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('success'):
        print(f"\n✅ SUCESSO! Agendamento criado com ID: {result.get('agendamento_id')}")
    else:
        print(f"\n❌ FALHA: {result.get('error')}")
