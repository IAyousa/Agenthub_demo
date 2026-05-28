"""
AgentHub Agent Service — H2 数据库连接管理

本模块负责 Python 进程与 Java 后端共享的 H2 文件数据库建立 JDBC 连接。

核心原理：
    由于 H2 是 Java 编写的嵌入式数据库，Python 无法直接通过 ODBC/DBAPI 驱动连接。
    解决方案是使用 JPype 启动一个内嵌 JVM，再通过 jaydebeapi（JDBC 桥接库）
    加载 H2 JDBC 驱动，实现 Python → JVM → H2 的调用链路。

架构示意：
    ┌──────────────┐    jaydebeapi     ┌──────────────────┐    JDBC     ┌──────────┐
    │  Python 代码  │ ────────────────► │  JPype JVM 进程   │ ────────►  │  H2 文件  │
    │  (CPython)   │ ◄──────────────── │  (org.h2.Driver) │ ◄────────  │ agenthub │
    └──────────────┘                   └──────────────────┘            └──────────┘

H2 AUTO_SERVER 模式：
    Java 后端通过 application.yml 配置了 AUTO_SERVER=TRUE，允许多个 JVM 进程
    同时连接同一个 H2 数据库文件。Python 启动的 JPype JVM 作为第二个进程接入。

jar 查找策略（按优先级）：
    1. 环境变量 H2_JAR_PATH 指定的路径
    2. agent-service/lib/h2.jar（手动放置）
    3. ~/.m2/repository/com/h2database/h2/（Maven 本地仓库，取最新版本）

连接 URL 格式：
    jdbc:h2:file:<db_path>;AUTO_SERVER=TRUE;IFEXISTS=TRUE
    - file:      文件模式（非内存模式）
    - AUTO_SERVER=TRUE  允许多进程连接
    - IFEXISTS=TRUE     数据库文件不存在时不自动创建（由 Java 端负责初始化）
"""

import os
import jaydebeapi
import jpype


def _find_h2_jar() -> str:
    """自动查找 H2 JDBC 驱动 jar 文件路径。

    查找优先级：
        1. 环境变量 H2_JAR_PATH — 开发/生产环境可手动指定
        2. agent-service/lib/h2.jar — 项目本地 lib 目录
        3. Maven 本地仓库 — ~/.m2/repository/com/h2database/h2/，取最新版本

    Returns:
        str: H2 jar 文件的绝对路径

    Raises:
        FileNotFoundError: 当所有路径都找不到 jar 文件时抛出
    """
    # 策略 1：检查环境变量 H2_JAR_PATH
    env_path = os.getenv("H2_JAR_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # 策略 2：检查项目本地 lib 目录
    lib_dir = os.path.join(os.path.dirname(__file__), "..", "..", "lib")
    lib_jar = os.path.join(lib_dir, "h2.jar")
    if os.path.exists(lib_jar):
        return lib_jar

    # 策略 3：搜索 Maven 本地仓库
    m2_repo = os.path.join(os.path.expanduser("~"), ".m2", "repository", "com", "h2database", "h2")
    if os.path.isdir(m2_repo):
        # 获取所有已安装的 H2 版本目录，按版本号降序排列（取最新）
        versions = sorted(
            [v for v in os.listdir(m2_repo) if os.path.isdir(os.path.join(m2_repo, v))],
            reverse=True
        )
        for v in versions:
            jar = os.path.join(m2_repo, v, f"h2-{v}.jar")
            if os.path.exists(jar):
                return jar

    # 全部未找到，给出明确的错误提示
    raise FileNotFoundError(
        "找不到 H2 JDBC 驱动 jar。请设置环境变量 H2_JAR_PATH 或将 h2.jar 放入 agent-service/lib/ 目录"
    )


def get_connection():
    """获取 H2 数据库的 JDBC 连接。

    连接流程：
        1. 查找 H2 JDBC 驱动 jar 文件
        2. 如果 JPype JVM 尚未启动，启动 JVM 并加载 H2 驱动
        3. 构造 JDBC URL（文件模式 + AUTO_SERVER + IFEXISTS）
        4. 建立 JDBC 连接并返回

    连接参数：
        - 用户名：sa（H2 默认超级管理员）
        - 密码：空（H2 默认无密码，与 Java 端 application.yml 一致）
        - IFEXISTS=TRUE：数据库文件由 Java 端负责创建，Python 不自动创建

    Returns:
        jaydebeapi.Connection: H2 JDBC 数据库连接对象
    """
    # 步骤 1：查找 H2 JDBC 驱动 jar
    jar = _find_h2_jar()

    # 步骤 2：启动 JPype JVM（全局单例，仅启动一次）
    # jpype.startJVM 是幂等的：如果 JVM 已启动则直接返回
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=[jar])

    # 步骤 3：构造数据库文件路径
    # shared-data/ 目录位于项目根目录，与 Java 后端共享
    db_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared-data")
    db_dir = os.path.abspath(db_dir)
    os.makedirs(db_dir, exist_ok=True)                      # 确保目录存在
    db_path = os.path.join(db_dir, "agenthub")
    db_path = db_path.replace("\\", "/")                     # Windows 反斜杠转正斜杠（JDBC URL 要求）

    # 步骤 4：构造 JDBC 连接 URL 并建立连接
    url = f"jdbc:h2:file:{db_path};AUTO_SERVER=TRUE;IFEXISTS=TRUE"

    conn = jaydebeapi.connect(
        "org.h2.Driver",     # H2 JDBC 驱动类全限定名
        url,                  # JDBC 连接 URL
        ["sa", ""],           # [用户名, 密码]
    )
    return conn


def close_connection(conn):
    """安全关闭数据库连接。

    Args:
        conn: jaydebeapi.Connection 或 None
    """
    if conn:
        try:
            conn.close()
        except Exception:
            pass                       # 忽略关闭时的异常，避免影响主流程
