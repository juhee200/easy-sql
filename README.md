# Easy SQL - Natural Language to SQL Visualizer

An AI-powered data analysis tool that converts natural language to SQL queries and visualizes the results.

## Key Features

- **Natural Language Queries**: Automatically converts natural language questions to SQL without knowing complex SQL syntax
- **Multiple LLM Support**: Supports OpenAI GPT-4 and Anthropic Claude
- **Automatic Visualization**: Automatically analyzes query results and generates optimal charts
- **Multiple Databases**: Supports SQLite, PostgreSQL, and MySQL
- **Interactive UI**: User-friendly interface based on Streamlit
- **Query History**: Track and reuse previous query history
- **Data Download**: Download query results as CSV

## Project Structure

```
easy-sql/
├── app.py                    # Main Streamlit application
├── config/
│   └── settings.py          # Configuration settings
├── src/
│   ├── llm/
│   │   └── nl_to_sql.py     # Natural language to SQL converter
│   ├── database/
│   │   └── db_manager.py    # Database manager
│   └── visualization/
│       └── chart_generator.py # Chart generation
├── data/
│   └── sample.db            # Sample SQLite database
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── create_sample_db.py      # Sample database creation script
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/easy-sql.git
cd easy-sql
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variable Setup

Copy the `.env.example` file to `.env` and configure your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file to enter your API keys:

```env
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Or for Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

DEFAULT_LLM_PROVIDER=openai  # or anthropic
DEFAULT_MODEL=gpt-4          # or claude-3-opus-20240229
```

### 5. Create Sample Database (Optional)

```bash
python create_sample_db.py
```

## Running the Application

```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`.

## Usage

### Basic Usage

1. Select LLM provider and model from the sidebar
2. Enter your question in natural language
   - Example: "Show me total sales by category"
   - Example: "What are the top 5 customers by order amount?"
3. Click the "Execute" button
4. View the generated SQL query and visualized results

### Example Questions

When using the sample database:

- "Show me total sales by category"
- "What are the top 5 customers by order amount?"
- "Show monthly revenue trend"
- "Which products have low stock?"
- "Show customer distribution by city"
- "What is the average order value?"
- "Show products with the highest sales"

### Connecting Your Own Database

#### Using SQLite

In the `.env` file:
```env
DATABASE_TYPE=sqlite
DATABASE_PATH=data/your_database.db
```

#### Using PostgreSQL

In the `.env` file:
```env
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

#### Using MySQL

In the `.env` file:
```env
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=your_database
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
```

## Feature Details

### Natural Language Processing

- Uses GPT-4 or Claude to convert natural language to SQL
- Automatically analyzes database schema to generate accurate queries
- Maintains conversation history for context-based queries

### Visualization

Automatically selects various chart types:
- **Bar Chart**: Category comparisons
- **Line Chart**: Time series data and trends
- **Pie Chart**: Composition ratios
- **Scatter Plot**: Relationship between two variables
- **Histogram**: Distribution analysis

### Security

- Only SELECT queries allowed (INSERT, UPDATE, DELETE blocked)
- Query validation to prevent SQL injection
- Uses SQLAlchemy for safe query execution

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New LLMs

You can add new LLM providers in `src/llm/nl_to_sql.py`:

```python
def _convert_with_new_provider(self, query: str, system_prompt: str, conversation_history: Optional[List[Dict]] = None) -> str:
    # Implementation
    pass
```

### Adding New Chart Types

You can add new chart generation methods in `src/visualization/chart_generator.py`.

## Technology Stack

- **Frontend & Backend**: Streamlit
- **LLM**: OpenAI GPT-4, Anthropic Claude
- **Database**: SQLAlchemy (SQLite, PostgreSQL, MySQL)
- **Visualization**: Plotly
- **Data Processing**: Pandas

## License

MIT License

## Contributing

Pull Requests and Issues are always welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

If you have any questions or suggestions about the project, please create an Issue.

## Future Plans

- [ ] Query result caching
- [ ] Support for more chart types
- [ ] Query optimization suggestions
- [ ] Automatic multi-table join recommendations
- [ ] Natural language-based data filtering
- [ ] Dashboard save and share
- [ ] Excel file upload support
- [ ] Real-time data streaming
