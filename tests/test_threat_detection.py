"""
威胁检测模块测试
"""
import pytest
from datetime import datetime, timedelta

from core.threat_detection import ThreatDetector, ThreatPattern, ThreatEvent


def test_threat_pattern_registration():
    """测试威胁模式注册"""
    detector = ThreatDetector()
    
    # 创建测试模式
    pattern = ThreatPattern(
        name="test_pattern",
        description="测试模式",
        pattern=r"test",
        risk_level="low",
        category="test",
        mitigation="测试缓解措施"
    )
    
    # 注册模式
    detector.register_pattern(pattern)
    
    # 验证模式已注册
    assert "test_pattern" in detector._patterns


def test_threat_detection():
    """测试威胁检测"""
    detector = ThreatDetector()
    
    # 测试文件系统威胁
    events = detector.detect_threats("rm -rf /", "test_user")
    assert len(events) > 0
    assert events[0].pattern_name == "dangerous_file_operation"
    assert events[0].risk_level == "high"
    
    # 测试系统命令威胁
    events = detector.detect_threats("sudo chmod 777 /etc/passwd", "test_user")
    assert len(events) > 0
    assert events[0].pattern_name == "dangerous_system_command"
    assert events[0].risk_level == "high"
    
    # 测试网络威胁
    events = detector.detect_threats("nc -l 8080", "test_user")
    assert len(events) > 0
    assert events[0].pattern_name == "suspicious_network_activity"
    assert events[0].risk_level == "medium"


def test_threat_event_filtering():
    """测试威胁事件过滤"""
    detector = ThreatDetector()
    
    # 生成一些测试事件
    now = datetime.now()
    events = [
        ThreatEvent(
            timestamp=now - timedelta(hours=1),
            pattern_name="test1",
            risk_level="high",
            details={"text": "test1", "pattern": "test1", "category": "test"},
            source="test_user"
        ),
        ThreatEvent(
            timestamp=now,
            pattern_name="test2",
            risk_level="medium",
            details={"text": "test2", "pattern": "test2", "category": "test"},
            source="test_user"
        )
    ]
    detector._events.extend(events)
    
    # 测试时间过滤
    filtered = detector.get_threat_events(
        start_time=now - timedelta(hours=2),
        end_time=now
    )
    assert len(filtered) == 2
    
    # 测试风险等级过滤
    filtered = detector.get_threat_events(risk_level="high")
    assert len(filtered) == 1
    
    # 测试类别过滤
    filtered = detector.get_threat_events(category="test")
    assert len(filtered) == 2


def test_threat_statistics():
    """测试威胁统计"""
    detector = ThreatDetector()
    
    # 生成测试事件
    events = [
        ThreatEvent(
            pattern_name="test1",
            risk_level="high",
            details={"text": "test1", "pattern": "test1", "category": "test1"},
            source="test_user"
        ),
        ThreatEvent(
            pattern_name="test2",
            risk_level="medium",
            details={"text": "test2", "pattern": "test2", "category": "test2"},
            source="test_user"
        )
    ]
    detector._events.extend(events)
    
    # 获取统计信息
    stats = detector.get_threat_statistics()
    
    # 验证统计信息
    assert stats["total_events"] == 2
    assert stats["high_risk_events"] == 1
    assert stats["medium_risk_events"] == 1
    assert stats["low_risk_events"] == 0
    assert len(stats["categories"]) == 2


def test_pattern_blocking():
    """测试模式阻止"""
    detector = ThreatDetector()
    
    # 注册测试模式
    pattern = ThreatPattern(
        name="test_block",
        description="测试阻止模式",
        pattern=r"block",
        risk_level="high",
        category="test",
        mitigation="测试缓解措施"
    )
    detector.register_pattern(pattern)
    
    # 检测威胁（应该触发阻止）
    events = detector.detect_threats("block", "test_user")
    assert len(events) > 0
    assert "test_block" in detector._blocked_patterns
    
    # 再次检测（应该被阻止）
    events = detector.detect_threats("block", "test_user")
    assert len(events) == 0
    
    # 解除阻止
    detector.unblock_pattern("test_block")
    assert "test_block" not in detector._blocked_patterns
    
    # 再次检测（应该可以检测到）
    events = detector.detect_threats("block", "test_user")
    assert len(events) > 0 