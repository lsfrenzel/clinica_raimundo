import sys
sys.path.append('.')
import json

# Testar o contexto que está sendo passado
test_context = {
    'especialidade_id': 7,
    'medico_id': 3,
    'datetime_slot': '2025-09-29T14:00:00',
    'authenticated': False,
    'user_name': 'Visitante'
}

print("Contexto de teste:")
print(json.dumps(test_context, indent=2, ensure_ascii=False))

# Verificar se o contexto está sendo formatado corretamente
context_info = f"\n\nContexto da conversa: {json.dumps(test_context, ensure_ascii=False)}"
print("\nContexto formatado para Gemini:")
print(context_info)
