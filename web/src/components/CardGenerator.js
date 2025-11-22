import React, { useState } from 'react';
import './CardGenerator.css';

function CardGenerator({ onGenerate, loading }) {
  const [text, setText] = useState('');
  const [showInput, setShowInput] = useState(false);

  const handleGenerate = () => {
    if (!text.trim()) {
      alert('텍스트를 입력하세요');
      return;
    }

    onGenerate(text);
    setText('');
    setShowInput(false);
  };

  const exampleTexts = [
    {
      title: '점심 선택',
      text: `예산은 12000원이야.
시간은 30분밖에 없어.
동행자가 3명이라서 단체석 필요해.
날씨가 비라서 실내가 좋을 것 같아.`
    },
    {
      title: '제품 전략',
      text: `예산은 50만 달러 가용 가능해.
마감 기한은 6개월이야. 정말 촉박해.
현지화 전략이 매우 중요해.
사용자 데이터 분석 결과, 모바일 트래픽이 80%야.`
    }
  ];

  return (
    <div className="card-generator">
      <div className="generator-header">
        <h3>🤖 AI 카드 자동 생성</h3>
        <button
          className="btn-toggle"
          onClick={() => setShowInput(!showInput)}
        >
          {showInput ? '닫기' : '텍스트 입력'}
        </button>
      </div>

      {showInput && (
        <div className="generator-content">
          <textarea
            className="text-input"
            placeholder="회의록이나 메모를 입력하면 AI가 자동으로 카드를 생성합니다..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
          />

          <div className="generator-actions">
            <button
              className="btn-generate"
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? '생성 중...' : '카드 생성'}
            </button>
          </div>

          <div className="examples">
            <p className="examples-label">예시 템플릿:</p>
            <div className="example-buttons">
              {exampleTexts.map((example, idx) => (
                <button
                  key={idx}
                  className="btn-example"
                  onClick={() => setText(example.text)}
                >
                  {example.title}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CardGenerator;
