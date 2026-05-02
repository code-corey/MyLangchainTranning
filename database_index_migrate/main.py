import os

import pymysql
import pyodbc
import re
from typing import List, Dict, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库连接配置
SQLSERVER_CONFIG = {
    'server': 'xxxxx',
    'database': 'xxxx',
    'username': 'xxxx',
    'password': os.getenv("SQLSERVER_CONFIG_PASSWORD"),
    'driver': '{ODBC Driver 17 for SQL Server}'  # 可能需要根据实际情况调整
}

MYSQL_CONFIG = {
    'host': 'xxxxx',
    'user': 'xxx',
    'password': os.getenv("MYSQL_CONFIG_PASSWORD"),
    'database': 'xxxx',
    'charset': 'utf8mb4'
}


class IndexMigrator:
    def __init__(self):
        self.sqlserver_conn = None
        self.mysql_conn = None

    def connect(self):
        """建立数据库连接"""
        try:
            if not SQLSERVER_CONFIG.get('password'):
                raise ValueError("缺少环境变量: SQLSERVER_CONFIG_PASSWORD")
            if not MYSQL_CONFIG.get('password'):
                raise ValueError("缺少环境变量: MYSQL_CONFIG_PASSWORD")

            # 连接SQL Server
            conn_str = (
                f"DRIVER={SQLSERVER_CONFIG['driver']};"
                f"SERVER={SQLSERVER_CONFIG['server']};"
                f"DATABASE={SQLSERVER_CONFIG['database']};"
                f"UID={SQLSERVER_CONFIG['username']};"
                f"PWD={SQLSERVER_CONFIG['password']};"
                f"MultipleActiveResultSets=true;"
            )
            self.sqlserver_conn = pyodbc.connect(conn_str)
            logger.info("成功连接到SQL Server")

            # 连接MySQL
            self.mysql_conn = pymysql.connect(**MYSQL_CONFIG)
            logger.info("成功连接到MySQL")

            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def get_mysql_tables(self) -> List[str]:
        """获取MySQL中的所有表名"""
        with self.mysql_conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"在MySQL中找到 {len(tables)} 张表")
            return tables

    def get_sqlserver_indexes(self, table_name: str) -> Dict:
        """从SQL Server获取指定表的索引信息"""
        query = """
            SELECT
                t.name AS table_name,
                i.name AS index_name,
                i.is_primary_key,
                i.is_unique,
                i.type_desc,
                STUFF((
                    SELECT ',' + col.name
                    FROM sys.index_columns ic
                    JOIN sys.columns col
                        ON ic.object_id = col.object_id
                        AND ic.column_id = col.column_id
                    WHERE ic.object_id = i.object_id
                        AND ic.index_id = i.index_id
                        AND ic.is_included_column = 0
                    ORDER BY ic.key_ordinal
                    FOR XML PATH('')
                ), 1, 1, '') AS index_columns,
                STUFF((
                    SELECT ',' + col.name
                    FROM sys.index_columns ic
                    JOIN sys.columns col
                        ON ic.object_id = col.object_id
                        AND ic.column_id = col.column_id
                    WHERE ic.object_id = i.object_id
                        AND ic.index_id = i.index_id
                        AND ic.is_included_column = 1
                    ORDER BY ic.key_ordinal
                    FOR XML PATH('')
                ), 1, 1, '') AS included_columns
            FROM sys.tables t
            JOIN sys.indexes i ON t.object_id = i.object_id
            WHERE t.name = ?
                AND i.name IS NOT NULL
                AND i.type_desc != 'HEAP'
            ORDER BY i.is_primary_key DESC, i.name
        """

        try:
            cursor = self.sqlserver_conn.cursor()
            try:
                cursor.execute(query, (table_name,))
                rows = cursor.fetchall()
            finally:
                cursor.close()

            if not rows:
                return None

            indexes = {
                'primary_key': None,
                'unique_indexes': [],
                'normal_indexes': []
            }

            for row in rows:
                index_info = {
                    'name': row.index_name,
                    'columns': row.index_columns.split(',') if row.index_columns else [],
                    'included_columns': row.included_columns.split(',') if row.included_columns else [],
                    'is_unique': row.is_unique
                }

                if row.is_primary_key:
                    indexes['primary_key'] = index_info
                elif row.is_unique:
                    indexes['unique_indexes'].append(index_info)
                else:
                    indexes['normal_indexes'].append(index_info)

            return indexes
        except Exception as e:
            logger.error(f"获取表 {table_name} 的索引信息失败: {e}")
            return None

    def check_columns_exist(self, table_name: str, columns: List[str]) -> Tuple[bool, List[str]]:
        """检查MySQL表中的列是否存在"""
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = %s
                """,
                (MYSQL_CONFIG['database'], table_name),
            )
            existing_columns = [row[0] for row in cursor.fetchall()]

            existing_columns_lower = {col.lower() for col in existing_columns if col is not None}
            missing_columns = [col for col in columns if col.lower() not in existing_columns_lower]
            return len(missing_columns) == 0, missing_columns

    def primary_key_exists(self, table_name: str) -> bool:
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = %s
                  AND CONSTRAINT_TYPE = 'PRIMARY KEY'
                """,
                (MYSQL_CONFIG['database'], table_name),
            )
            return (cursor.fetchone() or (0,))[0] > 0

    def index_exists(self, table_name: str, index_name: str) -> bool:
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = %s
                  AND INDEX_NAME = %s
                LIMIT 1
                """,
                (MYSQL_CONFIG['database'], table_name, index_name),
            )
            return cursor.fetchone() is not None

    def normalize_index_name(self, table_name: str, index_name: str) -> str:
        name = (index_name or "").replace("`", "_").strip()
        name = re.sub(r"\s+", "_", name)
        if not name:
            name = f"idx_{table_name}"
        return name[:64]

    def make_unique_index_name(self, table_name: str, desired_name: str) -> str:
        base = self.normalize_index_name(table_name, desired_name)
        if not self.index_exists(table_name, base):
            return base
        for i in range(2, 1000):
            suffix = f"_{i}"
            candidate = f"{base[:64 - len(suffix)]}{suffix}"
            if not self.index_exists(table_name, candidate):
                return candidate
        raise ValueError(f"无法为表 {table_name} 生成可用索引名: {desired_name}")

    def create_primary_key(self, table_name: str, pk_info: Dict) -> bool:
        """创建主键"""
        if not pk_info or not pk_info['columns']:
            return True

        if self.primary_key_exists(table_name):
            logger.info(f"表 {table_name} 已存在主键，跳过")
            return True

        # 检查列是否存在
        columns_exist, missing = self.check_columns_exist(table_name, pk_info['columns'])
        if not columns_exist:
            logger.warning(f"表 {table_name} 主键列 {missing} 不存在，跳过")
            return False

        columns_str = '`, `'.join(pk_info['columns'])
        sql = f"ALTER TABLE `{table_name}` ADD PRIMARY KEY (`{columns_str}`)"

        try:
            with self.mysql_conn.cursor() as cursor:
                cursor.execute(sql)
                self.mysql_conn.commit()
                logger.info(f"✓ 表 {table_name} 主键创建成功: {pk_info['columns']}")
                return True
        except Exception as e:
            logger.error(f"表 {table_name} 主键创建失败: {e}")
            return False

    def create_index(self, table_name: str, index_info: Dict, index_type: str) -> bool:
        """创建普通索引或唯一索引"""
        if not index_info['columns']:
            return True

        # 检查列是否存在
        columns_exist, missing = self.check_columns_exist(table_name, index_info['columns'])
        if not columns_exist:
            logger.warning(f"表 {table_name} 索引 {index_info['name']} 的列 {missing} 不存在，跳过")
            return False

        # MySQL索引名长度限制为64字符
        index_name = self.make_unique_index_name(table_name, index_info['name'])
        columns_str = '`, `'.join(index_info['columns'])

        if index_type == 'unique':
            sql = f"CREATE UNIQUE INDEX `{index_name}` ON `{table_name}` (`{columns_str}`)"
        else:
            sql = f"CREATE INDEX `{index_name}` ON `{table_name}` (`{columns_str}`)"

        # 处理包含列（MySQL 8.0+ 支持，但一般场景较少用）
        if index_info['included_columns'] and index_type == 'normal':
            # MySQL不支持SQL Server的INCLUDE列，但可以创建覆盖索引
            all_columns = index_info['columns'] + index_info['included_columns']
            columns_str = '`, `'.join(all_columns)
            sql = f"CREATE INDEX `{index_name}` ON `{table_name}` (`{columns_str}`)"
            logger.info(f"  已将包含列 {index_info['included_columns']} 添加到索引中")

        try:
            with self.mysql_conn.cursor() as cursor:
                cursor.execute(sql)
                self.mysql_conn.commit()
                logger.info(f"✓ 表 {table_name} {index_type}索引创建成功: {index_info['name']}")
                return True
        except Exception as e:
            logger.error(f"表 {table_name} 索引 {index_info['name']} 创建失败: {e}")
            return False

    def migrate_all_indexes(self):
        """迁移所有表的索引"""
        tables = self.get_mysql_tables()

        success_count = 0
        fail_count = 0

        for table_name in tables:
            logger.info(f"\n处理表: {table_name}")

            # 获取SQL Server中的索引定义
            indexes = self.get_sqlserver_indexes(table_name)

            if not indexes:
                logger.warning(f"表 {table_name} 在SQL Server中没有找到索引定义或查询失败")
                continue

            # 创建主键
            if indexes['primary_key']:
                if self.create_primary_key(table_name, indexes['primary_key']):
                    success_count += 1
                else:
                    fail_count += 1

            # 创建唯一索引
            for idx in indexes['unique_indexes']:
                if self.create_index(table_name, idx, 'unique'):
                    success_count += 1
                else:
                    fail_count += 1

            # 创建普通索引
            for idx in indexes['normal_indexes']:
                if self.create_index(table_name, idx, 'normal'):
                    success_count += 1
                else:
                    fail_count += 1

        logger.info(f"\n{'=' * 50}")
        logger.info(f"索引迁移完成！成功: {success_count}, 失败: {fail_count}")
        logger.info(f"{'=' * 50}")

    def verify_indexes(self):
        """验证MySQL中的索引"""
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    TABLE_NAME,
                    INDEX_NAME,
                    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as COLUMNS,
                    NON_UNIQUE
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = '{MYSQL_CONFIG['database']}'
                GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE
                ORDER BY TABLE_NAME, INDEX_NAME
            """)

            indexes = cursor.fetchall()
            logger.info(f"\nMySQL中当前共有 {len(indexes)} 个索引")

            # 按表分组显示
            current_table = None
            for idx in indexes:
                if idx[0] != current_table:
                    current_table = idx[0]
                    logger.info(f"\n表 {current_table}:")
                idx_type = "唯一索引" if idx[3] == 0 else "普通索引"
                logger.info(f"  - {idx[1]} ({idx_type}): {idx[2]}")

    def close(self):
        """关闭数据库连接"""
        if self.sqlserver_conn:
            self.sqlserver_conn.close()
        if self.mysql_conn:
            self.mysql_conn.close()
        logger.info("数据库连接已关闭")


def main():
    migrator = IndexMigrator()

    try:
        # 连接数据库
        if not migrator.connect():
            logger.error("数据库连接失败，请检查配置")
            return

        # 执行迁移
        migrator.migrate_all_indexes()

        # 验证结果
        migrator.verify_indexes()

    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close()


if __name__ == "__main__":
    main()
