"""
그래프 분석 데모: 메인스트림/서브스트림 자동 구별
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_analyzer_lite import analyze_meeting_notes
import json


def main():
    print("🕸️  카드 관계 그래프 분석 - 메인스트림/서브스트림 구별")
    print("=" * 80)
    print()

    # ==================== 회의록 예시 ====================
    meeting_text = """
    제품 로드맵 회의 - 2025 Q1

    우리의 핵심 목표는 글로벌 시장 진출입니다.
    예산은 50만 달러로 매우 제한적입니다.
    마감 기한은 6개월로 정말 촉박합니다.

    현지화 전략이 가장 중요합니다. 이것이 성공의 핵심입니다.
    특히 언어 지원과 문화 적응이 필수적입니다.

    A/B 테스트를 통해 번역 어투를 최적화해야 합니다.
    사용자 피드백 수집도 병행해야 합니다.

    데이터 분석 결과, 모바일 트래픽이 80%입니다.
    모바일 최적화가 우선순위여야 합니다.

    하지만 데스크톱 사용자의 구매 전환율이 3배 높습니다.
    데스크톱 UX도 무시할 수 없습니다.

    경쟁사는 이미 5개 언어를 지원하고 있습니다.
    우리는 차별화된 접근이 필요합니다.

    팀 규모는 10명이 투입 가능합니다.
    개발자 5명, 디자이너 2명, PM 1명, QA 2명입니다.

    마케팅 예산도 별도로 10만 달러 확보했습니다.
    SNS 광고와 인플루언서 마케팅에 집중할 계획입니다.
    """

    print("📝 입력 회의록:")
    print("-" * 80)
    print(meeting_text.strip())
    print()
    print("=" * 80)
    print()

    # ==================== 분석 실행 ====================
    print("🔍 분석 중...")
    result = analyze_meeting_notes(meeting_text, max_cards=15)

    if 'error' in result:
        print(f"⚠️  에러: {result['error']}")
        return

    print("✅ 분석 완료!")
    print()

    # ==================== 통계 ====================
    stats = result['statistics']
    print("📊 통계:")
    print("-" * 80)
    print(f"  총 카드 수:        {stats['total_cards']}")
    print(f"  메인스트림 카드:   {stats['mainstream_count']} "
          f"({stats['mainstream_count']/stats['total_cards']*100:.1f}%)")
    print(f"  서브스트림 카드:   {stats['substream_count']} "
          f"({stats['substream_count']/stats['total_cards']*100:.1f}%)")
    print(f"  감지된 아젠다:     {stats['agendas_count']}")
    print(f"  고아 카드:         {stats['orphan_count']}")
    print()

    # ==================== 메인스트림 카드 ====================
    print("🎯 메인스트림 카드 (핵심 아젠다):")
    print("-" * 80)

    mainstream_cards = result['mainstream']['mainstream']
    sorted_mainstream = sorted(
        mainstream_cards.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for i, (card_name, score) in enumerate(sorted_mainstream, 1):
        bar = "█" * int(score * 50)
        print(f"  {i}. [{card_name}]")
        print(f"     중요도: {score:.4f} {bar}")

        # 중심성 세부 정보
        centrality = result['mainstream']['centrality']
        print(f"     PageRank:     {centrality['pagerank'].get(card_name, 0):.4f}")
        print(f"     Betweenness:  {centrality['betweenness'].get(card_name, 0):.4f}")
        print(f"     Degree:       {centrality['degree'].get(card_name, 0):.4f}")
        print()

    # ==================== 계층 구조 ====================
    print("🌳 계층 구조 (메인 → 서브):")
    print("-" * 80)

    hierarchy = result['hierarchy']

    for main_card in hierarchy['main']:
        print(f"📌 {main_card['name']} (메인)")

        # 이 메인 카드에 연결된 서브 카드들
        if main_card['name'] in hierarchy['sub']:
            subs = hierarchy['sub'][main_card['name']]
            subs.sort(key=lambda x: x['connection_strength'], reverse=True)

            for sub in subs:
                strength = sub['connection_strength']
                bar = "─" * int(strength * 30)
                print(f"  └{bar}> {sub['name']} (서브, 연결강도: {strength:.2f})")

        print()

    # 고아 카드
    if hierarchy['orphan']:
        print("🔸 고아 카드 (독립적):")
        for orphan in hierarchy['orphan']:
            print(f"  • {orphan['name']}")
        print()

    # ==================== 아젠다 ====================
    print("📋 자동 추출된 아젠다:")
    print("-" * 80)

    for agenda in result['agendas']:
        print(f"\n{agenda['name']}")
        print(f"  대표 카드:   {agenda['representative_card']}")
        print(f"  카드 수:     {agenda['size']}")
        print(f"  카테고리:    {agenda['category']}")
        print(f"  응집도:      {agenda['cohesion']:.2f}")
        print(f"  포함 카드:   {', '.join(agenda['cards'])}")

    print()
    print("=" * 80)

    # ==================== JSON 출력 (API용) ====================
    print()
    print("📦 그래프 데이터 (D3.js 시각화용):")
    print("-" * 80)

    graph_data = result['graph']
    print(f"노드 수: {len(graph_data['nodes'])}")
    print(f"간선 수: {len(graph_data['links'])}")
    print()

    # 샘플 출력
    print("노드 샘플 (상위 3개):")
    for node in graph_data['nodes'][:3]:
        print(f"  - {node['id']}: mainstream={node['is_mainstream']}, "
              f"centrality={node['centrality_score']:.4f}")

    print()
    print("간선 샘플 (상위 3개):")
    for link in sorted(graph_data['links'], key=lambda x: x['weight'], reverse=True)[:3]:
        print(f"  - {link['source']} ↔ {link['target']}: {link['weight']:.2f}")

    print()
    print("=" * 80)

    # JSON 파일로 저장
    output_file = "graph_analysis_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 전체 결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    main()
