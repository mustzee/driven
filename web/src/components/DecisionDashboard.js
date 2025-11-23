import React, { useState, useEffect } from 'react';
import './DecisionDashboard.css';

/**
 * Decision Dashboard - 통합 의사결정 대시보드
 *
 * 카드 최적화, 프레임워크 선택, 심층 분석을 한 곳에서
 */
const DecisionDashboard = ({ currentCards, onOptimizedCards }) => {
  const [activeTab, setActiveTab] = useState('optimize'); // optimize, frameworks, deep-analysis
  const [loading, setLoading] = useState(false);

  // 카드 최적화 상태
  const [optimizeResult, setOptimizeResult] = useState(null);

  // 프레임워크 상태
  const [frameworks, setFrameworks] = useState([]);
  const [selectedFramework, setSelectedFramework] = useState(null);

  // 심층 분석 상태
  const [deepAnalysisInput, setDeepAnalysisInput] = useState({
    optionName: '',
    baseData: {}
  });
  const [deepAnalysisResult, setDeepAnalysisResult] = useState(null);

  // 프레임워크 목록 로드
  useEffect(() => {
    loadFrameworks();
  }, []);

  const loadFrameworks = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/frameworks');
      const data = await response.json();
      setFrameworks(data.frameworks || []);
    } catch (error) {
      console.error('Failed to load frameworks:', error);
    }
  };

  // 카드 최적화 실행
  const handleOptimizeCards = async () => {
    if (!currentCards || currentCards.length === 0) {
      alert('최적화할 카드가 없습니다.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/v1/cards/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cards: currentCards,
          max_cards: 7,
          remove_duplicates: true,
          remove_noise: true,
          trim_to_limit: true,
        }),
      });

      const data = await response.json();
      setOptimizeResult(data);

      // 부모 컴포넌트에 최적화된 카드 전달
      if (onOptimizedCards && data.optimized_cards) {
        onOptimizedCards(data.optimized_cards);
      }
    } catch (error) {
      console.error('Optimization error:', error);
      alert('최적화 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 프레임워크 선택
  const handleSelectFramework = async (frameworkId) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8080/api/v1/frameworks/${frameworkId}`);
      const data = await response.json();
      setSelectedFramework(data);
    } catch (error) {
      console.error('Framework load error:', error);
    } finally {
      setLoading(false);
    }
  };

  // 심층 분석 실행
  const handleDeepAnalysis = async () => {
    if (!deepAnalysisInput.optionName) {
      alert('옵션 이름을 입력하세요.');
      return;
    }

    if (Object.keys(deepAnalysisInput.baseData).length === 0) {
      alert('기본 데이터를 입력하세요 (예: 효과, 비용 등)');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/v1/deep-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          option_name: deepAnalysisInput.optionName,
          base_data: deepAnalysisInput.baseData,
          category: 'strategy',
        }),
      });

      const data = await response.json();
      setDeepAnalysisResult(data);
    } catch (error) {
      console.error('Deep analysis error:', error);
      alert('심층 분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="decision-dashboard">
      <div className="dashboard-header">
        <h2>🎯 통합 의사결정 대시보드</h2>
        <p>카드 최적화, 프레임워크 선택, 심층 분석을 한 곳에서</p>
      </div>

      {/* 탭 메뉴 */}
      <div className="dashboard-tabs">
        <button
          className={`tab-btn ${activeTab === 'optimize' ? 'active' : ''}`}
          onClick={() => setActiveTab('optimize')}
        >
          🔧 카드 최적화
        </button>
        <button
          className={`tab-btn ${activeTab === 'frameworks' ? 'active' : ''}`}
          onClick={() => setActiveTab('frameworks')}
        >
          📋 프레임워크
        </button>
        <button
          className={`tab-btn ${activeTab === 'deep-analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('deep-analysis')}
        >
          🔬 심층 분석
        </button>
      </div>

      {/* 탭 내용 */}
      <div className="dashboard-content">
        {/* 카드 최적화 */}
        {activeTab === 'optimize' && (
          <div className="optimize-section">
            <h3>스마트 카드 최적화</h3>
            <p>중복, 노이즈 제거 및 Miller's Law (7±2) 적용</p>

            <div className="current-status">
              <div className="status-item">
                <span className="label">현재 카드 수:</span>
                <span className="value">{currentCards?.length || 0}개</span>
              </div>
            </div>

            <button
              onClick={handleOptimizeCards}
              disabled={loading || !currentCards || currentCards.length === 0}
              className="optimize-btn"
            >
              {loading ? '최적화 중...' : '🔧 카드 최적화 실행'}
            </button>

            {optimizeResult && (
              <div className="optimize-result">
                <h4>✅ 최적화 완료</h4>
                <div className="stats-grid">
                  <div className="stat">
                    <span className="stat-label">원본 카드</span>
                    <span className="stat-value">{optimizeResult.stats.original_count}개</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">중복 제거</span>
                    <span className="stat-value removed">-{optimizeResult.stats.duplicates_removed}개</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">노이즈 제거</span>
                    <span className="stat-value removed">-{optimizeResult.stats.noise_removed}개</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">최종 카드</span>
                    <span className="stat-value final">{optimizeResult.stats.final_count}개</span>
                  </div>
                </div>

                {optimizeResult.summary && (
                  <div className="optimize-summary">
                    <h5>상세 내역:</h5>
                    <pre>{optimizeResult.summary}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 프레임워크 선택 */}
        {activeTab === 'frameworks' && (
          <div className="frameworks-section">
            <h3>의사결정 프레임워크 라이브러리</h3>
            <p>검증된 비즈니스 프레임워크 7개</p>

            <div className="frameworks-grid">
              {frameworks.map((fw) => (
                <div
                  key={fw.id}
                  className={`framework-card ${selectedFramework?.id === fw.id ? 'selected' : ''}`}
                  onClick={() => handleSelectFramework(fw.id)}
                >
                  <h4>{fw.name}</h4>
                  <p className="fw-description">{fw.description}</p>
                  <div className="fw-meta">
                    <span className="fw-category">{fw.category}</span>
                    <span className="fw-dimensions">{fw.dimensions}개 차원</span>
                  </div>
                </div>
              ))}
            </div>

            {selectedFramework && (
              <div className="framework-detail">
                <h4>📋 {selectedFramework.name}</h4>
                <p>{selectedFramework.description}</p>

                <div className="dimensions-list">
                  <h5>평가 차원:</h5>
                  {selectedFramework.dimensions?.map((dim, index) => (
                    <div key={index} className="dimension-item">
                      <div className="dim-header">
                        <span className="dim-name">{dim.name}</span>
                        <span className="dim-weight">가중치: {dim.weight}</span>
                      </div>
                      <p className="dim-description">{dim.description}</p>
                      {dim.scoring_guide && Object.keys(dim.scoring_guide).length > 0 && (
                        <div className="scoring-guide">
                          {Object.entries(dim.scoring_guide).map(([level, desc]) => (
                            <div key={level} className="guide-item">
                              <span className="level">{level}:</span>
                              <span className="desc">{desc}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 심층 분석 */}
        {activeTab === 'deep-analysis' && (
          <div className="deep-analysis-section">
            <h3>심층 의사결정 분석</h3>
            <p>시나리오, 리스크, 민감도 분석</p>

            <div className="analysis-input">
              <div className="input-group">
                <label>옵션 이름</label>
                <input
                  type="text"
                  value={deepAnalysisInput.optionName}
                  onChange={(e) => setDeepAnalysisInput({...deepAnalysisInput, optionName: e.target.value})}
                  placeholder="예: 공격적 마케팅"
                />
              </div>

              <div className="input-group">
                <label>기본 데이터 (JSON 형식)</label>
                <textarea
                  value={JSON.stringify(deepAnalysisInput.baseData, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value);
                      setDeepAnalysisInput({...deepAnalysisInput, baseData: parsed});
                    } catch (err) {
                      // Invalid JSON - ignore
                    }
                  }}
                  placeholder={'{\n  "효과": 85,\n  "비용": 500,\n  "시간": 3\n}'}
                  rows={8}
                />
              </div>

              <button
                onClick={handleDeepAnalysis}
                disabled={loading}
                className="analyze-btn"
              >
                {loading ? '분석 중...' : '🔬 심층 분석 실행'}
              </button>
            </div>

            {deepAnalysisResult && (
              <div className="analysis-result">
                <h4>✅ 분석 완료: {deepAnalysisResult.option}</h4>

                {/* 시나리오 분석 */}
                {deepAnalysisResult.scenario_analysis && (
                  <div className="scenario-section">
                    <h5>1️⃣ 시나리오 분석</h5>
                    {deepAnalysisResult.scenario_analysis.scenarios?.map((scenario, idx) => (
                      <div key={idx} className="scenario-item">
                        <div className="scenario-header">
                          <span className="scenario-type">{scenario.type.toUpperCase()}</span>
                          <span className="scenario-prob">{(scenario.probability * 100).toFixed(0)}% 확률</span>
                        </div>
                        <p>{scenario.description}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* 리스크 분석 */}
                {deepAnalysisResult.risk_analysis && (
                  <div className="risk-section">
                    <h5>2️⃣ 리스크 분석</h5>
                    <div className="risk-adjusted">
                      <span>리스크 조정 가치: </span>
                      <span className="value-strike">{deepAnalysisResult.risk_analysis.risk_adjusted?.base_value}</span>
                      {' → '}
                      <span className="value-adjusted">{deepAnalysisResult.risk_analysis.risk_adjusted?.risk_adjusted_value?.toFixed(1)}</span>
                    </div>
                    {deepAnalysisResult.risk_analysis.identified_risks?.slice(0, 3).map((risk, idx) => (
                      <div key={idx} className={`risk-item risk-${risk.level}`}>
                        <div className="risk-header">
                          <span className="risk-name">⚠️ {risk.name}</span>
                          <span className="risk-level">[{risk.level.toUpperCase()}]</span>
                        </div>
                        <p className="risk-desc">{risk.description}</p>
                        <p className="risk-mitigation">💡 완화 전략: {risk.mitigation}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* 민감도 분석 */}
                {deepAnalysisResult.sensitivity_analysis && (
                  <div className="sensitivity-section">
                    <h5>3️⃣ 민감도 분석</h5>
                    <p className="sensitivity-recommendation">
                      {deepAnalysisResult.sensitivity_analysis.recommendation}
                    </p>
                    {deepAnalysisResult.sensitivity_analysis.top_sensitive_variables?.map((variable, idx) => (
                      <div key={idx} className="sensitive-var">
                        <div className="var-header">
                          <span className="var-name">📈 {variable.variable}</span>
                          <span className="var-coef">민감도: {variable.sensitivity_coefficient.toFixed(1)}%</span>
                        </div>
                        <div className="var-impact">{variable.impact_level}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* 종합 추천 */}
                {deepAnalysisResult.overall_recommendation && (
                  <div className="overall-recommendation">
                    <h5>💡 종합 추천</h5>
                    <p>{deepAnalysisResult.overall_recommendation}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DecisionDashboard;
