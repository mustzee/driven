import React, { useState, useEffect } from 'react';
import './GuidedDecisionFlow.css';

/**
 * 🎴 Cognitive Deck - Framework-Specific Decision Making System
 * 
 * No Card Format - Direct Framework-Specific Input Methods
 * 1. SWOT: 4-quadrant direct input
 * 2. Porter's 5 Forces: 5-area textarea
 * 3. BCG Matrix: Business unit placement
 * 4. ICE/RICE: Slider-based scoring
 * 5. Others: Framework-optimized inputs
 */

// Framework Use Cases Data
const FRAMEWORK_USE_CASES = {
  swot: [
    {
      situation: "신규 사업 진입 결정",
      output: "내부 역량(S/W)과 외부 환경(O/T)을 4분할로 정리하여 진입 전략 수립"
    },
    {
      situation: "제품 리뉴얼 검토",
      output: "현재 제품의 강점과 약점, 시장 기회와 위협을 시각화하여 개선 방향 도출"
    },
    {
      situation: "경쟁사 분석",
      output: "우리와 경쟁사의 차별화 포인트와 시장 포지셔닝을 비교 분석"
    }
  ],
  porter_5_forces: [
    {
      situation: "새로운 시장 진입 검토",
      output: "5가지 경쟁 요인을 분석하여 진입 장벽과 수익성 예측"
    },
    {
      situation: "산업 구조 변화 대응",
      output: "공급자/구매자 교섭력, 신규 진입자, 대체재 위협을 종합적으로 파악"
    }
  ],
  bcg_matrix: [
    {
      situation: "사업 포트폴리오 최적화",
      output: "Star/Question Mark/Cash Cow/Dog 분류로 투자 우선순위 결정"
    },
    {
      situation: "자원 배분 전략 수립",
      output: "성장률과 점유율 기준으로 사업별 투자 규모 조정"
    }
  ],
  ice_score: [
    {
      situation: "프로덕트 백로그 우선순위 결정",
      output: "Impact, Confidence, Ease 점수로 빠른 기능 선정"
    },
    {
      situation: "스타트업 MVP 기능 선택",
      output: "제한된 리소스로 가장 효과적인 기능 우선 개발"
    }
  ],
  rice_score: [
    {
      situation: "제품 로드맵 작성",
      output: "Reach, Impact, Confidence, Effort를 종합하여 분기별 개발 계획 수립"
    }
  ]
};

const GuidedDecisionFlow = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [frameworks, setFrameworks] = useState([]);
  const [selectedFramework, setSelectedFramework] = useState(null);
  const [expandedFrameworks, setExpandedFrameworks] = useState({});
  const [loading, setLoading] = useState(false);

  // Framework-specific data structures
  const [swotData, setSwotData] = useState({
    strengths: [],
    weaknesses: [],
    opportunities: [],
    threats: []
  });

  const [forcesData, setForcesData] = useState({
    newEntrants: '',
    suppliers: '',
    buyers: '',
    substitutes: '',
    rivalry: ''
  });

  const [bcgData, setBcgData] = useState({
    star: [],
    questionMark: [],
    cashCow: [],
    dog: []
  });

  const [ideasData, setIdeasData] = useState([]);

  const [analysisResult, setAnalysisResult] = useState(null);

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
    e.stopPropagation();
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
      
      // Reset data
      setSwotData({ strengths: [], weaknesses: [], opportunities: [], threats: [] });
      setForcesData({ newEntrants: '', suppliers: '', buyers: '', substitutes: '', rivalry: '' });
      setBcgData({ star: [], questionMark: [], cashCow: [], dog: [] });
      setIdeasData([]);
      
      setCurrentStep(2);
    } catch (error) {
      console.error('Framework load error:', error);
      alert('프레임워크를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
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
      // Convert framework-specific data to cards format for API
      let cards = [];
      
      if (selectedFramework.id === 'swot') {
        swotData.strengths.forEach(item => cards.push({ dimension: 'Strengths', name: item, value: item }));
        swotData.weaknesses.forEach(item => cards.push({ dimension: 'Weaknesses', name: item, value: item }));
        swotData.opportunities.forEach(item => cards.push({ dimension: 'Opportunities', name: item, value: item }));
        swotData.threats.forEach(item => cards.push({ dimension: 'Threats', name: item, value: item }));
      } else if (selectedFramework.id === 'porter_5_forces') {
        if (forcesData.newEntrants) cards.push({ dimension: 'New Entrants', name: 'New Entrants', value: forcesData.newEntrants });
        if (forcesData.suppliers) cards.push({ dimension: 'Supplier Power', name: 'Supplier Power', value: forcesData.suppliers });
        if (forcesData.buyers) cards.push({ dimension: 'Buyer Power', name: 'Buyer Power', value: forcesData.buyers });
        if (forcesData.substitutes) cards.push({ dimension: 'Substitutes', name: 'Substitutes', value: forcesData.substitutes });
        if (forcesData.rivalry) cards.push({ dimension: 'Competitive Rivalry', name: 'Competitive Rivalry', value: forcesData.rivalry });
      } else if (selectedFramework.id === 'bcg_matrix') {
        bcgData.star.forEach(item => cards.push({ dimension: 'Star', name: item, value: item }));
        bcgData.questionMark.forEach(item => cards.push({ dimension: 'Question Mark', name: item, value: item }));
        bcgData.cashCow.forEach(item => cards.push({ dimension: 'Cash Cow', name: item, value: item }));
        bcgData.dog.forEach(item => cards.push({ dimension: 'Dog', name: item, value: item }));
      } else if (selectedFramework.id === 'ice_score' || selectedFramework.id === 'rice_score') {
        ideasData.forEach(idea => {
          cards.push({
            dimension: 'Idea',
            name: idea.name,
            value: JSON.stringify(idea.scores)
          });
        });
      }

      const analysisResponse = await fetch('/api/v1/decision/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: `${selectedFramework?.name} Analysis`,
          options: ["Option A", "Option B"],
          current_cards: cards,
          category: selectedFramework?.category || 'strategy',
        }),
      });
      const analysis = await analysisResponse.json();

      setAnalysisResult(analysis);
      setCurrentStep(4); // Skip to results
    } catch (error) {
      console.error('Analysis error:', error);
      alert('분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const progress = (currentStep / 4) * 100; // Now 4 steps instead of 5

  return (
    <div className="guided-flow">
      <div className="flow-header">
        <h1>COGNITIVE DECK</h1>
        <p>Framework-Specific Decision Making System</p>
      </div>

      <div className="progress-section">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="step-indicators">
          {[1, 2, 3, 4].map(step => (
            <div
              key={step}
              className={`step-indicator ${currentStep >= step ? 'active' : ''} ${currentStep === step ? 'current' : ''}`}
            >
              <div className="step-number">{step}</div>
              <div className="step-label">
                {step === 1 && 'Select'}
                {step === 2 && 'Guide'}
                {step === 3 && 'Input'}
                {step === 4 && 'Result'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Step 1: Framework Selection with Use Cases */}
      {currentStep === 1 && (
        <div className="step-content">
          <h2>Step 1: Framework Selection</h2>
          <p className="step-desc">상황에 맞는 프레임워크를 선택하세요. 각 프레임워크의 활용 사례를 확인할 수 있습니다.</p>

          <div className="frameworks-list">
            {frameworks.map(fw => {
              const isExpanded = expandedFrameworks[fw.id];
              const useCases = FRAMEWORK_USE_CASES[fw.id] || [];

              return (
                <div key={fw.id} className="framework-item">
                  <h3>{fw.name}</h3>
                  <p className="fw-desc">{fw.description}</p>
                  <div className="fw-meta">
                    <span className="fw-cat">{fw.category}</span>
                    <span className="fw-dims">{fw.dimensions}개 차원</span>
                  </div>

                  {/* Use Cases */}
                  {useCases.length > 0 && (
                    <div className="use-cases">
                      <h4>활용 사례</h4>
                      {useCases.map((useCase, i) => (
                        <div key={i} className="use-case-item">
                          <div className="use-case-situation">{useCase.situation}</div>
                          <div className="use-case-output">→ {useCase.output}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Toggle Details */}
                  <div className="framework-toggle">
                    <button className="toggle-button" onClick={(e) => toggleFrameworkDetails(fw.id, e)}>
                      <span>상세 정보</span>
                      <span className={`toggle-icon ${isExpanded ? 'open' : ''}`}>▼</span>
                    </button>

                    {isExpanded && (
                      <div className="framework-details">
                        <div className="detail-section">
                          <h4>How to Use</h4>
                          <div className="how-to-use">
                            <p>
                              {fw.id === 'swot' && '내부(강점/약점)와 외부(기회/위협) 요인을 4분할로 정리하여 전략을 수립합니다.'}
                              {fw.id === 'porter_5_forces' && '5가지 경쟁 요인을 분석하여 산업 구조와 수익성을 파악합니다.'}
                              {fw.id === 'bcg_matrix' && '사업 포트폴리오를 시장 성장률과 점유율로 분류하여 자원 배분 전략을 수립합니다.'}
                              {fw.id === 'ice_score' && 'Impact, Confidence, Ease 3가지 기준으로 아이디어의 우선순위를 결정합니다.'}
                              {fw.id === 'rice_score' && 'Reach, Impact, Confidence, Effort 4가지 기준으로 제품 기능의 우선순위를 결정합니다.'}
                              {!['swot', 'porter_5_forces', 'bcg_matrix', 'ice_score', 'rice_score'].includes(fw.id) &&
                                '이 프레임워크를 사용하여 체계적인 의사결정을 수행합니다.'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <button className="select-btn" onClick={() => handleSelectFramework(fw.id)}>
                    Select Framework →
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
      {/* Step 2: Interactive Framework Guide */}
      {currentStep === 2 && selectedFramework && (
        <div className="step-content">
          <h2>Step 2: {selectedFramework.name} Guide</h2>
          <p className="step-desc">프레임워크 사용 방법과 필요한 정보를 확인하세요</p>

          <div className="framework-guide">
            {/* Detailed Guide Sections */}
            <div className="guide-section">
              <h3>📊 분석 개요</h3>
              <p>{selectedFramework.description}</p>
            </div>

            {selectedFramework.pros && selectedFramework.pros.length > 0 && (
              <div className="guide-section">
                <h3>✓ 장점</h3>
                <ul className="guide-list">
                  {selectedFramework.pros.map((pro, i) => (
                    <li key={i}>{pro}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedFramework.when_to_use && selectedFramework.when_to_use.length > 0 && (
              <div className="guide-section">
                <h3>→ 적합한 상황</h3>
                <ul className="guide-list">
                  {selectedFramework.when_to_use.map((when, i) => (
                    <li key={i}>{when}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedFramework.card_template && selectedFramework.card_template.length > 0 && (
              <div className="guide-section">
                <h3>📝 입력 가이드</h3>
                <p>다음 단계에서 아래 정보를 입력하게 됩니다:</p>
                <ul className="guide-list">
                  {selectedFramework.card_template.map((template, i) => (
                    <li key={i}>
                      <strong>{template.dimension}:</strong> {template.description}
                      {template.examples && template.examples.length > 0 && (
                        <span> (예: {template.examples.slice(0, 2).join(', ')})</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="step-nav">
            <button onClick={goToPrevStep} className="btn-prev">← Previous</button>
            <button onClick={goToNextStep} className="btn-next">Next: Input Data →</button>
          </div>
        </div>
      )}

      {/* Step 3: Framework-Specific Input */}
      {currentStep === 3 && selectedFramework && (
        <div className="step-content">
          <h2>Step 3: Data Input</h2>
          <p className="step-desc">
            {selectedFramework.name}에 필요한 정보를 입력하세요
          </p>

          {/* SWOT Analysis Input */}
          {selectedFramework.id === 'swot' && (
            <SWOTInput data={swotData} setData={setSwotData} />
          )}

          {/* Porter's 5 Forces Input */}
          {selectedFramework.id === 'porter_5_forces' && (
            <PorterForcesInput data={forcesData} setData={setForcesData} />
          )}

          {/* BCG Matrix Input */}
          {selectedFramework.id === 'bcg_matrix' && (
            <BCGMatrixInput data={bcgData} setData={setBcgData} />
          )}

          {/* ICE/RICE Score Input */}
          {(selectedFramework.id === 'ice_score' || selectedFramework.id === 'rice_score') && (
            <ScoreInput 
              frameworkId={selectedFramework.id}
              data={ideasData} 
              setData={setIdeasData} 
            />
          )}

          {/* Default Input for Other Frameworks */}
          {!['swot', 'porter_5_forces', 'bcg_matrix', 'ice_score', 'rice_score'].includes(selectedFramework.id) && (
            <div className="guide-section">
              <h3>데이터 입력 준비 중...</h3>
              <p>이 프레임워크를 위한 특화 입력 UI는 곧 추가될 예정입니다.</p>
            </div>
          )}

          <div className="step-nav">
            <button onClick={goToPrevStep} className="btn-prev">← Previous</button>
            <button
              onClick={runAnalysis}
              disabled={loading}
              className="btn-next"
            >
              {loading ? 'Analyzing...' : 'Analyze →'}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Results */}
      {currentStep === 4 && analysisResult && (
        <div className="step-content">
          <h2>Step 4: Analysis Result</h2>
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
            <button onClick={() => { setCurrentStep(1); setAnalysisResult(null); }} className="btn-restart">
              New Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
/**
 * SWOT Analysis 4-Quadrant Input Component
 */
const SWOTInput = ({ data, setData }) => {
  const [inputs, setInputs] = useState({
    strengths: '',
    weaknesses: '',
    opportunities: '',
    threats: ''
  });

  const addItem = (quadrant) => {
    if (!inputs[quadrant].trim()) return;
    
    setData(prev => ({
      ...prev,
      [quadrant]: [...prev[quadrant], inputs[quadrant].trim()]
    }));
    
    setInputs(prev => ({ ...prev, [quadrant]: '' }));
  };

  const removeItem = (quadrant, index) => {
    setData(prev => ({
      ...prev,
      [quadrant]: prev[quadrant].filter((_, i) => i !== index)
    }));
  };

  const quadrants = [
    { key: 'strengths', title: 'Strengths', subtitle: '내부의 경쟁 우위 요소', className: 'strengths' },
    { key: 'weaknesses', title: 'Weaknesses', subtitle: '내부의 개선이 필요한 요소', className: 'weaknesses' },
    { key: 'opportunities', title: 'Opportunities', subtitle: '외부의 활용 가능한 기회', className: 'opportunities' },
    { key: 'threats', title: 'Threats', subtitle: '외부의 위협 요인', className: 'threats' }
  ];

  return (
    <div className="swot-input-grid">
      {quadrants.map(quadrant => (
        <div key={quadrant.key} className={`swot-quadrant-input ${quadrant.className}`}>
          <h3>{quadrant.title}</h3>
          <span className="quadrant-subtitle">{quadrant.subtitle}</span>
          
          <ul className="swot-item-list">
            {data[quadrant.key].map((item, index) => (
              <li key={index} className="swot-item">
                <span className="swot-item-text">{item}</span>
                <button 
                  onClick={() => removeItem(quadrant.key, index)} 
                  className="swot-item-remove"
                  type="button"
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>

          <form className="swot-input-form" onSubmit={(e) => { e.preventDefault(); addItem(quadrant.key); }}>
            <input
              type="text"
              value={inputs[quadrant.key]}
              onChange={(e) => setInputs(prev => ({ ...prev, [quadrant.key]: e.target.value }))}
              placeholder={`${quadrant.title} 항목 입력...`}
            />
            <button type="submit">Add</button>
          </form>
        </div>
      ))}
    </div>
  );
};

/**
 * Porter's 5 Forces Input Component
 */
const PorterForcesInput = ({ data, setData }) => {
  const forces = [
    { key: 'newEntrants', title: '신규 진입자의 위협', subtitle: 'New Entrants', position: 'top' },
    { key: 'suppliers', title: '공급자의 교섭력', subtitle: 'Supplier Power', position: 'left' },
    { key: 'rivalry', title: '산업 내 경쟁', subtitle: 'Competitive Rivalry', position: 'center' },
    { key: 'buyers', title: '구매자의 교섭력', subtitle: 'Buyer Power', position: 'right' },
    { key: 'substitutes', title: '대체재의 위협', subtitle: 'Substitutes', position: 'bottom' }
  ];

  return (
    <div className="forces-input-layout">
      {forces.map(force => (
        <div key={force.key} className={`force-input-box ${force.position}`}>
          <h4>{force.title}</h4>
          <p>{force.subtitle}</p>
          <textarea
            className="force-textarea"
            value={data[force.key]}
            onChange={(e) => setData(prev => ({ ...prev, [force.key]: e.target.value }))}
            placeholder={`${force.title}에 대한 분석을 입력하세요...`}
          />
        </div>
      ))}
    </div>
  );
};

/**
 * BCG Matrix Input Component
 */
const BCGMatrixInput = ({ data, setData }) => {
  const [inputs, setInputs] = useState({
    star: '',
    questionMark: '',
    cashCow: '',
    dog: ''
  });

  const addBusiness = (quadrant) => {
    if (!inputs[quadrant].trim()) return;
    
    setData(prev => ({
      ...prev,
      [quadrant]: [...prev[quadrant], inputs[quadrant].trim()]
    }));
    
    setInputs(prev => ({ ...prev, [quadrant]: '' }));
  };

  const removeBusiness = (quadrant, index) => {
    setData(prev => ({
      ...prev,
      [quadrant]: prev[quadrant].filter((_, i) => i !== index)
    }));
  };

  const quadrants = [
    { key: 'star', title: '★ Star', desc: '높은 성장률, 높은 점유율 - 투자 확대' },
    { key: 'questionMark', title: '? Question Mark', desc: '높은 성장률, 낮은 점유율 - 선택적 투자' },
    { key: 'cashCow', title: '$ Cash Cow', desc: '낮은 성장률, 높은 점유율 - 수익 창출' },
    { key: 'dog', title: '✕ Dog', desc: '낮은 성장률, 낮은 점유율 - 철수 검토' }
  ];

  return (
    <div className="bcg-input-layout">
      {quadrants.map(quadrant => (
        <div key={quadrant.key} className="bcg-quadrant-input">
          <h3>{quadrant.title}</h3>
          <p className="quadrant-desc">{quadrant.desc}</p>
          
          <ul className="bcg-business-list">
            {data[quadrant.key].map((business, index) => (
              <li key={index} className="bcg-business-item">
                <span>{business}</span>
                <button
                  onClick={() => removeBusiness(quadrant.key, index)}
                  className="swot-item-remove"
                  type="button"
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>

          <form className="bcg-add-business" onSubmit={(e) => { e.preventDefault(); addBusiness(quadrant.key); }}>
            <input
              type="text"
              value={inputs[quadrant.key]}
              onChange={(e) => setInputs(prev => ({ ...prev, [quadrant.key]: e.target.value }))}
              placeholder="사업 단위명 입력..."
            />
            <button type="submit">Add</button>
          </form>
        </div>
      ))}
    </div>
  );
};

/**
 * ICE/RICE Score Input Component
 */
const ScoreInput = ({ frameworkId, data, setData }) => {
  const [newIdeaName, setNewIdeaName] = useState('');
  
  const criteria = frameworkId === 'ice_score'
    ? ['impact', 'confidence', 'ease']
    : ['reach', 'impact', 'confidence', 'effort'];

  const addIdea = (e) => {
    e.preventDefault();
    if (!newIdeaName.trim()) return;

    const newIdea = {
      id: Date.now(),
      name: newIdeaName.trim(),
      scores: {}
    };

    criteria.forEach(criterion => {
      newIdea.scores[criterion] = 5;
    });

    setData([...data, newIdea]);
    setNewIdeaName('');
  };

  const removeIdea = (ideaId) => {
    setData(data.filter(idea => idea.id !== ideaId));
  };

  const updateScore = (ideaId, criterion, value) => {
    setData(data.map(idea => {
      if (idea.id === ideaId) {
        return {
          ...idea,
          scores: {
            ...idea.scores,
            [criterion]: parseInt(value)
          }
        };
      }
      return idea;
    }));
  };

  const calculateScore = (scores) => {
    if (frameworkId === 'ice_score') {
      return ((scores.impact || 0) * (scores.confidence || 0) * (scores.ease || 0)) / 10;
    } else {
      // RICE: (Reach * Impact * Confidence) / Effort
      return ((scores.reach || 0) * (scores.impact || 0) * (scores.confidence || 0)) / (scores.effort || 1);
    }
  };

  const criteriaLabels = {
    impact: 'Impact',
    confidence: 'Confidence',
    ease: 'Ease',
    reach: 'Reach',
    effort: 'Effort'
  };

  return (
    <div className="score-input-layout">
      <h3>{frameworkId === 'ice_score' ? 'ICE Score' : 'RICE Score'} 평가</h3>

      <div className="ideas-list">
        {data.map(idea => (
          <div key={idea.id} className="idea-item">
            <div className="idea-header">
              <span className="idea-name">{idea.name}</span>
              <button onClick={() => removeIdea(idea.id)} className="idea-remove">✕</button>
            </div>

            <div className="idea-sliders">
              {criteria.map(criterion => (
                <div key={criterion} className="slider-group">
                  <label>{criteriaLabels[criterion]}</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={idea.scores[criterion] || 5}
                    onChange={(e) => updateScore(idea.id, criterion, e.target.value)}
                  />
                  <span className="slider-value">{idea.scores[criterion] || 5}</span>
                </div>
              ))}
            </div>

            <div className="idea-score">
              Score: {calculateScore(idea.scores).toFixed(2)}
            </div>
          </div>
        ))}
      </div>

      <form className="add-idea-form" onSubmit={addIdea}>
        <input
          type="text"
          value={newIdeaName}
          onChange={(e) => setNewIdeaName(e.target.value)}
          placeholder="아이디어 또는 기능명 입력..."
        />
        <button type="submit">Add Idea</button>
      </form>
    </div>
  );
};

export default GuidedDecisionFlow;
