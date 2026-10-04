import React, { useState, useEffect } from 'react';
import { Plus, Search, AlertCircle, AlertTriangle, FileText, ChevronRight, RefreshCw } from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface PurchaseRequestsViewProps {
  onNewRequest: () => void;
  onSelectPR?: (pr: any) => void;
  user: AuthenticatedUser | null;
}

// Sample static reference cards from Figma frame 9:317 for Visual match
const referencePRs = [
  {
    id: 'PR-2026-042',
    title: 'Data team workstations (4 units)',
    creatorName: 'Trương Bảo Long · Engineering',
    departmentName: 'IT Equipment',
    estimatedValue: 180000000,
    neededBy: '05 Oct 2026',
    status: 'BUDGET_WARNING',
    overBudget: true,
  },
  {
    id: 'PR-2026-041',
    title: 'Laptops for engineering onboarding (15 seats)',
    creatorName: 'Nguyễn Hoài An · Engineering',
    departmentName: 'IT Equipment',
    estimatedValue: 300000000,
    neededBy: '15 Sept 2026',
    status: 'PENDING_APPROVAL',
    overBudget: true,
  },
  {
    id: 'PR-2026-040',
    title: 'Ergonomic task chairs (20 units)',
    creatorName: 'Phạm Thu Hà · Operations',
    departmentName: 'Facilities',
    estimatedValue: 84000000,
    neededBy: '30 Sept 2026',
    status: 'APPROVED',
  },
  {
    id: 'PR-2026-039',
    title: 'Printer toner — bulk replenishment',
    creatorName: 'Phạm Thu Hà · Operations',
    departmentName: 'Office Supplies',
    estimatedValue: 50400000,
    neededBy: '05 Sept 2026',
    status: 'QUOTATION_COMPARISON',
  },
  {
    id: 'PR-2026-038',
    title: 'Access-layer network switches (8 units)',
    creatorName: 'Nguyễn Hoài An · Engineering',
    departmentName: 'IT Equipment',
    estimatedValue: 216000000,
    neededBy: '20 Sept 2026',
    status: 'AI_RECOMMENDATION_READY',
  },
  {
    id: 'PR-2026-037',
    title: 'Standing desk converters (12 units)',
    creatorName: 'Đặng Khánh Vy · People',
    departmentName: 'Facilities',
    estimatedValue: 37200000,
    neededBy: '01 Oct 2026',
    status: 'REVISION_REQUIRED',
  },
  {
    id: 'PR-2026-036',
    title: 'Conference room display, 86"',
    creatorName: 'Phạm Thu Hà · Operations',
    departmentName: 'IT Equipment',
    estimatedValue: 96000000,
    neededBy: '10 Sept 2026',
    status: 'REJECTED',
    overBudget: true,
  },
  {
    id: 'PR-2026-035',
    title: 'Whiteboard markers and erasers',
    creatorName: 'Đặng Khánh Vy · People',
    departmentName: 'Office Supplies',
    estimatedValue: 1680000,
    neededBy: '—',
    status: 'DRAFT',
  },
  {
    id: 'PR-2026-034',
    title: 'Server rack rails and cable management',
    creatorName: 'Trương Bảo Long · Engineering',
    departmentName: 'IT Equipment',
    estimatedValue: 14400000,
    neededBy: '25 Sept 2026',
    status: 'ERROR',
  },
  {
    id: 'PR-2026-033',
    title: 'Monitor arms (10 units)',
    creatorName: 'Trương Bảo Long · Engineering',
    departmentName: 'Office Supplies',
    estimatedValue: 11500000,
    neededBy: '18 Sept 2026',
    status: 'SUBMITTED',
  },
  {
    id: 'PR-2026-032',
    title: 'Meeting room webcams (10 units)',
    creatorName: 'Phạm Thu Hà · Operations',
    departmentName: 'IT Equipment',
    estimatedValue: 45000000,
    neededBy: '30 Aug 2026',
    status: 'PO_ISSUED',
  },
  {
    id: 'PR-2026-031',
    title: 'Office paper A4 (200 reams)',
    creatorName: 'Phạm Thu Hà · Operations',
    departmentName: 'Office Supplies',
    estimatedValue: 24800000,
    neededBy: '20 Jul 2026',
    status: 'CLOSED',
  },
];

export const PurchaseRequestsView: React.FC<PurchaseRequestsViewProps> = ({
  onNewRequest,
  onSelectPR,
  user,
}) => {
  const [prs, setPrs] = useState<any[]>(referencePRs);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'All' | 'In flight' | 'Needs me' | 'Sourcing' | 'Fulfilment' | 'Closed'>('All');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchPRs = async () => {
    try {
      setLoading(true);
      const data = await api.listPRs();
      if (Array.isArray(data) && data.length > 0) {
        const backendIds = new Set(data.map((d: any) => d.id));
        const merged = [...data, ...referencePRs.filter((r) => !backendIds.has(r.id))];
        setPrs(merged);
      }
    } catch (err: any) {
      console.warn('Backend PR load notice:', err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPRs();
  }, []);

  const displayPRs = (prs.length > 0 ? prs : referencePRs).filter((item) => {
    const title = item.title?.toLowerCase() || '';
    const id = item.id?.toLowerCase() || '';
    const cat = (item.departmentName || item.deptId || '')?.toLowerCase();
    const query = searchQuery.toLowerCase();
    const matchesSearch = !query || title.includes(query) || id.includes(query) || cat.includes(query);

    if (activeTab === 'All') return matchesSearch;
    if (activeTab === 'In flight') return matchesSearch && (item.status?.includes('PENDING') || item.status === 'SUBMITTED');
    if (activeTab === 'Needs me') return matchesSearch && (item.status === 'REVISION_REQUIRED' || item.status === 'ERROR');
    if (activeTab === 'Sourcing') return matchesSearch && (item.status === 'APPROVED' || item.status?.includes('QUOTATION'));
    if (activeTab === 'Fulfilment') return matchesSearch && item.status?.includes('PO');
    if (activeTab === 'Closed') return matchesSearch && item.status === 'CLOSED';
    return matchesSearch;
  });

  const getStatusBadge = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'APPROVED':
        return <span className="badge badge-approved">Approved</span>;
      case 'BUDGET_WARNING':
        return <span className="badge badge-warning">Budget warning</span>;
      case 'PENDING_APPROVAL':
      case 'PENDING_MANAGER_APPROVAL':
      case 'PENDING_FINANCE_APPROVAL':
        return <span className="badge badge-pending">Pending approval</span>;
      case 'QUOTATION_COMPARISON':
      case 'COLLECTING_QUOTATIONS':
        return <span className="badge badge-sourcing">Quotation comparison</span>;
      case 'AI_RECOMMENDATION_READY':
        return <span className="badge badge-pending">AI recommendation ready</span>;
      case 'REVISION_REQUIRED':
        return <span className="badge badge-warning">Revision required</span>;
      case 'REJECTED':
        return <span className="badge badge-error">Rejected</span>;
      case 'ERROR':
        return <span className="badge badge-error">Error</span>;
      case 'SUBMITTED':
        return <span className="badge badge-pending">Submitted</span>;
      case 'PO_ISSUED':
      case 'PO_CREATED':
        return <span className="badge badge-sourcing">PO issued</span>;
      case 'CLOSED':
        return <span className="badge badge-draft">Closed</span>;
      case 'DRAFT':
      default:
        return <span className="badge badge-draft">Draft</span>;
    }
  };

  return (
    <div style={{ maxWidth: '860px', margin: '0 auto' }} data-node-id="9:317" data-testid="purchase-requests-view">
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <div
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#8a929e',
              textTransform: 'uppercase',
              letterSpacing: '0.55px',
              marginBottom: '4px',
            }}
          >
            Employee
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
            Purchase requests
          </h1>
          <p style={{ margin: 0, fontSize: '14px', color: '#5a6472', lineHeight: '20px' }}>
            Everything you raised, and where each one currently sits.
          </p>
        </div>

        <button
          onClick={onNewRequest}
          className="btn btn-primary"
          style={{ height: '36px', padding: '0 16px', borderRadius: '4px' }}
          data-testid="new-request-btn"
        >
          <Plus size={16} />
          <span>New request</span>
        </button>
      </div>

      {/* Action Alert Cards (Figma 9:333) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '24px' }}>
        {/* Card 1: Revision required (Figma 9:334) */}
        <div
          style={{
            backgroundColor: '#fdf4e3',
            border: '0.667px solid #f2ddad',
            borderRadius: '8px',
            padding: '16px',
            boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
            cursor: 'pointer',
          }}
          data-node-id="9:334"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <AlertTriangle size={16} color="#7a5209" />
            <span className="badge badge-warning">Revision required</span>
            <span style={{ fontSize: '11px', color: '#8a929e' }}>PR-2026-037</span>
          </div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
            Standing desk converters (12 units)
          </div>
          <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '19.5px' }}>
            Split into two phases and name the twelve recipients before resubmitting.
          </div>
        </div>

        {/* Card 2: Error (Figma 9:345) */}
        <div
          style={{
            backgroundColor: '#fdecec',
            border: '0.667px solid #f4c2c2',
            borderRadius: '8px',
            padding: '16px',
            boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
            cursor: 'pointer',
          }}
          data-node-id="9:345"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <AlertCircle size={16} color="#8e1e1e" />
            <span className="badge badge-error">Error</span>
            <span style={{ fontSize: '11px', color: '#8a929e' }}>PR-2026-034</span>
          </div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
            Server rack rails and cable management
          </div>
          <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '19.5px' }}>
            Submission could not be posted to the ERP (cost-centre service timed out). Nothing was sent for approval.
          </div>
        </div>
      </div>

      {/* Filter Tabs + Search bar (Figma 9:356) */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '12px',
        }}
        data-node-id="9:356"
      >
        {/* Tablist */}
        <div
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '4px',
            height: '33.33px',
            display: 'inline-flex',
            alignItems: 'center',
            padding: '2px 4px',
            boxSizing: 'border-box',
          }}
          role="tablist"
          data-node-id="9:357"
        >
          {(['All', 'In flight', 'Needs me', 'Sourcing', 'Fulfilment', 'Closed'] as const).map((tab) => {
            const isSelected = activeTab === tab;
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  height: '24px',
                  padding: '0 10px',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: isSelected ? '#eef1ff' : 'transparent',
                  color: isSelected ? '#2f3789' : '#5a6472',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  transition: 'all 0.1s ease',
                }}
                role="tab"
                aria-selected={isSelected}
                data-testid={`tab-${tab.toLowerCase().replace(/\s+/g, '-')}`}
              >
                {tab}
              </button>
            );
          })}
        </div>

        {/* Search input with left search icon */}
        <div style={{ position: 'relative', width: '320px' }}>
          <Search
            size={16}
            color="#8a929e"
            style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }}
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by id, title, category"
            style={{
              width: '100%',
              height: '37px',
              padding: '0 12px 0 34px',
              borderRadius: '4px',
              border: '0.667px solid #e4e7ec',
              backgroundColor: '#ffffff',
              fontSize: '13px',
              color: '#12161c',
              fontFamily: 'inherit',
              boxSizing: 'border-box',
              outline: 'none',
            }}
            data-testid="search-prs-input"
          />
        </div>
      </div>

      {/* PR Table Container (Figma 9:377) */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0px 1px 2px rgba(18, 22, 28, 0.05)',
        }}
        data-node-id="9:377"
        data-testid="pr-table"
      >
        {/* Table Header Row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '296px 126px 143px 113px 1fr',
            height: '32.33px',
            backgroundColor: '#ffffff',
            borderBottom: '0.667px solid #e4e7ec',
            alignItems: 'center',
            padding: '0 16px',
            fontSize: '11px',
            fontWeight: 600,
            color: '#5a6472',
            letterSpacing: '0.3px',
          }}
        >
          <div>Request</div>
          <div>Category</div>
          <div style={{ textAlign: 'right', paddingRight: '12px' }}>Estimated</div>
          <div>Needed by</div>
          <div>Status</div>
        </div>

        {/* Table Body Rows */}
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#8a929e', fontSize: '13px' }}>
            <RefreshCw size={20} className="animate-spin" style={{ margin: '0 auto 8px' }} />
            <span>Đang tải danh sách yêu cầu mua sắm...</span>
          </div>
        ) : displayPRs.length === 0 ? (
          <div style={{ padding: '48px', textAlign: 'center', color: '#8a929e', fontSize: '13px' }}>
            Không tìm thấy yêu cầu mua sắm nào phù hợp với bộ lọc.
          </div>
        ) : (
          displayPRs.map((item, index) => {
            const formattedPrice = Number(item.estimatedValue || 0).toLocaleString();
            return (
              <div
                key={item.id || index}
                onClick={() => onSelectPR && onSelectPR(item)}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '296px 126px 143px 113px 1fr',
                  minHeight: '78px',
                  alignItems: 'center',
                  padding: '12px 16px',
                  borderBottom: index < displayPRs.length - 1 ? '0.667px solid #f0f2f5' : 'none',
                  cursor: 'pointer',
                  transition: 'background-color 0.1s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#fbfcfd';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#ffffff';
                }}
                data-testid={`pr-row-${item.id}`}
              >
                {/* Request Column: Title + Meta */}
                <div style={{ paddingRight: '8px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '2px' }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: '11px', color: '#8a929e' }}>
                    {item.id} · {item.creatorName || item.creatorId || 'Employee'}
                  </div>
                </div>

                {/* Category Column */}
                <div style={{ fontSize: '13px', color: '#5a6472' }}>
                  {item.departmentName || item.deptId || 'IT Equipment'}
                </div>

                {/* Estimated Column */}
                <div style={{ textAlign: 'right', paddingRight: '12px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                    {formattedPrice}
                  </div>
                  {item.overBudget && (
                    <div style={{ fontSize: '10px', color: '#7a5209', marginTop: '2px' }}>
                      over remaining budget
                    </div>
                  )}
                </div>

                {/* Needed by Column */}
                <div style={{ fontSize: '13px', color: '#5a6472' }}>
                  {item.neededBy || '15 Oct 2026'}
                </div>

                {/* Status Column */}
                <div>
                  {getStatusBadge(item.status)}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
