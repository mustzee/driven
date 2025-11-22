package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os/exec"

	"github.com/gin-gonic/gin"
)

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
	// Python 스크립트 경로
	pythonScript := `
import sys
import json
sys.path.append('python')

from graph_analyzer_lite import analyze_meeting_notes

text = sys.stdin.read()
result = analyze_meeting_notes(text, max_cards=` + string(rune(maxCards+48)) + `)
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
