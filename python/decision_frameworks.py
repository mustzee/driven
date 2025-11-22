#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decision Frameworks - 구체적인 의사결정 프레임워크 템플릿

McKinsey, BCG, SWOT, Porter's 5 Forces 등
실제 비즈니스에서 사용하는 검증된 프레임워크들
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FrameworkDimension:
    """프레임워크 평가 차원"""
    name: str
    description: str
    weight: float = 1.0
    scoring_guide: Dict[str, str] = field(default_factory=dict)


@dataclass
class DecisionFrameworkTemplate:
    """의사결정 프레임워크 템플릿"""
    id: str
    name: str
    description: str
    category: str
    dimensions: List[FrameworkDimension]
    questions: List[Dict[str, Any]] = field(default_factory=list)
    analysis_method: str = "weighted_sum"


class FrameworkLibrary:
    """의사결정 프레임워크 라이브러리"""

    @staticmethod
    def get_mckinsey_7s() -> DecisionFrameworkTemplate:
        """McKinsey 7S Framework - 조직 변화/전략 실행"""
        return DecisionFrameworkTemplate(
            id="mckinsey_7s",
            name="McKinsey 7S Framework",
            description="조직의 7가지 핵심 요소 분석을 통한 전략 실행 및 조직 변화 관리",
            category="strategy",
            dimensions=[
                FrameworkDimension(
                    name="Strategy (전략)",
                    description="경쟁 우위를 확보하기 위한 계획",
                    weight=1.0,
                    scoring_guide={
                        "high": "명확하고 차별화된 전략",
                        "medium": "전략은 있으나 차별화 부족",
                        "low": "전략이 모호하거나 없음"
                    }
                ),
                FrameworkDimension(
                    name="Structure (구조)",
                    description="조직의 계층 구조와 보고 체계",
                    weight=0.9,
                    scoring_guide={
                        "high": "전략 실행에 최적화된 구조",
                        "medium": "구조는 있으나 개선 필요",
                        "low": "비효율적인 조직 구조"
                    }
                ),
                FrameworkDimension(
                    name="Systems (시스템)",
                    description="업무 프로세스 및 절차",
                    weight=0.8,
                    scoring_guide={
                        "high": "자동화되고 효율적인 시스템",
                        "medium": "기본 시스템 존재",
                        "low": "시스템 부족 또는 비효율"
                    }
                ),
                FrameworkDimension(
                    name="Shared Values (공유 가치)",
                    description="조직의 핵심 가치와 문화",
                    weight=1.0,
                    scoring_guide={
                        "high": "명확하고 공유된 가치",
                        "medium": "가치는 있으나 공유 부족",
                        "low": "가치가 없거나 혼란"
                    }
                ),
                FrameworkDimension(
                    name="Skills (역량)",
                    description="조직과 구성원의 핵심 역량",
                    weight=0.9,
                    scoring_guide={
                        "high": "전략 실행에 필요한 역량 보유",
                        "medium": "기본 역량은 있으나 부족",
                        "low": "역량 격차가 큼"
                    }
                ),
                FrameworkDimension(
                    name="Staff (인력)",
                    description="인재 채용, 육성, 배치",
                    weight=0.8,
                    scoring_guide={
                        "high": "적재적소 인력 배치",
                        "medium": "인력은 있으나 최적화 필요",
                        "low": "인력 부족 또는 미스매치"
                    }
                ),
                FrameworkDimension(
                    name="Style (리더십 스타일)",
                    description="리더십 및 경영 스타일",
                    weight=0.7,
                    scoring_guide={
                        "high": "상황에 맞는 유연한 리더십",
                        "medium": "리더십은 있으나 개선 필요",
                        "low": "리더십 부재 또는 부적절"
                    }
                ),
            ],
            questions=[
                {
                    "dimension": "Strategy",
                    "question": "우리의 전략은 명확하고 차별화되어 있는가?",
                    "type": "rating",
                    "scale": [1, 2, 3, 4, 5]
                },
                {
                    "dimension": "Structure",
                    "question": "조직 구조가 전략 실행에 최적화되어 있는가?",
                    "type": "rating",
                    "scale": [1, 2, 3, 4, 5]
                },
                # ... 각 차원마다 질문
            ],
            analysis_method="gap_analysis"
        )

    @staticmethod
    def get_swot() -> DecisionFrameworkTemplate:
        """SWOT Analysis - 전략 수립"""
        return DecisionFrameworkTemplate(
            id="swot",
            name="SWOT Analysis",
            description="강점, 약점, 기회, 위협 분석을 통한 전략 수립",
            category="strategy",
            dimensions=[
                FrameworkDimension(
                    name="Strengths (강점)",
                    description="내부의 경쟁 우위 요소",
                    weight=1.0,
                    scoring_guide={
                        "high": "3개 이상의 명확한 강점",
                        "medium": "1-2개의 강점",
                        "low": "강점이 불분명"
                    }
                ),
                FrameworkDimension(
                    name="Weaknesses (약점)",
                    description="내부의 개선이 필요한 요소",
                    weight=1.0,
                    scoring_guide={
                        "high": "약점이 명확히 파악됨",
                        "medium": "일부 약점 파악",
                        "low": "약점 파악 안 됨"
                    }
                ),
                FrameworkDimension(
                    name="Opportunities (기회)",
                    description="외부의 활용 가능한 기회",
                    weight=1.0,
                    scoring_guide={
                        "high": "명확한 시장 기회 존재",
                        "medium": "일부 기회 있음",
                        "low": "기회가 불분명"
                    }
                ),
                FrameworkDimension(
                    name="Threats (위협)",
                    description="외부의 위협 요인",
                    weight=1.0,
                    scoring_guide={
                        "high": "위협이 명확히 파악됨",
                        "medium": "일부 위협 있음",
                        "low": "위협 파악 안 됨"
                    }
                ),
            ],
            questions=[
                {
                    "dimension": "Strengths",
                    "question": "우리의 핵심 강점 3가지는 무엇인가?",
                    "type": "open",
                },
                {
                    "dimension": "Weaknesses",
                    "question": "개선이 시급한 약점은 무엇인가?",
                    "type": "open",
                },
                {
                    "dimension": "Opportunities",
                    "question": "지금 활용할 수 있는 시장 기회는?",
                    "type": "open",
                },
                {
                    "dimension": "Threats",
                    "question": "가장 큰 외부 위협은 무엇인가?",
                    "type": "open",
                },
            ],
            analysis_method="quadrant"
        )

    @staticmethod
    def get_porter_5_forces() -> DecisionFrameworkTemplate:
        """Porter's 5 Forces - 산업 구조 분석"""
        return DecisionFrameworkTemplate(
            id="porter_5_forces",
            name="Porter's 5 Forces",
            description="산업 구조 분석을 통한 경쟁 전략 수립",
            category="strategy",
            dimensions=[
                FrameworkDimension(
                    name="경쟁 강도 (Rivalry)",
                    description="기존 경쟁자들 간의 경쟁 강도",
                    weight=1.0,
                    scoring_guide={
                        "high": "치열한 경쟁 (가격 전쟁, 마케팅 경쟁)",
                        "medium": "중간 수준의 경쟁",
                        "low": "경쟁 강도 낮음 (과점 또는 독점)"
                    }
                ),
                FrameworkDimension(
                    name="신규 진입 위협 (New Entrants)",
                    description="새로운 경쟁자의 진입 가능성",
                    weight=0.9,
                    scoring_guide={
                        "high": "진입 장벽 낮음 (쉽게 진입 가능)",
                        "medium": "중간 수준의 진입 장벽",
                        "low": "진입 장벽 높음 (규제, 자본, 기술)"
                    }
                ),
                FrameworkDimension(
                    name="대체재 위협 (Substitutes)",
                    description="대체 제품/서비스의 위협",
                    weight=0.9,
                    scoring_guide={
                        "high": "대체재 많고 전환 비용 낮음",
                        "medium": "일부 대체재 존재",
                        "low": "대체재 거의 없음"
                    }
                ),
                FrameworkDimension(
                    name="구매자 협상력 (Buyer Power)",
                    description="고객의 협상력",
                    weight=0.8,
                    scoring_guide={
                        "high": "구매자 협상력 강함 (대량 구매, 선택 많음)",
                        "medium": "중간 수준",
                        "low": "구매자 협상력 약함 (선택 제한)"
                    }
                ),
                FrameworkDimension(
                    name="공급자 협상력 (Supplier Power)",
                    description="공급업체의 협상력",
                    weight=0.8,
                    scoring_guide={
                        "high": "공급자 협상력 강함 (독점, 대체 불가)",
                        "medium": "중간 수준",
                        "low": "공급자 협상력 약함 (다수 존재)"
                    }
                ),
            ],
            questions=[
                {
                    "dimension": "경쟁 강도",
                    "question": "시장 내 경쟁 강도를 평가하세요 (1-5)",
                    "type": "rating",
                    "scale": [1, 2, 3, 4, 5]
                },
                {
                    "dimension": "신규 진입 위협",
                    "question": "신규 진입이 얼마나 쉬운가? (1-5)",
                    "type": "rating",
                    "scale": [1, 2, 3, 4, 5]
                },
                # ... 각 차원마다 질문
            ],
            analysis_method="weighted_sum"
        )

    @staticmethod
    def get_bcg_matrix() -> DecisionFrameworkTemplate:
        """BCG Growth-Share Matrix - 포트폴리오 관리"""
        return DecisionFrameworkTemplate(
            id="bcg_matrix",
            name="BCG Growth-Share Matrix",
            description="사업 포트폴리오 분석 및 자원 배분 전략",
            category="strategy",
            dimensions=[
                FrameworkDimension(
                    name="시장 성장률 (Market Growth)",
                    description="해당 시장의 성장 속도",
                    weight=1.0,
                    scoring_guide={
                        "high": "연 10% 이상 고성장",
                        "medium": "연 5-10% 성장",
                        "low": "연 5% 미만 저성장"
                    }
                ),
                FrameworkDimension(
                    name="상대적 시장 점유율 (Relative Market Share)",
                    description="1위 경쟁자 대비 시장 점유율",
                    weight=1.0,
                    scoring_guide={
                        "high": "1.0 이상 (시장 리더)",
                        "medium": "0.5-1.0",
                        "low": "0.5 미만"
                    }
                ),
            ],
            questions=[
                {
                    "dimension": "시장 성장률",
                    "question": "시장의 연평균 성장률은? (CAGR %)",
                    "type": "number",
                },
                {
                    "dimension": "상대적 시장 점유율",
                    "question": "1위 경쟁자 대비 우리의 점유율 비율은?",
                    "type": "number",
                },
            ],
            analysis_method="quadrant"
        )

    @staticmethod
    def get_raci_matrix() -> DecisionFrameworkTemplate:
        """RACI Matrix - 역할과 책임 명확화"""
        return DecisionFrameworkTemplate(
            id="raci",
            name="RACI Matrix",
            description="프로젝트/의사결정에서 역할과 책임을 명확히 정의",
            category="project",
            dimensions=[
                FrameworkDimension(
                    name="Responsible (실행자)",
                    description="실제 작업을 수행하는 사람",
                    weight=1.0,
                ),
                FrameworkDimension(
                    name="Accountable (책임자)",
                    description="최종 책임을 지는 사람 (1명)",
                    weight=1.0,
                ),
                FrameworkDimension(
                    name="Consulted (협의 대상)",
                    description="의견을 구해야 하는 사람",
                    weight=0.8,
                ),
                FrameworkDimension(
                    name="Informed (정보 공유)",
                    description="결과를 알려야 하는 사람",
                    weight=0.6,
                ),
            ],
            questions=[
                {
                    "question": "각 태스크의 실행자(R)가 명확한가?",
                    "type": "yes_no",
                },
                {
                    "question": "최종 책임자(A)가 1명으로 지정되었는가?",
                    "type": "yes_no",
                },
            ],
            analysis_method="coverage"
        )

    @staticmethod
    def get_ice_score() -> DecisionFrameworkTemplate:
        """ICE Score - 우선순위 결정"""
        return DecisionFrameworkTemplate(
            id="ice_score",
            name="ICE Score (Impact-Confidence-Ease)",
            description="프로젝트/아이디어 우선순위 결정",
            category="prioritization",
            dimensions=[
                FrameworkDimension(
                    name="Impact (영향도)",
                    description="성공했을 때의 임팩트",
                    weight=1.0,
                    scoring_guide={
                        "10": "게임 체인저급 임팩트",
                        "5": "중간 수준 임팩트",
                        "1": "미미한 임팩트"
                    }
                ),
                FrameworkDimension(
                    name="Confidence (신뢰도)",
                    description="성공 가능성에 대한 확신",
                    weight=1.0,
                    scoring_guide={
                        "10": "매우 확신함 (90%+)",
                        "5": "중간 (50%)",
                        "1": "확신 없음 (10%)"
                    }
                ),
                FrameworkDimension(
                    name="Ease (용이성)",
                    description="실행의 용이함",
                    weight=1.0,
                    scoring_guide={
                        "10": "매우 쉬움 (1주 이내)",
                        "5": "중간 (1-3개월)",
                        "1": "매우 어려움 (6개월+)"
                    }
                ),
            ],
            questions=[
                {
                    "dimension": "Impact",
                    "question": "이 아이디어의 임팩트를 1-10으로 평가하세요",
                    "type": "rating",
                    "scale": list(range(1, 11))
                },
                {
                    "dimension": "Confidence",
                    "question": "성공 확신도를 1-10으로 평가하세요",
                    "type": "rating",
                    "scale": list(range(1, 11))
                },
                {
                    "dimension": "Ease",
                    "question": "실행 용이성을 1-10으로 평가하세요",
                    "type": "rating",
                    "scale": list(range(1, 11))
                },
            ],
            analysis_method="multiply"  # ICE = Impact * Confidence * Ease
        )

    @staticmethod
    def get_rice_score() -> DecisionFrameworkTemplate:
        """RICE Score - 제품 우선순위 결정"""
        return DecisionFrameworkTemplate(
            id="rice_score",
            name="RICE Score (Reach-Impact-Confidence-Effort)",
            description="제품 기능 우선순위 결정 (Product Management)",
            category="product",
            dimensions=[
                FrameworkDimension(
                    name="Reach (도달 범위)",
                    description="영향을 받을 사용자 수",
                    weight=1.0,
                    scoring_guide={
                        "high": "전체 사용자의 50% 이상",
                        "medium": "10-50%",
                        "low": "10% 미만"
                    }
                ),
                FrameworkDimension(
                    name="Impact (영향도)",
                    description="개별 사용자에 대한 영향",
                    weight=1.0,
                    scoring_guide={
                        "3": "Massive impact",
                        "2": "High impact",
                        "1": "Medium impact",
                        "0.5": "Low impact",
                        "0.25": "Minimal impact"
                    }
                ),
                FrameworkDimension(
                    name="Confidence (신뢰도)",
                    description="추정치에 대한 확신",
                    weight=1.0,
                    scoring_guide={
                        "100%": "높은 확신 (데이터 기반)",
                        "80%": "중간 확신",
                        "50%": "낮은 확신 (추측)"
                    }
                ),
                FrameworkDimension(
                    name="Effort (노력)",
                    description="소요 공수 (인월: person-months)",
                    weight=1.0,
                    scoring_guide={
                        "0.5": "2주 이내",
                        "1": "1개월",
                        "3": "3개월",
                        "6": "6개월+"
                    }
                ),
            ],
            questions=[],
            analysis_method="rice"  # (Reach * Impact * Confidence) / Effort
        )

    @staticmethod
    def get_all_frameworks() -> List[DecisionFrameworkTemplate]:
        """모든 프레임워크 반환"""
        return [
            FrameworkLibrary.get_mckinsey_7s(),
            FrameworkLibrary.get_swot(),
            FrameworkLibrary.get_porter_5_forces(),
            FrameworkLibrary.get_bcg_matrix(),
            FrameworkLibrary.get_raci_matrix(),
            FrameworkLibrary.get_ice_score(),
            FrameworkLibrary.get_rice_score(),
        ]

    @staticmethod
    def get_framework_by_id(framework_id: str) -> Optional[DecisionFrameworkTemplate]:
        """ID로 프레임워크 조회"""
        frameworks = FrameworkLibrary.get_all_frameworks()
        for fw in frameworks:
            if fw.id == framework_id:
                return fw
        return None

    @staticmethod
    def get_frameworks_by_category(category: str) -> List[DecisionFrameworkTemplate]:
        """카테고리별 프레임워크 조회"""
        frameworks = FrameworkLibrary.get_all_frameworks()
        return [fw for fw in frameworks if fw.category == category]


def list_frameworks():
    """프레임워크 목록 출력"""
    frameworks = FrameworkLibrary.get_all_frameworks()

    print("=" * 70)
    print("의사결정 프레임워크 라이브러리")
    print("=" * 70)

    by_category = {}
    for fw in frameworks:
        if fw.category not in by_category:
            by_category[fw.category] = []
        by_category[fw.category].append(fw)

    for category, fws in by_category.items():
        print(f"\n📁 {category.upper()}")
        for fw in fws:
            print(f"  • {fw.name} ({fw.id})")
            print(f"    {fw.description}")
            print(f"    차원: {len(fw.dimensions)}개, 질문: {len(fw.questions)}개")


if __name__ == "__main__":
    # 프레임워크 목록 출력
    list_frameworks()

    # SWOT 상세 출력
    print("\n\n" + "=" * 70)
    print("SWOT Analysis 상세")
    print("=" * 70)

    swot = FrameworkLibrary.get_swot()
    print(f"\n{swot.name}")
    print(f"{swot.description}\n")

    print("평가 차원:")
    for dim in swot.dimensions:
        print(f"\n  {dim.name}")
        print(f"  {dim.description}")
        print(f"  가중치: {dim.weight}")
        if dim.scoring_guide:
            print(f"  평가 기준:")
            for level, desc in dim.scoring_guide.items():
                print(f"    - {level}: {desc}")

    print("\n질문:")
    for q in swot.questions:
        print(f"  Q: {q['question']}")
        print(f"     (차원: {q.get('dimension', 'N/A')}, 타입: {q['type']})")
