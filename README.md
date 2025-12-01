# Easy SQL - Natural Language to SQL Visualizer

자연어를 SQL 쿼리로 변환하고 결과를 시각화하는 AI 기반 데이터 분석 도구입니다.

## 주요 기능

- **자연어 쿼리**: 복잡한 SQL을 몰라도 자연어로 질문하면 자동으로 SQL로 변환
- **다중 LLM 지원**: OpenAI GPT-4 및 Anthropic Claude 지원
- **자동 시각화**: 쿼리 결과를 자동으로 분석하여 최적의 차트 생성
- **다양한 데이터베이스**: SQLite, PostgreSQL, MySQL 지원
- **인터랙티브 UI**: Streamlit 기반의 사용자 친화적 인터페이스
- **쿼리 히스토리**: 이전 쿼리 내역 추적 및 재사용
- **데이터 다운로드**: 쿼리 결과를 CSV로 다운로드

## 프로젝트 구조

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

## 설치 방법

### 1. 레포지토리 클론

```bash
git clone https://github.com/yourusername/easy-sql.git
cd easy-sql
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 API 키를 설정합니다:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 API 키를 입력:

```env
# OpenAI 사용 시
OPENAI_API_KEY=your_openai_api_key_here

# 또는 Anthropic 사용 시
ANTHROPIC_API_KEY=your_anthropic_api_key_here

DEFAULT_LLM_PROVIDER=openai  # 또는 anthropic
DEFAULT_MODEL=gpt-4          # 또는 claude-3-opus-20240229
```

### 5. 샘플 데이터베이스 생성 (선택사항)

```bash
python create_sample_db.py
```

## 실행 방법

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 이 열립니다.

## 사용 방법

### 기본 사용

1. 사이드바에서 LLM 제공자와 모델을 선택
2. 자연어로 질문 입력
   - 예: "Show me total sales by category"
   - 예: "What are the top 5 customers by order amount?"
3. "실행" 버튼 클릭
4. 생성된 SQL 쿼리 확인 및 결과 시각화

### 예시 질문들

샘플 데이터베이스를 사용하는 경우:

- "Show me total sales by category"
- "What are the top 5 customers by order amount?"
- "Show monthly revenue trend"
- "Which products have low stock?"
- "Show customer distribution by city"
- "What is the average order value?"
- "Show products with the highest sales"

### 자신의 데이터베이스 연결

#### SQLite 사용

`.env` 파일에서:
```env
DATABASE_TYPE=sqlite
DATABASE_PATH=data/your_database.db
```

#### PostgreSQL 사용

`.env` 파일에서:
```env
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

#### MySQL 사용

`.env` 파일에서:
```env
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=your_database
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
```

## 기능 상세

### 자연어 처리

- GPT-4 또는 Claude를 사용하여 자연어를 SQL로 변환
- 데이터베이스 스키마를 자동으로 분석하여 정확한 쿼리 생성
- 대화 히스토리를 유지하여 맥락 기반 쿼리 지원

### 시각화

다양한 차트 타입을 자동으로 선택:
- **Bar Chart**: 카테고리별 비교
- **Line Chart**: 시계열 데이터 및 트렌드
- **Pie Chart**: 구성 비율
- **Scatter Plot**: 두 변수 간 관계
- **Histogram**: 분포 분석

### 보안

- SELECT 쿼리만 허용 (INSERT, UPDATE, DELETE 차단)
- SQL 인젝션 방지를 위한 쿼리 검증
- 안전한 쿼리 실행을 위한 SQLAlchemy 사용

## 개발

### 테스트 실행

```bash
pytest tests/
```

### 새로운 LLM 추가

`src/llm/nl_to_sql.py`에서 새로운 LLM 제공자를 추가할 수 있습니다:

```python
def _convert_with_new_provider(self, query: str, system_prompt: str, conversation_history: Optional[List[Dict]] = None) -> str:
    # Implementation
    pass
```

### 새로운 차트 타입 추가

`src/visualization/chart_generator.py`에서 새로운 차트 생성 메서드를 추가할 수 있습니다.

## 기술 스택

- **Frontend & Backend**: Streamlit
- **LLM**: OpenAI GPT-4, Anthropic Claude
- **Database**: SQLAlchemy (SQLite, PostgreSQL, MySQL)
- **Visualization**: Plotly
- **Data Processing**: Pandas

## 라이선스

MIT License

## 기여

Pull Request와 Issue는 언제나 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 Issue를 생성해주세요.

## 향후 계획

- [ ] 쿼리 결과 캐싱
- [ ] 더 많은 차트 타입 지원
- [ ] 쿼리 최적화 제안
- [ ] 멀티 테이블 조인 자동 추천
- [ ] 자연어 기반 데이터 필터링
- [ ] 대시보드 저장 및 공유
- [ ] Excel 파일 업로드 지원
- [ ] 실시간 데이터 스트리밍
