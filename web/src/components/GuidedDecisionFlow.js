import React, { useState, useEffect } from 'react';
import './GuidedDecisionFlow.css';

/**
 * GuidedDecisionFlow - 완전 가이드형 의사결정 시스템 (Modern Monochrome)
 *
 * 5단계 워크플로우:
 * 1. 프레임워크 선택 (토글, How to Use)
 * 2. 프레임워크별 특화 UI (SWOT 4분할, Porter's 5 Forces 등)
 * 3. 카드 작성
 * 4. 자동 분석
 * 5. 결과 및 추천
 */
const GuidedDecisionFlow = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [frameworks, setFrameworks] = useState([]);
  const [selectedFramework, setSelectedFramework] = useState(null);
  const [cards, setCards] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // 프레임워크 상세 정보 토글 상태
  const [expandedFrameworks, setExpandedFrameworks] = useState({});

  useEffect(() => {
    loadFrameworks();
  }, []);

  const loadFrameworks = async () => {
    try {
      const response = await fetch('/api/v1/frameworks');
      const data = await response.json();
      setFrameworks(data.frameworks || []);
    } catch (error) {
      console.error('Failed to load frameworks:', error);
    }
  };

  const toggleFrameworkDetails = (frameworkId, e) => {
    e.stopPropagation(); // 카드 클릭 이벤트 방지
    setExpandedFrameworks(prev => ({
      ...prev,
      [frameworkId]: !prev[frameworkId]
    }));
  };

  const handleSelectFramework = async (frameworkId) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/frameworks/${frameworkId}`);
      const data = await response.json();
      setSelectedFramework(data);
      setCurrentStep(2);
    } catch (error) {
      console.error('Framework load error:', error);
      alert('프레임워크를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCard = (cardData) => {
    const newCard = {
      id: `card-${Date.now()}-${Math.random()}`,
      ...cardData,
      timestamp: new Date().toISOString()
    };
    setCards([...cards, newCard]);
  };

  const handleRemoveCard = (cardId) => {
    setCards(cards.filter(c => c.id !== cardId));
  };

  const goToNextStep = () => {
    setCurrentStep(currentStep + 1);
  };

  const goToPrevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const optimizeResponse = await fetch('/api/v1/cards/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cards: cards,
          max_cards: 7,
          remove_duplicates: true,
          remove_noise: true,
          trim_to_limit: true,
        }),
      });
      const optimized = await optimizeResponse.json();

      if (optimized.optimized_cards) {
        setCards(optimized.optimized_cards);
      }

      const analysisResponse = await fetch('/api/v1/decision/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: `${selectedFramework?.name} 분석`,
          options: ["Option A", "Option B"],
          current_cards: optimized.optimized_cards || cards,
          category: selectedFramework?.category || 'strategy',
        }),
      });
      const analysis = await analysisResponse.json();

      setAnalysisResult(analysis);
      setCurrentStep(5);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const progress = (currentStep / 5) * 100;

  return (
    <div className="guided-flow">
      {/* 헤더 */}
      <div className="flow-header">
        <h1>COGNITIVE DECK</h1>
        <p>Data-Driven Decision Making System</p>
      </div>

      {/* 진행 바 */}
      <div className="progress-section">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="step-indicators">
          {[1, 2, 3, 4, 5].map(step => (
            <div
              key={step}
              className={`step-indicator ${currentStep >= step ? 'active' : ''} ${currentStep === step ? 'current' : ''}`}
            >
              <div className="step-number">{step}</div>
              <div className="step-label">
                {step === 1 && 'Select'}
                {step === 2 && 'Guide'}
                {step === 3 && 'Input'}
                {step === 4 && 'Analyze'}
                {step === 5 && 'Result'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Step 1: 프레임워크 선택 (토글 기능 포함) */}
      {currentStep === 1 && (
        <div className="step-content">
          <h2>Step 1: Framework Selection</h2>
          <p className="step-desc">상황에 맞는 의사결정 프레임워크를 선택하세요</p>

          <div className="frameworks-list">
            {frameworks.map(fw => {
              const isExpanded = expandedFrameworks[fw.id];

              return (
                <FrameworkCard
                  key={fw.id}
                  framework={fw}
                  isExpanded={isExpanded}
                  onToggle={(e) => toggleFrameworkDetails(fw.id, e)}
                  onSelect={() => handleSelectFramework(fw.id)}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Step 2: 프레임워크별 특화 UI */}
      {currentStep === 2 && selectedFramework && (
        <div className="step-content">
          <h2>Step 2: {selectedFramework.name}</h2>
          <p className="step-desc">프레임워크 정보 및 필요한 카드를 확인하세요</p>

          {/* 프레임워크별 특화 레이아웃 렌더링 */}
          <FrameworkSpecializedLayout framework={selectedFramework} />

          {/* 카드 요구사항 */}
          <div className="card-requirements">
            <h4>📋 필요한 최소 카드: {selectedFramework.required_cards}개</h4>
            <div className="template-grid">
              {selectedFramework.card_template?.map((template, i) => (
                <div key={i} className="template-card">
                  <h5>{template.dimension}</h5>
                  <p className="template-desc">{template.description}</p>
                  {template.examples && (
                    <div className="template-examples">
                      <strong>예시</strong>
                      <ul>
                        {template.examples.map((ex, j) => (
                          <li key={j}>{ex}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="step-nav">
            <button onClick={goToPrevStep} className="btn-prev">← Previous</button>
            <button onClick={goToNextStep} className="btn-next">Next: Card Input →</button>
          </div>
        </div>
      )}

      {/* Step 3: 카드 작성 */}
      {currentStep === 3 && selectedFramework && (
        <div className="step-content">
          <h2>Step 3: Card Creation</h2>
          <p className="step-desc">
            프레임워크에 필요한 정보를 카드로 작성하세요
            (최소 {selectedFramework.required_cards}개 필요, 현재 {cards.length}개)
          </p>

          <CardInputForm
            framework={selectedFramework}
            onAddCard={handleAddCard}
          />

          <div className="cards-list">
            <h4>작성된 카드 ({cards.length}개)</h4>
            {cards.length === 0 && (
              <p className="empty-message">아직 작성된 카드가 없습니다</p>
            )}
            <div className="cards-grid">
              {cards.map(card => (
                <div key={card.id} className="card-item">
                  <div className="card-header">
                    <span className="card-name">{card.name}</span>
                    <button onClick={() => handleRemoveCard(card.id)} className="card-remove">✕</button>
                  </div>
                  <div className="card-body">
                    {card.dimension && <span className="card-dim">{card.dimension}</span>}
                    <span className="card-value">{card.value}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="step-nav">
            <button onClick={goToPrevStep} className="btn-prev">← Previous</button>
            <button
              onClick={goToNextStep}
              className="btn-next"
              disabled={cards.length < selectedFramework.required_cards}
            >
              {cards.length < selectedFramework.required_cards
                ? `최소 ${selectedFramework.required_cards}개 필요 (${cards.length}/${selectedFramework.required_cards})`
                : 'Next: Analyze →'}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: 분석 실행 */}
      {currentStep === 4 && (
        <div className="step-content">
          <h2>Step 4: Analysis</h2>
          <p className="step-desc">작성한 {cards.length}개의 카드를 분석합니다</p>

          <div className="analysis-ready">
            <div className="ready-info">
              <h4>✓ Ready to Analyze</h4>
              <ul>
                <li>프레임워크: {selectedFramework?.name}</li>
                <li>카드 수: {cards.length}개</li>
                <li>분석 방법: {selectedFramework?.analysis_method}</li>
              </ul>
            </div>

            <button
              onClick={runAnalysis}
              disabled={loading}
              className="btn-analyze"
            >
              {loading ? 'Analyzing...' : 'Start Analysis'}
            </button>
          </div>

          <div className="step-nav">
            <button onClick={goToPrevStep} className="btn-prev">← Previous</button>
          </div>
        </div>
      )}

      {/* Step 5: 결과 및 추천 */}
      {currentStep === 5 && analysisResult && (
        <div className="step-content">
          <h2>Step 5: Analysis Result</h2>
          <p className="step-desc">프레임워크 기반 분석이 완료되었습니다</p>

          <div className="result-sections">
            {analysisResult.gaps && analysisResult.gaps.length > 0 && (
              <div className="result-section">
                <h4>Gap Analysis</h4>
                <p>부족한 데이터: {analysisResult.gaps.length}개</p>
                <div className="gaps-list">
                  {analysisResult.gaps.slice(0, 3).map((gap, i) => (
                    <div key={i} className="gap-item">
                      <span className="gap-dim">{gap.dimension}</span>
                      <span className="gap-priority">우선순위: {gap.priority.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysisResult.recommendation && (
              <div className="result-section recommendation">
                <h4>Recommendation</h4>
                <p>{analysisResult.recommendation}</p>
              </div>
            )}

            {analysisResult.tradeoff?.confidence && (
              <div className="result-section">
                <h4>Confidence Score</h4>
                <div className="confidence-meter">
                  <div
                    className="confidence-bar"
                    style={{ width: `${analysisResult.tradeoff.confidence.score}%` }}
                  >
                    <span>{analysisResult.tradeoff.confidence.score}%</span>
                  </div>
                </div>
                <p>{analysisResult.tradeoff.confidence.message}</p>
              </div>
            )}
          </div>

          <div className="step-nav">
            <button onClick={() => setCurrentStep(1)} className="btn-restart">
              New Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * 프레임워크 카드 컴포넌트 (토글 기능 포함)
 */
const FrameworkCard = ({ framework, isExpanded, onToggle, onSelect }) => {
  return (
    <div className="framework-item">
      <h3>{framework.name}</h3>
      <p className="fw-desc">{framework.description}</p>
      <div className="fw-meta">
        <span className="fw-cat">{framework.category}</span>
        <span className="fw-dims">{framework.dimensions}개 차원</span>
      </div>

      {/* 토글 버튼 */}
      <div className="framework-toggle">
        <button className="toggle-button" onClick={onToggle}>
          <span>상세 정보</span>
          <span className={`toggle-icon ${isExpanded ? 'open' : ''}`}>▼</span>
        </button>

        {/* 상세 정보 (토글 시 표시) */}
        {isExpanded && (
          <div className="framework-details">
            <div className="detail-section">
              <h4>How to Use</h4>
              <div className="how-to-use">
                <p>
                  {framework.id === 'swot' && '내부(강점/약점)와 외부(기회/위협) 요인을 4분할로 정리하여 전략을 수립합니다.'}
                  {framework.id === 'porter_5_forces' && '5가지 경쟁 요인을 분석하여 산업 구조와 수익성을 파악합니다.'}
                  {framework.id === 'bcg_matrix' && '사업 포트폴리오를 시장 성장률과 점유율로 분류하여 자원 배분 전략을 수립합니다.'}
                  {framework.id === 'ice_score' && 'Impact, Confidence, Ease 3가지 기준으로 아이디어의 우선순위를 결정합니다.'}
                  {framework.id === 'rice_score' && 'Reach, Impact, Confidence, Effort 4가지 기준으로 제품 기능의 우선순위를 결정합니다.'}
                  {framework.id === 'mckinsey_7s' && '7가지 핵심 요소(전략, 구조, 시스템, 공유가치, 기술, 스타일, 인력)의 정렬 상태를 분석합니다.'}
                  {framework.id === 'raci' && '프로젝트 역할을 Responsible, Accountable, Consulted, Informed로 명확히 정의합니다.'}
                  {!['swot', 'porter_5_forces', 'bcg_matrix', 'ice_score', 'rice_score', 'mckinsey_7s', 'raci'].includes(framework.id) &&
                    '이 프레임워크를 사용하여 체계적인 의사결정을 수행합니다.'}
                </p>
              </div>
            </div>

            <div className="detail-section">
              <h4>When to Use</h4>
              <ul>
                {framework.id === 'swot' && (
                  <>
                    <li>새로운 사업 시작 전 전략 수립</li>
                    <li>현재 상황 파악 및 팀 워크샵</li>
                  </>
                )}
                {framework.id === 'porter_5_forces' && (
                  <>
                    <li>신규 시장 진입 검토</li>
                    <li>산업 구조 분석 필요 시</li>
                  </>
                )}
                {framework.id === 'bcg_matrix' && (
                  <>
                    <li>다수의 사업/제품 포트폴리오 관리</li>
                    <li>자원 배분 전략 수립</li>
                  </>
                )}
                {framework.id === 'ice_score' && (
                  <>
                    <li>빠른 아이디어 우선순위 결정</li>
                    <li>스타트업 초기 기능 선정</li>
                  </>
                )}
                {framework.id === 'rice_score' && (
                  <>
                    <li>제품 로드맵 작성</li>
                    <li>기능 우선순위 결정</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        )}
      </div>

      <button className="select-btn" onClick={onSelect}>
        Select Framework →
      </button>
    </div>
  );
};

/**
 * 프레임워크별 특화 레이아웃
 */
const FrameworkSpecializedLayout = ({ framework }) => {
  // SWOT Analysis - 2x2 Quadrant
  if (framework.id === 'swot') {
    return (
      <div className="swot-layout">
        <div className="swot-quadrant strengths">
          <h3>Strengths</h3>
          <p>내부의 경쟁 우위 요소</p>
          <ul>
            {framework.pros?.slice(0, 3).map((pro, i) => (
              <li key={i}>{pro}</li>
            ))}
          </ul>
        </div>
        <div className="swot-quadrant weaknesses">
          <h3>Weaknesses</h3>
          <p>내부의 개선이 필요한 요소</p>
          <ul>
            {framework.cons?.slice(0, 3).map((con, i) => (
              <li key={i}>{con}</li>
            ))}
          </ul>
        </div>
        <div className="swot-quadrant opportunities">
          <h3>Opportunities</h3>
          <p>외부의 활용 가능한 기회</p>
          <ul>
            {framework.when_to_use?.slice(0, 3).map((when, i) => (
              <li key={i}>{when}</li>
            ))}
          </ul>
        </div>
        <div className="swot-quadrant threats">
          <h3>Threats</h3>
          <p>외부의 위협 요인</p>
          <ul>
            {framework.when_not_to_use?.slice(0, 3).map((when, i) => (
              <li key={i}>{when}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  // Porter's 5 Forces - 5-Direction Layout
  if (framework.id === 'porter_5_forces') {
    return (
      <div className="forces-layout">
        <div className="force-box top">
          <h4>신규 진입자의 위협</h4>
          <p>New Entrants</p>
        </div>
        <div className="force-box left">
          <h4>공급자의 교섭력</h4>
          <p>Supplier Power</p>
        </div>
        <div className="force-box center">
          <h3>산업 내 경쟁</h3>
          <p>Competitive Rivalry</p>
        </div>
        <div className="force-box right">
          <h4>구매자의 교섭력</h4>
          <p>Buyer Power</p>
        </div>
        <div className="force-box bottom">
          <h4>대체재의 위협</h4>
          <p>Substitutes</p>
        </div>
      </div>
    );
  }

  // BCG Matrix - 2x2 Growth-Share Matrix
  if (framework.id === 'bcg_matrix') {
    return (
      <div className="bcg-layout">
        <div className="bcg-quadrant">
          <h3>★ Star</h3>
          <p className="quadrant-desc">높은 성장률, 높은 점유율</p>
          <p>투자 확대 필요</p>
        </div>
        <div className="bcg-quadrant">
          <h3>? Question Mark</h3>
          <p className="quadrant-desc">높은 성장률, 낮은 점유율</p>
          <p>선택적 투자 검토</p>
        </div>
        <div className="bcg-quadrant">
          <h3>$ Cash Cow</h3>
          <p className="quadrant-desc">낮은 성장률, 높은 점유율</p>
          <p>수익 창출원</p>
        </div>
        <div className="bcg-quadrant">
          <h3>✕ Dog</h3>
          <p className="quadrant-desc">낮은 성장률, 낮은 점유율</p>
          <p>철수 검토</p>
        </div>
      </div>
    );
  }

  // ICE/RICE Score - Slider Layout
  if (framework.id === 'ice_score' || framework.id === 'rice_score') {
    const criteria = framework.id === 'ice_score'
      ? ['Impact', 'Confidence', 'Ease']
      : ['Reach', 'Impact', 'Confidence', 'Effort'];

    return (
      <div className="score-layout">
        <h3>{framework.name} 평가 기준</h3>
        {criteria.map((criterion, i) => (
          <div key={i} className="score-slider">
            <label>{criterion}</label>
            <input type="range" min="1" max="10" defaultValue="5" disabled />
            <span className="score-value">5</span>
          </div>
        ))}
        <p style={{ marginTop: '20px', color: 'var(--gray-600)' }}>
          실제 평가는 Step 3: 카드 작성 단계에서 진행됩니다
        </p>
      </div>
    );
  }

  // Default: Generic Info Grid
  return (
    <div className="framework-info-grid">
      {framework.pros && framework.pros.length > 0 && (
        <div className="info-box">
          <h4>✓ Pros</h4>
          <ul>
            {framework.pros.map((pro, i) => (
              <li key={i}>{pro}</li>
            ))}
          </ul>
        </div>
      )}

      {framework.cons && framework.cons.length > 0 && (
        <div className="info-box">
          <h4>✕ Cons</h4>
          <ul>
            {framework.cons.map((con, i) => (
              <li key={i}>{con}</li>
            ))}
          </ul>
        </div>
      )}

      {framework.when_to_use && framework.when_to_use.length > 0 && (
        <div className="info-box">
          <h4>→ When to Use</h4>
          <ul>
            {framework.when_to_use.map((when, i) => (
              <li key={i}>{when}</li>
            ))}
          </ul>
        </div>
      )}

      {framework.when_not_to_use && framework.when_not_to_use.length > 0 && (
        <div className="info-box">
          <h4>! When NOT to Use</h4>
          <ul>
            {framework.when_not_to_use.map((when, i) => (
              <li key={i}>{when}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

/**
 * 카드 입력 폼
 */
const CardInputForm = ({ framework, onAddCard }) => {
  const [formData, setFormData] = useState({
    name: '',
    value: '',
    dimension: framework?.card_template?.[0]?.dimension || '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.value) {
      alert('카드 이름과 값을 입력하세요');
      return;
    }

    onAddCard(formData);

    setFormData({
      name: '',
      value: '',
      dimension: framework?.card_template?.[0]?.dimension || '',
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card-input-form">
      <div className="form-row">
        <div className="form-group">
          <label>Dimension</label>
          <select
            value={formData.dimension}
            onChange={(e) => setFormData({...formData, dimension: e.target.value})}
          >
            {framework?.card_template?.map(template => (
              <option key={template.dimension} value={template.dimension}>
                {template.dimension}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Card Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            placeholder="예: 강력한 브랜드"
          />
        </div>

        <div className="form-group">
          <label>Value / Description</label>
          <input
            type="text"
            value={formData.value}
            onChange={(e) => setFormData({...formData, value: e.target.value})}
            placeholder="예: 시장 점유율 1위"
          />
        </div>

        <button type="submit" className="btn-add-card">Add Card</button>
      </div>
    </form>
  );
};

export default GuidedDecisionFlow;
