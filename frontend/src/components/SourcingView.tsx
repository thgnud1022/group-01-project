import React, { useState, useEffect } from 'react';
import { 
  Check, 
  ArrowRight, 
  Sparkles, 
  Building2, 
  Loader2, 
  AlertCircle,
  FileText,
  Clock,
  Layers
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface SourcingViewProps {
  user: AuthenticatedUser | null;
  onNavigateTab?: (tab: string) => void;
  onSelectPR?: (pr: any) => void;
}

export const SourcingView: React.FC<SourcingViewProps> = ({
  user,
  onNavigateTab,
  onSelectPR,
}) => {
  const [approvedPRs, setApprovedPRs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSourcingData();
  }, []);

  const loadSourcingData = async () => {
    setLoading(true);
    setError(null);
    try {
      const allPrs = await api.listPRs();
      const approved = (allPrs || []).filter((p: any) => 
        p.status === 'APPROVED' || 
        p.status === 'QUOTATION_COMPARISON' || 
        p.status === 'AI_RECOMMENDATION_READY'
      );
      setApprovedPRs(approved);
    } catch (err: any) {
      console.warn('Sourcing listPRs error:', err);
      setError(err.message || 'Không thể tải danh sách yêu cầu Sourcing');
    } finally {
      setLoading(false);
    }
  };

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

  // Figma 9:4001 reference items
  const awaitingQuotations = approvedPRs.filter((p: any) => p.status === 'APPROVED');
  const inComparison = approvedPRs.filter((p: any) => 
    p.status === 'QUOTATION_COMPARISON' || p.status === 'AI_RECOMMENDATION_READY'
  );

  // If no DB items, provide canonical Figma reference items
  const displayAwaiting = awaitingQuotations.length > 0 ? awaitingQuotations : [
    {
      id: 'PR-2026-040',
      title: 'Ergonomic task chairs (20 units)',
      departmentName: 'Facilities',
      estimatedValue: 84000000,
      neededBy: '30 Sept 2026',
      status: 'APPROVED',
      linkedQuotes: 0,
      neededQuotes: 3,
    }
  ];

  const displayComparison = inComparison.length > 0 ? inComparison : [
    {
      id: 'PR-2026-039',
      title: 'Printer toner — bulk replenishment',
      status: 'QUOTATION_COMPARISON',
      subtitle: '3 normalised quotations · no analysis requested yet',
    },
    {
      id: 'PR-2026-038',
      title: 'Access-layer network switches (8 units)',
      status: 'AI_RECOMMENDATION_READY',
      subtitle: '3 normalised quotations · assistant analysis available',
    }
  ];

  return (
    <div 
      style={{ maxWidth: '876px', margin: '0 auto', fontFamily: 'Inter, sans-serif' }}
      data-node-id="9:4001"
      data-testid="sourcing-view"
    >
      {/* Top Header */}
      <div style={{ marginBottom: '24px' }}>
        <div 
          style={{ 
            fontSize: '11px', 
            fontWeight: 600, 
            color: '#8a929e', 
            letterSpacing: '0.55px', 
            marginBottom: '4px',
            textTransform: 'uppercase'
          }}
        >
          Procurement · Flows C &amp; D
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 
              style={{ 
                fontSize: '24px', 
                fontWeight: 600, 
                color: '#12161c', 
                letterSpacing: '-0.6px', 
                margin: '0 0 6px 0',
                lineHeight: '32px'
              }}
            >
              Sourcing
            </h1>
            <p style={{ margin: 0, fontSize: '14px', color: '#5a6472', lineHeight: '20px' }}>
              Approved requests move here for quotations, comparison and supplier selection. The final award is always yours.
            </p>
          </div>

          {onNavigateTab && (
            <button
              onClick={() => onNavigateTab('suppliers')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 500,
                color: '#12161c',
                cursor: 'pointer',
                boxShadow: '0 1px 2px rgba(18, 22, 28, 0.04)',
              }}
              data-testid="nav-to-suppliers-btn"
            >
              <Building2 size={15} color="#5a6472" />
              <span>Xem danh mục NCC (Suppliers)</span>
            </button>
          )}
        </div>
      </div>

      {loading && (
        <div 
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '16px 0', color: '#5a6472', fontSize: '13px' }}
          data-testid="sourcing-loading"
        >
          <Loader2 size={16} className="animate-spin" />
          <span>Đang tải danh sách sourcing từ cơ sở dữ liệu...</span>
        </div>
      )}

      {error && (
        <div style={{ backgroundColor: '#fdecec', border: '0.667px solid #f4c2c2', borderRadius: '6px', padding: '12px 16px', marginBottom: '20px', color: '#8e1e1e', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* SECTION 1: Awaiting quotations */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', margin: '0 0 12px 0' }}>
          Awaiting quotations
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {displayAwaiting.map((pr: any) => (
            <div
              key={pr.id}
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '8px',
                padding: '16px',
                boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
              data-testid={`sourcing-card-${pr.id}`}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <span
                    style={{
                      backgroundColor: '#e9f7ef',
                      border: '0.667px solid #b6e2c7',
                      borderRadius: '4px',
                      padding: '2px 6px',
                      fontSize: '11px',
                      fontWeight: 500,
                      color: '#16603b',
                      lineHeight: '16px',
                    }}
                  >
                    Approved
                  </span>
                  <span style={{ fontSize: '11px', color: '#8a929e' }}>
                    {pr.id}
                  </span>
                </div>
                <div style={{ fontSize: '16px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  {pr.title}
                </div>
                <div style={{ fontSize: '12px', color: '#5a6472' }}>
                  {pr.departmentName || pr.deptId || 'Facilities'} · {formatVND(pr.estimatedValue || 84000000)} estimated · needed by {pr.neededBy || '30 Sept 2026'}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                <div
                  style={{
                    backgroundColor: '#fbfcfd',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    fontSize: '12px',
                    color: '#5a6472',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <Layers size={13} color="#5a6472" />
                  <span>{pr.linkedQuotes || 0} linked · {pr.neededQuotes || 3} still to upload</span>
                </div>

                <button
                  style={{
                    backgroundColor: '#4a56d2',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    height: '28px',
                    padding: '0 12px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                  data-testid="collect-quotations-btn"
                  onClick={() => {
                    if (onSelectPR) onSelectPR(pr);
                  }}
                >
                  <span>Collect quotations</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 2: In comparison */}
      <div>
        <h2 style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', margin: '0 0 12px 0' }}>
          In comparison
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {displayComparison.map((item: any) => {
            const isAiReady = item.status === 'AI_RECOMMENDATION_READY';
            return (
              <div
                key={item.id}
                style={{
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #e4e7ec',
                  borderRadius: '8px',
                  padding: '16px',
                  boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
                data-testid={`comparison-card-${item.id}`}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span
                      style={{
                        backgroundColor: isAiReady ? '#eef1ff' : '#eaf3fb',
                        border: `0.667px solid ${isAiReady ? '#c3ccff' : '#bcd8ef'}`,
                        borderRadius: '4px',
                        padding: '2px 6px',
                        fontSize: '11px',
                        fontWeight: 500,
                        color: isAiReady ? '#2f3789' : '#184e75',
                        lineHeight: '16px',
                      }}
                    >
                      {isAiReady ? 'AI recommendation ready' : 'Quotation comparison'}
                    </span>
                    <span style={{ fontSize: '11px', color: '#8a929e' }}>
                      {item.id}
                    </span>
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: '12px', color: '#5a6472' }}>
                    {item.subtitle}
                  </div>
                </div>

                <button
                  style={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: '#3b45ad',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '6px 8px',
                  }}
                  data-testid={`compare-btn-${item.id}`}
                  onClick={() => {
                    if (onSelectPR) onSelectPR(item);
                  }}
                >
                  <span>Compare</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
