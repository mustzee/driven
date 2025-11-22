#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decision Framework - 합리적 의사결정 지원 시스템

사용자의 선택장애를 해결하고, 어떤 데이터를 모으면
더 합리적인 결정을 내릴 수 있는지 안내합니다.

핵심 기능:
1. Gap Analysis: 부족한 데이터 식별
2. Data Collection Roadmap: 데이터 수집 우선순위
3. Trade-off Matrix: 선택지 간 트레이드오프 비교
"""

import re
from typing import List, Dict, Any, Optional


class DecisionDimension:
    """결정을 평가하는 차원 (예: 가격, 시간, 품질 등)"""

    # 도메인별 일반적인 차원들
    COMMON_DIMENSIONS = {
        "food": ["가격", "맛", "거리", "시간", "건강", "분위기", "선호도"],
        "product": ["가격", "품질", "브랜드", "배송", "AS", "리뷰", "기능"],
        "hiring": ["경력", "기술", "문화적합성", "급여", "성장가능성", "팀워크"],
        "investment": ["수익률", "위험도", "유동성", "시장전망", "배당", "수수료"],
        "strategy": ["효과", "비용", "시간", "위험", "확장성", "팀역량"],
    }

    @classmethod
    def suggest_dimensions(cls, goal: str, category: str = None) -> List[str]:
        """Goal과 카테고리를 기반으로 평가 차원 제안"""
        # 카테고리 자동 감지
        if category is None:
            category = cls._detect_category(goal)

        base_dimensions = cls.COMMON_DIMENSIONS.get(category, [])

        # Goal에서 추가 차원 추출
        extracted = cls._extract_dimensions_from_goal(goal)

        # 중복 제거하고 병합
        all_dimensions = list(set(base_dimensions + extracted))

        return all_dimensions[:10]  # 최대 10개 차원

    @classmethod
    def _detect_category(cls, goal: str) -> str:
        """Goal 텍스트에서 카테고리 감지"""
        goal_lower = goal.lower()

        keywords = {
            "food": ["점심", "저녁", "식사", "메뉴", "음식", "먹", "restaurant"],
            "product": ["구매", "제품", "상품", "물건", "buy", "purchase"],
            "hiring": ["채용", "인재", "면접", "recruit", "hire"],
            "investment": ["투자", "주식", "펀드", "invest", "stock"],
            "strategy": ["전략", "방향", "계획", "프로젝트", "strategy", "plan"],
        }

        for category, words in keywords.items():
            if any(word in goal_lower for word in words):
                return category

        return "strategy"  # 기본값

    @classmethod
    def _extract_dimensions_from_goal(cls, goal: str) -> List[str]:
        """Goal 텍스트에서 평가 차원 추출"""
        dimensions = []

        # 패턴: "~를 고려해서", "~도 중요", "~때문에" 등
        patterns = [
            r'(\w+)[를을]\s*고려',
            r'(\w+)[도가]\s*중요',
            r'(\w+)\s*때문에',
            r'(\w+)\s*관점',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, goal)
            dimensions.extend(matches)

        return dimensions


class DataGap:
    """부족한 데이터 정보"""

    def __init__(self, dimension: str, impact: float, difficulty: str,
                 suggestion: str = ""):
        self.dimension = dimension  # 데이터 차원
        self.impact = impact  # 0.0 ~ 1.0 (결정에 미치는 영향)
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.suggestion = suggestion  # 수집 방법 제안
        self.priority = self._calculate_priority()

    def _calculate_priority(self) -> float:
        """우선순위 계산: ROI = Impact / Difficulty"""
        difficulty_weights = {
            "easy": 1.0,
            "medium": 2.0,
            "hard": 4.0,
        }

        difficulty_cost = difficulty_weights.get(self.difficulty, 2.0)
        return self.impact / difficulty_cost

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "impact": round(self.impact, 2),
            "difficulty": self.difficulty,
            "suggestion": self.suggestion,
            "priority": round(self.priority, 2),
        }


class DecisionOption:
    """결정의 선택지"""

    def __init__(self, name: str, data: Dict[str, Any] = None):
        self.name = name
        self.data = data or {}  # {차원: 값}
        self.scores = {}  # {차원: 정규화된 점수 0~1}

    def add_data(self, dimension: str, value: Any):
        """데이터 추가"""
        self.data[dimension] = value

    def get_coverage(self, required_dimensions: List[str]) -> float:
        """필요한 차원 중 얼마나 데이터가 있는지"""
        if not required_dimensions:
            return 0.0

        covered = sum(1 for dim in required_dimensions if dim in self.data)
        return covered / len(required_dimensions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "data": self.data,
            "scores": self.scores,
        }


class DecisionFramework:
    """합리적 의사결정 프레임워크"""

    def __init__(self, goal: str, options: List[str],
                 current_cards: List[Dict[str, Any]] = None,
                 category: str = None):
        self.goal = goal
        self.options = [DecisionOption(opt) for opt in options]
        self.current_cards = current_cards or []
        self.category = category or DecisionDimension._detect_category(goal)

        # 필요한 평가 차원들
        self.dimensions = DecisionDimension.suggest_dimensions(goal, self.category)

        # 현재 카드에서 데이터 추출
        self._extract_data_from_cards()

    def _extract_data_from_cards(self):
        """현재 카드들에서 각 선택지의 데이터 추출"""
        for card in self.current_cards:
            card_name = card.get("name", "")
            card_value = card.get("value")
            card_category = card.get("category", "")

            # 카드가 어떤 선택지와 관련있는지 매칭
            for option in self.options:
                if option.name.lower() in card_name.lower() or \
                   card_name.lower() in option.name.lower():
                    # 카드 카테고리를 차원으로 매핑
                    dimension = self._map_category_to_dimension(card_category)
                    if dimension:
                        option.add_data(dimension, card_value)

            # 전역 데이터 (모든 선택지에 적용)
            if "선호도" in card_name or "투표" in card_name:
                for option in self.options:
                    option.add_data("선호도", card_value)

    def _map_category_to_dimension(self, category: str) -> Optional[str]:
        """카드 카테고리를 평가 차원으로 매핑"""
        mapping = {
            "경제적": "가격",
            "시간적": "시간",
            "사회적": "선호도",
            "감정적": "만족도",
            "물리적": "거리",
            "품질": "품질",
        }
        return mapping.get(category)

    def analyze_gaps(self) -> List[DataGap]:
        """부족한 데이터 분석"""
        gaps = []

        for dimension in self.dimensions:
            # 이 차원의 데이터가 있는 선택지 개수
            covered_options = sum(
                1 for opt in self.options if dimension in opt.data
            )
            coverage = covered_options / len(self.options) if self.options else 0

            # 데이터가 부족하면 Gap으로 추가
            if coverage < 0.5:  # 50% 미만 커버리지
                impact = self._estimate_impact(dimension)
                difficulty = self._estimate_difficulty(dimension)
                suggestion = self._suggest_collection_method(dimension)

                gap = DataGap(dimension, impact, difficulty, suggestion)
                gaps.append(gap)

        # 우선순위 순으로 정렬
        gaps.sort(key=lambda g: g.priority, reverse=True)

        return gaps

    def _estimate_impact(self, dimension: str) -> float:
        """차원의 중요도 추정 (0.0 ~ 1.0)"""
        # Goal에 명시적으로 언급되었으면 높은 중요도
        if dimension in self.goal:
            return 0.9

        # 카테고리별 핵심 차원
        high_impact_dims = {
            "food": ["맛", "가격", "시간"],
            "product": ["가격", "품질", "리뷰"],
            "hiring": ["기술", "문화적합성", "경력"],
            "investment": ["수익률", "위험도"],
            "strategy": ["효과", "비용"],
        }

        critical_dims = high_impact_dims.get(self.category, [])
        if dimension in critical_dims:
            return 0.8

        return 0.5  # 기본 중요도

    def _estimate_difficulty(self, dimension: str) -> str:
        """데이터 수집 난이도 추정"""
        easy_dims = ["가격", "거리", "시간", "배송"]
        medium_dims = ["선호도", "리뷰", "기능", "경력"]
        # hard_dims는 나머지

        if dimension in easy_dims:
            return "easy"
        elif dimension in medium_dims:
            return "medium"
        else:
            return "hard"

    def _suggest_collection_method(self, dimension: str) -> str:
        """데이터 수집 방법 제안"""
        suggestions = {
            "가격": "각 선택지의 가격을 조사하세요 (웹사이트, 전화)",
            "시간": "소요 시간을 측정하거나 추정하세요",
            "거리": "지도 앱에서 거리를 확인하세요",
            "선호도": f"{len(self.options)}개 선택지에 대해 팀원 투표를 진행하세요",
            "맛": "리뷰 사이트나 지인 추천을 확인하세요",
            "품질": "제품 사양서나 리뷰를 검토하세요",
            "리뷰": "온라인 리뷰 점수(평균)를 수집하세요",
            "기술": "기술 스택 매칭도를 평가하세요 (0~100점)",
            "경력": "관련 경력 연수를 확인하세요",
        }

        return suggestions.get(
            dimension,
            f"'{dimension}' 데이터를 각 선택지별로 조사하세요"
        )

    def generate_collection_roadmap(self) -> Dict[str, Any]:
        """데이터 수집 로드맵 생성"""
        gaps = self.analyze_gaps()

        if not gaps:
            return {
                "status": "complete",
                "message": "충분한 데이터가 있습니다. 결정을 진행하세요!",
                "steps": [],
            }

        # 우선순위별로 단계 생성
        steps = []
        for i, gap in enumerate(gaps[:5], 1):  # 상위 5개만
            priority_label = "🔴 High" if gap.priority > 0.4 else \
                           "🟡 Medium" if gap.priority > 0.2 else "🟢 Low"

            steps.append({
                "step": i,
                "dimension": gap.dimension,
                "priority": priority_label,
                "priority_score": gap.priority,
                "impact": gap.impact,
                "difficulty": gap.difficulty,
                "suggestion": gap.suggestion,
                "estimated_time": self._estimate_collection_time(gap.difficulty),
            })

        # 전체 완성도 계산
        total_dimensions = len(self.dimensions)
        missing_dimensions = len(gaps)
        completeness = (total_dimensions - missing_dimensions) / total_dimensions

        return {
            "status": "incomplete",
            "completeness": round(completeness * 100, 1),
            "total_dimensions": total_dimensions,
            "missing_dimensions": missing_dimensions,
            "steps": steps,
            "estimated_total_time": sum(
                self._estimate_collection_time(s["difficulty"])
                for s in steps
            ),
        }

    def _estimate_collection_time(self, difficulty: str) -> int:
        """데이터 수집 예상 시간 (분)"""
        times = {
            "easy": 5,
            "medium": 15,
            "hard": 30,
        }
        return times.get(difficulty, 15)

    def build_tradeoff_matrix(self) -> Dict[str, Any]:
        """선택지 간 트레이드오프 매트릭스"""
        # 1. 각 선택지를 차원별로 정규화 (0~1 스코어)
        self._normalize_scores()

        # 2. 각 선택지의 장단점 분석
        comparisons = []
        for i, opt1 in enumerate(self.options):
            for opt2 in self.options[i+1:]:
                comparison = self._compare_options(opt1, opt2)
                if comparison:
                    comparisons.append(comparison)

        # 3. 전체 선택지 랭킹
        rankings = self._calculate_rankings()

        # 4. 각 선택지별 요약
        summaries = []
        for option in self.options:
            summary = {
                "name": option.name,
                "strengths": self._find_strengths(option),
                "weaknesses": self._find_weaknesses(option),
                "total_score": rankings.get(option.name, 0),
                "data_coverage": option.get_coverage(self.dimensions),
            }
            summaries.append(summary)

        return {
            "comparisons": comparisons,
            "rankings": rankings,
            "summaries": summaries,
            "confidence": self._calculate_decision_confidence(),
        }

    def _normalize_scores(self):
        """각 차원별로 선택지들의 값을 0~1로 정규화"""
        for dimension in self.dimensions:
            # 이 차원의 모든 값 수집
            values = []
            for option in self.options:
                if dimension in option.data:
                    val = option.data[dimension]
                    # 숫자로 변환 시도
                    try:
                        if isinstance(val, (int, float)):
                            values.append((option, float(val)))
                        elif isinstance(val, str):
                            # 숫자 추출
                            num = re.search(r'[\d,]+\.?\d*', val)
                            if num:
                                values.append((option, float(num.group().replace(',', ''))))
                    except:
                        pass

            if not values:
                continue

            # Min-Max 정규화
            min_val = min(v[1] for v in values)
            max_val = max(v[1] for v in values)

            if max_val == min_val:
                for option, _ in values:
                    option.scores[dimension] = 0.5
            else:
                for option, val in values:
                    # 가격, 시간, 위험도 등은 낮을수록 좋음
                    if dimension in ["가격", "시간", "위험도", "비용", "수수료"]:
                        normalized = 1.0 - (val - min_val) / (max_val - min_val)
                    else:
                        normalized = (val - min_val) / (max_val - min_val)

                    option.scores[dimension] = normalized

    def _compare_options(self, opt1: DecisionOption, opt2: DecisionOption) -> Optional[Dict]:
        """두 선택지 비교"""
        # 공통으로 데이터가 있는 차원만 비교
        common_dims = set(opt1.scores.keys()) & set(opt2.scores.keys())

        if not common_dims:
            return None

        opt1_wins = []
        opt2_wins = []

        for dim in common_dims:
            score1 = opt1.scores[dim]
            score2 = opt2.scores[dim]

            if score1 > score2 + 0.1:  # 유의미한 차이
                opt1_wins.append({
                    "dimension": dim,
                    "advantage": round((score1 - score2) * 100, 1),
                })
            elif score2 > score1 + 0.1:
                opt2_wins.append({
                    "dimension": dim,
                    "advantage": round((score2 - score1) * 100, 1),
                })

        return {
            "option1": opt1.name,
            "option2": opt2.name,
            "option1_advantages": opt1_wins,
            "option2_advantages": opt2_wins,
        }

    def _find_strengths(self, option: DecisionOption) -> List[str]:
        """선택지의 강점 (상위 3개 차원)"""
        if not option.scores:
            return []

        sorted_dims = sorted(
            option.scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            f"{dim}: {score*100:.0f}점"
            for dim, score in sorted_dims[:3]
            if score > 0.6
        ]

    def _find_weaknesses(self, option: DecisionOption) -> List[str]:
        """선택지의 약점 (하위 3개 차원)"""
        if not option.scores:
            return []

        sorted_dims = sorted(
            option.scores.items(),
            key=lambda x: x[1]
        )

        return [
            f"{dim}: {score*100:.0f}점"
            for dim, score in sorted_dims[:3]
            if score < 0.4
        ]

    def _calculate_rankings(self) -> Dict[str, float]:
        """전체 선택지 랭킹 (평균 점수)"""
        rankings = {}

        for option in self.options:
            if option.scores:
                avg_score = sum(option.scores.values()) / len(option.scores)
                rankings[option.name] = round(avg_score * 100, 1)
            else:
                rankings[option.name] = 0.0

        return rankings

    def _calculate_decision_confidence(self) -> Dict[str, Any]:
        """현재 데이터로 결정할 수 있는 신뢰도"""
        total_coverage = sum(
            opt.get_coverage(self.dimensions) for opt in self.options
        ) / len(self.options) if self.options else 0

        # 데이터 품질 점수
        avg_dimensions_per_option = sum(
            len(opt.data) for opt in self.options
        ) / len(self.options) if self.options else 0

        quality = min(avg_dimensions_per_option / len(self.dimensions), 1.0) if self.dimensions else 0

        # 최종 신뢰도 = (커버리지 + 품질) / 2
        confidence_score = (total_coverage + quality) / 2

        if confidence_score >= 0.8:
            level = "high"
            message = "충분한 데이터가 있습니다. 자신있게 결정하세요!"
        elif confidence_score >= 0.5:
            level = "medium"
            message = "기본적인 결정은 가능하지만, 더 많은 데이터가 있으면 좋습니다."
        else:
            level = "low"
            message = "데이터가 부족합니다. 더 많은 정보를 수집하는 것을 권장합니다."

        return {
            "score": round(confidence_score * 100, 1),
            "level": level,
            "message": message,
            "coverage": round(total_coverage * 100, 1),
            "quality": round(quality * 100, 1),
        }

    def generate_full_analysis(self) -> Dict[str, Any]:
        """전체 분석 결과 생성"""
        gaps = self.analyze_gaps()
        roadmap = self.generate_collection_roadmap()
        tradeoff = self.build_tradeoff_matrix()

        return {
            "goal": self.goal,
            "category": self.category,
            "options": [opt.name for opt in self.options],
            "dimensions": self.dimensions,
            "gaps": [gap.to_dict() for gap in gaps],
            "roadmap": roadmap,
            "tradeoff": tradeoff,
            "recommendation": self._generate_recommendation(tradeoff),
        }

    def _generate_recommendation(self, tradeoff: Dict) -> str:
        """최종 추천 메시지"""
        confidence = tradeoff["confidence"]
        rankings = tradeoff["rankings"]

        if not rankings:
            return "선택지들의 데이터를 더 수집해주세요."

        # 1위 선택지
        top_option = max(rankings.items(), key=lambda x: x[1])

        if confidence["level"] == "high":
            return f"✅ 추천: '{top_option[0]}' (신뢰도 {confidence['score']}%)"
        elif confidence["level"] == "medium":
            return f"⚠️ 잠정 추천: '{top_option[0]}' (신뢰도 {confidence['score']}%) - 더 많은 데이터 수집 권장"
        else:
            return f"❌ 데이터 부족 (신뢰도 {confidence['score']}%) - 결정 보류하고 데이터 수집 먼저 진행하세요"


def analyze_decision(goal: str, options: List[str],
                    current_cards: List[Dict] = None,
                    category: str = None) -> Dict[str, Any]:
    """Decision Framework 실행 (메인 함수)"""
    framework = DecisionFramework(goal, options, current_cards, category)
    return framework.generate_full_analysis()


if __name__ == "__main__":
    # 테스트 케이스 1: 점심 메뉴 선택 (데이터 일부만 있음)
    print("=" * 60)
    print("테스트 1: 점심 메뉴 선택 (부분 데이터)")
    print("=" * 60)

    result1 = analyze_decision(
        goal="점심 메뉴를 선택하려고 합니다. 맛과 시간이 중요합니다.",
        options=["이탈리안", "한식", "중식"],
        current_cards=[
            {"name": "이탈리안 가격", "value": "12000원", "category": "경제적"},
            {"name": "한식 가격", "value": "9000원", "category": "경제적"},
            {"name": "중식 가격", "value": "10000원", "category": "경제적"},
        ],
        category="food"
    )

    print("\n📊 Gap Analysis:")
    for gap in result1["gaps"][:3]:
        print(f"  - {gap['dimension']}: 중요도 {gap['impact']}, "
              f"난이도 {gap['difficulty']}, 우선순위 {gap['priority']}")

    print(f"\n🗺️ Data Collection Roadmap:")
    print(f"  완성도: {result1['roadmap']['completeness']}%")
    for step in result1['roadmap']['steps'][:3]:
        print(f"  Step {step['step']}: {step['dimension']} ({step['priority']})")
        print(f"    → {step['suggestion']}")

    print(f"\n⚖️ Trade-off Matrix:")
    print(f"  신뢰도: {result1['tradeoff']['confidence']['score']}% "
          f"({result1['tradeoff']['confidence']['level']})")
    for summary in result1['tradeoff']['summaries']:
        print(f"  - {summary['name']}: {summary['total_score']}점 "
              f"(데이터 커버리지 {summary['data_coverage']*100:.0f}%)")

    print(f"\n💡 {result1['recommendation']}")

    # 테스트 케이스 2: 신제품 전략 (데이터 충분)
    print("\n\n" + "=" * 60)
    print("테스트 2: 신제품 전략 선택 (충분한 데이터)")
    print("=" * 60)

    result2 = analyze_decision(
        goal="신제품 출시 전략을 결정해야 합니다.",
        options=["공격적 마케팅", "점진적 확대", "틈새시장 집중"],
        current_cards=[
            {"name": "공격적 마케팅 비용", "value": "5억", "category": "경제적"},
            {"name": "점진적 확대 비용", "value": "2억", "category": "경제적"},
            {"name": "틈새시장 집중 비용", "value": "1억", "category": "경제적"},
            {"name": "공격적 마케팅 효과", "value": "85", "category": "품질"},
            {"name": "점진적 확대 효과", "value": "65", "category": "품질"},
            {"name": "틈새시장 집중 효과", "value": "70", "category": "품질"},
            {"name": "공격적 마케팅 시간", "value": "3개월", "category": "시간적"},
            {"name": "점진적 확대 시간", "value": "12개월", "category": "시간적"},
            {"name": "틈새시장 집중 시간", "value": "6개월", "category": "시간적"},
        ],
        category="strategy"
    )

    print(f"\n📊 Roadmap Status: {result2['roadmap']['status']}")
    print(f"  완성도: {result2['roadmap']['completeness']}%")

    print(f"\n⚖️ Trade-off Rankings:")
    for summary in result2['tradeoff']['summaries']:
        print(f"  - {summary['name']}: {summary['total_score']}점")
        if summary['strengths']:
            print(f"    강점: {', '.join(summary['strengths'])}")
        if summary['weaknesses']:
            print(f"    약점: {', '.join(summary['weaknesses'])}")

    print(f"\n💡 {result2['recommendation']}")
