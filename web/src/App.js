import React, { useState, useEffect } from 'react';
import './App.css';
import DeckBoard from './components/DeckBoard';
import GaugePanel from './components/GaugePanel';
import CardGenerator from './components/CardGenerator';
import NetworkGraph from './components/NetworkGraph';
import OnboardingFlow from './components/OnboardingFlow';
import DecisionFramework from './components/DecisionFramework';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8080/api/v1';

function App() {
  const [deck, setDeck] = useState(null);
  const [gauges, setGauges] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(true);

  // 초기 덱 생성
  useEffect(() => {
    createInitialDeck();
  }, []);

  const createInitialDeck = async () => {
    try {
      const response = await axios.post(`${API_BASE}/decks`, {
        id: 'demo-deck-' + Date.now(),
        goal: '의사결정 목표를 입력하세요',
        max_slots: 7
      });
      setDeck(response.data);
    } catch (error) {
      console.error('Failed to create deck:', error);
      // Fallback: 로컬 덱
      setDeck({
        id: 'local-deck',
        goal: '의사결정 목표를 입력하세요',
        max_slots: 7,
        cards: []
      });
    }
  };

  const addCard = async (cardData) => {
    if (!deck) return;

    try {
      const response = await axios.post(`${API_BASE}/decks/${deck.id}/cards`, cardData);
      setDeck(response.data);
      await updateGauges();
    } catch (error) {
      console.error('Failed to add card:', error);
      // Fallback: 로컬 업데이트
      const newCard = {
        ...cardData,
        id: cardData.id || `card-${Date.now()}`
      };
      setDeck(prev => ({
        ...prev,
        cards: [...prev.cards, newCard]
      }));
    }
  };

  const removeCard = async (cardId) => {
    if (!deck) return;

    try {
      const response = await axios.delete(`${API_BASE}/decks/${deck.id}/cards/${cardId}`);
      setDeck(response.data);
      await updateGauges();
    } catch (error) {
      console.error('Failed to remove card:', error);
      // Fallback
      setDeck(prev => ({
        ...prev,
        cards: prev.cards.filter(c => c.id !== cardId)
      }));
    }
  };

  const updateGauges = async () => {
    if (!deck || !deck.cards || deck.cards.length === 0) {
      setGauges([]);
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/decks/${deck.id}/gauges`);
      setGauges(response.data.gauges || []);
    } catch (error) {
      console.error('Failed to update gauges:', error);
    }
  };

  const generateCardsFromText = async (text) => {
    setLoading(true);
    try {
      // 그래프 분석 먼저 실행
      const graphResponse = await axios.post(`${API_BASE}/graph/analyze`, {
        text,
        max_cards: 10
      });

      if (graphResponse.data.graph) {
        setGraphData(graphResponse.data.graph);
      }

      // 생성된 카드들 추가
      const generatedCards = graphResponse.data.cards || [];
      for (const cardData of generatedCards) {
        await addCard({
          id: `ai-${Date.now()}-${Math.random()}`,
          ...cardData,
          trade_offs: cardData.trade_offs || []
        });
      }
    } catch (error) {
      console.error('Failed to generate cards:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOnboardingComplete = async (cards) => {
    setShowOnboarding(false);

    // 온보딩 카드들 추가
    for (const cardData of cards) {
      await addCard(cardData);
    }
  };

  const handleOnboardingSkip = () => {
    setShowOnboarding(false);
  };

  return (
    <div className="App">
      {showOnboarding && (
        <OnboardingFlow
          onComplete={handleOnboardingComplete}
          onSkip={handleOnboardingSkip}
        />
      )}

      <header className="app-header">
        <h1>🎴 Cognitive Deck</h1>
        <p className="subtitle">데이터 기반 의사결정 시스템</p>
        {!showOnboarding && (
          <button
            className="btn-restart-onboarding"
            onClick={() => setShowOnboarding(true)}
          >
            ↻ 온보딩 다시 시작
          </button>
        )}
      </header>

      <div className="app-container">
        {/* 왼쪽: 카드 보드 */}
        <div className="left-panel">
          <CardGenerator
            onGenerate={generateCardsFromText}
            loading={loading}
          />

          <DeckBoard
            deck={deck}
            onAddCard={addCard}
            onRemoveCard={removeCard}
            onUpdateGauges={updateGauges}
          />
        </div>

        {/* 오른쪽: 게이지 & 분석 */}
        <div className="right-panel">
          <GaugePanel gauges={gauges} deck={deck} />
        </div>
      </div>

      {/* 그래프 시각화 (전체 너비) */}
      {graphData && graphData.nodes && graphData.nodes.length > 0 && (
        <div className="graph-section">
          <NetworkGraph graphData={graphData} />
        </div>
      )}

      {/* Decision Framework (전체 너비) */}
      <div className="decision-section">
        <DecisionFramework
          currentCards={deck?.cards || []}
          onAddCard={addCard}
        />
      </div>
    </div>
  );
}

export default App;
