import csv
import psycopg2
import os
import glob
from pathlib import Path

# Configuração do banco
conn_params = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "spdrop_db"),
    "user": os.getenv("DB_USER", "spdrop_user"),
    "password": os.getenv("DB_PASSWORD", "spdrop_password")
}

def parse_normal_csv():
    """Processa o CSV de scripts normais"""
    base_dir = Path(__file__).parent / "docs da minha empresa" / "movos"
    csv_files = glob.glob(str(base_dir / "*normal*.csv"))

    if not csv_files:
        raise FileNotFoundError("CSV de scripts normais não encontrado")

    csv_path = csv_files[0]
    scripts = []

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            profile_id = int(row['ID'])
            profile_name = row['Perfil do Cliente']

            # Etapa 1: Abertura (Gabi)
            scripts.append({
                'script_type': 'normal',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'abertura',
                'speaker': 'gabi',
                'content': row['1. Abertura & Conexão (Gabi)'].strip('"')
            })

            # Etapa 2: Resposta do Cliente
            scripts.append({
                'script_type': 'normal',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'resposta_cliente',
                'speaker': 'cliente',
                'content': row['2. Resposta do Cliente (Situação)'].strip('"')
            })

            # Etapa 3: Diagnóstico (Gabi)
            scripts.append({
                'script_type': 'normal',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'diagnostico',
                'speaker': 'gabi',
                'content': row['3. Diagnóstico & Valor (Gabi)'].strip('"')
            })

            # Etapa 4: Objeção (Cliente)
            scripts.append({
                'script_type': 'normal',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'objecao',
                'speaker': 'cliente',
                'content': row['4. Objeção / Dúvida (Cliente)'].strip('"')
            })

            # Etapa 5: Quebra de Objeção (Gabi)
            scripts.append({
                'script_type': 'normal',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'quebra_objecao',
                'speaker': 'gabi',
                'content': row['5. Quebra de Objeção & Storytelling (Gabi)'].strip('"')
            })

            # Etapa 6: Fechamento (Gabi)
            scripts.append({
                'script_type': 'normal',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'fechamento',
                'speaker': 'gabi',
                'content': row['6. Fechamento (Gabi)'].strip('"')
            })

    return scripts

def parse_promocao_csv():
    """Processa o CSV de scripts de promoção"""
    base_dir = Path(__file__).parent / "docs da minha empresa" / "movos"
    csv_files = glob.glob(str(base_dir / "*dando*.csv"))

    if not csv_files:
        raise FileNotFoundError("CSV de scripts de promoção não encontrado")

    csv_path = csv_files[0]
    scripts = []

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            profile_id = int(row['ID'])
            profile_name = row['Perfil do Cliente']

            # Etapa 1: Abertura & Diagnóstico (Gabi)
            scripts.append({
                'script_type': 'promocao',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'abertura_diagnostico',
                'speaker': 'gabi',
                'content': row['1. Abertura & Diagnóstico (Gabi)'].strip('"')
            })

            # Etapa 2: Apresentação com Preço Cheio (Gabi)
            scripts.append({
                'script_type': 'promocao',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'apresentacao_preco',
                'speaker': 'gabi',
                'content': row['2. Apresentação (Preço Cheio - Ancoragem)'].strip('"')
            })

            # Etapa 3: Objeção "Sem Dinheiro" (Cliente)
            scripts.append({
                'script_type': 'promocao',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'objecao_sem_dinheiro',
                'speaker': 'cliente',
                'content': row['3. Objeção "Sem Dinheiro" (Cliente)'].strip('"')
            })

            # Etapa 4: Cartada Black Friday (Gabi)
            scripts.append({
                'script_type': 'promocao',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'cartada_promocao',
                'speaker': 'gabi',
                'content': row['4. Cartada Black Friday (Gabi)'].strip('"')
            })

            # Etapa 5: Fechamento (Gabi)
            scripts.append({
                'script_type': 'promocao',
                'profile_id': profile_id,
                'profile_name': profile_name,
                'stage': 'fechamento',
                'speaker': 'gabi',
                'content': row['5. Fechamento (Gabi)'].strip('"')
            })

    return scripts

def insert_scripts(scripts):
    """Insere scripts no banco de dados"""
    conn = psycopg2.connect(**conn_params)

    try:
        with conn.cursor() as cur:
            # Limpar tabela antes de popular
            cur.execute("DELETE FROM conversation_scripts")

            # Inserir scripts
            for script in scripts:
                cur.execute("""
                    INSERT INTO conversation_scripts
                    (script_type, profile_id, profile_name, stage, speaker, content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    script['script_type'],
                    script['profile_id'],
                    script['profile_name'],
                    script['stage'],
                    script['speaker'],
                    script['content']
                ))

            conn.commit()
            print(f"✓ {len(scripts)} scripts inseridos com sucesso!")

            # Verificar total por tipo
            cur.execute("""
                SELECT script_type, COUNT(*) as total
                FROM conversation_scripts
                GROUP BY script_type
            """)

            print("\nResumo:")
            for row in cur.fetchall():
                print(f"  - {row[0]}: {row[1]} scripts")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir scripts: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Processando CSVs...")

    # Processar scripts normais
    print("\n1. Processando scripts normais...")
    normal_scripts = parse_normal_csv()
    print(f"   ✓ {len(normal_scripts)} scripts normais processados")

    # Processar scripts de promoção
    print("\n2. Processando scripts de promoção...")
    promocao_scripts = parse_promocao_csv()
    print(f"   ✓ {len(promocao_scripts)} scripts de promoção processados")

    # Combinar todos os scripts
    all_scripts = normal_scripts + promocao_scripts
    print(f"\n3. Total de scripts: {len(all_scripts)}")

    # Inserir no banco
    print("\n4. Inserindo no banco de dados...")
    insert_scripts(all_scripts)

    print("\n✓ Processo concluído!")
