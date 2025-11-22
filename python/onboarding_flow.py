"""
온보딩 시스템: 질문 기반 구체화 엔진
점진적 질문으로 의사결정 맥락 수집
"""

from typing import List, Dict, Any, Tuple


class OnboardingFlow:
    """온보딩 플로우 관리"""

    # 사전 정의된 시나리오 템플릿
    SCENARIOS = {
        "lunch": {
            "name": "점심 메뉴 선택",
            "description": "오늘 점심 어디서 먹을지 결정하기",
            "icon": "🍽️",
            "questions": [
                {
                    "id": "q1",
                    "text": "점심 식사의 주요 목적은 무엇인가요?",
                    "weight": 0.3,
                    "category": "심리적",
                    "options": [
                        {"text": "빠르게 끼니 해결", "value": "efficiency", "weight_bonus": 0.1},
                        {"text": "맛있는 음식 즐기기", "value": "taste", "weight_bonus": 0.2},
                        {"text": "동료와 소통", "value": "social", "weight_bonus": 0.15},
                        {"text": "건강한 식사", "value": "health", "weight_bonus": 0.15}
                    ]
                },
                {
                    "id": "q2",
                    "text": "가장 중요한 제약사항은 무엇인가요?",
                    "weight": 0.5,
                    "category": "제약적",
                    "options": [
                        {"text": "시간 (30분 이내)", "value": "time", "weight_bonus": 0.2},
                        {"text": "예산 (만원 이하)", "value": "budget", "weight_bonus": 0.25},
                        {"text": "거리 (가까운 곳)", "value": "distance", "weight_bonus": 0.15},
                        {"text": "특별한 제약 없음", "value": "none", "weight_bonus": 0}
                    ]
                },
                {
                    "id": "q3",
                    "text": "최종 결정에서 가장 우선시할 요소는?",
                    "weight": 0.8,
                    "category": "핵심",
                    "options": [
                        {"text": "만족도 (후회 없는 선택)", "value": "satisfaction", "weight_bonus": 0.3},
                        {"text": "효율성 (빠른 결정)", "value": "efficiency", "weight_bonus": 0.2},
                        {"text": "경제성 (가성비)", "value": "value", "weight_bonus": 0.25},
                        {"text": "새로운 경험", "value": "novelty", "weight_bonus": 0.2}
                    ]
                }
            ]
        },
        "product": {
            "name": "제품 전략 수립",
            "description": "신제품 로드맵 의사결정",
            "icon": "🚀",
            "questions": [
                {
                    "id": "q1",
                    "text": "제품의 주요 목표 시장은 어디인가요?",
                    "weight": 0.4,
                    "category": "전략적",
                    "options": [
                        {"text": "국내 시장", "value": "domestic", "weight_bonus": 0.1},
                        {"text": "글로벌 진출", "value": "global", "weight_bonus": 0.3},
                        {"text": "특정 니치 시장", "value": "niche", "weight_bonus": 0.2}
                    ]
                },
                {
                    "id": "q2",
                    "text": "현재 가장 큰 제약사항은?",
                    "weight": 0.6,
                    "category": "제약적",
                    "options": [
                        {"text": "예산 부족", "value": "budget", "weight_bonus": 0.25},
                        {"text": "인력 부족", "value": "team", "weight_bonus": 0.2},
                        {"text": "기술적 한계", "value": "tech", "weight_bonus": 0.3},
                        {"text": "시간 압박", "value": "time", "weight_bonus": 0.25}
                    ]
                },
                {
                    "id": "q3",
                    "text": "성공의 핵심 지표는 무엇인가요?",
                    "weight": 0.9,
                    "category": "핵심",
                    "options": [
                        {"text": "매출 성장", "value": "revenue", "weight_bonus": 0.35},
                        {"text": "사용자 수", "value": "users", "weight_bonus": 0.3},
                        {"text": "시장 점유율", "value": "market_share", "weight_bonus": 0.3},
                        {"text": "브랜드 인지도", "value": "brand", "weight_bonus": 0.2}
                    ]
                }
            ]
        },
        "hiring": {
            "name": "채용 결정",
            "description": "신규 인력 채용 의사결정",
            "icon": "👥",
            "questions": [
                {
                    "id": "q1",
                    "text": "채용의 주요 목적은 무엇인가요?",
                    "weight": 0.4,
                    "category": "전략적",
                    "options": [
                        {"text": "긴급한 공백 메우기", "value": "urgent", "weight_bonus": 0.2},
                        {"text": "팀 확장", "value": "growth", "weight_bonus": 0.25},
                        {"text": "전문성 보강", "value": "expertise", "weight_bonus": 0.3}
                    ]
                },
                {
                    "id": "q2",
                    "text": "가장 중요한 평가 기준은?",
                    "weight": 0.6,
                    "category": "평가",
                    "options": [
                        {"text": "기술 역량", "value": "tech", "weight_bonus": 0.3},
                        {"text": "문화 적합성", "value": "culture", "weight_bonus": 0.25},
                        {"text": "경력/경험", "value": "experience", "weight_bonus": 0.2},
                        {"text": "성장 가능성", "value": "potential", "weight_bonus": 0.25}
                    ]
                },
                {
                    "id": "q3",
                    "text": "최종 결정 시 가장 고려할 요소는?",
                    "weight": 0.85,
                    "category": "핵심",
                    "options": [
                        {"text": "즉시 기여 가능성", "value": "immediate", "weight_bonus": 0.3},
                        {"text": "장기적 성장성", "value": "longterm", "weight_bonus": 0.35},
                        {"text": "팀 시너지", "value": "synergy", "weight_bonus": 0.25},
                        {"text": "급여 협상 여지", "value": "salary", "weight_bonus": 0.15}
                    ]
                }
            ]
        }
    }

    def __init__(self, scenario_type: str = "lunch"):
        """
        Args:
            scenario_type: 시나리오 타입 (lunch, product, hiring)
        """
        if scenario_type not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_type}")

        self.scenario = self.SCENARIOS[scenario_type]
        self.answers = {}  # {question_id: selected_option}
        self.current_question_index = 0

    def get_current_question(self) -> Dict[str, Any]:
        """현재 질문 가져오기"""
        if self.current_question_index >= len(self.scenario["questions"]):
            return None

        return self.scenario["questions"][self.current_question_index]

    def answer_question(self, option_value: str) -> bool:
        """
        질문에 답변

        Args:
            option_value: 선택한 옵션의 value

        Returns:
            다음 질문이 있는지 여부
        """
        current_q = self.get_current_question()
        if not current_q:
            return False

        # 답변 저장
        self.answers[current_q["id"]] = option_value

        # 다음 질문으로
        self.current_question_index += 1

        return self.current_question_index < len(self.scenario["questions"])

    def generate_cards(self) -> List[Dict[str, Any]]:
        """
        답변 기반 카드 생성

        가중치 계산:
        - 기본 가중치 = 질문의 weight
        - 보너스 = 선택한 옵션의 weight_bonus
        - 최종 = 기본 + 보너스
        """
        cards = []

        for question in self.scenario["questions"]:
            q_id = question["id"]

            if q_id not in self.answers:
                continue

            selected_value = self.answers[q_id]

            # 선택한 옵션 찾기
            selected_option = None
            for option in question["options"]:
                if option["value"] == selected_value:
                    selected_option = option
                    break

            if not selected_option:
                continue

            # 카드 생성
            base_weight = question["weight"]
            bonus = selected_option["weight_bonus"]
            final_weight = min(base_weight + bonus, 1.0)

            card = {
                "name": question["text"][:20] + "...",  # 짧게
                "category": question["category"],
                "value": selected_option["text"],
                "weight": final_weight,
                "source": f"{question['text']} → {selected_option['text']}",
                "metadata": {
                    "question_id": q_id,
                    "question_weight": base_weight,
                    "option_bonus": bonus,
                    "option_value": selected_value
                }
            }

            cards.append(card)

        return cards

    def get_summary(self) -> Dict[str, Any]:
        """온보딩 완료 후 요약"""
        cards = self.generate_cards()

        # 가장 높은 가중치 카드 = 핵심 아젠다
        if cards:
            main_card = max(cards, key=lambda c: c["weight"])
        else:
            main_card = None

        return {
            "scenario": self.scenario["name"],
            "total_questions": len(self.scenario["questions"]),
            "answered": len(self.answers),
            "cards": cards,
            "main_agenda": main_card["name"] if main_card else None,
            "main_weight": main_card["weight"] if main_card else 0
        }

    def get_progress(self) -> Tuple[int, int]:
        """진행도 (현재, 전체)"""
        return (self.current_question_index, len(self.scenario["questions"]))


def get_available_scenarios() -> List[Dict[str, str]]:
    """사용 가능한 시나리오 목록"""
    return [
        {
            "id": key,
            "name": scenario["name"],
            "description": scenario["description"],
            "icon": scenario["icon"]
        }
        for key, scenario in OnboardingFlow.SCENARIOS.items()
    ]


def quick_demo(scenario_type: str = "lunch"):
    """빠른 데모"""
    print(f"\n{'='*60}")
    print(f"📚 온보딩 플로우 데모: {scenario_type}")
    print(f"{'='*60}\n")

    flow = OnboardingFlow(scenario_type)

    # 자동으로 첫 번째 옵션 선택
    while True:
        question = flow.get_current_question()
        if not question:
            break

        print(f"Q{flow.current_question_index + 1}. {question['text']}")
        print(f"   (가중치: {question['weight']}, 카테고리: {question['category']})")

        for i, option in enumerate(question["options"], 1):
            print(f"   {i}. {option['text']} (보너스: +{option['weight_bonus']})")

        # 첫 번째 옵션 자동 선택
        selected = question["options"][0]
        print(f"   → 선택: {selected['text']}\n")

        flow.answer_question(selected["value"])

    # 요약
    summary = flow.get_summary()

    print(f"\n{'='*60}")
    print("✅ 온보딩 완료!")
    print(f"{'='*60}\n")

    print(f"시나리오: {summary['scenario']}")
    print(f"답변한 질문: {summary['answered']}/{summary['total_questions']}")
    print(f"핵심 아젠다: {summary['main_agenda']} (가중치: {summary['main_weight']:.2f})")

    print(f"\n생성된 카드:")
    for i, card in enumerate(summary['cards'], 1):
        print(f"{i}. [{card['name']}]")
        print(f"   값: {card['value']}")
        print(f"   가중치: {card['weight']:.2f} "
              f"(기본 {card['metadata']['question_weight']:.2f} "
              f"+ 보너스 {card['metadata']['option_bonus']:.2f})")
        print(f"   카테고리: {card['category']}")
        print()


if __name__ == "__main__":
    # 모든 시나리오 데모
    for scenario_type in ["lunch", "product", "hiring"]:
        quick_demo(scenario_type)
        print("\n")
