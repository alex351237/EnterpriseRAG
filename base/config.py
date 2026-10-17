"""
config2 - 配置类（更好的版本）

说明：推荐使用 Pydantic Settings 彻底替代 configparser。它提供自动类型校验、环境变量自动映射及默认值约束。

Author: 骆昊
Version: 0.0.1
"""
import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

import logging

# 项目根目录（这里代码里省略了BASE_DIR定义，一般是 BASE_DIR = Path(__file__).resolve().parent）
# BASE_DIR = Path(__file__).resolve().parent


class Config(BaseSettings):
    """
    全局配置类，基于 pydantic-settings 实现
    自动从 .env 文件读取环境变量，覆盖类里面写的默认值
    会自动做类型校验、数值范围校验
    """

    # -------------------------- 本地文件目录配置 --------------------------
    # 数据根目录：存放rag系统运行产生的资源文件
    DATA_DIR: Path = BASE_DIR / 'rag_system/res'
    # 模型存放目录：本地大模型/embedding模型权重文件放在这里
    MODELS_DIR: Path = BASE_DIR / 'rag_system/models'
    # 原始文档目录：待解析、入库的PDF/Word/TXT等源文档
    DOCS_DIR: Path = BASE_DIR / 'rag_system/docs'

    # -------------------------- MySQL 数据库配置 --------------------------
    # MySQL服务地址
    MYSQL_HOST: str = 'localhost'
    # MySQL端口，默认3306
    MYSQL_PORT: int = 3306
    # MySQL登录用户名
    MYSQL_USER: str = 'root'
    # MySQL登录密码，无默认值，必须在.env里面配置
    MYSQL_PASSWORD: str
    # 使用的数据库名，这里是学科知识库 subjects_kg
    MYSQL_DATABASE: str = 'subjects_kg'

    # -------------------------- Redis 缓存配置 --------------------------
    # Redis服务地址
    REDIS_HOST: str = 'localhost'
    # Redis端口默认6379
    REDIS_PORT: int = 6379
    # Redis密码，无默认值，需要.env配置
    REDIS_PASSWORD: str
    # Redis使用的db编号，默认0号库
    REDIS_DB: int = 0
    # Redis缓存key前缀，用来区分不同业务，防止key冲突：ragpro:qa 代表RAG项目问答缓存
    CACHE_KEY_PREFIX: str = 'ragpro:qa'

    # -------------------------- Milvus 向量数据库配置（HNSW向量检索） --------------------------
    # Milvus向量库服务地址
    MILVUS_HOST: str = 'localhost'
    # Milvus默认端口19530
    MILVUS_PORT: int = 19530
    # Milvus逻辑数据库名称
    MILVUS_DATABASE_NAME: str = 'rag_enterprise'
    # Milvus集合名（相当于mysql的表），企业RAG向量集合
    MILVUS_COLLECTION_NAME: str = 'enterprise_rag'

    # -------------------------- LLM大模型配置 --------------------------
    # LLM模型名称：deepseek-flash
    LLM_MODEL_NAME: str = 'deepseek-flash'
    # 模型服务商，使用兼容OpenAI接口格式的调用方式
    LLM_MODEL_PROVIDER: str = 'openai'
    # 大模型接口地址，deepseek官方api地址
    LLM_BASE_URL: str = 'https://api.deepseek.com'

    # -------------------------- 文档分块 & 检索参数（RAG核心参数） --------------------------
    # 父块大小：父文档块字符长度，范围300~4000，默认1200；父子分块策略（父块检索，子块精细）
    PARENT_CHUNK_SIZE: int = Field(default=1200, ge=300, le=4000)
    # 子块大小：子文档块字符长度，范围50~1000，默认300
    CHILD_CHUNK_SIZE: int = Field(default=300, ge=50, le=1000)
    # 父块重叠长度：块之间重叠文本，用来解决上下文被切分断裂的问题，>=0，默认100
    PARENT_CHUNK_OVERLAP: int = Field(default=100, ge=0)
    # 子块重叠长度，默认20
    CHILD_CHUNK_OVERLAP: int = Field(default=20, ge=0)
    # 检索返回Top-K：向量检索召回多少个相似块，>=1，默认召回5条
    RETRIEVAL_K: int = Field(default=5, ge=1)
    # 候选倍数M：一般用于父块检索策略，先召回 M*K 候选再二次筛选，>=1，默认2倍
    CANDIDATE_M: int = Field(default=2, ge=1)

    # -------------------------- 日志配置 --------------------------
    # 日志文件路径
    LOG_FILE: Path = BASE_DIR / 'logs/app.log'
    # 文件日志输出级别：DEBUG级别，会记录详细调试信息
    FILE_HANDLER_LEVEL: int = logging.DEBUG
    # 控制台日志输出级别：DEBUG级别
    CONSOLE_HANDLER_LEVEL: int = logging.DEBUG

    # pydantic-settings配置
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / '.env'),  # 指定从项目根目录的.env文件读取环境变量
        env_file_encoding='utf-8',        # env文件编码utf8
        extra='ignore'                    # 忽略.env里面没有在Config类定义的多余字段，不报错
    )


# 实例化全局唯一配置对象，项目各处直接 import config 使用
config = Config()

