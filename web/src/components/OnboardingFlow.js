import React, { useState, useEffect } from 'react';
import './OnboardingFlow.css';

const SCENARIOS = {
  lunch: {
    name: "점심 메뉴 선택",
    description: "오늘 점심 어디서 먹을지 결정하기",
    icon: "🍽️",
    questions: [
      {
        id: "q1",
        text: "점심 식사의 주요 목적은 무엇인가요?",
        weight: 0.3,
        category: "심리적",
        options: [
          { text: "빠르게 끼니 해결", value: "efficiency", weightBonus: 0.1 },
          { text: "맛있는 음식 즐기기", value: "taste", weightBonus: 0.2 },
          { text: "동료와 소통", value: "social", weightBonus: 0.15 },
          { text: "건강한 식사", value: "health", weightBonus: 0.15 }
        ]
      },
      {
        id: "q2",
        text: "가장 중요한 제약사항은 무엇인가요?",
        weight: 0.5,
        category: "제약적",
        options: [
          { text: "시간 (30분 이내)", value: "time", weightBonus: 0.2 },
          { text: "예산 (만원 이하)", value: "budget", weightBonus: 0.25 },
          { text: "거리 (가까운 곳)", value: "distance", weightBonus: 0.15 },
          { text: "특별한 제약 없음", value: "none", weightBonus: 0 }
        ]
      },
      {
        id: "q3",
        text: "최종 결정에서 가장 우선시할 요소는?",
        weight: 0.8,
        category: "핵심",
        options: [
          { text: "만족도 (후회 없는 선택)", value: "satisfaction", weightBonus: 0.3 },
          { text: "효율성 (빠른 결정)", value: "efficiency", weightBonus: 0.2 },
          { text: "경제성 (가성비)", value: "value", weightBonus: 0.25 },
          { text: "새로운 경험", value: "novelty", weightBonus: 0.2 }
        ]
      }
    ]
  },
  product: {
    name: "제품 전략 수립",
    description: "신제품 로드맵 의사결정",
    icon: "🚀",
    questions: [
      {
        id: "q1",
        text: "제품의 주요 목표 시장은 어디인가요?",
        weight: 0.4,
        category: "전략적",
        options: [
          { text: "국내 시장", value: "domestic", weightBonus: 0.1 },
          { text: "글로벌 진출", value: "global", weightBonus: 0.3 },
          { text: "특정 니치 시장", value: "niche", weightBonus: 0.2 }
        ]
      },
      {
        id: "q2",
        text: "현재 가장 큰 제약사항은?",
        weight: 0.6,
        category: "제약적",
        options: [
          { text: "예산 부족", value: "budget", weightBonus: 0.25 },
          { text: "인력 부족", value: "team", weightBonus: 0.2 },
          { text: "기술적 한계", value: "tech", weightBonus: 0.3 },
          { text: "시간 압박", value: "time", weightBonus: 0.25 }
        ]
      },
      {
        id: "q3",
        text: "성공의 핵심 지표는 무엇인가요?",
        weight: 0.9,
        category: "핵심",
        options: [
          { text: "매출 성장", value: "revenue", weightBonus: 0.35 },
          { text: "사용자 수", value: "users", weightBonus: 0.3 },
          { text: "시장 점유율", value: "market_share", weightBonus: 0.3 },
          { text: "브랜드 인지도", value: "brand", weightBonus: 0.2 }
        ]
      }
    ]
  },
  hiring: {
    name: "채용 결정",
    description: "신규 인력 채용 의사결정",
    icon: "👥",
    questions: [
      {
        id: "q1",
        text: "채용의 주요 목적은 무엇인가요?",
        weight: 0.4,
        category: "전략적",
        options: [
          { text: "긴급한 공백 메우기", value: "urgent", weightBonus: 0.2 },
          { text: "팀 확장", value: "growth", weightBonus: 0.25 },
          { text: "전문성 보강", value: "expertise", weightBonus: 0.3 }
        ]
      },
      {
        id: "q2",
        text: "가장 중요한 평가 기준은?",
        weight: 0.6,
        category: "평가",
        options: [
          { text: "기술 역량", value: "tech", weightBonus: 0.3 },
          { text: "문화 적합성", value: "culture", weightBonus: 0.25 },
          { text: "경력/경험", value: "experience", weightBonus: 0.2 },
          { text: "성장 가능성", value: "potential", weightBonus: 0.25 }
        ]
      },
      {
        id: "q3",
        text: "최종 결정 시 가장 고려할 요소는?",
        weight: 0.85,
        category: "핵심",
        options: [
          { text: "즉시 기여 가능성", value: "immediate", weightBonus: 0.3 },
          { text: "장기적 성장성", value: "longterm", weightBonus: 0.35 },
          { text: "팀 시너지", value: "synergy", weightBonus: 0.25 },
          { text: "급여 협상 여지", value: "salary", weightBonus: 0.15 }
        ]
      }
    ]
  }
};

function OnboardingFlow({ onComplete, onSkip }) {
  const [step, setStep] = useState('scenario-select'); // scenario-select, questions, summary
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});

  const handleScenarioSelect = (scenarioKey) => {
    setSelectedScenario(scenarioKey);
    setStep('questions');
    setCurrentQuestionIndex(0);
    setAnswers({});
  };

  const handleAnswerSelect = (questionId, optionValue) => {
    const newAnswers = { ...answers, [questionId]: optionValue };
    setAnswers(newAnswers);

    // 다음 질문으로
    const scenario = SCENARIOS[selectedScenario];
    if (currentQuestionIndex < scenario.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // 완료
      setStep('summary');
    }
  };

  const generateCards = () => {
    const scenario = SCENARIOS[selectedScenario];
    const cards = [];

    scenario.questions.forEach(question => {
      const selectedValue = answers[question.id];
      if (!selectedValue) return;

      const selectedOption = question.options.find(opt => opt.value === selectedValue);
      if (!selectedOption) return;

      const finalWeight = Math.min(question.weight + selectedOption.weightBonus, 1.0);

      cards.push({
        id: `onboarding-${question.id}`,
        name: question.text.length > 20 ? question.text.substring(0, 20) + '...' : question.text,
        category: question.category,
        value: selectedOption.text,
        weight: finalWeight,
        trade_offs: [],
        source: `${question.text} → ${selectedOption.text}`
      });
    });

    return cards;
  };

  const handleComplete = () => {
    const cards = generateCards();
    onComplete(cards);
  };

  // 시나리오 선택 화면
  if (step === 'scenario-select') {
    return (
      <div className="onboarding-overlay">
        <div className="onboarding-modal">
          <h2>🎯 시작하기</h2>
          <p className="onboarding-subtitle">어떤 의사결정을 도와드릴까요?</p>

          <div className="scenario-grid">
            {Object.entries(SCENARIOS).map(([key, scenario]) => (
              <button
                key={key}
                className="scenario-card"
                onClick={() => handleScenarioSelect(key)}
              >
                <div className="scenario-icon">{scenario.icon}</div>
                <h3>{scenario.name}</h3>
                <p>{scenario.description}</p>
              </button>
            ))}
          </div>

          <div className="onboarding-actions">
            <button className="btn-skip" onClick={onSkip}>
              건너뛰고 직접 입력
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 질문 화면
  if (step === 'questions') {
    const scenario = SCENARIOS[selectedScenario];
    const currentQuestion = scenario.questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / scenario.questions.length) * 100;

    return (
      <div className="onboarding-overlay">
        <div className="onboarding-modal">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>

          <div className="question-header">
            <span className="question-number">
              질문 {currentQuestionIndex + 1} / {scenario.questions.length}
            </span>
            <span className="question-category">{currentQuestion.category}</span>
          </div>

          <h2 className="question-text">{currentQuestion.text}</h2>

          <div className="weight-indicator">
            <span>가중치:</span>
            <div className="weight-bar">
              <div
                className="weight-fill"
                style={{ width: `${currentQuestion.weight * 100}%` }}
              />
            </div>
            <span>{currentQuestion.weight.toFixed(1)}</span>
          </div>

          <div className="options-grid">
            {currentQuestion.options.map((option) => {
              const totalWeight = currentQuestion.weight + option.weightBonus;
              return (
                <button
                  key={option.value}
                  className="option-card"
                  onClick={() => handleAnswerSelect(currentQuestion.id, option.value)}
                >
                  <div className="option-text">{option.text}</div>
                  <div className="option-bonus">
                    최종 가중치: {totalWeight.toFixed(2)}
                    {option.weightBonus > 0 && (
                      <span className="bonus-badge">+{option.weightBonus}</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          <button className="btn-back" onClick={() => {
            if (currentQuestionIndex > 0) {
              setCurrentQuestionIndex(currentQuestionIndex - 1);
            } else {
              setStep('scenario-select');
            }
          }}>
            ← 이전
          </button>
        </div>
      </div>
    );
  }

  // 요약 화면
  if (step === 'summary') {
    const cards = generateCards();
    const mainCard = cards.reduce((max, card) => card.weight > max.weight ? card : max, cards[0]);

    return (
      <div className="onboarding-overlay">
        <div className="onboarding-modal summary">
          <h2>✅ 온보딩 완료!</h2>

          <div className="summary-stats">
            <div className="stat-box">
              <span className="stat-label">시나리오</span>
              <span className="stat-value">{SCENARIOS[selectedScenario].name}</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">생성된 카드</span>
              <span className="stat-value">{cards.length}개</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">핵심 아젠다</span>
              <span className="stat-value">{mainCard.name}</span>
            </div>
          </div>

          <div className="generated-cards">
            <h3>생성된 카드 미리보기</h3>
            {cards.map((card, idx) => (
              <div key={idx} className="preview-card">
                <div className="preview-header">
                  <span className="preview-name">{card.name}</span>
                  <span className="preview-category">{card.category}</span>
                </div>
                <div className="preview-value">{card.value}</div>
                <div className="preview-weight">
                  가중치: {card.weight.toFixed(2)}
                  <div className="preview-weight-bar">
                    <div
                      className="preview-weight-fill"
                      style={{ width: `${card.weight * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="summary-actions">
            <button className="btn-confirm" onClick={handleComplete}>
              이 카드들로 시작하기
            </button>
            <button className="btn-retry" onClick={() => {
              setStep('scenario-select');
              setAnswers({});
              setCurrentQuestionIndex(0);
            }}>
              다시 시작
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default OnboardingFlow;
