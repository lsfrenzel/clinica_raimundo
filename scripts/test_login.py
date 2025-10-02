#!/usr/bin/env python3
"""
Script para testar o sistema de login
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from models import User

def test_login():
    """Testa o sistema de login"""
    
    app = create_app()
    
    print("🧪 TESTE DE LOGIN")
    print("=" * 60)
    
    with app.app_context():
        # Buscar admin
        admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        
        if not admin:
            print("❌ Admin não encontrado no banco!")
            print("   Execute: python scripts/auto_migrate.py")
            return False
        
        print(f"✅ Admin encontrado: {admin.email}")
        print(f"   ID: {admin.id}")
        print(f"   Nome: {admin.nome}")
        print(f"   Role: {admin.role}")
        print(f"   Ativo: {admin.ativo}")
        print(f"   Senha hash: {admin.senha_hash[:30] if admin.senha_hash else 'None'}...")
        
        # Testar várias senhas
        test_passwords = ['admin123', 'Admin123', 'ADMIN123', 'admin']
        
        print("\n🔐 TESTANDO SENHAS:")
        for pwd in test_passwords:
            try:
                result = admin.check_password(pwd)
                status = "✅ CORRETA" if result else "❌ Incorreta"
                print(f"   '{pwd}': {status}")
                if result:
                    print(f"\n✨ SENHA FUNCIONANDO: '{pwd}'")
                    print("\n🔑 USE ESTAS CREDENCIAIS:")
                    print(f"   Email: {admin.email}")
                    print(f"   Senha: {pwd}")
                    return True
            except Exception as e:
                print(f"   '{pwd}': ❌ Erro - {e}")
        
        print("\n⚠️  NENHUMA SENHA FUNCIONOU!")
        print("\n🔧 Resetando senha para 'admin123'...")
        
        try:
            admin.set_password('admin123')
            from extensions import db
            db.session.commit()
            
            # Testar novamente
            if admin.check_password('admin123'):
                print("✅ Senha resetada com sucesso!")
                print("\n🔑 USE ESTAS CREDENCIAIS:")
                print(f"   Email: {admin.email}")
                print(f"   Senha: admin123")
                return True
            else:
                print("❌ Erro: senha resetada mas ainda não funciona!")
                return False
        except Exception as e:
            print(f"❌ Erro ao resetar senha: {e}")
            return False

if __name__ == '__main__':
    success = test_login()
    print("\n" + "=" * 60)
    sys.exit(0 if success else 1)
