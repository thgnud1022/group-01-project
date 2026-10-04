import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, 
  AlertTriangle,
  Loader2
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface BudgetReviewViewProps {
  user: AuthenticatedUser | null;
  onSelectPR: (pr: any) => void;
}

export const BudgetReviewView: React.FC<BudgetReviewViewProps> = ({
  user,
  onSelectPR,
}) => {
  const [prs, setPrs] = useState<any[]>([]);
  const [budgets, setBudgets] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [allPrs, allBudgets] = await Promise.all([
        api.listPRs().catch(() => []),
        api.listBudgets().catch(() => []),
      ]);
      setPrs(allPrs || []);
      setBudgets(allBudgets || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

  // Find escalated PRs: e.g. PRs in PENDING_FINANCE_APPROVAL or > 50M or with budget warning
  const escalatedPRs = prs.filter((p) => 
    p.status === 'PENDING_FINANCE_APPROVAL' || 
    (p.status === 'PENDING_MANAGER_APPROVAL' && Number(p.estimatedValue) > 50000000)
  );

  const displayEscalated = escalatedPRs.length > 0 ? escalatedPRs[0] : {
    id: 'PR-2026-042',
    title: 'Data team workstations (4 units)',
    creatorName: 'Trương Bảo Long',
    departmentName: 'Engineering',
    neededBy: '05 Oct 2026',
    estimatedValue: 180000000,
    overAmount: 122000000,
    status: 'PENDING_FINANCE_APPROVAL',
  };

  const budgetLines = [
    {
      category: 'IT Equipment',
      owner: 'Finance · Trần Mỹ Linh',
      allocated: 500000000,
      spent: 412000000,
      committed: 30000000,
      available: 58000000,
      usedPercent: 88,
      isWarning: true,
    },
    {
      category: 'Office Supplies',
      owner: 'Finance · Trần Mỹ Linh',
      allocated: 120000000,
      spent: 61500000,
      committed: 8000000,
      available: 50500000,
      usedPercent: 58,
      isWarning: false,
    },
    {
      category: 'Facilities',
      owner: 'Finance · Vũ Quang Huy',
      allocated: 300000000,
      spent: 90000000,
      committed: 24000000,
      available: 186000000,
      usedPercent: 38,
      isWarning: false,
    },
    {
      category: 'Software & Licences',
      owner: 'Finance · Vũ Quang Huy',
      allocated: 260000000,
      spent: 118000000,
      committed: 0,
      available: 142000000,
      usedPercent: 45,
      isWarning: false,
    },
  ];

  return (
    <div 
      style={{ maxWidth: '876px', margin: '0 auto', fontFamily: 'Inter, sans-serif' }}
      data-node-id="9:2431"
      data-testid="budget-review-view"
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
          }}
        >
          Finance · Flow B
        </div>
        <h1 
          style={{ 
            fontSize: '24px', 
            fontWeight: 600, 
            color: '#12161c', 
            margin: '0 0 4px 0', 
            letterSpacing: '-0.6px',
            lineHeight: '32px',
          }}
        >
          Budget review
        </h1>
        <p 
          style={{ 
            margin: 0, 
            fontSize: '14px', 
            color: '#5a6472',
            lineHeight: '20px',
          }}
        >
          Requests a manager escalated because they exceed the remaining budget on their category.
        </p>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '16px 0', color: '#5a6472' }}>
          <Loader2 size={16} className="animate-spin" />
          <span>Đang tải số liệu ngân sách...</span>
        </div>
      )}

      {/* Top Escalated PR Card */}
      <div
        style={{
          backgroundColor: '#fdf4e3',
          border: '0.667px solid #f2ddad',
          borderRadius: '8px',
          padding: '16px',
          boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
          marginBottom: '32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
        data-testid={`escalated-pr-${displayEscalated.id}`}
      >
        <div>
          {/* Badge + ID */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
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
            <span style={{ fontSize: '11px', color: '#8a929e', lineHeight: '16px' }}>
              {displayEscalated.id}
            </span>
          </div>

          {/* Title */}
          <h3
            style={{
              fontSize: '16px',
              fontWeight: 600,
              color: '#12161c',
              margin: '0 0 4px 0',
              lineHeight: '24px',
            }}
          >
            {displayEscalated.title}
          </h3>

          {/* Metadata */}
          <div
            style={{
              fontSize: '12px',
              color: '#5a6472',
              lineHeight: '16px',
            }}
          >
            {displayEscalated.creatorName || (displayEscalated.creator && displayEscalated.creator.name) || 'Trương Bảo Long'} · {displayEscalated.departmentName || 'Engineering'} · needed by {displayEscalated.neededBy || '05 Oct 2026'}
          </div>
        </div>

        {/* Right side: Amount, Over by, Review link */}
        <div style={{ textAlign: 'right', minWidth: '140px' }}>
          <div
            style={{
              fontSize: '18px',
              fontWeight: 600,
              color: '#12161c',
              lineHeight: '28px',
            }}
          >
            {formatVND(displayEscalated.estimatedValue)}
          </div>
          <div
            style={{
              fontSize: '12px',
              color: '#7a5209',
              lineHeight: '16px',
              marginBottom: '8px',
            }}
          >
            over by {formatVND(displayEscalated.overAmount || 122000000)}
          </div>
          <button
            onClick={() => onSelectPR(displayEscalated)}
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
            data-testid="review-budget-btn"
          >
            <span>Review budget</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {/* Section Title: Q3 2026 budget lines */}
      <h2
        style={{
          fontSize: '14px',
          fontWeight: 600,
          color: '#12161c',
          margin: '0 0 8px 0',
          lineHeight: '20px',
        }}
      >
        Q3 2026 budget lines
      </h2>

      {/* Budget Table */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0px 1px 1px 0px rgba(18,22,28,0.03), 0px 1px 2px 0px rgba(18,22,28,0.04)',
        }}
        data-testid="budget-lines-table"
      >
        {/* Table Header */}
        <div
          style={{
            backgroundColor: '#fbfcfd',
            borderBottom: '0.667px solid #e4e7ec',
            display: 'grid',
            gridTemplateColumns: '182px 144px 144px 134px 144px 128px',
            height: '32px',
            alignItems: 'center',
            padding: '0 16px',
            fontSize: '11px',
            fontWeight: 600,
            color: '#8a929e',
            letterSpacing: '0.275px',
          }}
        >
          <div>Category</div>
          <div style={{ textAlign: 'right' }}>Allocated</div>
          <div style={{ textAlign: 'right' }}>Spent</div>
          <div style={{ textAlign: 'right' }}>Committed</div>
          <div style={{ textAlign: 'right' }}>Available</div>
          <div style={{ paddingLeft: '16px' }}>Used</div>
        </div>

        {/* Table Rows */}
        {budgetLines.map((line, idx) => (
          <div
            key={line.category}
            style={{
              display: 'grid',
              gridTemplateColumns: '182px 144px 144px 134px 144px 128px',
              padding: '12px 16px',
              alignItems: 'center',
              borderTop: idx > 0 ? '0.667px solid rgba(228,231,236,0.7)' : 'none',
              fontSize: '14px',
            }}
          >
            {/* Category + Owner */}
            <div>
              <div style={{ fontWeight: 500, color: '#12161c', lineHeight: '20px' }}>
                {line.category}
              </div>
              <div style={{ fontSize: '11px', color: '#8a929e', lineHeight: '16px' }}>
                {line.owner}
              </div>
            </div>

            {/* Allocated */}
            <div style={{ textAlign: 'right', color: '#12161c' }}>
              {formatVND(line.allocated)}
            </div>

            {/* Spent */}
            <div style={{ textAlign: 'right', color: '#5a6472' }}>
              {formatVND(line.spent)}
            </div>

            {/* Committed */}
            <div style={{ textAlign: 'right', color: '#5a6472' }}>
              {formatVND(line.committed)}
            </div>

            {/* Available */}
            <div 
              style={{ 
                textAlign: 'right', 
                fontWeight: line.isWarning ? 600 : 400, 
                color: line.isWarning ? '#7a5209' : '#12161c' 
              }}
            >
              {formatVND(line.available)}
            </div>

            {/* Used progress */}
            <div style={{ paddingLeft: '16px' }}>
              <div
                style={{
                  backgroundColor: '#f5f6f8',
                  height: '6px',
                  borderRadius: '9999px',
                  overflow: 'hidden',
                  width: '96px',
                  marginBottom: '4px',
                }}
              >
                <div
                  style={{
                    backgroundColor: line.isWarning ? '#96650b' : '#4a56d2',
                    height: '100%',
                    width: `${line.usedPercent}%`,
                  }}
                />
              </div>
              <div style={{ fontSize: '11px', color: '#8a929e', lineHeight: '16px' }}>
                {line.usedPercent}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
