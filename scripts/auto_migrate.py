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
        
        # 3. Criar especialidades básicas (se não existirem)
        print("\n📝 Verificando especialidades...")
        from models import Especialidade, Medico, Agenda
        from datetime import timedelta, time
        
        especialidades_basicas = [
            {'nome': 'DIU e Implanon', 'duracao_padrao': 45},
            {'nome': 'Pré-Natal de Alto Risco', 'duracao_padrao': 60},
            {'nome': 'Mastologia', 'duracao_padrao': 30},
            {'nome': 'Uroginecologia', 'duracao_padrao': 45},
            {'nome': 'Climatério e Menopausa', 'duracao_padrao': 30},
        ]
        
        for esp_data in especialidades_basicas:
            esp = Especialidade.query.filter_by(nome=esp_data['nome']).first()
            if not esp:
                esp = Especialidade(**esp_data)
                db.session.add(esp)
                print(f"   ✅ Criada: {esp_data['nome']}")
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"   ⚠️  Erro ao criar especialidades: {e}")
        
        # 4. Resumo
        print("\n📊 RESUMO:")
        total_users = User.query.count()
        total_admins = User.query.filter_by(role='admin').count()
        total_especialidades = Especialidade.query.count()
        print(f"   Total de usuários: {total_users}")
        print(f"   Administradores: {total_admins}")
        print(f"   Especialidades: {total_especialidades}")
        
        print("\n✨ Migration completa!")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
