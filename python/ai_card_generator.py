"""
AI 기반 카드 자동 생성
회의록이나 텍스트에서 자동으로 의사결정 카드 추출
"""

import re
from typing import List, Dict, Any


class CardGenerator:
    """텍스트에서 의사결정 카드를 자동 생성"""

    # 카테고리 키워드 매핑
    CATEGORY_KEYWORDS = {
        "생리적": ["배고픔", "피곤", "건강", "아픔", "졸림", "목마름"],
        "경제적": ["예산", "비용", "가격", "돈", "저렴", "비싼", "할인"],
        "제약적": ["시간", "기한", "마감", "거리", "위치", "날짜"],
        "사회적": ["동행자", "친구", "가족", "동료", "팀", "사람"],
        "환경적": ["날씨", "온도", "계절", "분위기", "소음"],
        "심리적": ["스트레스", "불안", "기분", "감정", "만족"],
    }

    # 트레이드오프 패턴
    TRADEOFF_PATTERNS = {
        "정적-동적": {
            "정적": ["안정", "확실", "검증", "보수", "전통", "익숙"],
            "동적": ["새로운", "혁신", "모험", "시도", "실험", "도전"]
        },
        "이성-감성": {
            "이성": ["논리", "데이터", "분석", "계산", "효율", "합리"],
            "감성": ["감정", "느낌", "직관", "분위기", "경험", "인간적"]
        },
        "단기-장기": {
            "단기": ["즉시", "빠른", "당장", "오늘", "긴급"],
            "장기": ["장기적", "천천히", "지속", "미래", "투자"]
        }
    }

    def __init__(self, max_cards: int = 7):
        self.max_cards = max_cards

    def generate_from_text(self, text: str, goal: str = "") -> Dict[str, Any]:
        """
        텍스트에서 카드 추출

        Args:
            text: 분석할 텍스트 (회의록, 메모 등)
            goal: 의사결정 목표

        Returns:
            덱 정보 (카드들 포함)
        """
        cards = []

        # 1. 문장 분리
        sentences = self._split_sentences(text)

        # 2. 각 문장에서 카드 후보 추출
        for sentence in sentences:
            card_candidate = self._extract_card_from_sentence(sentence)
            if card_candidate:
                cards.append(card_candidate)

        # 3. 중복 제거 & 중요도 순 정렬
        cards = self._deduplicate_cards(cards)
        cards = sorted(cards, key=lambda x: x["weight"], reverse=True)

        # 4. 상위 N개만 선택 (인지 한계)
        cards = cards[:self.max_cards]

        return {
            "goal": goal or "의사결정",
            "max_slots": self.max_cards,
            "cards": cards
        }

    def _split_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        # 간단한 문장 분리 (., !, ? 기준)
        sentences = re.split(r'[.!?\n]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_card_from_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        문장에서 카드 후보 추출

        패턴:
        - "예산이 12000원"
        - "시간은 30분밖에 없어"
        - "배가 많이 고파"
        """
        # 카테고리 감지
        category = self._detect_category(sentence)
        if not category:
            return None

        # 값 추출 시도
        value = self._extract_value(sentence)

        # 가중치 계산 (문장 길이, 강조 표현 등)
        weight = self._calculate_weight(sentence)

        # 트레이드오프 추출
        trade_offs = self._extract_trade_offs(sentence)

        # 카드명 생성
        name = self._generate_card_name(sentence, category)

        return {
            "name": name,
            "category": category,
            "value": value,
            "weight": weight,
            "trade_offs": trade_offs,
            "source": sentence
        }

    def _detect_category(self, sentence: str) -> str:
        """문장에서 카테고리 감지"""
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in sentence:
                    return category
        return None

    def _extract_value(self, sentence: str) -> Any:
        """문장에서 값 추출"""
        # 숫자 패턴
        numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', sentence)
        if numbers:
            # 쉼표 제거 후 숫자로 변환
            num_str = numbers[0].replace(',', '')
            try:
                if '.' in num_str:
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                pass

        # 퍼센트 패턴
        percent = re.search(r'(\d+)%', sentence)
        if percent:
            return int(percent.group(1))

        # 기본값: 문장 자체
        return sentence

    def _calculate_weight(self, sentence: str) -> float:
        """가중치 계산"""
        weight = 0.5  # 기본 가중치

        # 강조 표현
        emphasis_words = ["매우", "정말", "너무", "꼭", "반드시", "중요", "필수"]
        for word in emphasis_words:
            if word in sentence:
                weight += 0.2

        # 부정 표현 (덜 중요)
        negative_words = ["별로", "그다지", "굳이"]
        for word in negative_words:
            if word in sentence:
                weight -= 0.2

        # 0~1 범위로 제한
        return max(0.1, min(1.0, weight))

    def _extract_trade_offs(self, sentence: str) -> List[Dict[str, float]]:
        """트레이드오프 추출"""
        trade_offs = []

        for dimension, sides in self.TRADEOFF_PATTERNS.items():
            left_keywords = sides[list(sides.keys())[0]]
            right_keywords = sides[list(sides.keys())[1]]

            left_count = sum(1 for kw in left_keywords if kw in sentence)
            right_count = sum(1 for kw in right_keywords if kw in sentence)

            if left_count > 0 or right_count > 0:
                # -1 (왼쪽) ~ +1 (오른쪽)
                value = (right_count - left_count) / max(left_count + right_count, 1)
                trade_offs.append({
                    "dimension": dimension,
                    "value": value
                })

        return trade_offs

    def _generate_card_name(self, sentence: str, category: str) -> str:
        """카드명 생성"""
        # 카테고리 키워드 찾기
        for keyword in self.CATEGORY_KEYWORDS.get(category, []):
            if keyword in sentence:
                return keyword

        # 기본값: 카테고리명
        return category

    def _deduplicate_cards(self, cards: List[Dict]) -> List[Dict]:
        """중복 카드 제거 (같은 이름의 카드는 병합)"""
        unique_cards = {}

        for card in cards:
            name = card["name"]

            if name in unique_cards:
                # 가중치 평균
                existing = unique_cards[name]
                existing["weight"] = (existing["weight"] + card["weight"]) / 2
            else:
                unique_cards[name] = card

        return list(unique_cards.values())


def demo():
    """AI 카드 생성 데모"""
    print("🤖 AI 카드 자동 생성 데모")
    print("=" * 60)
    print()

    # 회의록 예시
    meeting_notes = """
    오늘 점심 어디 갈지 결정해야 해.
    예산은 12000원 정도 생각하고 있어.
    시간은 30분밖에 없어서 빨리 먹어야 해.
    동행자가 3명이라서 단체석 필요해.
    날씨가 비라서 실내가 좋을 것 같아.
    거리는 500m 이내로 가깝게 가자.
    새로운 곳보다는 익숙한 곳이 안전할 것 같아.
    하지만 맛은 정말 중요해!
    """

    generator = CardGenerator(max_cards=7)
    result = generator.generate_from_text(
        meeting_notes,
        goal="만족스러운 점심 선택"
    )

    print(f"🎯 목표: {result['goal']}")
    print(f"📦 생성된 카드 수: {len(result['cards'])}/{result['max_slots']}")
    print()

    print("🃏 생성된 카드들:")
    print("-" * 60)
    for i, card in enumerate(result['cards'], 1):
        print(f"{i}. [{card['name']}]")
        print(f"   카테고리: {card['category']}")
        print(f"   값: {card['value']}")
        print(f"   가중치: {card['weight']:.2f}")
        if card['trade_offs']:
            print(f"   트레이드오프:")
            for to in card['trade_offs']:
                print(f"     - {to['dimension']}: {to['value']:+.2f}")
        print(f"   출처: \"{card['source']}\"")
        print()

    print("=" * 60)


if __name__ == "__main__":
    demo()
