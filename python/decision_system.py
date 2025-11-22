#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decision System - 통합 의사결정 시스템

전체 의사결정 프로세스를 체계화하고 워크플로우로 관리
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from decision_framework import analyze_decision
from decision_frameworks import FrameworkLibrary
from deep_decision_analysis import DeepDecisionAnalyzer
from card_optimizer import optimize_cards


class DecisionStage(Enum):
    """의사결정 단계"""
    PROBLEM_DEFINITION = "problem_definition"      # 1. 문제 정의
    DATA_COLLECTION = "data_collection"            # 2. 데이터 수집
    FRAMEWORK_SELECTION = "framework_selection"    # 3. 프레임워크 선택
    ANALYSIS = "analysis"                          # 4. 분석
    DECISION = "decision"                          # 5. 결정
    EXECUTION = "execution"                        # 6. 실행
    REVIEW = "review"                              # 7. 회고


class DecisionStatus(Enum):
    """의사결정 상태"""
    DRAFT = "draft"              # 초안
    IN_PROGRESS = "in_progress"  # 진행 중
    COMPLETED = "completed"      # 완료
    CANCELLED = "cancelled"      # 취소
    DEFERRED = "deferred"        # 보류


@dataclass
class DecisionRecord:
    """의사결정 기록"""
    id: str
    title: str
    goal: str
    options: List[str]
    category: str
    stage: DecisionStage
    status: DecisionStatus
    created_at: str
    updated_at: str

    # 데이터
    cards: List[Dict[str, Any]] = field(default_factory=list)
    framework_id: Optional[str] = None

    # 분석 결과
    gap_analysis: Optional[Dict] = None
    scenario_analysis: Optional[Dict] = None
    risk_analysis: Optional[Dict] = None
    sensitivity_analysis: Optional[Dict] = None

    # 결정
    selected_option: Optional[str] = None
    rationale: Optional[str] = None
    confidence: Optional[float] = None

    # 실행 및 회고
    execution_plan: Optional[str] = None
    actual_outcome: Optional[Dict] = None
    lessons_learned: Optional[str] = None

    # 메타데이터
    tags: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['stage'] = self.stage.value
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'DecisionRecord':
        """딕셔너리에서 생성"""
        data['stage'] = DecisionStage(data['stage'])
        data['status'] = DecisionStatus(data['status'])
        return cls(**data)


class DecisionWorkflow:
    """의사결정 워크플로우 관리"""

    WORKFLOW_STEPS = [
        {
            "stage": DecisionStage.PROBLEM_DEFINITION,
            "name": "1. 문제 정의",
            "description": "의사결정 목표와 선택지를 명확히 정의합니다",
            "required_fields": ["title", "goal", "options"],
            "checklist": [
                "목표가 SMART하게 정의되었는가? (Specific, Measurable, Achievable, Relevant, Time-bound)",
                "선택지가 상호 배타적인가?",
                "모든 실질적 선택지가 포함되었는가?",
            ],
            "deliverables": ["명확한 목표", "선택지 목록", "의사결정 기준"]
        },
        {
            "stage": DecisionStage.DATA_COLLECTION,
            "name": "2. 데이터 수집",
            "description": "의사결정에 필요한 데이터를 수집하고 카드로 정리합니다",
            "required_fields": ["cards"],
            "checklist": [
                "각 선택지에 대한 핵심 데이터가 수집되었는가?",
                "데이터의 출처가 신뢰할 만한가?",
                "정량적/정성적 데이터가 균형있게 수집되었는가?",
            ],
            "deliverables": ["정리된 카드 덱", "데이터 출처 목록"]
        },
        {
            "stage": DecisionStage.FRAMEWORK_SELECTION,
            "name": "3. 프레임워크 선택",
            "description": "상황에 맞는 의사결정 프레임워크를 선택합니다",
            "required_fields": ["framework_id"],
            "checklist": [
                "문제 유형에 적합한 프레임워크인가?",
                "조직의 의사결정 문화와 맞는가?",
                "프레임워크를 적용할 역량이 있는가?",
            ],
            "deliverables": ["선택된 프레임워크", "적용 계획"]
        },
        {
            "stage": DecisionStage.ANALYSIS,
            "name": "4. 분석",
            "description": "선택한 프레임워크로 심층 분석을 수행합니다",
            "required_fields": ["gap_analysis", "scenario_analysis", "risk_analysis"],
            "checklist": [
                "모든 선택지가 공정하게 평가되었는가?",
                "리스크와 불확실성이 고려되었는가?",
                "민감도 분석이 수행되었는가?",
            ],
            "deliverables": ["분석 보고서", "시나리오별 결과", "리스크 매트릭스"]
        },
        {
            "stage": DecisionStage.DECISION,
            "name": "5. 결정",
            "description": "분석 결과를 바탕으로 최종 선택을 합니다",
            "required_fields": ["selected_option", "rationale"],
            "checklist": [
                "분석 결과가 충분히 고려되었는가?",
                "이해관계자의 의견이 반영되었는가?",
                "결정 근거가 명확한가?",
            ],
            "deliverables": ["최종 선택", "결정 근거", "신뢰도 평가"]
        },
        {
            "stage": DecisionStage.EXECUTION,
            "name": "6. 실행",
            "description": "결정사항을 실행합니다",
            "required_fields": ["execution_plan"],
            "checklist": [
                "실행 계획이 구체적인가?",
                "책임자와 일정이 명확한가?",
                "모니터링 지표가 정의되었는가?",
            ],
            "deliverables": ["실행 계획", "마일스톤", "KPI"]
        },
        {
            "stage": DecisionStage.REVIEW,
            "name": "7. 회고",
            "description": "실행 결과를 평가하고 학습합니다",
            "required_fields": ["actual_outcome", "lessons_learned"],
            "checklist": [
                "예상과 실제 결과가 비교되었는가?",
                "잘된 점과 개선점이 파악되었는가?",
                "다음 의사결정에 활용할 교훈이 정리되었는가?",
            ],
            "deliverables": ["결과 보고서", "교훈 정리", "프로세스 개선안"]
        },
    ]

    @staticmethod
    def get_stage_info(stage: DecisionStage) -> Dict[str, Any]:
        """단계 정보 조회"""
        for step in DecisionWorkflow.WORKFLOW_STEPS:
            if step["stage"] == stage:
                return step
        return {}

    @staticmethod
    def get_next_stage(current_stage: DecisionStage) -> Optional[DecisionStage]:
        """다음 단계 조회"""
        stages = [step["stage"] for step in DecisionWorkflow.WORKFLOW_STEPS]
        try:
            current_idx = stages.index(current_stage)
            if current_idx < len(stages) - 1:
                return stages[current_idx + 1]
        except ValueError:
            pass
        return None

    @staticmethod
    def validate_stage_completion(record: DecisionRecord) -> Dict[str, Any]:
        """현재 단계 완료 조건 검증"""
        stage_info = DecisionWorkflow.get_stage_info(record.stage)
        required_fields = stage_info.get("required_fields", [])

        missing_fields = []
        for field in required_fields:
            value = getattr(record, field, None)
            if value is None or (isinstance(value, list) and len(value) == 0):
                missing_fields.append(field)

        is_complete = len(missing_fields) == 0

        return {
            "is_complete": is_complete,
            "missing_fields": missing_fields,
            "checklist": stage_info.get("checklist", []),
            "next_stage": DecisionWorkflow.get_next_stage(record.stage).value if is_complete else None
        }


class DecisionHistory:
    """의사결정 이력 관리"""

    def __init__(self, storage_path: str = "decision_history.json"):
        self.storage_path = storage_path
        self.records: Dict[str, DecisionRecord] = {}
        self.load()

    def load(self):
        """이력 로드"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for record_data in data.get("records", []):
                    record = DecisionRecord.from_dict(record_data)
                    self.records[record.id] = record
        except FileNotFoundError:
            pass

    def save(self):
        """이력 저장"""
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "records": [record.to_dict() for record in self.records.values()]
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_record(self, title: str, goal: str, options: List[str],
                     category: str = "strategy") -> DecisionRecord:
        """새 의사결정 기록 생성"""
        record_id = hashlib.md5(
            f"{title}{goal}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        record = DecisionRecord(
            id=record_id,
            title=title,
            goal=goal,
            options=options,
            category=category,
            stage=DecisionStage.PROBLEM_DEFINITION,
            status=DecisionStatus.DRAFT,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        self.records[record_id] = record
        self.save()
        return record

    def update_record(self, record_id: str, updates: Dict[str, Any]) -> DecisionRecord:
        """기록 업데이트"""
        if record_id not in self.records:
            raise ValueError(f"Record {record_id} not found")

        record = self.records[record_id]

        for key, value in updates.items():
            if hasattr(record, key):
                setattr(record, key, value)

        record.updated_at = datetime.now().isoformat()
        self.save()
        return record

    def get_record(self, record_id: str) -> Optional[DecisionRecord]:
        """기록 조회"""
        return self.records.get(record_id)

    def list_records(self, status: Optional[DecisionStatus] = None,
                    category: Optional[str] = None) -> List[DecisionRecord]:
        """기록 목록 조회"""
        records = list(self.records.values())

        if status:
            records = [r for r in records if r.status == status]

        if category:
            records = [r for r in records if r.category == category]

        # 최신순 정렬
        records.sort(key=lambda r: r.updated_at, reverse=True)

        return records


class IntegratedDecisionSystem:
    """통합 의사결정 시스템"""

    def __init__(self, storage_path: str = "decision_history.json"):
        self.history = DecisionHistory(storage_path)

    def start_new_decision(self, title: str, goal: str, options: List[str],
                          category: str = "strategy") -> Dict[str, Any]:
        """새로운 의사결정 시작"""
        record = self.history.create_record(title, goal, options, category)

        return {
            "record_id": record.id,
            "record": record.to_dict(),
            "current_stage": DecisionWorkflow.get_stage_info(record.stage),
            "message": f"의사결정 '{title}'이 시작되었습니다."
        }

    def add_cards(self, record_id: str, cards: List[Dict[str, Any]],
                 auto_optimize: bool = True) -> Dict[str, Any]:
        """카드 추가 (데이터 수집 단계)"""
        record = self.history.get_record(record_id)
        if not record:
            raise ValueError("Record not found")

        # 카드 최적화
        if auto_optimize:
            optimization_result = optimize_cards(
                cards,
                max_cards=7,
                remove_duplicates=True,
                remove_noise=True,
                trim_to_limit=True
            )
            optimized_cards = optimization_result['optimized_cards']
            optimization_stats = optimization_result['stats']
        else:
            optimized_cards = cards
            optimization_stats = None

        # 기존 카드에 추가
        all_cards = record.cards + optimized_cards

        # 기록 업데이트
        self.history.update_record(record_id, {
            "cards": all_cards,
            "stage": DecisionStage.DATA_COLLECTION,
            "status": DecisionStatus.IN_PROGRESS
        })

        return {
            "cards_added": len(optimized_cards),
            "total_cards": len(all_cards),
            "optimization_stats": optimization_stats,
            "message": f"{len(optimized_cards)}개 카드가 추가되었습니다."
        }

    def select_framework(self, record_id: str, framework_id: str) -> Dict[str, Any]:
        """프레임워크 선택"""
        record = self.history.get_record(record_id)
        if not record:
            raise ValueError("Record not found")

        framework = FrameworkLibrary.get_framework_by_id(framework_id)
        if not framework:
            raise ValueError(f"Framework {framework_id} not found")

        self.history.update_record(record_id, {
            "framework_id": framework_id,
            "stage": DecisionStage.FRAMEWORK_SELECTION,
        })

        return {
            "framework": {
                "id": framework.id,
                "name": framework.name,
                "description": framework.description,
                "dimensions": len(framework.dimensions),
            },
            "message": f"프레임워크 '{framework.name}'이 선택되었습니다."
        }

    def run_analysis(self, record_id: str) -> Dict[str, Any]:
        """분석 실행"""
        record = self.history.get_record(record_id)
        if not record:
            raise ValueError("Record not found")

        # 1. Gap Analysis & Data Collection Roadmap
        gap_result = analyze_decision(
            goal=record.goal,
            options=record.options,
            current_cards=record.cards,
            category=record.category
        )

        # 2. 각 옵션별 심층 분석 (첫 번째 옵션만 샘플로)
        if record.options and record.cards:
            # 옵션별 데이터 추출 (간단히 첫 옵션)
            option_data = {}
            for card in record.cards[:3]:  # 샘플
                if 'name' in card and 'value' in card:
                    try:
                        value_str = str(card.get('value', 0)).replace('원', '').replace(',', '').replace('%', '')
                        option_data[card['name']] = float(value_str)
                    except (ValueError, AttributeError):
                        pass  # 숫자로 변환할 수 없는 값은 건너뜀

            if option_data:
                deep_analyzer = DeepDecisionAnalyzer(
                    record.options[0],
                    option_data,
                    record.category
                )
                deep_result = deep_analyzer.run_full_analysis()
            else:
                deep_result = None
        else:
            deep_result = None

        # 기록 업데이트 (분석 결과는 저장 안 함 - JSON 직렬화 이슈)
        # 실제 환경에서는 별도 분석 결과 DB에 저장
        self.history.update_record(record_id, {
            "stage": DecisionStage.ANALYSIS,
        })

        return {
            "gap_analysis": gap_result,
            "deep_analysis": deep_result,
            "message": "분석이 완료되었습니다."
        }

    def make_decision(self, record_id: str, selected_option: str,
                     rationale: str, confidence: float) -> Dict[str, Any]:
        """최종 결정"""
        record = self.history.get_record(record_id)
        if not record:
            raise ValueError("Record not found")

        if selected_option not in record.options:
            raise ValueError(f"Invalid option: {selected_option}")

        self.history.update_record(record_id, {
            "selected_option": selected_option,
            "rationale": rationale,
            "confidence": confidence,
            "stage": DecisionStage.DECISION,
            "status": DecisionStatus.COMPLETED
        })

        return {
            "selected_option": selected_option,
            "confidence": confidence,
            "message": f"'{selected_option}'이(가) 선택되었습니다 (신뢰도: {confidence*100:.0f}%)"
        }

    def get_insights(self) -> Dict[str, Any]:
        """전체 의사결정 인사이트"""
        all_records = self.history.list_records()

        # 통계
        total_decisions = len(all_records)
        completed = len([r for r in all_records if r.status == DecisionStatus.COMPLETED])
        in_progress = len([r for r in all_records if r.status == DecisionStatus.IN_PROGRESS])

        # 카테고리별
        by_category = {}
        for record in all_records:
            cat = record.category
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += 1

        # 평균 신뢰도
        confidences = [r.confidence for r in all_records if r.confidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "total_decisions": total_decisions,
            "completed": completed,
            "in_progress": in_progress,
            "by_category": by_category,
            "average_confidence": avg_confidence,
            "recent_decisions": [r.to_dict() for r in all_records[:5]]
        }


if __name__ == "__main__":
    print("=" * 70)
    print("통합 의사결정 시스템 테스트")
    print("=" * 70)

    # 시스템 초기화
    system = IntegratedDecisionSystem("test_decision_history.json")

    # 1. 새 의사결정 시작
    print("\n1️⃣ 새 의사결정 시작")
    print("-" * 70)
    result = system.start_new_decision(
        title="신제품 출시 전략",
        goal="Q4까지 신제품을 성공적으로 출시하고 시장 점유율 10% 확보",
        options=["공격적 마케팅", "점진적 확대", "틈새시장 집중"],
        category="strategy"
    )
    record_id = result["record_id"]
    print(f"  ✅ {result['message']}")
    print(f"  ID: {record_id}")
    print(f"  현재 단계: {result['current_stage']['name']}")

    # 2. 카드 추가
    print("\n2️⃣ 데이터 수집 (카드 추가)")
    print("-" * 70)
    test_cards = [
        {"name": "예산", "value": 500000000, "category": "경제적", "weight": 0.8},
        {"name": "예산", "value": 500000000, "category": "경제적", "weight": 0.7},  # 중복
        {"name": "시장 성장률", "value": "15%", "category": "시장", "weight": 0.9},
    ]
    result = system.add_cards(record_id, test_cards, auto_optimize=True)
    print(f"  ✅ {result['message']}")
    if result['optimization_stats']:
        print(f"  최적화: {result['optimization_stats']['original_count']}개 → {result['optimization_stats']['final_count']}개")

    # 3. 프레임워크 선택
    print("\n3️⃣ 프레임워크 선택")
    print("-" * 70)
    result = system.select_framework(record_id, "swot")
    print(f"  ✅ {result['message']}")

    # 4. 분석
    print("\n4️⃣ 분석 실행")
    print("-" * 70)
    result = system.run_analysis(record_id)
    print(f"  ✅ {result['message']}")
    print(f"  Gap 분석: {len(result['gap_analysis']['gaps'])}개 데이터 부족")
    if result['deep_analysis']:
        print(f"  심층 분석: 시나리오 {len(result['deep_analysis']['scenario_analysis']['scenarios'])}개")

    # 5. 최종 결정
    print("\n5️⃣ 최종 결정")
    print("-" * 70)
    result = system.make_decision(
        record_id,
        selected_option="점진적 확대",
        rationale="리스크가 낮고 실행 가능성이 높음",
        confidence=0.75
    )
    print(f"  ✅ {result['message']}")

    # 6. 인사이트
    print("\n6️⃣ 전체 인사이트")
    print("-" * 70)
    insights = system.get_insights()
    print(f"  총 의사결정: {insights['total_decisions']}개")
    print(f"  완료: {insights['completed']}개, 진행중: {insights['in_progress']}개")
    print(f"  평균 신뢰도: {insights['average_confidence']*100:.0f}%")
