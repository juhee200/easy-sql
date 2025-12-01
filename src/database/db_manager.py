from typing import List, Dict, Tuple, Any
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from config.settings import settings


class DatabaseManager:
    """Manage database connections and query execution"""

    def __init__(self, database_url: str = None):
        """
        Initialize database manager

        Args:
            database_url: Database connection URL (if None, uses settings)
        """
        self.database_url = database_url or settings.get_database_url()
        self.engine = create_engine(self.database_url)

    def get_schema_info(self) -> str:
        """
        Get database schema information as a formatted string

        Returns:
            Formatted string with table and column information
        """
        inspector = inspect(self.engine)
        schema_info = []

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            column_info = []

            for column in columns:
                col_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                column_info.append(f"  - {column['name']} ({col_type}) {nullable}")

            schema_info.append(f"Table: {table_name}")
            schema_info.extend(column_info)
            schema_info.append("")

        return "\n".join(schema_info)

    def get_tables(self) -> List[str]:
        """
        Get list of all tables in the database

        Returns:
            List of table names
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema for a specific table

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        inspector = inspect(self.engine)
        return inspector.get_columns(table_name)

    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """
        Execute SQL query and return results

        Args:
            query: SQL query to execute

        Returns:
            Tuple of (success: bool, result: DataFrame or error message)
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return True, df
        except SQLAlchemyError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """
        Get sample data from a table

        Args:
            table_name: Name of the table
            limit: Number of rows to fetch

        Returns:
            DataFrame with sample data
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        success, result = self.execute_query(query)

        if success:
            return result
        else:
            return pd.DataFrame()

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """
        Get statistics about a table

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table statistics
        """
        stats = {}

        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        success, result = self.execute_query(count_query)

        if success:
            stats['row_count'] = result.iloc[0]['count']
        else:
            stats['row_count'] = 0

        # Get column names
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        stats['columns'] = [col['name'] for col in columns]
        stats['column_count'] = len(columns)

        return stats

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test database connection

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return True, "Database connection successful"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
