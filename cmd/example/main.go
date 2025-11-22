package main

import (
	"encoding/json"
	"fmt"

	"github.com/mustzee/driven/internal/card"
)

func main() {
	fmt.Println("🎴 Cognitive Deck - Go Implementation")
	fmt.Println("=" + repeat("=", 59))
	fmt.Println()

	// ============================================
	// 덱 생성 (Miller's Law: 7±2)
	// ============================================
	deck := card.NewDeck("lunch-001", "만족스러운 점심 선택", card.OptimalDeckSize)

	fmt.Printf("📋 목표: %s\n", deck.Goal)
	fmt.Printf("   최대 슬롯: %d개 (인지 한계)\n\n", deck.MaxSlots)

	// ============================================
	// 카드 추가
	// ============================================
	fmt.Println("🃏 카드 추가 중...")

	// 1. 배고픔 카드
	hungerCard := card.NewCard("hunger", "배고픔", "생리적", 80, 0.9)
	hungerCard.AddTradeOff("정적-동적", 0.7)  // 동적
	hungerCard.AddTradeOff("이성-감성", 0.5) // 이성적
	deck.AddCard(hungerCard)

	// 2. 예산 카드
	budgetCard := card.NewCard("budget", "예산", "경제적", 12000, 0.7)
	budgetCard.AddTradeOff("정적-동적", -0.6) // 정적
	budgetCard.AddTradeOff("이성-감성", 0.8)  // 이성적
	deck.AddCard(budgetCard)

	// 3. 시간 카드
	timeCard := card.NewCard("time", "시간제약", "제약적", 30, 0.8)
	timeCard.AddTradeOff("정적-동적", 0.5)  // 동적
	timeCard.AddTradeOff("이성-감성", 0.6) // 이성적
	deck.AddCard(timeCard)

	// 4. 동행자 카드
	companionCard := card.NewCard("companion", "동행자", "사회적", 3, 0.6)
	companionCard.AddTradeOff("정적-동적", -0.3) // 정적
	companionCard.AddTradeOff("이성-감성", -0.7) // 감성적
	deck.AddCard(companionCard)

	// 5. 모험성향 카드
	adventureCard := card.NewCard("adventure", "모험성향", "성향", 0.3, 0.4)
	adventureCard.AddTradeOff("정적-동적", 0.9)  // 동적
	adventureCard.AddTradeOff("이성-감성", -0.4) // 감성적
	deck.AddCard(adventureCard)

	// 6. 날씨 카드
	weatherCard := card.NewCard("weather", "날씨", "외부환경", "비", 0.5)
	weatherCard.AddTradeOff("정적-동적", -0.5) // 정적
	weatherCard.AddTradeOff("이성-감성", 0.3)  // 이성적
	deck.AddCard(weatherCard)

	// 7. 거리 카드
	distanceCard := card.NewCard("distance", "거리", "제약적", 500, 0.7)
	distanceCard.AddTradeOff("정적-동적", -0.4) // 정적
	distanceCard.AddTradeOff("이성-감성", 0.5)  // 이성적
	deck.AddCard(distanceCard)

	fmt.Printf("   추가된 카드: %d/%d\n", len(deck.Cards), deck.MaxSlots)
	fmt.Printf("   남은 슬롯: %d\n\n", deck.AvailableSlots())

	// ============================================
	// 현재 덱 상태 출력
	// ============================================
	fmt.Println("📊 현재 덱 구성:")
	fmt.Println("   " + repeat("-", 56))

	for i, c := range deck.Cards {
		fmt.Printf("   %d. [%s] %v (가중치: %.1f, %s)\n",
			i+1, c.Name, c.Value, c.Weight, c.Category)
	}
	fmt.Println()

	// ============================================
	// 게이지 계산
	// ============================================
	fmt.Println("📈 덱의 전체 성향 게이지:")
	fmt.Println("   " + repeat("-", 56))

	gauges := deck.CalculateGauges()
	for _, g := range gauges {
		fmt.Printf("   %s: %s (%.2f)\n", g.Dimension, g.Label, g.Value)
	}
	fmt.Println()

	// ============================================
	// 가중치 순 정렬
	// ============================================
	fmt.Println("🎯 중요도 순위 (Top 5):")
	fmt.Println("   " + repeat("-", 56))

	topCards := deck.GetTopCards(5)
	for i, c := range topCards {
		bar := repeat("█", int(c.Weight*20))
		fmt.Printf("   %d. %s %.1f %s\n", i+1, c.Name, c.Weight, bar)
	}
	fmt.Println()

	// ============================================
	// JSON 출력 (Python과 연동용)
	// ============================================
	fmt.Println("📦 JSON 출력 (Python 연동용):")
	fmt.Println("   " + repeat("-", 56))

	deckJSON, err := json.MarshalIndent(deck, "   ", "  ")
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
		return
	}
	fmt.Printf("%s\n", deckJSON)

	fmt.Println()
	fmt.Println("=" + repeat("=", 59))
}

func repeat(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}
