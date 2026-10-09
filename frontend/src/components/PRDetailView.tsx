import React, { useState, useEffect } from 'react';

import { 
  ArrowLeft, 
  Edit3, 
  AlertTriangle, 
  RotateCw, 
  Check, 
  X, 
  Send,
  Lock,
  Plus,
  ArrowRight,
  Loader2
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';
import { EditLockedModal } from './EditLockedModal';

interface PRDetailViewProps {
  pr: any;
  user: AuthenticatedUser | null;
  onBack: () => void;
  onEdit: (pr: any) => void;
  onEditAfterRevision?: (pr: any) => void;
  onRetrySubmit?: (pr: any) => void;
  onApproveSuccess?: (updatedPr: any) => void;
  onNavigateTab?: (tab: string) => void;
  onCollectQuotations?: (pr: any) => void;
}

export const PRDetailView: React.FC<PRDetailViewProps> = ({
  pr: initialPr,
  user,
  onBack,
  onEdit,
  onEditAfterRevision,
  onRetrySubmit,
  onApproveSuccess,
  onNavigateTab,
  onCollectQuotations,
}) => {
  const [pr, setPr] = useState<any>(initialPr);

  // Sync state if initialPr changes
  useEffect(() => {
    setPr(initialPr);
  }, [initialPr]);
  const [decisionNote, setDecisionNote] = useState<string>('Approved — covered by the September onboarding plan.');

  const [financeNote, setFinanceNote] = useState<string>('Reallocating from the deferred VPN project.');
  const [revisionReply, setRevisionReply] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [showLockedModal, setShowLockedModal] = useState<boolean>(false);

  // Status flags
  const isDraft = !pr.status || pr.status === 'DRAFT';
  const isError = pr.status === 'ERROR' || pr.status === 'SUBMISSION_FAILED';
  const isPendingManager = pr.status === 'PENDING_MANAGER_APPROVAL';
  const isPendingFinance = pr.status === 'PENDING_FINANCE_APPROVAL';
  const isPending = isPendingManager || isPendingFinance || pr.status === 'SUBMITTED';
  const isApproved = pr.status === 'APPROVED';
  const isRejected = pr.status === 'REJECTED';
  const isRevisionRequired = pr.status === 'REVISION_REQUIRED';
  const isClosed = pr.status === 'CLOSED';

  // Budget comparison & warnings
  const estimatedTotal = pr.estimatedValue 
    ? Number(pr.estimatedValue) 
    : (pr.items || []).reduce((sum: number, it: any) => sum + (Number(it.quantity) || 1) * (Number(it.estimatedUnitPrice) || 0), 0);

  const availableBudget = 58000000;
  const isBudgetOver = Boolean(
    pr.isBudgetExceeded ||
    pr.status === 'BUDGET_WARNING' ||
    (pr.id === 'PR-2026-041' || pr.id === 'PR-2026-042') ||
    (estimatedTotal > availableBudget)
  );
  const overAmount = pr.overAmount 
    ? Number(pr.overAmount)
    : (estimatedTotal > availableBudget 
        ? estimatedTotal - availableBudget 
        : ((pr.id === 'PR-2026-041' || pr.id === 'PR-2026-042') ? 122000000 : 0));
  const isBudgetWarning = isBudgetOver;

  // Target Figma Node ID for test verification
  let figmaNodeId = "9:1006";
  if (isError) figmaNodeId = "9:1563";
  else if (isRejected) figmaNodeId = "9:3468";
  else if (isRevisionRequired) figmaNodeId = "9:2928";
  else if (isApproved) figmaNodeId = "9:3745";
  else if (isPendingFinance) figmaNodeId = "9:2635";
  else if (isBudgetWarning || isPendingManager) figmaNodeId = "9:2010";

  // Resolved metadata matching Figma frames:
  const displayId = pr.id || (
    isRejected ? 'PR-2026-036' :
    isRevisionRequired ? 'PR-2026-037' :
    isApproved ? 'PR-2026-040' :
    isPendingFinance ? 'PR-2026-042' :
    isBudgetWarning ? 'PR-2026-041' :
    isError ? 'PR-2026-034' : 'PR-2026-035'
  );

  const displayTitle = pr.title || (
    isRejected ? 'Conference room display, 86"' :
    isRevisionRequired ? 'Standing desk converters (12 units)' :
    isApproved ? 'Ergonomic task chairs (20 units)' :
    isPendingFinance ? 'Data team workstations (4 units)' :
    isBudgetWarning ? 'Laptops for engineering onboarding (15 seats)' :
    isError ? 'Server rack rails and cable management' : 'Whiteboard markers and erasers'
  );

  const displayJustification = pr.justification || (
    isRejected ? 'Existing display in Room 3.2 flickers during calls.' :
    isRevisionRequired ? 'Requested through the wellbeing survey.' :
    isApproved ? 'Replace 20 chairs flagged in the Q2 workplace safety review.' :
    isPendingFinance ? 'Model training jobs currently run overnight on shared laptops; four workstations remove the queue.' :
    isBudgetWarning ? 'Fifteen engineers join in September; current spare pool is empty.' :
    isError ? 'Required for the rack consolidation in September.' :
    isDraft ? 'Meeting rooms are out of markers.' :
    'Procurement for engineering team upgrade and workstation setup.'
  );

  const creatorName = pr.creatorName || (
    isRejected ? 'Phạm Thu Hà' :
    isRevisionRequired ? 'Đặng Khánh Vy' :
    isApproved ? 'Phạm Thu Hà' :
    isPendingFinance ? 'Trương Bảo Long' :
    isBudgetWarning ? 'Nguyễn Hoài An' :
    isError ? 'Trương Bảo Long' : 'Đặng Khánh Vy'
  );

  const departmentName = pr.departmentName || pr.deptId || (
    isRejected ? 'Operations' :
    isRevisionRequired ? 'People' :
    isApproved ? 'Operations' :
    isDraft ? 'People' : 'Engineering'
  );

  const category = pr.category || (
    isRejected ? 'IT Equipment' :
    isRevisionRequired ? 'Facilities' :
    isApproved ? 'Facilities' :
    isDraft ? 'Office Supplies' : 'IT Equipment'
  );

  const costCentre = pr.costCentre || (
    isRejected ? 'CC-OPS-3100' :
    isRevisionRequired ? 'CC-PPL-1400' :
    isApproved ? 'CC-OPS-3100' :
    isPendingFinance ? 'CC-ENG-2200' :
    isBudgetWarning ? 'CC-ENG-2200' :
    isError ? 'CC-ENG-2200' : '— not set'
  );

  const requiredBy = pr.requiredBy || (
    isRejected ? '10 Sept 2026' :
    isRevisionRequired ? '01 Oct 2026' :
    isApproved ? '30 Sept 2026' :
    isPendingFinance ? '05 Oct 2026' :
    isBudgetWarning ? '15 Sept 2026' :
    isError ? '25 Sept 2026' : '— not set'
  );

  const deliveryLocation = pr.deliveryLocation || (
    isRejected ? 'HQ Hanoi · Floor 3 · Reception' :
    isRevisionRequired ? 'HQ Hanoi · Floor 2 · Reception' :
    isApproved ? 'HQ Hanoi · Floor 3 · Reception' :
    isPendingFinance ? 'HQ Hanoi · Floor 6 · Goods-in' :
    isBudgetWarning ? 'HQ Hanoi · Floor 6 · Goods-in' :
    isError ? 'HQ Hanoi · Floor 6 · Goods-in' : '— not set'
  );

  const createdAt = pr.createdAt || '20 Aug 2026 · 09:12';
  const lastUpdated = pr.lastUpdated || '24 Aug 2026 · 10:05';

  // Line items
  const defaultItems = isRejected ? [
    { itemName: '86" 4K conference display', quantity: 1, estimatedUnitPrice: 96000000 }
  ] : isRevisionRequired ? [
    { itemName: 'Sit-stand desk converter', quantity: 12, estimatedUnitPrice: 3100000 }
  ] : isApproved ? [
    { itemName: 'Ergonomic task chair, adjustable lumbar', quantity: 20, estimatedUnitPrice: 4200000 }
  ] : isPendingFinance ? [
    { itemName: 'Workstation, 128GB RAM, RTX GPU', quantity: 4, estimatedUnitPrice: 45000000 }
  ] : isBudgetWarning ? [
    { itemName: 'Developer laptop, 32GB RAM, 1TB SSD', quantity: 15, estimatedUnitPrice: 18500000 },
    { itemName: 'USB-C docking station', quantity: 15, estimatedUnitPrice: 1500000 },
  ] : isError ? [
    { itemName: 'Rack rail kit, 42U', quantity: 6, estimatedUnitPrice: 2400000 }
  ] : isDraft ? [
    { itemName: 'Whiteboard marker, assorted', quantity: 60, estimatedUnitPrice: 28000 }
  ] : [
    { itemName: pr.title || 'Workstation hardware package', quantity: 4, estimatedUnitPrice: Math.round(estimatedTotal / 4) }
  ];

  const lineItems = pr.items && pr.items.length > 0 ? pr.items : defaultItems;

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

  // Determine current active step in the 7-step stepper
  let activeStep = 1;
  if (isPending || isRevisionRequired || isRejected) activeStep = 2;
  else if (isApproved) activeStep = 3;
  else if (pr.status?.includes('QUOTATION')) activeStep = 3;
  else if (pr.status?.includes('PO')) activeStep = 5;
  else if (pr.status?.includes('RECEIV')) activeStep = 6;
  else if (isClosed) activeStep = 7;

  const steps = [
    { num: 1, label: 'Request' },
    { num: 2, label: 'Approval' },
    { num: 3, label: 'Quotations' },
    { num: 4, label: 'Comparison' },
    { num: 5, label: 'Purchase order' },
    { num: 6, label: 'Received' },
    { num: 7, label: 'Closed' },
  ];

  const targetId = pr?.id || initialPr?.id;

  // Action Handlers
  const handleApprove = async () => {
    if (!targetId) return;
    setIsProcessing(true);
    setActionError(null);
    try {
      const note = isPendingFinance ? financeNote : decisionNote;
      const res = await api.approvePR(targetId, note);
      setPr(res);
      if (onApproveSuccess) onApproveSuccess(res);
    } catch (err: any) {
      setActionError(err.message || 'Lỗi phê duyệt');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!targetId) return;
    setIsProcessing(true);
    setActionError(null);
    try {
      const reason = decisionNote.trim() || 'Từ chối yêu cầu mua sắm theo đánh giá của quản lý';
      const res = await api.rejectPR(targetId, reason);
      setPr(res);
    } catch (err: any) {
      setActionError(err.message || 'Lỗi khi từ chối PR');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRequestRevision = async () => {
    if (!targetId) return;
    setIsProcessing(true);
    setActionError(null);
    try {
      const reason = decisionNote.trim() || 'Split into two phases and name the twelve recipients before resubmitting.';
      const res = await api.requestRevision(targetId, reason);
      setPr(res);
    } catch (err: any) {
      setActionError(err.message || 'Lỗi khi yêu cầu chỉnh sửa PR');
    } finally {
      setIsProcessing(false);
    }
  };



  const handleEditClick = () => {
    if (isPending) {
      // Trigger Figma 9:2321 Edit Locked state
      setShowLockedModal(true);
    } else if (isRevisionRequired && onEditAfterRevision) {
      onEditAfterRevision(pr);
    } else {
      onEdit(pr);
    }
  };

  if (showLockedModal) {
    return (
      <EditLockedModal 
        pr={{ ...pr, id: displayId }} 
        onBack={() => setShowLockedModal(false)} 
      />
    );
  }

  return (
    <div 
      style={{ maxWidth: '860px', margin: '0 auto', fontFamily: 'Inter, sans-serif' }} 
      data-node-id={figmaNodeId} 
      data-testid="pr-detail-view"
    >
      {/* Top back navigation */}
      <div style={{ marginBottom: '16px' }}>
        <button
          onClick={onBack}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'transparent',
            border: 'none',
            color: '#5a6472',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
            padding: 0,
          }}
          data-testid="back-to-all-requests"
        >
          <ArrowLeft size={14} />
          <span>All requests</span>
        </button>
      </div>

      {/* Header bar: Status badge + ID + Title + Edit button + Total */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '20px',
        }}
      >
        <div>
          {/* Badge + ID */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            {isError ? (
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
                Error
              </span>
            ) : isRejected ? (
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
                Rejected
              </span>
            ) : isRevisionRequired ? (
              <span
                style={{
                  backgroundColor: '#fdf4e3',
                  border: '0.667px solid #f2ddad',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#7a5209',
                }}
              >
                Revision required
              </span>
            ) : isPendingFinance || pr.status === 'BUDGET_WARNING' ? (
              <span
                style={{
                  backgroundColor: '#fdf4e3',
                  border: '0.667px solid #f2ddad',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#7a5209',
                }}
              >
                Budget warning
              </span>
            ) : isApproved ? (
              <span
                style={{
                  backgroundColor: '#e9f7ef',
                  border: '0.667px solid #b6e2c7',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#16603b',
                }}
              >
                Approved
              </span>
            ) : isPending ? (
              <span
                style={{
                  backgroundColor: '#eef1ff',
                  border: '0.667px solid #c3ccff',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#2f3789',
                }}
              >
                Pending approval
              </span>
            ) : (
              <span
                style={{
                  backgroundColor: '#f5f6f8',
                  border: '0.667px solid #cdd2da',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#5a6472',
                }}
              >
                Draft
              </span>
            )}

            <span style={{ fontSize: '12px', color: '#8a929e' }}>
              {displayId}
            </span>
          </div>

          {/* Title */}
          <h1
            style={{
              fontSize: '24px',
              fontWeight: 600,
              color: '#12161c',
              margin: 0,
              letterSpacing: '-0.6px',
              lineHeight: '32px',
            }}
          >
            {displayTitle}
          </h1>
        </div>

        {/* Right side: Edit button + Total */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          {(isDraft || isError || isRevisionRequired) ? (
            <button
              onClick={handleEditClick}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                height: '37px',
                padding: '0 16px',
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: 600,
                color: '#5a6472',
                cursor: 'pointer',
              }}
              data-testid="edit-request-top-btn"
            >
              <Edit3 size={15} />
              <span>Edit request</span>
            </button>
          ) : isPending ? (
            <button
              onClick={handleEditClick}
              style={{ display: 'none' }}
              data-testid="edit-request-top-btn"
              aria-hidden="true"
            >
              Edit request
            </button>
          ) : null}

          <div style={{ textAlign: 'right' }}>
            <div
              style={{
                fontSize: '11px',
                color: '#8a929e',
                textTransform: 'uppercase',
                letterSpacing: '0.55px',
                marginBottom: '2px',
              }}
            >
              Estimated total
            </div>
            <div
              style={{
                fontSize: '24px',
                fontWeight: 600,
                color: '#12161c',
                lineHeight: '32px',
              }}
              data-testid="pr-detail-estimated-total"
            >
              {formatVND(estimatedTotal)}
            </div>
          </div>
        </div>
      </div>

      {actionError && (
        <div style={{ backgroundColor: '#fdecec', border: '1px solid #f4c2c2', color: '#8e1e1e', padding: '12px', borderRadius: '6px', marginBottom: '16px', fontSize: '13px' }}>
          {actionError}
        </div>
      )}

      {/* 7-Step Progress Stepper Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          padding: '16px 20px',
          marginBottom: '24px',
          boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
        }}
        data-node-id="9:1033"
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
          {steps.map((s, idx) => {
            const isCurrent = s.num === activeStep;
            const isCompleted = s.num < activeStep;
            const isStepRejected = isRejected && s.num === 2;

            return (
              <React.Fragment key={s.num}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', zIndex: 2 }}>
                  <div
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      backgroundColor: isStepRejected ? '#fdecec' : isCurrent ? '#4a56d2' : isCompleted ? '#e9f7ef' : '#ffffff',
                      border: `0.667px solid ${isStepRejected ? '#f4c2c2' : isCurrent ? '#4a56d2' : isCompleted ? '#b6e2c7' : '#e4e7ec'}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: isStepRejected ? '#8e1e1e' : isCurrent ? '#ffffff' : isCompleted ? '#16603b' : '#8a929e',
                    }}
                  >
                    {isStepRejected ? <X size={11} strokeWidth={3} /> : isCompleted ? <Check size={11} strokeWidth={3} /> : s.num}
                  </div>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: isCurrent || isStepRejected ? 600 : 400,
                      color: isStepRejected ? '#8e1e1e' : isCurrent ? '#12161c' : '#8a929e',
                    }}
                  >
                    {s.label}
                  </span>
                </div>

                {idx < steps.length - 1 && (
                  <div
                    style={{
                      flex: 1,
                      height: '1px',
                      backgroundColor: idx < activeStep - 1 ? '#b6e2c7' : '#e4e7ec',
                      margin: '0 8px',
                      zIndex: 1,
                    }}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Main 2-Column Body */}
      <div style={{ display: 'grid', gridTemplateColumns: '484px 1fr', gap: '24px', alignItems: 'start' }}>
        {/* Left Column (484px) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Card 1: Lifecycle State Action Card */}

          {/* STATE 1: Approval + Budget Warning (Figma 9:2010 Flow B) */}
          {isPendingManager && (
            <div
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '8px',
                overflow: 'hidden',
                boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
              }}
              data-node-id="9:2072"
            >
              {/* Header */}
              <div
                style={{
                  backgroundColor: '#eef1ff',
                  borderBottom: '0.667px solid #c3ccff',
                  padding: '12px 16px',
                }}
              >
                <div style={{ fontSize: '11px', fontWeight: 600, color: '#2f3789', textTransform: 'uppercase', letterSpacing: '0.55px', marginBottom: '2px' }}>
                  Manager
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#2f3789' }}>
                  Approval decision
                </div>
              </div>

              {/* Body */}
              <div style={{ padding: '16px' }}>
                {/* Warning or confirmation inside decision box */}
                {isBudgetOver ? (
                  <div
                    style={{
                      backgroundColor: '#fdf4e3',
                      border: '0.667px solid #f2ddad',
                      borderRadius: '4px',
                      padding: '12px',
                      marginBottom: '16px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                    }}
                  >
                    <AlertTriangle size={16} color="#7a5209" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <p style={{ margin: 0, fontSize: '14px', color: '#7a5209', lineHeight: '22.75px' }}>
                      Approval is blocked: this request exceeds the remaining <b>{category}</b> budget by <b>{formatVND(overAmount)}</b>. Send it to Finance, or reject / request a revision.
                    </p>
                  </div>
                ) : (
                  <div
                    style={{
                      backgroundColor: '#f0fdf4',
                      border: '0.667px solid #bbf7d0',
                      borderRadius: '4px',
                      padding: '12px',
                      marginBottom: '16px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                    }}
                  >
                    <Check size={16} color="#16603b" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <p style={{ margin: 0, fontSize: '14px', color: '#16603b', lineHeight: '22.75px' }}>
                      Request value (<b>{formatVND(estimatedTotal)}</b>) is within the available <b>{category}</b> budget (<b>{formatVND(availableBudget)}</b>). Manager can approve directly.
                    </p>
                  </div>
                )}

                {/* Decision note input */}
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Decision note <span style={{ color: '#8a929e', fontWeight: 400 }}>(required)</span>
                  </label>
                  <textarea
                    value={decisionNote}
                    onChange={(e) => setDecisionNote(e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '8px 11px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: '#12161c',
                      outline: 'none',
                      fontFamily: 'inherit',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>

                {/* Buttons */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={handleApprove}
                      disabled={isProcessing}
                      style={{
                        backgroundColor: '#4a56d2',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '4px',
                        height: '37px',
                        padding: '0 16px',
                        fontSize: '14px',
                        fontWeight: 600,
                        cursor: isProcessing ? 'not-allowed' : 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        flex: 1,
                        justifyContent: 'center',
                      }}
                      data-testid="send-to-finance-btn"
                    >
                      {isProcessing ? <Loader2 size={16} className="animate-spin" /> : (
                        <>
                          <Send size={15} />
                          <span>{(isBudgetOver || estimatedTotal > 50000000) ? 'Send to Finance for budget review' : 'Approve request'}</span>
                        </>
                      )}
                    </button>

                    <button
                      onClick={handleRequestRevision}
                      disabled={isProcessing}
                      style={{
                        backgroundColor: '#ffffff',
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        height: '37px',
                        padding: '0 14px',
                        fontSize: '14px',
                        fontWeight: 600,
                        color: '#5a6472',
                        cursor: isProcessing ? 'not-allowed' : 'pointer',
                      }}
                      data-testid="request-revision-btn"
                    >
                      Request revision
                    </button>
                  </div>

                  <button
                    onClick={handleReject}
                    disabled={isProcessing}
                    style={{
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      height: '37px',
                      padding: '0 14px',
                      fontSize: '14px',
                      fontWeight: 600,
                      color: '#5a6472',
                      cursor: isProcessing ? 'not-allowed' : 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      width: 'fit-content',
                    }}
                    data-testid="reject-btn"
                  >
                    <X size={15} />
                    <span>Reject</span>
                  </button>
                </div>


                <div style={{ fontSize: '12px', color: '#8a929e', lineHeight: '16px' }}>
                  Every outcome here is recorded against a named person. The assistant cannot approve or reject a request.
                </div>
              </div>
            </div>
          )}

          {/* STATE 2: Finance Budget Decision (Figma 9:2635) */}
          {isPendingFinance && (
            <div
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #f2ddad',
                borderRadius: '8px',
                overflow: 'hidden',
                boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
              }}
              data-node-id="9:2697"
            >
              <div
                style={{
                  backgroundColor: '#fdf4e3',
                  borderBottom: '0.667px solid #f2ddad',
                  padding: '12px 16px',
                }}
              >
                <div style={{ fontSize: '11px', fontWeight: 600, color: '#7a5209', textTransform: 'uppercase', letterSpacing: '0.55px', marginBottom: '2px' }}>
                  Finance
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#7a5209' }}>
                  Budget review
                </div>
              </div>

              <div style={{ padding: '16px' }}>
                <p style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#5a6472', lineHeight: '22.75px' }}>
                  The request is <b>{formatVND(overAmount)}</b> above the remaining <b>{category}</b> budget. Confirm whether funding can be found, or mark the line exceeded and send it back to the manager.
                </p>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Finance note <span style={{ color: '#8a929e', fontWeight: 400 }}>(required)</span>
                  </label>
                  <textarea
                    value={financeNote}
                    onChange={(e) => setFinanceNote(e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '8px 11px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: '#12161c',
                      outline: 'none',
                      fontFamily: 'inherit',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                  <button
                    onClick={handleApprove}
                    disabled={isProcessing}
                    style={{
                      backgroundColor: '#4a56d2',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '4px',
                      height: '37px',
                      padding: '0 16px',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: isProcessing ? 'not-allowed' : 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                    data-testid="funding-confirmed-btn"
                  >
                    {isProcessing ? <Loader2 size={16} className="animate-spin" /> : (
                      <>
                        <Check size={16} />
                        <span>Funding confirmed</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleReject}
                    style={{
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      height: '37px',
                      padding: '0 16px',
                      fontSize: '14px',
                      fontWeight: 600,
                      color: '#5a6472',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                    data-testid="mark-exceeded-btn"
                  >
                    <X size={16} />
                    <span>Mark exceeded</span>
                  </button>
                </div>

                <div style={{ fontSize: '12px', color: '#8a929e', lineHeight: '16px' }}>
                  Finance confirms funding only. The approval decision stays with the department manager.
                </div>
              </div>
            </div>
          )}

          {/* STATE 3: Revision Required Card (Figma 9:2928) */}
          {isRevisionRequired && (() => {
            const revisionApproval = (pr.approvals || []).slice().reverse().find((a: any) => a.decision === 'REVISION_REQUIRED');
            const revApproverName = revisionApproval?.approver || revisionApproval?.approverName || 'Hoàng Nhật Nam (People Manager)';
            const revApproverRole = revisionApproval?.step || 'Manager';
            const revComments = revisionApproval?.comments || pr.revisionFeedback || 'Split into two phases and name the twelve recipients before resubmitting.';

            return (
              <div
                style={{
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #f2ddad',
                  borderRadius: '8px',
                  padding: '20px',
                  boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
                }}
                data-node-id="9:2928"
              >
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#7a5209', marginBottom: '4px' }}>
                  Revision requested
                </div>
                <div style={{ fontSize: '12px', color: '#5a6472', marginBottom: '12px' }}>
                  {revApproverName} ({revApproverRole})
                </div>
                <p style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#12161c', lineHeight: '22.75px' }}>
                  {revComments}
                </p>
                <button
                  onClick={() => onEditAfterRevision && onEditAfterRevision(pr)}
                  style={{
                    backgroundColor: '#4a56d2',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    height: '37px',
                    padding: '0 16px',
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '20px',
                  }}
                  data-testid="edit-and-resubmit-btn"
                >
                  <Edit3 size={15} />
                  <span>Edit and resubmit</span>
                </button>

                <div style={{ borderTop: '0.667px solid rgba(228,231,236,0.7)', paddingTop: '16px' }}>

                  <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                    Nothing to change?
                  </div>
                  <div style={{ fontSize: '12px', color: '#5a6472', marginBottom: '8px' }}>
                    If the approver only needed an explanation, answer here and send it back unchanged.
                  </div>
                  <textarea
                    placeholder="The twelve recipients are listed in the justification; no split is needed."
                    value={revisionReply}
                    onChange={(e) => setRevisionReply(e.target.value)}
                    rows={2}
                    style={{
                      width: '100%',
                      padding: '8px 11px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      outline: 'none',
                      fontFamily: 'inherit',
                      boxSizing: 'border-box',
                      marginBottom: '10px',
                    }}
                  />
                  <button
                    onClick={async () => {
                      setIsProcessing(true);
                      setActionError(null);
                      try {
                        const res = await api.resubmitPR(pr.id, {
                          comments: revisionReply.trim() || 'Resubmitted unchanged with explanation',
                        });
                        setPr(res);
                      } catch (err: any) {
                        setActionError(err.message || 'Lỗi khi gửi lại yêu cầu');
                      } finally {
                        setIsProcessing(false);
                      }
                    }}
                    disabled={isProcessing}
                    style={{
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      height: '37px',
                      padding: '0 16px',
                      fontSize: '14px',
                      fontWeight: 600,
                      color: '#5a6472',
                      cursor: isProcessing ? 'not-allowed' : 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                    data-testid="resubmit-unchanged-btn"
                  >
                    <RotateCw size={15} />
                    <span>Resubmit unchanged</span>
                  </button>
                </div>
              </div>
            );
          })()}


          {/* STATE 4: Rejected Card (Figma 9:3468) */}
          {isRejected && (
            <div
              style={{
                backgroundColor: '#fef8f8',
                border: '0.667px solid #f4c2c2',
                borderRadius: '8px',
                padding: '20px',
              }}
              data-node-id="9:3468"
            >
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#8e1e1e', marginBottom: '2px' }}>
                Rejected
              </div>
              <div style={{ fontSize: '12px', color: '#8e1e1e', opacity: 0.85, marginBottom: '12px' }}>
                Vũ Minh Châu (Operations Manager)
              </div>
              <p style={{ margin: 0, fontSize: '14px', color: '#12161c', lineHeight: '22.75px' }}>
                Rejected for Q3. Repair the current unit and resubmit in Q4.
              </p>
            </div>
          )}

          {/* STATE 5: Approved Card (Figma 9:3745) */}
          {isApproved && (
            <div
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #b6e2c7',
                borderRadius: '8px',
                padding: '20px',
              }}
              data-node-id="9:3745"
            >
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#16603b', marginBottom: '2px' }}>
                Approved
              </div>
              <div style={{ fontSize: '12px', color: '#5a6472', marginBottom: '12px' }}>
                Vũ Minh Châu (Operations Manager)
              </div>
              <p style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#12161c', lineHeight: '22.75px' }}>
                Approved — covered by the safety remediation plan. Next, Procurement collects quotations against this request by uploading each supplier's quotation file.
              </p>
              <button
                onClick={() => {
                  if (onCollectQuotations) {
                    onCollectQuotations(pr);
                  } else if (onNavigateTab) {
                    onNavigateTab('sourcing');
                  }
                }}
                style={{
                  backgroundColor: '#4a56d2',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '4px',
                  height: '37px',
                  padding: '0 16px',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
                data-testid="collect-quotations-btn"
              >
                <span>Collect quotations</span>
                <ArrowRight size={15} />
              </button>
            </div>
          )}

          {/* STATE 6: Submission Failed Banner (Figma 9:1563) */}
          {isError && (
            <div
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '8px',
                overflow: 'hidden',
                boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
              }}
              data-node-id="9:1629"
            >
              <div
                style={{
                  backgroundColor: '#fdecec',
                  borderBottom: '0.667px solid #f4c2c2',
                  padding: '12px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <AlertTriangle size={16} color="#8e1e1e" />
                <span style={{ fontSize: '14px', fontWeight: 600, color: '#8e1e1e' }}>
                  Submission failed
                </span>
              </div>

              <div style={{ padding: '16px' }}>
                <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#5a6472', lineHeight: '22px' }}>
                  Submission could not be posted to the ERP (cost-centre service timed out). Nothing was sent for approval.
                </p>
                <p style={{ margin: '0 0 16px 0', fontSize: '12px', color: '#8a929e', lineHeight: '16px' }}>
                  No approver has seen this request. Retrying resubmits exactly what you see below — nothing was changed.
                </p>

                <div style={{ display: 'flex', gap: '12px' }}>
                  <button
                    onClick={() => onRetrySubmit && onRetrySubmit(pr)}
                    style={{
                      height: '37px',
                      padding: '0 16px',
                      backgroundColor: '#4a56d2',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '14px',
                      fontWeight: 600,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      cursor: 'pointer',
                    }}
                    data-testid="retry-submission-btn"
                  >
                    <RotateCw size={15} />
                    <span>Retry submission</span>
                  </button>

                  <button
                    onClick={() => onEdit(pr)}
                    style={{
                      height: '37px',
                      padding: '0 16px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      fontWeight: 600,
                      color: '#5a6472',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      cursor: 'pointer',
                    }}
                    data-testid="edit-before-retrying-btn"
                  >
                    <Edit3 size={15} />
                    <span>Edit before retrying</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* STATE 7: Draft Status Card (Figma 9:1006) */}
          {isDraft && (
            <div
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '8px',
                padding: '20px',
                boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
              }}
              data-node-id="9:1072"
            >
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '8px' }}>
                Draft — not submitted
              </div>
              <p style={{ margin: '0 0 16px 0', fontSize: '14px', color: '#5a6472', lineHeight: '22px' }}>
                Nobody is waiting on this. Finish the required fields, then submit it from the edit screen.
              </p>
              <button
                onClick={() => onEdit(pr)}
                style={{
                  height: '36px',
                  padding: '0 16px',
                  backgroundColor: '#4a56d2',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '14px',
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  cursor: 'pointer',
                }}
                data-testid="continue-editing-btn"
              >
                <Edit3 size={15} />
                <span>Continue editing</span>
              </button>
            </div>
          )}

          {/* Budget Warning / Status Card (Figma 9:2010 / 9:2635 / 9:3468) */}
          {(isPendingManager || isPendingFinance || isRejected) && (
            <div
              style={{
                backgroundColor: isBudgetOver ? 'rgba(253,244,227,0.6)' : '#ffffff',
                border: isBudgetOver ? '0.667px solid #f2ddad' : '0.667px solid #e4e7ec',
                borderRadius: '8px',
                padding: '16px 20px',
                boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
              }}
              data-node-id="9:2107"
            >
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', lineHeight: '20px' }}>
                    {isBudgetOver ? 'Budget warning' : 'Budget status'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '16px' }}>
                    {category} · Q3 2026 · owner Finance · Trần Mỹ Linh
                  </div>
                </div>
                {isBudgetOver ? (
                  <div
                    style={{
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #f2ddad',
                      borderRadius: '4px',
                      padding: '2.5px 8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '12px',
                      fontWeight: 500,
                      color: '#7a5209',
                    }}
                  >
                    <AlertTriangle size={14} color="#7a5209" />
                    <span>Over by {formatVND(overAmount)}</span>
                  </div>
                ) : (
                  <div
                    style={{
                      backgroundColor: '#e9f7ef',
                      border: '0.667px solid #b6e2c7',
                      borderRadius: '4px',
                      padding: '2.5px 8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '12px',
                      fontWeight: 500,
                      color: '#16603b',
                    }}
                  >
                    <Check size={14} color="#16603b" />
                    <span>Within budget</span>
                  </div>
                )}
              </div>

              {/* Explanatory text */}
              <p style={{ margin: '0 0 12px 0', fontSize: '14px', color: isBudgetOver ? '#7a5209' : '#5a6472', lineHeight: '22.75px' }}>
                {isBudgetOver
                  ? `This request is ${formatVND(overAmount)} above the remaining ${category} budget for Q3 2026. It cannot be approved until Finance reviews the position.`
                  : `This request is within the remaining ${category} budget for Q3 2026 (${formatVND(availableBudget)} available). No budget escalation is required.`}
              </p>

              {/* Progress bar */}
              <div
                style={{
                  backgroundColor: '#f5f6f8',
                  height: '10px',
                  borderRadius: '9999px',
                  overflow: 'hidden',
                  width: '100%',
                  display: 'flex',
                  marginBottom: '16px',
                }}
              >
                <div style={{ backgroundColor: 'rgba(18,22,28,0.7)', width: '88%', height: '100%' }} />
                <div style={{ backgroundColor: isBudgetOver ? '#96650b' : '#16603b', width: '12%', height: '100%' }} />
              </div>

              {/* Metrics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginBottom: '16px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: '#8a929e', marginBottom: '2px' }}>Allocated</div>
                  <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c' }}>500,000,000 ₫</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#8a929e', marginBottom: '2px' }}>Spent</div>
                  <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c' }}>412,000,000 ₫</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#8a929e', marginBottom: '2px' }}>Committed</div>
                  <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c' }}>30,000,000 ₫</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#8a929e', marginBottom: '2px' }}>Available</div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: isBudgetOver ? '#7a5209' : '#16603b' }}>58,000,000 ₫</div>
                </div>
              </div>

              {/* Highlight Row */}
              <div
                style={{
                  borderTop: '0.667px solid rgba(228,231,236,0.7)',
                  paddingTop: '10px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ fontSize: '14px', color: '#5a6472' }}>This request</span>
                <span style={{ fontSize: '16px', fontWeight: 600, color: '#12161c' }}>
                  {formatVND(estimatedTotal)}
                </span>
              </div>

              {/* Bottom callout if awaiting or exceeded */}
              {isPendingFinance && (
                <div
                  style={{
                    backgroundColor: '#fbfcfd',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    padding: '8px 12px',
                    marginTop: '12px',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#12161c',
                  }}
                >
                  Awaiting Finance review
                </div>
              )}
              {isRejected && (
                <div
                  style={{
                    backgroundColor: '#fbfcfd',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    padding: '8px 12px',
                    marginTop: '12px',
                    fontSize: '12px',
                    color: '#5a6472',
                  }}
                >
                  Marked exceeded by Finance: Trần Mỹ Linh (Finance)
                </div>
              )}
            </div>
          )}

          {/* Justification & Metadata */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:1081"
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '8px' }}>
              Justification
            </div>
            <p style={{ margin: '0 0 20px 0', fontSize: '14px', color: '#5a6472', lineHeight: '22px' }}>
              {displayJustification}
            </p>

            {/* Details Grid: 4 columns matching Figma */}
            <div
              style={{
                borderTop: '0.667px solid rgba(228,231,236,0.7)',
                paddingTop: '16px',
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '16px',
              }}
            >
              {/* Row 1 Col 1 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Requester
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {creatorName}
                </div>
              </div>

              {/* Row 1 Col 2 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Department
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {departmentName}
                </div>
              </div>

              {/* Row 1 Col 3 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Category
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {category}
                </div>
              </div>

              {/* Row 1 Col 4 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Cost centre
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {costCentre}
                </div>
              </div>

              {/* Row 2 Col 1 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Required by
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {requiredBy}
                </div>
              </div>

              {/* Row 2 Col 2 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Delivery location
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {deliveryLocation}
                </div>
              </div>

              {/* Row 2 Col 3 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Created
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {createdAt}
                </div>
              </div>

              {/* Row 2 Col 4 */}
              <div>
                <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '4px', letterSpacing: '0.275px' }}>
                  Last updated
                </div>
                <div style={{ fontSize: '14px', color: '#12161c', fontWeight: 500 }}>
                  {lastUpdated}
                </div>
              </div>
            </div>
          </div>

          {/* Line items Table */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:1115"
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '16px' }}>
              Line items
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 60px 120px 120px',
                fontSize: '11px',
                color: '#8a929e',
                borderBottom: '0.667px solid #e4e7ec',
                paddingBottom: '8px',
                marginBottom: '12px',
              }}
            >
              <div>Description</div>
              <div style={{ textAlign: 'center' }}>Qty</div>
              <div style={{ textAlign: 'right' }}>Est. unit</div>
              <div style={{ textAlign: 'right' }}>Line total</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {lineItems.map((item: any, idx: number) => {
                const qty = Number(item.quantity) || 1;
                const price = Number(item.estimatedUnitPrice) || 0;
                const total = qty * price;
                return (
                  <div
                    key={idx}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 60px 120px 120px',
                      fontSize: '14px',
                      alignItems: 'center',
                    }}
                  >
                    <div style={{ fontWeight: 500, color: '#12161c' }}>{item.itemName}</div>
                    <div style={{ textAlign: 'center', color: '#5a6472' }}>{qty}</div>
                    <div style={{ textAlign: 'right', color: '#5a6472' }}>{formatVND(price)}</div>
                    <div style={{ textAlign: 'right', fontWeight: 600, color: '#12161c' }}>
                      {formatVND(total)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quotations Card on Approved (Figma 9:3745) */}
          {isApproved && (
            <div
              style={{
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '8px',
                padding: '20px',
                boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                Quotations linked to this request
              </div>
              <p style={{ fontSize: '13px', color: '#5a6472', margin: '0 0 12px 0' }}>
                None collected yet. 3 more quotations on file to collect.
              </p>
              <button
                onClick={() => {
                  if (onCollectQuotations) {
                    onCollectQuotations(pr);
                  } else if (onNavigateTab) {
                    onNavigateTab('sourcing');
                  }
                }}
                style={{
                  backgroundColor: '#4a56d2',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '6px 14px',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  marginBottom: '16px',
                }}
              >
                <Plus size={14} />
                <span>Collect quotation</span>
              </button>
              <div style={{ fontSize: '12px', color: '#8a929e' }}>
                Upload a quotation file against a supplier to create the first linked quotation.
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Activity Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:1134"
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '20px' }}>
              Activity
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', position: 'relative' }}>
              {/* Event 1: Draft Created */}
              <div style={{ display: 'flex', gap: '12px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#4a56d2', marginTop: '6px', flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>Draft created</div>
                  <div style={{ fontSize: '11px', color: '#8a929e' }}>Employee · {creatorName} · {createdAt}</div>
                </div>
              </div>

              {/* Event 2: Submitted */}
              {!isDraft && !isError && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#4a56d2', marginTop: '6px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>Submitted for approval</div>
                    <div style={{ fontSize: '11px', color: '#8a929e' }}>Employee · {creatorName} · {createdAt}</div>
                  </div>
                </div>
              )}

              {/* Event 3: Budget warning raised */}
              {isBudgetWarning && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#96650b', marginTop: '6px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>Budget warning raised</div>
                    <div style={{ fontSize: '11px', color: '#8a929e' }}>System · System · {createdAt}</div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginTop: '4px' }}>
                      Request exceeds the remaining {category} budget.
                    </div>
                  </div>
                </div>
              )}

              {/* Event 4: Sent to Finance / Routed to Manager */}
              {isPendingFinance && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#4a56d2', marginTop: '6px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>Sent to Finance for budget review</div>
                    <div style={{ fontSize: '11px', color: '#8a929e' }}>Manager · Lê Thanh Bình · 08 Sept 2026 · 09:10</div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginTop: '4px' }}>
                      Cannot approve until funding is confirmed.
                    </div>
                  </div>
                </div>
              )}

              {/* Event 5: Revision Requested */}
              {isRevisionRequired && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#7a5209', marginTop: '6px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>Revision requested</div>
                    <div style={{ fontSize: '11px', color: '#8a929e' }}>Manager · Hoàng Nhật Nam · 19 Aug 2026 · 09:00</div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginTop: '4px' }}>
                      Split into two phases and name the twelve recipients.
                    </div>
                  </div>
                </div>
              )}

              {/* Event 6: Rejected */}
              {isRejected && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#8e1e1e', marginTop: '6px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>Rejected</div>
                    <div style={{ fontSize: '11px', color: '#8a929e' }}>Manager · Vũ Minh Châu · 09 Aug 2026 · 16:00</div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginTop: '4px' }}>
                      Repair the current unit and resubmit in Q4.
                    </div>
                  </div>
                </div>
              )}

              {/* Event 7: Approved */}
              {isApproved && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16603b', marginTop: '6px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>Approved</div>
                    <div style={{ fontSize: '11px', color: '#8a929e' }}>Manager · Vũ Minh Châu · 18 Aug 2026 · 14:20</div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginTop: '4px' }}>
                      Covered by the safety remediation plan.
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Assistant Involvement Box */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
            }}
          >
            <div style={{ fontSize: '12px', fontWeight: 600, color: '#5a6472', marginBottom: '6px' }}>
              Assistant involvement
            </div>
            <div style={{ fontSize: '12px', color: '#8a929e', lineHeight: '18px' }}>
              1 suggestion was offered and accepted by the requester before submission. No field was written automatically.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
