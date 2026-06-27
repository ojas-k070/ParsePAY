import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

// Import Chart.js elements
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Doughnut as DoughnutChart, Line as LineChart } from 'react-chartjs-2';


ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const CATEGORIES = [
  'Food & Dining',
  'Shopping',
  'Salary & Income',
  'Bills & Utilities',
  'Investment',
  'Travel & Fuel',
  'Cash Withdrawal',
  'Transfer',
  'Medical & Healthcare',
  'Entertainment & Subscriptions',
  'Rent & Maintenance',
  'Education',
  'Other'
];

const Dashboard = () => {
  const { fileId } = useParams();
  const { theme, toggleTheme, toggleSidebar, isSidebarOpen } = useTheme();
  const { user } = useAuth();
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [updatingTxId, setUpdatingTxId] = useState(null);
  const [activeDropdownId, setActiveDropdownId] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [filterTableByCategory, setFilterTableByCategory] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/dashboard-data/${fileId}?t=${Date.now()}`);
      if (res.status === 401 || res.status === 403) {
        setError('Unauthorized access. Please login.');
        return;
      }
      const json = await res.json();
      if (json.error) {
        setError(json.error);
      } else {
        setData(json);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Check connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fileId) {
      fetchDashboardData();
    }
  }, [fileId]);

  // Click outside to close dropdowns
  useEffect(() => {
    const handleOutsideClick = () => {
      setActiveDropdownId(null);
    };
    document.addEventListener('click', handleOutsideClick);
    return () => document.removeEventListener('click', handleOutsideClick);
  }, []);

  const formatMoney = (amount) => {
    return Number(amount).toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const handleCategoryChange = async (txId, newCategory) => {
    setUpdatingTxId(txId);
    try {
      const res = await fetch('/api/update-category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: txId,
          category: newCategory
        })
      });
      const result = await res.json();
      if (result.success) {
        // Refresh data
        const refreshRes = await fetch(`/api/dashboard-data/${fileId}?t=${Date.now()}`);
        const refreshJson = await refreshRes.json();
        setData(refreshJson);
      } else {
        alert('Failed to update category: ' + (result.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Error updating category:', err);
      alert('Error updating category. Check connection.');
    } finally {
      setUpdatingTxId(null);
    }
  };

  const handleSwapAmount = async (txId, e) => {
    e.stopPropagation();
    setActiveDropdownId(null);
    try {
      const res = await fetch('/api/swap-transaction-amount', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transaction_id: txId })
      });
      const result = await res.json();
      if (result.success) {
        // Refresh data
        const refreshRes = await fetch(`/api/dashboard-data/${fileId}?t=${Date.now()}`);
        const refreshJson = await refreshRes.json();
        setData(refreshJson);
      } else {
        alert('Failed to swap amounts: ' + (result.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Error swapping transaction amount:', err);
      alert('Error swapping amounts.');
    }
  };

  // Filtered transactions list based on search query and category filter
  const filteredTransactions = useMemo(() => {
    if (!data || !data.transactions) return [];
    const query = searchQuery.toLowerCase().trim();
    
    return data.transactions.filter(tx => {
      const matchesSearch = !query || 
        tx.particulars.toLowerCase().includes(query) ||
        tx.category.toLowerCase().includes(query) ||
        tx.date.toLowerCase().includes(query);
        
      const matchesCategory = !filterTableByCategory || tx.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }, [data, searchQuery, selectedCategory, filterTableByCategory]);

  // Set default selected category to the one with the highest spending
  useEffect(() => {
    if (data && data.category_totals && !selectedCategory) {
      const categoriesWithSpending = Object.keys(data.category_totals)
        .filter(cat => data.category_totals[cat] > 0);
        
      if (categoriesWithSpending.length > 0) {
        const highestCat = categoriesWithSpending.reduce((a, b) => 
          data.category_totals[a] > data.category_totals[b] ? a : b
        );
        setSelectedCategory(highestCat);
      } else if (CATEGORIES.length > 0) {
        setSelectedCategory(CATEGORIES[0]);
      }
    }
  }, [data, selectedCategory]);

  // Spend summary notification bar statistics
  const spendSummaryStats = useMemo(() => {
    if (!data) return { totalCredited: 0, categoryDebited: 0, percentage: '0.00' };
    
    const totalCredited = data.total_deposits || 0;
    
    const categoryDebited = filteredTransactions
      .filter(tx => tx.category === selectedCategory)
      .reduce((sum, tx) => sum + (tx.withdrawal || 0), 0);
      
    const percentage = totalCredited > 0 ? (categoryDebited / totalCredited) * 100 : 0;
    
    return {
      totalCredited,
      categoryDebited,
      percentage: percentage.toFixed(2)
    };
  }, [data, filteredTransactions, selectedCategory]);

  // Sort categories by count descending
  const sortedCategoryCounts = useMemo(() => {
    if (!data || !data.category_counts) return [];
    return Object.keys(data.category_counts)
      .map(cat => ({ category: cat, count: data.category_counts[cat] }))
      .sort((a, b) => b.count - a.count);
  }, [data]);

  // Theme-aware Chart configurations
  const isLight = theme === 'light';
  const textColor = isLight ? '#475569' : '#e0e0e0';
  const tickColor = isLight ? '#475569' : '#9ca3af';
  const gridColor = isLight ? 'rgba(15, 23, 42, 0.08)' : 'rgba(255, 255, 255, 0.04)';

  const categoryChartConfig = useMemo(() => {
    if (!data || !data.category_totals) return null;
    
    // Filter out categories with 0 values
    let labels = Object.keys(data.category_totals).filter(k => data.category_totals[k] > 0);
    let chartData = labels.map(k => data.category_totals[k]);
    let hasData = chartData.length > 0;

    if (!hasData) {
      labels = ["No spending recorded"];
      chartData = [1];
    }

    const chartColors = [
      '#4BC0D9', // Teal
      '#8884d8', // Purple
      '#10b981', // Green
      '#ffc658', // Yellow
      '#ff7300', // Orange
      '#3b82f6', // Blue
      '#00c49f', // Aqua
      '#ef4444', // Red
      '#a4de6c', // Lime
      '#f59e0b', // Amber
      '#ec4899', // Pink
      '#8b5cf6'  // Violet
    ];

    return {
      data: {
        labels,
        datasets: [{
          data: chartData,
          backgroundColor: hasData ? chartColors.slice(0, labels.length) : ['#2a3556'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: textColor,
              padding: 15,
              font: {
                family: 'Plus Jakarta Sans',
                size: 11,
                weight: '500'
              }
            }
          },
          tooltip: {
            enabled: hasData
          }
        }
      }
    };
  }, [data, textColor]);

  const trendChartConfig = useMemo(() => {
    if (!data || !data.daily_trends) return null;

    return {
      data: {
        labels: data.daily_trends.labels || [],
        datasets: [
          {
            label: 'Income (Deposits)',
            data: data.daily_trends.deposits || [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.03)',
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointRadius: 1,
            pointHoverRadius: 4
          },
          {
            label: 'Expenses (Withdrawals)',
            data: data.daily_trends.withdrawals || [],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.03)',
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointRadius: 1,
            pointHoverRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              color: textColor,
              boxWidth: 12,
              boxHeight: 4,
              font: {
                family: 'Plus Jakarta Sans',
                size: 11,
                weight: '500'
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: tickColor,
              maxTicksLimit: 8,
              font: {
                family: 'Plus Jakarta Sans',
                size: 10
              }
            }
          },
          y: {
            grid: {
              color: gridColor
            },
            ticks: {
              color: tickColor,
              font: {
                family: 'Plus Jakarta Sans',
                size: 10
              }
            }
          }
        }
      }
    };
  }, [data, textColor, tickColor, gridColor]);

  if (error) {
    return (
      <div className="dashboard-container">
        <Sidebar />
        <main className="main-content center-content">
          <div className="upload-card glass text-center" style={{ padding: '40px' }}>
            <h2 style={{ color: 'var(--color-expense)', marginBottom: '10px' }}>Error</h2>
            <p className="subtitle" style={{ marginBottom: '20px' }}>{error}</p>
            <Link to="/" className="primary-btn" style={{ textDecoration: 'none', display: 'inline-block' }}>
              Go Back Home
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className={`dashboard-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      {/* Menu Toggle Button */}
      {!isSidebarOpen && (
        <button className="sidebar-toggle-btn" onClick={toggleSidebar} title="Open Menu">
          <span>☰</span>
        </button>
      )}

      {/* Floating Theme Toggle Button */}
      <button className="theme-toggle-float" onClick={toggleTheme} title="Toggle Light/Dark Theme">
        <span id="theme-icon">{theme === 'light' ? '🌙' : '☀️'}</span>
      </button>

      {/* Sidebar navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="main-content">
        {loading ? (
          <div className="center-content" style={{ height: '80vh', display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <span style={{ fontSize: '2.5rem' }}>⏳</span>
            <h3>Analyzing statement dashboard data...</h3>
          </div>
        ) : data ? (
          <>
            {/* Top bar */}
            <header className="top-bar glass">
              <div className="header-info">
                <h1>Daily Spendings Analysis</h1>
                <p className="file-meta">Statement: <strong>{data.filename}</strong></p>
              </div>
              <div className="header-actions">
                <a 
                  href={`/download/${data.filename}.xlsx`} 
                  className="action-btn download-btn"
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  <span className="btn-icon">📥</span> Download Excel
                </a>
              </div>
            </header>

            {/* Dynamic Spend Summary Notification Bar */}
            <div className="spend-summary-bar glass">
              <div className="spend-summary-content">
                <span className="spend-summary-icon">💡</span>
                <span className="spend-summary-text">
                  Out of your total credited amount of{' '}
                  <strong className="highlight-credited">₹{formatMoney(spendSummaryStats.totalCredited)}</strong>
                  , you spent{' '}
                  <strong className="highlight-debited">₹{formatMoney(spendSummaryStats.categoryDebited)}</strong>{' '}
                  (<strong className="highlight-percentage">{spendSummaryStats.percentage}%</strong>) on{' '}
                  <select
                    className="spend-summary-select"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  >
                    {CATEGORIES.map((cat, i) => (
                      <option key={i} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                  .
                </span>
              </div>
              <div className="spend-summary-actions">
                <label className="filter-toggle-label">
                  <input
                    type="checkbox"
                    className="filter-toggle-checkbox"
                    checked={filterTableByCategory}
                    onChange={(e) => setFilterTableByCategory(e.target.checked)}
                  />
                  Filter list by this category
                </label>
              </div>
            </div>

            {/* Stat Cards */}
            <section className="stats-grid">
              <div className="stat-card glass border-glow-teal">
                <div className="card-icon opening-bal-icon">🔓</div>
                <div className="card-details">
                  <span className="card-title">Opening Balance</span>
                  <h2>₹{formatMoney(data.opening_balance)}</h2>
                </div>
              </div>

              <div className="stat-card glass border-glow-green">
                <div className="card-icon deposit-icon">↘️</div>
                <div className="card-details">
                  <span className="card-title">Total Credited</span>
                  <h2>₹{formatMoney(data.total_deposits)}</h2>
                </div>
              </div>

              <div className="stat-card glass border-glow-red">
                <div className="card-icon withdrawal-icon">↗️</div>
                <div className="card-details">
                  <span className="card-title">Total Debited</span>
                  <h2>₹{formatMoney(data.total_withdrawals)}</h2>
                </div>
              </div>

              <div className="stat-card glass border-glow-purple">
                <div className="card-icon closing-bal-icon">🔒</div>
                <div className="card-details">
                  <span className="card-title">Closing Balance</span>
                  <h2>₹{formatMoney(data.closing_balance)}</h2>
                </div>
              </div>

              <div className="stat-card glass border-glow-gold">
                <div className="card-icon count-icon">🔢</div>
                <div className="card-details">
                  <span className="card-title">Transactions</span>
                  <h2>{data.transaction_count}</h2>
                </div>
              </div>
            </section>

            {/* Charts Section */}
            <section className="charts-grid">
              {/* Spending by Category (Doughnut) */}
              <div className="chart-card glass">
                <h3>Spending by Category</h3>
                <div className="chart-container">
                  {categoryChartConfig && (
                    <DoughnutChart data={categoryChartConfig.data} options={categoryChartConfig.options} />
                  )}
                </div>
              </div>

              {/* Transactions by Category (Counts Table) */}
              <div className="chart-card glass">
                <h3>Transactions by Category</h3>
                <div className="table-container category-counts-container">
                  <table className="tx-table category-counts-table">
                    <thead>
                      <tr>
                        <th>Category</th>
                        <th style={{ textAlign: 'right' }}>Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sortedCategoryCounts.length > 0 ? (
                        sortedCategoryCounts.map((c, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: 500, fontSize: '0.85rem', padding: '10px 12px' }}>{c.category}</td>
                            <td style={{ textAlign: 'right', fontWeight: 600, fontSize: '0.85rem', padding: '10px 12px', color: 'var(--accent-teal)' }}>{c.count}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="2" className="table-empty">No categories recorded.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Cash Flow Trends (Line) */}
              <div className="chart-card glass">
                <h3>Daily Cash Flow Trend</h3>
                <div className="chart-container">
                  {trendChartConfig && (
                    <LineChart data={trendChartConfig.data} options={trendChartConfig.options} />
                  )}
                </div>
              </div>
            </section>

            {/* Transactions List */}
            <section className="transactions-section glass">
              <div className="section-header">
                <h3>Parsed Transactions</h3>
                <div className="search-box">
                  <input 
                    type="text" 
                    placeholder="Search particulars, category..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <span className="search-icon">🔍</span>
                </div>
              </div>

              <div className="table-container">
                <table className="tx-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Particulars</th>
                      <th>Category</th>
                      <th>Withdrawals (Dr)</th>
                      <th>Deposits (Cr)</th>
                      <th style={{ textAlign: 'center' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTransactions.length > 0 ? (
                      filteredTransactions.map((tx) => {
                        const isReviewNeeded = tx.category === 'Other';
                        const selectClass = `category-select ${isReviewNeeded ? 'review-needed' : ''}`;
                        const wVal = tx.withdrawal > 0 ? `₹${formatMoney(tx.withdrawal)}` : '-';
                        const dVal = tx.deposit > 0 ? `₹${formatMoney(tx.deposit)}` : '-';
                        const isUpdating = updatingTxId === tx.id;

                        return (
                          <tr key={tx.id}>
                            <td className="col-date">{tx.date}</td>
                            <td className="col-particulars" title={tx.particulars}>{tx.particulars}</td>
                            <td className="col-category">
                              <div className="category-select-wrapper">
                                <select 
                                  className={selectClass} 
                                  value={tx.category} 
                                  onChange={(e) => handleCategoryChange(tx.id, e.target.value)}
                                  disabled={isUpdating}
                                >
                                  {CATEGORIES.map((cat, i) => (
                                    <option key={i} value={cat}>{cat}</option>
                                  ))}
                                </select>
                                {isReviewNeeded && (
                                  <span className="review-badge" title="Unclassified or low prediction confidence (< 70%). Please confirm correct category.">
                                    ⚠️ Review
                                  </span>
                                )}
                                {isUpdating && <span style={{ fontSize: '0.8rem', opacity: 0.5 }}>⏳</span>}
                              </div>
                            </td>
                            <td className={`col-withdrawal ${tx.withdrawal > 0 ? 'text-expense' : ''}`}>{wVal}</td>
                            <td className={`col-deposit ${tx.deposit > 0 ? 'text-income' : ''}`}>{dVal}</td>
                            <td className="col-actions">
                              <div className="actions-dropdown" onClick={(e) => e.stopPropagation()}>
                                <button 
                                  className="actions-dropdown-trigger" 
                                  onClick={() => setActiveDropdownId(activeDropdownId === tx.id ? null : tx.id)}
                                  title="Actions"
                                >
                                  ⋮
                                </button>
                                <div className={`actions-dropdown-menu ${activeDropdownId === tx.id ? 'active' : ''}`}>
                                  <div className="actions-dropdown-item" onClick={(e) => handleSwapAmount(tx.id, e)}>
                                    <span>⇄</span> Swap Transaction
                                  </div>
                                </div>
                              </div>
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan="6" className="table-empty">No transactions found.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        ) : (
          <div className="center-content" style={{ height: '80vh' }}>
            <h3>Statement not found or access denied.</h3>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
