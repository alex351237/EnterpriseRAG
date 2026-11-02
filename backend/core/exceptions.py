"""
Author  :Alex Aug
Date    :2026/11/2 20:53
describe:自定义异常 , 自动多种异常类型是为了精准捕获异常然后做精准处理！！！
"""

from abc import ABCMeta


class EduAgentBaseError(Exception, metaclass=ABCMeta):
    """自定义异常的基类"""

    def __init__(self, message: str, agent_type: str = '', details: dict | None = None):
        super().__init__(message)
        self.agent_type = agent_type
        self.details = details or {}


class LLMAPIError(EduAgentBaseError):
    """大模型 API 调用失败（超时 / 限流 / 网络错误）"""
    pass


class AgentExecutionError(EduAgentBaseError):
    """Agent 业务逻辑执行失败"""
    pass


class PipelineError(EduAgentBaseError):
    """多 Agent Pipeline（流水线编排）失败"""
    pass


class IntentRouteError(EduAgentBaseError):
    """意图识别路由失败（没判断出该交给哪个 Agent）"""
    pass


class MilvusConnectionError(EduAgentBaseError):
    """Milvus 向量库连接失败"""
    pass


class FileParseError(EduAgentBaseError):
    """文件解析失败（Word / PDF）"""
    pass


class InvalidInputError(EduAgentBaseError):
    """用户输入不合法"""
    pass


class AuthenticationError(EduAgentBaseError):
    """认证失败"""
    pass
