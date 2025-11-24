#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHP (Analytic Hierarchy Process) Engine

다차원 복잡도를 계층적으로 해소하는 의사결정 알고리즘

핵심 기능:
1. 계층적 분해: 목표 → 기준 → 대안
2. 쌍대비교: 2개씩 비교하여 복잡도 감소
3. 일관성 검증: CR (Consistency Ratio) 계산
4. 가중치 계산: 고유벡터 방법
"""

import numpy as np
from typing import List, Dict, Tuple, Any
import math


class AHPMatrix:
    """쌍대비교 매트릭스"""

    # Saaty 9점 척도
    SAATY_SCALE = {
        1: "동등하게 중요",
        3: "약간 더 중요",
        5: "확실히 더 중요",
        7: "매우 확실히 더 중요",
        9: "절대적으로 더 중요",
        2: "1과 3 사이",
        4: "3과 5 사이",
        6: "5와 7 사이",
        8: "7과 9 사이",
    }

    # 일관성 지수 (Random Index)
    RI = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
    }

    def __init__(self, items: List[str]):
        """
        Args:
            items: 비교할 항목들 (예: ['맛', '가격', '시간'])
        """
        self.items = items
        self.n = len(items)
        # 단위 행렬로 초기화 (대각선은 1, 자기 자신과의 비교)
        self.matrix = np.ones((self.n, self.n))

    def set_comparison(self, item1: str, item2: str, value: float):
        """
        쌍대비교 값 설정

        Args:
            item1: 첫 번째 항목
            item2: 두 번째 항목
            value: item1이 item2에 비해 얼마나 중요한지 (1-9)
                   예: 3 = item1이 item2보다 3배 중요
        """
        i = self.items.index(item1)
        j = self.items.index(item2)

        self.matrix[i][j] = value
        self.matrix[j][i] = 1.0 / value  # 역수 관계

    def calculate_weights(self) -> np.ndarray:
        """
        가중치 계산 (고유벡터 방법)

        Returns:
            각 항목의 가중치 배열 (합=1.0)
        """
        # 1. 고유값과 고유벡터 계산
        eigenvalues, eigenvectors = np.linalg.eig(self.matrix)

        # 2. 최대 고유값에 해당하는 고유벡터 찾기
        max_eigenvalue_index = np.argmax(eigenvalues.real)
        principal_eigenvector = eigenvectors[:, max_eigenvalue_index].real

        # 3. 정규화 (합이 1이 되도록)
        weights = principal_eigenvector / principal_eigenvector.sum()

        return weights

    def calculate_consistency_ratio(self) -> Tuple[float, float, str]:
        """
        일관성 비율 계산

        Returns:
            (CR, CI, 판정) 튜플
            - CR < 0.1: 일관성 있음
            - CR >= 0.1: 일관성 없음 (재검토 필요)
        """
        # 1. 최대 고유값 계산
        eigenvalues = np.linalg.eigvals(self.matrix)
        lambda_max = np.max(eigenvalues.real)

        # 2. CI (Consistency Index) 계산
        CI = (lambda_max - self.n) / (self.n - 1) if self.n > 1 else 0

        # 3. CR (Consistency Ratio) 계산
        RI = self.RI.get(self.n, 1.49)
        CR = CI / RI if RI > 0 else 0

        # 4. 판정
        if CR < 0.1:
            judgement = "✅ 일관성 있음"
        elif CR < 0.2:
            judgement = "⚠️ 일관성 보통 (재검토 권장)"
        else:
            judgement = "❌ 일관성 없음 (재평가 필요)"

        return CR, CI, judgement

    def get_comparison_summary(self) -> List[Dict]:
        """쌍대비교 요약"""
        comparisons = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                value = self.matrix[i][j]
                if value >= 1:
                    comparisons.append({
                        "item1": self.items[i],
                        "item2": self.items[j],
                        "ratio": round(value, 2),
                        "description": f"{self.items[i]}가 {self.items[j]}보다 {value:.1f}배 중요"
                    })
                else:
                    comparisons.append({
                        "item1": self.items[j],
                        "item2": self.items[i],
                        "ratio": round(1/value, 2),
                        "description": f"{self.items[j]}가 {self.items[i]}보다 {1/value:.1f}배 중요"
                    })
        return comparisons


class AHPEngine:
    """AHP 의사결정 엔진"""

    def __init__(self, goal: str, criteria: List[str], alternatives: List[str]):
        """
        Args:
            goal: 의사결정 목표 (예: "최적의 점심 메뉴 선택")
            criteria: 평가 기준들 (예: ['맛', '가격', '시간'])
            alternatives: 대안들 (예: ['이탈리안', '한식', '중식'])
        """
        self.goal = goal
        self.criteria = criteria
        self.alternatives = alternatives

        # Step 1: 기준 간 쌍대비교 매트릭스
        self.criteria_matrix = AHPMatrix(criteria)

        # Step 2: 각 기준별로 대안 간 쌍대비교 매트릭스
        self.alternative_matrices = {
            criterion: AHPMatrix(alternatives)
            for criterion in criteria
        }

        # 계산 결과 저장
        self.criteria_weights = None
        self.alternative_scores = {}
        self.final_scores = None

    def set_criteria_comparison(self, criterion1: str, criterion2: str, value: float):
        """기준 간 중요도 비교"""
        self.criteria_matrix.set_comparison(criterion1, criterion2, value)

    def set_alternative_comparison(self, criterion: str, alt1: str, alt2: str, value: float):
        """특정 기준 하에서 대안 간 비교"""
        if criterion in self.alternative_matrices:
            self.alternative_matrices[criterion].set_comparison(alt1, alt2, value)

    def calculate(self) -> Dict[str, Any]:
        """AHP 계산 실행"""

        # 1. 기준 가중치 계산
        self.criteria_weights = self.criteria_matrix.calculate_weights()
        cr_criteria, ci_criteria, judgement_criteria = self.criteria_matrix.calculate_consistency_ratio()

        # 2. 각 기준별 대안 점수 계산
        for criterion in self.criteria:
            scores = self.alternative_matrices[criterion].calculate_weights()
            self.alternative_scores[criterion] = scores

        # 3. 최종 점수 계산 (가중합)
        self.final_scores = np.zeros(len(self.alternatives))
        for i, criterion in enumerate(self.criteria):
            criterion_weight = self.criteria_weights[i]
            alt_scores = self.alternative_scores[criterion]
            self.final_scores += criterion_weight * alt_scores

        # 4. 순위 결정
        rankings = sorted(
            enumerate(self.alternatives),
            key=lambda x: self.final_scores[x[0]],
            reverse=True
        )

        # 5. 차원 복잡도 해소 단계 시각화 데이터
        complexity_reduction = self._calculate_complexity_reduction()

        return {
            "goal": self.goal,
            "criteria": self.criteria,
            "alternatives": self.alternatives,

            # 기준 가중치
            "criteria_weights": {
                criterion: {
                    "weight": round(float(weight) * 100, 1),
                    "rank": i + 1
                }
                for i, (criterion, weight) in enumerate(
                    sorted(zip(self.criteria, self.criteria_weights),
                           key=lambda x: x[1], reverse=True)
                )
            },
            "criteria_consistency": {
                "CR": round(cr_criteria, 3),
                "CI": round(ci_criteria, 3),
                "judgement": judgement_criteria
            },

            # 대안별 점수 (기준별)
            "alternative_scores_by_criterion": {
                criterion: {
                    alt: round(float(score) * 100, 1)
                    for alt, score in zip(self.alternatives, scores)
                }
                for criterion, scores in self.alternative_scores.items()
            },

            # 최종 점수 및 순위
            "final_scores": {
                alt: round(float(score) * 100, 1)
                for alt, score in zip(self.alternatives, self.final_scores)
            },
            "rankings": [
                {
                    "rank": i + 1,
                    "alternative": alt,
                    "score": round(float(self.final_scores[idx]) * 100, 1),
                    "score_breakdown": {
                        criterion: round(
                            float(self.criteria_weights[j]) *
                            float(self.alternative_scores[criterion][idx]) * 100,
                            1
                        )
                        for j, criterion in enumerate(self.criteria)
                    }
                }
                for i, (idx, alt) in enumerate(rankings)
            ],

            # 차원 복잡도 해소 과정
            "complexity_reduction": complexity_reduction,

            # 추천
            "recommendation": {
                "best_alternative": rankings[0][1],
                "confidence": round(float(self.final_scores[rankings[0][0]]) * 100, 1),
                "reason": self._generate_recommendation_reason(rankings[0][0])
            }
        }

    def _calculate_complexity_reduction(self) -> Dict[str, Any]:
        """
        차원 복잡도가 단계별로 어떻게 해소되는지 계산

        복잡도 = 비교 횟수로 측정
        """
        n_criteria = len(self.criteria)
        n_alternatives = len(self.alternatives)

        # 원시 복잡도: 모든 대안을 모든 기준에서 한 번에 비교
        # = n_alternatives^n_criteria (조합 폭발)
        raw_complexity = n_alternatives ** n_criteria

        # AHP 복잡도: 계층적 쌍대비교
        # = C(n_criteria, 2) + n_criteria * C(n_alternatives, 2)
        criteria_comparisons = n_criteria * (n_criteria - 1) // 2
        alternative_comparisons = n_criteria * (n_alternatives * (n_alternatives - 1) // 2)
        ahp_complexity = criteria_comparisons + alternative_comparisons

        reduction_ratio = ahp_complexity / raw_complexity if raw_complexity > 0 else 0

        return {
            "raw_complexity": raw_complexity,
            "ahp_complexity": ahp_complexity,
            "reduction_ratio": round(reduction_ratio, 4),
            "reduction_percentage": round((1 - reduction_ratio) * 100, 1),

            "steps": [
                {
                    "step": 1,
                    "name": "문제 계층화",
                    "description": f"{n_criteria}개 기준, {n_alternatives}개 대안으로 분해",
                    "complexity_before": raw_complexity,
                    "complexity_after": n_criteria + n_alternatives,
                    "reduction": round((1 - (n_criteria + n_alternatives) / raw_complexity) * 100, 1)
                },
                {
                    "step": 2,
                    "name": "기준 가중치 계산",
                    "description": f"{n_criteria}개 기준을 쌍대비교 ({criteria_comparisons}회)",
                    "complexity_before": n_criteria,
                    "complexity_after": 1,  # 가중치 벡터 1개
                    "reduction": round((1 - 1 / n_criteria) * 100, 1) if n_criteria > 0 else 0
                },
                {
                    "step": 3,
                    "name": "대안 평가",
                    "description": f"각 기준별 {n_alternatives}개 대안 비교 (총 {alternative_comparisons}회)",
                    "complexity_before": n_alternatives * n_criteria,
                    "complexity_after": n_alternatives,  # 점수 벡터
                    "reduction": round((1 - n_alternatives / (n_alternatives * n_criteria)) * 100, 1)
                },
                {
                    "step": 4,
                    "name": "최종 통합",
                    "description": "가중치와 점수를 곱하여 최종 순위 도출",
                    "complexity_before": n_alternatives,
                    "complexity_after": 1,  # 최종 추천 1개
                    "reduction": round((1 - 1 / n_alternatives) * 100, 1) if n_alternatives > 0 else 0
                }
            ]
        }

    def _generate_recommendation_reason(self, best_idx: int) -> str:
        """추천 이유 생성"""
        reasons = []

        # 각 기준에서 강점 찾기
        for i, criterion in enumerate(self.criteria):
            score = self.alternative_scores[criterion][best_idx]
            weight = self.criteria_weights[i]
            contribution = score * weight

            if score > 0.4:  # 이 기준에서 강점이 있음
                reasons.append(
                    f"{criterion}({round(weight*100, 1)}% 가중치)에서 {round(score*100, 1)}점으로 우수"
                )

        if not reasons:
            return "종합 점수가 가장 높습니다."

        return " / ".join(reasons[:3])  # 상위 3개 이유


def analyze_with_ahp(
    goal: str,
    criteria: List[str],
    alternatives: List[str],
    criteria_comparisons: Dict[Tuple[str, str], float],
    alternative_comparisons: Dict[str, Dict[Tuple[str, str], float]]
) -> Dict[str, Any]:
    """
    AHP 분석 실행 (편의 함수)

    Args:
        goal: 의사결정 목표
        criteria: 평가 기준 리스트
        alternatives: 대안 리스트
        criteria_comparisons: 기준 간 비교 {(기준1, 기준2): 중요도}
        alternative_comparisons: 대안 간 비교 {기준: {(대안1, 대안2): 선호도}}

    Example:
        result = analyze_with_ahp(
            goal="점심 메뉴 선택",
            criteria=["맛", "가격", "시간"],
            alternatives=["이탈리안", "한식", "중식"],
            criteria_comparisons={
                ("맛", "가격"): 3,  # 맛이 가격보다 3배 중요
                ("맛", "시간"): 2,  # 맛이 시간보다 2배 중요
                ("가격", "시간"): 1,  # 가격과 시간은 동등
            },
            alternative_comparisons={
                "맛": {
                    ("이탈리안", "한식"): 2,
                    ("이탈리안", "중식"): 3,
                    ("한식", "중식"): 2,
                },
                "가격": {
                    ("한식", "이탈리안"): 3,
                    ("한식", "중식"): 2,
                    ("중식", "이탈리안"): 2,
                },
                "시간": {
                    ("중식", "한식"): 2,
                    ("중식", "이탈리안"): 3,
                    ("한식", "이탈리안"): 2,
                }
            }
        )
    """

    # 1. AHP 엔진 초기화
    ahp = AHPEngine(goal, criteria, alternatives)

    # 2. 기준 간 비교 설정
    for (c1, c2), value in criteria_comparisons.items():
        ahp.set_criteria_comparison(c1, c2, value)

    # 3. 대안 간 비교 설정 (각 기준별)
    for criterion, comparisons in alternative_comparisons.items():
        for (a1, a2), value in comparisons.items():
            ahp.set_alternative_comparison(criterion, a1, a2, value)

    # 4. 계산 실행
    return ahp.calculate()


if __name__ == "__main__":
    # 테스트: 점심 메뉴 선택
    print("=" * 70)
    print("AHP 테스트: 점심 메뉴 선택")
    print("=" * 70)

    result = analyze_with_ahp(
        goal="팀 점심 메뉴 선택",
        criteria=["맛", "가격", "시간"],
        alternatives=["이탈리안", "한식", "중식"],
        criteria_comparisons={
            ("맛", "가격"): 3,
            ("맛", "시간"): 2,
            ("가격", "시간"): 1,
        },
        alternative_comparisons={
            "맛": {
                ("이탈리안", "한식"): 2,
                ("이탈리안", "중식"): 3,
                ("한식", "중식"): 2,
            },
            "가격": {
                ("한식", "이탈리안"): 3,
                ("한식", "중식"): 2,
                ("중식", "이탈리안"): 2,
            },
            "시간": {
                ("중식", "한식"): 2,
                ("중식", "이탈리안"): 3,
                ("한식", "이탈리안"): 2,
            }
        }
    )

    print(f"\n🎯 목표: {result['goal']}")
    print(f"\n📊 기준 가중치:")
    for criterion, data in result['criteria_weights'].items():
        print(f"  {criterion}: {data['weight']}% (순위 {data['rank']})")

    print(f"\n✅ 일관성 검증: {result['criteria_consistency']['judgement']}")
    print(f"   CR = {result['criteria_consistency']['CR']:.3f} (< 0.1이면 일관성 있음)")

    print(f"\n🥇 추천: {result['recommendation']['best_alternative']}")
    print(f"   신뢰도: {result['recommendation']['confidence']}%")
    print(f"   이유: {result['recommendation']['reason']}")

    print(f"\n📈 복잡도 감소:")
    cr = result['complexity_reduction']
    print(f"   원시 복잡도: {cr['raw_complexity']}")
    print(f"   AHP 복잡도: {cr['ahp_complexity']}")
    print(f"   감소율: {cr['reduction_percentage']}%")

    print(f"\n🔍 단계별 복잡도 해소:")
    for step in cr['steps']:
        print(f"   Step {step['step']}: {step['name']}")
        print(f"      {step['description']}")
        print(f"      {step['complexity_before']} → {step['complexity_after']} (감소율 {step['reduction']}%)")

    print(f"\n🏆 최종 순위:")
    for ranking in result['rankings']:
        print(f"   {ranking['rank']}위: {ranking['alternative']} ({ranking['score']}점)")
        breakdown = ", ".join([f"{k}:{v}" for k, v in ranking['score_breakdown'].items()])
        print(f"      상세: {breakdown}")
