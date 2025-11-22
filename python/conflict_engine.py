"""
상충도 계산 엔진
같은 카테고리 내 옵션들의 상충 관계를 수학적으로 정량화
"""

from typing import Dict, List, Tuple, Any


class ConflictEngine:
    """옵션 간 상충도를 계산하는 엔진"""

    def __init__(self, card_weights: Dict[str, float]):
        """
        Args:
            card_weights: 각 카드(기준)의 중요도 가중치
                예: {'가격': 0.8, '거리': 0.6, '맛': 0.9}
        """
        self.card_weights = card_weights

    def calculate_conflict(
        self,
        option_a: Dict[str, Any],
        option_b: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        두 옵션 간의 상충도 계산

        상충도 = Σ(카드 가중치 × 정규화된 속성 차이)

        Args:
            option_a: 옵션 A의 속성들
            option_b: 옵션 B의 속성들

        Returns:
            (상충도 0~1, 상충 이유)
        """
        conflicts = []
        total_conflict = 0.0
        total_weight = 0.0

        for card_name, weight in self.card_weights.items():
            if card_name not in option_a or card_name not in option_b:
                continue

            val_a = option_a[card_name]
            val_b = option_b[card_name]

            # 정규화된 차이 계산
            diff = self._normalize_difference(val_a, val_b, card_name)

            weighted_diff = weight * diff
            total_conflict += weighted_diff
            total_weight += weight

            if diff > 0.5:  # 큰 차이가 있는 경우
                conflicts.append(f"{card_name} 차이 큼")

        # 0~1 범위로 정규화
        conflict_rate = total_conflict / total_weight if total_weight > 0 else 0
        reason = ", ".join(conflicts) if conflicts else "차이 미미"

        return conflict_rate, reason

    def _normalize_difference(
        self,
        val_a: Any,
        val_b: Any,
        card_name: str
    ) -> float:
        """
        두 값의 차이를 0~1로 정규화
        """
        # 숫자형 데이터
        if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
            # 상대적 차이 계산
            max_val = max(abs(val_a), abs(val_b), 1)  # 0으로 나누기 방지
            diff = abs(val_a - val_b) / max_val
            return min(diff, 1.0)

        # 문자열/카테고리형 데이터
        if isinstance(val_a, str) and isinstance(val_b, str):
            return 0.0 if val_a == val_b else 1.0

        # 리스트형 (태그 등)
        if isinstance(val_a, list) and isinstance(val_b, list):
            set_a = set(val_a)
            set_b = set(val_b)
            # Jaccard 거리
            intersection = len(set_a & set_b)
            union = len(set_a | set_b)
            return 1.0 - (intersection / union if union > 0 else 0)

        return 0.0

    def rank_options(
        self,
        options: List[Dict[str, Any]],
        preferences: Dict[str, Any]
    ) -> List[Tuple[Dict, float]]:
        """
        사용자 선호도에 따라 옵션들을 순위화

        Args:
            options: 선택 가능한 옵션들
            preferences: 사용자의 선호 기준

        Returns:
            (옵션, 점수) 리스트 (점수 높은 순)
        """
        scored_options = []

        for option in options:
            score = self._calculate_option_score(option, preferences)
            scored_options.append((option, score))

        # 점수 높은 순으로 정렬
        scored_options.sort(key=lambda x: x[1], reverse=True)

        return scored_options

    def _calculate_option_score(
        self,
        option: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> float:
        """
        옵션의 점수 계산

        점수 = Σ(카드 가중치 × 선호도 매칭도)
        """
        total_score = 0.0
        total_weight = 0.0

        for card_name, weight in self.card_weights.items():
            if card_name not in option or card_name not in preferences:
                continue

            option_val = option[card_name]
            pref_val = preferences[card_name]

            # 선호도와의 유사도 계산
            similarity = self._calculate_similarity(option_val, pref_val, card_name)

            total_score += weight * similarity
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0

    def _calculate_similarity(
        self,
        option_val: Any,
        pref_val: Any,
        card_name: str
    ) -> float:
        """
        옵션 값과 선호 값의 유사도 (0~1)
        """
        # 숫자형: 가까울수록 높은 점수
        if isinstance(option_val, (int, float)) and isinstance(pref_val, (int, float)):
            diff = abs(option_val - pref_val)
            max_val = max(abs(pref_val), abs(option_val), 1)
            return 1.0 - min(diff / max_val, 1.0)

        # 문자열: 일치 여부
        if isinstance(option_val, str) and isinstance(pref_val, str):
            return 1.0 if option_val == pref_val else 0.0

        # 리스트: 교집합 비율
        if isinstance(option_val, list) and isinstance(pref_val, list):
            set_option = set(option_val)
            set_pref = set(pref_val)
            intersection = len(set_option & set_pref)
            union = len(set_option | set_pref)
            return intersection / union if union > 0 else 0

        return 0.5  # 기본값


def analyze_tradeoffs(
    options: List[Dict[str, Any]],
    card_weights: Dict[str, float]
) -> Dict[str, List[Tuple[str, str, float]]]:
    """
    모든 옵션 쌍의 트레이드오프 분석

    Returns:
        차원별 상충 관계 리스트
    """
    engine = ConflictEngine(card_weights)

    tradeoffs = {}

    for i, opt_a in enumerate(options):
        for j, opt_b in enumerate(options):
            if i >= j:
                continue

            conflict_rate, reason = engine.calculate_conflict(opt_a, opt_b)

            pair_name = f"{opt_a.get('name', i)} vs {opt_b.get('name', j)}"

            if conflict_rate not in tradeoffs:
                tradeoffs[conflict_rate] = []

            tradeoffs[conflict_rate].append((
                opt_a.get('name', i),
                opt_b.get('name', j),
                reason
            ))

    return tradeoffs
