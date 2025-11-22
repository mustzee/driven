import React, { useState } from 'react';
import './DeckBoard.css';
import Card from './Card';

function DeckBoard({ deck, onAddCard, onRemoveCard, onUpdateGauges }) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCard, setNewCard] = useState({
    name: '',
    category: '경제적',
    value: '',
    weight: 0.5
  });

  if (!deck) {
    return (
      <div className="deck-board loading">
        <p>덱 로딩 중...</p>
      </div>
    );
  }

  const handleAddCard = () => {
    if (!newCard.name) {
      alert('카드 이름을 입력하세요');
      return;
    }

    const cardData = {
      id: `card-${Date.now()}`,
      name: newCard.name,
      category: newCard.category,
      value: parseFloat(newCard.value) || newCard.value,
      weight: parseFloat(newCard.weight),
      trade_offs: []
    };

    onAddCard(cardData);
    setNewCard({ name: '', category: '경제적', value: '', weight: 0.5 });
    setShowAddForm(false);
  };

  const availableSlots = deck.max_slots - (deck.cards?.length || 0);
  const isFull = availableSlots <= 0;

  return (
    <div className="deck-board">
      <div className="deck-header">
        <div>
          <h2>{deck.goal}</h2>
          <p className="deck-info">
            {deck.cards?.length || 0} / {deck.max_slots} 카드
            {isFull && <span className="full-badge">덱 가득참 (인지 한계)</span>}
          </p>
        </div>

        {!isFull && (
          <button
            className="btn-add"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            + 카드 추가
          </button>
        )}
      </div>

      {showAddForm && (
        <div className="add-card-form">
          <input
            type="text"
            placeholder="카드 이름 (예: 예산, 시간)"
            value={newCard.name}
            onChange={(e) => setNewCard({ ...newCard, name: e.target.value })}
          />

          <select
            value={newCard.category}
            onChange={(e) => setNewCard({ ...newCard, category: e.target.value })}
          >
            <option value="생리적">생리적</option>
            <option value="경제적">경제적</option>
            <option value="제약적">제약적</option>
            <option value="사회적">사회적</option>
            <option value="환경적">환경적</option>
            <option value="심리적">심리적</option>
          </select>

          <input
            type="text"
            placeholder="값 (숫자 또는 텍스트)"
            value={newCard.value}
            onChange={(e) => setNewCard({ ...newCard, value: e.target.value })}
          />

          <div className="weight-input">
            <label>가중치: {newCard.weight}</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={newCard.weight}
              onChange={(e) => setNewCard({ ...newCard, weight: e.target.value })}
            />
          </div>

          <div className="form-actions">
            <button className="btn-confirm" onClick={handleAddCard}>
              추가
            </button>
            <button className="btn-cancel" onClick={() => setShowAddForm(false)}>
              취소
            </button>
          </div>
        </div>
      )}

      <div className="cards-grid">
        {deck.cards?.map((card) => (
          <Card
            key={card.id}
            card={card}
            onRemove={() => {
              onRemoveCard(card.id);
              setTimeout(onUpdateGauges, 100);
            }}
          />
        ))}

        {!deck.cards || deck.cards.length === 0 ? (
          <div className="empty-state">
            <p>카드를 추가하여 의사결정을 시작하세요</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default DeckBoard;
