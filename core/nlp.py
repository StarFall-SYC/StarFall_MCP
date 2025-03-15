"""
自然语言处理模块
"""
import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from transformers import pipeline


class Intent(BaseModel):
    """意图"""
    name: str
    confidence: float
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolMatch(BaseModel):
    """工具匹配"""
    tool_name: str
    confidence: float
    parameters: Dict[str, Any] = Field(default_factory=dict)


class NLProcessor:
    """自然语言处理器"""
    
    def __init__(self):
        self._intents: Dict[str, Dict[str, Any]] = {}
        self._tool_patterns: Dict[str, List[str]] = {}
        self._parameter_patterns: Dict[str, Dict[str, str]] = {}
        self._classifier = pipeline("zero-shot-classification")
        self._extractor = pipeline("token-classification")
        
        # 初始化默认意图
        self._init_default_intents()
        
        # 初始化工具模式
        self._init_tool_patterns()
        
        # 初始化参数模式
        self._init_parameter_patterns()
    
    def _init_default_intents(self):
        """初始化默认意图"""
        self.register_intent(
            "file_operation",
            [
                "创建文件",
                "删除文件",
                "读取文件",
                "修改文件",
                "列出目录"
            ],
            {
                "path": "文件路径",
                "content": "文件内容",
                "overwrite": "是否覆盖"
            }
        )
        
        self.register_intent(
            "system_operation",
            [
                "执行命令",
                "查看进程",
                "系统信息",
                "关闭程序"
            ],
            {
                "command": "命令内容",
                "process_id": "进程ID",
                "timeout": "超时时间"
            }
        )
    
    def _init_tool_patterns(self):
        """初始化工具模式"""
        self.register_tool_patterns(
            "file_create",
            [
                r"创建(?:一个)?文件\s*[:：](?P<path>[^\s]+)",
                r"新建(?:一个)?文件\s*[:：](?P<path>[^\s]+)",
                r"建立(?:一个)?文件\s*[:：](?P<path>[^\s]+)"
            ]
        )
        
        self.register_tool_patterns(
            "file_delete",
            [
                r"删除文件\s*[:：](?P<path>[^\s]+)",
                r"移除文件\s*[:：](?P<path>[^\s]+)",
                r"删除\s*(?P<path>[^\s]+)"
            ]
        )
        
        self.register_tool_patterns(
            "command_execute",
            [
                r"执行命令\s*[:：](?P<command>[^\n]+)",
                r"运行命令\s*[:：](?P<command>[^\n]+)",
                r"执行\s*(?P<command>[^\n]+)"
            ]
        )
    
    def _init_parameter_patterns(self):
        """初始化参数模式"""
        self._parameter_patterns = {
            "path": r"(?:路径|文件|目录)\s*[:：](?P<value>[^\s]+)",
            "content": r"(?:内容|文本)\s*[:：](?P<value>[^\n]+)",
            "command": r"(?:命令|指令)\s*[:：](?P<value>[^\n]+)",
            "timeout": r"(?:超时|时间)\s*[:：](?P<value>\d+)",
            "process_id": r"(?:进程|PID)\s*[:：](?P<value>\d+)"
        }
    
    def register_intent(self, name: str, patterns: List[str], parameters: Dict[str, Any]) -> None:
        """注册意图"""
        self._intents[name] = {
            "patterns": patterns,
            "parameters": parameters
        }
    
    def register_tool_patterns(self, tool_name: str, patterns: List[str]) -> None:
        """注册工具匹配模式"""
        self._tool_patterns[tool_name] = patterns
    
    async def parse_intent(self, text: str) -> List[Intent]:
        """解析意图"""
        intents = []
        
        # 准备候选意图
        candidate_labels = list(self._intents.keys())
        
        # 使用零样本分类器进行意图识别
        result = self._classifier(text, candidate_labels)
        
        # 处理结果
        for label, score in zip(result["labels"], result["scores"]):
            if score > 0.5:  # 置信度阈值
                intents.append(Intent(
                    name=label,
                    confidence=score,
                    parameters={}
                ))
        
        return intents
    
    async def match_tools(self, text: str) -> List[ToolMatch]:
        """匹配工具"""
        matches = []
        
        # 遍历所有工具模式
        for tool_name, patterns in self._tool_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    # 提取参数
                    params = match.groupdict()
                    
                    # 计算置信度（基于模式匹配）
                    confidence = 0.8 if len(params) > 0 else 0.6
                    
                    matches.append(ToolMatch(
                        tool_name=tool_name,
                        confidence=confidence,
                        parameters=params
                    ))
        
        return matches
    
    async def extract_parameters(self, text: str, tool_name: str) -> Dict[str, Any]:
        """提取参数"""
        parameters = {}
        
        # 使用命名实体识别提取参数
        entities = self._extractor(text)
        
        # 处理识别到的实体
        for entity in entities:
            param_type = entity["entity"].split("-")[-1]
            if param_type in self._parameter_patterns:
                parameters[param_type] = entity["word"]
        
        # 使用模式匹配提取参数
        for param_name, pattern in self._parameter_patterns.items():
            match = re.search(pattern, text)
            if match:
                parameters[param_name] = match.group("value")
        
        return parameters
    
    async def generate_workflow(self, text: str) -> List[ToolMatch]:
        """生成工作流"""
        # 1. 解析意图
        intents = await self.parse_intent(text)
        
        # 2. 匹配工具
        tool_matches = await self.match_tools(text)
        
        # 3. 提取参数
        for match in tool_matches:
            match.parameters.update(await self.extract_parameters(text, match.tool_name))
        
        return tool_matches


# 全局自然语言处理器实例
nl_processor = NLProcessor() 