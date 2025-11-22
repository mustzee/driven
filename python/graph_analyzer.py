"""
카드 관계 그래프 분석 엔진
메인스트림 vs 서브스트림 자동 구별

수학적 접근:
1. 그래프 중심성 (Centrality) - 어떤 카드가 핵심인가?
2. 커뮤니티 감지 (Community Detection) - 어떤 아젠다로 묶이는가?
3. 계층 구조 (Hierarchy) - 메인/서브 레벨 구분
"""

import networkx as nx
from typing import List, Dict, Tuple, Any
from collections import defaultdict
import math


class CardGraphAnalyzer:
    """카드 간 관계를 그래프로 분석"""

    def __init__(self, cards: List[Dict[str, Any]]):
        """
        Args:
            cards: 카드 리스트
        """
        self.cards = cards
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        """카드들로 그래프 구성"""
        # 노드 추가 (각 카드)
        for card in self.cards:
            self.graph.add_node(
                card['name'],
                weight=card.get('weight', 0.5),
                category=card.get('category', ''),
                value=card.get('value', ''),
                source=card.get('source', '')
            )

        # 엣지 추가 (카드 간 연관성)
        for i, card_a in enumerate(self.cards):
            for j, card_b in enumerate(self.cards):
                if i >= j:
                    continue

                similarity = self._calculate_similarity(card_a, card_b)

                # 유사도가 임계값 이상이면 연결
                if similarity > 0.2:
                    self.graph.add_edge(
                        card_a['name'],
                        card_b['name'],
                        weight=similarity
                    )

    def _calculate_similarity(self, card_a: Dict, card_b: Dict) -> float:
        """
        두 카드 간 유사도 계산

        방법:
        1. 카테고리 동일 -> +0.3
        2. 텍스트 유사도 (단어 겹침) -> 0~0.5
        3. 가중치 차이 -> 0~0.2
        """
        similarity = 0.0

        # 같은 카테고리
        if card_a.get('category') == card_b.get('category'):
            similarity += 0.3

        # 텍스트 유사도 (출처 문장)
        source_a = card_a.get('source', '').lower()
        source_b = card_b.get('source', '').lower()

        if source_a and source_b:
            words_a = set(source_a.split())
            words_b = set(source_b.split())

            if words_a and words_b:
                # Jaccard 유사도
                intersection = len(words_a & words_b)
                union = len(words_a | words_b)
                text_sim = intersection / union if union > 0 else 0
                similarity += text_sim * 0.5

        # 가중치 유사도 (비슷한 중요도)
        weight_a = card_a.get('weight', 0.5)
        weight_b = card_b.get('weight', 0.5)
        weight_diff = abs(weight_a - weight_b)
        weight_sim = 1.0 - weight_diff
        similarity += weight_sim * 0.2

        return min(similarity, 1.0)

    def identify_mainstream_cards(self) -> Dict[str, Any]:
        """
        메인스트림 카드 식별

        수학적 방법:
        - PageRank: 다른 카드들과 많이 연결된 카드 (중요도)
        - Betweenness Centrality: 여러 카드를 연결하는 "허브" 카드
        - Degree Centrality: 직접 연결 수
        """

        # 1. PageRank (구글 검색 알고리즘)
        pagerank = nx.pagerank(self.graph, weight='weight')

        # 2. Betweenness Centrality (매개 중심성)
        betweenness = nx.betweenness_centrality(self.graph, weight='weight')

        # 3. Degree Centrality (연결 중심성)
        degree = nx.degree_centrality(self.graph)

        # 4. Eigenvector Centrality (고유벡터 중심성)
        # 중요한 노드와 연결된 노드가 중요
        try:
            eigenvector = nx.eigenvector_centrality(self.graph, weight='weight', max_iter=1000)
        except:
            eigenvector = {node: 0 for node in self.graph.nodes()}

        # 종합 점수 계산 (가중 평균)
        mainstream_scores = {}
        for node in self.graph.nodes():
            score = (
                pagerank.get(node, 0) * 0.4 +
                betweenness.get(node, 0) * 0.3 +
                degree.get(node, 0) * 0.2 +
                eigenvector.get(node, 0) * 0.1
            )
            mainstream_scores[node] = score

        # 상위 30%를 메인스트림으로
        threshold = sorted(mainstream_scores.values(), reverse=True)[
            int(len(mainstream_scores) * 0.3)
        ] if len(mainstream_scores) > 3 else 0.5

        mainstream_cards = {
            node: score
            for node, score in mainstream_scores.items()
            if score >= threshold
        }

        return {
            'mainstream': mainstream_cards,
            'all_scores': mainstream_scores,
            'centrality': {
                'pagerank': pagerank,
                'betweenness': betweenness,
                'degree': degree,
                'eigenvector': eigenvector
            }
        }

    def detect_agendas(self) -> List[Dict[str, Any]]:
        """
        아젠다(주제) 자동 추출

        방법: Louvain 커뮤니티 감지 알고리즘
        - 같은 커뮤니티 = 같은 아젠다
        """
        communities = nx.community.louvain_communities(self.graph, weight='weight')

        agendas = []
        for i, community in enumerate(communities):
            # 커뮤니티 내 카드들
            cards_in_community = list(community)

            # 커뮤니티 대표 카드 (가장 중심적인 카드)
            subgraph = self.graph.subgraph(community)
            pagerank = nx.pagerank(subgraph, weight='weight')
            representative = max(pagerank, key=pagerank.get)

            # 커뮤니티 카테고리 (다수결)
            categories = [
                self.graph.nodes[card]['category']
                for card in cards_in_community
            ]
            main_category = max(set(categories), key=categories.count)

            agendas.append({
                'agenda_id': f'agenda-{i}',
                'name': f'아젠다 {i+1}: {representative}',
                'representative_card': representative,
                'cards': cards_in_community,
                'size': len(cards_in_community),
                'category': main_category,
                'cohesion': self._calculate_cohesion(subgraph)
            })

        # 크기 순으로 정렬
        agendas.sort(key=lambda x: x['size'], reverse=True)

        return agendas

    def _calculate_cohesion(self, subgraph) -> float:
        """
        커뮤니티 응집도 계산

        응집도 = (실제 엣지 수) / (가능한 최대 엣지 수)
        """
        n = subgraph.number_of_nodes()
        if n <= 1:
            return 0.0

        actual_edges = subgraph.number_of_edges()
        max_edges = n * (n - 1) / 2

        return actual_edges / max_edges if max_edges > 0 else 0

    def build_hierarchy(self) -> Dict[str, Any]:
        """
        계층 구조 구축

        메인 레벨: 메인스트림 카드들
        서브 레벨: 메인에 연결된 서브스트림 카드들
        """
        mainstream_result = self.identify_mainstream_cards()
        mainstream = set(mainstream_result['mainstream'].keys())

        hierarchy = {
            'main': [],
            'sub': {},
            'orphan': []  # 어디에도 속하지 않는 카드
        }

        # 메인 레벨 카드
        for card in mainstream:
            hierarchy['main'].append({
                'name': card,
                'score': mainstream_result['mainstream'][card],
                'level': 'main'
            })

        # 서브 레벨 카드 (메인에 연결된 것들)
        for node in self.graph.nodes():
            if node in mainstream:
                continue

            # 이 카드가 연결된 메인스트림 카드 찾기
            connected_main = [
                neighbor for neighbor in self.graph.neighbors(node)
                if neighbor in mainstream
            ]

            if connected_main:
                # 가장 강하게 연결된 메인 카드에 배속
                main_parent = max(
                    connected_main,
                    key=lambda m: self.graph[node][m]['weight']
                )

                if main_parent not in hierarchy['sub']:
                    hierarchy['sub'][main_parent] = []

                hierarchy['sub'][main_parent].append({
                    'name': node,
                    'score': mainstream_result['all_scores'][node],
                    'level': 'sub',
                    'connection_strength': self.graph[node][main_parent]['weight']
                })
            else:
                hierarchy['orphan'].append({
                    'name': node,
                    'score': mainstream_result['all_scores'][node],
                    'level': 'orphan'
                })

        return hierarchy

    def get_graph_data(self) -> Dict[str, Any]:
        """
        D3.js 시각화를 위한 그래프 데이터 반환

        형식:
        {
            nodes: [{id, label, weight, ...}],
            links: [{source, target, weight}]
        }
        """
        mainstream_result = self.identify_mainstream_cards()
        mainstream = set(mainstream_result['mainstream'].keys())

        nodes = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            nodes.append({
                'id': node,
                'label': node,
                'weight': node_data.get('weight', 0.5),
                'category': node_data.get('category', ''),
                'value': str(node_data.get('value', '')),
                'is_mainstream': node in mainstream,
                'centrality_score': mainstream_result['all_scores'].get(node, 0),
                'pagerank': mainstream_result['centrality']['pagerank'].get(node, 0),
                'betweenness': mainstream_result['centrality']['betweenness'].get(node, 0)
            })

        links = []
        for edge in self.graph.edges(data=True):
            links.append({
                'source': edge[0],
                'target': edge[1],
                'weight': edge[2].get('weight', 0.5)
            })

        return {
            'nodes': nodes,
            'links': links
        }


def analyze_meeting_notes(text: str, max_cards: int = 10) -> Dict[str, Any]:
    """
    회의록 분석 전체 파이프라인

    Args:
        text: 회의록 텍스트
        max_cards: 최대 카드 수

    Returns:
        분석 결과 (그래프, 메인스트림, 아젠다 등)
    """
    from ai_card_generator import CardGenerator

    # 1. 카드 생성
    generator = CardGenerator(max_cards=max_cards)
    deck_data = generator.generate_from_text(text)
    cards = deck_data['cards']

    if len(cards) < 2:
        return {
            'error': 'Not enough cards generated',
            'cards': cards
        }

    # 2. 그래프 분석
    analyzer = CardGraphAnalyzer(cards)

    # 3. 메인스트림 식별
    mainstream_result = analyzer.identify_mainstream_cards()

    # 4. 아젠다 추출
    agendas = analyzer.detect_agendas()

    # 5. 계층 구조
    hierarchy = analyzer.build_hierarchy()

    # 6. 그래프 데이터
    graph_data = analyzer.get_graph_data()

    return {
        'cards': cards,
        'mainstream': mainstream_result,
        'agendas': agendas,
        'hierarchy': hierarchy,
        'graph': graph_data,
        'statistics': {
            'total_cards': len(cards),
            'mainstream_count': len(mainstream_result['mainstream']),
            'substream_count': len(cards) - len(mainstream_result['mainstream']),
            'agendas_count': len(agendas),
            'orphan_count': len(hierarchy['orphan'])
        }
    }
