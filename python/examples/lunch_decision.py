"""
점심식사 의사결정 시뮬레이션
뇌과학 + 넛지 이론 기반
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conflict_engine import ConflictEngine, analyze_tradeoffs


def main():
    print("🎴 인지 덱 시스템 - 점심식사 의사결정")
    print("=" * 60)
    print()

    # ============================================
    # 1. 활성화된 카드 (덱) 정의
    # ============================================
    print("📋 Step 1: 현재 활성화된 카드 (Miller's Law: 7개 제한)")
    print("-" * 60)

    active_cards = {
        "배고픔": {"value": 80, "weight": 0.9, "category": "생리적"},
        "예산": {"value": 12000, "weight": 0.7, "category": "경제적"},
        "시간": {"value": 30, "weight": 0.8, "category": "제약적"},
        "동행자": {"value": 3, "weight": 0.6, "category": "사회적"},
        "모험성향": {"value": 0.3, "weight": 0.4, "category": "성향"},  # 0: 안정, 1: 모험
        "날씨": {"value": "비", "weight": 0.5, "category": "외부환경"},
        "거리": {"value": 500, "weight": 0.7, "category": "제약적"},
    }

    for card_name, card_data in active_cards.items():
        print(f"  [{card_name:8s}] {str(card_data['value']):10s} "
              f"(가중치: {card_data['weight']:.1f}, {card_data['category']})")

    print()

    # ============================================
    # 2. 트레이드오프 게이지 계산
    # ============================================
    print("📊 Step 2: 덱의 전체 성향 게이지")
    print("-" * 60)

    # 각 카드의 성향값 (예시)
    tradeoff_contributions = {
        "배고픔": {"정적-동적": 0.7, "이성-감성": -0.5},  # 동적, 이성적
        "예산": {"정적-동적": -0.6, "이성-감성": 0.8},   # 정적, 이성적
        "시간": {"정적-동적": 0.5, "이성-감성": 0.6},    # 동적, 이성적
        "동행자": {"정적-동적": -0.3, "이성-감성": -0.7}, # 정적, 감성적
        "모험성향": {"정적-동적": 0.9, "이성-감성": -0.4},
        "날씨": {"정적-동적": -0.5, "이성-감성": 0.3},
        "거리": {"정적-동적": -0.4, "이성-감성": 0.5},
    }

    # 가중 평균 계산
    dimensions = ["정적-동적", "이성-감성"]
    gauges = {}

    for dim in dimensions:
        weighted_sum = 0
        total_weight = 0

        for card_name, card_data in active_cards.items():
            if card_name in tradeoff_contributions:
                weight = card_data["weight"]
                value = tradeoff_contributions[card_name].get(dim, 0)
                weighted_sum += weight * value
                total_weight += weight

        gauges[dim] = weighted_sum / total_weight if total_weight > 0 else 0

    for dim, value in gauges.items():
        bar = create_gauge_bar(value)
        print(f"  {dim:10s} {bar}")

    print()

    # ============================================
    # 3. 선택 가능한 옵션들
    # ============================================
    print("🍽️  Step 3: 선택 가능한 음식점 옵션")
    print("-" * 60)

    restaurants = [
        {
            "name": "A한식",
            "가격": 12000,
            "거리": 500,
            "예상시간": 40,
            "만족도": 8.5,
            "tags": ["건강", "느림", "전통"],
            "날씨대응": "보통",
        },
        {
            "name": "B양식",
            "가격": 15000,
            "거리": 200,
            "예상시간": 25,
            "만족도": 9.0,
            "tags": ["맛", "빠름", "세련"],
            "날씨대응": "좋음",  # 실내 쾌적
        },
        {
            "name": "C분식",
            "가격": 7000,
            "거리": 800,
            "예상시간": 20,
            "만족도": 7.0,
            "tags": ["저렴", "빠름", "간편"],
            "날씨대응": "나쁨",  # 야외 좌석
        },
        {
            "name": "D일식",
            "가격": 18000,
            "거리": 300,
            "예상시간": 35,
            "만족도": 8.8,
            "tags": ["품질", "모험", "고급"],
            "날씨대응": "좋음",
        },
    ]

    for rest in restaurants:
        print(f"  [{rest['name']}] "
              f"가격: {rest['가격']:,}원, "
              f"거리: {rest['거리']}m, "
              f"시간: {rest['예상시간']}분, "
              f"만족도: {rest['만족도']}")
        print(f"      태그: {', '.join(rest['tags'])}")

    print()

    # ============================================
    # 4. 상충도 분석
    # ============================================
    print("⚖️  Step 4: 옵션 간 상충도 분석")
    print("-" * 60)

    card_weights = {k: v["weight"] for k, v in active_cards.items()}

    # 사용자 선호도 (활성 카드 기반)
    preferences = {
        "가격": active_cards["예산"]["value"],
        "거리": active_cards["거리"]["value"],
        "예상시간": active_cards["시간"]["value"],
    }

    engine = ConflictEngine(card_weights)

    # 옵션 쌍의 상충도 계산
    print("  주요 상충 관계:")
    for i, rest_a in enumerate(restaurants):
        for j, rest_b in enumerate(restaurants):
            if i >= j:
                continue

            conflict_rate, reason = engine.calculate_conflict(rest_a, rest_b)

            if conflict_rate > 0.3:  # 상충도가 높은 경우만 출력
                print(f"    {rest_a['name']} vs {rest_b['name']}: "
                      f"상충도 {conflict_rate:.2f} - {reason}")

    print()

    # ============================================
    # 5. 최종 추천
    # ============================================
    print("🎯 Step 5: AI 기반 최종 추천")
    print("-" * 60)

    ranked = engine.rank_options(restaurants, preferences)

    print("  순위:")
    for idx, (rest, score) in enumerate(ranked, 1):
        bar = "█" * int(score * 20)
        print(f"    {idx}. {rest['name']:6s} {score:.3f} {bar}")

    print()

    # 넛지: 이유 설명
    winner = ranked[0][0]
    print(f"  💡 추천: {winner['name']}")
    print(f"     이유:")
    print(f"      - 배고픔(80%) + 시간제약(30분) → 빠른 식사 필요")
    print(f"      - 날씨(비) → 실내 쾌적도 중요")
    print(f"      - 거리({winner['거리']}m) 가까움")
    print(f"      - 만족도 높음({winner['만족도']})")

    print()
    print("=" * 60)


def create_gauge_bar(value: float) -> str:
    """
    -1.0 ~ 1.0 값을 시각적 게이지로 변환
    """
    bars = 10
    position = int((value + 1.0) / 2.0 * bars)
    position = max(0, min(bars, position))

    visual = ""
    for i in range(bars):
        if i == position:
            visual += "█"
        else:
            visual += "░"

    # 레이블 추가
    if value < -0.5:
        label = " << 왼쪽 치우침"
    elif value > 0.5:
        label = " >> 오른쪽 치우침"
    else:
        label = " = 중립"

    return f"{visual} ({value:+.2f}){label}"


if __name__ == "__main__":
    main()
