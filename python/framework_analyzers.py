#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Framework-Specific Analyzers

각 의사결정 프레임워크별 분석 엔진
"""

from typing import List, Dict, Any
import re


class SWOTAnalyzer:
    """SWOT 분석 엔진"""

    def __init__(self, strengths: List[str], weaknesses: List[str],
                 opportunities: List[str], threats: List[str]):
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.opportunities = opportunities
        self.threats = threats

    def analyze(self) -> Dict[str, Any]:
        """SWOT 분석 실행"""

        # 1. 각 차원 점수 계산
        s_score = len(self.strengths)
        w_score = len(self.weaknesses)
        o_score = len(self.opportunities)
        t_score = len(self.threats)

        # 2. 전략적 위치 결정
        internal_score = s_score - w_score  # 내부: 강점 - 약점
        external_score = o_score - t_score  # 외부: 기회 - 위협

        position = self._determine_position(internal_score, external_score)

        # 3. SO, WO, ST, WT 전략 생성
        strategies = self._generate_strategies()

        # 4. 우선순위 액션 아이템
        action_items = self._generate_action_items()

        return {
            "framework": "SWOT Analysis",
            "scores": {
                "strengths": s_score,
                "weaknesses": w_score,
                "opportunities": o_score,
                "threats": t_score,
                "internal_balance": internal_score,  # + = 강점 우세, - = 약점 우세
                "external_balance": external_score,  # + = 기회 우세, - = 위협 우세
            },
            "position": position,
            "strategies": strategies,
            "action_items": action_items,
            "visualization": {
                "quadrants": [
                    {"name": "Strengths", "items": self.strengths, "count": s_score, "type": "positive"},
                    {"name": "Weaknesses", "items": self.weaknesses, "count": w_score, "type": "negative"},
                    {"name": "Opportunities", "items": self.opportunities, "count": o_score, "type": "positive"},
                    {"name": "Threats", "items": self.threats, "count": t_score, "type": "negative"}
                ]
            }
        }

    def _determine_position(self, internal: int, external: int) -> Dict[str, Any]:
        """전략적 위치 결정"""
        if internal > 0 and external > 0:
            return {
                "zone": "SO (공격적 전략)",
                "description": "강점을 활용하여 기회를 극대화하는 공격적 성장 전략",
                "priority": "강점 기반 기회 활용"
            }
        elif internal < 0 and external > 0:
            return {
                "zone": "WO (개선 전략)",
                "description": "약점을 보완하여 기회를 잡는 전환 전략",
                "priority": "약점 개선 후 기회 활용"
            }
        elif internal > 0 and external < 0:
            return {
                "zone": "ST (다각화 전략)",
                "description": "강점을 활용하여 위협을 회피하는 방어적 전략",
                "priority": "강점으로 위협 대응"
            }
        else:  # internal < 0 and external < 0
            return {
                "zone": "WT (방어/철수 전략)",
                "description": "약점과 위협을 최소화하는 생존 전략",
                "priority": "위험 최소화, 선택과 집중"
            }

    def _generate_strategies(self) -> List[Dict[str, Any]]:
        """SWOT 기반 전략 생성"""
        strategies = []

        # SO 전략 (Strengths-Opportunities)
        if self.strengths and self.opportunities:
            strategies.append({
                "type": "SO (공격 전략)",
                "description": f"강점 '{self.strengths[0]}'을(를) 활용하여 기회 '{self.opportunities[0]}'를 공략",
                "priority": "high" if len(self.strengths) >= 2 and len(self.opportunities) >= 2 else "medium"
            })

        # WO 전략 (Weaknesses-Opportunities)
        if self.weaknesses and self.opportunities:
            strategies.append({
                "type": "WO (개선 전략)",
                "description": f"약점 '{self.weaknesses[0]}'을(를) 보완하여 기회 '{self.opportunities[0]}'를 확보",
                "priority": "medium"
            })

        # ST 전략 (Strengths-Threats)
        if self.strengths and self.threats:
            strategies.append({
                "type": "ST (방어 전략)",
                "description": f"강점 '{self.strengths[0]}'을(를) 활용하여 위협 '{self.threats[0]}'에 대응",
                "priority": "high" if len(self.threats) >= 2 else "medium"
            })

        # WT 전략 (Weaknesses-Threats)
        if self.weaknesses and self.threats:
            strategies.append({
                "type": "WT (회피 전략)",
                "description": f"약점 '{self.weaknesses[0]}'과(와) 위협 '{self.threats[0]}'를 최소화",
                "priority": "low"
            })

        return strategies

    def _generate_action_items(self) -> List[str]:
        """실행 가능한 액션 아이템 생성"""
        actions = []

        # 강점 활용
        if self.strengths:
            actions.append(f"✅ 강점 강화: '{self.strengths[0]}' 역량을 더욱 발전시키기")

        # 약점 보완
        if self.weaknesses:
            actions.append(f"🔧 약점 개선: '{self.weaknesses[0]}' 문제 해결 계획 수립")

        # 기회 포착
        if self.opportunities:
            actions.append(f"🎯 기회 활용: '{self.opportunities[0]}' 기회를 위한 로드맵 작성")

        # 위협 대응
        if self.threats:
            actions.append(f"🛡️ 위협 대응: '{self.threats[0]}' 리스크 완화 계획")

        return actions


class PorterFiveForcesAnalyzer:
    """Porter's 5 Forces 분석 엔진"""

    def __init__(self, forces_data: Dict[str, str]):
        """
        Args:
            forces_data: {
                'newEntrants': '텍스트',
                'suppliers': '텍스트',
                'buyers': '텍스트',
                'substitutes': '텍스트',
                'rivalry': '텍스트'
            }
        """
        self.forces = forces_data

    def analyze(self) -> Dict[str, Any]:
        """Porter's 5 Forces 분석 실행"""

        # 각 Force의 강도 평가 (0-10)
        scores = {}
        for force_key, text in self.forces.items():
            scores[force_key] = self._evaluate_force_intensity(text)

        # 산업 매력도 계산 (Force가 낮을수록 매력적)
        average_threat = sum(scores.values()) / len(scores) if scores else 0
        attractiveness = 10 - average_threat  # 위협 반전

        # 최대 위협 요소
        max_threat = max(scores.items(), key=lambda x: x[1]) if scores else (None, 0)

        # 최소 위협 요소 (진입 장벽)
        min_threat = min(scores.items(), key=lambda x: x[1]) if scores else (None, 0)

        # 전략 추천
        recommendations = self._generate_recommendations(scores)

        return {
            "framework": "Porter's 5 Forces",
            "force_scores": {
                "newEntrants": {
                    "score": scores.get('newEntrants', 0),
                    "label": "신규 진입자의 위협",
                    "level": self._score_to_level(scores.get('newEntrants', 0))
                },
                "suppliers": {
                    "score": scores.get('suppliers', 0),
                    "label": "공급자의 교섭력",
                    "level": self._score_to_level(scores.get('suppliers', 0))
                },
                "buyers": {
                    "score": scores.get('buyers', 0),
                    "label": "구매자의 교섭력",
                    "level": self._score_to_level(scores.get('buyers', 0))
                },
                "substitutes": {
                    "score": scores.get('substitutes', 0),
                    "label": "대체재의 위협",
                    "level": self._score_to_level(scores.get('substitutes', 0))
                },
                "rivalry": {
                    "score": scores.get('rivalry', 0),
                    "label": "산업 내 경쟁 강도",
                    "level": self._score_to_level(scores.get('rivalry', 0))
                }
            },
            "industry_analysis": {
                "average_threat_level": round(average_threat, 1),
                "attractiveness_score": round(attractiveness, 1),
                "attractiveness_rating": self._attractiveness_rating(attractiveness),
                "primary_threat": {
                    "force": self._force_name(max_threat[0]),
                    "score": round(max_threat[1], 1)
                },
                "competitive_advantage": {
                    "force": self._force_name(min_threat[0]),
                    "score": round(min_threat[1], 1)
                }
            },
            "recommendations": recommendations
        }

    def _evaluate_force_intensity(self, text: str) -> float:
        """Force 강도 평가 (텍스트 분석 기반)"""
        if not text or len(text.strip()) == 0:
            return 5.0  # 중립

        text_lower = text.lower()

        # 키워드 기반 점수 계산
        high_threat_keywords = ['높', '많', '강', '심각', '위험', '어려', '취약', 'high', 'strong', 'severe']
        low_threat_keywords = ['낮', '적', '약', '쉬운', '유리', '안전', 'low', 'weak', 'easy']

        high_count = sum(1 for keyword in high_threat_keywords if keyword in text_lower)
        low_count = sum(1 for keyword in low_threat_keywords if keyword in text_lower)

        # 텍스트 길이도 고려 (상세할수록 위협 인지)
        length_factor = min(len(text) / 100, 2.0)  # 최대 2배

        # 점수 계산 (0-10)
        base_score = 5.0
        score = base_score + (high_count - low_count) * 1.5 + length_factor * 0.5

        return max(0, min(10, score))  # 0-10 범위로 제한

    def _score_to_level(self, score: float) -> str:
        """점수를 레벨로 변환"""
        if score >= 7:
            return "높음"
        elif score >= 4:
            return "보통"
        else:
            return "낮음"

    def _force_name(self, force_key: str) -> str:
        """Force 키를 한글명으로 변환"""
        names = {
            'newEntrants': '신규 진입자의 위협',
            'suppliers': '공급자의 교섭력',
            'buyers': '구매자의 교섭력',
            'substitutes': '대체재의 위협',
            'rivalry': '산업 내 경쟁 강도'
        }
        return names.get(force_key, force_key)

    def _attractiveness_rating(self, score: float) -> str:
        """산업 매력도 평가"""
        if score >= 7:
            return "매우 매력적 (진입 추천)"
        elif score >= 5:
            return "보통 (신중한 진입)"
        elif score >= 3:
            return "낮음 (재검토 필요)"
        else:
            return "매우 낮음 (진입 비추천)"

    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """전략 추천"""
        recs = []

        if scores.get('newEntrants', 0) < 4:
            recs.append("✅ 진입 장벽이 낮아 시장 확대 기회 존재")
        elif scores.get('newEntrants', 0) > 7:
            recs.append("⚠️ 신규 진입자 위협 대비: 차별화 전략 강화 필요")

        if scores.get('suppliers', 0) > 7:
            recs.append("🔧 공급자 의존도 낮추기: 다중 소싱 전략 검토")

        if scores.get('buyers', 0) > 7:
            recs.append("🎯 구매자 교섭력 높음: 고객 락인 전략 필요")

        if scores.get('substitutes', 0) > 7:
            recs.append("🛡️ 대체재 위협 대응: 차별화된 가치 제공")

        if scores.get('rivalry', 0) > 7:
            recs.append("⚔️ 경쟁 심화: 틈새시장 또는 블루오션 전략 고려")

        if not recs:
            recs.append("✨ 전반적으로 안정적인 산업 구조")

        return recs


class BCGMatrixAnalyzer:
    """BCG Growth-Share Matrix 분석 엔진"""

    def __init__(self, bcg_data: Dict[str, List[str]]):
        """
        Args:
            bcg_data: {
                'star': ['사업부1', ...],
                'questionMark': ['사업부2', ...],
                'cashCow': ['사업부3', ...],
                'dog': ['사업부4', ...]
            }
        """
        self.star = bcg_data.get('star', [])
        self.question_mark = bcg_data.get('questionMark', [])
        self.cash_cow = bcg_data.get('cashCow', [])
        self.dog = bcg_data.get('dog', [])

    def analyze(self) -> Dict[str, Any]:
        """BCG Matrix 분석 실행"""

        # 포트폴리오 균형 분석
        total = len(self.star) + len(self.question_mark) + len(self.cash_cow) + len(self.dog)

        if total == 0:
            return {
                "framework": "BCG Matrix",
                "error": "No business units provided"
            }

        distribution = {
            "star": len(self.star) / total * 100,
            "question_mark": len(self.question_mark) / total * 100,
            "cash_cow": len(self.cash_cow) / total * 100,
            "dog": len(self.dog) / total * 100
        }

        # 포트폴리오 건전성 평가
        health = self._evaluate_portfolio_health(distribution)

        # 자원 배분 전략
        allocation = self._recommend_allocation()

        # 액션 플랜
        actions = self._generate_actions()

        return {
            "framework": "BCG Matrix",
            "portfolio_distribution": {
                "star": {
                    "count": len(self.star),
                    "percentage": round(distribution['star'], 1),
                    "items": self.star
                },
                "question_mark": {
                    "count": len(self.question_mark),
                    "percentage": round(distribution['question_mark'], 1),
                    "items": self.question_mark
                },
                "cash_cow": {
                    "count": len(self.cash_cow),
                    "percentage": round(distribution['cash_cow'], 1),
                    "items": self.cash_cow
                },
                "dog": {
                    "count": len(self.dog),
                    "percentage": round(distribution['dog'], 1),
                    "items": self.dog
                }
            },
            "portfolio_health": health,
            "resource_allocation": allocation,
            "action_plan": actions
        }

    def _evaluate_portfolio_health(self, dist: Dict[str, float]) -> Dict[str, Any]:
        """포트폴리오 건전성 평가"""

        # 이상적인 분포: Star 20-30%, Question Mark 20-30%, Cash Cow 30-40%, Dog 10-20%
        score = 0
        issues = []

        # Star 비중
        if 20 <= dist['star'] <= 30:
            score += 25
        elif dist['star'] < 10:
            issues.append("Star 사업이 부족 (미래 성장 동력 부족)")
        elif dist['star'] > 40:
            issues.append("Star 사업 과다 (자금 소모 위험)")

        # Cash Cow 비중
        if 30 <= dist['cash_cow'] <= 40:
            score += 30
        elif dist['cash_cow'] < 20:
            issues.append("Cash Cow 부족 (현금 창출 능력 부족)")

        # Question Mark 관리
        if dist['question_mark'] <= 30:
            score += 20
        else:
            issues.append("Question Mark 과다 (의사결정 필요)")

        # Dog 최소화
        if dist['dog'] <= 20:
            score += 25
        else:
            issues.append("Dog 사업 과다 (구조조정 필요)")

        if score >= 80:
            rating = "매우 건강"
        elif score >= 60:
            rating = "건강"
        elif score >= 40:
            rating = "보통"
        else:
            rating = "개선 필요"

        return {
            "score": score,
            "rating": rating,
            "issues": issues if issues else ["포트폴리오 균형 양호"]
        }

    def _recommend_allocation(self) -> List[Dict[str, str]]:
        """자원 배분 추천"""
        recommendations = []

        if self.star:
            recommendations.append({
                "quadrant": "Star",
                "strategy": "적극 투자",
                "allocation": "높음",
                "goal": "시장 점유율 유지 및 확대"
            })

        if self.cash_cow:
            recommendations.append({
                "quadrant": "Cash Cow",
                "strategy": "수확 (Harvest)",
                "allocation": "유지",
                "goal": "현금 흐름 극대화, 다른 사업 지원"
            })

        if self.question_mark:
            recommendations.append({
                "quadrant": "Question Mark",
                "strategy": "선택적 투자",
                "allocation": "중간",
                "goal": "Star로 전환 또는 철수 결정"
            })

        if self.dog:
            recommendations.append({
                "quadrant": "Dog",
                "strategy": "철수 또는 최소 투자",
                "allocation": "최소",
                "goal": "구조조정 또는 매각 검토"
            })

        return recommendations

    def _generate_actions(self) -> List[str]:
        """구체적 액션 플랜"""
        actions = []

        if self.star:
            actions.append(f"🌟 Star '{self.star[0]}': 마케팅 예산 확대 및 R&D 투자")

        if self.cash_cow:
            actions.append(f"💰 Cash Cow '{self.cash_cow[0]}': 효율성 개선으로 수익성 극대화")

        if self.question_mark:
            actions.append(f"❓ Question Mark '{self.question_mark[0]}': 3개월 내 성과 평가 후 Go/No-Go 결정")

        if self.dog:
            actions.append(f"🐕 Dog '{self.dog[0]}': 구조조정 또는 사업 매각 검토")

        return actions


def analyze_framework(framework_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    프레임워크별 분석 실행

    Args:
        framework_id: 'swot', 'porter_5_forces', 'bcg_matrix', etc.
        data: 프레임워크별 입력 데이터

    Returns:
        분석 결과
    """

    if framework_id == 'swot':
        analyzer = SWOTAnalyzer(
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', []),
            opportunities=data.get('opportunities', []),
            threats=data.get('threats', [])
        )
        return analyzer.analyze()

    elif framework_id == 'porter_5_forces':
        analyzer = PorterFiveForcesAnalyzer(
            forces_data=data.get('forces', {})
        )
        return analyzer.analyze()

    elif framework_id == 'bcg_matrix':
        analyzer = BCGMatrixAnalyzer(
            bcg_data=data
        )
        return analyzer.analyze()

    elif framework_id in ['ice_score', 'rice_score']:
        # ICE/RICE는 프론트엔드에서 이미 계산
        return {
            "framework": "ICE Score" if framework_id == 'ice_score' else "RICE Score",
            "ideas": data.get('ideas', []),
            "note": "점수는 프론트엔드에서 계산됨"
        }

    else:
        return {
            "error": f"Unknown framework: {framework_id}"
        }


if __name__ == "__main__":
    # 테스트 1: SWOT 분석
    print("=" * 70)
    print("Test 1: SWOT Analysis")
    print("=" * 70)

    swot_result = analyze_framework('swot', {
        'strengths': ['강력한 브랜드', '우수한 기술력', '충성 고객층'],
        'weaknesses': ['높은 가격', '제한적 유통망'],
        'opportunities': ['시장 확대', '신기술 트렌드', '규제 완화'],
        'threats': ['강력한 경쟁사', '경기 침체']
    })

    print(f"\n위치: {swot_result['position']['zone']}")
    print(f"설명: {swot_result['position']['description']}")
    print(f"\n전략:")
    for strategy in swot_result['strategies']:
        print(f"  - [{strategy['type']}] {strategy['description']}")

    print(f"\n액션 아이템:")
    for action in swot_result['action_items']:
        print(f"  {action}")

    # 테스트 2: Porter's 5 Forces
    print("\n" + "=" * 70)
    print("Test 2: Porter's 5 Forces")
    print("=" * 70)

    porter_result = analyze_framework('porter_5_forces', {
        'forces': {
            'newEntrants': '진입 장벽이 낮아 신규 업체들이 쉽게 진입 가능',
            'suppliers': '소수의 공급자가 시장을 장악하고 있어 교섭력이 매우 높음',
            'buyers': '구매자들이 가격에 민감하고 전환 비용이 낮음',
            'substitutes': '대체재가 많지 않아 위협이 낮음',
            'rivalry': '수많은 경쟁사들이 가격 경쟁 중'
        }
    })

    print(f"\n산업 매력도: {porter_result['industry_analysis']['attractiveness_score']}/10")
    print(f"평가: {porter_result['industry_analysis']['attractiveness_rating']}")
    print(f"\n주요 위협: {porter_result['industry_analysis']['primary_threat']['force']}")
    print(f"\n추천 전략:")
    for rec in porter_result['recommendations']:
        print(f"  {rec}")

    # 테스트 3: BCG Matrix
    print("\n" + "=" * 70)
    print("Test 3: BCG Matrix")
    print("=" * 70)

    bcg_result = analyze_framework('bcg_matrix', {
        'star': ['신제품 A', '성장 서비스 B'],
        'questionMark': ['실험 프로젝트 C'],
        'cashCow': ['주력 제품 D', '안정 서비스 E', '레거시 F'],
        'dog': ['구형 제품 G']
    })

    print(f"\n포트폴리오 건전성: {bcg_result['portfolio_health']['score']}/100")
    print(f"평가: {bcg_result['portfolio_health']['rating']}")
    print(f"\n이슈:")
    for issue in bcg_result['portfolio_health']['issues']:
        print(f"  - {issue}")

    print(f"\n액션 플랜:")
    for action in bcg_result['action_plan']:
        print(f"  {action}")
