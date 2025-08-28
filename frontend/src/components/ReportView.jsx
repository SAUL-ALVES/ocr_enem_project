import React from 'react';

const ReportView = ({ reportData, userCode, onClose }) => {
  if (!reportData) return null;

  const { acertos, total_questoes } = reportData;
  const percentual = acertos / total_questoes;
  const percentualDisplay = (percentual * 100).toFixed(1);

  const radius = 65;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - percentual * circumference;

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <button className="close-button" onClick={onClose}>&times;</button>
        
        <h3>Seu Relatório de Desempenho</h3>
        <p className="user-code">Código: {userCode}</p>

        <div className="score-circle">
          <svg>
            <circle className="circle-bg" cx="75" cy="75" r={radius}></circle>
            <circle
              className="circle-progress"
              cx="75"
              cy="75"
              r={radius}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
            ></circle>
          </svg>
          <div className="score-text">{percentualDisplay}%</div>
        </div>

        <p className="score-details">
          Você acertou <strong>{acertos}</strong> de <strong>{total_questoes}</strong> questões.
        </p>

        <button id="correct-button" style={{marginTop: '30px'}} onClick={onClose}>
          Corrigir Outro Gabarito
        </button>
      </div>
    </div>
  );
};

export default ReportView;