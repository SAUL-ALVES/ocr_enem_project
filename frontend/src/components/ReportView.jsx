import React from 'react';


const ReportView = ({ result, onClose }) => {
  
  if (!result) return null;


  const codigoAluno = result?.codigo_aluno ?? 'N/A';
  const analise = result?.analise;

  
  const acertos = analise?.acertos ?? 0;
  const totalQuestoes = analise?.total_questoes ?? 0;


  const percentual = totalQuestoes > 0 ? (acertos / totalQuestoes) : 0;
  const percentualDisplay = (percentual * 100).toFixed(0); 

  
  const radius = 65;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - percentual * circumference;

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <button className="close-button" onClick={onClose}>&times;</button>
        
        <h3>Seu Relatório de Desempenho</h3>
        {/* Exibe o código do aluno extraído */}
        <p className="user-code">Código: {codigoAluno}</p>

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
          {/* Exibe a porcentagem calculada de forma segura */}
          <div className="score-text">{percentualDisplay}%</div>
        </div>

        <p className="score-details">
          Você acertou <strong>{acertos}</strong> de <strong>{totalQuestoes}</strong> questões.
        </p>

        <button id="correct-button" style={{marginTop: '30px'}} onClick={onClose}>
          Corrigir Outro Gabarito
        </button>
      </div>
    </div>
  );
};

export default ReportView;
