#!/usr/bin/env python3
"""
Script para corrigir agendamentos criados via API/chatbot que foram salvos
em horário de Brasília ao invés de UTC.

Este script deve ser executado no ambiente Railway para corrigir os dados existentes.

Uso:
    python scripts/fix_timezone_agendamentos.py [--dry-run]
"""
import sys
import os
from datetime import timedelta

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_timezone_agendamentos(dry_run=True, cutoff_date=None):
    """
    Corrige agendamentos criados via API/chatbot convertendo de Brasília para UTC.
    
    IMPORTANTE: Apenas corrige agendamentos criados ANTES da data de corte (cutoff_date)
    para evitar corrigir agendamentos duas vezes.
    
    Args:
        dry_run: Se True, apenas mostra o que seria alterado sem fazer mudanças
        cutoff_date: Data limite (apenas agendamentos criados antes serão corrigidos)
                     OBRIGATÓRIO - deve ser a data/hora do deploy do código corrigido
    
    Raises:
        ValueError: Se cutoff_date não for fornecida
    """
    from main import app
    from models import Agendamento
    from extensions import db
    from datetime import datetime
    
    # PROTEÇÃO CRÍTICA: cutoff_date é obrigatória
    if cutoff_date is None:
        raise ValueError(
            "❌ ERRO: cutoff_date é obrigatória!\n"
            "\n"
            "A data de corte deve ser a data/hora do deploy do código corrigido em UTC.\n"
            "Isso previne correções duplas em agendamentos criados após o deploy.\n"
            "\n"
            "Exemplo de uso:\n"
            "  from datetime import datetime\n"
            "  cutoff = datetime.strptime('2025-10-21 22:30:00', '%Y-%m-%d %H:%M:%S')\n"
            "  fix_timezone_agendamentos(dry_run=True, cutoff_date=cutoff)\n"
        )
    
    with app.app_context():
        print("=" * 80)
        print("CORREÇÃO DE TIMEZONE DE AGENDAMENTOS")
        print("=" * 80)
        print()
        
        print(f"⚠️  Data de corte: {cutoff_date} UTC")
        print(f"   Apenas agendamentos criados ANTES desta data serão corrigidos")
        print()
        
        # Buscar agendamentos criados via API ou chatbot ANTES da data de corte
        agendamentos = Agendamento.query.filter(
            Agendamento.origem.in_(['mobile', 'chatbot']),
            Agendamento.created_at < cutoff_date
        ).all()
        
        print(f"Encontrados {len(agendamentos)} agendamentos criados via API/chatbot antes de {cutoff_date}")
        print()
        
        if len(agendamentos) == 0:
            print("✅ Nenhum agendamento para corrigir!")
            return
        
        # Contador de correções
        corrigidos = 0
        pulados = 0
        ja_corretos = 0
        
        for agendamento in agendamentos:
            inicio_original = agendamento.inicio
            fim_original = agendamento.fim
            
            # VERIFICAÇÃO DE SEGURANÇA: Detectar se já está em UTC
            # Se o horário de início é no passado distante (mais de 3 horas atrás do created_at),
            # provavelmente já está em UTC
            if agendamento.created_at and inicio_original < agendamento.created_at:
                print(f"Agendamento ID {agendamento.id}:")
                print(f"  ⚠️  PULADO - Horário de início é anterior à criação (já pode estar em UTC)")
                print(f"  Criado em: {agendamento.created_at}")
                print(f"  Início: {inicio_original}")
                print()
                ja_corretos += 1
                continue
            
            # VERIFICAÇÃO DE SEGURANÇA 2: Se observacoes contém "TIMEZONE_CORRIGIDO"
            if agendamento.observacoes and "TIMEZONE_CORRIGIDO" in agendamento.observacoes:
                print(f"Agendamento ID {agendamento.id}:")
                print(f"  ℹ️  JÁ CORRIGIDO - Marcado como corrigido anteriormente")
                print()
                ja_corretos += 1
                continue
            
            # Adicionar 3 horas para converter de Brasília para UTC
            inicio_utc = inicio_original + timedelta(hours=3)
            fim_utc = fim_original + timedelta(hours=3)
            
            print(f"Agendamento ID {agendamento.id}:")
            print(f"  Paciente: {agendamento.nome_paciente}")
            print(f"  Médico ID: {agendamento.medico_id}")
            print(f"  Origem: {agendamento.origem}")
            print(f"  Criado em: {agendamento.created_at}")
            print(f"  Início (atual Brasília): {inicio_original}")
            print(f"  Início (corrigido UTC):  {inicio_utc}")
            print(f"  Fim (atual Brasília):    {fim_original}")
            print(f"  Fim (corrigido UTC):     {fim_utc}")
            
            if dry_run:
                print(f"  🔍 DRY RUN - Não foi alterado")
                pulados += 1
            else:
                # Aplicar correção
                agendamento.inicio = inicio_utc
                agendamento.fim = fim_utc
                
                # Marcar como corrigido nas observações
                if agendamento.observacoes:
                    agendamento.observacoes += " | TIMEZONE_CORRIGIDO"
                else:
                    agendamento.observacoes = "TIMEZONE_CORRIGIDO"
                
                print(f"  ✅ CORRIGIDO e MARCADO")
                corrigidos += 1
            
            print()
        
        if not dry_run:
            # Commit das mudanças
            try:
                db.session.commit()
                print("=" * 80)
                print(f"✅ {corrigidos} agendamentos corrigidos com sucesso!")
                print(f"ℹ️  {ja_corretos} agendamentos já estavam corretos (pulados)")
                print("=" * 80)
            except Exception as e:
                db.session.rollback()
                print("=" * 80)
                print(f"❌ ERRO ao salvar mudanças: {e}")
                print("=" * 80)
                raise
        else:
            print("=" * 80)
            print(f"🔍 DRY RUN completado:")
            print(f"   - {pulados} agendamentos SERIAM corrigidos")
            print(f"   - {ja_corretos} agendamentos já corretos (pulados)")
            print()
            print("Execute novamente com --apply para aplicar as correções")
            print("=" * 80)

if __name__ == '__main__':
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description='Corrige timezone de agendamentos criados via API/chatbot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
IMPORTANTE: Este script deve ser executado APENAS UMA VEZ após o deploy da correção do código.

Você DEVE especificar a data/hora do deploy usando --cutoff-date para garantir que
apenas agendamentos criados ANTES da correção do código sejam ajustados.

Exemplo:
  # Se você fez deploy em 21 de outubro de 2025 às 22:30 UTC
  python scripts/fix_timezone_agendamentos.py --cutoff-date "2025-10-21 22:30:00" --dry-run
  
  # Depois de verificar que está correto
  python scripts/fix_timezone_agendamentos.py --cutoff-date "2025-10-21 22:30:00" --apply
"""
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostra o que seria alterado sem fazer mudanças (SEMPRE use isto primeiro!)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Aplica as correções no banco de dados'
    )
    parser.add_argument(
        '--cutoff-date',
        type=str,
        required=True,
        help='Data/hora limite em UTC (formato: "YYYY-MM-DD HH:MM:SS"). Apenas agendamentos criados ANTES desta data serão corrigidos. OBRIGATÓRIO: use a data/hora do seu deploy do código corrigido.'
    )
    
    args = parser.parse_args()
    
    # Se nem dry-run nem apply foram especificados, usar dry-run por padrão
    dry_run = not args.apply
    
    # Parsear cutoff_date (agora obrigatória)
    try:
        cutoff_date = datetime.strptime(args.cutoff_date, "%Y-%m-%d %H:%M:%S")
        print(f"📅 Usando data de corte: {cutoff_date} UTC")
        print(f"   Apenas agendamentos criados ANTES desta data serão corrigidos")
        print()
    except ValueError:
        print("❌ ERRO: Formato de data inválido. Use 'YYYY-MM-DD HH:MM:SS'")
        print("   Exemplo: '2025-10-21 22:30:00'")
        print()
        sys.exit(1)
    
    if dry_run:
        print("⚠️  Executando em modo DRY RUN - nenhuma alteração será feita")
        print()
    else:
        print("⚠️  ATENÇÃO: As alterações serão aplicadas no banco de dados!")
        print()
        if cutoff_date:
            print(f"   Apenas agendamentos criados ANTES de {cutoff_date} UTC serão corrigidos")
        else:
            print(f"   ⚠️  RISCO: Usando data atual como corte (pode corrigir agendamentos novos!)")
        print()
        resposta = input("Tem certeza que deseja continuar? (digite 'sim' para confirmar): ")
        if resposta.lower() != 'sim':
            print("❌ Operação cancelada")
            sys.exit(0)
        print()
    
    fix_timezone_agendamentos(dry_run=dry_run, cutoff_date=cutoff_date)
