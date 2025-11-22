"""
전체 파이프라인 통합 예시
텍스트 입력 → AI 카드 생성 → 상충도 분석 → 최종 추천
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_card_generator import CardGenerator
from conflict_engine import ConflictEngine


def main():
    print("🎴 인지 덱 시스템 - 전체 파이프라인")
    print("=" * 70)
    print()

    # ============================================
    # Step 1: 텍스트 입력 (회의록/메모)
    # ============================================
    print("📝 Step 1: 입력 텍스트")
    print("-" * 70)

    input_text = """
    제품 로드맵 회의 내용:

    우리는 글로벌 시장 진출을 목표로 하고 있어.
    예산은 50만 달러 정도 가용 가능해.
    마감 기한은 6개월이야. 정말 촉박해.

    현지화 전략이 매우 중요해. 특히 언어 지원.
    A/B 테스트로 번역 어투를 실험해봐야 할 것 같아.

    사용자 데이터 분석 결과, 모바일 트래픽이 80%야.
    하지만 데스크톱 사용자의 구매 전환율이 3배 높아.

    경쟁사는 이미 5개 언어를 지원하고 있어.
    우리는 새로운 접근이 필요해. 혁신적인 방법으로.

    팀 규모는 10명 정도 투입 가능해.
    """

    print(input_text)
    print()

    # ============================================
    # Step 2: AI 자동 카드 생성
    # ============================================
    print("🤖 Step 2: AI 카드 자동 생성")
    print("-" * 70)

    generator = CardGenerator(max_cards=7)
    deck_data = generator.generate_from_text(
        input_text,
        goal="글로벌 시장 진출 전략 수립"
    )

    print(f"목표: {deck_data['goal']}")
    print(f"생성된 카드: {len(deck_data['cards'])}개\n")

    for i, card in enumerate(deck_data['cards'], 1):
        print(f"  {i}. [{card['name']}] {card['value']}")
        print(f"     가중치: {card['weight']:.2f} | {card['category']}")

    print()

    # ============================================
    # Step 3: 전략 옵션 정의
    # ============================================
    print("🎯 Step 3: 전략 옵션")
    print("-" * 70)

    strategies = [
        {
            "name": "전면 현지화",
            "예산": 450000,
            "시간": 6,
            "언어": 10,
            "리스크": 0.7,
            "tags": ["안정", "전통", "품질"],
        },
        {
            "name": "점진적 확장",
            "예산": 200000,
            "시간": 3,
            "언어": 3,
            "리스크": 0.3,
            "tags": ["효율", "빠름", "데이터"],
        },
        {
            "name": "AI 자동화",
            "예산": 300000,
            "시간": 4,
            "언어": 20,
            "리스크": 0.8,
            "tags": ["혁신", "모험", "새로운"],
        },
        {
            "name": "커뮤니티 번역",
            "예산": 100000,
            "시간": 5,
            "언어": 15,
            "리스크": 0.5,
            "tags": ["경제적", "사회적", "실험"],
        },
    ]

    for strategy in strategies:
        print(f"  [{strategy['name']}]")
        print(f"    예산: ${strategy['예산']:,} | "
              f"기간: {strategy['시간']}개월 | "
              f"언어: {strategy['언어']}개")
        print(f"    태그: {', '.join(strategy['tags'])}")

    print()

    # ============================================
    # Step 4: 상충도 분석
    # ============================================
    print("⚖️  Step 4: 전략 간 상충도 분석")
    print("-" * 70)

    # 카드 가중치 추출
    card_weights = {
        card['name']: card['weight']
        for card in deck_data['cards']
    }

    engine = ConflictEngine(card_weights)

    print("  주요 상충 관계:")
    for i, strat_a in enumerate(strategies):
        for j, strat_b in enumerate(strategies):
            if i >= j:
                continue

            conflict_rate, reason = engine.calculate_conflict(strat_a, strat_b)

            if conflict_rate > 0.3:
                print(f"    {strat_a['name']:15s} vs {strat_b['name']:15s}: "
                      f"{conflict_rate:.2f}")

    print()

    # ============================================
    # Step 5: 최종 추천
    # ============================================
    print("🏆 Step 5: AI 기반 전략 추천")
    print("-" * 70)

    # 선호도 (카드에서 추출)
    preferences = {
        "예산": 500000,
        "시간": 6,
        "리스크": 0.5,
    }

    ranked = engine.rank_options(strategies, preferences)

    print("  순위:")
    for idx, (strategy, score) in enumerate(ranked, 1):
        bar = "█" * int(score * 30)
        print(f"    {idx}. {strategy['name']:15s} {score:.3f} {bar}")

    print()

    # 추천 이유
    winner = ranked[0][0]
    print(f"  💡 추천 전략: {winner['name']}")
    print(f"")
    print(f"  🎯 선택 이유:")
    print(f"     - 예산 범위 내: ${winner['예산']:,} (한도: ${preferences['예산']:,})")
    print(f"     - 기한 준수: {winner['시간']}개월 (목표: {preferences['시간']}개월)")
    print(f"     - 언어 커버리지: {winner['언어']}개 언어 지원")
    print(f"     - 리스크 수준: {winner['리스크']:.1f} (적절)")
    print()

    # 넛지: 실행 가이드
    print("  📋 실행 계획 (넛지):")
    print("     1. 먼저 핵심 3개 언어부터 시작 (빠른 검증)")
    print("     2. A/B 테스트로 번역 어투 최적화")
    print("     3. 사용자 피드백 기반 점진적 확장")
    print("     4. 모바일 최적화 우선 (80% 트래픽)")
    print()

    print("=" * 70)


if __name__ == "__main__":
    main()
