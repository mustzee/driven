package card

import (
	"errors"
	"sort"
)

const (
	// MillersLaw 인간이 동시에 처리할 수 있는 정보의 개수 (Miller's Law)
	MinDeckSize = 5
	MaxDeckSize = 9
	OptimalDeckSize = 7
)

// Deck 카드들의 집합 (제한된 인지 용량)
type Deck struct {
	ID       string  `json:"id"`
	Goal     string  `json:"goal"`      // 이 덱의 목표
	MaxSlots int     `json:"max_slots"` // 최대 카드 수
	Cards    []*Card `json:"cards"`     // 현재 활성화된 카드들
}

// Gauge 전체 덱의 성향 게이지
type Gauge struct {
	Dimension string  `json:"dimension"`
	Value     float64 `json:"value"`     // -1.0 ~ 1.0
	Label     string  `json:"label"`     // 시각화용 레이블
}

// NewDeck 새로운 덱 생성
func NewDeck(id, goal string, maxSlots int) *Deck {
	if maxSlots < MinDeckSize {
		maxSlots = MinDeckSize
	}
	if maxSlots > MaxDeckSize {
		maxSlots = MaxDeckSize
	}

	return &Deck{
		ID:       id,
		Goal:     goal,
		MaxSlots: maxSlots,
		Cards:    make([]*Card, 0, maxSlots),
	}
}

// AddCard 카드를 덱에 추가
func (d *Deck) AddCard(card *Card) error {
	if len(d.Cards) >= d.MaxSlots {
		return errors.New("deck is full - cognitive load limit reached")
	}

	d.Cards = append(d.Cards, card)
	return nil
}

// RemoveCard 카드를 덱에서 제거
func (d *Deck) RemoveCard(cardID string) error {
	for i, card := range d.Cards {
		if card.ID == cardID {
			d.Cards = append(d.Cards[:i], d.Cards[i+1:]...)
			return nil
		}
	}
	return errors.New("card not found")
}

// IsFull 덱이 가득 찼는지 확인
func (d *Deck) IsFull() bool {
	return len(d.Cards) >= d.MaxSlots
}

// AvailableSlots 남은 슬롯 수
func (d *Deck) AvailableSlots() int {
	return d.MaxSlots - len(d.Cards)
}

// CalculateGauges 덱의 전체적인 성향 게이지 계산
func (d *Deck) CalculateGauges() []Gauge {
	// 모든 차원 수집
	dimensionSums := make(map[string]float64)
	dimensionCounts := make(map[string]int)

	for _, card := range d.Cards {
		for _, tradeOff := range card.TradeOffs {
			// 가중치를 적용한 값
			weightedValue := tradeOff.Value * card.Weight
			dimensionSums[tradeOff.Dimension] += weightedValue
			dimensionCounts[tradeOff.Dimension]++
		}
	}

	// 평균 계산
	gauges := make([]Gauge, 0, len(dimensionSums))
	for dimension, sum := range dimensionSums {
		count := dimensionCounts[dimension]
		avgValue := sum / float64(count)

		gauges = append(gauges, Gauge{
			Dimension: dimension,
			Value:     avgValue,
			Label:     formatGaugeLabel(dimension, avgValue),
		})
	}

	return gauges
}

// SortCardsByWeight 가중치 순으로 카드 정렬
func (d *Deck) SortCardsByWeight() {
	sort.Slice(d.Cards, func(i, j int) bool {
		return d.Cards[i].Weight > d.Cards[j].Weight
	})
}

// GetTopCards 상위 N개 카드 반환
func (d *Deck) GetTopCards(n int) []*Card {
	d.SortCardsByWeight()

	if n > len(d.Cards) {
		n = len(d.Cards)
	}

	return d.Cards[:n]
}

// formatGaugeLabel 게이지 시각화용 레이블 생성
func formatGaugeLabel(dimension string, value float64) string {
	// value: -1.0 (왼쪽) ~ 0.0 (중립) ~ 1.0 (오른쪽)
	bars := 10
	position := int((value + 1.0) / 2.0 * float64(bars))

	if position < 0 {
		position = 0
	}
	if position > bars {
		position = bars
	}

	visual := ""
	for i := 0; i < bars; i++ {
		if i == position {
			visual += "█"
		} else {
			visual += "░"
		}
	}

	return visual
}
