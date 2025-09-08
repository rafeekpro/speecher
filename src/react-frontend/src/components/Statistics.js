import React, { useState, useEffect } from 'react';
import { getStatistics } from '../services/api';
import { 
  TrendingUp, 
  DollarSign, 
  Clock, 
  FileText,
  PieChart,
  BarChart,
  Globe
} from 'lucide-react';
import './Statistics.css';

const Statistics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('all');

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    setLoading(true);
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }).format(amount || 0);
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0h 0m';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const calculatePercentage = (value, total) => {
    if (!total) return 0;
    return Math.round((value / total) * 100);
  };

  if (loading) {
    return (
      <div className="statistics-loading">
        <div className="spinner"></div>
        <p>Loading statistics...</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="statistics-error">
        <p>Failed to load statistics</p>
        <button onClick={loadStatistics}>Retry</button>
      </div>
    );
  }

  const totalCost = stats.provider_statistics?.reduce((sum, p) => sum + (p.total_cost || 0), 0) || 0;
  const totalDuration = stats.provider_statistics?.reduce((sum, p) => sum + (p.total_duration || 0), 0) || 0;

  return (
    <div className="statistics-container">
      <div className="stats-header">
        <h3>Usage Overview</h3>
        <select 
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="time-range-select"
        >
          <option value="all">All Time</option>
          <option value="month">This Month</option>
          <option value="week">This Week</option>
          <option value="today">Today</option>
        </select>
      </div>

      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">
            <FileText size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Transcriptions</span>
            <span className="stat-value">{stats.total_transcriptions || 0}</span>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">
            <Clock size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Duration</span>
            <span className="stat-value">{formatDuration(totalDuration)}</span>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">
            <DollarSign size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Cost</span>
            <span className="stat-value">{formatCurrency(totalCost)}</span>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Avg Cost/Min</span>
            <span className="stat-value">
              {formatCurrency(totalDuration ? (totalCost / (totalDuration / 60)) : 0)}
            </span>
          </div>
        </div>
      </div>

      <div className="stats-sections">
        <div className="stats-section">
          <h4>
            <PieChart size={20} />
            Provider Distribution
          </h4>
          <div className="provider-stats">
            {stats.provider_statistics?.map(provider => (
              <div key={provider._id} className="provider-stat">
                <div className="provider-header">
                  <span className={`provider-name ${provider._id}`}>
                    {provider._id?.toUpperCase()}
                  </span>
                  <span className="provider-count">{provider.count} files</span>
                </div>
                <div className="provider-bar">
                  <div 
                    className={`provider-fill ${provider._id}`}
                    style={{ 
                      width: `${calculatePercentage(provider.count, stats.total_transcriptions)}%` 
                    }}
                  />
                </div>
                <div className="provider-details">
                  <span>Duration: {formatDuration(provider.total_duration)}</span>
                  <span>Cost: {formatCurrency(provider.total_cost)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="stats-section">
          <h4>
            <BarChart size={20} />
            Recent Activity
          </h4>
          <div className="recent-files">
            {stats.recent_files?.length > 0 ? (
              <ul>
                {stats.recent_files.map((file, index) => (
                  <li key={index} className="recent-file">
                    <FileText size={14} />
                    {file}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-activity">No recent activity</p>
            )}
          </div>
        </div>

        <div className="stats-section">
          <h4>
            <Globe size={20} />
            Language Usage
          </h4>
          <div className="language-stats">
            {stats.language_statistics ? (
              Object.entries(stats.language_statistics).map(([lang, count]) => (
                <div key={lang} className="language-stat">
                  <span className="language-code">{lang}</span>
                  <span className="language-count">{count}</span>
                </div>
              ))
            ) : (
              <p className="no-data">No language data available</p>
            )}
          </div>
        </div>
      </div>

      <div className="stats-insights">
        <h4>💡 Insights</h4>
        <div className="insights-grid">
          <div className="insight">
            <span className="insight-label">Most Used Provider:</span>
            <span className="insight-value">
              {stats.provider_statistics?.[0]?._id?.toUpperCase() || 'N/A'}
            </span>
          </div>
          <div className="insight">
            <span className="insight-label">Average File Duration:</span>
            <span className="insight-value">
              {formatDuration(
                stats.total_transcriptions ? totalDuration / stats.total_transcriptions : 0
              )}
            </span>
          </div>
          <div className="insight">
            <span className="insight-label">Average Cost per File:</span>
            <span className="insight-value">
              {formatCurrency(
                stats.total_transcriptions ? totalCost / stats.total_transcriptions : 0
              )}
            </span>
          </div>
        </div>
      </div>

      <div className="stats-footer">
        <button onClick={loadStatistics} className="refresh-btn">
          Refresh Statistics
        </button>
        <p className="last-updated">
          Last updated: {new Date().toLocaleString()}
        </p>
      </div>
    </div>
  );
};

export default Statistics;