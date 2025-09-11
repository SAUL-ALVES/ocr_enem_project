import React, { forwardRef } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const Sidebar = ({ history, searchCode, onSearch, selectedDate, onDateChange, onClearSearch }) => {

  const CalendarIcon = forwardRef(({ onClick }, ref) => (
    <svg onClick={onClick} ref={ref} className="calendar-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>
    </svg>
  ));

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">Histórico</h2>
      </div>

      <div className="search-area">
        <h3>Buscar por Histórico</h3>
        <div className="search-container">
          <input
            type="text"
            placeholder="Digite o código do aluno..."
            className="search-input"
            value={searchCode}
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
      </div>

      <ul className="history-list">
        {history.length > 0 ? (
          history.map((item, index) => (
            <li key={index} className="history-item">
              <div className="history-item-date">{item.date}</div>
              <div className="history-item-score">
                Acertos: <strong>{item.acertos} / {item.total_questoes}</strong>
              </div>
            </li>
          ))
        ) : (
          <p className="no-history">Digite um código para buscar.</p>
        )}
      </ul>
      
      {searchCode && (
        <div className="sidebar-footer">
          <button onClick={onClearSearch} className="clear-button">
            Limpar Busca
          </button>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;