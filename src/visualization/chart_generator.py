import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any


class ChartGenerator:
    """Generate charts from query results"""

    def __init__(self):
        """Initialize chart generator"""
        self.color_sequence = px.colors.qualitative.Set3

    def auto_detect_chart_type(self, df: pd.DataFrame) -> str:
        """
        Automatically detect the best chart type for the data

        Args:
            df: DataFrame with query results

        Returns:
            Suggested chart type
        """
        if df.empty:
            return "table"

        num_cols = len(df.columns)
        num_rows = len(df)

        # Get numeric and non-numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()

        # Single numeric column - use bar chart
        if num_cols == 1 and numeric_cols:
            return "metric"

        # Two columns: one categorical, one numeric
        if num_cols == 2 and len(numeric_cols) == 1 and len(non_numeric_cols) == 1:
            if num_rows <= 20:
                return "bar"
            else:
                return "line"

        # Multiple numeric columns - use line chart
        if len(numeric_cols) >= 2:
            return "line"

        # Time series detection
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols and numeric_cols:
            return "line"

        # Default to table for complex data
        return "table"

    def create_bar_chart(
        self,
        df: pd.DataFrame,
        x_column: str = None,
        y_column: str = None,
        title: str = "Bar Chart"
    ) -> go.Figure:
        """Create a bar chart"""
        if x_column is None:
            x_column = df.columns[0]
        if y_column is None:
            y_column = df.columns[1] if len(df.columns) > 1 else df.columns[0]

        fig = px.bar(
            df,
            x=x_column,
            y=y_column,
            title=title,
            color_discrete_sequence=self.color_sequence
        )

        fig.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column,
            hovermode='x unified'
        )

        return fig

    def create_line_chart(
        self,
        df: pd.DataFrame,
        x_column: str = None,
        y_columns: list = None,
        title: str = "Line Chart"
    ) -> go.Figure:
        """Create a line chart"""
        if x_column is None:
            x_column = df.columns[0]

        if y_columns is None:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            y_columns = numeric_cols if numeric_cols else [df.columns[1]]

        fig = go.Figure()

        for i, y_col in enumerate(y_columns):
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='lines+markers',
                name=y_col,
                line=dict(color=self.color_sequence[i % len(self.color_sequence)])
            ))

        fig.update_layout(
            title=title,
            xaxis_title=x_column,
            yaxis_title="Value",
            hovermode='x unified'
        )

        return fig

    def create_pie_chart(
        self,
        df: pd.DataFrame,
        names_column: str = None,
        values_column: str = None,
        title: str = "Pie Chart"
    ) -> go.Figure:
        """Create a pie chart"""
        if names_column is None:
            names_column = df.columns[0]
        if values_column is None:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            values_column = numeric_cols[0] if numeric_cols else df.columns[1]

        fig = px.pie(
            df,
            names=names_column,
            values=values_column,
            title=title,
            color_discrete_sequence=self.color_sequence
        )

        return fig

    def create_scatter_plot(
        self,
        df: pd.DataFrame,
        x_column: str = None,
        y_column: str = None,
        title: str = "Scatter Plot"
    ) -> go.Figure:
        """Create a scatter plot"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if x_column is None:
            x_column = numeric_cols[0] if numeric_cols else df.columns[0]
        if y_column is None:
            y_column = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]

        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=title,
            color_discrete_sequence=self.color_sequence
        )

        fig.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column
        )

        return fig

    def create_histogram(
        self,
        df: pd.DataFrame,
        column: str = None,
        title: str = "Histogram"
    ) -> go.Figure:
        """Create a histogram"""
        if column is None:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            column = numeric_cols[0] if numeric_cols else df.columns[0]

        fig = px.histogram(
            df,
            x=column,
            title=title,
            color_discrete_sequence=self.color_sequence
        )

        fig.update_layout(
            xaxis_title=column,
            yaxis_title="Frequency"
        )

        return fig

    def create_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a chart based on type

        Args:
            df: DataFrame with data
            chart_type: Type of chart ('bar', 'line', 'pie', 'scatter', 'histogram')
            config: Additional configuration for the chart

        Returns:
            Plotly figure
        """
        if config is None:
            config = {}

        if chart_type == "bar":
            return self.create_bar_chart(df, **config)
        elif chart_type == "line":
            return self.create_line_chart(df, **config)
        elif chart_type == "pie":
            return self.create_pie_chart(df, **config)
        elif chart_type == "scatter":
            return self.create_scatter_plot(df, **config)
        elif chart_type == "histogram":
            return self.create_histogram(df, **config)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    def get_numeric_columns(self, df: pd.DataFrame) -> list:
        """Get list of numeric columns"""
        return df.select_dtypes(include=['number']).columns.tolist()

    def get_categorical_columns(self, df: pd.DataFrame) -> list:
        """Get list of categorical columns"""
        return df.select_dtypes(exclude=['number']).columns.tolist()
