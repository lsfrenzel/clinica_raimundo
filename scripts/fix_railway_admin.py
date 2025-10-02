#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problemas de login do admin no Railway
Uso: python scripts/fix_railway_admin.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from extensions import db
from models import User

def diagnose_and_fix():
    """Diagnostica e corrige problemas de login do admin"""
    
    app = create_app()
    with app.app_context():
        print("🔍 DIAGNÓSTICO DO BANCO DE DADOS RAILWAY")
        print("=" * 60)
        
        # Verificar conexão com banco
        try:
            db.engine.connect()
            print("✅ Conexão com banco de dados: OK")
            # Mascarar credenciais da URL para segurança
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')
            if db_url and db_url != 'N/A':
                # Mostrar apenas o protocolo e host (sem credenciais)
                if '@' in db_url:
                    protocol = db_url.split('://')[0] if '://' in db_url else 'unknown'
                    host_part = db_url.split('@')[1] if '@' in db_url else 'unknown'
                    print(f"   Protocolo: {protocol}://")
                    print(f"   Host: {host_part.split('/')[0] if '/' in host_part else host_part}")
                else:
                    print(f"   URL: {db_url[:20]}... (mascarada)")
            else:
                print(f"   Database URL: {db_url}")
        except Exception as e:
            print(f"❌ Erro de conexão com banco: {e}")
            return False
        
        # Verificar tabelas
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Tabelas encontradas: {len(tables)}")
            if 'users' in tables:
                print("   ✓ Tabela 'users' existe")
            else:
                print("   ✗ Tabela 'users' NÃO existe")
                print("   ⚠️  Execute: flask db upgrade")
                return False
        except Exception as e:
            print(f"❌ Erro ao verificar tabelas: {e}")
            return False
        
        # Verificar usuários
        try:
            total_users = User.query.count()
            print(f"📊 Total de usuários no banco: {total_users}")
            
            if total_users == 0:
                print("⚠️  Banco vazio! É necessário popular o banco de dados.")
                print("   Execute: python scripts/seed_data.py")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao contar usuários: {e}")
            return False
        
        # Verificar admin
        print("\n🔍 VERIFICANDO USUÁRIO ADMIN")
        print("=" * 60)
        
        admin_emails = [
            'admin@clinicadrraimundonunes.com.br',
            'admin@clinica.com.br',
            'admin@admin.com'
        ]
        
        admin_user = None
        for email in admin_emails:
            admin_user = User.query.filter_by(email=email).first()
            if admin_user:
                print(f"✅ Admin encontrado: {email}")
                break
        
        if not admin_user:
            print("❌ Usuário admin NÃO encontrado!")
            print("\n📝 Criando usuário admin...")
            
            admin_user = User()
            admin_user.nome = "Administrador"
            admin_user.email = "admin@clinicadrraimundonunes.com.br"
            admin_user.telefone = "(11) 99999-9999"
            admin_user.role = "admin"
            admin_user.ativo = True
            admin_user.set_password("admin123")
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin criado com sucesso!")
            print(f"   Email: {admin_user.email}")
            print(f"   Senha: admin123")
            return True
        
        # Verificar dados do admin
        print(f"\n📋 DADOS DO ADMIN:")
        print(f"   ID: {admin_user.id}")
        print(f"   Nome: {admin_user.nome}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   Ativo: {admin_user.ativo}")
        print(f"   Tem senha: {'Sim' if admin_user.senha_hash else 'Não'}")
        
        if not admin_user.ativo:
            print("\n⚠️  Admin está INATIVO! Ativando...")
            admin_user.ativo = True
            db.session.commit()
            print("✅ Admin ativado!")
        
        # Testar senha
        print("\n🔐 TESTANDO SENHA DO ADMIN")
        print("=" * 60)
        
        test_password = "admin123"
        try:
            if admin_user.check_password(test_password):
                print(f"✅ Senha '{test_password}' está CORRETA!")
                print("\n✨ DIAGNÓSTICO COMPLETO - TUDO OK!")
                print("\n🔑 CREDENCIAIS:")
                print(f"   Email: {admin_user.email}")
                print(f"   Senha: {test_password}")
                return True
            else:
                print(f"❌ Senha '{test_password}' está INCORRETA!")
                print("\n🔧 RESETANDO SENHA...")
                
                admin_user.set_password(test_password)
                db.session.commit()
                
                # Verificar novamente
                if admin_user.check_password(test_password):
                    print(f"✅ Senha resetada com sucesso para: {test_password}")
                    print("\n✨ CORREÇÃO COMPLETA!")
                    print("\n🔑 CREDENCIAIS:")
                    print(f"   Email: {admin_user.email}")
                    print(f"   Senha: {test_password}")
                    return True
                else:
                    print("❌ ERRO: Não foi possível resetar a senha!")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro ao testar senha: {e}")
            print("\n🔧 Tentando resetar senha...")
            try:
                admin_user.set_password(test_password)
                db.session.commit()
                print(f"✅ Senha resetada para: {test_password}")
                return True
            except Exception as e2:
                print(f"❌ Erro ao resetar senha: {e2}")
                return False

if __name__ == '__main__':
    print("🚀 Iniciando diagnóstico e correção...\n")
    success = diagnose_and_fix()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCESSO! O login do admin deve funcionar agora.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ FALHA! Verifique os erros acima e tente novamente.")
        print("=" * 60)
        sys.exit(1)
