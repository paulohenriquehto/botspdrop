import psycopg2
from psycopg2.extras import RealDictCursor
from agno.tools import Toolkit
from typing import List, Dict, Any
import os

class ConversationScriptsTools(Toolkit):
    """Ferramenta de Scripts de Conversação para SPDrop - Base de conhecimento de atendimento"""

    def __init__(self):
        # Database configuration
        self.conn_params = {
            "host": os.getenv("DB_HOST", "postgres"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "spdrop_db"),
            "user": os.getenv("DB_USER", "spdrop_user"),
            "password": os.getenv("DB_PASSWORD", "spdrop_password")
        }

        # Register all tools in the constructor
        tools = [
            self.buscar_por_perfil,
            self.buscar_por_etapa,
            self.buscar_por_tipo_script,
            self.listar_perfis,
            self.buscar_exemplo_completo,
            self.buscar_por_palavra_chave
        ]

        super().__init__(name="conversation_scripts", tools=tools)

    def _get_connection(self):
        """Criar conexão com o banco de dados"""
        try:
            return psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            return None

    def buscar_por_perfil(self, perfil_nome: str, tipo_script: str = None) -> Dict[str, Any]:
        """
        Busca scripts de conversação por perfil de cliente.

        Args:
            perfil_nome: Nome do perfil (ex: "Mãe ocupada", "Estudante")
            tipo_script: Filtrar por tipo ('normal' ou 'promocao'), opcional

        Returns:
            Dict com scripts encontrados organizados por etapa
        """
        conn = self._get_connection()
        if not conn:
            return {"erro": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT profile_id, profile_name, stage, speaker, content, script_type
                    FROM conversation_scripts
                    WHERE LOWER(profile_name) LIKE LOWER(%s)
                """
                params = [f"%{perfil_nome}%"]

                if tipo_script:
                    query += " AND script_type = %s"
                    params.append(tipo_script)

                query += " ORDER BY profile_id, stage"

                cur.execute(query, params)
                results = cur.fetchall()

                if not results:
                    return {
                        "encontrado": False,
                        "perfil": perfil_nome,
                        "mensagem": f"Nenhum script encontrado para o perfil '{perfil_nome}'"
                    }

                # Organizar por etapas
                scripts_organizados = {}
                for row in results:
                    stage = row['stage']
                    if stage not in scripts_organizados:
                        scripts_organizados[stage] = []

                    scripts_organizados[stage].append({
                        "speaker": row['speaker'],
                        "content": row['content']
                    })

                return {
                    "encontrado": True,
                    "perfil": results[0]['profile_name'],
                    "tipo_script": results[0]['script_type'],
                    "total_etapas": len(scripts_organizados),
                    "scripts": scripts_organizados
                }

        except psycopg2.Error as e:
            return {"erro": str(e)}
        finally:
            conn.close()

    def buscar_por_etapa(self, etapa: str) -> Dict[str, Any]:
        """
        Busca exemplos de como conduzir uma etapa específica da conversa.

        Args:
            etapa: Nome da etapa (ex: "abertura", "objecao", "fechamento")

        Returns:
            Dict com exemplos de diferentes perfis para aquela etapa
        """
        conn = self._get_connection()
        if not conn:
            return {"erro": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT profile_name, speaker, content, script_type
                    FROM conversation_scripts
                    WHERE LOWER(stage) LIKE LOWER(%s)
                    ORDER BY profile_id, speaker
                    LIMIT 20
                """, (f"%{etapa}%",))

                results = cur.fetchall()

                if not results:
                    return {
                        "encontrado": False,
                        "etapa": etapa,
                        "mensagem": f"Nenhum exemplo encontrado para a etapa '{etapa}'"
                    }

                exemplos = []
                for row in results:
                    exemplos.append({
                        "perfil": row['profile_name'],
                        "speaker": row['speaker'],
                        "content": row['content'],
                        "tipo": row['script_type']
                    })

                return {
                    "encontrado": True,
                    "etapa": etapa,
                    "total_exemplos": len(exemplos),
                    "exemplos": exemplos
                }

        except psycopg2.Error as e:
            return {"erro": str(e)}
        finally:
            conn.close()

    def buscar_por_tipo_script(self, tipo: str) -> Dict[str, Any]:
        """
        Busca scripts por tipo (normal ou promoção).

        Args:
            tipo: Tipo de script ('normal' ou 'promocao')

        Returns:
            Dict com todos os perfis daquele tipo
        """
        conn = self._get_connection()
        if not conn:
            return {"erro": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT profile_id, profile_name
                    FROM conversation_scripts
                    WHERE script_type = %s
                    ORDER BY profile_id
                """, (tipo,))

                results = cur.fetchall()

                if not results:
                    return {
                        "encontrado": False,
                        "tipo": tipo,
                        "mensagem": f"Nenhum perfil encontrado para o tipo '{tipo}'"
                    }

                perfis = [{"id": row['profile_id'], "nome": row['profile_name']} for row in results]

                return {
                    "encontrado": True,
                    "tipo": tipo,
                    "total_perfis": len(perfis),
                    "perfis": perfis
                }

        except psycopg2.Error as e:
            return {"erro": str(e)}
        finally:
            conn.close()

    def listar_perfis(self) -> Dict[str, Any]:
        """
        Lista todos os perfis de cliente disponíveis.

        Returns:
            Dict com lista de perfis organizados por tipo
        """
        conn = self._get_connection()
        if not conn:
            return {"erro": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT script_type, profile_id, profile_name
                    FROM conversation_scripts
                    ORDER BY script_type, profile_id
                """)

                results = cur.fetchall()

                if not results:
                    return {
                        "total": 0,
                        "perfis": []
                    }

                # Organizar por tipo
                perfis_por_tipo = {}
                for row in results:
                    tipo = row['script_type']
                    if tipo not in perfis_por_tipo:
                        perfis_por_tipo[tipo] = []

                    perfis_por_tipo[tipo].append({
                        "id": row['profile_id'],
                        "nome": row['profile_name']
                    })

                return {
                    "total": len(results),
                    "perfis_por_tipo": perfis_por_tipo
                }

        except psycopg2.Error as e:
            return {"erro": str(e)}
        finally:
            conn.close()

    def buscar_exemplo_completo(self, profile_id: int, tipo_script: str) -> Dict[str, Any]:
        """
        Busca um exemplo completo de conversação para um perfil específico.

        Args:
            profile_id: ID do perfil (1-10)
            tipo_script: Tipo de script ('normal' ou 'promocao')

        Returns:
            Dict com conversa completa organizada em sequência
        """
        conn = self._get_connection()
        if not conn:
            return {"erro": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT profile_name, stage, speaker, content
                    FROM conversation_scripts
                    WHERE profile_id = %s AND script_type = %s
                    ORDER BY id
                """, (profile_id, tipo_script))

                results = cur.fetchall()

                if not results:
                    return {
                        "encontrado": False,
                        "profile_id": profile_id,
                        "tipo": tipo_script
                    }

                conversa = []
                for row in results:
                    conversa.append({
                        "etapa": row['stage'],
                        "speaker": row['speaker'],
                        "texto": row['content']
                    })

                return {
                    "encontrado": True,
                    "perfil": results[0]['profile_name'],
                    "tipo": tipo_script,
                    "total_mensagens": len(conversa),
                    "conversa_completa": conversa
                }

        except psycopg2.Error as e:
            return {"erro": str(e)}
        finally:
            conn.close()

    def buscar_por_palavra_chave(self, palavra_chave: str) -> Dict[str, Any]:
        """
        Busca scripts que contenham uma palavra-chave específica.

        Args:
            palavra_chave: Palavra ou frase para buscar

        Returns:
            Dict com scripts encontrados
        """
        conn = self._get_connection()
        if not conn:
            return {"erro": "Falha na conexão com o banco"}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT profile_name, stage, speaker, content, script_type
                    FROM conversation_scripts
                    WHERE LOWER(content) LIKE LOWER(%s)
                    OR LOWER(profile_name) LIKE LOWER(%s)
                    OR LOWER(stage) LIKE LOWER(%s)
                    ORDER BY profile_id
                    LIMIT 20
                """, (f"%{palavra_chave}%", f"%{palavra_chave}%", f"%{palavra_chave}%"))

                results = cur.fetchall()

                if not results:
                    return {
                        "encontrado": False,
                        "palavra_chave": palavra_chave,
                        "mensagem": f"Nenhum script encontrado com '{palavra_chave}'"
                    }

                scripts = []
                for row in results:
                    scripts.append({
                        "perfil": row['profile_name'],
                        "etapa": row['stage'],
                        "speaker": row['speaker'],
                        "conteudo": row['content'],
                        "tipo": row['script_type']
                    })

                return {
                    "encontrado": True,
                    "palavra_chave": palavra_chave,
                    "total": len(scripts),
                    "scripts": scripts
                }

        except psycopg2.Error as e:
            return {"erro": str(e)}
        finally:
            conn.close()
