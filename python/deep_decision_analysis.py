#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Decision Analysis - 심층 의사결정 분석 모형

시나리오 분석, 리스크 분석, 민감도 분석을 통한
다층 의사결정 지원
"""

import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ScenarioType(Enum):
    """시나리오 유형"""
    BEST = "best"        # 최선
    BASE = "base"        # 기본
    WORST = "worst"      # 최악


class RiskLevel(Enum):
    """리스크 레벨"""
    CRITICAL = "critical"  # 치명적
    HIGH = "high"          # 높음
    MEDIUM = "medium"      # 중간
    LOW = "low"            # 낮음


@dataclass
class Scenario:
    """시나리오"""
    type: ScenarioType
    name: str
    description: str
    probability: float  # 발생 확률 (0.0 ~ 1.0)
    assumptions: List[str] = field(default_factory=list)
    outcomes: Dict[str, float] = field(default_factory=dict)  # {차원: 예상값}


@dataclass
class Risk:
    """리스크"""
    name: str
    description: str
    probability: float  # 발생 확률 (0.0 ~ 1.0)
    impact: float       # 영향도 (0.0 ~ 1.0)
    level: RiskLevel
    mitigation: str = ""  # 완화 전략

    @property
    def risk_score(self) -> float:
        """리스크 점수 = 확률 x 영향도"""
        return self.probability * self.impact


@dataclass
class SensitivityVariable:
    """민감도 분석 변수"""
    name: str
    base_value: float
    min_value: float
    max_value: float
    impact_on_result: float  # 결과에 미치는 영향도 (-1.0 ~ 1.0)


class ScenarioAnalyzer:
    """시나리오 분석 엔진"""

    @staticmethod
    def generate_scenarios(option: str,
                          base_data: Dict[str, float],
                          variance: float = 0.3) -> List[Scenario]:
        """3가지 시나리오 생성 (최선/기본/최악)"""
        scenarios = []

        # 기본 시나리오 (Base Case)
        base_scenario = Scenario(
            type=ScenarioType.BASE,
            name=f"{option} - 기본 시나리오",
            description="현재 추세가 지속되는 경우",
            probability=0.5,
            assumptions=[
                "시장 상황 유지",
                "경쟁 구도 변화 없음",
                "내부 역량 현재 수준 유지"
            ],
            outcomes=base_data.copy()
        )
        scenarios.append(base_scenario)

        # 최선 시나리오 (Best Case)
        best_outcomes = {}
        for key, value in base_data.items():
            # 긍정적 차원은 +variance, 부정적 차원은 -variance
            if key in ["비용", "시간", "위험", "리스크"]:
                best_outcomes[key] = value * (1 - variance)
            else:
                best_outcomes[key] = value * (1 + variance)

        best_scenario = Scenario(
            type=ScenarioType.BEST,
            name=f"{option} - 최선 시나리오",
            description="모든 조건이 유리하게 작용하는 경우",
            probability=0.2,
            assumptions=[
                "시장이 예상보다 빠르게 성장",
                "경쟁사 대응 지연",
                "팀 생산성 향상"
            ],
            outcomes=best_outcomes
        )
        scenarios.append(best_scenario)

        # 최악 시나리오 (Worst Case)
        worst_outcomes = {}
        for key, value in base_data.items():
            # 긍정적 차원은 -variance, 부정적 차원은 +variance
            if key in ["비용", "시간", "위험", "리스크"]:
                worst_outcomes[key] = value * (1 + variance)
            else:
                worst_outcomes[key] = value * (1 - variance)

        worst_scenario = Scenario(
            type=ScenarioType.WORST,
            name=f"{option} - 최악 시나리오",
            description="불리한 조건들이 겹치는 경우",
            probability=0.3,
            assumptions=[
                "시장 침체 또는 경쟁 심화",
                "예상치 못한 기술적 문제",
                "핵심 인력 이탈"
            ],
            outcomes=worst_outcomes
        )
        scenarios.append(worst_scenario)

        return scenarios

    @staticmethod
    def calculate_expected_value(scenarios: List[Scenario],
                                 dimension: str) -> Dict[str, Any]:
        """기대값 계산 (확률 가중 평균)"""
        ev = 0.0
        total_prob = sum(s.probability for s in scenarios)

        for scenario in scenarios:
            if dimension in scenario.outcomes:
                ev += scenario.outcomes[dimension] * (scenario.probability / total_prob)

        # 각 시나리오별 값
        scenario_values = {
            s.type.value: s.outcomes.get(dimension, 0.0)
            for s in scenarios
        }

        return {
            "expected_value": ev,
            "scenarios": scenario_values,
            "range": {
                "min": min(s.outcomes.get(dimension, 0) for s in scenarios),
                "max": max(s.outcomes.get(dimension, 0) for s in scenarios),
            }
        }


class RiskAnalyzer:
    """리스크 분석 엔진"""

    # 일반적인 비즈니스 리스크 템플릿
    COMMON_RISKS = {
        "strategy": [
            {
                "name": "시장 리스크",
                "description": "시장 상황 악화 또는 수요 감소",
                "base_probability": 0.3,
                "base_impact": 0.7,
            },
            {
                "name": "경쟁 리스크",
                "description": "경쟁사의 공격적 대응",
                "base_probability": 0.4,
                "base_impact": 0.6,
            },
            {
                "name": "실행 리스크",
                "description": "전략 실행 과정의 차질",
                "base_probability": 0.5,
                "base_impact": 0.5,
            },
        ],
        "product": [
            {
                "name": "기술 리스크",
                "description": "기술적 구현 실패 또는 지연",
                "base_probability": 0.4,
                "base_impact": 0.8,
            },
            {
                "name": "사용자 반응 리스크",
                "description": "사용자 수용도 낮음",
                "base_probability": 0.3,
                "base_impact": 0.7,
            },
        ],
        "project": [
            {
                "name": "일정 지연 리스크",
                "description": "프로젝트 일정 지연",
                "base_probability": 0.6,
                "base_impact": 0.5,
            },
            {
                "name": "리소스 부족 리스크",
                "description": "인력/예산 부족",
                "base_probability": 0.4,
                "base_impact": 0.6,
            },
        ],
    }

    @staticmethod
    def identify_risks(category: str = "strategy",
                      custom_risks: List[Dict] = None) -> List[Risk]:
        """리스크 식별"""
        risks = []

        # 기본 리스크
        base_risks = RiskAnalyzer.COMMON_RISKS.get(category, [])
        for risk_template in base_risks:
            risk = RiskAnalyzer._create_risk_from_template(risk_template)
            risks.append(risk)

        # 커스텀 리스크
        if custom_risks:
            for custom in custom_risks:
                risk = Risk(
                    name=custom.get("name", "Unknown Risk"),
                    description=custom.get("description", ""),
                    probability=custom.get("probability", 0.5),
                    impact=custom.get("impact", 0.5),
                    level=RiskAnalyzer._calculate_risk_level(
                        custom.get("probability", 0.5),
                        custom.get("impact", 0.5)
                    ),
                    mitigation=custom.get("mitigation", "")
                )
                risks.append(risk)

        return risks

    @staticmethod
    def _create_risk_from_template(template: Dict) -> Risk:
        """템플릿에서 리스크 생성"""
        prob = template["base_probability"]
        impact = template["base_impact"]

        return Risk(
            name=template["name"],
            description=template["description"],
            probability=prob,
            impact=impact,
            level=RiskAnalyzer._calculate_risk_level(prob, impact),
            mitigation=RiskAnalyzer._suggest_mitigation(template["name"])
        )

    @staticmethod
    def _calculate_risk_level(probability: float, impact: float) -> RiskLevel:
        """리스크 레벨 계산"""
        score = probability * impact

        if score >= 0.5:
            return RiskLevel.CRITICAL
        elif score >= 0.3:
            return RiskLevel.HIGH
        elif score >= 0.15:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    @staticmethod
    def _suggest_mitigation(risk_name: str) -> str:
        """리스크 완화 전략 제안"""
        mitigations = {
            "시장 리스크": "다양한 시장 세그먼트 공략, 사전 시장 조사 강화",
            "경쟁 리스크": "차별화 전략 강화, 빠른 시장 진입",
            "실행 리스크": "단계별 검증 포인트 설정, 애자일 접근법 적용",
            "기술 리스크": "기술 검증 단계 추가, 대안 기술 준비",
            "사용자 반응 리스크": "MVP 테스트, 얼리어답터 피드백 수집",
            "일정 지연 리스크": "버퍼 시간 확보, 우선순위 명확화",
            "리소스 부족 리스크": "사전 리소스 확보, 외부 파트너 활용",
        }
        return mitigations.get(risk_name, "지속적 모니터링 및 대응 계획 수립")

    @staticmethod
    def calculate_risk_adjusted_value(base_value: float,
                                     risks: List[Risk]) -> Dict[str, Any]:
        """리스크 조정 가치 계산"""
        total_risk_impact = sum(r.risk_score for r in risks)
        risk_discount_factor = 1.0 - min(total_risk_impact, 0.8)

        adjusted_value = base_value * risk_discount_factor

        return {
            "base_value": base_value,
            "risk_adjusted_value": adjusted_value,
            "total_risk_score": total_risk_impact,
            "discount_factor": risk_discount_factor,
            "major_risks": sorted(risks, key=lambda r: r.risk_score, reverse=True)[:3]
        }


class SensitivityAnalyzer:
    """민감도 분석 엔진"""

    @staticmethod
    def identify_key_variables(data: Dict[str, float]) -> List[SensitivityVariable]:
        """주요 변수 식별"""
        variables = []

        for name, value in data.items():
            # 변동 범위 설정 (±30%)
            var_range = abs(value * 0.3) if value != 0 else 1.0

            # 결과에 미치는 영향도 (임시로 랜덤, 실제로는 회귀분석 등 사용)
            impact = random.uniform(0.3, 0.9)

            variable = SensitivityVariable(
                name=name,
                base_value=value,
                min_value=value - var_range,
                max_value=value + var_range,
                impact_on_result=impact
            )
            variables.append(variable)

        # 영향도 순으로 정렬
        variables.sort(key=lambda v: abs(v.impact_on_result), reverse=True)

        return variables

    @staticmethod
    def run_sensitivity_analysis(variables: List[SensitivityVariable],
                                 base_result: float) -> Dict[str, Any]:
        """민감도 분석 실행"""
        analysis_results = []

        for var in variables:
            # Min 값일 때 결과
            delta_min = (var.min_value - var.base_value) / var.base_value if var.base_value != 0 else 0
            result_min = base_result * (1 + delta_min * var.impact_on_result)

            # Max 값일 때 결과
            delta_max = (var.max_value - var.base_value) / var.base_value if var.base_value != 0 else 0
            result_max = base_result * (1 + delta_max * var.impact_on_result)

            # 민감도 계수 (변수 1% 변화 시 결과 변화%)
            sensitivity_coef = var.impact_on_result * 100

            analysis_results.append({
                "variable": var.name,
                "base_value": var.base_value,
                "range": {
                    "min": var.min_value,
                    "max": var.max_value
                },
                "result_range": {
                    "min": result_min,
                    "max": result_max
                },
                "sensitivity_coefficient": sensitivity_coef,
                "impact_level": SensitivityAnalyzer._get_impact_level(abs(var.impact_on_result))
            })

        # 가장 민감한 변수 찾기
        top_3_sensitive = sorted(
            analysis_results,
            key=lambda x: abs(x["sensitivity_coefficient"]),
            reverse=True
        )[:3]

        return {
            "base_result": base_result,
            "variables": analysis_results,
            "top_sensitive_variables": top_3_sensitive,
            "recommendation": SensitivityAnalyzer._generate_recommendation(top_3_sensitive)
        }

    @staticmethod
    def _get_impact_level(impact: float) -> str:
        """영향 레벨 분류"""
        if impact >= 0.7:
            return "매우 높음"
        elif impact >= 0.5:
            return "높음"
        elif impact >= 0.3:
            return "중간"
        else:
            return "낮음"

    @staticmethod
    def _generate_recommendation(top_variables: List[Dict]) -> str:
        """추천사항 생성"""
        if not top_variables:
            return "민감한 변수가 없습니다."

        top_var = top_variables[0]
        return f"'{top_var['variable']}' 변수에 가장 민감합니다. 이 변수의 정확한 추정과 관리가 중요합니다."


class DeepDecisionAnalyzer:
    """통합 심층 분석 엔진"""

    def __init__(self, option_name: str, base_data: Dict[str, float], category: str = "strategy"):
        self.option_name = option_name
        self.base_data = base_data
        self.category = category

    def run_full_analysis(self) -> Dict[str, Any]:
        """전체 심층 분석 실행"""

        # 1. 시나리오 분석
        scenarios = ScenarioAnalyzer.generate_scenarios(
            self.option_name,
            self.base_data
        )

        # 차원별 기대값 계산
        scenario_analysis = {}
        for dimension in self.base_data.keys():
            scenario_analysis[dimension] = ScenarioAnalyzer.calculate_expected_value(
                scenarios, dimension
            )

        # 2. 리스크 분석
        risks = RiskAnalyzer.identify_risks(self.category)

        # 대표 값으로 리스크 조정 (첫 번째 차원)
        first_dimension = list(self.base_data.keys())[0]
        base_value = self.base_data[first_dimension]
        risk_analysis = RiskAnalyzer.calculate_risk_adjusted_value(base_value, risks)

        # 3. 민감도 분석
        variables = SensitivityAnalyzer.identify_key_variables(self.base_data)
        sensitivity_analysis = SensitivityAnalyzer.run_sensitivity_analysis(
            variables[:5],  # 상위 5개만
            base_value
        )

        return {
            "option": self.option_name,
            "base_data": self.base_data,
            "scenario_analysis": {
                "scenarios": [
                    {
                        "type": s.type.value,
                        "name": s.name,
                        "description": s.description,
                        "probability": s.probability,
                        "assumptions": s.assumptions,
                        "outcomes": s.outcomes
                    }
                    for s in scenarios
                ],
                "expected_values": scenario_analysis
            },
            "risk_analysis": {
                "identified_risks": [
                    {
                        "name": r.name,
                        "description": r.description,
                        "probability": r.probability,
                        "impact": r.impact,
                        "risk_score": r.risk_score,
                        "level": r.level.value,
                        "mitigation": r.mitigation
                    }
                    for r in risks
                ],
                "risk_adjusted": risk_analysis
            },
            "sensitivity_analysis": sensitivity_analysis,
            "overall_recommendation": self._generate_overall_recommendation(
                scenario_analysis,
                risk_analysis,
                sensitivity_analysis
            )
        }

    def _generate_overall_recommendation(self, scenario_analysis, risk_analysis, sensitivity_analysis) -> str:
        """종합 추천"""
        risk_level = risk_analysis["discount_factor"]

        if risk_level > 0.7:
            risk_msg = "리스크가 낮아 실행 권장"
        elif risk_level > 0.5:
            risk_msg = "중간 수준의 리스크, 완화 전략과 함께 진행"
        else:
            risk_msg = "높은 리스크, 신중한 검토 필요"

        sensitive_var = sensitivity_analysis["top_sensitive_variables"][0]["variable"]

        return f"{risk_msg}. 특히 '{sensitive_var}' 변수 관리가 중요합니다."


if __name__ == "__main__":
    print("=" * 70)
    print("심층 의사결정 분석 테스트")
    print("=" * 70)

    # 테스트 데이터
    test_data = {
        "효과": 85,
        "비용": 500,
        "시간": 3,
        "품질": 90
    }

    analyzer = DeepDecisionAnalyzer("공격적 마케팅", test_data, "strategy")
    result = analyzer.run_full_analysis()

    print(f"\n📊 선택지: {result['option']}")
    print(f"기본 데이터: {result['base_data']}")

    print("\n\n1️⃣ 시나리오 분석")
    print("-" * 70)
    for scenario in result["scenario_analysis"]["scenarios"]:
        print(f"\n  [{scenario['type'].upper()}] {scenario['name']}")
        print(f"    확률: {scenario['probability']*100:.0f}%")
        print(f"    가정: {', '.join(scenario['assumptions'][:2])}")
        print(f"    결과: 효과 {scenario['outcomes']['효과']:.1f}, 비용 {scenario['outcomes']['비용']:.0f}")

    print(f"\n  기대값 (효과): {result['scenario_analysis']['expected_values']['효과']['expected_value']:.1f}")
    print(f"  범위: {result['scenario_analysis']['expected_values']['효과']['range']['min']:.1f} ~ "
          f"{result['scenario_analysis']['expected_values']['효과']['range']['max']:.1f}")

    print("\n\n2️⃣ 리스크 분석")
    print("-" * 70)
    for risk in result["risk_analysis"]["identified_risks"]:
        print(f"\n  ⚠️  {risk['name']} [{risk['level'].upper()}]")
        print(f"    {risk['description']}")
        print(f"    확률: {risk['probability']*100:.0f}%, 영향도: {risk['impact']*100:.0f}%, "
              f"리스크 점수: {risk['risk_score']:.2f}")
        print(f"    완화: {risk['mitigation']}")

    print(f"\n  리스크 조정 가치:")
    print(f"    기본값: {result['risk_analysis']['risk_adjusted']['base_value']:.1f}")
    print(f"    조정값: {result['risk_analysis']['risk_adjusted']['risk_adjusted_value']:.1f}")
    print(f"    할인율: {(1-result['risk_analysis']['risk_adjusted']['discount_factor'])*100:.1f}%")

    print("\n\n3️⃣ 민감도 분석")
    print("-" * 70)
    for var in result["sensitivity_analysis"]["top_sensitive_variables"]:
        print(f"\n  📈 {var['variable']} (민감도: {var['sensitivity_coefficient']:.1f}%)")
        print(f"    기준값: {var['base_value']:.1f}")
        print(f"    변동 범위: {var['range']['min']:.1f} ~ {var['range']['max']:.1f}")
        print(f"    결과 영향: {var['result_range']['min']:.1f} ~ {var['result_range']['max']:.1f}")
        print(f"    영향 수준: {var['impact_level']}")

    print(f"\n\n💡 종합 추천")
    print("-" * 70)
    print(f"  {result['overall_recommendation']}")
