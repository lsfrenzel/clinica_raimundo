#!/usr/bin/env python3
"""
Script de migration automático para Railway/Produção
Inicializa, cria e aplica migrations + garante que admin existe
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from extensions import db
from models import User

def run_migrations():
    """Executa migrations automaticamente"""
    
    app = create_app()
    
    print("🚀 SISTEMA DE MIGRATION AUTOMÁTICO")
    print("=" * 60)
    
    with app.app_context():
        # 1. Criar todas as tabelas
        print("\n📦 Criando/atualizando tabelas no banco...")
        try:
            db.create_all()
            print("✅ Tabelas criadas/atualizadas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False
        
        # 2. Verificar/criar usuário admin
        print("\n🔑 Verificando usuário administrador...")
        admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
        
        if not admin:
            print("   Criando usuário admin...")
            admin = User()
            admin.nome = "Administrador"
            admin.email = "admin@clinicadrraimundonunes.com.br"
            admin.telefone = "(11) 99999-9999"
            admin.role = "admin"
            admin.ativo = True
            admin.set_password("admin123")
            
            try:
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin criado com sucesso!")
                print(f"   Email: {admin.email}")
                print(f"   Senha: admin123")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao criar admin: {e}")
                return False
        else:
            print(f"✅ Admin já existe: {admin.email}")
            
            # Garantir que a senha está funcionando
            if not admin.check_password("admin123"):
                print("   ⚠️  Resetando senha do admin...")
                admin.set_password("admin123")
                try:
                    db.session.commit()
                    print("   ✅ Senha resetada com sucesso!")
                except Exception as e:
                    db.session.rollback()
                    print(f"   ❌ Erro ao resetar senha: {e}")
            
            # Garantir que admin está ativo
            if not admin.ativo:
                print("   ⚠️  Ativando admin...")
                admin.ativo = True
                try:
                    db.session.commit()
                    print("   ✅ Admin ativado!")
                except Exception as e:
                    db.session.rollback()
                    print(f"   ❌ Erro ao ativar admin: {e}")
        
        # 3. Resumo
        print("\n📊 RESUMO:")
        total_users = User.query.count()
        total_admins = User.query.filter_by(role='admin').count()
        print(f"   Total de usuários: {total_users}")
        print(f"   Administradores: {total_admins}")
        
        print("\n✨ Migration completa!")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
