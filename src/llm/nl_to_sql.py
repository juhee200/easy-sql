from typing import Dict, List, Optional
import openai
from anthropic import Anthropic
from config.settings import settings


class NLToSQLConverter:
    """Convert natural language queries to SQL using LLM"""

    def __init__(self, provider: str = None, model: str = None):
        """
        Initialize the NL to SQL converter

        Args:
            provider: LLM provider ('openai' or 'anthropic')
            model: Model name to use
        """
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model or settings.DEFAULT_MODEL

        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found in environment variables")
            openai.api_key = settings.OPENAI_API_KEY
        elif self.provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not found in environment variables")
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _get_system_prompt(self, schema_info: str) -> str:
        """Generate system prompt with database schema information"""
        return f"""You are an expert SQL query generator. Convert natural language questions into valid SQL queries.

Database Schema:
{schema_info}

Rules:
1. Generate ONLY the SQL query, without any explanation or markdown
2. Use proper SQL syntax
3. Consider the schema carefully when generating queries
4. Use appropriate JOINs when needed
5. Add LIMIT clauses for safety when appropriate
6. Return only SELECT queries (no INSERT, UPDATE, DELETE, DROP)
7. Make sure column names and table names match the schema exactly
"""

    def convert(
        self,
        natural_language_query: str,
        schema_info: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Convert natural language to SQL

        Args:
            natural_language_query: User's question in natural language
            schema_info: Database schema information
            conversation_history: Previous conversation context

        Returns:
            Generated SQL query
        """
        system_prompt = self._get_system_prompt(schema_info)

        if self.provider == "openai":
            return self._convert_with_openai(
                natural_language_query,
                system_prompt,
                conversation_history
            )
        elif self.provider == "anthropic":
            return self._convert_with_anthropic(
                natural_language_query,
                system_prompt,
                conversation_history
            )

    def _convert_with_openai(
        self,
        query: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Convert using OpenAI API"""
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": query})

        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            max_tokens=500
        )

        sql_query = response.choices[0].message.content.strip()
        return self._clean_sql_query(sql_query)

    def _convert_with_anthropic(
        self,
        query: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Convert using Anthropic API"""
        messages = []

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": query})

        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0,
            system=system_prompt,
            messages=messages
        )

        sql_query = response.content[0].text.strip()
        return self._clean_sql_query(sql_query)

    def _clean_sql_query(self, query: str) -> str:
        """Clean and format the SQL query"""
        # Remove markdown code blocks if present
        query = query.replace("```sql", "").replace("```", "")

        # Remove any leading/trailing whitespace
        query = query.strip()

        # Remove semicolon if present at the end
        if query.endswith(";"):
            query = query[:-1]

        return query

    def validate_query(self, query: str) -> bool:
        """
        Basic validation of SQL query

        Args:
            query: SQL query to validate

        Returns:
            True if query appears valid, False otherwise
        """
        query_upper = query.upper().strip()

        # Must be a SELECT query
        if not query_upper.startswith("SELECT"):
            return False

        # Should not contain dangerous keywords
        dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False

        return True
