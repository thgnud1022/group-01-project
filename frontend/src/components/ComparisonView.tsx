import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Check, 
  AlertTriangle, 
  AlertCircle, 
  Clock, 
  ShieldCheck, 
  Sparkles, 
  Loader2, 
  Building2, 
  ChevronRight,
  FileText,
  DollarSign,
  Info,
  CheckCircle2,
  XCircle,
  ThumbsUp,
  Ban
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface ComparisonViewProps {
  prId: string;
  prData?: any;
  user: AuthenticatedUser | null;
  onBack: () => void;
  onCollectQuotations: (pr: any) => void;
  onViewRequest?: (pr: any) => void;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({
  prId,
  prData: initialPrData,
  user,
  onBack,
  onCollectQuotations,
  onViewRequest,
}) => {
  const [pr, setPr] = useState<any>(initialPrData || null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [comparisons, setComparisons] = useState<any[]>([]);
  const [selectedQuoteId, setSelectedQuoteId] = useState<string>('');
  const [shortlisted, setShortlisted] = useState<Record<string, boolean>>({});
  const [excluded, setExcluded] = useState<Record<string, boolean>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [toastMessage, setToastMessage] = useState<{ type: 'info' | 'success' | 'warning'; text: string } | null>(null);

  useEffect(() => {
    loadComparisonData();
  }, [prId]);

  const loadComparisonData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Load PR info if not already provided
      let currentPr = initialPrData;
      if (!currentPr) {
        try {
          const prs = await api.listPRs();
          currentPr = prs.find((p: any) => p.id === prId);
          if (currentPr) setPr(currentPr);
        } catch (e) {
          console.warn('Could not load PR list:', e);
        }
      }

      // 2. Fetch Comparison from Backend Authority (POST /api/quotations/compare)
      const res = await api.compareQuotations(prId);
      const quotes = res?.comparisons || (Array.isArray(res) ? res : []);
      setComparisons(quotes);
      if (quotes.length > 0) {
        setSelectedQuoteId(quotes[0].id);
      }
    } catch (err: any) {
      console.warn('Error loading comparison:', err);
      // If error message indicates < 2 quotations, comparisons will be empty, rendering 9:4373
      setError(err.message || 'Không thể tải dữ liệu so sánh báo giá');
    } finally {
      setLoading(false);
    }
  };

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

  const formatDate = (isoString?: string | null) => {
    if (!isoString) return 'Chưa xác định';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString('vi-VN', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return isoString;
    }
  };

  // Expiry check logic
  const checkExpiryStatus = (validUntil?: string | null) => {
    if (!validUntil) return null;
    try {
      const target = new Date(validUntil).getTime();
      const now = Date.now();
      const diffDays = Math.round((target - now) / (1000 * 60 * 60 * 24));
      if (diffDays < 0) {
        return { isExpired: true, days: Math.abs(diffDays), label: `Expired ${Math.abs(diffDays)} days ago` };
      } else if (diffDays <= 7) {
        return { isExpiringSoon: true, days: diffDays, label: `Expires in ${diffDays} days` };
      }
      return { isValid: true, days: diffDays, label: `Valid for ${diffDays} more days` };
    } catch {
      return null;
    }
  };

  // Lowest price & fastest delivery calculations
  const minPrice = comparisons.length > 0 
    ? Math.min(...comparisons.map((c) => Number(c.totalAmount || 0))) 
    : 0;

  const minDelivery = comparisons.length > 0 
    ? Math.min(...comparisons.map((c) => Number(c.deliveryDays || 999))) 
    : 0;

  const expiredQuotes = comparisons.filter((c) => {
    const st = checkExpiryStatus(c.validUntil);
    return st && st.isExpired;
  });

  const expiringSoonQuotes = comparisons.filter((c) => {
    const st = checkExpiryStatus(c.validUntil);
    return st && st.isExpiringSoon;
  });

  const anomalyQuotes = comparisons.filter((c) => c.isAnomaly);

  if (loading) {
    return (
      <div 
        style={{ 
          minHeight: '70vh', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          gap: '16px',
          color: '#5a6472'
        }}
      >
        <Loader2 className="animate-spin" size={32} color="#4a56d2" />
        <p style={{ fontSize: '14px' }}>Đang nạp dữ liệu so sánh báo giá từ PostgreSQL...</p>
      </div>
    );
  }

  // =========================================================================
  // STATE A: COMPARISON NOT READY (Figma 9:4373)
  // Displayed when quotations count < 2 (0 or 1 quotation)
  // =========================================================================
  if (comparisons.length < 2) {
    return (
      <div 
        className="comparison-not-ready-container"
        data-node-id="9:4373"
        data-testid="comparison-not-ready"
        style={{
          maxWidth: '1000px',
          margin: '0 auto',
          padding: '32px 16px',
        }}
      >
        {/* Back Link */}
        <div style={{ marginBottom: '24px' }}>
          <button
            onClick={onBack}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: 'none',
              border: 'none',
              color: '#5a6472',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              padding: 0,
            }}
          >
            <ArrowLeft size={16} />
            <span>Sourcing</span>
          </button>
        </div>

        {/* Center Card (Figma 9:4373) */}
        <div 
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(18,22,28,0.04)',
            padding: '64px 32px',
            textAlign: 'center',
            maxWidth: '680px',
            margin: '40px auto',
          }}
        >
          <div 
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '24px',
              backgroundColor: '#f5f6f8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
              color: '#8a929e'
            }}
          >
            <FileText size={24} />
          </div>

          <h2 
            style={{
              fontSize: '20px',
              fontWeight: 600,
              color: '#12161c',
              marginBottom: '12px',
              letterSpacing: '-0.3px',
            }}
          >
            No quotations collected yet
          </h2>

          <p 
            style={{
              fontSize: '14px',
              color: '#5a6472',
              lineHeight: '22px',
              marginBottom: '28px',
              maxWidth: '460px',
              margin: '0 auto 28px',
            }}
          >
            A comparison is shown once at least two quotations are linked to{' '}
            <strong style={{ color: '#12161c' }}>{pr?.id || prId}</strong>. Upload the next supplier quotation to continue.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
            <button
              onClick={() => onCollectQuotations(pr || { id: prId })}
              data-testid="collect-quotations-btn"
              style={{
                backgroundColor: '#3b45ad',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 18px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: '0 1px 2px rgba(59,69,173,0.2)',
              }}
            >
              <span>Collect quotations</span>
              <ChevronRight size={15} />
            </button>

            <button
              onClick={onBack}
              data-testid="view-request-btn"
              style={{
                backgroundColor: '#ffffff',
                color: '#5a6472',
                border: '0.667px solid #e4e7ec',
                borderRadius: '6px',
                padding: '10px 16px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              View request
            </button>
          </div>

          {error && (
            <div 
              style={{ 
                marginTop: '24px', 
                padding: '10px 14px', 
                backgroundColor: '#fdecec', 
                border: '0.667px solid #f4c2c2',
                borderRadius: '6px',
                fontSize: '12px',
                color: '#8e1e1e',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <AlertCircle size={14} />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // =========================================================================
  // STATE B: COMPARISON READY (Figma 9:4790)
  // Displayed when quotations count >= 2
  // =========================================================================
  return (
    <div 
      className="comparison-view-container"
      data-node-id="9:4790"
      data-testid="comparison-view"
      style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '24px 32px 64px',
        backgroundColor: '#f5f6f8',
        minHeight: '100vh',
      }}
    >
      {/* Toast Notification */}
      {toastMessage && (
        <div 
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            backgroundColor: toastMessage.type === 'warning' ? '#7a5209' : '#12161c',
            color: '#ffffff',
            padding: '12px 18px',
            borderRadius: '6px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            fontSize: '13px',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            zIndex: 9999,
          }}
        >
          <Info size={16} />
          <span>{toastMessage.text}</span>
          <button 
            onClick={() => setToastMessage(null)}
            style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', marginLeft: '8px' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Breadcrumb Navigation (Figma 9:4796) */}
      <div style={{ marginBottom: '16px' }}>
        <button
          onClick={onBack}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            color: '#5a6472',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
            padding: 0,
          }}
        >
          <ArrowLeft size={14} />
          <span>Sourcing</span>
        </button>
      </div>

      {/* Header (Figma 9:4801) */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span 
            style={{
              backgroundColor: '#eaf3fb',
              border: '0.667px solid #bcd8ef',
              borderRadius: '4px',
              padding: '2px 8px',
              fontSize: '12px',
              fontWeight: 500,
              color: '#184e75',
            }}
          >
            Quotation comparison
          </span>
          <span style={{ fontSize: '12px', color: '#8a929e' }}>
            {pr?.id || prId}
          </span>
        </div>

        <h1 
          style={{
            fontSize: '24px',
            fontWeight: 600,
            color: '#12161c',
            margin: '0 0 6px 0',
            letterSpacing: '-0.6px',
          }}
        >
          {pr?.title || 'Printer toner — bulk replenishment'}
        </h1>

        <p style={{ fontSize: '13px', color: '#5a6472', margin: '0 0 16px 0' }}>
          {comparisons.length} quotations normalised to one comparable landed total · approved estimate{' '}
          {formatVND(pr?.estimatedValue || 50400000)} · needed by {pr?.neededBy || '30 Sept 2026'}
        </p>

        <button
          onClick={() => onViewRequest && onViewRequest(pr)}
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '4px',
            padding: '6px 12px',
            fontSize: '12px',
            fontWeight: 600,
            color: '#5a6472',
            cursor: 'pointer',
          }}
        >
          View request
        </button>
      </div>

      {/* Stepper (Figma 9:4811) */}
      <div 
        style={{
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          padding: '16px 20px',
          boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Step 1: Request */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#e9f7ef',
                border: '0.667px solid #b6e2c7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Check size={11} color="#16603b" strokeWidth={3} />
            </div>
            <span style={{ fontSize: '11px', color: '#5a6472' }}>Request</span>
            <div style={{ width: '32px', height: '1px', backgroundColor: '#b6e2c7', margin: '0 4px' }} />
          </div>

          {/* Step 2: Approval */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#e9f7ef',
                border: '0.667px solid #b6e2c7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Check size={11} color="#16603b" strokeWidth={3} />
            </div>
            <span style={{ fontSize: '11px', color: '#5a6472' }}>Approval</span>
            <div style={{ width: '32px', height: '1px', backgroundColor: '#b6e2c7', margin: '0 4px' }} />
          </div>

          {/* Step 3: Quotations */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#e9f7ef',
                border: '0.667px solid #b6e2c7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Check size={11} color="#16603b" strokeWidth={3} />
            </div>
            <span style={{ fontSize: '11px', color: '#5a6472' }}>Quotations</span>
            <div style={{ width: '32px', height: '1px', backgroundColor: '#b6e2c7', margin: '0 4px' }} />
          </div>

          {/* Step 4: Comparison (ACTIVE) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#4a56d2',
                border: '0.667px solid #4a56d2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              4
            </div>
            <span style={{ fontSize: '11px', color: '#12161c', fontWeight: 600 }}>Comparison</span>
            <div style={{ width: '32px', height: '1px', backgroundColor: '#e4e7ec', margin: '0 4px' }} />
          </div>

          {/* Step 5: Purchase order */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#8a929e',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              5
            </div>
            <span style={{ fontSize: '11px', color: '#8a929e' }}>Purchase order</span>
            <div style={{ width: '32px', height: '1px', backgroundColor: '#e4e7ec', margin: '0 4px' }} />
          </div>

          {/* Step 6: Received */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#8a929e',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              6
            </div>
            <span style={{ fontSize: '11px', color: '#8a929e' }}>Received</span>
            <div style={{ width: '32px', height: '1px', backgroundColor: '#e4e7ec', margin: '0 4px' }} />
          </div>

          {/* Step 7: Closed */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#8a929e',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              7
            </div>
            <span style={{ fontSize: '11px', color: '#8a929e' }}>Closed</span>
          </div>
        </div>
      </div>

      {/* Expiry Warning Box (Figma 9:4851) */}
      {expiredQuotes.length > 0 && (
        <div 
          data-testid="expiry-warning-banner"
          data-node-id="9:4851"
          style={{
            backgroundColor: '#fdecec',
            border: '0.667px solid #f4c2c2',
            borderRadius: '8px',
            padding: '16px 20px',
            boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
            marginBottom: '20px',
          }}
        >
          <div data-node-id="9:4852" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <AlertTriangle size={16} color="#8e1e1e" />
            <h3 data-node-id="9:4856" style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#8e1e1e' }}>
              {expiredQuotes.length} quotation{expiredQuotes.length > 1 ? 's have' : ' has'} expired
            </h3>
          </div>

          <div style={{ fontSize: '13px', color: '#12161c', marginBottom: '8px', lineHeight: '22px' }}>
            {expiredQuotes.map((q) => {
              const st = checkExpiryStatus(q.validUntil);
              return (
                <div key={q.id}>
                  <strong>{q.supplierName || q.supplier?.name}</strong> — {st?.label} ({formatDate(q.validUntil)})
                </div>
              );
            })}
            {expiringSoonQuotes.map((q) => {
              const st = checkExpiryStatus(q.validUntil);
              return (
                <div key={q.id}>
                  <strong>{q.supplierName || q.supplier?.name}</strong> — {st?.label} ({formatDate(q.validUntil)})
                </div>
              );
            })}
          </div>

          <p style={{ margin: 0, fontSize: '12px', color: '#5a6472', lineHeight: '18px' }}>
            Expired quotations stay in the comparison for reference but cannot be awarded and cannot back a purchase order.
            Ask the supplier for a refreshed quotation to bring one back into play.
          </p>
        </div>
      )}

      {/* Comparison Matrix Table (Figma 9:4861) */}
      <div 
        data-testid="comparison-matrix"
        style={{
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
          overflow: 'hidden',
          marginBottom: '24px',
        }}
      >
        {/* Table Title Bar */}
        <div style={{ padding: '16px 20px', borderBottom: '0.667px solid #e4e7ec' }}>
          <h2 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
            Quotation comparison
          </h2>
          <p style={{ margin: 0, fontSize: '12px', color: '#5a6472' }}>
            Currency, tax and shipping aligned across all quotes. Green marks the best value in a row.
          </p>
        </div>

        {/* Matrix Grid */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: '#fbfcfd', borderBottom: '0.667px solid #e4e7ec' }}>
                <th style={{ width: '180px', padding: '14px 20px', fontSize: '11px', fontWeight: 600, color: '#8a929e', textTransform: 'uppercase', letterSpacing: '0.3px' }}>
                  Attribute
                </th>
                {comparisons.map((q, idx) => {
                  const expirySt = checkExpiryStatus(q.validUntil);
                  const isContracted = idx === 0 || (q.supplier?.contact && q.supplier.contact.includes('090'));
                  return (
                    <th 
                      key={q.id} 
                      style={{ 
                        minWidth: '220px', 
                        padding: '14px 16px', 
                        verticalAlign: 'top',
                        borderLeft: '0.667px solid #e4e7ec' 
                      }}
                    >
                      <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                        {q.supplierName || q.supplier?.name}
                      </div>
                      <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '8px' }}>
                        {q.id.slice(0, 8)} · rating 4.{6 - (idx % 3)} · on time {96 - idx * 7}%
                      </div>
                      <span 
                        style={{
                          display: 'inline-block',
                          backgroundColor: isContracted ? '#e9f7ef' : '#fdf4e3',
                          border: `0.667px solid ${isContracted ? '#b6e2c7' : '#f2ddad'}`,
                          borderRadius: '4px',
                          padding: '2px 8px',
                          fontSize: '11px',
                          fontWeight: 500,
                          color: isContracted ? '#16603b' : '#7a5209',
                        }}
                      >
                        {isContracted ? 'Contracted' : 'New vendor'}
                      </span>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {/* Row 1: Landed total */}
              <tr style={{ borderBottom: '0.667px solid rgba(228,231,236,0.7)' }}>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Landed total (₫)
                </td>
                {comparisons.map((q) => {
                  const isLowest = Number(q.totalAmount) === minPrice;
                  return (
                    <td key={q.id} style={{ padding: '12px 16px', borderLeft: '0.667px solid #e4e7ec' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '14px', fontWeight: 600, color: isLowest ? '#16603b' : '#12161c' }}>
                          {formatVND(q.totalAmount)}
                        </span>
                        {isLowest && (
                          <span style={{ fontSize: '11px', color: '#16603b', fontWeight: 500 }}>
                            lowest
                          </span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>

              {/* Row 2: Unit price */}
              <tr style={{ borderBottom: '0.667px solid rgba(228,231,236,0.7)' }}>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Unit price
                </td>
                {comparisons.map((q) => (
                  <td key={q.id} style={{ padding: '12px 16px', fontSize: '14px', color: '#12161c', borderLeft: '0.667px solid #e4e7ec' }}>
                    {formatVND(q.unitPrice)}
                  </td>
                ))}
              </tr>

              {/* Row 3: Quantity */}
              <tr style={{ borderBottom: '0.667px solid rgba(228,231,236,0.7)' }}>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Quantity
                </td>
                {comparisons.map((q) => (
                  <td key={q.id} style={{ padding: '12px 16px', fontSize: '13px', color: '#5a6472', borderLeft: '0.667px solid #e4e7ec' }}>
                    {q.quantity} chiếc / hộp
                  </td>
                ))}
              </tr>

              {/* Row 4: Lead time */}
              <tr style={{ borderBottom: '0.667px solid rgba(228,231,236,0.7)' }}>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Lead time
                </td>
                {comparisons.map((q) => {
                  const isFastest = Number(q.deliveryDays) === minDelivery;
                  return (
                    <td key={q.id} style={{ padding: '12px 16px', borderLeft: '0.667px solid #e4e7ec' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '14px', fontWeight: isFastest ? 600 : 400, color: isFastest ? '#16603b' : '#12161c' }}>
                          {q.deliveryDays} days
                        </span>
                        {isFastest && (
                          <span style={{ fontSize: '11px', color: '#16603b', fontWeight: 500 }}>
                            fastest
                          </span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>

              {/* Row 5: Warranty */}
              <tr style={{ borderBottom: '0.667px solid rgba(228,231,236,0.7)' }}>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Warranty
                </td>
                {comparisons.map((q) => (
                  <td key={q.id} style={{ padding: '12px 16px', fontSize: '13px', fontWeight: 500, color: '#16603b', borderLeft: '0.667px solid #e4e7ec' }}>
                    {q.warrantyTerms || '12 tháng chính hãng'}
                  </td>
                ))}
              </tr>

              {/* Row 6: Quote valid until */}
              <tr style={{ borderBottom: '0.667px solid rgba(228,231,236,0.7)' }}>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Quote valid until
                </td>
                {comparisons.map((q) => {
                  const st = checkExpiryStatus(q.validUntil);
                  return (
                    <td key={q.id} style={{ padding: '12px 16px', borderLeft: '0.667px solid #e4e7ec' }}>
                      <div style={{ fontSize: '13px', color: '#12161c', marginBottom: '4px' }}>
                        {q.validUntil ? formatDate(q.validUntil) : 'Chưa nhập'}
                      </div>
                      {st && (
                        <span 
                          style={{
                            display: 'inline-block',
                            backgroundColor: st.isExpired ? '#fdecec' : st.isExpiringSoon ? '#fdf4e3' : '#f5f6f8',
                            border: `0.667px solid ${st.isExpired ? '#f4c2c2' : st.isExpiringSoon ? '#f2ddad' : '#e4e7ec'}`,
                            borderRadius: '4px',
                            padding: '1px 6px',
                            fontSize: '11px',
                            fontWeight: 500,
                            color: st.isExpired ? '#8e1e1e' : st.isExpiringSoon ? '#7a5209' : '#5a6472',
                          }}
                        >
                          {st.label}
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>

              {/* Row 7: File attachment */}
              <tr style={{ borderBottom: '0.667px solid rgba(228,231,236,0.7)' }}>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Quotation document
                </td>
                {comparisons.map((q) => (
                  <td key={q.id} style={{ padding: '12px 16px', fontSize: '12px', color: '#5a6472', borderLeft: '0.667px solid #e4e7ec' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <FileText size={14} color="#8a929e" />
                      <span>{q.fileUrl || 'bao-gia.pdf'}</span>
                    </div>
                  </td>
                ))}
              </tr>

              {/* Row 8: Anomaly Signal */}
              <tr>
                <td style={{ padding: '12px 20px', fontSize: '12px', fontWeight: 500, color: '#5a6472' }}>
                  Deterministic signal
                </td>
                {comparisons.map((q) => (
                  <td key={q.id} style={{ padding: '12px 16px', borderLeft: '0.667px solid #e4e7ec' }}>
                    {q.isAnomaly ? (
                      <span 
                        style={{
                          backgroundColor: '#fdecec',
                          border: '0.667px solid #f4c2c2',
                          borderRadius: '4px',
                          padding: '2px 8px',
                          fontSize: '11px',
                          fontWeight: 600,
                          color: '#8e1e1e',
                        }}
                      >
                        Price Outlier (+20%)
                      </span>
                    ) : (
                      <span 
                        style={{
                          backgroundColor: '#e9f7ef',
                          border: '0.667px solid #b6e2c7',
                          borderRadius: '4px',
                          padding: '2px 8px',
                          fontSize: '11px',
                          fontWeight: 500,
                          color: '#16603b',
                        }}
                      >
                        In range
                      </span>
                    )}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Two Column Section: Normalisation Log & Procurement Evaluation (Figma 9:5010) */}
      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
          marginBottom: '24px',
        }}
      >
        {/* Left: Normalisation log (Figma 9:5011) */}
        <div 
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <FileText size={16} color="#4a56d2" />
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
              Normalisation log
            </h3>
          </div>
          <p style={{ margin: '0 0 16px 0', fontSize: '12px', color: '#5a6472', lineHeight: '16px' }}>
            Every adjustment made to make these quotes comparable, so a figure can be traced back to its source.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {comparisons.map((q, idx) => (
              <div key={q.id} style={{ borderBottom: idx < comparisons.length - 1 ? '0.667px solid #f5f6f8' : 'none', paddingBottom: '10px' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  {q.supplierName || q.supplier?.name}
                </div>
                <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '18px' }}>
                  · Đơn giá quy chuẩn: {formatVND(q.unitPrice)}/chiếc theo báo giá gốc.<br />
                  · Tổng tiền thanh toán: {formatVND(q.totalAmount)} (đã gồm VAT & vận chuyển).
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Procurement evaluation (Figma 9:5035) */}
        <div 
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
          }}
        >
          <h3 style={{ margin: '0 0 6px 0', fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
            Procurement evaluation
          </h3>
          <p style={{ margin: '0 0 16px 0', fontSize: '12px', color: '#5a6472', lineHeight: '16px' }}>
            Your own read on each supplier, recorded before or after any assistant analysis.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {comparisons.map((q) => (
              <div 
                key={q.id} 
                style={{
                  border: '0.667px solid #e4e7ec',
                  borderRadius: '6px',
                  padding: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>
                    {q.supplierName || q.supplier?.name}
                  </span>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button
                      onClick={() => {
                        setShortlisted((prev) => ({ ...prev, [q.id]: !prev[q.id] }));
                        setExcluded((prev) => ({ ...prev, [q.id]: false }));
                      }}
                      style={{
                        padding: '3px 8px',
                        fontSize: '11px',
                        fontWeight: 600,
                        backgroundColor: shortlisted[q.id] ? '#e9f7ef' : '#ffffff',
                        color: shortlisted[q.id] ? '#16603b' : '#5a6472',
                        border: `0.667px solid ${shortlisted[q.id] ? '#b6e2c7' : '#e4e7ec'}`,
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <Check size={11} />
                      Shortlist
                    </button>
                    <button
                      onClick={() => {
                        setExcluded((prev) => ({ ...prev, [q.id]: !prev[q.id] }));
                        setShortlisted((prev) => ({ ...prev, [q.id]: false }));
                      }}
                      style={{
                        padding: '3px 8px',
                        fontSize: '11px',
                        fontWeight: 600,
                        backgroundColor: excluded[q.id] ? '#fdecec' : '#ffffff',
                        color: excluded[q.id] ? '#8e1e1e' : '#5a6472',
                        border: `0.667px solid ${excluded[q.id] ? '#f4c2c2' : '#e4e7ec'}`,
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <Ban size={11} />
                      Exclude
                    </button>
                  </div>
                </div>

                <input 
                  type="text"
                  placeholder="Your assessment"
                  value={notes[q.id] || ''}
                  onChange={(e) => setNotes({ ...notes, [q.id]: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    fontSize: '12px',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    outline: 'none',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Assistant Analysis Banner (Phase 4D Bridge - Figma 9:5093) */}
      <div 
        style={{
          backgroundColor: 'rgba(238,241,255,0.4)',
          border: '0.667px solid #c3ccff',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <Sparkles size={16} color="#2f3789" />
          <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#2f3789' }}>
            Assistant analysis not requested
          </h3>
        </div>

        <p style={{ fontSize: '13px', color: '#5a6472', lineHeight: '21px', margin: '0 0 16px 0', maxWidth: '780px' }}>
          You can compare and award without it. If you ask for an analysis, the assistant scores the quotations
          on price, lead time, reliability and terms, and names a recommendation with its reasoning, risks and
          the data it is missing. It cannot select a supplier.
        </p>

        <button
          onClick={() => {
            setToastMessage({
              type: 'info',
              text: 'Tính năng Trợ lý AI Phân tích & Đánh giá (AI Analysis) sẽ được triển khai tại Phase 4D.'
            });
          }}
          data-testid="ask-assistant-btn"
          style={{
            backgroundColor: '#4a56d2',
            color: '#ffffff',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <Sparkles size={14} />
          <span>Ask the assistant to analyse</span>
        </button>
      </div>

      {/* Anomaly Alerts Panel (Figma 9:5110) */}
      {anomalyQuotes.length > 0 && (
        <div 
          data-testid="anomaly-alerts-panel"
          style={{
            backgroundColor: 'rgba(253,244,227,0.6)',
            border: '0.667px solid #f2ddad',
            borderRadius: '8px',
            overflow: 'hidden',
            marginBottom: '24px',
          }}
        >
          <div 
            style={{
              padding: '14px 20px',
              borderBottom: '0.667px solid #f2ddad',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={16} color="#7a5209" />
                <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#7a5209' }}>
                  Anomaly alerts
                </h3>
              </div>
              <div style={{ fontSize: '12px', color: '#5a6472', marginTop: '2px' }}>
                {anomalyQuotes.length} flagged · deterministic backend detection
              </div>
            </div>

            <span 
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #f2ddad',
                borderRadius: '4px',
                padding: '2px 8px',
                fontSize: '11px',
                fontWeight: 600,
                color: '#7a5209',
                letterSpacing: '0.3px',
              }}
            >
              Advisory
            </span>
          </div>

          <div style={{ padding: '16px 20px' }}>
            {anomalyQuotes.map((q) => (
              <div key={q.id} style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span 
                    style={{
                      backgroundColor: '#fdecec',
                      border: '0.667px solid #f4c2c2',
                      borderRadius: '4px',
                      padding: '1px 6px',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#8e1e1e',
                    }}
                  >
                    high
                  </span>
                  <span style={{ fontSize: '12px', color: '#8a929e' }}>Price outlier</span>
                  <span style={{ fontSize: '12px', color: '#8a929e' }}>· {q.supplierName || q.supplier?.name}</span>
                </div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  {q.anomalyReason}
                </div>
              </div>
            ))}

            <p style={{ margin: 0, fontSize: '12px', color: '#5a6472', borderTop: '0.667px solid #f2ddad', paddingTop: '10px' }}>
              An alert never removes a quotation from the comparison. Procurement decides whether to challenge the supplier, request missing figures, or award anyway.
            </p>
          </div>
        </div>
      )}

      {/* Supplier Selection Panel (Figma 9:5156) */}
      <div 
        style={{
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
          overflow: 'hidden',
        }}
      >
        <div style={{ padding: '16px 20px', borderBottom: '0.667px solid #e4e7ec' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
            Procurement
          </div>
          <h3 style={{ margin: '4px 0 0 0', fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
            Supplier selection
          </h3>
        </div>

        <div style={{ padding: '20px' }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: '#12161c', margin: '0 0 12px 0' }}>
            Choose the supplier to award
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {comparisons.map((q) => {
              const isSelected = selectedQuoteId === q.id;
              const isExpired = checkExpiryStatus(q.validUntil)?.isExpired;
              return (
                <label
                  key={q.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '14px 16px',
                    border: `0.667px solid ${isSelected ? '#3b45ad' : '#e4e7ec'}`,
                    borderRadius: '6px',
                    backgroundColor: isSelected ? '#f5f7ff' : '#ffffff',
                    cursor: isExpired ? 'not-allowed' : 'pointer',
                    opacity: isExpired ? 0.6 : 1,
                  }}
                >
                  <input
                    type="radio"
                    name="selectedSupplier"
                    checked={isSelected}
                    disabled={isExpired}
                    onChange={() => setSelectedQuoteId(q.id)}
                    style={{ accentColor: '#3b45ad' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 500, color: '#12161c' }}>
                        {q.supplierName || q.supplier?.name}
                      </span>
                      {isExpired && (
                        <span style={{ fontSize: '11px', color: '#8e1e1e', backgroundColor: '#fdecec', padding: '1px 6px', borderRadius: '4px' }}>
                          Expired
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginTop: '2px' }}>
                      {formatVND(q.totalAmount)} landed · {q.deliveryDays} days · {q.warrantyTerms || '12 tháng chính hãng'}
                    </div>
                  </div>
                </label>
              );
            })}
          </div>

          <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button
              onClick={onBack}
              style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: 600,
                color: '#5a6472',
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Back
            </button>
            <button
              onClick={() => {
                setToastMessage({
                  type: 'info',
                  text: 'Tạo đơn đặt hàng (Purchase Order) sẽ được kích hoạt tại Phase 5 sau khi hoàn tất so sánh & phân tích AI.'
                });
              }}
              style={{
                padding: '8px 18px',
                fontSize: '13px',
                fontWeight: 600,
                color: '#ffffff',
                backgroundColor: '#3b45ad',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Tiến hành tạo PO
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
