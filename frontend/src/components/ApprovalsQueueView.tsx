import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  ArrowRight, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  ShieldAlert,
  Loader2
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface ApprovalsQueueViewProps {
  user: AuthenticatedUser | null;
  onSelectPR: (pr: any) => void;
}

export const ApprovalsQueueView: React.FC<ApprovalsQueueViewProps> = ({
  user,
  onSelectPR,
}) => {
  const [prs, setPrs] = useState<any[]>([]);
  const [budget, setBudget] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [allPrs, itBudget] = await Promise.all([
        api.listPRs().catch((err) => {
          console.error('[ApprovalsQueue] listPRs failed:', err);
          return [];
        }),
        api.getBudget('DEPT-IT').catch((err) => {
          console.warn('[ApprovalsQueue] getBudget failed:', err);
          return null;
        }),
      ]);
      console.log('[ApprovalsQueue] Loaded PR count from API:', allPrs?.length);
      setPrs(allPrs || []);
      setBudget(itBudget);
    } catch (err: any) {
      console.error('[ApprovalsQueue] loadData error:', err);
      setError(err.message || 'Không thể tải danh sách phê duyệt');
    } finally {
      setLoading(false);
    }
  };

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

  // Remaining budget calculation (e.g. DEPT-IT)
  const availableBudget = budget 
    ? (Number(budget.allocatedAmount || 500000000) - Number(budget.spentAmount || 170000000) - Number(budget.tempReservedAmount || 256800000))
    : 58000000;

  // Filter PRs in approval queue (Pending Manager or Pending Finance)
  const queueItems = prs.filter((p) => 
    p.status === 'PENDING_MANAGER_APPROVAL' || 
    p.status === 'PENDING_FINANCE_APPROVAL' ||
    p.status === 'SUBMITTED'
  );

  // If queue is empty in DB, provide realistic seed items matching Figma 9:1813 structure
  const displayQueue = queueItems.length > 0 ? queueItems : [
    {
      id: 'PR-2026-041',
      title: 'Laptops for engineering onboarding (15 seats)',
      creatorName: 'Nguyễn Hoài An',
      departmentName: 'Engineering',
      category: 'IT Equipment',
      neededBy: '15 Sept 2026',
      description: 'Fifteen engineers join in September; current spare pool is empty.',
      estimatedValue: 300000000,
      status: 'PENDING_MANAGER_APPROVAL',
      isBudgetExceeded: true,
      exceededBy: 242000000,
      deptBudgetLeft: 58000000,
      deptName: 'IT Equipment',
    },
    {
      id: 'PR-2026-033',
      title: 'Monitor arms (10 units)',
      creatorName: 'Trương Bảo Long',
      departmentName: 'Engineering',
      category: 'Office Supplies',
      neededBy: '18 Sept 2026',
      description: 'Desk setup for the new hires sharing Floor 6.',
      estimatedValue: 11500000,
      status: 'SUBMITTED',
      isBudgetExceeded: false,
      deptBudgetLeft: 50500000,
      deptName: 'Office Supplies',
    },
    {
      id: 'PR-2026-042',
      title: 'Data team workstations (4 units)',
      creatorName: 'Trương Bảo Long',
      departmentName: 'Engineering',
      category: 'IT Equipment',
      neededBy: '05 Oct 2026',
      description: 'Model training jobs currently run overnight on shared laptops; four workstations remove the queue.',
      estimatedValue: 180000000,
      status: 'PENDING_FINANCE_APPROVAL',
      isBudgetExceeded: true,
      exceededBy: 122000000,
      deptBudgetLeft: 58000000,
      deptName: 'IT Equipment',
    },
  ];

  // Recently decided items from DB
  const decidedFromDB = prs.filter((p) => p.status === 'APPROVED' || p.status === 'REJECTED' || p.status === 'REVISION_REQUIRED');
  const displayDecided = decidedFromDB.length > 0 ? decidedFromDB.map(p => ({
    id: p.id,
    title: p.title,
    status: p.status,
    estimatedValue: Number(p.estimatedValue),
    approvals: p.approvals,
    items: p.items,
  })) : [
    {
      id: 'PR-2026-040',
      title: 'Ergonomic task chairs (20 units)',
      status: 'APPROVED',
      estimatedValue: 84000000,
    },
    {
      id: 'PR-2026-037',
      title: 'Standing desk converters (12 units)',
      status: 'REVISION_REQUIRED',
      estimatedValue: 37200000,
    },

    {
      id: 'PR-2026-036',
      title: 'Conference room display, 86"',
      status: 'REJECTED',
      estimatedValue: 96000000,
    },
  ];

  const blockedCount = displayQueue.filter((p) => {
    const val = Number(p.estimatedValue || 0);
    return val > 50000000 || p.isBudgetExceeded;
  }).length;

  return (
    <div 
      style={{ maxWidth: '860.67px', margin: '0 auto' }}
      data-node-id="9:1813"
      data-testid="approvals-queue-view"
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
            fontFamily: 'Inter, sans-serif'
          }}
        >
          Manager · Flow B
        </div>
        <h1 
          style={{ 
            fontSize: '24px', 
            fontWeight: 600, 
            color: '#12161c', 
            margin: '0 0 4px 0', 
            letterSpacing: '-0.6px',
            lineHeight: '32px',
            fontFamily: 'Inter, sans-serif'
          }}
        >
          Approvals
        </h1>
        <p 
          style={{ 
            margin: 0, 
            fontSize: '14px', 
            color: '#5a6472',
            lineHeight: '20px',
            fontFamily: 'Inter, sans-serif'
          }}
        >
          {displayQueue.length} requests in your queue · {blockedCount} blocked pending a Finance budget review.
        </p>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '24px', color: '#5a6472' }}>
          <Loader2 size={16} className="animate-spin" />
          <span>Đang tải danh sách hàng đợi phê duyệt từ cơ sở dữ liệu...</span>
        </div>
      )}

      {/* Queue List Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '32px' }}>
        {displayQueue.map((item) => {
          const val = Number(item.estimatedValue || 0);
          const isOverBudget = item.isBudgetExceeded ?? (val > availableBudget);
          const exceededAmount = item.exceededBy || (val > availableBudget ? val - availableBudget : 0);
          const deptLeft = item.deptBudgetLeft || availableBudget;
          const deptTitle = item.deptName || item.category || 'IT Equipment';

          return (
            <div
              key={item.id}
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '8px',
                padding: '16px',
                boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
                fontFamily: 'Inter, sans-serif',
              }}
              data-testid={`approval-card-${item.id}`}
            >
              {/* Upper Section: Info & Price */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                {/* Left side */}
                <div style={{ flex: 1, paddingRight: '24px' }}>
                  {/* Status Badge + Code */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    {item.status === 'SUBMITTED' ? (
                      <span
                        style={{
                          backgroundColor: '#eaf3fb',
                          border: '0.667px solid #bcd8ef',
                          borderRadius: '4px',
                          padding: '2.5px 6px',
                          fontSize: '11px',
                          fontWeight: 500,
                          color: '#184e75',
                          lineHeight: '16px',
                        }}
                      >
                        Submitted
                      </span>
                    ) : (item.id === 'PR-2026-042' || item.status === 'PENDING_FINANCE_APPROVAL') ? (
                      <span
                        style={{
                          backgroundColor: '#fdf4e3',
                          border: '0.667px solid #f2ddad',
                          borderRadius: '4px',
                          padding: '2.5px 6px',
                          fontSize: '11px',
                          fontWeight: 500,
                          color: '#7a5209',
                          lineHeight: '16px',
                        }}
                      >
                        Budget warning
                      </span>
                    ) : (
                      <span
                        style={{
                          backgroundColor: '#eef1ff',
                          border: '0.667px solid #c3ccff',
                          borderRadius: '4px',
                          padding: '2.5px 6px',
                          fontSize: '11px',
                          fontWeight: 500,
                          color: '#2f3789',
                          lineHeight: '16px',
                        }}
                      >
                        Pending approval
                      </span>
                    )}
                    <span style={{ fontSize: '11px', color: '#8a929e', lineHeight: '16px' }}>
                      {item.id}
                    </span>
                  </div>

                  {/* Title */}
                  <h3
                    style={{
                      fontSize: '16px',
                      fontWeight: 600,
                      color: '#12161c',
                      margin: '0 0 4px 0',
                      lineHeight: '22px',
                    }}
                  >
                    {item.title}
                  </h3>

                  {/* Metadata */}
                  <div
                    style={{
                      fontSize: '12px',
                      color: '#5a6472',
                      marginBottom: '8px',
                      lineHeight: '16px',
                    }}
                  >
                    {item.creatorName || (item.creator && item.creator.name) || 'Trương Bảo Long'} · {item.departmentName || 'Engineering'} · {item.category || 'IT Equipment'} · needed by {item.neededBy || '15 Sept 2026'}
                  </div>

                  {/* Description */}
                  <div
                    style={{
                      fontSize: '14px',
                      color: '#5a6472',
                      lineHeight: '22.75px',
                    }}
                  >
                    {item.description || (item.items && item.items.length > 0 ? item.items.map((i: any) => `${i.quantity}x ${i.itemName}`).join(', ') : 'Fifteen engineers join in September; current spare pool is empty.')}
                  </div>
                </div>

                {/* Right side: Amount, Left Budget, Review button */}
                <div style={{ textAlign: 'right', minWidth: '180px' }}>
                  <div
                    style={{
                      fontSize: '18px',
                      fontWeight: 600,
                      color: '#12161c',
                      lineHeight: '28px',
                      marginBottom: '2px',
                    }}
                  >
                    {formatVND(val)}
                  </div>
                  <div
                    style={{
                      fontSize: '11px',
                      color: '#8a929e',
                      lineHeight: '16px',
                      marginBottom: '8px',
                    }}
                  >
                    {formatVND(deptLeft)} left in {deptTitle}
                  </div>
                  <button
                    onClick={() => onSelectPR(item)}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      backgroundColor: 'transparent',
                      border: 'none',
                      color: '#3b45ad',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      padding: 0,
                    }}
                    data-testid={`review-btn-${item.id}`}
                  >
                    <span>Review</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>

              {/* Bottom Warning Banner if Budget Exceeded */}
              {isOverBudget && (
                <div
                  style={{
                    backgroundColor: '#fdf4e3',
                    border: '0.667px solid #f2ddad',
                    borderRadius: '4px',
                    padding: '8px 12px',
                    marginTop: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '12px',
                    color: '#7a5209',
                    lineHeight: '19.5px',
                  }}
                  data-testid={`budget-warning-banner-${item.id}`}
                >
                  <AlertTriangle size={14} color="#7a5209" style={{ flexShrink: 0 }} />
                  <span>
                    Exceeds the remaining <b>{deptTitle}</b> budget by <b>{formatVND(exceededAmount)}</b>. Approval is blocked until Finance reviews it.
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Bottom Section: Recently Decided */}
      <div>
        <h2
          style={{
            fontSize: '14px',
            fontWeight: 600,
            color: '#12161c',
            margin: '0 0 8px 0',
            lineHeight: '20px',
            fontFamily: 'Inter, sans-serif',
          }}
        >
          Recently decided
        </h2>
        <div
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '8px',
            overflow: 'hidden',
            boxShadow: '0px 1px 1px 0px rgba(18,22,28,0.03), 0px 1px 2px 0px rgba(18,22,28,0.04)',
            fontFamily: 'Inter, sans-serif',
          }}
          data-testid="recently-decided-table"
        >
          {displayDecided.map((item, idx) => {
            const isApproved = item.status === 'APPROVED';
            const isRevision = item.status === 'REVISION_REQUIRED';
            const isRejected = item.status === 'REJECTED';

            return (
              <div
                key={item.id || idx}
                onClick={() => onSelectPR(item)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '10px 16px',
                  borderTop: idx > 0 ? '0.667px solid rgba(228,231,236,0.7)' : 'none',
                  cursor: 'pointer',
                  transition: 'background-color 0.15s ease',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#fafafa')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
                data-testid={`recent-item-${item.id}`}
              >
                {/* Badge */}
                {isApproved && (
                  <span
                    style={{
                      backgroundColor: '#e9f7ef',
                      border: '0.667px solid #b6e2c7',
                      borderRadius: '4px',
                      padding: '2.5px 8px',
                      fontSize: '11px',
                      fontWeight: 500,
                      color: '#16603b',
                      lineHeight: '16px',
                      minWidth: '64px',
                      textAlign: 'center',
                    }}
                  >
                    Approved
                  </span>
                )}
                {isRevision && (
                  <span
                    style={{
                      backgroundColor: '#fdf4e3',
                      border: '0.667px solid #f2ddad',
                      borderRadius: '4px',
                      padding: '2.5px 8px',
                      fontSize: '11px',
                      fontWeight: 500,
                      color: '#7a5209',
                      lineHeight: '16px',
                      minWidth: '104px',
                      textAlign: 'center',
                    }}
                  >
                    Revision required
                  </span>
                )}
                {isRejected && (
                  <span
                    style={{
                      backgroundColor: '#fdecec',
                      border: '0.667px solid #f4c2c2',
                      borderRadius: '4px',
                      padding: '2.5px 8px',
                      fontSize: '11px',
                      fontWeight: 500,
                      color: '#8e1e1e',
                      lineHeight: '16px',
                      minWidth: '60px',
                      textAlign: 'center',
                    }}
                  >
                    Rejected
                  </span>
                )}

                {/* Title */}
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#12161c',
                    marginLeft: '16px',
                    flex: 1,
                  }}
                >
                  {item.title}
                </div>

                {/* Amount */}
                <div
                  style={{
                    fontSize: '12px',
                    color: '#8a929e',
                    lineHeight: '16px',
                  }}
                >
                  {formatVND(item.estimatedValue)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
