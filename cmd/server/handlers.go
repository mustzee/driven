package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os/exec"

	"github.com/gin-gonic/gin"
)

// optimizeCards 카드 최적화
func optimizeCards(c *gin.Context) {
	var req struct {
		Cards            []map[string]interface{} `json:"cards" binding:"required"`
		MaxCards         int                      `json:"max_cards"`
		RemoveDuplicates bool                     `json:"remove_duplicates"`
		RemoveNoise      bool                     `json:"remove_noise"`
		TrimToLimit      bool                     `json:"trim_to_limit"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 기본값 설정
	if req.MaxCards == 0 {
		req.MaxCards = 7
	}

	result, err := runPythonOptimize(req.Cards, req.MaxCards, req.RemoveDuplicates, req.RemoveNoise, req.TrimToLimit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

// runPythonOptimize Python 카드 최적화 실행
func runPythonOptimize(cards []map[string]interface{}, maxCards int, removeDuplicates, removeNoise, trimToLimit bool) (map[string]interface{}, error) {
	inputData := map[string]interface{}{
		"cards":             cards,
		"max_cards":         maxCards,
		"remove_duplicates": removeDuplicates,
		"remove_noise":      removeNoise,
		"trim_to_limit":     trimToLimit,
	}

	inputJSON, err := json.Marshal(inputData)
	if err != nil {
		return nil, err
	}

	pythonScript := `
import sys
import json
sys.path.append('python')

from card_optimizer import optimize_cards

input_data = json.loads(sys.stdin.read())

result = optimize_cards(
    cards=input_data["cards"],
    max_cards=input_data["max_cards"],
    remove_duplicates=input_data["remove_duplicates"],
    remove_noise=input_data["remove_noise"],
    trim_to_limit=input_data["trim_to_limit"]
)

print(json.dumps(result, ensure_ascii=False))
`

	cmd := exec.Command("python3", "-c", pythonScript)
	cmd.Stdin = bytes.NewBufferString(string(inputJSON))

	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// listFrameworks 프레임워크 목록 조회
func listFrameworks(c *gin.Context) {
	result, err := runPythonListFrameworks()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

// runPythonListFrameworks Python 프레임워크 목록 조회
func runPythonListFrameworks() (map[string]interface{}, error) {
	pythonScript := `
import sys
import json
sys.path.append('python')

from decision_frameworks import FrameworkLibrary

frameworks = FrameworkLibrary.get_all_frameworks()

result = {
    "frameworks": [
        {
            "id": fw.id,
            "name": fw.name,
            "description": fw.description,
            "category": fw.category,
            "dimensions": len(fw.dimensions),
            "questions": len(fw.questions)
        }
        for fw in frameworks
    ]
}

print(json.dumps(result, ensure_ascii=False))
`

	cmd := exec.Command("python3", "-c", pythonScript)

	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// getFramework 특정 프레임워크 상세 조회
func getFramework(c *gin.Context) {
	frameworkID := c.Param("id")

	result, err := runPythonGetFramework(frameworkID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if result == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Framework not found"})
		return
	}

	c.JSON(http.StatusOK, result)
}

// runPythonGetFramework Python 프레임워크 상세 조회
func runPythonGetFramework(frameworkID string) (map[string]interface{}, error) {
	pythonScript := `
import sys
import json
sys.path.append('python')

from decision_frameworks import FrameworkLibrary

framework = FrameworkLibrary.get_framework_by_id("` + frameworkID + `")

if framework:
    result = {
        "id": framework.id,
        "name": framework.name,
        "description": framework.description,
        "category": framework.category,
        "pros": framework.pros,
        "cons": framework.cons,
        "when_to_use": framework.when_to_use,
        "when_not_to_use": framework.when_not_to_use,
        "required_cards": framework.required_cards,
        "card_template": framework.card_template,
        "dimensions": [
            {
                "name": dim.name,
                "description": dim.description,
                "weight": dim.weight,
                "scoring_guide": dim.scoring_guide
            }
            for dim in framework.dimensions
        ],
        "questions": framework.questions,
        "analysis_method": framework.analysis_method
    }
    print(json.dumps(result, ensure_ascii=False))
else:
    print("null")
`

	cmd := exec.Command("python3", "-c", pythonScript)

	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// runDeepAnalysis 심층 분석 실행
func runDeepAnalysis(c *gin.Context) {
	var req struct {
		OptionName string                 `json:"option_name" binding:"required"`
		BaseData   map[string]interface{} `json:"base_data" binding:"required"`
		Category   string                 `json:"category"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.Category == "" {
		req.Category = "strategy"
	}

	result, err := runPythonDeepAnalysis(req.OptionName, req.BaseData, req.Category)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

// runPythonDeepAnalysis Python 심층 분석 실행
func runPythonDeepAnalysis(optionName string, baseData map[string]interface{}, category string) (map[string]interface{}, error) {
	inputData := map[string]interface{}{
		"option_name": optionName,
		"base_data":   baseData,
		"category":    category,
	}

	inputJSON, err := json.Marshal(inputData)
	if err != nil {
		return nil, err
	}

	pythonScript := `
import sys
import json
sys.path.append('python')

from deep_decision_analysis import DeepDecisionAnalyzer

input_data = json.loads(sys.stdin.read())

# Convert base_data values to float
base_data_float = {}
for key, value in input_data["base_data"].items():
    try:
        base_data_float[key] = float(value)
    except:
        base_data_float[key] = 0.0

analyzer = DeepDecisionAnalyzer(
    input_data["option_name"],
    base_data_float,
    input_data["category"]
)

result = analyzer.run_full_analysis()
print(json.dumps(result, ensure_ascii=False))
`

	cmd := exec.Command("python3", "-c", pythonScript)
	cmd.Stdin = bytes.NewBufferString(string(inputJSON))

	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// System 관련 핸들러는 간략히 구현 (실제로는 별도 파일로 분리 권장)

// createDecision 새 의사결정 생성
func createDecision(c *gin.Context) {
	var req struct {
		Title    string   `json:"title" binding:"required"`
		Goal     string   `json:"goal" binding:"required"`
		Options  []string `json:"options" binding:"required"`
		Category string   `json:"category"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Python 시스템 호출 (간략히 구현)
	c.JSON(http.StatusOK, gin.H{
		"message": "의사결정이 생성되었습니다",
		"title":   req.Title,
	})
}

// 나머지 시스템 핸들러들은 추후 구현 (Placeholder)
func listDecisions(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"decisions": []interface{}{}})
}

func getDecision(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"id": c.Param("id")})
}

func addCardsToDecision(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "Cards added"})
}

func selectFramework(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "Framework selected"})
}

func analyzeDecisionSystem(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "Analysis complete"})
}

func makeDecision(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "Decision made"})
}

func getInsights(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"total_decisions": 0,
		"completed":       0,
	})
}
