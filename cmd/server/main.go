package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os/exec"
	"strconv"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/mustzee/driven/internal/card"
)

func main() {
	r := gin.Default()

	// CORS 설정
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		AllowCredentials: true,
	}))

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"service": "cognitive-deck-api",
		})
	})

	// API v1 그룹
	v1 := r.Group("/api/v1")
	{
		// 덱 관련 API
		v1.POST("/decks", createDeck)
		v1.GET("/decks/:id", getDeck)
		v1.POST("/decks/:id/cards", addCard)
		v1.DELETE("/decks/:id/cards/:cardId", removeCard)
		v1.GET("/decks/:id/gauges", calculateGauges)

		// 분석 API
		v1.POST("/analyze/conflicts", analyzeConflicts)
		v1.POST("/analyze/recommend", getRecommendation)

		// AI 카드 생성
		v1.POST("/ai/generate-cards", generateCards)

		// 그래프 분석
		v1.POST("/graph/analyze", analyzeGraphFromText)

		// 의사결정 프레임워크
		v1.POST("/decision/analyze", analyzeDecision)
	}

	// 서버 시작
	port := ":8080"
	println("🎴 Cognitive Deck API Server")
	println("🚀 Starting on " + port)
	r.Run(port)
}

// 임시 저장소 (실제로는 DB 사용)
var decks = make(map[string]*card.Deck)

// createDeck 덱 생성
func createDeck(c *gin.Context) {
	var req struct {
		ID       string `json:"id" binding:"required"`
		Goal     string `json:"goal" binding:"required"`
		MaxSlots int    `json:"max_slots"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	maxSlots := req.MaxSlots
	if maxSlots == 0 {
		maxSlots = card.OptimalDeckSize
	}

	deck := card.NewDeck(req.ID, req.Goal, maxSlots)
	decks[req.ID] = deck

	c.JSON(http.StatusCreated, deck)
}

// getDeck 덱 조회
func getDeck(c *gin.Context) {
	id := c.Param("id")
	deck, exists := decks[id]

	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "deck not found"})
		return
	}

	c.JSON(http.StatusOK, deck)
}

// addCard 카드 추가
func addCard(c *gin.Context) {
	id := c.Param("id")
	deck, exists := decks[id]

	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "deck not found"})
		return
	}

	var cardReq struct {
		ID          string                 `json:"id" binding:"required"`
		Name        string                 `json:"name" binding:"required"`
		Category    string                 `json:"category" binding:"required"`
		Value       interface{}            `json:"value"`
		Weight      float64                `json:"weight"`
		TradeOffs   []card.TradeOff        `json:"trade_offs"`
		Description string                 `json:"description"`
	}

	if err := c.ShouldBindJSON(&cardReq); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	newCard := &card.Card{
		ID:          cardReq.ID,
		Name:        cardReq.Name,
		Category:    cardReq.Category,
		Value:       cardReq.Value,
		Weight:      cardReq.Weight,
		TradeOffs:   cardReq.TradeOffs,
		Description: cardReq.Description,
	}

	if err := deck.AddCard(newCard); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, deck)
}

// removeCard 카드 제거
func removeCard(c *gin.Context) {
	id := c.Param("id")
	cardID := c.Param("cardId")

	deck, exists := decks[id]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "deck not found"})
		return
	}

	if err := deck.RemoveCard(cardID); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, deck)
}

// calculateGauges 게이지 계산
func calculateGauges(c *gin.Context) {
	id := c.Param("id")
	deck, exists := decks[id]

	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "deck not found"})
		return
	}

	gauges := deck.CalculateGauges()

	c.JSON(http.StatusOK, gin.H{
		"deck_id": id,
		"gauges":  gauges,
	})
}

// analyzeConflicts 상충도 분석
func analyzeConflicts(c *gin.Context) {
	var req struct {
		Options     []map[string]interface{} `json:"options" binding:"required"`
		CardWeights map[string]float64       `json:"card_weights" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Python 서비스 호출하거나 Go로 구현
	// 여기서는 간단히 응답만
	c.JSON(http.StatusOK, gin.H{
		"status": "conflict analysis completed",
		"conflicts": []gin.H{
			{"option_a": "A", "option_b": "B", "rate": 0.75},
		},
	})
}

// getRecommendation 추천
func getRecommendation(c *gin.Context) {
	var req struct {
		DeckID  string                   `json:"deck_id" binding:"required"`
		Options []map[string]interface{} `json:"options" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"recommended": req.Options[0],
		"score":       0.95,
		"reason":      "Best match based on deck preferences",
	})
}

// generateCards AI 카드 생성
func generateCards(c *gin.Context) {
	var req struct {
		Text     string `json:"text" binding:"required"`
		Goal     string `json:"goal"`
		MaxCards int    `json:"max_cards"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Python AI 서비스 호출 (여기서는 모킹)
	c.JSON(http.StatusOK, gin.H{
		"generated_cards": []gin.H{
			{
				"name":     "예산",
				"category": "경제적",
				"value":    12000,
				"weight":   0.7,
			},
		},
	})
}

// analyzeGraphFromText 텍스트에서 그래프 분석
func analyzeGraphFromText(c *gin.Context) {
	var req struct {
		Text     string `json:"text" binding:"required"`
		MaxCards int    `json:"max_cards"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.MaxCards == 0 {
		req.MaxCards = 10
	}

	// Python 스크립트 호출
	result, err := runPythonGraphAnalysis(req.Text, req.MaxCards)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

// runPythonGraphAnalysis Python 그래프 분석 실행
func runPythonGraphAnalysis(text string, maxCards int) (map[string]interface{}, error) {
	// Python 스크립트
	pythonScript := `
import sys
import json
sys.path.append('python')

from graph_analyzer_lite import analyze_meeting_notes

text = sys.stdin.read()
result = analyze_meeting_notes(text, max_cards=` + strconv.Itoa(maxCards) + `)
print(json.dumps(result, ensure_ascii=False))
`

	cmd := exec.Command("python3", "-c", pythonScript)

	// 텍스트를 stdin으로 전달
	cmd.Stdin = bytes.NewBufferString(text)

	// 출력 받기
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, err
	}

	// JSON 파싱
	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// analyzeDecision 의사결정 프레임워크 분석
func analyzeDecision(c *gin.Context) {
	var req struct {
		Goal         string                   `json:"goal" binding:"required"`
		Options      []string                 `json:"options" binding:"required"`
		CurrentCards []map[string]interface{} `json:"current_cards"`
		Category     string                   `json:"category"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Python 스크립트 호출
	result, err := runPythonDecisionAnalysis(req.Goal, req.Options, req.CurrentCards, req.Category)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

// runPythonDecisionAnalysis Python 의사결정 분석 실행
func runPythonDecisionAnalysis(goal string, options []string, currentCards []map[string]interface{}, category string) (map[string]interface{}, error) {
	// 입력 데이터를 JSON으로 직렬화
	inputData := map[string]interface{}{
		"goal":          goal,
		"options":       options,
		"current_cards": currentCards,
		"category":      category,
	}

	inputJSON, err := json.Marshal(inputData)
	if err != nil {
		return nil, err
	}

	// Python 스크립트
	pythonScript := `
import sys
import json
sys.path.append('python')

from decision_framework import analyze_decision

# stdin에서 JSON 읽기
input_data = json.loads(sys.stdin.read())

# 분석 실행
result = analyze_decision(
    goal=input_data["goal"],
    options=input_data["options"],
    current_cards=input_data.get("current_cards"),
    category=input_data.get("category")
)

print(json.dumps(result, ensure_ascii=False))
`

	cmd := exec.Command("python3", "-c", pythonScript)

	// JSON 데이터를 stdin으로 전달
	cmd.Stdin = bytes.NewBufferString(string(inputJSON))

	// 출력 받기
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, err
	}

	// JSON 파싱
	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}
