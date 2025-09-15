import React, { forwardRef } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const HistoryView = ({ history, onSearch, selectedDate, onDateChange, onSwitchView }) => {
  
  const CalendarIcon = forwardRef(({ onClick }, ref) => (
    <svg onClick={onClick} ref={ref} className="calendar-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>
    </svg>
  ));

  return (
    <div className="history-view">
      <h1>Buscar Histórico</h1>
      <div className="search-container">
        <input
          type="text"
          placeholder="Digite o código do aluno..."
          className="search-input"
          onChange={(e) => onSearch(e.target.value)}
        />
        <DatePicker 
          selected={selectedDate} 
          onChange={onDateChange}
          customInput={<CalendarIcon />}
          dateFormat="dd/MM/yyyy"
          isClearable
        />
      </div>

      <ul className="history-list">
        {history.length > 0 ? (
          history.map((item, index) => (
            <li key={index} className="history-item">
              <span className="history-item-date">{item.date}</span>
              <span className="history-item-score">
                Acertos: <strong>{item.acertos} / {item.total_questoes}</strong>
              </span>
            </li>
          ))
        ) : (
          <p className="no-history">Nenhum resultado para a busca.</p>
        )}
      </ul>
      
      <button onClick={onSwitchView} className="view-toggle-button">
        Corrigir Nova Prova
      </button>
    </div>
  );
};

export default HistoryView;