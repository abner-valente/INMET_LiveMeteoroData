from __future__ import annotations
import pandas as pd
import pyodbc
import logging
from dataclasses import dataclass
from typing import Optional, Mapping, Any, Literal
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv(encoding="utf-8") #carrega variaveis do .env

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class DBConfig:
    """
    Configuração de conexão.
    Para SQL Server:
      dialect="mssql", driver="pyodbc" (ou "pymssql")
    Para PostgreSQL:
      dialect="postgresql", driver="psycopg2" (ou "psycopg")
    
    Uso:
      # Conexão padrão (sem prefixo)
      config = DBConfig.from_env()
      
      # Conexão específica (com prefixo)
      config_mssql = DBConfig.from_env(prefix="MSSQL")
      config_postgres = DBConfig.from_env(prefix="POSTGRES")
    """
    dialect: str
    driver: Optional[str]
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @staticmethod
    def _clean(v: str) -> str:
        # remove espaços, CRLF, aspas e BOM
        return (v or "").strip().strip('"').strip("'").replace("\ufeff", "")
    
    @classmethod
    def from_env(cls: type[DBConfig], prefix: str = "DB") -> "DBConfig":
        """
        Cria DBConfig a partir de variáveis de ambiente com prefixo opcional.
        
        Args:
            prefix: Prefixo das variáveis (ex: "DB", "MSSQL", "POSTGRES")
        
        Exemplo:
            config = DBConfig.from_env("MSSQL")  # Lê MSSQL_HOST, MSSQL_PORT, etc.
        """
        return cls(
        dialect=cls._clean(os.getenv(f"{prefix}_DIALECT", "mssql")),
        driver=cls._clean(os.getenv(f"{prefix}_DRIVER", "pyodbc")) or None,
        host=cls._clean(os.getenv(f"{prefix}_HOST", "localhost")),
        port=int(cls._clean(os.getenv(f"{prefix}_PORT", "1433"))),
        database=cls._clean(os.getenv(f"{prefix}_NAME", "")),
        user=cls._clean(os.getenv(f"{prefix}_USER", "")),
        password=cls._clean(os.getenv(f"{prefix}_PASSWORD", "")),
    )
        

class DBClient: 
    """
    Cliente simples para:
    - abrir Engine
    - executar SELECT e retornar DataFrame
    - executar comandos (INSERT/UPDATE/DDL)
    - inserir DataFrame em tabela (to_sql)
    """

    def __init__(self, config: DBConfig, echo: bool = False):
        self.config = config
        self.echo = echo
        self._engine: Optional[Engine] = None
        logger.info(f"DBClient inicializado: {config.dialect}+{config.driver}://{config.host}:{config.port}/{config.database}")

    def _build_url(self) -> str:
        """
        Constrói a URL de conexão apropriada para o banco.
        Para SQL Server com pyodbc, usa formato ODBC completo.
        Para outros bancos, usa formato padrão.
        """
        
        if self.config.dialect == "mssql" and self.config.driver == "pyodbc":
            # Para SQL Server com pyodbc, usar formato ODBC completo
            available_drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
            
            if not available_drivers:
                logger.error("Nenhum driver ODBC para SQL Server encontrado. Verifique a instalação do driver ODBC.")
                raise Exception("Nenhum driver ODBC para SQL Server encontrado.")
                
            preferred_order = [
                'ODBC Driver 18 for SQL Server',
                'ODBC Driver 17 for SQL Server',
                'ODBC Driver 13 for SQL Server',
                'ODBC Driver 11 for SQL Server',
                'SQL Server Native Client 11.0',
                'SQL Server'
            ]
            
            selected_driver = None
            
            for preferred in preferred_order: # tenta encontrar o driver preferido na lista de drivers disponíveis possíveis
                if preferred in available_drivers:
                    selected_driver = preferred
                    break
            
            if not selected_driver:
                selected_driver = available_drivers[0]
                logger.warning(f"Nenhum driver ODBC preferido encontrado. Usando o primeiro disponível: {selected_driver}")
            
            logger.info(f"Usando driver ODBC: {selected_driver}")
            
            # Parâmetros ODBC para SQL Server
            params = (
                f'DRIVER={{{selected_driver}}};'
                f'SERVER={self.config.host},{self.config.port};'
                f'DATABASE={self.config.database};'
                f'UID={self.config.user};'
                f'PWD={self.config.password};'
                f'TrustServerCertificate=yes;'
            )
            return f'mssql+pyodbc:///?odbc_connect={quote_plus(params)}'
        
        else:
            # Para outros bancos (PostgreSQL, MySQL, etc.), usar formato padrão
            # Fazer URL encoding de user e password para lidar com caracteres especiais
            driver_part = f"+{self.config.driver}" if self.config.driver else ""
            user_encoded = quote_plus(self.config.user)
            password_encoded = quote_plus(self.config.password)
            return (
                f"{self.config.dialect}{driver_part}://"
                f"{user_encoded}:{password_encoded}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
            )

    def engine(self) -> Engine:
        if self._engine is None:
            logger.info("Criando engine do SQLAlchemy...")
            url = self._build_url()
            self._engine = create_engine(url, echo=self.echo, future=True)
            logger.info("Engine criado com sucesso")
        return self._engine

    """
    Métodos de execução de SQL (DDL, DML) e manipulação de DataFrames
    """

    def query_df(self, sql: str, params: Optional[Mapping[str, Any]] = None,) -> pd.DataFrame:
        """
        Executa SELECT e retorna DataFrame.
        Use params para SQL com :params ou %(params)s, dependendo do driver.
        """
        logger.debug("Executando query SELECT...")
        with self.engine().connect() as conn:
            df = pd.read_sql(text(sql), conn, params=params)
        logger.info(f"Query executada: {len(df)} registros retornados")
        
        return df

    def execute_ddl(self, sql: str, params: Optional[Mapping[str, Any]] = None,) -> int:
        """
        Executa comandos (INSERT/UPDATE/DELETE/DDL).
        Retorna o rowcount (quando aplicável).
        """
        logger.debug("Executando comando SQL...")
        with self.engine().begin() as conn:  # begin() já faz commit
            result = conn.execute(text(sql), params or {})
            rowcount = result.rowcount if result.rowcount is not None else 0
        logger.info(f"Comando executado: {rowcount} linhas afetadas")
        
        return rowcount

    def df_to_table(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: Optional[str] = None,
        if_exists: Literal["fail", "replace", "append"] = "append",
        chunksize: int = 1000,
    ) -> None:
        """
        Insere DataFrame no banco.
        if_exists: "append" | "replace" | "fail"
        """
        
        # --- proteção contra limite de parâmetros (psycopg/postgres) ---
        driver = (self.config.driver or "").lower()
        dialect = (self.config.dialect or "").lower()
        
        if "postgres" in dialect and "psycopg" in driver:
            ncols = max(1, len(df.columns))
            max_params = 65535
            max_rows_safe = max(1, (max_params // ncols) - 1)  # margem de segurança
            if chunksize > max_rows_safe:
                logger.warning(
                    f"chunksize={chunksize} reduzido para {max_rows_safe} "
                    f"para evitar limite de parâmetros ({ncols} colunas)."
                )
                chunksize = max_rows_safe
        
        logger.info(f"Inserindo {len(df)} registros na tabela {table_name} (modo: {if_exists})...")
        df.to_sql(
            name=table_name,
            con=self.engine(),
            schema=schema,
            if_exists=if_exists,
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        logger.info(f"Inserção concluída: {len(df)} registros em {table_name}")

    def dispose(self) -> None:
        """Fecha conexões do pool."""
        if self._engine is not None:
            logger.info("Fechando conexões do pool de banco de dados...")
            self._engine.dispose()
            self._engine = None
            logger.info("Conexões fechadas")