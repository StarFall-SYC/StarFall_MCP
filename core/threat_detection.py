"""
威胁检测模块
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class ThreatPattern(BaseModel):
    """威胁模式"""
    name: str
    description: str
    pattern: str
    risk_level: str
    category: str
    mitigation: str


class ThreatEvent(BaseModel):
    """威胁事件"""
    timestamp: datetime = Field(default_factory=datetime.now)
    pattern_name: str
    risk_level: str
    details: Dict[str, Any]
    source: str
    status: str = "detected"


class ThreatDetector:
    """威胁检测器"""
    
    def __init__(self):
        self._patterns: Dict[str, ThreatPattern] = {}
        self._events: List[ThreatEvent] = []
        self._blocked_patterns: Set[str] = set()
        
        # 初始化默认威胁模式
        self._init_default_patterns()
    
    def _init_default_patterns(self):
        """初始化默认威胁模式"""
        # 文件系统威胁
        self.register_pattern(ThreatPattern(
            name="dangerous_file_operation",
            description="危险的文件操作",
            pattern=r"(?:rm\s+-rf|mkfs\.|dd\s+if=)",
            risk_level="high",
            category="file_system",
            mitigation="阻止执行并记录"
        ))
        
        # 系统命令威胁
        self.register_pattern(ThreatPattern(
            name="dangerous_system_command",
            description="危险的系统命令",
            pattern=r"(?:sudo\s+|chmod\s+777|chown\s+root)",
            risk_level="high",
            category="system",
            mitigation="阻止执行并记录"
        ))
        
        # 网络威胁
        self.register_pattern(ThreatPattern(
            name="suspicious_network_activity",
            description="可疑的网络活动",
            pattern=r"(?:nc\s+-l|nmap|wget\s+http)",
            risk_level="medium",
            category="network",
            mitigation="记录并警告"
        ))
        
        # 权限提升威胁
        self.register_pattern(ThreatPattern(
            name="privilege_escalation",
            description="权限提升尝试",
            pattern=r"(?:sudo\s+su|sudo\s+bash|sudo\s+sh)",
            risk_level="high",
            category="security",
            mitigation="阻止执行并记录"
        ))
    
    def register_pattern(self, pattern: ThreatPattern) -> None:
        """注册威胁模式"""
        self._patterns[pattern.name] = pattern
    
    def detect_threats(self, text: str, source: str) -> List[ThreatEvent]:
        """检测威胁"""
        events = []
        
        # 遍历所有威胁模式
        for pattern in self._patterns.values():
            if pattern.name in self._blocked_patterns:
                continue
            
            # 检查是否匹配模式
            if re.search(pattern.pattern, text, re.IGNORECASE):
                event = ThreatEvent(
                    pattern_name=pattern.name,
                    risk_level=pattern.risk_level,
                    details={
                        "text": text,
                        "pattern": pattern.pattern,
                        "category": pattern.category
                    },
                    source=source
                )
                events.append(event)
                
                # 如果是高风险威胁，阻止该模式
                if pattern.risk_level == "high":
                    self._blocked_patterns.add(pattern.name)
        
        # 记录事件
        self._events.extend(events)
        
        return events
    
    def get_threat_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        risk_level: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ThreatEvent]:
        """获取威胁事件"""
        events = self._events
        
        # 按时间过滤
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # 按风险等级过滤
        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]
        
        # 按类别过滤
        if category:
            events = [e for e in events if e.details["category"] == category]
        
        return events
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """获取威胁统计信息"""
        stats = {
            "total_events": len(self._events),
            "high_risk_events": len([e for e in self._events if e.risk_level == "high"]),
            "medium_risk_events": len([e for e in self._events if e.risk_level == "medium"]),
            "low_risk_events": len([e for e in self._events if e.risk_level == "low"]),
            "blocked_patterns": len(self._blocked_patterns),
            "categories": {}
        }
        
        # 统计各类别的威胁数量
        for event in self._events:
            category = event.details["category"]
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1
        
        return stats
    
    def clear_events(self) -> None:
        """清除事件记录"""
        self._events.clear()
    
    def unblock_pattern(self, pattern_name: str) -> None:
        """解除模式阻止"""
        if pattern_name in self._blocked_patterns:
            self._blocked_patterns.remove(pattern_name)


# 全局威胁检测器实例
threat_detector = ThreatDetector() 