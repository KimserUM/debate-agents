"""
stats.py -- 辩论统计

追踪每轮发言字数、各角色贡献、总轮数和耗时。
DebateResult里加上stats字段, 辩论结束后自动生成summary。

230511535 杨光裕
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SpeakerStats:
    """单个发言者的统计"""
    turn_count: int = 0
    total_chars: int = 0
    avg_chars: float = 0.0

    def record(self, text: str):
        self.turn_count += 1
        self.total_chars += len(text)
        self.avg_chars = self.total_chars / self.turn_count


@dataclass
class DebateStats:
    """整场辩论的统计"""
    topic: str = ""
    total_rounds: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    speakers: Dict[str, SpeakerStats] = field(default_factory=dict)
    verdict_char_count: int = 0

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    def record_speech(self, speaker: str, text: str):
        if speaker not in self.speakers:
            self.speakers[speaker] = SpeakerStats()
        self.speakers[speaker].record(text)
        self.total_rounds += 1

    def record_verdict(self, text: str):
        self.verdict_char_count = len(text)

    @property
    def elapsed_seconds(self) -> float:
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def total_chars(self) -> int:
        return sum(s.total_chars for s in self.speakers.values())

    def summary(self) -> str:
        """生成可读的统计summary"""
        if not self.speakers:
            return "(无统计数据)"

        lines = [
            f"辩论统计 | 总轮数={self.total_rounds} | "
            f"耗时={self.elapsed_seconds:.1f}s | "
            f"总字数={self.total_chars}",
            f"裁判verdict字数={self.verdict_char_count}",
            "",
        ]

        for name, ss in self.speakers.items():
            lines.append(
                f"  {name}: {ss.turn_count}次发言, "
                f"共{ss.total_chars}字, "
                f"平均{ss.avg_chars:.0f}字/次"
            )

        return "\n".join(lines)
