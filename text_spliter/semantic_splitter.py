"""
Author  :Alex Aug
Date    :2026/11/6 9:07
describe:
"""
import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

from base.config import config, BASE_DIR

logger = logging.getLogger(f'{BASE_DIR.name}.{__name__}')


class BgeSemanticSplitter:
    """基于 BGE-M3 向量模型的语义切分器"""

    def __init__(
        self,
        model_path: str | Path | None = None,
        device: str = 'cpu',
        breakpoint_threshold_type: str = 'percentile',
        breakpoint_threshold_amount: float = 80.0
    ):
        """
        初始化 BGE-M3 语义切分器
        :param model_path: BGE-M3 模型路径，若为 None 则从 config 读取
        :param device: 运行设备 ('cpu', 'cuda', 'mps')
        :param breakpoint_threshold_type: 切分断点阈值类型
               - "percentile": 基于相似度差异的百分位（推荐 75.0 - 95.0）
               - "standard_deviation": 基于标准差偏差量
               - "interquartile": 基于四分位距
        :param breakpoint_threshold_amount: 阈值数值，数值越高切出的 Chunk 越大，越低切得越细
        """
        # 指定 BGE-M3 模型路径（原生支持 8192 上下文长度）
        self.model_path = model_path or f'{config.MODELS_DIR}/BAAI/bge-m3'
        logger.debug(f'正在加载 BGE-M3 Embedding 模型用于语义切分: {self.model_path}')

        # 实例化 HuggingFaceBgeEmbeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_path,
            model_kwargs={'device': device},
            encode_kwargs={
                'normalize_embeddings': True,
                'batch_size': 16
            }
        )

        # 构建 SemanticChunker 对象
        self.chunker = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type=breakpoint_threshold_type,
            breakpoint_threshold_amount=breakpoint_threshold_amount,
            # 正则表达式正向回顾，默认值 (?<=[.?!])\s+ 只能处理西文
            sentence_split_regex = r'(?<=[。！？\n])'
        )
        logger.debug('BgeSemanticSplitter 初始化完成')

    def split_text(self, text: str) -> List[str]:
        """对长字符串进行语义切分，返回切分后的字符串列表"""
        if not text or not text.strip():
            return []

        try:
            documents: List[Document] = self.chunker.create_documents([text])
            chunks = [doc.page_content.strip() for doc in documents if doc.page_content.strip()]
            logger.debug(f'语义切分完成，共生成 {len(chunks)} 个 Chunk')
            return chunks
        except Exception as e:
            logger.error(f'语义切分发生异常: {e}', exc_info=True)
            return [text.strip()]