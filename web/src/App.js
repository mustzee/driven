import React, { useState, useEffect } from 'react';
import './App.css';
import DeckBoard from './components/DeckBoard';
import GaugePanel from './components/GaugePanel';
import CardGenerator from './components/CardGenerator';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8080/api/v1';

function App() {
  const [deck, setDeck] = useState(null);
  const [gauges, setGauges] = useState([]);
  const [loading, setLoading] = useState(false);

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
      const response = await axios.post(`${API_BASE}/ai/generate-cards`, {
        text,
        goal: deck?.goal || '',
        max_cards: 7
      });

      // 생성된 카드들 추가
      const generatedCards = response.data.generated_cards || [];
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

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎴 Cognitive Deck</h1>
        <p className="subtitle">데이터 기반 의사결정 시스템</p>
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
    </div>
  );
}

export default App;
