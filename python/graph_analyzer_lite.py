"""
카드 관계 그래프 분석 엔진 (경량 버전 - 외부 의존성 없음)
메인스트림 vs 서브스트림 자동 구별
"""

from typing import List, Dict, Tuple, Any
from collections import defaultdict
import math


class SimpleGraph:
    """간단한 그래프 구현"""

    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.adjacency = defaultdict(dict)

    def add_node(self, node_id, **attrs):
        self.nodes[node_id] = attrs

    def add_edge(self, source, target, weight=1.0):
        self.edges.append((source, target, weight))
        self.adjacency[source][target] = weight
        self.adjacency[target][source] = weight  # 무방향 그래프

    def neighbors(self, node_id):
        return list(self.adjacency[node_id].keys())

    def get_edge_weight(self, source, target):
        return self.adjacency.get(source, {}).get(target, 0)


class CardGraphAnalyzer:
    """카드 간 관계를 그래프로 분석 (의존성 없는 버전)"""

    def __init__(self, cards: List[Dict[str, Any]]):
        self.cards = cards
        self.graph = SimpleGraph()
        self._build_graph()

    def _build_graph(self):
        """카드들로 그래프 구성"""
        # 노드 추가
        for card in self.cards:
            self.graph.add_node(
                card['name'],
                weight=card.get('weight', 0.5),
                category=card.get('category', ''),
                value=card.get('value', ''),
                source=card.get('source', '')
            )

        # 엣지 추가
        for i, card_a in enumerate(self.cards):
            for j, card_b in enumerate(self.cards):
                if i >= j:
                    continue

                similarity = self._calculate_similarity(card_a, card_b)

                if similarity > 0.2:
                    self.graph.add_edge(
                        card_a['name'],
                        card_b['name'],
                        similarity
                    )

    def _calculate_similarity(self, card_a: Dict, card_b: Dict) -> float:
        """두 카드 간 유사도 계산"""
        similarity = 0.0

        # 같은 카테고리
        if card_a.get('category') == card_b.get('category'):
            similarity += 0.3

        # 텍스트 유사도
        source_a = card_a.get('source', '').lower()
        source_b = card_b.get('source', '').lower()

        if source_a and source_b:
            words_a = set(source_a.split())
            words_b = set(source_b.split())

            if words_a and words_b:
                intersection = len(words_a & words_b)
                union = len(words_a | words_b)
                text_sim = intersection / union if union > 0 else 0
                similarity += text_sim * 0.5

        # 가중치 유사도
        weight_a = card_a.get('weight', 0.5)
        weight_b = card_b.get('weight', 0.5)
        weight_diff = abs(weight_a - weight_b)
        weight_sim = 1.0 - weight_diff
        similarity += weight_sim * 0.2

        return min(similarity, 1.0)

    def calculate_pagerank(self, iterations=20, damping=0.85) -> Dict[str, float]:
        """PageRank 계산 (간단한 구현)"""
        nodes = list(self.graph.nodes.keys())
        n = len(nodes)

        if n == 0:
            return {}

        # 초기값
        pagerank = {node: 1.0 / n for node in nodes}

        for _ in range(iterations):
            new_pagerank = {}

            for node in nodes:
                rank_sum = 0.0

                # 이 노드를 가리키는 모든 노드로부터 rank 받기
                for neighbor in self.graph.neighbors(node):
                    neighbor_degree = len(self.graph.neighbors(neighbor))
                    if neighbor_degree > 0:
                        edge_weight = self.graph.get_edge_weight(neighbor, node)
                        rank_sum += (pagerank[neighbor] * edge_weight) / neighbor_degree

                new_pagerank[node] = (1 - damping) / n + damping * rank_sum

            pagerank = new_pagerank

        # 정규화
        total = sum(pagerank.values())
        if total > 0:
            pagerank = {k: v / total for k, v in pagerank.items()}

        return pagerank

    def calculate_degree_centrality(self) -> Dict[str, float]:
        """연결 중심성 계산"""
        n = len(self.graph.nodes)
        if n <= 1:
            return {node: 0 for node in self.graph.nodes}

        centrality = {}
        for node in self.graph.nodes:
            degree = len(self.graph.neighbors(node))
            centrality[node] = degree / (n - 1)

        return centrality

    def calculate_betweenness_centrality(self) -> Dict[str, float]:
        """매개 중심성 계산 (단순화된 버전)"""
        nodes = list(self.graph.nodes.keys())
        betweenness = {node: 0.0 for node in nodes}

        # 모든 노드 쌍에 대해
        for source in nodes:
            # BFS로 최단 경로 찾기
            distances = {node: float('inf') for node in nodes}
            distances[source] = 0
            predecessors = {node: [] for node in nodes}

            queue = [source]
            while queue:
                current = queue.pop(0)

                for neighbor in self.graph.neighbors(current):
                    if distances[neighbor] == float('inf'):
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)

                    if distances[neighbor] == distances[current] + 1:
                        predecessors[neighbor].append(current)

            # 각 경로에서 중간 노드 카운트
            for target in nodes:
                if target == source or distances[target] == float('inf'):
                    continue

                # 경로 역추적
                paths = self._find_all_paths(predecessors, source, target)

                for path in paths:
                    for intermediate in path[1:-1]:  # 시작/끝 제외
                        betweenness[intermediate] += 1

        # 정규화
        n = len(nodes)
        if n > 2:
            norm = (n - 1) * (n - 2)
            betweenness = {k: v / norm for k, v in betweenness.items()}

        return betweenness

    def _find_all_paths(self, predecessors, source, target):
        """모든 최단 경로 찾기"""
        if target == source:
            return [[source]]

        paths = []
        for pred in predecessors[target]:
            for path in self._find_all_paths(predecessors, source, pred):
                paths.append(path + [target])

        return paths if paths else [[]]

    def identify_mainstream_cards(self) -> Dict[str, Any]:
        """메인스트림 카드 식별"""
        pagerank = self.calculate_pagerank()
        degree = self.calculate_degree_centrality()
        betweenness = self.calculate_betweenness_centrality()

        # 고유벡터 중심성 (간단 버전: degree와 유사)
        eigenvector = degree.copy()

        # 종합 점수
        mainstream_scores = {}
        for node in self.graph.nodes:
            score = (
                pagerank.get(node, 0) * 0.4 +
                betweenness.get(node, 0) * 0.3 +
                degree.get(node, 0) * 0.2 +
                eigenvector.get(node, 0) * 0.1
            )
            mainstream_scores[node] = score

        # 상위 30%를 메인스트림으로
        if len(mainstream_scores) >= 3:
            threshold_idx = int(len(mainstream_scores) * 0.3)
            threshold = sorted(mainstream_scores.values(), reverse=True)[threshold_idx]
        else:
            threshold = 0.5

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
        """아젠다 추출 (간단한 클러스터링)"""
        visited = set()
        agendas = []

        for node in self.graph.nodes:
            if node in visited:
                continue

            # BFS로 연결된 컴포넌트 찾기
            component = self._bfs_component(node, visited)

            if len(component) == 0:
                continue

            # 대표 카드 (가장 연결이 많은 것)
            representative = max(
                component,
                key=lambda n: len(self.graph.neighbors(n))
            )

            # 카테고리
            categories = [
                self.graph.nodes[card]['category']
                for card in component
            ]
            main_category = max(set(categories), key=categories.count) if categories else ''

            agendas.append({
                'agenda_id': f'agenda-{len(agendas)}',
                'name': f'아젠다 {len(agendas)+1}: {representative}',
                'representative_card': representative,
                'cards': list(component),
                'size': len(component),
                'category': main_category,
                'cohesion': self._calculate_cohesion(component)
            })

        agendas.sort(key=lambda x: x['size'], reverse=True)
        return agendas

    def _bfs_component(self, start_node, visited):
        """BFS로 연결된 컴포넌트 찾기"""
        component = set()
        queue = [start_node]

        while queue:
            node = queue.pop(0)

            if node in visited:
                continue

            visited.add(node)
            component.add(node)

            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)

        return component

    def _calculate_cohesion(self, nodes) -> float:
        """커뮤니티 응집도"""
        n = len(nodes)
        if n <= 1:
            return 0.0

        edge_count = 0
        for i, node_a in enumerate(nodes):
            for node_b in list(nodes)[i+1:]:
                if self.graph.get_edge_weight(node_a, node_b) > 0:
                    edge_count += 1

        max_edges = n * (n - 1) / 2
        return edge_count / max_edges if max_edges > 0 else 0

    def build_hierarchy(self) -> Dict[str, Any]:
        """계층 구조 구축"""
        mainstream_result = self.identify_mainstream_cards()
        mainstream = set(mainstream_result['mainstream'].keys())

        hierarchy = {
            'main': [],
            'sub': {},
            'orphan': []
        }

        # 메인 레벨
        for card in mainstream:
            hierarchy['main'].append({
                'name': card,
                'score': mainstream_result['mainstream'][card],
                'level': 'main'
            })

        # 서브 레벨
        for node in self.graph.nodes:
            if node in mainstream:
                continue

            connected_main = [
                neighbor for neighbor in self.graph.neighbors(node)
                if neighbor in mainstream
            ]

            if connected_main:
                main_parent = max(
                    connected_main,
                    key=lambda m: self.graph.get_edge_weight(node, m)
                )

                if main_parent not in hierarchy['sub']:
                    hierarchy['sub'][main_parent] = []

                hierarchy['sub'][main_parent].append({
                    'name': node,
                    'score': mainstream_result['all_scores'][node],
                    'level': 'sub',
                    'connection_strength': self.graph.get_edge_weight(node, main_parent)
                })
            else:
                hierarchy['orphan'].append({
                    'name': node,
                    'score': mainstream_result['all_scores'][node],
                    'level': 'orphan'
                })

        return hierarchy

    def get_graph_data(self) -> Dict[str, Any]:
        """D3.js 시각화용 그래프 데이터"""
        mainstream_result = self.identify_mainstream_cards()
        mainstream = set(mainstream_result['mainstream'].keys())

        nodes = []
        for node_id, node_data in self.graph.nodes.items():
            nodes.append({
                'id': node_id,
                'label': node_id,
                'weight': node_data.get('weight', 0.5),
                'category': node_data.get('category', ''),
                'value': str(node_data.get('value', '')),
                'is_mainstream': node_id in mainstream,
                'centrality_score': mainstream_result['all_scores'].get(node_id, 0),
                'pagerank': mainstream_result['centrality']['pagerank'].get(node_id, 0),
                'betweenness': mainstream_result['centrality']['betweenness'].get(node_id, 0)
            })

        links = []
        for source, target, weight in self.graph.edges:
            links.append({
                'source': source,
                'target': target,
                'weight': weight
            })

        return {
            'nodes': nodes,
            'links': links
        }


def analyze_meeting_notes(text: str, max_cards: int = 10) -> Dict[str, Any]:
    """회의록 분석 전체 파이프라인"""
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
