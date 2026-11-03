"""
Author  :Alex Aug
Date    :2026/11/3 20:06
describe:
"""

from pymilvus import DataType, AsyncMilvusClient

from backend.config import settings
from backend.core.logger import setup_logger, logger


def build_schema(client: AsyncMilvusClient):
    """构建集合 schema：稠密 + 稀疏双向量 + 标量字段（含 tenant_id）。"""
    schema = client.create_schema(auto_id=False,
                                  enable_dynamic_field=True,
                                  partition_key_fields=['tenant_id'],)

    schema.add_field('id',               DataType.VARCHAR, is_primary=True, max_length=64)
    schema.add_field('embedding',        DataType.FLOAT_VECTOR, dim=settings.bge_embedding_dim)
    schema.add_field('sparse_embedding', DataType.SPARSE_FLOAT_VECTOR)
    schema.add_field('content',          DataType.VARCHAR, max_length=4096)
    schema.add_field('tenant_id',        DataType.VARCHAR, max_length=64)
    schema.add_field('chunk_index',      DataType.INT64)
    schema.add_field('document_id',      DataType.VARCHAR, max_length=64)
    schema.add_field('course_id',        DataType.VARCHAR, max_length=64)
    schema.add_field('source_location',  DataType.VARCHAR, max_length=256)
    schema.add_field('chunk_type',       DataType.VARCHAR, max_length=32)
    schema.add_field('version',          DataType.VARCHAR, max_length=32)
    schema.add_field('updated_at',       DataType.INT64)

    return schema


def build_index_params(client: AsyncMilvusClient):
    """构建索引：稠密 HNSW、稀疏 SPARSE_INVERTED、标量 INVERTED。"""
    index_params = client.prepare_index_params()

    # 稠密向量：HNSW + COSINE（语义相似度）
    index_params.add_index(
        field_name='embedding',
        index_type='HNSW',
        metric_type='COSINE',
        params={'M': 16, 'efConstruction': 256}
    )

    # 稀疏向量：SPARSE_INVERTED_INDEX + IP（内积）；drop_ratio_build 丢弃最低权重 token 省存储
    index_params.add_index(
        field_name='sparse_embedding',
        index_type='SPARSE_INVERTED_INDEX',
        metric_type='IP',
        params={'drop_ratio_build': 0.2}
    )

    # 标量字段：INVERTED 索引，加速 filter 过滤
    index_params.add_index(field_name='tenant_id', index_type='INVERTED')
    index_params.add_index(field_name='course_id', index_type='INVERTED')

    return index_params


async def main():
    setup_logger(console_level='DEBUG')

    milvus_client = AsyncMilvusClient(uri=settings.milvus_uri)

    if await milvus_client.has_collection(settings.collection_name):
        logger.info(f'删除集合 {settings.collection_name}')
        await milvus_client.drop_collection(settings.collection_name)

    await milvus_client.create_collection(
        collection_name=settings.collection_name,
        schema=build_schema(milvus_client),
        index_params=build_index_params(milvus_client),
    )
    logger.info(f'✅ 集合 {settings.collection_name} 创建完成')
    logger.info(f'当前集合: {await milvus_client.list_collections()}')
    logger.warning("⚠️ 集合已重建，原有数据已清空，请重新运行 build_knowledge_base.py 导入数据")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
