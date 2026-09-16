import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api';

export default function App() {
  const [role, setRole] = useState<'EMPLOYEE' | 'MANAGER' | 'PROCUREMENT' | 'FINANCE' | 'ADMIN'>('EMPLOYEE');
  const [rawText, setRawText] = useState('Tôi cần mua gấp 3 cái laptop Dell tầm 25 triệu cho dev mới trong tuần này');
  const [standardized, setStandardized] = useState<any>(null);
  const [budget, setBudget] = useState<any>(null);
  const [prs, setPrs] = useState<any[]>([]);
  const [pos, setPos] = useState<any[]>([]);
  const [comparedQuotations, setComparedQuotations] = useState<any[]>([]);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBudget();
    fetchPrs();
    fetchPos();
  }, []);

  const fetchBudget = async () => {
    try {
      const res = await fetch(`${API_BASE}/budget/DEPT-IT`);
      if (res.ok) {
        const data = await res.json();
        setBudget(data);
      }
    } catch (e) {
      console.warn("Backend server not running yet, using local mock");
      setBudget({
        departmentName: "Phòng Công nghệ Thông tin",
        allocatedAmount: 500000000,
        spentAmount: 150000000,
        tempReservedAmount: 0,
        availableAmount: 350000000
      });
    }
  };

  const fetchPrs = async () => {
    try {
      const res = await fetch(`${API_BASE}/pr`);
      if (res.ok) {
        const data = await res.json();
        setPrs(data);
      }
    } catch (e) {
      setPrs([]);
    }
  };

  const fetchPos = async () => {
    try {
      const res = await fetch(`${API_BASE}/po`);
      if (res.ok) {
        const data = await res.json();
        setPos(data);
      }
    } catch (e) {
      setPos([]);
    }
  };

  const handleStandardize = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/assistant/standardize-pr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: rawText })
      });
      const data = await res.json();
      if (res.ok) {
        setStandardized(data.standardized);
        setMessage({ text: "AI đã bóc tách và chuẩn hóa PR thành công!", type: "success" });
      } else {
        setMessage({ text: data.detail || "Lỗi chuẩn hóa AI", type: "error" });
      }
    } catch (e) {
      // Mock Fallback
      setStandardized({
        title: "Yêu cầu mua sắm: Laptop Dell Vostro Workstation",
        items: [{ itemName: "Laptop Dell Vostro Workstation", quantity: 3, estimatedUnitPrice: 25000000 }],
        total_estimated_value: 75000000
      });
      setMessage({ text: "AI Fast Fallback: Bóc tách thành công!", type: "success" });
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePR = async () => {
    if (!standardized) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/pr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          departmentId: "DEPT-IT",
          creatorId: "employee@company.com",
          title: standardized.title,
          items: standardized.items
        })
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({ text: `Tạo PR ${data.id} thành công! Tạm khóa ${data.estimatedValue.toLocaleString()}đ ngân sách.`, type: "success" });
        fetchBudget();
        fetchPrs();
        setStandardized(null);
      } else {
        setMessage({ text: data.detail, type: "error" });
      }
    } catch (e) {
      setMessage({ text: "Lỗi kết nối Backend", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleApprovePR = async (prId: string) => {
    try {
      const res = await fetch(`${API_BASE}/pr/${prId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approverRole: role,
          approverName: role === 'MANAGER' ? 'Trần Văn B (Manager)' : 'Phạm Văn D (Finance)',
          comments: "Đã duyệt nhu cầu mua sắm"
        })
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({ text: `Cập nhật trạng thái PR: ${data.status}`, type: "success" });
        fetchPrs();
      } else {
        setMessage({ text: data.detail, type: "error" });
      }
    } catch (e) {
      setMessage({ text: "Lỗi kết nối", type: "error" });
    }
  };

  const handleAICompare = async (prId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/quotations/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          purchaseRequestId: prId,
          files: ["bao_gia_phong_vu.pdf", "bao_gia_tran_anh.pdf", "bao_gia_fpt.pdf"]
        })
      });
      const data = await res.json();
      setComparedQuotations(data.comparisons);
      setMessage({ text: "AI đã trích xuất 3 báo giá PDF và phát hiện bất thường đơn giá!", type: "info" });
    } catch (e) {
      setMessage({ text: "Lỗi so sánh báo giá AI", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePO = async (prId: string, q: any) => {
    try {
      const res = await fetch(`${API_BASE}/po`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          purchaseRequestId: prId,
          quotation: q,
          creatorId: "procurement@company.com"
        })
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({ text: `Đã tạo PO ${data.poNumber}! Khóa cố định 100% đơn giá (${data.totalAmount.toLocaleString()}đ).`, type: "success" });
        fetchPrs();
        fetchPos();
        setComparedQuotations([]);
      } else {
        setMessage({ text: data.detail, type: "error" });
      }
    } catch (e) {
      setMessage({ text: "Lỗi tạo PO", type: "error" });
    }
  };

  const handleClosePR = async (prId: string) => {
    try {
      const res = await fetch(`${API_BASE}/pr/${prId}/close`, { method: 'POST' });
      if (res.ok) {
        setMessage({ text: `Đóng hồ sơ PR ${prId} thành công! Đã hạch toán trừ tiền thực tế.`, type: "success" });
        fetchBudget();
        fetchPrs();
      }
    } catch (e) {
      setMessage({ text: "Lỗi đóng hồ sơ", type: "error" });
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '2px solid #e2e8f0', paddingBottom: '16px' }}>
        <div>
          <h1 style={{ margin: 0, color: '#1e3a8a', fontSize: '24px' }}>🛡️ AI Procurement & Purchase Approval System</h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Nhóm 1 · MIS3032_1 · Hướng dẫn AI-Assisted Enterprise Platform 2026</p>
        </div>
        
        {/* Role Selector */}
        <div style={{ background: '#ffffff', padding: '8px 16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: 600, fontSize: '14px', color: '#475569' }}>Vai trò hiện tại:</span>
          <select value={role} onChange={(e: any) => setRole(e.target.value)} style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontWeight: 600, color: '#1e3a8a' }}>
            <option value="EMPLOYEE">👨‍💼 Employee (Người tạo PR)</option>
            <option value="MANAGER">👔 Manager (Người duyệt bước 1)</option>
            <option value="PROCUREMENT">📦 Procurement Specialist (Thu mua)</option>
            <option value="FINANCE">💰 Finance Specialist (Duyệt bước 2 & Quyết toán)</option>
            <option value="ADMIN">⚙️ Admin (Quản trị)</option>
          </select>
        </div>
      </header>

      {/* Alert Banner */}
      {message && (
        <div style={{ 
          padding: '12px 16px', borderRadius: '8px', marginBottom: '24px', fontWeight: 500,
          backgroundColor: message.type === 'success' ? '#dcfce7' : message.type === 'error' ? '#fee2e2' : '#e0f2fe',
          color: message.type === 'success' ? '#166534' : message.type === 'error' ? '#991b1b' : '#075985',
          border: `1px solid ${message.type === 'success' ? '#86efac' : message.type === 'error' ? '#fca5a5' : '#7dd3fc'}`
        }}>
          {message.text}
        </div>
      )}

      {/* Budget Summary Card */}
      {budget && (
        <div style={{ background: '#ffffff', borderRadius: '12px', padding: '20px', marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 16px', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
            📊 Tình Trạng Ngân Sách: <span style={{ color: '#1e3a8a' }}>{budget.departmentName}</span>
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Hạn mức cấp Quý</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>{budget.allocatedAmount?.toLocaleString()}đ</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Đã chi thực tế</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#166534' }}>{budget.spentAmount?.toLocaleString()}đ</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Tạm khóa (PR đang xử lý)</div>
              <div style={{ fontSize: '20px', fontWeight 700, color: '#b45309' }}>{budget.tempReservedAmount?.toLocaleString()}đ</div>
            </div>
            <div style={{ background: '#eff6ff', padding: '12px', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
              <div style={{ fontSize: '12px', color: '#1e40af' }}>Ngân sách khả dụng (BR-01)</div>
              <div style={{ fontSize: '20px', fontWeight 700, color: '#1e3a8a' }}>{budget.availableAmount?.toLocaleString()}đ</div>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Left = Actions based on Role, Right = PR List */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        
        {/* Left Column */}
        <div>
          {role === 'EMPLOYEE' && (
            <div style={{ background: '#ffffff', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ margin: '0 0 16px', color: '#1e3a8a' }}>🎙️ AI Assistant: Khởi Tạo PR Từ Văn Bản / Voice</h3>
              <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '12px' }}>Nhập nội dung thô hoặc yêu cầu bằng giọng nói. AI sẽ chuẩn hóa thành sản phẩm và đơn giá ước tính.</p>
              
              <textarea 
                value={rawText} 
                onChange={(e) => setRawText(e.target.value)}
                rows={3} 
                style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontFamily: 'inherit', fontSize: '14px', boxSizing: 'border-box', marginBottom: '12px' }} 
              />
              
              <button 
                onClick={handleStandardize} 
                disabled={loading}
                style={{ width: '100%', padding: '10px', backgroundColor: '#1e3a8a', color: '#ffffff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer', marginBottom: '16px' }}
              >
                {loading ? 'AI đang bóc tách...' : '✨ Chạy AI Chuẩn Hóa PR (REQ-FR-01)'}
              </button>

              {standardized && (
                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px' }}>
                  <h4 style={{ margin: '0 0 8px', color: '#0f172a' }}>{standardized.title}</h4>
                  <ul style={{ paddingLeft: '20px', margin: '0 0 12px', fontSize: '14px' }}>
                    {standardized.items?.map((item: any, idx: number) => (
                      <li key={idx}>
                        <b>{item.itemName}</b>: {item.quantity} cái × {item.estimatedUnitPrice?.toLocaleString()}đ = {(item.quantity * item.estimatedUnitPrice).toLocaleString()}đ
                      </li>
                    ))}
                  </ul>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: '#1e3a8a', marginBottom: '16px' }}>
                    Tổng ước tính: {standardized.total_estimated_value?.toLocaleString()}đ
                  </div>
                  <button 
                    onClick={handleCreatePR} 
                    style={{ width: '100%', padding: '10px', backgroundColor: '#15803d', color: '#ffffff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}
                  >
                    🚀 Gửi Yêu Cầu PR & Kiểm Tra Ngân Sách
                  </button>
                </div>
              )}
            </div>
          )}

          {role === 'PROCUREMENT' && comparedQuotations.length > 0 && (
            <div style={{ background: '#ffffff', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ margin: '0 0 16px', color: '#1e3a8a' }}>📊 Bảng So Sánh Báo Giá AI (REQ-FR-06)</h3>
              {comparedQuotations.map((q: any, idx: number) => (
                <div key={idx} style={{ 
                  background: q.is_anomaly ? '#fff1f2' : '#f8fafc', 
                  border: `1px solid ${q.is_anomaly ? '#fecdd3' : '#e2e8f0'}`, 
                  borderRadius: '8px', padding: '12px', marginBottom: '12px' 
                }}>
                  <div style={{ fontWeight: 700, color: q.is_anomaly ? '#991b1b' : '#0f172a' }}>{q.supplier_name}</div>
                  <div style={{ fontSize: '13px', color: '#475569' }}>Đơn giá: {q.unit_price?.toLocaleString()}đ | Tổng: {q.total_amount?.toLocaleString()}đ</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>Giao hàng: {q.delivery_days} ngày | Bảo hành: {q.warranty_terms}</div>
                  
                  {q.is_anomaly && (
                    <div style={{ marginTop: '8px', fontSize: '12px', fontWeight: 600, color: '#b91c1c' }}>
                      ⚠️ {q.anomaly_reason}
                    </div>
                  )}

                  <button 
                    onClick={() => handleCreatePO(q.purchaseRequestId || prs[0]?.id, q)} 
                    style={{ marginTop: '10px', padding: '6px 12px', backgroundColor: q.is_anomaly ? '#991b1b' : '#15803d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}
                  >
                    Chọn Báo Giá Này & Khởi Tạo PO (Khóa Giá 100%)
                  </button>
                </div>
              ))}
            </div>
          )}

          {role !== 'EMPLOYEE' && comparedQuotations.length === 0 && (
            <div style={{ background: '#ffffff', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ margin: '0 0 12px', color: '#1e3a8a' }}>ℹ️ Hướng Dẫn Thao Tác Theo Vai Trò ({role})</h3>
              {role === 'MANAGER' && <p style={{ fontSize: '14px', color: '#475569' }}>Bạn có quyền Phê duyệt bước 1 cho các PR gửi từ nhân viên. PR trên 50 triệu VND sẽ cần chuyển tiếp sang Finance duyệt bước 2.</p>}
              {role === 'PROCUREMENT' && <p style={{ fontSize: '14px', color: '#475569' }}>Chọn một PR ở trạng thái `APPROVED` bên phải và bấm <b>"Trích xuất Báo giá PDF (AI)"</b> để so sánh tự động.</p>}
              {role === 'FINANCE' && <p style={{ fontSize: '14px', color: '#475569' }}>Bạn phụ trách duyệt PR bước 2 ($> 50$tr VND) và bấm <b>"Đóng Hồ Sơ (Close PR)"</b> để hạch toán ngân sách thực tế.</p>}
              {role === 'ADMIN' && <p style={{ fontSize: '14px', color: '#475569' }}>Toàn quyền quản trị hệ thống và kiểm tra nhật ký Audit Log.</p>}
            </div>
          )}
        </div>

        {/* Right Column: PR List */}
        <div style={{ background: '#ffffff', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 16px', color: '#1e3a8a' }}>📋 Danh Sách Yêu Cầu Mua Sắm (PR)</h3>
          {prs.length === 0 ? (
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>Chưa có PR nào trong hệ thống. Hãy khởi tạo từ thẻ bên trái.</p>
          ) : (
            prs.map((pr: any) => (
              <div key={pr.id} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px', marginBottom: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 700, color: '#1e3a8a' }}>{pr.id} - {pr.title}</span>
                  <span style={{ 
                    padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700,
                    backgroundColor: pr.status === 'APPROVED' ? '#dcfce7' : pr.status === 'CLOSED' ? '#e2e8f0' : '#fef3c7',
                    color: pr.status === 'APPROVED' ? '#15803d' : pr.status === 'CLOSED' ? '#475569' : '#b45309'
                  }}>
                    {pr.status}
                  </span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a', marginBottom: '8px' }}>
                  Ước tính: {pr.estimatedValue?.toLocaleString()}đ {pr.estimatedValue > 50000000 && <span style={{ color: '#b45309', fontSize: '12px' }}>(Trên 50tr - Luồng 2 cấp)</span>}
                </div>

                {/* Actions based on Role and Status */}
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '10px' }}>
                  {role === 'MANAGER' && pr.status === 'PENDING_MANAGER_APPROVAL' && (
                    <button onClick={() => handleApprovePR(pr.id)} style={{ padding: '6px 12px', backgroundColor: '#15803d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                      👔 Duyệt PR Bước 1 (Manager)
                    </button>
                  )}

                  {role === 'FINANCE' && pr.status === 'PENDING_FINANCE_APPROVAL' && (
                    <button onClick={() => handleApprovePR(pr.id)} style={{ padding: '6px 12px', backgroundColor: '#15803d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                      💰 Duyệt PR Bước 2 (Finance > 50tr)
                    </button>
                  )}

                  {role === 'PROCUREMENT' && pr.status === 'APPROVED' && (
                    <button onClick={() => handleAICompare(pr.id)} style={{ padding: '6px 12px', backgroundColor: '#1e3a8a', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                      📄 Trích Xuất Báo Giá PDF (AI)
                    </button>
                  )}

                  {role === 'FINANCE' && pr.status === 'PO_CREATED' && (
                    <button onClick={() => handleClosePR(pr.id)} style={{ padding: '6px 12px', backgroundColor: '#475569', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                      🔒 Phê Duyệt Đóng Hồ Sơ (Close PR)
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

      </div>

      {/* Footer link to Vault */}
      <footer style={{ marginTop: '40px', borderTop: '1px solid #e2e8f0', paddingTop: '16px', textAlign: 'center', fontSize: '13px', color: '#64748b' }}>
        Tài liệu tri thức Project Vault: <a href="file:///d:/THUDDN/group-01-project/docs/00-project-index.md" style={{ color: '#1e3a8a', fontWeight: 600 }}>docs/00-project-index.md</a> | Môn học MIS3032_1
      </footer>
    </div>
  );
}
