package card

// TradeOff 트레이드오프 차원 (양극단 사이의 성향)
type TradeOff struct {
	Dimension string  `json:"dimension"` // 예: "정적-동적", "이성-감성"
	Value     float64 `json:"value"`     // -1.0 ~ 1.0 (-1: 왼쪽 극단, +1: 오른쪽 극단)
}

// Card 의사결정에 필요한 하나의 정보/요소
type Card struct {
	ID          string      `json:"id"`
	Name        string      `json:"name"`
	Category    string      `json:"category"`    // 예: "생리적", "경제적", "사회적"
	Value       interface{} `json:"value"`       // 카드의 실제 데이터
	Weight      float64     `json:"weight"`      // 중요도 (0.0 ~ 1.0)
	TradeOffs   []TradeOff  `json:"trade_offs"`  // 이 카드가 가진 성향들
	Description string      `json:"description"` // 설명
	DataSource  string      `json:"data_source"` // 데이터 출처
}

// Option 선택 가능한 옵션 (예: 식당 A, B, C)
type Option struct {
	ID         string                 `json:"id"`
	Name       string                 `json:"name"`
	Attributes map[string]interface{} `json:"attributes"` // 이 옵션의 속성들
	Tags       []string               `json:"tags"`       // 특성 태그
	Score      float64                `json:"score"`      // 계산된 점수
}

// ConflictResult 상충도 분석 결과
type ConflictResult struct {
	OptionA      string  `json:"option_a"`
	OptionB      string  `json:"option_b"`
	ConflictRate float64 `json:"conflict_rate"` // 0.0 ~ 1.0
	Reason       string  `json:"reason"`        // 상충 이유
}

// NewCard 카드 생성 헬퍼
func NewCard(id, name, category string, value interface{}, weight float64) *Card {
	return &Card{
		ID:        id,
		Name:      name,
		Category:  category,
		Value:     value,
		Weight:    weight,
		TradeOffs: make([]TradeOff, 0),
	}
}

// AddTradeOff 트레이드오프 추가
func (c *Card) AddTradeOff(dimension string, value float64) {
	// value를 -1.0 ~ 1.0 범위로 제한
	if value < -1.0 {
		value = -1.0
	}
	if value > 1.0 {
		value = 1.0
	}

	c.TradeOffs = append(c.TradeOffs, TradeOff{
		Dimension: dimension,
		Value:     value,
	})
}
