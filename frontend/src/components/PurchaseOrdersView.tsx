import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  ChevronRight, 
  FileText, 
  Building2, 
  Package, 
  CheckCircle2, 
  Clock, 
  Loader2,
  RefreshCw,
  AlertCircle,
  Check,
  CheckCircle
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface PurchaseOrdersViewProps {
  user: AuthenticatedUser | null;
  onNavigateTab?: (tab: string) => void;
  onSelectPO?: (po: any) => void;
}

export const PurchaseOrdersView: React.FC<PurchaseOrdersViewProps> = ({
  user,
  onNavigateTab,
}) => {
  const [pos, setPos] = useState<any[]>([]);
  const [selectedPO, setSelectedPO] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  // Receiving Form State
  const [deliveryCondition, setDeliveryCondition] = useState<'full' | 'part'>('full');
  const [partialQty, setPartialQty] = useState<number>(1);
  const [receiptNote, setReceiptNote] = useState<string>('All items delivered and verified at goods-in.');

  useEffect(() => {
    loadPOs();
  }, []);

  const loadPOs = async (keepSelectedId?: string | null) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listPOs();
      const loaded = Array.isArray(data) ? data : [];
      setPos(loaded);
      if (keepSelectedId === null) {
        setSelectedPO(null);
      } else if (keepSelectedId) {
        const found = loaded.find((p) => p.id === keepSelectedId || p.poNumber === keepSelectedId);
        if (found) setSelectedPO(found);
      } else {
        setSelectedPO((prev: any) => {
          if (!prev) return null;
          return loaded.find((p) => p.id === prev.id || p.poNumber === prev.poNumber) || null;
        });
      }
    } catch (err: any) {
      console.error('Failed to load POs:', err);
      setError(err.message || 'Không thể tải danh sách Purchase Orders');
    } finally {
      setLoading(false);
    }
  };

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

  const showToast = (type: 'success' | 'error' | 'info', text: string) => {
    setToastMessage({ type, text });
    setTimeout(() => setToastMessage(null), 5000);
  };

  // Group POs into the 3 Figma 9:6424 categories
  const issuedPOs = pos.filter((p) => (p.status === 'SENT' || p.status === 'PO_CREATED' || p.status === 'ISSUED') && (p.totalReceived || 0) < p.quantity && p.prStatus !== 'CLOSED');
  const receivedPOs = pos.filter((p) => (p.status === 'RECEIVED' || (p.totalReceived || 0) >= p.quantity) && p.prStatus !== 'CLOSED' && p.status !== 'CLOSED');
  const closedPOs = pos.filter((p) => p.status === 'CLOSED' || p.prStatus === 'CLOSED');

  // Handle Receiving Goods
  const handleRecordReceipt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPO) return;

    const remaining = selectedPO.remainingQty ?? (selectedPO.quantity - (selectedPO.totalReceived || 0));
    const qtyToReceive = deliveryCondition === 'full' ? remaining : Number(partialQty);

    if (qtyToReceive <= 0) {
      showToast('error', 'Số lượng nhận hàng phải lớn hơn 0');
      return;
    }
    if (qtyToReceive > remaining) {
      showToast('error', `Số lượng nhận (${qtyToReceive}) không được vượt quá số lượng còn lại (${remaining})`);
      return;
    }

    setActionLoading(true);
    try {
      const res = await api.receiveGoods({
        purchaseOrderId: selectedPO.id,
        receivedQty: qtyToReceive,
        receivedItems: receiptNote || `Nhận ${qtyToReceive} sản phẩm bàn giao`,
      });
      showToast('success', `Đã ghi nhận nhận hàng thành công: ${qtyToReceive} sản phẩm.`);
      await loadPOs(selectedPO.id);
    } catch (err: any) {
      console.error('Receive goods failed:', err);
      showToast('error', err.message || 'Ghi nhận nhận hàng thất bại');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Close PR
  const handleClosePO = async () => {
    if (!selectedPO) return;
    setActionLoading(true);
    try {
      const prId = selectedPO.purchaseRequestId || selectedPO.prId;
      await api.closePR(prId);
      showToast('success', `Đã đóng Purchase Request ${prId} thành công (HD-07).`);
      await loadPOs(selectedPO.id);
    } catch (err: any) {
      console.error('Close PR failed:', err);
      showToast('error', err.message || 'Không thể đóng Purchase Request');
    } finally {
      setActionLoading(false);
    }
  };

  // =========================================================================
  // VIEW 2: PO DETAIL / RECEIVING VIEW (FIGMA 9:6580 & 9:6793)
  // =========================================================================
  if (selectedPO) {
    const isClosed = selectedPO.status === 'CLOSED' || selectedPO.prStatus === 'CLOSED';
    const isFullyReceived = (selectedPO.totalReceived || 0) >= selectedPO.quantity || selectedPO.status === 'RECEIVED';
    const remaining = Math.max(0, selectedPO.quantity - (selectedPO.totalReceived || 0));

    return (
      <div 
        className="po-detail-view"
        data-node-id={isClosed ? '9:6793' : '9:6580'}
        data-testid="po-detail-view"
        style={{
          maxWidth: '876px',
          margin: '0 auto',
          padding: '24px 16px',
          fontFamily: 'Inter, sans-serif'
        }}
      >
        {/* Toast Alert */}
        {toastMessage && (
          <div 
            style={{
              position: 'fixed',
              bottom: '24px',
              right: '24px',
              zIndex: 9999,
              backgroundColor: toastMessage.type === 'success' ? '#12161c' : '#7f1d1d',
              color: '#ffffff',
              padding: '12px 18px',
              borderRadius: '6px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '13px',
              maxWidth: '420px',
            }}
          >
            {toastMessage.type === 'success' ? <CheckCircle size={16} color="#4ade80" /> : <AlertCircle size={16} color="#f87171" />}
            <span>{toastMessage.text}</span>
          </div>
        )}

        {/* Back Link */}
        <div style={{ marginBottom: '16px' }}>
          <button
            data-testid="back-to-pos-btn"
            onClick={() => {
              setSelectedPO(null);
              loadPOs(null);
            }}
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              fontSize: '13px',
              fontWeight: 500,
              color: '#5a6472',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <ArrowLeft size={14} />
            <span>Purchase orders</span>
          </button>
        </div>

        {/* Header (Figma 9:6580 / 9:6793) */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span 
                data-testid={isClosed ? 'po-detail-closed-badge' : isFullyReceived ? 'po-detail-received-badge' : 'po-detail-issued-badge'}
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  backgroundColor: isClosed ? '#f1f5f9' : isFullyReceived ? '#f0fdf4' : '#eef2ff',
                  color: isClosed ? '#475569' : isFullyReceived ? '#166534' : '#3b45ad',
                  border: `0.667px solid ${isClosed ? '#cbd5e1' : isFullyReceived ? '#bbf7d0' : '#c7d2fe'}`,
                  padding: '2px 8px',
                  borderRadius: '4px',
                }}
              >
                {isClosed ? 'Closed' : isFullyReceived ? 'Received' : 'PO issued'}
              </span>
              <span data-testid="po-detail-number" style={{ fontSize: '13px', color: '#8a929e', fontFamily: 'monospace' }}>
                {selectedPO.poNumber || selectedPO.id}
              </span>
            </div>

            <h1 
              data-testid="po-detail-title"
              style={{
                fontSize: '24px',
                fontWeight: 600,
                color: '#12161c',
                margin: '0 0 6px 0',
                letterSpacing: '-0.5px'
              }}
            >
              {selectedPO.prTitle || 'Purchase Request'} ({selectedPO.quantity} units)
            </h1>

            <div style={{ fontSize: '13px', color: '#5a6472' }}>
              Raised from {selectedPO.purchaseRequestId || selectedPO.prId}
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '11px', color: '#8a929e', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>
              Order value
            </div>
            <div 
              data-testid="po-detail-amount"
              style={{
                fontSize: '24px',
                fontWeight: 700,
                color: '#12161c',
                fontVariantNumeric: 'tabular-nums'
              }}
            >
              {formatVND(selectedPO.totalAmount)}
            </div>
          </div>
        </div>

        {/* 7-Step Progress Stepper (Figma 9:6580 & 9:6793) */}
        <div 
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '8px',
            padding: '14px 20px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px'
          }}
        >
          {/* Step 1: Request */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, color: '#166534' }}>
            <div style={{ width: '18px', height: '18px', borderRadius: '50%', backgroundColor: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Check size={12} color="#166534" />
            </div>
            <span>Request</span>
          </div>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />

          {/* Step 2: Approval */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, color: '#166534' }}>
            <div style={{ width: '18px', height: '18px', borderRadius: '50%', backgroundColor: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Check size={12} color="#166534" />
            </div>
            <span>Approval</span>
          </div>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />

          {/* Step 3: Quotations */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, color: '#166534' }}>
            <div style={{ width: '18px', height: '18px', borderRadius: '50%', backgroundColor: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Check size={12} color="#166534" />
            </div>
            <span>Quotations</span>
          </div>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />

          {/* Step 4: Comparison */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, color: '#166534' }}>
            <div style={{ width: '18px', height: '18px', borderRadius: '50%', backgroundColor: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Check size={12} color="#166534" />
            </div>
            <span>Comparison</span>
          </div>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />

          {/* Step 5: Purchase order */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, color: isClosed || isFullyReceived ? '#166534' : '#3b45ad' }}>
            <div style={{ 
              width: '18px', 
              height: '18px', 
              borderRadius: '50%', 
              backgroundColor: isClosed || isFullyReceived ? '#dcfce7' : '#3b45ad', 
              color: '#ffffff',
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontSize: '11px',
              fontWeight: 600
            }}>
              {isClosed || isFullyReceived ? <Check size={12} color="#166534" /> : '5'}
            </div>
            <span>Purchase order</span>
          </div>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />

          {/* Step 6: Received */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, color: isClosed ? '#166534' : isFullyReceived ? '#3b45ad' : '#8a929e' }}>
            <div style={{ 
              width: '18px', 
              height: '18px', 
              borderRadius: '50%', 
              backgroundColor: isClosed ? '#dcfce7' : isFullyReceived ? '#3b45ad' : '#f1f5f9', 
              color: isClosed ? '#166534' : isFullyReceived ? '#ffffff' : '#8a929e',
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontSize: '11px',
              fontWeight: 600
            }}>
              {isClosed ? <Check size={12} color="#166534" /> : '6'}
            </div>
            <span>Received</span>
          </div>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />

          {/* Step 7: Closed */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, color: isClosed ? '#166534' : '#8a929e' }}>
            <div style={{ 
              width: '18px', 
              height: '18px', 
              borderRadius: '50%', 
              backgroundColor: isClosed ? '#dcfce7' : '#f1f5f9', 
              color: isClosed ? '#166534' : '#8a929e',
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontSize: '11px',
              fontWeight: 600
            }}>
              {isClosed ? <Check size={12} color="#166534" /> : '7'}
            </div>
            <span>Closed</span>
          </div>
        </div>

        {/* Section: Order Details (Figma 9:6580) */}
        <div 
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '20px',
          }}
        >
          <h2 style={{ margin: '0 0 16px 0', fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
            Order details
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>Supplier</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>{selectedPO.supplierName || 'Awarded Supplier'}</div>
            </div>
            <div>
              <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>Payment terms</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>Net 30</div>
            </div>
            <div>
              <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>From quotation</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c', fontFamily: 'monospace' }}>{selectedPO.quotationId}</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>Quantity ordered</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>{selectedPO.quantity} units</div>
            </div>
            <div>
              <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>Total received</div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: isFullyReceived ? '#166534' : '#3b45ad' }}>
                {selectedPO.totalReceived || 0} / {selectedPO.quantity} units
              </div>
            </div>
            <div>
              <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>Issued timestamp</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>
                {selectedPO.createdAt ? new Date(selectedPO.createdAt).toLocaleString('vi-VN') : 'Mới phát hành'}
              </div>
            </div>
          </div>

          <div style={{ borderTop: '0.667px solid #f1f5f9', paddingTop: '12px', fontSize: '12px', color: '#5a6472' }}>
            <span style={{ fontWeight: 600, color: '#12161c' }}>Why this supplier: </span>
            Authorised reseller, spec confirmed, and human award decision matched assistant recommendation.
          </div>
        </div>

        {/* Section: Goods Receiving Form (Figma 9:6580) - when not fully received and not closed */}
        {!isFullyReceived && !isClosed && (
          <div 
            data-testid="record-goods-section"
            style={{
              backgroundColor: '#f5f7ff',
              border: '0.667px solid #c7d2fe',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '20px',
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 600, color: '#4338ca', letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '4px' }}>
              Receiving
            </div>
            <h2 style={{ margin: '0 0 14px 0', fontSize: '16px', fontWeight: 600, color: '#12161c' }}>
              Record goods received
            </h2>

            <form onSubmit={handleRecordReceipt}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, color: '#12161c', marginBottom: '8px' }}>
                  Delivery condition
                </label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <label
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '10px 14px',
                      backgroundColor: deliveryCondition === 'full' ? '#ffffff' : 'rgba(255,255,255,0.6)',
                      border: `0.667px solid ${deliveryCondition === 'full' ? '#3b45ad' : '#c7d2fe'}`,
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '13px',
                    }}
                  >
                    <input 
                      type="radio"
                      name="deliveryCondition"
                      data-testid="condition-full-radio"
                      checked={deliveryCondition === 'full'}
                      onChange={() => setDeliveryCondition('full')}
                      style={{ accentColor: '#3b45ad' }}
                    />
                    <span>Received in full ({remaining} units)</span>
                  </label>

                  <label
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '10px 14px',
                      backgroundColor: deliveryCondition === 'part' ? '#ffffff' : 'rgba(255,255,255,0.6)',
                      border: `0.667px solid ${deliveryCondition === 'part' ? '#3b45ad' : '#c7d2fe'}`,
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '13px',
                    }}
                  >
                    <input 
                      type="radio"
                      name="deliveryCondition"
                      data-testid="condition-part-radio"
                      checked={deliveryCondition === 'part'}
                      onChange={() => setDeliveryCondition('part')}
                      style={{ accentColor: '#3b45ad' }}
                    />
                    <span>Received in part</span>
                  </label>
                </div>
              </div>

              {/* Partial Quantity Input */}
              {deliveryCondition === 'part' && (
                <div style={{ marginBottom: '14px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, color: '#12161c', marginBottom: '4px' }}>
                    Received quantity (units, max: {remaining})
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={remaining}
                    data-testid="received-qty-input"
                    value={partialQty}
                    onChange={(e) => setPartialQty(Math.max(1, Math.min(remaining, Number(e.target.value))))}
                    style={{
                      width: '180px',
                      height: '36px',
                      padding: '0 10px',
                      fontSize: '13px',
                      border: '0.667px solid #c7d2fe',
                      borderRadius: '4px',
                      backgroundColor: '#ffffff'
                    }}
                  />
                </div>
              )}

              {/* Receipt Note */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, color: '#12161c', marginBottom: '4px' }}>
                  Receipt note (required)
                </label>
                <textarea
                  data-testid="receipt-note-input"
                  rows={3}
                  value={receiptNote}
                  onChange={(e) => setReceiptNote(e.target.value)}
                  placeholder="All units delivered, serial numbers logged at goods-in."
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    fontSize: '13px',
                    border: '0.667px solid #c7d2fe',
                    borderRadius: '4px',
                    backgroundColor: '#ffffff',
                    fontFamily: 'inherit',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', color: '#5a6472', fontStyle: 'italic' }}>
                  Receiving is recorded at order level only. Inventory and invoice matching are out of scope.
                </span>

                <button
                  type="submit"
                  data-testid="submit-receipt-btn"
                  disabled={actionLoading}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 18px',
                    backgroundColor: actionLoading ? '#9ca3af' : '#3b45ad',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: actionLoading ? 'not-allowed' : 'pointer',
                  }}
                >
                  {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <Package size={14} />}
                  <span>Record receipt</span>
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Section: Received in full notice (Figma 9:6793) */}
        {isFullyReceived && (
          <div 
            data-testid="received-in-full-card"
            style={{
              backgroundColor: '#f0fdf4',
              border: '0.667px solid #bbf7d0',
              borderRadius: '8px',
              padding: '16px 20px',
              marginBottom: '20px',
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#166534', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle size={16} color="#166534" />
              <span>Received in full</span>
            </div>
            <div style={{ fontSize: '12px', color: '#15803d', marginBottom: '8px' }}>
              All {selectedPO.quantity} units received and confirmed against purchase order.
            </div>
            {selectedPO.receivings && selectedPO.receivings.length > 0 && (
              <div style={{ fontSize: '12px', color: '#166534', borderTop: '0.667px solid #dcfce7', paddingTop: '8px' }}>
                {selectedPO.receivings.map((r: any, idx: number) => (
                  <div key={r.id || idx} style={{ marginTop: '2px' }}>
                    • Đợt {idx + 1}: {r.receivedQty} sản phẩm — {r.receivedItems || 'Bàn giao hợp lệ'} ({r.receivedDate ? new Date(r.receivedDate).toLocaleDateString('vi-VN') : ''})
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Section: Close PR (HD-07) - when fully received but not closed */}
        {isFullyReceived && !isClosed && (
          <div 
            data-testid="close-po-section"
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 1px 2px rgba(18,22,28,0.03)'
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
              Finalization (HD-07)
            </div>
            <h2 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 600, color: '#12161c' }}>
              Close purchase order
            </h2>
            <p style={{ margin: '0 0 16px 0', fontSize: '13px', color: '#5a6472' }}>
              All goods have been delivered and verified against the purchase order. Close this request to finalize budget settlement and complete the business lifecycle.
            </p>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', color: '#8a929e', fontStyle: 'italic' }}>
                Requires role: Finance or Admin (HD-13 / RBAC)
              </span>

              <button
                data-testid="close-po-btn"
                onClick={handleClosePO}
                disabled={actionLoading}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 18px',
                  backgroundColor: actionLoading ? '#9ca3af' : '#12161c',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: actionLoading ? 'not-allowed' : 'pointer',
                }}
              >
                {actionLoading && <Loader2 size={14} className="animate-spin" />}
                <span>Close purchase order</span>
              </button>
            </div>
          </div>
        )}

        {/* Section: Order closed (Figma 9:6793) - when closed */}
        {isClosed && (
          <div 
            data-testid="order-closed-card"
            style={{
              backgroundColor: '#f8fafc',
              border: '0.667px solid #cbd5e1',
              borderRadius: '8px',
              padding: '16px 20px',
              marginBottom: '20px',
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#334155', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle size={16} color="#334155" />
              <span>Order closed</span>
            </div>
            <div style={{ fontSize: '12px', color: '#64748b' }}>
              Delivery complete and matched to the quotation. Budget settled in full. Nothing outstanding.
            </div>
          </div>
        )}
      </div>
    );
  }

  // =========================================================================
  // VIEW 1: PURCHASE ORDERS LIST VIEW (FIGMA 9:6424)
  // =========================================================================
  return (
    <div 
      className="purchase-orders-view"
      data-node-id="9:6424"
      data-testid="purchase-orders-view"
      style={{
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '24px 16px',
        fontFamily: 'Inter, sans-serif'
      }}
    >
      {/* Toast Alert */}
      {toastMessage && (
        <div 
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            zIndex: 9999,
            backgroundColor: toastMessage.type === 'success' ? '#12161c' : '#7f1d1d',
            color: '#ffffff',
            padding: '12px 18px',
            borderRadius: '6px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '13px',
            maxWidth: '420px',
          }}
        >
          {toastMessage.type === 'success' ? <CheckCircle size={16} color="#4ade80" /> : <AlertCircle size={16} color="#f87171" />}
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Header section (Figma 9:6424) */}
      <div style={{ marginBottom: '28px' }}>
        <div 
          style={{ 
            fontSize: '11px', 
            fontWeight: 600, 
            color: '#8a929e', 
            letterSpacing: '0.6px', 
            textTransform: 'uppercase',
            marginBottom: '4px' 
          }}
        >
          Procurement
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 
              style={{ 
                margin: '0 0 6px 0', 
                fontSize: '24px', 
                fontWeight: 600, 
                color: '#12161c', 
                letterSpacing: '-0.6px' 
              }}
            >
              Purchase orders
            </h1>
            <p style={{ margin: 0, fontSize: '13px', color: '#5a6472' }}>
              The last leg of the workflow: a purchase order is raised from the awarded quotation, goods are recorded as received, then the order is closed.
            </p>
          </div>

          <button
            onClick={() => loadPOs()}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 500,
              color: '#5a6472',
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={13} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div 
          style={{
            backgroundColor: '#fef2f2',
            border: '0.667px solid #fecaca',
            color: '#991b1b',
            borderRadius: '6px',
            padding: '12px 16px',
            marginBottom: '20px',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div 
          style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            padding: '60px 0',
            color: '#8a929e',
            gap: '12px'
          }}
        >
          <Loader2 className="animate-spin" size={28} color="#3b45ad" />
          <p style={{ fontSize: '13px', margin: 0 }}>Đang tải danh sách Purchase Orders...</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          {/* SECTION 1: Issued — awaiting delivery (Figma 9:6424) */}
          <div data-testid="section-issued-pos">
            <div style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                  Issued — awaiting delivery
                </h2>
                <span 
                  data-testid="issued-count-badge"
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    backgroundColor: '#eef2ff',
                    color: '#3b45ad',
                    padding: '1px 7px',
                    borderRadius: '10px',
                    border: '0.667px solid #c7d2fe',
                  }}
                >
                  {issuedPOs.length}
                </span>
              </div>
              <div style={{ fontSize: '12px', color: '#8a929e' }}>
                Sent to the supplier, goods not yet recorded.
              </div>
            </div>

            {issuedPOs.length === 0 ? (
              <div 
                style={{ 
                  padding: '24px', 
                  backgroundColor: '#ffffff', 
                  border: '0.667px dashed #e4e7ec', 
                  borderRadius: '6px', 
                  color: '#8a929e', 
                  fontSize: '13px', 
                  fontStyle: 'italic' 
                }}
              >
                None.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {issuedPOs.map((po) => (
                  <div
                    key={po.id}
                    data-testid={`po-card-${po.id}`}
                    onClick={() => setSelectedPO(po)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px 20px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '6px',
                      boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
                      transition: 'border-color 0.15s ease',
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                        <span 
                          data-testid="po-number"
                          style={{ 
                            fontSize: '14px', 
                            fontWeight: 600, 
                            color: '#12161c',
                            fontFamily: 'monospace',
                            letterSpacing: '0.2px',
                          }}
                        >
                          {po.poNumber || po.id}
                        </span>
                        <span 
                          data-testid="po-status-badge"
                          style={{
                            fontSize: '11px',
                            fontWeight: 600,
                            backgroundColor: '#eef2ff',
                            color: '#3b45ad',
                            border: '0.667px solid #c7d2fe',
                            padding: '1px 6px',
                            borderRadius: '4px',
                          }}
                        >
                          Issued
                        </span>
                      </div>

                      <div 
                        data-testid="po-item-supplier"
                        style={{ 
                          fontSize: '13px', 
                          fontWeight: 500, 
                          color: '#12161c', 
                          marginBottom: '4px' 
                        }}
                      >
                        {po.prTitle || 'Purchase Request'} ({po.quantity} {po.quantity > 1 ? 'units' : 'unit'}) · {po.supplierName || 'Awarded Supplier'}
                      </div>

                      <div 
                        data-testid="po-meta-info"
                        style={{ 
                          fontSize: '12px', 
                          color: '#8a929e' 
                        }}
                      >
                        {po.purchaseRequestId || po.prId} · {po.quotationId} · expected delivery in {po.deliveryDays || 5} days
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginLeft: '16px' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div 
                          data-testid="po-total-amount"
                          style={{ 
                            fontSize: '15px', 
                            fontWeight: 600, 
                            color: '#12161c', 
                            fontVariantNumeric: 'tabular-nums' 
                          }}
                        >
                          {formatVND(po.totalAmount)}
                        </div>
                        <div style={{ fontSize: '11px', color: '#8a929e' }}>
                          Unit: {formatVND(po.unitPrice || (po.totalAmount / (po.quantity || 1)))}
                        </div>
                      </div>

                      <ChevronRight size={16} color="#8a929e" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SECTION 2: Received — awaiting close (Figma 9:6424) */}
          <div data-testid="section-received-pos">
            <div style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                  Received — awaiting close
                </h2>
                <span 
                  data-testid="received-count-badge"
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    backgroundColor: '#f0fdf4',
                    color: '#166534',
                    padding: '1px 7px',
                    borderRadius: '10px',
                    border: '0.667px solid #bbf7d0',
                  }}
                >
                  {receivedPOs.length}
                </span>
              </div>
              <div style={{ fontSize: '12px', color: '#8a929e' }}>
                Goods recorded; Procurement closes the order.
              </div>
            </div>

            {receivedPOs.length === 0 ? (
              <div 
                style={{ 
                  padding: '24px', 
                  backgroundColor: '#ffffff', 
                  border: '0.667px dashed #e4e7ec', 
                  borderRadius: '6px', 
                  color: '#8a929e', 
                  fontSize: '13px', 
                  fontStyle: 'italic' 
                }}
              >
                None.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {receivedPOs.map((po) => (
                  <div
                    key={po.id}
                    data-testid={`received-po-card-${po.id}`}
                    onClick={() => setSelectedPO(po)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px 20px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '6px',
                      cursor: 'pointer',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <span style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', fontFamily: 'monospace' }}>
                          {po.poNumber || po.id}
                        </span>
                        <span style={{ fontSize: '11px', fontWeight: 600, backgroundColor: '#f0fdf4', color: '#166534', border: '0.667px solid #bbf7d0', padding: '1px 6px', borderRadius: '4px' }}>
                          Received
                        </span>
                      </div>
                      <div style={{ fontSize: '13px', color: '#12161c' }}>
                        {po.prTitle || 'Purchase Request'} ({po.quantity} units) · {po.supplierName}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '15px', fontWeight: 600, color: '#12161c' }}>
                          {formatVND(po.totalAmount)}
                        </div>
                        <div style={{ fontSize: '11px', color: '#166534', fontWeight: 500 }}>
                          Received: {po.totalReceived || po.quantity}/{po.quantity} units
                        </div>
                      </div>
                      <ChevronRight size={16} color="#8a929e" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SECTION 3: Closed (Figma 9:6424) */}
          <div data-testid="section-closed-pos">
            <div style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                  Closed
                </h2>
                <span 
                  data-testid="closed-count-badge"
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    backgroundColor: '#f8fafc',
                    color: '#64748b',
                    padding: '1px 7px',
                    borderRadius: '10px',
                    border: '0.667px solid #cbd5e1',
                  }}
                >
                  {closedPOs.length}
                </span>
              </div>
              <div style={{ fontSize: '12px', color: '#8a929e' }}>
                Nothing outstanding.
              </div>
            </div>

            {closedPOs.length === 0 ? (
              <div 
                style={{ 
                  padding: '24px', 
                  backgroundColor: '#ffffff', 
                  border: '0.667px dashed #e4e7ec', 
                  borderRadius: '6px', 
                  color: '#8a929e', 
                  fontSize: '13px', 
                  fontStyle: 'italic' 
                }}
              >
                None.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {closedPOs.map((po) => (
                  <div
                    key={po.id}
                    data-testid={`closed-po-card-${po.id}`}
                    onClick={() => setSelectedPO(po)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px 20px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '6px',
                      cursor: 'pointer',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <span style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', fontFamily: 'monospace' }}>
                          {po.poNumber || po.id}
                        </span>
                        <span style={{ fontSize: '11px', fontWeight: 600, backgroundColor: '#f1f5f9', color: '#475569', border: '0.667px solid #cbd5e1', padding: '1px 6px', borderRadius: '4px' }}>
                          Closed
                        </span>
                      </div>
                      <div style={{ fontSize: '13px', color: '#5a6472' }}>
                        {po.prTitle || 'Purchase Request'} ({po.quantity} units) · {po.supplierName}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '15px', fontWeight: 600, color: '#5a6472' }}>
                          {formatVND(po.totalAmount)}
                        </div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>
                          Settled in full
                        </div>
                      </div>
                      <ChevronRight size={16} color="#8a929e" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
};
