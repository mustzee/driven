import React, { useState, useEffect } from 'react';
import './GuidedDecisionFlow.css';

/**
 * GuidedDecisionFlow - 완전 가이드형 의사결정 시스템
 *
 * 5단계 워크플로우:
 * 1. 프레임워크 선택 (장단점 설명)
 * 2. 필요한 카드 안내
 * 3. 카드 작성
 * 4. 자동 분석
 * 5. 결과 및 추천
 */
const GuidedDecisionFlow = () => {
  // 현재 단계 (1~5)
  const [currentStep, setCurrentStep] = useState(1);

  // 프레임워크 목록 및 선택된 프레임워크
  const [frameworks, setFrameworks] = useState([]);
  const [selectedFramework, setSelectedFramework] = useState(null);

  // 작성된 카드들
  const [cards, setCards] = useState([]);

  // 분석 결과
  const [analysisResult, setAnalysisResult] = useState(null);

  const [loading, setLoading] = useState(false);

  // 프레임워크 목록 로드
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

  // 프레임워크 선택
  const handleSelectFramework = async (frameworkId) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/frameworks/${frameworkId}`);
      const data = await response.json();
      setSelectedFramework(data);
      setCurrentStep(2); // 다음 단계로
    } catch (error) {
      console.error('Framework load error:', error);
      alert('프레임워크를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 카드 추가
  const handleAddCard = (cardData) => {
    const newCard = {
      id: `card-${Date.now()}-${Math.random()}`,
      ...cardData,
      timestamp: new Date().toISOString()
    };
    setCards([...cards, newCard]);
  };

  // 카드 삭제
  const handleRemoveCard = (cardId) => {
    setCards(cards.filter(c => c.id !== cardId));
  };

  // 다음 단계로
  const goToNextStep = () => {
    setCurrentStep(currentStep + 1);
  };

  // 이전 단계로
  const goToPrevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  // 분석 실행
  const runAnalysis = async () => {
    setLoading(true);
    try {
      // 카드 최적화 먼저
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

      // 최적화된 카드로 업데이트
      if (optimized.optimized_cards) {
        setCards(optimized.optimized_cards);
      }

      // Decision Framework 분석
      const analysisResponse = await fetch('/api/v1/decision/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: `${selectedFramework?.name} 분석`,
          options: ["Option A", "Option B"], // 간단히
          current_cards: optimized.optimized_cards || cards,
          category: selectedFramework?.category || 'strategy',
        }),
      });
      const analysis = await analysisResponse.json();

      setAnalysisResult(analysis);
      setCurrentStep(5); // 결과 단계로
    } catch (error) {
      console.error('Analysis error:', error);
      alert('분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 진행률 계산
  const progress = (currentStep / 5) * 100;

  return (
    <div className="guided-flow">
      {/* 헤더 */}
      <div className="flow-header">
        <h1>🎯 가이드형 의사결정 시스템</h1>
        <p>단계별 안내에 따라 합리적인 결정을 내리세요</p>
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
                {step === 1 && '프레임워크 선택'}
                {step === 2 && '필요 카드 안내'}
                {step === 3 && '카드 작성'}
                {step === 4 && '분석 실행'}
                {step === 5 && '결과 확인'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Step 1: 프레임워크 선택 */}
      {currentStep === 1 && (
        <div className="step-content">
          <h2>Step 1: 프레임워크 선택</h2>
          <p className="step-desc">상황에 맞는 의사결정 프레임워크를 선택하세요</p>

          <div className="frameworks-list">
            {frameworks.map(fw => (
              <div
                key={fw.id}
                className="framework-item"
                onClick={() => handleSelectFramework(fw.id)}
              >
                <h3>{fw.name}</h3>
                <p className="fw-desc">{fw.description}</p>
                <div className="fw-meta">
                  <span className="fw-cat">{fw.category}</span>
                  <span className="fw-dims">{fw.dimensions}개 차원</span>
                </div>
                <button className="select-btn">선택하기 →</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: 필요한 카드 안내 */}
      {currentStep === 2 && selectedFramework && (
        <div className="step-content">
          <h2>Step 2: {selectedFramework.name} - 필요한 카드</h2>
          <p className="step-desc">이 프레임워크를 사용하기 위해 필요한 정보입니다</p>

          {/* 프레임워크 장단점 */}
          <div className="framework-info-grid">
            <div className="info-box pros-box">
              <h4>✅ 장점</h4>
              <ul>
                {selectedFramework.pros?.map((pro, i) => (
                  <li key={i}>{pro}</li>
                ))}
              </ul>
            </div>

            <div className="info-box cons-box">
              <h4>❌ 단점</h4>
              <ul>
                {selectedFramework.cons?.map((con, i) => (
                  <li key={i}>{con}</li>
                ))}
              </ul>
            </div>

            <div className="info-box when-box">
              <h4>🎯 적합한 상황</h4>
              <ul>
                {selectedFramework.when_to_use?.map((when, i) => (
                  <li key={i}>{when}</li>
                ))}
              </ul>
            </div>

            <div className="info-box when-not-box">
              <h4>⚠️ 부적합한 상황</h4>
              <ul>
                {selectedFramework.when_not_to_use?.map((when, i) => (
                  <li key={i}>{when}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* 필요한 카드 템플릿 */}
          <div className="card-requirements">
            <h4>📝 필요한 최소 카드: {selectedFramework.required_cards}개</h4>
            <div className="template-grid">
              {selectedFramework.card_template?.map((template, i) => (
                <div key={i} className="template-card">
                  <h5>{template.dimension}</h5>
                  <p className="template-desc">{template.description}</p>
                  {template.examples && (
                    <div className="template-examples">
                      <strong>예시:</strong>
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
            <button onClick={goToPrevStep} className="btn-prev">← 이전</button>
            <button onClick={goToNextStep} className="btn-next">다음: 카드 작성 →</button>
          </div>
        </div>
      )}

      {/* Step 3: 카드 작성 */}
      {currentStep === 3 && selectedFramework && (
        <div className="step-content">
          <h2>Step 3: 카드 작성</h2>
          <p className="step-desc">
            프레임워크에 필요한 정보를 카드로 작성하세요
            (최소 {selectedFramework.required_cards}개 필요, 현재 {cards.length}개)
          </p>

          {/* 카드 작성 폼 */}
          <CardInputForm
            framework={selectedFramework}
            onAddCard={handleAddCard}
          />

          {/* 작성된 카드 목록 */}
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
            <button onClick={goToPrevStep} className="btn-prev">← 이전</button>
            <button
              onClick={goToNextStep}
              className="btn-next"
              disabled={cards.length < selectedFramework.required_cards}
            >
              {cards.length < selectedFramework.required_cards
                ? `최소 ${selectedFramework.required_cards}개 필요 (${cards.length}/${selectedFramework.required_cards})`
                : '다음: 분석 실행 →'}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: 분석 실행 */}
      {currentStep === 4 && (
        <div className="step-content">
          <h2>Step 4: 분석 실행</h2>
          <p className="step-desc">작성한 {cards.length}개의 카드를 분석합니다</p>

          <div className="analysis-ready">
            <div className="ready-info">
              <h4>✅ 준비 완료</h4>
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
              {loading ? '분석 중...' : '🔬 분석 시작'}
            </button>
          </div>

          <div className="step-nav">
            <button onClick={goToPrevStep} className="btn-prev">← 이전</button>
          </div>
        </div>
      )}

      {/* Step 5: 결과 및 추천 */}
      {currentStep === 5 && analysisResult && (
        <div className="step-content">
          <h2>Step 5: 분석 결과</h2>
          <p className="step-desc">프레임워크 기반 분석이 완료되었습니다</p>

          <div className="result-sections">
            {/* Gap Analysis */}
            {analysisResult.gaps && analysisResult.gaps.length > 0 && (
              <div className="result-section">
                <h4>🔍 Gap Analysis</h4>
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

            {/* Recommendation */}
            {analysisResult.recommendation && (
              <div className="result-section recommendation">
                <h4>💡 추천</h4>
                <p>{analysisResult.recommendation}</p>
              </div>
            )}

            {/* Trade-off */}
            {analysisResult.tradeoff?.confidence && (
              <div className="result-section">
                <h4>⚖️ 신뢰도</h4>
                <div className="confidence-meter">
                  <div
                    className="confidence-bar"
                    style={{ width: `${analysisResult.tradeoff.confidence.score}%` }}
                  />
                  <span>{analysisResult.tradeoff.confidence.score}%</span>
                </div>
                <p>{analysisResult.tradeoff.confidence.message}</p>
              </div>
            )}
          </div>

          <div className="step-nav">
            <button onClick={() => setCurrentStep(1)} className="btn-restart">
              🔄 새로 시작
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// 카드 입력 폼 컴포넌트
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

    // 폼 초기화
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
          <label>차원</label>
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
          <label>카드 이름</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            placeholder="예: 강력한 브랜드"
          />
        </div>

        <div className="form-group">
          <label>값/설명</label>
          <input
            type="text"
            value={formData.value}
            onChange={(e) => setFormData({...formData, value: e.target.value})}
            placeholder="예: 시장 점유율 1위"
          />
        </div>

        <button type="submit" className="btn-add-card">+ 카드 추가</button>
      </div>
    </form>
  );
};

export default GuidedDecisionFlow;
