"""Middleware analyzer - Task 23

Detects Pulsar topics, producers, consumers, and middleware keywords.
Scans multiple files for messaging patterns.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict


@dataclass
class PulsarTopic:
    """Represents a Pulsar topic"""

    name: str
    producer_count: int = 0
    consumer_count: int = 0
    partition_count: Optional[int] = None
    confidence: float = 1.0


@dataclass
class Producer:
    """Represents a message producer"""

    name: str
    type: str  # "pulsar", "rabbitmq", "kafka", "activemq"
    topic: Optional[str] = None
    file_path: Optional[str] = None
    confidence: float = 1.0


@dataclass
class Consumer:
    """Represents a message consumer"""

    name: str
    type: str  # "pulsar", "rabbitmq", "kafka", "activemq"
    topic: Optional[str] = None
    file_path: Optional[str] = None
    confidence: float = 1.0


class MiddlewareAnalyzer:
    """Analyzes middleware patterns (Pulsar, RabbitMQ, Kafka, etc.)"""

    # Pulsar patterns
    PULSAR_PRODUCER_PATTERN = re.compile(
        r"(?:PulsarProducer|pulsarProducer|createProducer|producer\.create)\s*[(<]",
        re.IGNORECASE,
    )

    PULSAR_CONSUMER_PATTERN = re.compile(
        r"(?:PulsarConsumer|pulsarConsumer|createConsumer|consumer\.create)\s*[(<]",
        re.IGNORECASE,
    )

    PULSAR_TOPIC_PATTERN = re.compile(r"(?:topic|Topic)\s*[=:]\s*['\"]([^'\"]+)['\"]")

    # RabbitMQ patterns
    RABBITMQ_PATTERN = re.compile(r"(?:RabbitMQ|rabbitmq|amqp|Queue|Exchange)", re.IGNORECASE)

    # Kafka patterns
    KAFKA_PRODUCER_PATTERN = re.compile(r"(?:KafkaProducer|producer\.send)", re.IGNORECASE)

    KAFKA_CONSUMER_PATTERN = re.compile(r"(?:KafkaConsumer|consumer\.poll|subscribe)", re.IGNORECASE)

    # ActiveMQ patterns
    ACTIVEMQ_PATTERN = re.compile(r"(?:ActiveMQ|activemq|JMS|Queue)", re.IGNORECASE)

    # Generic messaging patterns
    MESSAGE_PUBLISH_PATTERN = re.compile(r"(?:publish|send|emit)\s*\(", re.IGNORECASE)

    MESSAGE_SUBSCRIBE_PATTERN = re.compile(r"(?:subscribe|listen|on)\s*\(", re.IGNORECASE)

    def __init__(self):
        """Initialize middleware analyzer"""
        self.topics: Dict[str, PulsarTopic] = {}
        self.producers: List[Producer] = []
        self.consumers: List[Consumer] = []
        self.middleware_types: Set[str] = set()

    def analyze_files(self, repo_path: Path) -> Dict[str, Any]:
        """
        Scan repository for middleware patterns.

        Args:
            repo_path: Path to repository

        Returns:
            Dictionary with topics, producers, consumers
        """
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return {
                "success": False,
                "error": f"Repository path not found: {repo_path}",
                "topics": [],
                "producers": [],
                "consumers": [],
            }

        if not repo_path.is_dir():
            # Single file analysis
            return self._analyze_single_file(repo_path)

        # Scan directory
        self._scan_directory(repo_path)

        return {
            "success": True,
            "topics": [asdict(t) for t in self.topics.values()],
            "producers": [asdict(p) for p in self.producers],
            "consumers": [asdict(c) for c in self.consumers],
            "middleware_types": list(self.middleware_types),
            "confidence": self._calculate_confidence(),
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single file for middleware patterns.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with detected patterns
        """
        return self._analyze_single_file(file_path)

    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file"""
        file_path = Path(file_path)

        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "topics": [],
                "producers": [],
                "consumers": [],
            }

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "topics": [],
                "producers": [],
                "consumers": [],
            }

        # Analyze content
        self._analyze_content(content, str(file_path))

        return {
            "success": True,
            "topics": [asdict(t) for t in self.topics.values()],
            "producers": [asdict(p) for p in self.producers],
            "consumers": [asdict(c) for c in self.consumers],
            "middleware_types": list(self.middleware_types),
            "confidence": self._calculate_confidence(),
        }

    def _scan_directory(self, repo_path: Path) -> None:
        """Recursively scan directory for source files"""
        # Common source file extensions
        extensions = [".py", ".java", ".js", ".ts", ".go", ".rb", ".php"]

        for ext in extensions:
            for file_path in repo_path.rglob(f"*{ext}"):
                # Skip test and node_modules directories
                if "test" in str(file_path) or "node_modules" in str(file_path):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    self._analyze_content(content, str(file_path))
                except Exception:
                    # Skip unreadable files
                    pass

    def _analyze_content(self, content: str, file_path: str) -> None:
        """Analyze file content for middleware patterns"""
        # Detect middleware types
        self._detect_middleware_types(content)

        # Detect Pulsar patterns
        self._extract_pulsar_patterns(content, file_path)

        # Detect RabbitMQ patterns
        if self.RABBITMQ_PATTERN.search(content):
            self.middleware_types.add("RabbitMQ")

        # Detect Kafka patterns
        self._extract_kafka_patterns(content, file_path)

        # Detect ActiveMQ patterns
        if self.ACTIVEMQ_PATTERN.search(content):
            self.middleware_types.add("ActiveMQ")

    def _detect_middleware_types(self, content: str) -> None:
        """Detect which middleware types are used"""
        if "pulsar" in content.lower():
            self.middleware_types.add("Pulsar")
        if any(x in content.lower() for x in ["rabbitmq", "amqp"]):
            self.middleware_types.add("RabbitMQ")
        if "kafka" in content.lower():
            self.middleware_types.add("Kafka")
        if "activemq" in content.lower() or "jms" in content.lower():
            self.middleware_types.add("ActiveMQ")

    def _extract_pulsar_patterns(self, content: str, file_path: str) -> None:
        """Extract Pulsar topics, producers, and consumers"""
        # Find producers
        for match in self.PULSAR_PRODUCER_PATTERN.finditer(content):
            # Extract surrounding context for topic name
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            context = content[start:end]

            topic_match = self.PULSAR_TOPIC_PATTERN.search(context)
            topic_name = topic_match.group(1) if topic_match else None

            producer = Producer(
                name=f"producer_{len(self.producers)}",
                type="pulsar",
                topic=topic_name,
                file_path=file_path,
            )
            self.producers.append(producer)

            # Add to topic
            if topic_name:
                if topic_name not in self.topics:
                    self.topics[topic_name] = PulsarTopic(name=topic_name)
                self.topics[topic_name].producer_count += 1

        # Find consumers
        for match in self.PULSAR_CONSUMER_PATTERN.finditer(content):
            # Extract surrounding context for topic name
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            context = content[start:end]

            topic_match = self.PULSAR_TOPIC_PATTERN.search(context)
            topic_name = topic_match.group(1) if topic_match else None

            consumer = Consumer(
                name=f"consumer_{len(self.consumers)}",
                type="pulsar",
                topic=topic_name,
                file_path=file_path,
            )
            self.consumers.append(consumer)

            # Add to topic
            if topic_name:
                if topic_name not in self.topics:
                    self.topics[topic_name] = PulsarTopic(name=topic_name)
                self.topics[topic_name].consumer_count += 1

    def _extract_kafka_patterns(self, content: str, file_path: str) -> None:
        """Extract Kafka topics, producers, and consumers"""
        # Find Kafka producers
        for match in self.KAFKA_PRODUCER_PATTERN.finditer(content):
            producer = Producer(
                name=f"kafka_producer_{len(self.producers)}",
                type="kafka",
                file_path=file_path,
            )
            self.producers.append(producer)

        # Find Kafka consumers
        for match in self.KAFKA_CONSUMER_PATTERN.finditer(content):
            consumer = Consumer(
                name=f"kafka_consumer_{len(self.consumers)}",
                type="kafka",
                file_path=file_path,
            )
            self.consumers.append(consumer)

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score"""
        if not self.topics and not self.producers and not self.consumers:
            return 0.5

        total_items = len(self.topics) + len(self.producers) + len(self.consumers)
        if total_items == 0:
            return 0.5

        return 0.85
