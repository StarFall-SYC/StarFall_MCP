"""
安全框架模块
"""
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field



class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SecurityContext(BaseModel):
    """安全上下文"""
    user_id: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    is_active: bool = True
    last_activity: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    session_id: Optional[str] = None


class SecurityPolicy(BaseModel):
    """安全策略"""
    name: str
    description: str
    risk_level: RiskLevel
    required_permissions: List[str]
    max_execution_time: int
    resource_limits: Dict[str, Any]
    command_patterns: List[str] = Field(default_factory=list)


class AuditLog(BaseModel):
    """审计日志"""
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str
    action: str
    details: Dict[str, Any]
    risk_level: RiskLevel
    status: str


class ThreatPattern(BaseModel):
    """威胁模式"""
    name: str
    description: str
    pattern: str
    risk_level: RiskLevel
    category: str
    mitigation: str


class ThreatEvent(BaseModel):
    """威胁事件"""
    timestamp: datetime = Field(default_factory=datetime.now)
    pattern_name: str
    risk_level: RiskLevel
    details: Dict[str, Any]
    source: str
    status: str = "detected"


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self._policies: Dict[str, SecurityPolicy] = {}
        self._contexts: Dict[str, SecurityContext] = {}
        self._audit_logs: List[AuditLog] = []
        self._logger = logging.getLogger(__name__)
        self._context = SecurityContext()
        self._risk_threshold = 0.7
        self._patterns: Dict[str, ThreatPattern] = {}
        self._threat_events: List[ThreatEvent] = []
        self._blocked_patterns: Set[str] = set()
        
        # 初始化默认安全策略和威胁模式
        self._init_default_policies()
        self._init_default_patterns()
    
    def _init_default_policies(self):
        """初始化默认安全策略"""
        # 文件操作策略
        self.register_policy(SecurityPolicy(
            name="file_operation",
            description="文件操作安全策略",
            risk_level=RiskLevel.MEDIUM,
            required_permissions=["file.read", "file.write"],
            max_execution_time=30,
            resource_limits={"max_file_size": 100 * 1024 * 1024},  # 100MB
            command_patterns=[
                r"rm\s+-rf\s+/",
                r"mkfs\.",
                r"dd\s+if=",
                r">\s+/dev/sda"
            ]
        ))
        
        # 系统命令策略
        self.register_policy(SecurityPolicy(
            name="system_command",
            description="系统命令安全策略",
            risk_level=RiskLevel.HIGH,
            required_permissions=["system.execute"],
            max_execution_time=60,
            resource_limits={"max_memory": 512 * 1024 * 1024},  # 512MB
            command_patterns=[
                r"sudo\s+",
                r"chmod\s+777",
                r"chown\s+root",
                r"mkfs\.",
                r"dd\s+if="
            ]
        ))

    def _init_default_patterns(self):
        """初始化默认威胁模式"""
        # 文件系统威胁
        self.register_pattern(ThreatPattern(
            name="dangerous_file_operation",
            description="危险的文件操作",
            pattern=r"(?:rm\s+-rf|mkfs\.|dd\s+if=)",
            risk_level=RiskLevel.HIGH,
            category="file_system",
            mitigation="阻止执行并记录"
        ))
        
        # 系统命令威胁
        self.register_pattern(ThreatPattern(
            name="dangerous_system_command",
            description="危险的系统命令",
            pattern=r"(?:sudo\s+|chmod\s+777|chown\s+root)",
            risk_level=RiskLevel.HIGH,
            category="system",
            mitigation="阻止执行并记录"
        ))
        
        # 网络威胁
        self.register_pattern(ThreatPattern(
            name="suspicious_network_activity",
            description="可疑的网络活动",
            pattern=r"(?:nc\s+-l|nmap|wget\s+http)",
            risk_level=RiskLevel.MEDIUM,
            category="network",
            mitigation="记录并警告"
        ))
        
        # 权限提升威胁
        self.register_pattern(ThreatPattern(
            name="privilege_escalation",
            description="权限提升尝试",
            pattern=r"(?:sudo\s+su|sudo\s+bash|sudo\s+sh)",
            risk_level=RiskLevel.HIGH,
            category="security",
            mitigation="阻止执行并记录"
        ))
    
    def register_policy(self, policy: SecurityPolicy) -> None:
        """注册安全策略"""
        self._policies[policy.name] = policy
        self._logger.info(f"注册安全策略: {policy.name}")
    
    def get_policy(self, name: str) -> Optional[SecurityPolicy]:
        """获取安全策略"""
        return self._policies.get(name)
    
    def create_context(self, user_id: str, roles: List[str], permissions: List[str]) -> SecurityContext:
        """创建安全上下文"""
        context = SecurityContext(
            user_id=user_id,
            roles=roles,
            permissions=permissions
        )
        self._contexts[user_id] = context
        self._logger.info(f"创建安全上下文: {user_id}")
        return context
    
    def get_context(self, user_id: str) -> Optional[SecurityContext]:
        """获取安全上下文"""
        return self._contexts.get(user_id)
    
    def check_permission(self, user_id: str, required_permissions: List[str]) -> bool:
        """检查权限"""
        context = self.get_context(user_id)
        if not context:
            return False
        return all(perm in context.permissions for perm in required_permissions)
    
    def register_pattern(self, pattern: ThreatPattern) -> None:
        """注册威胁模式"""
        self._patterns[pattern.name] = pattern
        self._logger.info(f"注册威胁模式: {pattern.name}")
    
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
                if pattern.risk_level == RiskLevel.HIGH:
                    self._blocked_patterns.add(pattern.name)
        
        # 记录事件
        self._threat_events.extend(events)
        
        return events
    
    def get_threat_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        risk_level: Optional[RiskLevel] = None,
        category: Optional[str] = None
    ) -> List[ThreatEvent]:
        """获取威胁事件"""
        events = self._threat_events
        
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
            "total_events": len(self._threat_events),
            "high_risk_events": len([e for e in self._threat_events if e.risk_level == RiskLevel.HIGH]),
            "medium_risk_events": len([e for e in self._threat_events if e.risk_level == RiskLevel.MEDIUM]),
            "low_risk_events": len([e for e in self._threat_events if e.risk_level == RiskLevel.LOW]),
            "blocked_patterns": len(self._blocked_patterns),
            "categories": {}
        }
        
        # 统计各类别的威胁数量
        for event in self._threat_events:
            category = event.details["category"]
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1
        
        return stats
    
    def unblock_pattern(self, pattern_name: str) -> None:
        """解除模式阻止"""
        if pattern_name in self._blocked_patterns:
            self._blocked_patterns.remove(pattern_name)
            self._logger.info(f"解除威胁模式阻止: {pattern_name}")
    
    def evaluate_risk(self, operation: str, params: Dict[str, Any]) -> RiskLevel:
        """评估操作风险"""
        # 检查命令模式
        for policy in self._policies.values():
            for pattern in policy.command_patterns:
                if re.search(pattern, operation, re.IGNORECASE):
                    return policy.risk_level
        
        # 检查参数风险
        if any(key in params for key in ["password", "secret", "key"]):
            return RiskLevel.HIGH
        
        # 检查资源使用
        if "memory" in params and params["memory"] > 512 * 1024 * 1024:  # 512MB
            return RiskLevel.HIGH
        
        return RiskLevel.LOW
    
    def sanitize_command(self, command: str) -> str:
        """命令消毒"""
        # 移除危险字符
        command = re.sub(r'[;&|`$]', '', command)
        
        # 移除命令替换
        command = re.sub(r'\$\(.*?\)', '', command)
        
        # 移除注释
        command = re.sub(r'#.*$', '', command)
        
        # 移除多余空格
        command = ' '.join(command.split())
        
        return command
    
    def log_audit(self, user_id: str, action: str, details: Dict[str, Any], risk_level: RiskLevel, status: str):
        """记录审计日志"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            risk_level=risk_level,
            status=status
        )
        self._audit_logs.append(log)
        self._logger.info(f"审计日志: {log.dict()}")
        
        # 如果风险等级高，记录警告
        if risk_level == RiskLevel.HIGH:
            self._logger.warning(f"高风险操作: {action} by {user_id}")
    
    def get_audit_logs(self, user_id: Optional[str] = None) -> List[AuditLog]:
        """获取审计日志"""
        if user_id:
            return [log for log in self._audit_logs if log.user_id == user_id]
        return self._audit_logs
    
    def set_context(self, **kwargs) -> None:
        """设置安全上下文"""
        for key, value in kwargs.items():
            if hasattr(self._context, key):
                setattr(self._context, key, value)
    
    def assess_risk(self, action: str, parameters: Dict[str, Any]) -> float:
        """评估风险"""
        risk_score = 0.0
        
        # 检查命令注入风险
        if any(isinstance(v, str) and any(cmd in v.lower() for cmd in [';', '&&', '||', '`']) 
               for v in parameters.values()):
            risk_score += 0.3
        
        # 检查文件操作风险
        if action in ['file_write', 'file_delete']:
            risk_score += 0.2
        
        # 检查系统命令风险
        if action in ['execute_command']:
            risk_score += 0.4
        
        # 检查网络操作风险
        if action in ['network_request']:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def detect_threats(self, text: str) -> List[ThreatEvent]:
        """检测威胁"""
        return threat_detector.detect_threats(text, self._context.user_id or "unknown")
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """获取威胁统计信息"""
        return threat_detector.get_threat_statistics()
    
    def get_audit_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取审计日志"""
        logs = self._audit_logs
        
        # 按时间过滤
        if start_time:
            logs = [l for l in logs if l.timestamp >= start_time]
        if end_time:
            logs = [l for l in logs if l.timestamp <= end_time]
        
        # 按用户过滤
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        # 按动作过滤
        if action:
            logs = [l for l in logs if l.action == action]
        
        return logs


# 全局安全管理器实例
security_manager = SecurityManager()