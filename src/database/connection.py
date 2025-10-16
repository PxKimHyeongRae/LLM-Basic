"""
MariaDB 데이터베이스 연결 관리 모듈
"""

import os
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class DatabaseConnection:
    """MariaDB 데이터베이스 연결 관리 클래스"""

    def __init__(self, host=None, port=None, database=None, user=None, password=None):
        """
        데이터베이스 연결 초기화

        Args:
            host: DB 호스트 (기본값: 환경변수에서 로드)
            port: DB 포트 (기본값: 환경변수에서 로드)
            database: DB 이름 (기본값: 환경변수에서 로드)
            user: DB 사용자 (기본값: 환경변수에서 로드)
            password: DB 비밀번호 (기본값: 환경변수에서 로드)
        """
        self.host = host or os.getenv('DB_HOST')
        self.port = int(port or os.getenv('DB_PORT', 3307))
        self.database = database or os.getenv('DB_NAME')
        self.user = user or os.getenv('DB_USER')
        self.password = password or os.getenv('DB_PASSWORD')

        self.connection = None
        self._connect()

    def _connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=True
            )
            logger.info(f"데이터베이스 연결 성공: {self.host}:{self.port}/{self.database}")
        except pymysql.Error as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise

    def reconnect(self):
        """데이터베이스 재연결"""
        try:
            if self.connection:
                self.connection.close()
        except:
            pass
        self._connect()

    def execute_query(self, query, params=None):
        """
        SELECT 쿼리 실행

        Args:
            query: SQL 쿼리문
            params: 쿼리 파라미터 (튜플 또는 딕셔너리)

        Returns:
            list: 쿼리 결과 (딕셔너리 리스트)
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except pymysql.Error as e:
            logger.error(f"쿼리 실행 실패: {e}")
            logger.error(f"Query: {query}")
            # 연결 끊김 시 재연결 시도
            if e.args[0] in (2006, 2013):  # MySQL server has gone away
                logger.info("재연결 시도 중...")
                self.reconnect()
                with self.connection.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                    return result
            raise

    def execute_one(self, query, params=None):
        """
        단일 결과 조회

        Args:
            query: SQL 쿼리문
            params: 쿼리 파라미터

        Returns:
            dict: 단일 쿼리 결과
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result
        except pymysql.Error as e:
            logger.error(f"쿼리 실행 실패: {e}")
            raise

    def test_connection(self):
        """연결 테스트"""
        try:
            result = self.execute_one("SELECT 1 as test")
            return result['test'] == 1
        except:
            return False

    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            logger.info("데이터베이스 연결 종료")

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
