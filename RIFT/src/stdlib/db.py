"""
RIFT Standard Library - Database Module

Database connections and query operations for:
- PostgreSQL
- MySQL
- MongoDB
- SQLite (via generic SQL interface)
- Query Builder
"""

import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager


def create_db_module(interpreter) -> Dict[str, Any]:
    """Create the database module for RIFT."""
    
    # ========================================================================
    # Query Builder
    # ========================================================================
    
    class QueryBuilder:
        """Fluent SQL query builder."""
        
        def __init__(self, connection):
            self._connection = connection
            self._table_name = None
            self._select_cols = ['*']
            self._where_clauses = []
            self._where_params = []
            self._order_by = []
            self._limit_val = None
            self._offset_val = None
            self._joins = []
            self._group_by = []
            self._having = []
        
        def table(self, name: str) -> 'QueryBuilder':
            """Set the table name."""
            self._table_name = name
            return self
        
        def select(self, *columns) -> 'QueryBuilder':
            """Set columns to select."""
            if columns:
                self._select_cols = list(columns)
            return self
        
        def where(self, column: str, operator: str = '=', value: Any = None) -> 'QueryBuilder':
            """Add WHERE clause."""
            if value is None and operator != '=' and operator != '!=':
                # where("column", "value") shorthand
                value = operator
                operator = '='
            
            self._where_clauses.append(f"{column} {operator} ?")
            self._where_params.append(value)
            return self
        
        def where_in(self, column: str, values: List) -> 'QueryBuilder':
            """Add WHERE IN clause."""
            placeholders = ','.join(['?' for _ in values])
            self._where_clauses.append(f"{column} IN ({placeholders})")
            self._where_params.extend(values)
            return self
        
        def where_null(self, column: str) -> 'QueryBuilder':
            """Add WHERE IS NULL clause."""
            self._where_clauses.append(f"{column} IS NULL")
            return self
        
        def where_not_null(self, column: str) -> 'QueryBuilder':
            """Add WHERE IS NOT NULL clause."""
            self._where_clauses.append(f"{column} IS NOT NULL")
            return self
        
        def or_where(self, column: str, operator: str = '=', value: Any = None) -> 'QueryBuilder':
            """Add OR WHERE clause."""
            if value is None:
                value = operator
                operator = '='
            
            if self._where_clauses:
                self._where_clauses[-1] = f"({self._where_clauses[-1]} OR {column} {operator} ?)"
            else:
                self._where_clauses.append(f"{column} {operator} ?")
            self._where_params.append(value)
            return self
        
        def order(self, column: str, direction: str = 'ASC') -> 'QueryBuilder':
            """Add ORDER BY clause."""
            self._order_by.append(f"{column} {direction.upper()}")
            return self
        
        def limit(self, count: int) -> 'QueryBuilder':
            """Set LIMIT."""
            self._limit_val = count
            return self
        
        def offset(self, count: int) -> 'QueryBuilder':
            """Set OFFSET."""
            self._offset_val = count
            return self
        
        def join(self, table: str, first: str, operator: str, second: str,
                 join_type: str = 'INNER') -> 'QueryBuilder':
            """Add JOIN clause."""
            self._joins.append(f"{join_type} JOIN {table} ON {first} {operator} {second}")
            return self
        
        def left_join(self, table: str, first: str, operator: str, second: str) -> 'QueryBuilder':
            """Add LEFT JOIN."""
            return self.join(table, first, operator, second, 'LEFT')
        
        def right_join(self, table: str, first: str, operator: str, second: str) -> 'QueryBuilder':
            """Add RIGHT JOIN."""
            return self.join(table, first, operator, second, 'RIGHT')
        
        def group_by(self, *columns) -> 'QueryBuilder':
            """Add GROUP BY clause."""
            self._group_by.extend(columns)
            return self
        
        def having(self, clause: str, *params) -> 'QueryBuilder':
            """Add HAVING clause."""
            self._having.append(clause)
            self._where_params.extend(params)
            return self
        
        def _build_select(self) -> Tuple[str, List]:
            """Build SELECT query."""
            cols = ', '.join(self._select_cols)
            sql = f"SELECT {cols} FROM {self._table_name}"
            
            if self._joins:
                sql += ' ' + ' '.join(self._joins)
            
            if self._where_clauses:
                sql += ' WHERE ' + ' AND '.join(self._where_clauses)
            
            if self._group_by:
                sql += ' GROUP BY ' + ', '.join(self._group_by)
            
            if self._having:
                sql += ' HAVING ' + ' AND '.join(self._having)
            
            if self._order_by:
                sql += ' ORDER BY ' + ', '.join(self._order_by)
            
            if self._limit_val is not None:
                sql += f' LIMIT {self._limit_val}'
            
            if self._offset_val is not None:
                sql += f' OFFSET {self._offset_val}'
            
            return sql, self._where_params
        
        def get(self) -> List[Dict]:
            """Execute SELECT and return results."""
            sql, params = self._build_select()
            return self._connection.query(sql, params)
        
        def first(self) -> Optional[Dict]:
            """Get first result."""
            self._limit_val = 1
            results = self.get()
            return results[0] if results else None
        
        def count(self) -> int:
            """Get count of results."""
            self._select_cols = ['COUNT(*) as count']
            result = self.first()
            return result['count'] if result else 0
        
        def insert(self, data: Dict) -> int:
            """Insert a row."""
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            sql = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
            return self._connection.execute(sql, list(data.values()))
        
        def insert_many(self, rows: List[Dict]) -> int:
            """Insert multiple rows."""
            if not rows:
                return 0
            
            columns = ', '.join(rows[0].keys())
            placeholders = ', '.join(['?' for _ in rows[0]])
            sql = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
            
            count = 0
            for row in rows:
                self._connection.execute(sql, list(row.values()))
                count += 1
            
            return count
        
        def update(self, data: Dict) -> int:
            """Update rows."""
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            sql = f"UPDATE {self._table_name} SET {set_clause}"
            
            params = list(data.values())
            
            if self._where_clauses:
                sql += ' WHERE ' + ' AND '.join(self._where_clauses)
                params.extend(self._where_params)
            
            return self._connection.execute(sql, params)
        
        def delete(self) -> int:
            """Delete rows."""
            sql = f"DELETE FROM {self._table_name}"
            
            if self._where_clauses:
                sql += ' WHERE ' + ' AND '.join(self._where_clauses)
            
            return self._connection.execute(sql, self._where_params)
        
        def raw(self, sql: str, params: List = None) -> List[Dict]:
            """Execute raw SQL query."""
            return self._connection.query(sql, params or [])
    
    # ========================================================================
    # SQLite / Generic SQL Connection
    # ========================================================================
    
    class SQLConnection:
        """Generic SQL database connection."""
        
        def __init__(self, connection_string: str):
            self.connection_string = connection_string
            self._conn = None
            self._connect()
        
        def _connect(self):
            """Establish database connection."""
            # Parse connection string
            if self.connection_string.startswith('sqlite:'):
                # SQLite
                db_path = self.connection_string.replace('sqlite:///', '').replace('sqlite:', '')
                self._conn = sqlite3.connect(db_path if db_path else ':memory:')
                self._conn.row_factory = sqlite3.Row
            else:
                raise ValueError(f"Unsupported connection string: {self.connection_string}")
        
        def table(self, name: str) -> QueryBuilder:
            """Start building a query for a table."""
            return QueryBuilder(self).table(name)
        
        def query(self, sql: str, params: List = None) -> List[Dict]:
            """Execute a SELECT query and return results."""
            cursor = self._conn.cursor()
            cursor.execute(sql, params or [])
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        def execute(self, sql: str, params: List = None) -> int:
            """Execute an INSERT/UPDATE/DELETE and return affected rows."""
            cursor = self._conn.cursor()
            cursor.execute(sql, params or [])
            self._conn.commit()
            return cursor.rowcount
        
        def raw(self, sql: str, params: List = None) -> List[Dict]:
            """Execute raw SQL."""
            return self.query(sql, params)
        
        @contextmanager
        def transaction(self):
            """Transaction context manager."""
            try:
                yield
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
        
        def close(self):
            """Close the connection."""
            if self._conn:
                self._conn.close()
                self._conn = None
    
    # ========================================================================
    # PostgreSQL Connection
    # ========================================================================
    
    class PostgresConnection:
        """PostgreSQL database connection."""
        
        def __init__(self, connection_string: str):
            self.connection_string = connection_string
            self._conn = None
            self._pool = None
            self._connect()
        
        def _connect(self):
            """Establish database connection."""
            try:
                import psycopg2
                import psycopg2.extras
                
                self._conn = psycopg2.connect(self.connection_string)
            except ImportError:
                raise ImportError("psycopg2-binary required for PostgreSQL")
        
        def table(self, name: str) -> QueryBuilder:
            """Start building a query for a table."""
            return QueryBuilder(self).table(name)
        
        def query(self, sql: str, params: List = None) -> List[Dict]:
            """Execute a SELECT query."""
            import psycopg2.extras
            
            # Convert ? placeholders to %s
            sql = sql.replace('?', '%s')
            
            cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql, params or [])
            return [dict(row) for row in cursor.fetchall()]
        
        def execute(self, sql: str, params: List = None) -> int:
            """Execute an INSERT/UPDATE/DELETE."""
            sql = sql.replace('?', '%s')
            cursor = self._conn.cursor()
            cursor.execute(sql, params or [])
            self._conn.commit()
            return cursor.rowcount
        
        def raw(self, sql: str, params: List = None) -> List[Dict]:
            """Execute raw SQL."""
            return self.query(sql, params)
        
        @contextmanager
        def transaction(self):
            """Transaction context manager."""
            try:
                yield
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
        
        def close(self):
            """Close connection."""
            if self._conn:
                self._conn.close()
                self._conn = None
    
    # ========================================================================
    # MySQL Connection
    # ========================================================================
    
    class MySQLConnection:
        """MySQL database connection."""
        
        def __init__(self, connection_string: str):
            self.connection_string = connection_string
            self._conn = None
            self._connect()
        
        def _connect(self):
            """Establish database connection."""
            try:
                import mysql.connector
                
                # Parse connection string: mysql://user:pass@host:port/database
                if self.connection_string.startswith('mysql://'):
                    from urllib.parse import urlparse
                    parsed = urlparse(self.connection_string)
                    self._conn = mysql.connector.connect(
                        host=parsed.hostname or 'localhost',
                        port=parsed.port or 3306,
                        user=parsed.username,
                        password=parsed.password,
                        database=parsed.path.lstrip('/')
                    )
                else:
                    raise ValueError("Invalid MySQL connection string")
            except ImportError:
                raise ImportError("mysql-connector-python required for MySQL")
        
        def table(self, name: str) -> QueryBuilder:
            """Start building a query for a table."""
            return QueryBuilder(self).table(name)
        
        def query(self, sql: str, params: List = None) -> List[Dict]:
            """Execute a SELECT query."""
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(sql, params or [])
            return list(cursor.fetchall())
        
        def execute(self, sql: str, params: List = None) -> int:
            """Execute an INSERT/UPDATE/DELETE."""
            cursor = self._conn.cursor()
            cursor.execute(sql, params or [])
            self._conn.commit()
            return cursor.rowcount
        
        def raw(self, sql: str, params: List = None) -> List[Dict]:
            """Execute raw SQL."""
            return self.query(sql, params)
        
        @contextmanager
        def transaction(self):
            """Transaction context manager."""
            try:
                yield
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
        
        def close(self):
            """Close connection."""
            if self._conn:
                self._conn.close()
                self._conn = None
    
    # ========================================================================
    # MongoDB Connection
    # ========================================================================
    
    class MongoConnection:
        """MongoDB database connection."""
        
        def __init__(self, connection_string: str, database: str = None):
            self.connection_string = connection_string
            self._client = None
            self._db = None
            self._connect(database)
        
        def _connect(self, database: str = None):
            """Establish database connection."""
            try:
                from pymongo import MongoClient
                from urllib.parse import urlparse
                
                self._client = MongoClient(self.connection_string)
                
                # Get database from connection string or parameter
                if database:
                    self._db = self._client[database]
                else:
                    parsed = urlparse(self.connection_string)
                    db_name = parsed.path.lstrip('/')
                    if db_name:
                        self._db = self._client[db_name]
                    else:
                        self._db = self._client['test']
            except ImportError:
                raise ImportError("pymongo required for MongoDB")
        
        def collection(self, name: str) -> 'MongoCollection':
            """Get a collection."""
            return MongoCollection(self._db[name])
        
        def close(self):
            """Close connection."""
            if self._client:
                self._client.close()
                self._client = None
    
    class MongoCollection:
        """MongoDB collection wrapper."""
        
        def __init__(self, collection):
            self._collection = collection
        
        def find(self, query: Dict = None, projection: Dict = None) -> List[Dict]:
            """Find documents."""
            cursor = self._collection.find(query or {}, projection)
            return [self._serialize_doc(doc) for doc in cursor]
        
        def find_one(self, query: Dict = None) -> Optional[Dict]:
            """Find one document."""
            doc = self._collection.find_one(query or {})
            return self._serialize_doc(doc) if doc else None
        
        def insert(self, document: Dict) -> str:
            """Insert a document."""
            result = self._collection.insert_one(document)
            return str(result.inserted_id)
        
        def insert_many(self, documents: List[Dict]) -> List[str]:
            """Insert multiple documents."""
            result = self._collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        
        def update(self, query: Dict, update: Dict, upsert: bool = False) -> int:
            """Update documents."""
            if not any(k.startswith('$') for k in update.keys()):
                update = {'$set': update}
            result = self._collection.update_many(query, update, upsert=upsert)
            return result.modified_count
        
        def update_one(self, query: Dict, update: Dict, upsert: bool = False) -> int:
            """Update one document."""
            if not any(k.startswith('$') for k in update.keys()):
                update = {'$set': update}
            result = self._collection.update_one(query, update, upsert=upsert)
            return result.modified_count
        
        def delete(self, query: Dict) -> int:
            """Delete documents."""
            result = self._collection.delete_many(query)
            return result.deleted_count
        
        def delete_one(self, query: Dict) -> int:
            """Delete one document."""
            result = self._collection.delete_one(query)
            return result.deleted_count
        
        def count(self, query: Dict = None) -> int:
            """Count documents."""
            return self._collection.count_documents(query or {})
        
        def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
            """Run aggregation pipeline."""
            cursor = self._collection.aggregate(pipeline)
            return [self._serialize_doc(doc) for doc in cursor]
        
        def create_index(self, keys, **kwargs) -> str:
            """Create an index."""
            return self._collection.create_index(keys, **kwargs)
        
        def _serialize_doc(self, doc: Dict) -> Dict:
            """Serialize MongoDB document for RIFT."""
            if doc is None:
                return None
            
            result = {}
            for key, value in doc.items():
                if key == '_id':
                    result['_id'] = str(value)
                else:
                    result[key] = value
            return result
    
    # ========================================================================
    # Module Functions
    # ========================================================================
    
    def db_sql(connection_string: str) -> SQLConnection:
        """Create a generic SQL connection. Supports SQLite via 'sqlite:' prefix."""
        return SQLConnection(connection_string)
    
    def db_postgres(connection_string: str) -> PostgresConnection:
        """Create a PostgreSQL connection."""
        return PostgresConnection(connection_string)
    
    def db_mysql(connection_string: str) -> MySQLConnection:
        """Create a MySQL connection."""
        return MySQLConnection(connection_string)
    
    def db_mongo(connection_string: str, database: str = None) -> MongoConnection:
        """Create a MongoDB connection."""
        return MongoConnection(connection_string, database)
    
    return {
        'sql': db_sql,
        'postgres': db_postgres,
        'mysql': db_mysql,
        'mongo': db_mongo,
    }
