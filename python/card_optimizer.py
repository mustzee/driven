#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Card Optimizer - 스마트 카드 제거 및 최적화

중복, 노이즈, 저품질 카드를 자동으로 감지하고 제거하여
의사결정에 필요한 핵심 카드만 유지합니다.
"""

import re
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict


class CardQuality:
    """카드 품질 평가"""

    @staticmethod
    def calculate_quality_score(card: Dict[str, Any]) -> float:
        """카드 품질 점수 계산 (0.0 ~ 1.0)"""
        score = 0.0
        weights = {
            'has_value': 0.3,        # 값이 있는가
            'has_category': 0.2,     # 카테고리가 있는가
            'has_weight': 0.2,       # 가중치가 있는가
            'name_quality': 0.15,    # 이름 품질
            'value_quality': 0.15,   # 값 품질
        }

        # 1. 값 존재 여부
        if card.get('value'):
            score += weights['has_value']

        # 2. 카테고리 존재 여부
        if card.get('category'):
            score += weights['has_category']

        # 3. 가중치 존재 여부
        weight = card.get('weight', 0)
        if weight and 0 < weight <= 1.0:
            score += weights['has_weight']

        # 4. 이름 품질 (너무 짧거나 의미없는 이름)
        name = card.get('name', '')
        if len(name) >= 2 and not CardQuality._is_meaningless_name(name):
            score += weights['name_quality']

        # 5. 값 품질 (숫자나 의미있는 텍스트)
        value = card.get('value')
        if CardQuality._is_meaningful_value(value):
            score += weights['value_quality']

        return score

    @staticmethod
    def _is_meaningless_name(name: str) -> bool:
        """의미없는 이름인지 확인"""
        meaningless_patterns = [
            r'^[0-9]+$',              # 숫자만
            r'^[a-z]$',               # 한 글자
            r'^test',                 # test로 시작
            r'^tmp',                  # tmp로 시작
            r'^undefined',            # undefined
            r'^null',                 # null
        ]

        for pattern in meaningless_patterns:
            if re.match(pattern, name.lower()):
                return True
        return False

    @staticmethod
    def _is_meaningful_value(value: Any) -> bool:
        """의미있는 값인지 확인"""
        if value is None:
            return False

        if isinstance(value, (int, float)):
            return True

        if isinstance(value, str):
            # 빈 문자열이거나 "null", "undefined" 같은 값
            if not value.strip() or value.lower() in ['null', 'undefined', 'none', 'n/a']:
                return False
            return True

        return False


class DuplicateDetector:
    """중복 카드 감지"""

    @staticmethod
    def find_duplicates(cards: List[Dict[str, Any]]) -> List[List[int]]:
        """중복 카드 그룹 찾기 (인덱스 리스트 반환)"""
        duplicate_groups = []

        # 이름 기반 그룹핑
        name_groups = defaultdict(list)
        for i, card in enumerate(cards):
            normalized_name = DuplicateDetector._normalize_name(card.get('name', ''))
            if normalized_name:
                name_groups[normalized_name].append(i)

        # 2개 이상인 그룹만 중복으로 간주
        for indices in name_groups.values():
            if len(indices) >= 2:
                # 값도 비교해서 정말 중복인지 확인
                if DuplicateDetector._are_truly_duplicates(cards, indices):
                    duplicate_groups.append(indices)

        return duplicate_groups

    @staticmethod
    def _normalize_name(name: str) -> str:
        """이름 정규화 (공백, 대소문자, 특수문자 제거)"""
        # 공백 제거
        normalized = re.sub(r'\s+', '', name)
        # 소문자 변환
        normalized = normalized.lower()
        # 특수문자 제거 (단, 한글/영문/숫자는 유지)
        normalized = re.sub(r'[^\w가-힣]', '', normalized)
        return normalized

    @staticmethod
    def _are_truly_duplicates(cards: List[Dict[str, Any]], indices: List[int]) -> bool:
        """정말 중복인지 값까지 비교"""
        if len(indices) < 2:
            return False

        # 첫 번째 카드와 나머지 비교
        first_card = cards[indices[0]]
        first_value = str(first_card.get('value', '')).lower().strip()

        for idx in indices[1:]:
            card = cards[idx]
            value = str(card.get('value', '')).lower().strip()

            # 값이 같으면 중복
            if first_value == value:
                return True

        return False

    @staticmethod
    def select_best_from_duplicates(cards: List[Dict[str, Any]], duplicate_indices: List[int]) -> int:
        """중복 그룹에서 가장 좋은 카드 선택 (인덱스 반환)"""
        best_idx = duplicate_indices[0]
        best_score = CardQuality.calculate_quality_score(cards[best_idx])

        for idx in duplicate_indices[1:]:
            score = CardQuality.calculate_quality_score(cards[idx])
            if score > best_score:
                best_idx = idx
                best_score = score

        return best_idx


class NoiseDetector:
    """노이즈 카드 감지"""

    # 노이즈로 간주할 카테고리 키워드
    NOISE_CATEGORIES = {'테스트', 'test', 'tmp', 'debug', '임시'}

    # 노이즈로 간주할 이름 패턴
    NOISE_NAME_PATTERNS = [
        r'^test',
        r'^tmp',
        r'^debug',
        r'임시',
        r'테스트',
    ]

    @staticmethod
    def is_noise(card: Dict[str, Any], threshold: float = 0.3) -> bool:
        """노이즈 카드인지 판단"""
        # 1. 품질 점수가 너무 낮으면 노이즈
        quality_score = CardQuality.calculate_quality_score(card)
        if quality_score < threshold:
            return True

        # 2. 카테고리가 노이즈 카테고리
        category = card.get('category', '').lower()
        if category in NoiseDetector.NOISE_CATEGORIES:
            return True

        # 3. 이름이 노이즈 패턴
        name = card.get('name', '').lower()
        for pattern in NoiseDetector.NOISE_NAME_PATTERNS:
            if re.search(pattern, name):
                return True

        # 4. 가중치가 너무 낮으면 노이즈
        weight = card.get('weight', 0)
        if weight > 0 and weight < 0.1:
            return True

        return False


class CardOptimizer:
    """카드 최적화 엔진"""

    def __init__(self, cards: List[Dict[str, Any]], max_cards: int = 7):
        self.cards = cards
        self.max_cards = max_cards
        self.removal_log = []

    def optimize(self, remove_duplicates: bool = True,
                remove_noise: bool = True,
                trim_to_limit: bool = True) -> Dict[str, Any]:
        """카드 최적화 실행"""
        optimized_cards = self.cards.copy()
        stats = {
            'original_count': len(self.cards),
            'duplicates_removed': 0,
            'noise_removed': 0,
            'trimmed': 0,
            'final_count': 0,
        }

        # 1. 중복 제거
        if remove_duplicates:
            optimized_cards, dup_count = self._remove_duplicates(optimized_cards)
            stats['duplicates_removed'] = dup_count

        # 2. 노이즈 제거
        if remove_noise:
            optimized_cards, noise_count = self._remove_noise(optimized_cards)
            stats['noise_removed'] = noise_count

        # 3. 개수 제한 (Miller's Law)
        if trim_to_limit and len(optimized_cards) > self.max_cards:
            optimized_cards, trim_count = self._trim_to_limit(optimized_cards)
            stats['trimmed'] = trim_count

        stats['final_count'] = len(optimized_cards)

        return {
            'optimized_cards': optimized_cards,
            'stats': stats,
            'removal_log': self.removal_log,
        }

    def _remove_duplicates(self, cards: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """중복 카드 제거"""
        duplicate_groups = DuplicateDetector.find_duplicates(cards)

        # 제거할 인덱스 수집
        indices_to_remove = set()
        for group in duplicate_groups:
            # 그룹에서 가장 좋은 카드 선택
            best_idx = DuplicateDetector.select_best_from_duplicates(cards, group)

            # 나머지는 제거
            for idx in group:
                if idx != best_idx:
                    indices_to_remove.add(idx)
                    self.removal_log.append({
                        'type': 'duplicate',
                        'card': cards[idx],
                        'reason': f"중복 (대표 카드: {cards[best_idx]['name']})"
                    })

        # 제거
        cleaned = [card for i, card in enumerate(cards) if i not in indices_to_remove]
        return cleaned, len(indices_to_remove)

    def _remove_noise(self, cards: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """노이즈 카드 제거"""
        noise_indices = []

        for i, card in enumerate(cards):
            if NoiseDetector.is_noise(card):
                noise_indices.append(i)
                quality = CardQuality.calculate_quality_score(card)
                self.removal_log.append({
                    'type': 'noise',
                    'card': card,
                    'reason': f"저품질 카드 (품질 점수: {quality:.2f})"
                })

        # 제거
        cleaned = [card for i, card in enumerate(cards) if i not in noise_indices]
        return cleaned, len(noise_indices)

    def _trim_to_limit(self, cards: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """개수 제한에 맞게 트림 (낮은 우선순위 카드 제거)"""
        if len(cards) <= self.max_cards:
            return cards, 0

        # 카드별 우선순위 점수 계산
        scored_cards = []
        for card in cards:
            priority = self._calculate_priority(card)
            scored_cards.append((card, priority))

        # 우선순위 내림차순 정렬
        scored_cards.sort(key=lambda x: x[1], reverse=True)

        # 상위 N개만 유지
        kept_cards = [card for card, _ in scored_cards[:self.max_cards]]
        removed_cards = scored_cards[self.max_cards:]

        # 제거 로그
        for card, priority in removed_cards:
            self.removal_log.append({
                'type': 'trimmed',
                'card': card,
                'reason': f"개수 제한 초과 (우선순위: {priority:.2f})"
            })

        return kept_cards, len(removed_cards)

    def _calculate_priority(self, card: Dict[str, Any]) -> float:
        """카드 우선순위 점수 계산"""
        # 품질 점수
        quality = CardQuality.calculate_quality_score(card)

        # 가중치
        weight = card.get('weight', 0.5)

        # 우선순위 = 품질 * 가중치
        priority = quality * weight

        return priority

    def get_removal_summary(self) -> str:
        """제거 요약 텍스트 생성"""
        if not self.removal_log:
            return "제거된 카드가 없습니다."

        summary_lines = []
        summary_lines.append(f"총 {len(self.removal_log)}개 카드 제거:")

        # 타입별 그룹핑
        by_type = defaultdict(list)
        for log in self.removal_log:
            by_type[log['type']].append(log)

        for card_type, logs in by_type.items():
            type_labels = {
                'duplicate': '중복',
                'noise': '노이즈',
                'trimmed': '개수 초과',
            }
            label = type_labels.get(card_type, card_type)
            summary_lines.append(f"\n  [{label}] {len(logs)}개")

            for log in logs[:3]:  # 최대 3개만 표시
                summary_lines.append(f"    - {log['card']['name']}: {log['reason']}")

            if len(logs) > 3:
                summary_lines.append(f"    ... 외 {len(logs) - 3}개")

        return '\n'.join(summary_lines)


def optimize_cards(cards: List[Dict[str, Any]],
                  max_cards: int = 7,
                  remove_duplicates: bool = True,
                  remove_noise: bool = True,
                  trim_to_limit: bool = True) -> Dict[str, Any]:
    """카드 최적화 (메인 함수)"""
    optimizer = CardOptimizer(cards, max_cards)
    result = optimizer.optimize(remove_duplicates, remove_noise, trim_to_limit)
    result['summary'] = optimizer.get_removal_summary()
    return result


if __name__ == "__main__":
    # 테스트 케이스
    test_cards = [
        {'name': '예산', 'value': 5000000, 'category': '경제적', 'weight': 0.8},
        {'name': '예산', 'value': 5000000, 'category': '경제적', 'weight': 0.7},  # 중복
        {'name': '예산  ', 'value': 5000000, 'category': '경제적', 'weight': 0.6},  # 중복 (공백)
        {'name': '팀', 'value': 10, 'category': '사회적', 'weight': 0.7},
        {'name': 'test', 'value': 'test', 'category': 'test', 'weight': 0.1},  # 노이즈
        {'name': '일정', 'value': '3개월', 'category': '시간적', 'weight': 0.9},
        {'name': '품질', 'value': 85, 'category': '품질', 'weight': 0.8},
        {'name': 'tmp', 'value': None, 'category': '임시', 'weight': 0.05},  # 노이즈
        {'name': '리스크', 'value': 'high', 'category': '위험', 'weight': 0.6},
        {'name': '확장성', 'value': 'medium', 'category': '전략', 'weight': 0.5},
        {'name': '팀역량', 'value': 75, 'category': '사회적', 'weight': 0.7},
        {'name': 'debug', 'value': 'x', 'category': 'test', 'weight': 0.01},  # 노이즈
    ]

    print("=" * 60)
    print("카드 최적화 테스트")
    print("=" * 60)

    print(f"\n📊 원본 카드: {len(test_cards)}개")
    for i, card in enumerate(test_cards, 1):
        quality = CardQuality.calculate_quality_score(card)
        print(f"  {i}. {card['name']} (품질: {quality:.2f}, 가중치: {card.get('weight', 0)})")

    # 최적화 실행
    result = optimize_cards(
        test_cards,
        max_cards=7,
        remove_duplicates=True,
        remove_noise=True,
        trim_to_limit=True
    )

    print(f"\n✨ 최적화 후: {len(result['optimized_cards'])}개")
    for i, card in enumerate(result['optimized_cards'], 1):
        quality = CardQuality.calculate_quality_score(card)
        print(f"  {i}. {card['name']} (품질: {quality:.2f}, 가중치: {card.get('weight', 0)})")

    print(f"\n📈 통계:")
    print(f"  원본: {result['stats']['original_count']}개")
    print(f"  중복 제거: -{result['stats']['duplicates_removed']}개")
    print(f"  노이즈 제거: -{result['stats']['noise_removed']}개")
    print(f"  개수 초과 트림: -{result['stats']['trimmed']}개")
    print(f"  최종: {result['stats']['final_count']}개")

    print(f"\n📝 제거 요약:")
    print(result['summary'])
