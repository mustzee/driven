import React, { useState } from 'react';
import './App.css';
import GuidedDecisionFlow from './components/GuidedDecisionFlow';

/**
 * Cognitive Deck - 데이터 기반 의사결정 시스템
 *
 * 모노아키텍처: 단일 가이드형 워크플로우로 통합
 * 1. 프레임워크 선택 (장단점 설명)
 * 2. 프레임워크 정보 및 필요 카드 설명
 * 3. 카드 작성
 * 4. 분석 실행
 * 5. 결과 및 추천
 */
function App() {
  const [showGuidedFlow, setShowGuidedFlow] = useState(true);

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎴 Cognitive Deck</h1>
        <p className="subtitle">데이터 기반 의사결정 시스템</p>
      </header>

      {showGuidedFlow ? (
        <GuidedDecisionFlow />
      ) : (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <button
            className="btn-restart-onboarding"
            onClick={() => setShowGuidedFlow(true)}
          >
            🎯 가이드형 의사결정 시작
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
