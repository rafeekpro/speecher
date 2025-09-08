import React, { useState, useEffect } from 'react';
import { getTranscriptionHistory, deleteTranscription, getTranscriptionById } from '../services/api';
import { 
  Search, 
  Calendar, 
  Trash2, 
  Eye, 
  Download,
  RefreshCw,
  ChevronLeft,
  ChevronRight 
} from 'lucide-react';
import './History.css';

const History = ({ onSelectTranscription }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProvider, setFilterProvider] = useState('all');
  const [filterLanguage, setFilterLanguage] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getTranscriptionHistory(100);
      setHistory(data);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this transcription?')) {
      try {
        await deleteTranscription(id);
        setHistory(history.filter(item => item.id !== id));
      } catch (error) {
        alert('Failed to delete transcription');
      }
    }
  };

  const handleView = async (id) => {
    try {
      const transcription = await getTranscriptionById(id);
      onSelectTranscription(transcription);
    } catch (error) {
      alert('Failed to load transcription');
    }
  };

  const exportHistory = () => {
    const dataStr = JSON.stringify(filteredHistory, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `speecher_history_${new Date().toISOString()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Filter logic
  const filteredHistory = history.filter(item => {
    const matchesSearch = searchTerm === '' || 
      item.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.transcript?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesProvider = filterProvider === 'all' || item.provider === filterProvider;
    const matchesLanguage = filterLanguage === 'all' || item.language === filterLanguage;
    
    const itemDate = new Date(item.created_at);
    const matchesDateFrom = !dateFrom || itemDate >= new Date(dateFrom);
    const matchesDateTo = !dateTo || itemDate <= new Date(dateTo);
    
    return matchesSearch && matchesProvider && matchesLanguage && matchesDateFrom && matchesDateTo;
  });

  // Pagination
  const totalPages = Math.ceil(filteredHistory.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedHistory = filteredHistory.slice(startIndex, startIndex + itemsPerPage);

  // Get unique providers and languages for filters
  const providers = [...new Set(history.map(item => item.provider))];
  const languages = [...new Set(history.map(item => item.language))];

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="history-loading">
        <div className="spinner"></div>
        <p>Loading history...</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-controls">
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search transcriptions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filters">
          <select 
            value={filterProvider}
            onChange={(e) => setFilterProvider(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Providers</option>
            {providers.map(p => (
              <option key={p} value={p}>{p?.toUpperCase()}</option>
            ))}
          </select>

          <select 
            value={filterLanguage}
            onChange={(e) => setFilterLanguage(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Languages</option>
            {languages.map(l => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>

          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            placeholder="From date"
            className="date-input"
          />

          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            placeholder="To date"
            className="date-input"
          />
        </div>

        <div className="history-actions">
          <button onClick={loadHistory} className="action-btn">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button onClick={exportHistory} className="action-btn">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      <div className="history-stats">
        <div className="stat">
          <span className="stat-label">Total:</span>
          <span className="stat-value">{filteredHistory.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Showing:</span>
          <span className="stat-value">
            {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredHistory.length)}
          </span>
        </div>
      </div>

      <div className="history-table">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Filename</th>
              <th>Provider</th>
              <th>Language</th>
              <th>Duration</th>
              <th>Cost</th>
              <th>Transcript Preview</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedHistory.map(item => (
              <tr key={item.id}>
                <td className="date-cell">
                  <Calendar size={14} />
                  {formatDate(item.created_at)}
                </td>
                <td className="filename-cell">{item.filename}</td>
                <td>
                  <span className={`provider-badge ${item.provider}`}>
                    {item.provider?.toUpperCase()}
                  </span>
                </td>
                <td>{item.language}</td>
                <td>{formatDuration(item.duration)}</td>
                <td>${item.cost_estimate?.toFixed(4) || '0.00'}</td>
                <td className="transcript-preview">
                  {item.transcript?.substring(0, 100)}...
                </td>
                <td className="actions-cell">
                  <button
                    onClick={() => handleView(item.id)}
                    className="icon-btn"
                    title="View"
                  >
                    <Eye size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="icon-btn delete"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {paginatedHistory.length === 0 && (
          <div className="no-results">
            <p>No transcriptions found</p>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            <ChevronLeft size={16} />
          </button>
          
          <span className="page-info">
            Page {currentPage} of {totalPages}
          </span>
          
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
};

export default History;