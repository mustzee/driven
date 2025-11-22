import React, { useState } from 'react';
import './DecisionFramework.css';

/**
 * DecisionFramework 컴포넌트
 *
 * 합리적 의사결정을 지원하는 프레임워크
 * - Gap Analysis: 부족한 데이터 식별
 * - Data Collection Roadmap: 데이터 수집 우선순위
 * - Trade-off Matrix: 선택지 간 비교
 */
const DecisionFramework = ({ currentCards = [], onAddCard }) => {
  const [goal, setGoal] = useState('');
  const [options, setOptions] = useState(['', '', '']);
  const [category, setCategory] = useState('strategy');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const categories = [
    { value: 'food', label: '🍽️ 음식/식사' },
    { value: 'product', label: '🛒 제품 구매' },
    { value: 'hiring', label: '👔 채용' },
    { value: 'investment', label: '💰 투자' },
    { value: 'strategy', label: '🎯 전략/프로젝트' },
  ];

  const handleOptionChange = (index, value) => {
    const newOptions = [...options];
    newOptions[index] = value;
    setOptions(newOptions);
  };

  const addOption = () => {
    setOptions([...options, '']);
  };

  const removeOption = (index) => {
    if (options.length > 2) {
      const newOptions = options.filter((_, i) => i !== index);
      setOptions(newOptions);
    }
  };

  const analyzeDecision = async () => {
    // 유효성 검사
    const validOptions = options.filter(opt => opt.trim() !== '');

    if (!goal.trim()) {
      setError('결정하려는 목표를 입력해주세요.');
      return;
    }

    if (validOptions.length < 2) {
      setError('최소 2개 이상의 선택지를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8080/api/v1/decision/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal: goal,
          options: validOptions,
          current_cards: currentCards,
          category: category,
        }),
      });

      if (!response.ok) {
        throw new Error('분석 요청 실패');
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError('분석 중 오류가 발생했습니다: ' + err.message);
      console.error('Decision analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadge = (confidence) => {
    if (!confidence) return null;

    const { level, score } = confidence;
    const colors = {
      high: '#10b981',
      medium: '#f59e0b',
      low: '#ef4444',
    };

    return (
      <div className="confidence-badge" style={{ backgroundColor: colors[level] }}>
        신뢰도 {score}%
      </div>
    );
  };

  const getPriorityIcon = (priority) => {
    if (priority.includes('High')) return '🔴';
    if (priority.includes('Medium')) return '🟡';
    return '🟢';
  };

  return (
    <div className="decision-framework">
      <div className="framework-header">
        <h2>🧠 Decision Framework</h2>
        <p>선택장애 해결 도우미 - 어떤 데이터를 모으면 합리적 결정이 가능한지 안내합니다</p>
      </div>

      <div className="framework-input">
        <div className="input-group">
          <label>결정하려는 목표 (Goal)</label>
          <input
            type="text"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="예: 점심 메뉴를 선택하려고 합니다. 맛과 시간이 중요합니다."
            className="goal-input"
          />
        </div>

        <div className="input-group">
          <label>카테고리</label>
          <select value={category} onChange={(e) => setCategory(e.target.value)} className="category-select">
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        <div className="input-group">
          <label>선택지들 (Options)</label>
          {options.map((option, index) => (
            <div key={index} className="option-row">
              <input
                type="text"
                value={option}
                onChange={(e) => handleOptionChange(index, e.target.value)}
                placeholder={`선택지 ${index + 1}`}
                className="option-input"
              />
              {options.length > 2 && (
                <button onClick={() => removeOption(index)} className="remove-btn">
                  ✕
                </button>
              )}
            </div>
          ))}
          <button onClick={addOption} className="add-option-btn">
            + 선택지 추가
          </button>
        </div>

        {currentCards && currentCards.length > 0 && (
          <div className="current-data-info">
            📊 현재 {currentCards.length}개의 카드 데이터가 분석에 사용됩니다
          </div>
        )}

        <button
          onClick={analyzeDecision}
          disabled={loading}
          className="analyze-btn"
        >
          {loading ? '분석 중...' : '🔍 분석 시작'}
        </button>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}
      </div>

      {analysis && (
        <div className="framework-results">
          {/* 전체 요약 */}
          <div className="result-summary">
            <h3>📋 분석 요약</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="label">목표</span>
                <span className="value">{analysis.goal}</span>
              </div>
              <div className="summary-item">
                <span className="label">선택지</span>
                <span className="value">{analysis.options.join(', ')}</span>
              </div>
              <div className="summary-item">
                <span className="label">평가 차원</span>
                <span className="value">{analysis.dimensions.length}개</span>
              </div>
              <div className="summary-item">
                <span className="label">신뢰도</span>
                {getConfidenceBadge(analysis.tradeoff?.confidence)}
              </div>
            </div>
          </div>

          {/* 최종 추천 */}
          <div className="recommendation-box">
            <h3>💡 추천</h3>
            <p className="recommendation-text">{analysis.recommendation}</p>
          </div>

          {/* Data Collection Roadmap */}
          {analysis.roadmap && (
            <div className="roadmap-section">
              <h3>🗺️ 데이터 수집 로드맵</h3>

              <div className="completeness-bar">
                <div className="completeness-label">
                  완성도: {analysis.roadmap.completeness}%
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${analysis.roadmap.completeness}%` }}
                  />
                </div>
                {analysis.roadmap.status === 'incomplete' && (
                  <div className="missing-info">
                    📌 {analysis.roadmap.missing_dimensions}개 차원의 데이터가 부족합니다
                    (예상 수집 시간: {analysis.roadmap.estimated_total_time}분)
                  </div>
                )}
              </div>

              {analysis.roadmap.steps && analysis.roadmap.steps.length > 0 && (
                <div className="roadmap-steps">
                  {analysis.roadmap.steps.map((step) => (
                    <div key={step.step} className="roadmap-step">
                      <div className="step-header">
                        <span className="step-number">Step {step.step}</span>
                        <span className="step-priority">{getPriorityIcon(step.priority)} {step.priority}</span>
                        <span className="step-time">⏱️ {step.estimated_time}분</span>
                      </div>
                      <div className="step-dimension">{step.dimension}</div>
                      <div className="step-suggestion">{step.suggestion}</div>
                      <div className="step-meta">
                        <span>중요도: {(step.impact * 100).toFixed(0)}%</span>
                        <span>난이도: {step.difficulty}</span>
                        <span>ROI: {step.priority_score.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Gap Analysis */}
          {analysis.gaps && analysis.gaps.length > 0 && (
            <div className="gaps-section">
              <h3>📊 Gap Analysis (부족한 데이터)</h3>
              <div className="gaps-grid">
                {analysis.gaps.map((gap, index) => (
                  <div key={index} className="gap-card">
                    <div className="gap-dimension">{gap.dimension}</div>
                    <div className="gap-metrics">
                      <span className="gap-impact">
                        중요도: {(gap.impact * 100).toFixed(0)}%
                      </span>
                      <span className="gap-difficulty">
                        난이도: {gap.difficulty}
                      </span>
                    </div>
                    <div className="gap-priority">
                      우선순위: {gap.priority.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trade-off Matrix */}
          {analysis.tradeoff && (
            <div className="tradeoff-section">
              <h3>⚖️ Trade-off Matrix</h3>

              {/* 선택지별 요약 */}
              {analysis.tradeoff.summaries && (
                <div className="summaries-grid">
                  {analysis.tradeoff.summaries.map((summary, index) => (
                    <div key={index} className="summary-card">
                      <div className="summary-header">
                        <h4>{summary.name}</h4>
                        <div className="summary-score">{summary.total_score}점</div>
                      </div>

                      <div className="coverage-info">
                        데이터 커버리지: {(summary.data_coverage * 100).toFixed(0)}%
                      </div>

                      {summary.strengths && summary.strengths.length > 0 && (
                        <div className="strengths">
                          <strong>💪 강점</strong>
                          <ul>
                            {summary.strengths.map((str, i) => (
                              <li key={i}>{str}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {summary.weaknesses && summary.weaknesses.length > 0 && (
                        <div className="weaknesses">
                          <strong>⚠️ 약점</strong>
                          <ul>
                            {summary.weaknesses.map((weak, i) => (
                              <li key={i}>{weak}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Rankings */}
              {analysis.tradeoff.rankings && (
                <div className="rankings">
                  <h4>📊 종합 랭킹</h4>
                  <div className="ranking-bars">
                    {Object.entries(analysis.tradeoff.rankings)
                      .sort((a, b) => b[1] - a[1])
                      .map(([option, score], index) => (
                        <div key={option} className="ranking-item">
                          <span className="rank-position">#{index + 1}</span>
                          <span className="rank-name">{option}</span>
                          <div className="rank-bar">
                            <div
                              className="rank-fill"
                              style={{
                                width: `${score}%`,
                                backgroundColor: index === 0 ? '#667eea' : '#a0aec0'
                              }}
                            />
                          </div>
                          <span className="rank-score">{score}점</span>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Comparisons */}
              {analysis.tradeoff.comparisons && analysis.tradeoff.comparisons.length > 0 && (
                <div className="comparisons">
                  <h4>🔀 선택지 간 비교</h4>
                  {analysis.tradeoff.comparisons.map((comp, index) => (
                    <div key={index} className="comparison-card">
                      <div className="comparison-header">
                        <span className="comp-option">{comp.option1}</span>
                        <span className="vs">vs</span>
                        <span className="comp-option">{comp.option2}</span>
                      </div>

                      <div className="comparison-details">
                        {comp.option1_advantages && comp.option1_advantages.length > 0 && (
                          <div className="advantages">
                            <strong>{comp.option1}의 우위:</strong>
                            <ul>
                              {comp.option1_advantages.map((adv, i) => (
                                <li key={i}>
                                  {adv.dimension}: +{adv.advantage}%
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {comp.option2_advantages && comp.option2_advantages.length > 0 && (
                          <div className="advantages">
                            <strong>{comp.option2}의 우위:</strong>
                            <ul>
                              {comp.option2_advantages.map((adv, i) => (
                                <li key={i}>
                                  {adv.dimension}: +{adv.advantage}%
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Confidence Details */}
              {analysis.tradeoff.confidence && (
                <div className="confidence-details">
                  <h4>🎯 신뢰도 상세</h4>
                  <p>{analysis.tradeoff.confidence.message}</p>
                  <div className="confidence-metrics">
                    <div className="metric">
                      <span className="metric-label">전체 신뢰도</span>
                      <span className="metric-value">{analysis.tradeoff.confidence.score}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">데이터 커버리지</span>
                      <span className="metric-value">{analysis.tradeoff.confidence.coverage}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">데이터 품질</span>
                      <span className="metric-value">{analysis.tradeoff.confidence.quality}%</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DecisionFramework;
