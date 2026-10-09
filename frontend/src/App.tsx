import React, { useState, useEffect } from 'react';
import { api, AuthenticatedUser } from './api/client';
import { AppShell, NavItemKey, canAccessTab, UserRole } from './components/AppShell';
import { Login } from './components/Login';
import { PurchaseRequestsView } from './components/PurchaseRequestsView';
import { NewRequestView } from './components/NewRequestView';
import { PRDetailView } from './components/PRDetailView';
import { EditDraftView } from './components/EditDraftView';
import { ApprovalsQueueView } from './components/ApprovalsQueueView';
import { BudgetReviewView } from './components/BudgetReviewView';
import { EditAfterRevisionView } from './components/EditAfterRevisionView';
import { EditLockedModal } from './components/EditLockedModal';
import { SourcingView } from './components/SourcingView';
import { SuppliersView } from './components/SuppliersView';
import { CollectQuotationsView } from './components/CollectQuotationsView';
import { ComparisonView } from './components/ComparisonView';
import { PurchaseOrdersView } from './components/PurchaseOrdersView';
import { 
  Sparkles, 
  Send, 
  Plus, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Package, 
  Building2, 
  FileText,
  Shield,
  ArrowRight
} from 'lucide-react';

export default function App() {
  const [user, setUser] = useState<AuthenticatedUser | null>(api.getUser());
  const [currentTab, setCurrentTab] = useState<NavItemKey>('purchase-requests');
  const [selectedPR, setSelectedPR] = useState<any | null>(null);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editAfterRevisionMode, setEditAfterRevisionMode] = useState<boolean>(false);
  const [collectingQuotationsPR, setCollectingQuotationsPR] = useState<any | null>(null);
  const [comparingPR, setComparingPR] = useState<any | null>(null);

  // System message banner
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  // New Request Form State (Flow A / Figma 9:645)
  const [rawText, setRawText] = useState('Cần mua 2 máy tính Dell XPS 15 cho team thiết kế, dự kiến 25tr/máy và 1 màn hình 4K');
  const [standardized, setStandardized] = useState<{
    title?: string;
    items?: Array<{ itemName: string; quantity: number; estimatedUnitPrice: number }>;
    total_estimated_value?: number;
    is_fallback?: boolean;
  } | null>(null);
  const [isAiLoading, setIsAiLoading] = useState(false);

  // Sourcing & Quotations State (Flow C & D / Figma 9:4479, 9:4790, 9:5291)
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [pos, setPos] = useState<any[]>([]);
  const [receivings, setReceivings] = useState<any[]>([]);
  const [comparedQuotations, setComparedQuotations] = useState<any[]>([]);
  const [aiRecommendation, setAiRecommendation] = useState<any | null>(null);

  // New Supplier Form State
  const [newSupplierName, setNewSupplierName] = useState('');
  const [newSupplierTax, setNewSupplierTax] = useState('');

  // Receiving Form State
  const [selectedPOForReceiving, setSelectedPOForReceiving] = useState<string>('');
  const [receivedQty, setReceivedQty] = useState<number>(1);

  // Auto clear message after 5 seconds
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  // Restore existing Supabase session on initial mount
  useEffect(() => {
    api.restoreSession().then((restoredUser) => {
      if (restoredUser) {
        setUser(restoredUser);
      }
    });
  }, []);

  // Listen for unauthorized 401 events to clear user session
  useEffect(() => {
    return api.onUnauthorized(() => {
      setUser(null);
      setMessage({ type: 'error', text: 'Phiên làm việc đã hết hạn hoặc chưa được xác thực (401).' });
    });
  }, []);

  // RBAC guard: redirect to default tab if current tab is not accessible for user's role
  useEffect(() => {
    if (!user) return;
    if (!canAccessTab(user.role as UserRole, currentTab)) {
      setCurrentTab('purchase-requests');
    }
  }, [user, currentTab]);

  // Load supporting domain data when tab changes
  useEffect(() => {
    if (!user) return;
    if (currentTab === 'suppliers' || currentTab === 'sourcing') {
      api.listSuppliers().then(setSuppliers).catch(console.error);
    }
    if (currentTab === 'purchase-orders') {
      api.listPOs().then(setPos).catch(console.error);
      api.listReceivings().then(setReceivings).catch(console.error);
    }
  }, [currentTab, user]);

  const handleLogout = async () => {
    await api.clearSession();
    setUser(null);
    setSelectedPR(null);
    setEditMode(false);
    setEditAfterRevisionMode(false);
    setCollectingQuotationsPR(null);
    setComparingPR(null);
    setCurrentTab('purchase-requests');
  };


  // Flow A: AI Standardize PR (P0-03 fixed: reads top-level fields)
  const handleStandardize = async () => {
    if (!rawText.trim()) return;
    setIsAiLoading(true);
    setMessage(null);
    try {
      const data = await api.standardizePR(rawText);
      setStandardized({
        title: data.title,
        items: data.items,
        total_estimated_value: data.total_estimated_value,
        is_fallback: data.is_fallback,
      });
      setMessage({ type: 'success', text: 'AI đã chuẩn hóa thành công yêu cầu mua sắm!' });
    } catch (err: any) {
      setMessage({ type: 'error', text: `Lỗi AI chuẩn hóa: ${err.message}` });
    } finally {
      setIsAiLoading(false);
    }
  };

  // Flow A: Submit PR to Backend
  const handleSubmitPR = async () => {
    if (!standardized || !standardized.items || standardized.items.length === 0) {
      setMessage({ type: 'error', text: 'Vui lòng chuẩn hóa danh mục trước khi tạo PR.' });
      return;
    }

    try {
      await api.createPR({
        departmentId: user?.departmentId || 'DEPT-IT',
        title: standardized.title || 'Yêu cầu thiết bị CNTT',
        items: standardized.items,
      });
      setMessage({ type: 'success', text: 'Tạo yêu cầu mua sắm (PR) thành công!' });
      setStandardized(null);
      setRawText('');
      setCurrentTab('purchase-requests');
    } catch (err: any) {
      setMessage({ type: 'error', text: `Lỗi tạo PR: ${err.message}` });
    }
  };

  // Flow B: Manager/Finance Approval
  const handleApprove = async (prId: string) => {
    try {
      await api.approvePR(prId, 'Phê duyệt yêu cầu mua sắm theo quy chuẩn');
      setMessage({ type: 'success', text: `Đã phê duyệt PR ${prId} thành công!` });
      setCurrentTab('purchase-requests');
    } catch (err: any) {
      setMessage({ type: 'error', text: `Lỗi phê duyệt: ${err.message}` });
    }
  };

  // Flow C/D: AI Quotation Recommendation (P0-04 fixed)
  const handleAICompare = async (prId: string) => {
    try {
      const res = await api.compareQuotations(prId);
      const quotes = res?.comparisons || (Array.isArray(res) ? res : []);
      setComparedQuotations(quotes);
      if (quotes.length > 0) {
        const reco = await api.recommendQuotations({
          purchase_request_id: prId,
          total_estimated_value: quotes.reduce((acc: number, q: any) => acc + (q.totalAmount || 0), 0) / quotes.length,
          quotations: quotes.map((q: any) => ({
            quotation_id: q.id,
            supplier_name: q.supplierName || 'Nhà cung cấp',
            total_amount: q.totalAmount || q.unitPrice * q.quantity,
            unit_price: q.unitPrice,
            quantity: q.quantity,
            delivery_days: q.deliveryDays || 3,
            warranty_terms: q.warrantyTerms || '12 tháng',
            is_anomaly: false,
          })),
        });
        setAiRecommendation(reco);
      }
      setMessage({ type: 'success', text: 'Đã trích xuất & so sánh báo giá thành công!' });
    } catch (err: any) {
      setMessage({ type: 'error', text: `Lỗi so sánh báo giá: ${err.message}` });
    }
  };

  // Flow D: Create PO (P0-04 fixed: sends purchaseRequestId & quotationId)
  const handleCreatePO = async (prId: string, quotationId: string) => {
    try {
      await api.createPO({
        purchaseRequestId: prId,
        quotationId: quotationId,
      });
      setMessage({ type: 'success', text: 'Tạo đơn đặt hàng (PO) thành công!' });
      setCurrentTab('purchase-orders');
    } catch (err: any) {
      setMessage({ type: 'error', text: `Lỗi tạo PO: ${err.message}` });
    }
  };

  // Flow E: Goods Receiving
  const handleReceiveGoods = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPOForReceiving) {
      setMessage({ type: 'error', text: 'Vui lòng chọn Purchase Order để nhận hàng.' });
      return;
    }
    try {
      await api.receiveGoods({
        purchaseOrderId: selectedPOForReceiving,
        receivedQty: Number(receivedQty),
        fileUrl: 'https://storage.company.com/receipts/bien-ban-nhan-hang.pdf',
      });
      setMessage({ type: 'success', text: 'Ghi nhận nhận hàng thành công!' });
      api.listReceivings().then(setReceivings);
      api.listPOs().then(setPos);
    } catch (err: any) {
      setMessage({ type: 'error', text: `Lỗi nhận hàng: ${err.message}` });
    }
  };

  // Flow F: Close PR (HD-07 Guard)
  const handleClosePR = async (prId: string) => {
    try {
      await api.closePR(prId);
      setMessage({ type: 'success', text: `Đã đóng hồ sơ PR ${prId} thành công!` });
      setCurrentTab('purchase-requests');
    } catch (err: any) {
      setMessage({ type: 'error', text: `Không thể đóng PR: ${err.message}` });
    }
  };

  // Create Supplier
  const handleCreateSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSupplierName.trim()) return;
    try {
      await api.createSupplier({ name: newSupplierName.trim(), taxCode: newSupplierTax.trim() });
      setMessage({ type: 'success', text: `Đã thêm nhà cung cấp ${newSupplierName}!` });
      setNewSupplierName('');
      setNewSupplierTax('');
      api.listSuppliers().then(setSuppliers);
    } catch (err: any) {
      setMessage({ type: 'error', text: `Lỗi tạo nhà cung cấp: ${err.message}` });
    }
  };

  // If user is not logged in, render Login screen
  if (!user) {
    return <Login onLoginSuccess={(loggedInUser) => setUser(loggedInUser)} />;
  }

  return (
    <AppShell
      currentTab={currentTab}
      onNavigate={(tab) => {
        setCurrentTab(tab);
        setSelectedPR(null);
        setEditMode(false);
        setEditAfterRevisionMode(false);
        setCollectingQuotationsPR(null);
        setComparingPR(null);
      }}
      user={user}
      onLogout={handleLogout}
    >
      {/* Toast / Alert Message Banner (Fixed non-disruptive toast) */}
      {message && (
        <div
          style={{
            position: 'fixed',
            top: '24px',
            right: '32px',
            zIndex: 9999,
            padding: '12px 18px',
            borderRadius: '6px',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            backgroundColor: message.type === 'success' ? '#e9f7ef' : message.type === 'error' ? '#fdecec' : '#eef1ff',
            border: `0.667px solid ${message.type === 'success' ? '#b6e2c7' : message.type === 'error' ? '#f4c2c2' : '#c3ccff'}`,
            color: message.type === 'success' ? '#16603b' : message.type === 'error' ? '#8e1e1e' : '#2f3789',
            boxShadow: '0 4px 14px rgba(18, 22, 28, 0.08)',
          }}
          data-testid="app-message-banner"
        >
          {message.type === 'success' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
          <span>{message.text}</span>
          <button
            onClick={() => setMessage(null)}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '16px',
              cursor: 'pointer',
              marginLeft: '8px',
              color: 'inherit',
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>
      )}

      {/* SCREEN 1 & 3 & 5 & 6 & 8 & 9: Purchase Requests List / PR Detail Lifecycle */}
      {currentTab === 'purchase-requests' && (
        selectedPR ? (
          editAfterRevisionMode ? (
            <EditAfterRevisionView
              pr={selectedPR}
              user={user}
              onBack={() => setEditAfterRevisionMode(false)}
              onResubmitSuccess={(updated) => {
                setMessage({ type: 'success', text: `Yêu cầu mua sắm ${updated.id || ''} đã được gửi lại thành công!` });
                setSelectedPR(updated);
                setEditAfterRevisionMode(false);
              }}
              onSaveSuccess={(updated) => {
                setMessage({ type: 'info', text: 'Đã lưu thay đổi yêu cầu!' });
                setSelectedPR(updated);
                setEditAfterRevisionMode(false);
              }}
            />
          ) : editMode ? (
            <EditDraftView
              pr={selectedPR}
              user={user}
              onBack={() => setEditMode(false)}
              onSubmitSuccess={(created) => {
                setMessage({ type: 'success', text: `Yêu cầu mua sắm ${created.id || ''} đã được gửi thành công!` });
                setSelectedPR(created);
                setEditMode(false);
              }}
              onSaveSuccess={(updated) => {
                setMessage({ type: 'info', text: 'Đã lưu thay đổi bản nháp!' });
                setSelectedPR(updated);
                setEditMode(false);
              }}
            />
          ) : (
            <PRDetailView
              pr={selectedPR}
              user={user}
              onBack={() => {
                setSelectedPR(null);
                setEditMode(false);
                setEditAfterRevisionMode(false);
              }}
              onEdit={(prToEdit) => {
                setSelectedPR(prToEdit);
                setEditMode(true);
              }}
              onEditAfterRevision={(prToEdit) => {
                setSelectedPR(prToEdit);
                setEditAfterRevisionMode(true);
              }}
              onApproveSuccess={(updated) => {
                setMessage({ type: 'success', text: `Phê duyệt yêu cầu ${updated.id} thành công!` });
                setSelectedPR(updated);
              }}
              onNavigateTab={(tab) => setCurrentTab(tab as NavItemKey)}
              onCollectQuotations={(prToCollect) => {
                const targetPR = prToCollect || selectedPR;
                setComparingPR(null);
                setCollectingQuotationsPR(targetPR);
                setCurrentTab('sourcing');
              }}
              onRetrySubmit={async (retryPr) => {
                try {
                  const res = await api.createPR({
                    departmentId: 'DEPT-IT',
                    title: retryPr.title,
                    items: retryPr.items && retryPr.items.length > 0 ? retryPr.items : [
                      { itemName: retryPr.title, quantity: 1, estimatedUnitPrice: Number(retryPr.estimatedValue || 14400000) }
                    ],
                  });
                  setSelectedPR(res);
                  setMessage({ type: 'success', text: 'Gửi lại yêu cầu thành công!' });
                } catch (err: any) {
                  setMessage({ type: 'error', text: `Gửi lại thất bại: ${err.message}` });
                }
              }}
            />
          )
        ) : (
          <PurchaseRequestsView
            onNewRequest={() => {
              setSelectedPR(null);
              setEditMode(false);
              setEditAfterRevisionMode(false);
              setCurrentTab('new-request');
            }}
            onSelectPR={(pr) => {
              setEditMode(false);
              setEditAfterRevisionMode(false);
              setSelectedPR(pr);
            }}
            user={user}
          />
        )
      )}

      {/* SCREEN 2: New Request (Figma 9:645 Flow A) */}
      {currentTab === 'new-request' && (
        <NewRequestView
          user={user}
          onSuccess={(created) => {
            setMessage({ type: 'success', text: `Tạo PR ${created.id} thành công!` });
            setSelectedPR(created);
            setEditMode(false);
            setCurrentTab('purchase-requests');
          }}
          onSaveDraft={(draft) => {
            setMessage({ type: 'info', text: 'Đã lưu bản nháp PR thành công!' });
            setSelectedPR(draft);
            setEditMode(false);
            setCurrentTab('purchase-requests');
          }}
          onErrorState={(errInfo) => {
            setSelectedPR({ ...errInfo, status: 'ERROR' });
            setEditMode(false);
            setCurrentTab('purchase-requests');
          }}
          onCancel={() => {
            setCurrentTab('purchase-requests');
          }}
        />
      )}

      {/* STEP 1: Approvals Queue (Figma 9:1813 Flow B) & STEP 2: Approval + Budget Warning (Figma 9:2010) */}
      {currentTab === 'approvals' && (
        selectedPR ? (
          editAfterRevisionMode ? (
            <EditAfterRevisionView
              pr={selectedPR}
              user={user}
              onBack={() => setEditAfterRevisionMode(false)}
              onResubmitSuccess={(updated) => {
                setMessage({ type: 'success', text: `Yêu cầu mua sắm ${updated.id || ''} đã được gửi lại thành công!` });
                setSelectedPR(updated);
                setEditAfterRevisionMode(false);
              }}
              onSaveSuccess={(updated) => {
                setMessage({ type: 'info', text: 'Đã lưu thay đổi yêu cầu!' });
                setSelectedPR(updated);
                setEditAfterRevisionMode(false);
              }}
            />
          ) : editMode ? (
            <EditDraftView
              pr={selectedPR}
              user={user}
              onBack={() => setEditMode(false)}
              onSubmitSuccess={(created) => {
                setMessage({ type: 'success', text: `Yêu cầu mua sắm ${created.id || ''} đã được gửi thành công!` });
                setSelectedPR(created);
                setEditMode(false);
              }}
              onSaveSuccess={(updated) => {
                setMessage({ type: 'info', text: 'Đã lưu thay đổi bản nháp!' });
                setSelectedPR(updated);
                setEditMode(false);
              }}
            />
          ) : (
            <PRDetailView
              pr={selectedPR}
              user={user}
              onBack={() => {
                setSelectedPR(null);
                setEditMode(false);
                setEditAfterRevisionMode(false);
              }}
              onEdit={(prToEdit) => {
                setSelectedPR(prToEdit);
                setEditMode(true);
              }}
              onEditAfterRevision={(prToEdit) => {
                setSelectedPR(prToEdit);
                setEditAfterRevisionMode(true);
              }}
              onApproveSuccess={(updated) => {
                setMessage({ type: 'success', text: `Phê duyệt yêu cầu ${updated.id} thành công!` });
                setSelectedPR(updated);
              }}
              onNavigateTab={(tab) => setCurrentTab(tab as NavItemKey)}
            />
          )
        ) : (
          <ApprovalsQueueView
            user={user}
            onSelectPR={(pr) => {
              setEditMode(false);
              setEditAfterRevisionMode(false);
              setSelectedPR(pr);
            }}
          />
        )
      )}

      {/* STEP 4: Budget Review (Figma 9:2431) & STEP 5: Finance Budget Decision (Figma 9:2635) */}
      {currentTab === 'budget-review' && (
        selectedPR ? (
          <PRDetailView
            pr={selectedPR}
            user={user}
            onBack={() => {
              setSelectedPR(null);
              setEditMode(false);
              setEditAfterRevisionMode(false);
            }}
            onEdit={(prToEdit) => {
              setSelectedPR(prToEdit);
              setEditMode(true);
            }}
            onEditAfterRevision={(prToEdit) => {
              setSelectedPR(prToEdit);
              setEditAfterRevisionMode(true);
            }}
            onApproveSuccess={(updated) => {
              setMessage({ type: 'success', text: `Thẩm tra ngân sách yêu cầu ${updated.id} thành công!` });
              setSelectedPR(updated);
            }}
            onNavigateTab={(tab) => setCurrentTab(tab as NavItemKey)}
          />
        ) : (
          <BudgetReviewView
            user={user}
            onSelectPR={(pr) => {
              setEditMode(false);
              setEditAfterRevisionMode(false);
              setSelectedPR(pr);
            }}
          />
        )
      )}

      {/* SCREEN 5: Sourcing (Figma 9:4001) / Collect Quotations (Figma 9:4163) / Comparison (Figma 9:4373 & 9:4790) */}
      {currentTab === 'sourcing' && (
        comparingPR ? (
          <ComparisonView
            prId={comparingPR.id}
            prData={comparingPR}
            user={user}
            onBack={() => setComparingPR(null)}
            onCollectQuotations={(pr) => {
              setComparingPR(null);
              setCollectingQuotationsPR(pr);
            }}
            onViewRequest={(pr) => {
              setComparingPR(null);
              setSelectedPR(pr);
              setCurrentTab('purchase-requests');
            }}
            onOpenPO={() => {
              setComparingPR(null);
              setCurrentTab('purchase-orders');
            }}
          />
        ) : collectingQuotationsPR ? (
          <CollectQuotationsView
            prId={collectingQuotationsPR.id}
            prData={collectingQuotationsPR}
            user={user}
            onBack={() => setCollectingQuotationsPR(null)}
            onNavigateTab={(tab) => {
              setCollectingQuotationsPR(null);
              setCurrentTab(tab as NavItemKey);
            }}
            onProceedToComparison={(prId) => {
              setComparingPR(collectingQuotationsPR || { id: prId });
            }}
          />
        ) : (
          <SourcingView
            user={user}
            onNavigateTab={(tab) => setCurrentTab(tab as NavItemKey)}
            onSelectPR={(pr) => {
              setSelectedPR(pr);
              setCurrentTab('purchase-requests');
            }}
            onCollectQuotations={(pr) => {
              setCollectingQuotationsPR(pr);
            }}
            onCompareQuotations={(pr) => {
              setComparingPR(pr);
            }}
          />
        )
      )}

      {/* SCREEN 6: Suppliers (Figma 9:4479) */}
      {currentTab === 'suppliers' && (
        <SuppliersView
          user={user}
          onNavigateTab={(tab) => setCurrentTab(tab as NavItemKey)}
        />
      )}

      {/* SCREEN 7: Purchase Orders (Figma 9:6424) */}
      {currentTab === 'purchase-orders' && (
        <PurchaseOrdersView
          user={user}
          onNavigateTab={(tab) => setCurrentTab(tab as NavItemKey)}
        />
      )}

      {/* SCREEN 8: Audit Trail (Rule 29) */}
      {currentTab === 'audit-trail' && (
        <div style={{ maxWidth: '860px', margin: '0 auto' }}>
          <div style={{ marginBottom: '24px' }}>
            <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', textTransform: 'uppercase', letterSpacing: '0.55px', marginBottom: '4px' }}>
              Governance · GOV-02
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: 600, color: '#12161c', margin: '0 0 4px 0', letterSpacing: '-0.6px' }}>
              Nhật ký kiểm toán (Audit Trail)
            </h1>
            <p style={{ margin: 0, fontSize: '14px', color: '#5a6472' }}>
              Ghi vết đầy đủ mọi hành động thay đổi trạng thái, vai trò tác tử, và thời gian thực hiện.
            </p>
          </div>

          <div style={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '0.667px solid #e4e7ec', overflow: 'hidden' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '20% 25% 15% 40%', padding: '10px 16px', backgroundColor: '#f8fafc', borderBottom: '0.667px solid #e4e7ec', fontSize: '11px', fontWeight: 600, color: '#5a6472' }}>
              <div>Thời gian</div>
              <div>Tác tử (Actor)</div>
              <div>Hành động</div>
              <div>Chi tiết đối tượng</div>
            </div>
            <div style={{ padding: '24px', textAlign: 'center', color: '#8a929e', fontSize: '13px' }}>
              Hồ sơ kiểm toán được bảo đảm toàn vẹn trên Supabase PostgreSQL theo tiêu chuẩn GOV-02.
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
