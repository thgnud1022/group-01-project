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
  ExternalLink,
  ShieldAlert
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
  onSelectPO,
}) => {
  const [pos, setPos] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPOs();
  }, []);

  const loadPOs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listPOs();
      setPos(Array.isArray(data) ? data : []);
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

  // Group POs into the 3 Figma 9:6424 categories
  const issuedPOs = pos.filter((p) => p.status === 'SENT' || p.status === 'PO_CREATED' || p.status === 'ISSUED');
  const receivedPOs = pos.filter((p) => p.status === 'RECEIVED' || p.status === 'PARTIALLY_RECEIVED');
  const closedPOs = pos.filter((p) => p.status === 'CLOSED');

  return (
    <div 
      className="purchase-orders-view"
      data-node-id="9:6424"
      data-testid="purchase-orders-view"
      style={{
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '24px 16px',
      }}
    >
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
              The last leg of the workflow: order, receive, close.
            </p>
          </div>
          <button
            onClick={loadPOs}
            disabled={loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 600,
              color: '#5a6472',
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div 
          style={{ 
            padding: '12px 16px', 
            backgroundColor: '#fdecec', 
            border: '0.667px solid #fad2d2', 
            borderRadius: '6px', 
            color: '#8e1e1e', 
            fontSize: '13px', 
            marginBottom: '20px' 
          }}
        >
          {error}
        </div>
      )}

      {loading ? (
        <div 
          style={{ 
            padding: '60px 0', 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                Issued — awaiting delivery
              </h2>
              <span 
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
                    onClick={() => onSelectPO && onSelectPO(po)}
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
                      cursor: onSelectPO ? 'pointer' : 'default',
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
                        {po.purchaseRequestId} · {po.quotationId} · expected delivery in {po.deliveryDays || 5} days
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                Received — awaiting close
              </h2>
              <span 
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
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px 20px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '6px',
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
                        {po.prTitle || 'Purchase Request'} · {po.supplierName}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '15px', fontWeight: 600, color: '#12161c' }}>
                        {formatVND(po.totalAmount)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SECTION 3: Closed (Figma 9:6424) */}
          <div data-testid="section-closed-pos">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                Closed
              </h2>
              <span 
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
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px 20px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '6px',
                    }}
                  >
                    <div>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', fontFamily: 'monospace' }}>
                        {po.poNumber || po.id}
                      </span>
                      <div style={{ fontSize: '13px', color: '#5a6472' }}>
                        {po.prTitle || 'Purchase Request'} · {po.supplierName}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '15px', fontWeight: 600, color: '#5a6472' }}>
                        {formatVND(po.totalAmount)}
                      </div>
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
