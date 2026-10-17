# EnterpriseRAG
# Enterprise\-grade RAG System

> 企业级RAG系统 \| FAQ知识库 \+ 向量检索，基于 MySQL \+ Milvus \+ BGE\-M3
>
> 

## 简介

本项目是一套面向企业内部知识库问答的**企业级RAG（Retrieval\-Augmented Generation）**系统。

- **MySQL**：存储FAQ结构化数据、问答对、文档元信息、权限、操作日志

- **Milvus**：向量数据库，使用HNSW索引存储文本向量，负责语义相似度检索

- **BGE\-M3**：多模态Embedding模型，支持稠密向量检索、稀疏检索、多语言，作为核心检索模型

- 采用**父子分块\(Parent\-Child Chunk\)**策略优化召回效果，支持大文档解析、向量化入库、语义检索、LLM生成回答

- LLM默认使用DeepSeek（兼容OpenAI接口协议，可快速切换其他服务商）

适合场景：企业FAQ智能问答、内部文档知识库、业务手册检索、客服知识库。

## 技术栈

| 模块          | 选型                       | 说明                                |
| ------------- | -------------------------- | ----------------------------------- |
| 后端框架      | Python                     | 核心业务                            |
| 配置管理      | Pydantic Settings          | 环境配置、自动校验，`.env`加载      |
| 关系数据库    | MySQL                      | FAQ问答对、文档元数据、业务数据存储 |
| 向量数据库    | Milvus 2\.x                | 向量存储 \& ANN检索（HNSW索引）     |
| 缓存          | Redis                      | 问答结果缓存、限流、去重            |
| Embedding模型 | BGE\-M3                    | 稠密\+稀疏混合检索，提升召回        |
| LLM           | DeepSeek\(OpenAI兼容接口\) | 答案生成、对话总结                  |
| 文档分块      | Parent\-Child Chunk        | 子块向量化检索，父块提供完整上下文  |
| 日志          | Python logging             | 分级日志输出，文件\+控制台双落盘    |

## 目录结构

```
rag_enterprise/
├── rag_system/
│   ├── res/                # 运行资源目录
│   ├── models/             # BGE-M3等本地模型存放目录
│   ├── docs/               # 原始待解析文档(PDF/MD/TXT/DOCX)
│   ├── faq/                # FAQ导入脚本、faq初始化sql
│   ├── chunker/            # 文档解析、父子分块逻辑
│   ├── embedding/          # BGE-M3封装、向量生成
│   ├── milvus_store/       # Milvus连接、索引构建、检索逻辑
│   ├── mysql_store/        # MySQL连接、FAQ CRUD、元数据管理
│   ├── llm/                # LLM调用、prompt管理
│   ├── cache/              # Redis缓存封装
│   └── rag_pipeline.py     # RAG主流程：检索 -> 重排 -> 组装prompt -> LLM回答
├── logs/
│   └── app.log             # 系统运行日志
├── config.py               # 全局配置类
├── .env.example            # 环境变量模板
├── requirements.txt        # Python依赖包
├── main.py                 # 入口服务/命令行入口
└── README.md               # 项目说明文档
```

## 环境准备

### 1\. 基础服务部署

需要提前启动以下服务：

- MySQL 8\.0\+

- Redis 6\.0\+

- Milvus 2\.4\+（推荐使用Docker部署，默认端口19530）

> Milvus 建议创建数据库 `rag_enterprise`，集合 `enterprise_rag`，索引类型 HNSW
>
> 

### 2\. Python环境

Python \>= 3\.10

```bash
# 安装依赖
pip install -r requirements.txt
```

### 3\. 模型准备

BGE\-M3 模型自动从 HuggingFace 拉取，或者手动下载放到 `rag_system/models/`

- 模型名称：`BAAI/bge-m3`

- 支持：稠密向量dense、稀疏向量sparse、多语言、长文本

## 配置说明

复制环境变量模板，修改参数

```bash
cp .env.example .env
```

`.env` 关键配置项（和 `config.py` 一一对应）

```env
# MySQL
MYSQL_PASSWORD=xxxxxx
# Redis
REDIS_PASSWORD=xxxxxx
# LLM
LLM_MODEL_NAME=deepseek-flash
LLM_BASE_URL=https://api.deepseek.com
```

> ⚠️ MYSQL\_PASSWORD、REDIS\_PASSWORD 为必填项，缺失会启动报错；分块参数、检索K值、缓存前缀均可在`.env`中覆盖默认值
>
> 

配置文件 `config.py` 采用 `pydantic-settings`，自动读取`.env`并做参数校验，包含：

- 目录路径

- MySQL / Redis / Milvus 连接信息

- LLM接口信息

- 父子分块大小、重叠长度、检索TopK、候选数量

- 日志级别

## 快速启动

### 1\. 初始化MySQL FAQ表

执行SQL脚本，创建FAQ表、文档元数据表

```bash
python rag_system/mysql_store/init_db.py
```

### 2\. 初始化Milvus集合 \& HNSW索引

```bash
python rag_system/milvus_store/init_collection.py
```

### 3\. 导入FAQ知识库

支持两种方式：

1. 批量导入FAQ问答对（优先用于客服FAQ）

```bash
python rag_system/faq/import_faq.py --file ./faq/faq_data.csv
```

1. 导入文档，自动解析、分块、向量化入库

```bash
python rag_system/chunker/ingest_docs.py
```

### 4\. 启动RAG问答服务

```bash
python main.py
```

## 核心流程说明（RAG Pipeline）

1. **用户提问**

2. **BGE\-M3编码问题**，生成稠密向量（可选稀疏向量做混合检索）

3. **Milvus HNSW近似检索**，召回 `RETRIEVAL_K` 个子块

4. 根据子块ID关联，取出对应的**父块完整上下文**

5. 拼接Prompt，送入LLM（DeepSeek）生成答案

6. 结果写入Redis缓存，相同问题直接返回缓存加速

7. 问答记录写入MySQL，用于后续知识库迭代、统计

> FAQ优先逻辑：会先检索MySQL内精准FAQ匹配，命中则直接返回FAQ答案，跳过向量检索流程，提升FAQ场景准确率与速度。
>
> 

## 参数调优指引（重点）

在`.env`修改下面参数，平衡召回率、速度、上下文完整性

| 参数                   | 含义                     | 建议范围    |
| ---------------------- | ------------------------ | ----------- |
| PARENT\_CHUNK\_SIZE    | 父块大小（完整上下文）   | 800 \~ 2000 |
| CHILD\_CHUNK\_SIZE     | 子块大小（用于向量检索） | 200 \~ 500  |
| PARENT\_CHUNK\_OVERLAP | 父块重叠                 | 100 \~ 200  |
| CHILD\_CHUNK\_OVERLAP  | 子块重叠                 | 20 \~ 80    |
| RETRIEVAL\_K           | 向量检索召回数量         | 3 \~ 10     |
| CANDIDATE\_M           | 候选放大倍数             | 1 \~ 3      |

> Milvus侧：HNSW索引参数 `M`、`ef_construction` 在集合初始化脚本内配置，影响建索引耗时和检索召回质量。
>
> 

## 功能特性

- ✅ FAQ精准匹配 \+ 文档语义检索双通路，FAQ优先，适合客服知识库

- ✅ Parent\-Child 父子分块，解决长上下文丢失问题

- ✅ BGE\-M3混合检索（稠密\+稀疏，可扩展）

- ✅ Milvus HNSW向量索引，支持百万级向量秒级检索

- ✅ Redis问答缓存，降低LLM调用成本

- ✅ 全链路日志记录，便于排查检索召回问题

- ✅ 环境变量配置，支持开发/测试/生产多环境切换

- ✅ 参数强校验，避免非法配置导致系统异常

- ✅ 支持增量文档入库，无需重建全部向量索引

## 待扩展功能（企业化增强方向）

- 用户权限 \& 多租户知识库隔离（Milvus多Collection/MySQL权限控制）

- 检索重排器Reranker，进一步提升召回精度

- 问答反馈机制（用户点赞/踩，回写知识库）

- 知识库管理后台（Web页面，上传、编辑FAQ、查看问答记录）

- 向量数据定时GC、Milvus软删除清理

- 接口鉴权、限流、链路追踪

- 评估模块：自动测试召回率、问答准确率

## 依赖参考 requirements\.txt

```txt
pydantic-settings>=2.0
pydantic>=2.0
pymysql
redis
pymilvus>=2.4.0
torch
transformers
sentence-transformers
python-dotenv
```

## 许可证

MIT

> （注：部分内容由豆包工作 AI 生成）