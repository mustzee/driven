import React, { useEffect, useRef, useState } from 'react';
import './NetworkGraph.css';

/**
 * D3.js Force-Directed 네트워크 그래프
 * 메인스트림/서브스트림 시각화
 */
function NetworkGraph({ graphData }) {
  const svgRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
      return;
    }

    renderGraph();
  }, [graphData]);

  const renderGraph = () => {
    const svg = svgRef.current;
    if (!svg) return;

    // SVG 초기화
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }

    const width = svg.clientWidth;
    const height = svg.clientHeight;

    const { nodes, links } = graphData;

    // 노드 위치 초기화 (간단한 force simulation)
    const centerX = width / 2;
    const centerY = height / 2;

    // 메인스트림 vs 서브스트림 분리
    const mainNodes = nodes.filter(n => n.is_mainstream);
    const subNodes = nodes.filter(n => !n.is_mainstream);

    // 메인스트림: 중앙 원형 배치
    mainNodes.forEach((node, i) => {
      const angle = (i / mainNodes.length) * 2 * Math.PI;
      const radius = Math.min(width, height) / 4;
      node.x = centerX + radius * Math.cos(angle);
      node.y = centerY + radius * Math.sin(angle);
    });

    // 서브스트림: 외곽 배치
    subNodes.forEach((node, i) => {
      const angle = (i / subNodes.length) * 2 * Math.PI;
      const radius = Math.min(width, height) / 2.5;
      node.x = centerX + radius * Math.cos(angle);
      node.y = centerY + radius * Math.sin(angle);
    });

    // 간단한 force simulation (수동)
    for (let iteration = 0; iteration < 100; iteration++) {
      // 노드 간 반발력
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const nodeA = nodes[i];
          const nodeB = nodes[j];

          const dx = nodeB.x - nodeA.x;
          const dy = nodeB.y - nodeA.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;

          const repulsion = 50 / distance;
          const fx = (dx / distance) * repulsion;
          const fy = (dy / distance) * repulsion;

          nodeA.x -= fx;
          nodeA.y -= fy;
          nodeB.x += fx;
          nodeB.y += fy;
        }
      }

      // 링크 인력
      links.forEach(link => {
        const source = nodes.find(n => n.id === link.source);
        const target = nodes.find(n => n.id === link.target);

        if (!source || !target) return;

        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const distance = Math.sqrt(dx * dx + dy * dy) || 1;

        const attraction = (distance - 100) * link.weight * 0.1;
        const fx = (dx / distance) * attraction;
        const fy = (dy / distance) * attraction;

        source.x += fx;
        source.y += fy;
        target.x -= fx;
        target.y -= fy;
      });

      // 중심 인력 (메인스트림만)
      mainNodes.forEach(node => {
        const dx = centerX - node.x;
        const dy = centerY - node.y;
        node.x += dx * 0.05;
        node.y += dy * 0.05;
      });
    }

    // 링크 그리기
    const linkGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    linkGroup.setAttribute('class', 'links');

    links.forEach(link => {
      const source = nodes.find(n => n.id === link.source);
      const target = nodes.find(n => n.id === link.target);

      if (!source || !target) return;

      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', source.x);
      line.setAttribute('y1', source.y);
      line.setAttribute('x2', target.x);
      line.setAttribute('y2', target.y);
      line.setAttribute('stroke', '#999');
      line.setAttribute('stroke-opacity', link.weight);
      line.setAttribute('stroke-width', 1 + link.weight * 3);

      linkGroup.appendChild(line);
    });

    svg.appendChild(linkGroup);

    // 노드 그리기
    const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    nodeGroup.setAttribute('class', 'nodes');

    nodes.forEach(node => {
      const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      group.setAttribute('class', 'node');
      group.setAttribute('transform', `translate(${node.x}, ${node.y})`);

      // 크기 = 중심성 점수
      const radius = 10 + node.centrality_score * 40;

      // 원
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', radius);
      circle.setAttribute('fill', node.is_mainstream ? '#667eea' : '#e0e0e0');
      circle.setAttribute('stroke', node.is_mainstream ? '#4c51bf' : '#999');
      circle.setAttribute('stroke-width', node.is_mainstream ? 3 : 1);
      circle.style.cursor = 'pointer';

      // 호버 효과
      circle.addEventListener('mouseenter', () => {
        circle.setAttribute('stroke-width', 4);
        circle.setAttribute('fill-opacity', 0.8);
        setSelectedNode(node);
      });

      circle.addEventListener('mouseleave', () => {
        circle.setAttribute('stroke-width', node.is_mainstream ? 3 : 1);
        circle.setAttribute('fill-opacity', 1);
      });

      group.appendChild(circle);

      // 라벨
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.textContent = node.label;
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dy', radius + 15);
      text.setAttribute('font-size', '12px');
      text.setAttribute('font-weight', node.is_mainstream ? 'bold' : 'normal');
      text.setAttribute('fill', '#333');

      group.appendChild(text);

      nodeGroup.appendChild(group);
    });

    svg.appendChild(nodeGroup);

    // 범례
    renderLegend(svg, width, height);
  };

  const renderLegend = (svg, width, height) => {
    const legendGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    legendGroup.setAttribute('class', 'legend');
    legendGroup.setAttribute('transform', `translate(${width - 180}, 20)`);

    // 배경
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', 160);
    bg.setAttribute('height', 80);
    bg.setAttribute('fill', 'white');
    bg.setAttribute('stroke', '#ddd');
    bg.setAttribute('rx', 5);
    legendGroup.appendChild(bg);

    // 메인스트림
    const mainCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    mainCircle.setAttribute('cx', 20);
    mainCircle.setAttribute('cy', 25);
    mainCircle.setAttribute('r', 8);
    mainCircle.setAttribute('fill', '#667eea');
    mainCircle.setAttribute('stroke', '#4c51bf');
    mainCircle.setAttribute('stroke-width', 2);
    legendGroup.appendChild(mainCircle);

    const mainText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    mainText.textContent = '메인스트림';
    mainText.setAttribute('x', 35);
    mainText.setAttribute('y', 30);
    mainText.setAttribute('font-size', '12px');
    legendGroup.appendChild(mainText);

    // 서브스트림
    const subCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    subCircle.setAttribute('cx', 20);
    subCircle.setAttribute('cy', 55);
    subCircle.setAttribute('r', 8);
    subCircle.setAttribute('fill', '#e0e0e0');
    subCircle.setAttribute('stroke', '#999');
    legendGroup.appendChild(subCircle);

    const subText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    subText.textContent = '서브스트림';
    subText.setAttribute('x', 35);
    subText.setAttribute('y', 60);
    subText.setAttribute('font-size', '12px');
    legendGroup.appendChild(subText);

    svg.appendChild(legendGroup);
  };

  return (
    <div className="network-graph-container">
      <div className="graph-header">
        <h3>🕸️ 카드 관계 네트워크</h3>
        <p className="graph-subtitle">
          노드 크기 = 중심성 | 굵은 선 = 강한 연관성
        </p>
      </div>

      <svg
        ref={svgRef}
        className="network-svg"
        width="100%"
        height="600"
      />

      {selectedNode && (
        <div className="node-details">
          <h4>{selectedNode.label}</h4>
          <div className="detail-row">
            <span className="detail-label">유형:</span>
            <span className={`detail-badge ${selectedNode.is_mainstream ? 'mainstream' : 'substream'}`}>
              {selectedNode.is_mainstream ? '메인스트림' : '서브스트림'}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">카테고리:</span>
            <span>{selectedNode.category}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">가중치:</span>
            <span>{selectedNode.weight.toFixed(2)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">중심성 점수:</span>
            <span>{selectedNode.centrality_score.toFixed(4)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">PageRank:</span>
            <span>{selectedNode.pagerank.toFixed(4)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">매개 중심성:</span>
            <span>{selectedNode.betweenness.toFixed(4)}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default NetworkGraph;
