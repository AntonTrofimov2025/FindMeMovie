# FindMeMovie

You wanna watch something special and dunno what exactly? You're at the right place then :)

**FindMeMovie** is a high-performance, modular console application designed to help users search, filter, and discover films seamlessly. Built on clean architecture principles (MVC-like split), it efficiently connects a MySQL relational dataset with a MongoDB instance used for structured user query logging and real-time analytics.

---

## 🚀 Key Features

*   **Advanced Search Engine**: Multi-criteria lookups including custom year ranges, multi-word fuzzy title matching (`LIKE`), and actor name queries.
*   **ACID-Compliant MySQL Backend**: High-speed relational processing utilizing windows functions (`row_number() over ()`) for fast, server-side data pagination.
*   **MongoDB Analytical Tracking**: Full logging of search queries into a NoSQL pipeline, enabling user habit auditing.
*   **Dynamic Data Aggregations**: Instantly computes top 5 statistical summaries for the most popular titles, genres, ratings, or actors.
*   **State-Driven Dynamic UI**: Interactive hierarchical console menu built on a data-driven stack engine, eliminating ugly nested `if/else` ladders.
*   **Production-Ready Logging**: Deep application audit architecture using decorators to write execution states and complete error tracebacks into secure rolling files.
*   **10/10 Pylint Approved**: 100% compliant with PEP 8 standards, typed definitions, and documentation requirements.

---

## 🛠️ Project Structure

The codebase is engineered around highly specialized modules obeying the Single Responsibility Principle:

*   `main.py` — The core application bootstrap orchestrating concurrent multi-database context entry points.
*   `ui.py` — Interaction and Routing layer handling state management and user validation routines.
*   `movie_db.py` — Secure connection manager managing MySQL transactional cycles.
*   `mongodb.py` — Context-managed NoSQL link equipped with automated connection health ping checks.
*   `movie_logging.py` — High-efficiency audit decorators capable of extracting full stack traces (`exc_info`).
*   `sql.py` — Fully capitalized catalog containing heavily optimized relational parameter constraints.
*   `errors.py` — Pass-free customized semantic exception domain classes.

---

## 📦 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/AntonTrofimov2025
cd FindMeMovie
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Create a `.env` file in the root directory of your project and populate it with your local cluster credentials:

```ini
# MySQL Configuration
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_DATABASE=sakila

# MongoDB Configuration
MONGO_DB=mongodb://localhost:27017
MONGO_DB_NAME=find_me_movie_logs
MONGO_TABLE_NAME=queries
```

### 4. Run the Application
```bash
python main.py
```

---

## 📈 Quality Metrics

This project adheres strictly to Python industry guidelines and is fully vetted against modern linting engines:

```bash
pylint *.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (All modules verified)
```

---

## 📄 License
This project is open-source software licensed under the MIT License.
