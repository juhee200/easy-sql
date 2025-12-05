from typing import Dict, List, Optional
from openai import OpenAI
from anthropic import Anthropic
from config.settings import settings


class NLToSQLConverter:
    """Convert natural language queries to SQL using LLM (OpenAI / Anthropic)
    Modernized for latest SDKs (OpenAI >= 1.60+, Anthropic >= 1.x)
    """

    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model or settings.DEFAULT_MODEL

        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found in environment variables")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        elif self.provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not found in environment variables")
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    # ------------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------------
    def _get_system_prompt(self, schema_info: str) -> str:
        return f"""
You are an expert SQL query generator. Convert natural language questions into valid SQL queries.

Database Schema:
{schema_info}

Rules:
1. Generate ONLY the SQL query (no explanation)
2. SQL syntax must be correct
3. Use proper JOINs when referencing multiple tables
4. Add LIMIT clauses when appropriate
5. Only generate SELECT queries
6. Use exact column/table names
""".strip()

    # ------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------
    def convert(
        self,
        natural_language_query: str,
        schema_info: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        system_prompt = self._get_system_prompt(schema_info)

        if self.provider == "openai":
            return self._convert_openai(natural_language_query, system_prompt, conversation_history)
        else:
            return self._convert_anthropic(natural_language_query, system_prompt, conversation_history)

    # ------------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------------
    def _convert_openai(
        self,
        query: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict]],
    ) -> str:

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": query})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            max_tokens=500,
        )

        sql = response.choices[0].message.content.strip()
        return self._clean_sql_query(sql)

    # ------------------------------------------------------------------------
    # Anthropic
    # ------------------------------------------------------------------------
    def _convert_anthropic(
        self,
        query: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict]],
    ) -> str:

        messages = conversation_history[:] if conversation_history else []
        messages.append({"role": "user", "content": query})

        response = self.anthropic_client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            max_tokens=500,
            temperature=0,
        )

        sql = response.content[0].text.strip()
        return self._clean_sql_query(sql)

    # ------------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------------
    def _clean_sql_query(self, query: str) -> str:
        query = query.replace("```sql", "").replace("```", "").strip()
        return query[:-1] if query.endswith(";") else query

    def validate_query(self, query: str) -> bool:
        q = query.upper().strip()
        if not q.startswith("SELECT"):
            return False

        banned = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]
        return not any(k in q for k in banned)
