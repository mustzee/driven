import React from 'react';
import './Card.css';

const categoryEmojis = {
  '생리적': '🍎',
  '경제적': '💰',
  '제약적': '⏰',
  '사회적': '👥',
  '환경적': '🌤️',
  '심리적': '🧠'
};

const categoryColors = {
  '생리적': '#ff6b6b',
  '경제적': '#51cf66',
  '제약적': '#339af0',
  '사회적': '#ff6b9d',
  '환경적': '#ffd43b',
  '심리적': '#ae3ec9'
};

function Card({ card, onRemove }) {
  const emoji = categoryEmojis[card.category] || '🎴';
  const color = categoryColors[card.category] || '#667eea';

  const weightWidth = Math.round(card.weight * 100);

  return (
    <div className="card" style={{ borderLeftColor: color }}>
      <button className="card-remove" onClick={onRemove}>
        ×
      </button>

      <div className="card-header">
        <span className="card-emoji">{emoji}</span>
        <span className="card-category">{card.category}</span>
      </div>

      <h3 className="card-name">{card.name}</h3>

      <div className="card-value">
        {typeof card.value === 'number'
          ? card.value.toLocaleString()
          : card.value}
      </div>

      <div className="card-weight">
        <div className="weight-label">
          가중치 <strong>{card.weight}</strong>
        </div>
        <div className="weight-bar">
          <div
            className="weight-fill"
            style={{ width: `${weightWidth}%`, background: color }}
          />
        </div>
      </div>

      {card.trade_offs && card.trade_offs.length > 0 && (
        <div className="card-tradeoffs">
          {card.trade_offs.map((to, idx) => (
            <div key={idx} className="tradeoff-item">
              <span className="tradeoff-label">{to.dimension}</span>
              <span className={`tradeoff-value ${to.value > 0 ? 'positive' : 'negative'}`}>
                {to.value > 0 ? '+' : ''}{to.value.toFixed(1)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Card;
