import streamlit as st
import pandas as pd
from src.llm.nl_to_sql import NLToSQLConverter
from src.database.db_manager import DatabaseManager
from src.visualization.chart_generator import ChartGenerator
from config.settings import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Easy SQL - NL to SQL Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sql-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_database():
    """Initialize database manager"""
    try:
        db = DatabaseManager()
        success, message = db.test_connection()
        if not success:
            st.error(f"Database connection failed: {message}")
            return None
        return db
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        return None


def init_llm(provider, model):
    """Initialize LLM converter"""
    try:
        converter = NLToSQLConverter(provider=provider, model=model)
        return converter
    except Exception as e:
        st.error(f"Failed to initialize LLM: {str(e)}")
        print("INIT ERROR:", e)
        return None


def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Easy SQL</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-powered tool to convert natural language to SQL and visualize results</p>',
        unsafe_allow_html=True
    )

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")

        # LLM Configuration
        st.subheader("LLM Configuration")
        llm_provider = st.selectbox(
            "LLM Provider",
            ["openai", "anthropic"],
            index=0 if settings.DEFAULT_LLM_PROVIDER == "openai" else 1
        )

        model_options = {
            "openai": ["gpt-4o-mini"],
            "anthropic": ["claude-3-haiku-20240307"]
        }

        llm_model = st.selectbox(
            "Model",
            model_options[llm_provider],
            index=0
        )

        # Database info
        st.subheader("📁 Database Information")
        db = init_database()

        if db:
            tables = db.get_tables()
            st.write(f"**Number of Tables:** {len(tables)}")

            selected_table = st.selectbox("Select Table", tables)

            if selected_table:
                stats = db.get_table_stats(selected_table)
                st.write(f"**Row Count:** {stats['row_count']}")
                st.write(f"**Column Count:** {stats['column_count']}")

                if st.checkbox("Show Sample Data"):
                    sample_df = db.get_sample_data(selected_table, limit=5)
                    st.dataframe(sample_df)

        # Example queries
        st.subheader("💡 Example Questions")
        example_queries = [
            "Show me total sales by category",
            "What are the top 5 customers by order amount?",
            "Show monthly revenue trend",
            "Which products have low stock?",
            "Show customer distribution by city"
        ]

        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.example_query = query

    # Main content
    if not db:
        st.error("Database connection failed. Please check your .env file.")
        return

    # Initialize conversation history in session state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "query_results" not in st.session_state:
        st.session_state.query_results = []

    # Query input
    st.subheader("🔍 Enter Question")

    # Use example query if set
    user_query = st.text_area(
        "Enter your question in natural language",
        value=st.session_state.get("example_query", ""),
        height=100,
        placeholder="Example: Show me the total revenue by category"
    )

    col1, col2 = st.columns([1, 5])

    with col1:
        submit_button = st.button("🚀 Execute", type="primary", use_container_width=True)

    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)

    if clear_button:
        st.session_state.conversation_history = []
        st.session_state.query_results = []
        st.rerun()

    if submit_button and user_query:
        if "example_query" in st.session_state:
            del st.session_state.example_query

        with st.spinner("Generating SQL query..."):
            logger.info(f"User query: {user_query}")
            logger.info(f"LLM Provider: {llm_provider}")

            # Initialize LLM
            converter = init_llm(llm_provider, llm_model)

            if not converter:
                st.error("Failed to initialize LLM. Please check your API key.")
                return

            # Get schema info
            schema_info = db.get_schema_info()

            # Convert to SQL
            try:
                sql_query = converter.convert(
                    user_query,
                    schema_info,
                    st.session_state.conversation_history
                )

                # Validate query
                if not converter.validate_query(sql_query):
                    st.error("⚠️ Generated query is not safe or valid.")
                    return

                # Display generated SQL
                st.subheader("📝 Generated SQL Query")
                st.markdown(f'<div class="sql-box"><code>{sql_query}</code></div>', unsafe_allow_html=True)

                # Execute query
                with st.spinner("Executing query..."):
                    success, result = db.execute_query(sql_query)

                    if success:
                        st.success(f"✅ Query executed successfully! ({len(result)} rows)")

                        # Save to history
                        st.session_state.conversation_history.append({
                            "role": "user",
                            "content": user_query
                        })
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": sql_query
                        })

                        st.session_state.query_results.append({
                            "query": user_query,
                            "sql": sql_query,
                            "result": result
                        })

                    else:
                        st.error(f"❌ Query execution failed: {result}")
                        return

            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")
                return

    # Display results
    if st.session_state.query_results:
        latest_result = st.session_state.query_results[-1]
        df = latest_result["result"]

        if not df.empty:
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Visualization", "📋 Data", "📈 Chart Settings"])

            with tab1:
                st.subheader("Data Visualization")

                # Auto-detect chart type
                chart_gen = ChartGenerator()
                suggested_chart = chart_gen.auto_detect_chart_type(df)

                # Display metric if single value
                if len(df) == 1 and len(df.columns) == 1:
                    st.metric(
                        label=df.columns[0],
                        value=df.iloc[0, 0]
                    )
                elif len(df.columns) == 1 and df[df.columns[0]].dtype in ['int64', 'float64']:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Sum", f"{df[df.columns[0]].sum():,.2f}")
                    with col2:
                        st.metric("Average", f"{df[df.columns[0]].mean():,.2f}")
                    with col3:
                        st.metric("Maximum", f"{df[df.columns[0]].max():,.2f}")

                # Display chart
                if len(df) > 1 and suggested_chart != "table":
                    try:
                        fig = chart_gen.create_chart(df, suggested_chart)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Chart generation failed: {str(e)}")
                        st.dataframe(df, use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)

            with tab2:
                st.subheader("Data Table")
                st.dataframe(df, use_container_width=True)

                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="query_result.csv",
                    mime="text/csv"
                )

                # Statistics
                if not df.empty:
                    st.subheader("Statistical Information")
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        st.dataframe(df[numeric_cols].describe())

            with tab3:
                st.subheader("Chart Customization")

                chart_type = st.selectbox(
                    "Chart Type",
                    ["bar", "line", "pie", "scatter", "histogram"],
                    index=["bar", "line", "pie", "scatter", "histogram"].index(suggested_chart)
                    if suggested_chart in ["bar", "line", "pie", "scatter", "histogram"] else 0
                )

                # Column selection based on chart type
                if chart_type in ["bar", "line", "scatter"]:
                    x_column = st.selectbox("X-axis", df.columns.tolist(), index=0)

                    numeric_cols = chart_gen.get_numeric_columns(df)
                    if chart_type == "line":
                        y_columns = st.multiselect("Y-axis (multiple selection)", numeric_cols, default=numeric_cols[:1])
                    else:
                        y_column = st.selectbox("Y-axis", numeric_cols, index=0 if numeric_cols else 0)

                elif chart_type == "pie":
                    names_column = st.selectbox("Names Column", df.columns.tolist(), index=0)
                    numeric_cols = chart_gen.get_numeric_columns(df)
                    values_column = st.selectbox("Values Column", numeric_cols, index=0 if numeric_cols else 0)

                elif chart_type == "histogram":
                    numeric_cols = chart_gen.get_numeric_columns(df)
                    column = st.selectbox("Select Column", numeric_cols, index=0 if numeric_cols else 0)

                if st.button("Generate Chart"):
                    try:
                        config = {}
                        if chart_type in ["bar", "scatter"]:
                            config = {"x_column": x_column, "y_column": y_column}
                        elif chart_type == "line":
                            config = {"x_column": x_column, "y_columns": y_columns}
                        elif chart_type == "pie":
                            config = {"names_column": names_column, "values_column": values_column}
                        elif chart_type == "histogram":
                            config = {"column": column}

                        fig = chart_gen.create_chart(df, chart_type, config)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Chart generation failed: {str(e)}")

    # Query history
    if st.session_state.query_results:
        with st.expander("📜 Query History"):
            for idx, item in enumerate(reversed(st.session_state.query_results)):
                st.write(f"**{len(st.session_state.query_results) - idx}. {item['query']}**")
                st.code(item['sql'], language='sql')
                st.write(f"Results: {len(item['result'])} rows")
                st.divider()


if __name__ == "__main__":
    main()
