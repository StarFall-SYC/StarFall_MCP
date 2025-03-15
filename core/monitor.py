"""监控分析模块"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MetricData(BaseModel):
    """指标数据"""
    timestamp: datetime = Field(default_factory=datetime.now)
    name: str
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)


class Alert(BaseModel):
    """告警信息"""
    id: str
    name: str
    description: str
    severity: str
    status: str = "firing"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)


class MonitorManager:
    """监控管理器"""
    
    def __init__(self):
        self._metrics: List[MetricData] = []
        self._alerts: Dict[str, Alert] = {}
        self._logger = logging.getLogger(__name__)
        self._alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # 初始化默认告警规则
        self._init_default_alert_rules()
    
    def _init_default_alert_rules(self):
        """初始化默认告警规则"""
        self.add_alert_rule(
            name="high_risk_operations",
            description="高风险操作频率过高",
            query="risk_level='high'",
            threshold=5,
            window="5m",
            severity="critical"
        )
        
        self.add_alert_rule(
            name="failed_operations",
            description="操作失败率过高",
            query="status='failed'",
            threshold=0.1,  # 10%
            window="15m",
            severity="warning"
        )
    
    def add_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """添加指标数据"""
        metric = MetricData(
            name=name,
            value=value,
            labels=labels or {}
        )
        self._metrics.append(metric)
        self._evaluate_alerts()
    
    def add_alert_rule(
        self,
        name: str,
        description: str,
        query: str,
        threshold: float,
        window: str,
        severity: str
    ) -> None:
        """添加告警规则"""
        self._alert_rules[name] = {
            "description": description,
            "query": query,
            "threshold": threshold,
            "window": window,
            "severity": severity
        }
    
    def _evaluate_alerts(self) -> None:
        """评估告警"""
        now = datetime.now()
        
        for name, rule in self._alert_rules.items():
            try:
                # 解析时间窗口
                window = self._parse_duration(rule["window"])
                start_time = now - window
                
                # 过滤指标
                filtered_metrics = [
                    m for m in self._metrics
                    if m.timestamp >= start_time and self._match_query(m, rule["query"])
                ]
                
                if not filtered_metrics:
                    continue
                
                # 计算聚合值
                value = sum(m.value for m in filtered_metrics) / len(filtered_metrics)
                
                # 检查是否超过阈值
                if value > rule["threshold"]:
                    self._create_or_update_alert(
                        name=name,
                        description=rule["description"],
                        severity=rule["severity"],
                        value=value,
                        threshold=rule["threshold"]
                    )
                else:
                    self._resolve_alert(name)
            
            except Exception as e:
                self._logger.error(f"评估告警规则失败 {name}: {str(e)}")
    
    def _match_query(self, metric: MetricData, query: str) -> bool:
        """匹配查询条件"""
        try:
            # 简单的标签匹配
            for condition in query.split(" and "):
                key, value = condition.split("=")
                if key.strip("'") not in metric.labels or \
                   metric.labels[key.strip("'")] != value.strip("'"): 
                    return False
            return True
        except Exception:
            return False
    
    def _parse_duration(self, duration: str) -> timedelta:
        """解析时间窗口"""
        unit = duration[-1]
        value = int(duration[:-1])
        
        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        else:
            raise ValueError(f"不支持的时间单位: {unit}")
    
    def _create_or_update_alert(self, name: str, description: str, severity: str, value: float, threshold: float) -> None:
        """创建或更新告警"""
        if name in self._alerts:
            alert = self._alerts[name]
            alert.updated_at = datetime.now()
        else:
            alert = Alert(
                id=f"alert_{len(self._alerts) + 1}",
                name=name,
                description=description,
                severity=severity,
                annotations={
                    "value": str(value),
                    "threshold": str(threshold)
                }
            )
            self._alerts[name] = alert
            self._logger.warning(f"触发新告警: {name} - {description}")
    
    def _resolve_alert(self, name: str) -> None:
        """解决告警"""
        if name in self._alerts:
            alert = self._alerts[name]
            alert.status = "resolved"
            alert.updated_at = datetime.now()
            self._logger.info(f"解决告警: {name}")
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活动告警"""
        return [alert for alert in self._alerts.values() if alert.status == "firing"]
    
    def get_metrics(self, start_time: Optional[datetime] = None) -> List[MetricData]:
        """获取指标数据"""
        if start_time:
            return [m for m in self._metrics if m.timestamp >= start_time]
        return self._metrics.copy()


# 创建全局监控管理器实例
monitor_manager = MonitorManager()