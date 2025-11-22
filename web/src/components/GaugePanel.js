import React from 'react';
import './GaugePanel.css';

function GaugePanel({ gauges, deck }) {
  const renderGauge = (gauge) => {
    // value: -1.0 ~ 1.0
    const position = ((gauge.value + 1) / 2) * 100; // 0 ~ 100%

    const [left, right] = gauge.dimension.split('-');

    return (
      <div key={gauge.dimension} className="gauge-item">
        <div className="gauge-header">
          <span className="gauge-dimension">{gauge.dimension}</span>
          <span className="gauge-value">
            {gauge.value > 0 ? '+' : ''}{gauge.value.toFixed(2)}
          </span>
        </div>

        <div className="gauge-labels">
          <span className="label-left">{left}</span>
          <span className="label-right">{right}</span>
        </div>

        <div className="gauge-bar">
          <div className="gauge-track">
            {[...Array(10)].map((_, i) => (
              <div
                key={i}
                className={`gauge-segment ${Math.floor(position / 10) === i ? 'active' : ''
                  }`}
              />
            ))}
          </div>
          <div
            className="gauge-indicator"
            style={{ left: `${position}%` }}
          />
        </div>

        <div className="gauge-interpretation">
          {getInterpretation(gauge.value, left, right)}
        </div>
      </div>
    );
  };

  const getInterpretation = (value, left, right) => {
    if (value < -0.5) return `${left} 성향 강함`;
    if (value > 0.5) return `${right} 성향 강함`;
    return '중립적 균형';
  };

  return (
    <div className="gauge-panel">
      <div className="panel-header">
        <h3>📊 성향 게이지</h3>
        <p className="panel-subtitle">현재 덱의 전체적인 의사결정 성향</p>
      </div>

      {(!gauges || gauges.length === 0) && (
        <div className="empty-gauges">
          <p>카드를 추가하면 게이지가 표시됩니다</p>
        </div>
      )}

      <div className="gauges-list">
        {gauges?.map((gauge) => renderGauge(gauge))}
      </div>

      {deck && deck.cards && deck.cards.length > 0 && (
        <div className="deck-summary">
          <h4>덱 요약</h4>
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-label">총 카드</span>
              <span className="stat-value">{deck.cards.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">평균 가중치</span>
              <span className="stat-value">
                {(
                  deck.cards.reduce((sum, c) => sum + c.weight, 0) /
                  deck.cards.length
                ).toFixed(2)}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">사용률</span>
              <span className="stat-value">
                {Math.round((deck.cards.length / deck.max_slots) * 100)}%
              </span>
            </div>
          </div>

          <div className="category-breakdown">
            <h5>카테고리 분포</h5>
            {getCategoryBreakdown(deck.cards).map(({ category, count, percentage }) => (
              <div key={category} className="category-bar">
                <span className="category-name">{category}</span>
                <div className="category-progress">
                  <div
                    className="category-fill"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="category-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function getCategoryBreakdown(cards) {
  const categoryCount = {};
  cards.forEach((card) => {
    categoryCount[card.category] = (categoryCount[card.category] || 0) + 1;
  });

  return Object.entries(categoryCount)
    .map(([category, count]) => ({
      category,
      count,
      percentage: (count / cards.length) * 100
    }))
    .sort((a, b) => b.count - a.count);
}

export default GaugePanel;
