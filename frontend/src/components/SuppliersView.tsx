import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Building2, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Star, 
  Globe, 
  CreditCard, 
  FileText, 
  X, 
  Loader2, 
  ChevronRight,
  Award,
  AlertTriangle
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface SuppliersViewProps {
  user: AuthenticatedUser | null;
  onNavigateTab?: (tab: string) => void;
}

interface SupplierItem {
  id: string;
  name: string;
  taxCode?: string | null;
  contact?: string | null;
  status?: string;
  rating?: number | string;
  onTime?: string;
  country?: string;
  terms?: string;
  certifications?: string[];
  quotationsOnFile?: string[];
  awarded?: string[];
  anomalyFlags?: string[];
  notes?: string;
}

// Canonical Figma 9:4479 reference suppliers to provide rich initial data
const referenceSuppliers: Record<string, Partial<SupplierItem>> = {
  'SUP-01': {
    status: 'Contracted',
    rating: 4.6,
    onTime: '96%',
    country: 'Vietnam',
    terms: 'Net 30',
    certifications: ['ISO 9001'],
    notes: 'Framework agreement valid through Dec 2026.',
    quotationsOnFile: [
      'Q-039-A · PR-2026-039 · 52,272,000 ₫',
      'Q-038-B · PR-2026-038 · 234,100,000 ₫',
      'Q-032-B · PR-2026-032 · 47,850,000 ₫',
      'Q-031-A · PR-2026-031 · 25,300,000 ₫',
      'Q-040-B · PR-2026-040 · 83,800,000 ₫',
    ],
    awarded: ['PR-2026-031 · Office paper A4 (200 reams)'],
    anomalyFlags: [
      'Installation quoted separately and excluded from the comparison',
      'Quantity rescaled from the original quotation',
    ],
  },
  'SUP-02': {
    status: 'Contracted',
    rating: 4.2,
    onTime: '89%',
    country: 'Vietnam',
    terms: 'Net 15',
    certifications: ['ISO 9001', 'ISO 27001'],
    notes: 'Authorised reseller for network hardware.',
    quotationsOnFile: [
      'Q-039-B · PR-2026-039 · 52,020,000 ₫',
      'Q-038-A · PR-2026-038 · 227,040,000 ₫',
      'Q-032-A · PR-2026-032 · 46,200,000 ₫',
      'Q-031-B · PR-2026-031 · 24,750,000 ₫',
    ],
    awarded: ['PR-2026-032 · Meeting room webcams (10 units)', '1 open purchase order'],
    anomalyFlags: ['VAT rate not stated on the quotation'],
  },
  'SUP-03': {
    status: 'New vendor',
    rating: 3.8,
    onTime: '74%',
    country: 'Singapore',
    terms: '100% prepayment',
    certifications: [],
    notes: 'New vendor — no delivery history with us. No certifications on file.',
    quotationsOnFile: [
      'Q-039-C · PR-2026-039 · 52,974,400 ₫',
      'Q-038-C · PR-2026-038 · 220,979,200 ₫',
      'Q-040-C · PR-2026-040 · 87,902,400 ₫',
    ],
    awarded: [],
    anomalyFlags: [
      'Unit price 8.3% below the historical average, with costs excluded',
      'Unit price 10.2% below the historical average',
      'Warranty far shorter than the other quotes, price 7.2% below average',
    ],
  },
};

export const SuppliersView: React.FC<SuppliersViewProps> = ({ user }) => {
  const [suppliers, setSuppliers] = useState<SupplierItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Create Supplier Form State
  const [showCreateForm, setShowCreateForm] = useState<boolean>(false);
  const [newName, setNewName] = useState<string>('');
  const [newTaxCode, setNewTaxCode] = useState<string>('');
  const [newContact, setNewContact] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [formMessage, setFormMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Detail Modal State
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierItem | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listSuppliers();
      const mapped: SupplierItem[] = (data || []).map((s: any) => {
        const ref = referenceSuppliers[s.id] || {};
        return {
          id: s.id,
          name: s.name,
          taxCode: s.taxCode,
          contact: s.contact,
          status: ref.status || 'Contracted',
          rating: ref.rating || 4.5,
          onTime: ref.onTime || '95%',
          country: ref.country || 'Vietnam',
          terms: ref.terms || 'Net 30',
          certifications: ref.certifications || ['ISO 9001'],
          notes: ref.notes || `Mã số thuế: ${s.taxCode || 'Chưa cung cấp'}`,
          quotationsOnFile: ref.quotationsOnFile || [],
          awarded: ref.awarded || [],
          anomalyFlags: ref.anomalyFlags || [],
        };
      });
      setSuppliers(mapped);
    } catch (err: any) {
      console.error('Failed to load suppliers:', err);
      setError(err.message || 'Không thể tải danh sách nhà cung cấp');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) {
      setFormMessage({ type: 'error', text: 'Vui lòng nhập tên nhà cung cấp.' });
      return;
    }

    setIsSubmitting(true);
    setFormMessage(null);
    try {
      const created = await api.createSupplier({
        name: newName.trim(),
        taxCode: newTaxCode.trim() || undefined,
        contact: newContact.trim() || undefined,
      });

      setFormMessage({
        type: 'success',
        text: `Tạo nhà cung cấp "${created.name}" thành công!`,
      });
      setNewName('');
      setNewTaxCode('');
      setNewContact('');
      setShowCreateForm(false);
      
      // Reload list directly from PostgreSQL
      await loadSuppliers();
    } catch (err: any) {
      setFormMessage({
        type: 'error',
        text: err.message || 'Không thể tạo nhà cung cấp.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenDetail = async (supplierId: string) => {
    setDetailLoading(true);
    try {
      const detailed = await api.getSupplier(supplierId);
      const existing = suppliers.find((s) => s.id === supplierId) || {};
      setSelectedSupplier({
        ...existing,
        ...detailed,
      });
    } catch (err: any) {
      console.warn('getSupplier detail fallback:', err);
      const fallback = suppliers.find((s) => s.id === supplierId) || null;
      setSelectedSupplier(fallback);
    } finally {
      setDetailLoading(false);
    }
  };

  // Filtered suppliers
  const filteredSuppliers = suppliers.filter((s) => {
    const q = searchQuery.toLowerCase();
    return (
      s.name.toLowerCase().includes(q) ||
      (s.id && s.id.toLowerCase().includes(q)) ||
      (s.taxCode && s.taxCode.toLowerCase().includes(q))
    );
  });

  const canManageSuppliers = user?.role === 'PROCUREMENT' || user?.role === 'ADMIN';

  return (
    <div 
      style={{ maxWidth: '860.67px', margin: '0 auto', fontFamily: 'Inter, sans-serif' }}
      data-node-id="9:4479"
      data-testid="suppliers-view"
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
          Procurement · Flow C
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
              Suppliers
            </h1>
            <div style={{ fontSize: '14px', color: '#5a6472', lineHeight: '20px' }}>
              <p style={{ margin: '0 0 2px 0' }}>Reference data for the suppliers in this prototype, with the quotations and awards linked to each one.</p>
              <p style={{ margin: 0, color: '#8a929e' }}>Nothing here can be edited — supplier onboarding is out of scope.</p>
            </div>
          </div>

          {canManageSuppliers && (
            <button
              onClick={() => {
                setShowCreateForm(!showCreateForm);
                setFormMessage(null);
              }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                backgroundColor: showCreateForm ? '#ffffff' : '#3b45ad',
                border: showCreateForm ? '0.667px solid #e4e7ec' : 'none',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                color: showCreateForm ? '#5a6472' : '#ffffff',
                cursor: 'pointer',
                boxShadow: '0 1px 2px rgba(18, 22, 28, 0.04)',
              }}
              data-testid="add-supplier-toggle-btn"
            >
              {showCreateForm ? <X size={15} /> : <Plus size={15} />}
              <span>{showCreateForm ? 'Đóng form' : 'Thêm nhà cung cấp'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Global Form Message */}
      {formMessage && (
        <div
          style={{
            padding: '12px 16px',
            borderRadius: '6px',
            marginBottom: '16px',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: formMessage.type === 'success' ? '#e9f7ef' : '#fdecec',
            border: `0.667px solid ${formMessage.type === 'success' ? '#b6e2c7' : '#f4c2c2'}`,
            color: formMessage.type === 'success' ? '#16603b' : '#8e1e1e',
          }}
          data-testid="supplier-form-alert"
        >
          {formMessage.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          <span>{formMessage.text}</span>
        </div>
      )}

      {/* Create Supplier Form (Accordion / Panel) */}
      {showCreateForm && (
        <div
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #c3ccff',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '24px',
            boxShadow: '0 2px 8px rgba(18, 22, 28, 0.04)',
          }}
          data-testid="create-supplier-panel"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <Building2 size={18} color="#3b45ad" />
            <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: '#12161c' }}>
              Tạo mới nhà cung cấp (Suppliers)
            </h3>
          </div>

          <form onSubmit={handleCreateSupplier}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  Tên nhà cung cấp <span style={{ color: '#b32626' }}>*</span>
                </label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Công ty CP Thiết bị Tân Phát"
                  required
                  style={{
                    width: '100%',
                    height: '36px',
                    padding: '0 10px',
                    borderRadius: '4px',
                    border: '0.667px solid #e4e7ec',
                    fontSize: '13px',
                    boxSizing: 'border-box',
                  }}
                  data-testid="input-supplier-name"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  Mã số thuế (Tax Code)
                </label>
                <input
                  type="text"
                  value={newTaxCode}
                  onChange={(e) => setNewTaxCode(e.target.value)}
                  placeholder="e.g. 0108999888"
                  style={{
                    width: '100%',
                    height: '36px',
                    padding: '0 10px',
                    borderRadius: '4px',
                    border: '0.667px solid #e4e7ec',
                    fontSize: '13px',
                    boxSizing: 'border-box',
                  }}
                  data-testid="input-supplier-tax"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  Thông tin liên hệ / Email
                </label>
                <input
                  type="text"
                  value={newContact}
                  onChange={(e) => setNewContact(e.target.value)}
                  placeholder="contact@tanphat.vn"
                  style={{
                    width: '100%',
                    height: '36px',
                    padding: '0 10px',
                    borderRadius: '4px',
                    border: '0.667px solid #e4e7ec',
                    fontSize: '13px',
                    boxSizing: 'border-box',
                  }}
                  data-testid="input-supplier-contact"
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #e4e7ec',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: '#5a6472',
                  cursor: 'pointer',
                }}
              >
                Hủy
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#3b45ad',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#ffffff',
                  cursor: isSubmitting ? 'not-allowed' : 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
                data-testid="submit-supplier-btn"
              >
                {isSubmitting ? <Loader2 size={15} className="animate-spin" /> : <Plus size={15} />}
                <span>Lưu vào cơ sở dữ liệu</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Search Input Bar */}
      <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search 
            size={15} 
            color="#8a929e" 
            style={{ position: 'absolute', left: '12px', top: '10px' }} 
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm kiếm nhà cung cấp theo tên, mã số thuế hoặc ID..."
            style={{
              width: '100%',
              height: '36px',
              paddingLeft: '34px',
              paddingRight: '12px',
              borderRadius: '6px',
              border: '0.667px solid #e4e7ec',
              fontSize: '13px',
              outline: 'none',
              boxSizing: 'border-box',
              backgroundColor: '#ffffff',
            }}
            data-testid="supplier-search-input"
          />
        </div>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '32px 0', color: '#5a6472', fontSize: '13px' }} data-testid="suppliers-loading">
          <Loader2 size={16} className="animate-spin" />
          <span>Đang tải danh sách nhà cung cấp từ PostgreSQL...</span>
        </div>
      )}

      {error && (
        <div style={{ backgroundColor: '#fdecec', border: '0.667px solid #f4c2c2', borderRadius: '6px', padding: '14px 18px', marginBottom: '20px', color: '#8e1e1e', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
          <button 
            onClick={loadSuppliers} 
            style={{ marginLeft: 'auto', background: 'none', border: 'none', color: '#3b45ad', cursor: 'pointer', fontWeight: 600, fontSize: '12px' }}
          >
            Thử lại
          </button>
        </div>
      )}

      {/* Suppliers Cards List matching Figma 9:4488 */}
      {!loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }} data-testid="suppliers-list">
          {filteredSuppliers.length === 0 ? (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '0.667px solid #e4e7ec', padding: '36px', textAlign: 'center', color: '#8a929e', fontSize: '13px' }}>
              Không tìm thấy nhà cung cấp nào phù hợp.
            </div>
          ) : (
            filteredSuppliers.map((supplier) => {
              const isContracted = supplier.status === 'Contracted';
              return (
                <div
                  key={supplier.id}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '8px',
                    boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
                    overflow: 'hidden',
                  }}
                  data-testid={`supplier-card-${supplier.id}`}
                >
                  {/* Top Header Card Info (Figma 9:4490) */}
                  <div
                    style={{
                      borderBottom: '0.667px solid #e4e7ec',
                      padding: '16px 20px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                    }}
                  >
                    <div>
                      {/* Name + Badge + ID */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <span style={{ fontSize: '16px', fontWeight: 600, color: '#12161c' }}>
                          {supplier.name}
                        </span>

                        <span
                          style={{
                            backgroundColor: isContracted ? '#e9f7ef' : '#fdf4e3',
                            border: `0.667px solid ${isContracted ? '#b6e2c7' : '#f2ddad'}`,
                            borderRadius: '4px',
                            padding: '1px 6px',
                            fontSize: '11px',
                            fontWeight: 500,
                            color: isContracted ? '#16603b' : '#7a5209',
                            lineHeight: '16px',
                          }}
                        >
                          {supplier.status}
                        </span>

                        <span style={{ fontSize: '11px', color: '#8a929e' }}>
                          {supplier.id}
                        </span>
                      </div>

                      {/* Notes / Subtitle */}
                      <div style={{ fontSize: '14px', color: '#5a6472', marginBottom: '6px' }}>
                        {supplier.notes}
                      </div>

                      {/* Certifications / Tax */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: '#5a6472' }}>
                        {supplier.certifications && supplier.certifications.length > 0 ? (
                          supplier.certifications.map((cert, idx) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <ShieldCheck size={14} color="#5a6472" />
                              <span>{cert}</span>
                            </div>
                          ))
                        ) : (
                          <div style={{ color: '#8a929e' }}>Chưa có chứng chỉ tiêu chuẩn</div>
                        )}
                        {supplier.taxCode && (
                          <div style={{ color: '#8a929e' }}>· MST: {supplier.taxCode}</div>
                        )}
                      </div>
                    </div>

                    {/* Right side stats: Rating, On-time, Country, Terms + Detail Action */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                      <div style={{ display: 'flex', gap: '20px', textAlign: 'left' }}>
                        <div>
                          <div style={{ fontSize: '11px', color: '#8a929e', letterSpacing: '0.275px' }}>Rating</div>
                          <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c' }}>{supplier.rating || '4.5'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '11px', color: '#8a929e', letterSpacing: '0.275px' }}>On time</div>
                          <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c' }}>{supplier.onTime || '95%'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '11px', color: '#8a929e', letterSpacing: '0.275px' }}>Country</div>
                          <div style={{ fontSize: '14px', color: '#12161c' }}>{supplier.country || 'Vietnam'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '11px', color: '#8a929e', letterSpacing: '0.275px' }}>Terms</div>
                          <div style={{ fontSize: '14px', color: '#12161c' }}>{supplier.terms || 'Net 30'}</div>
                        </div>
                      </div>

                      <button
                        onClick={() => handleOpenDetail(supplier.id)}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          backgroundColor: '#f8fafc',
                          border: '0.667px solid #e4e7ec',
                          borderRadius: '4px',
                          padding: '6px 10px',
                          fontSize: '12px',
                          fontWeight: 500,
                          color: '#3b45ad',
                          cursor: 'pointer',
                        }}
                        data-testid={`view-supplier-detail-btn-${supplier.id}`}
                      >
                        <span>Chi tiết</span>
                        <ChevronRight size={13} />
                      </button>
                    </div>
                  </div>

                  {/* Bottom 3 Columns (Figma 9:4516): Quotations, Awarded, Anomaly flags */}
                  <div
                    style={{
                      padding: '14px 20px',
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr 1fr',
                      gap: '24px',
                      backgroundColor: '#fafbfc',
                      fontSize: '12px',
                    }}
                  >
                    {/* Column 1: Quotations on file */}
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', textTransform: 'uppercase', marginBottom: '6px' }}>
                        Quotations on file ({supplier.quotationsOnFile ? supplier.quotationsOnFile.length : 0})
                      </div>
                      {supplier.quotationsOnFile && supplier.quotationsOnFile.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                          {supplier.quotationsOnFile.map((q, idx) => (
                            <div key={idx} style={{ color: '#5a6472', lineHeight: '16px' }}>
                              {q}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ color: '#8a929e' }}>Chưa có báo giá nào</div>
                      )}
                    </div>

                    {/* Column 2: Awarded */}
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', textTransform: 'uppercase', marginBottom: '6px' }}>
                        Awarded ({supplier.awarded ? supplier.awarded.length : 0})
                      </div>
                      {supplier.awarded && supplier.awarded.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                          {supplier.awarded.map((aw, idx) => (
                            <div key={idx} style={{ color: '#12161c', lineHeight: '16px' }}>
                              {aw}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ color: '#8a929e' }}>None.</div>
                      )}
                    </div>

                    {/* Column 3: Anomaly flags */}
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', textTransform: 'uppercase', marginBottom: '6px' }}>
                        Anomaly flags ({supplier.anomalyFlags ? supplier.anomalyFlags.length : 0})
                      </div>
                      {supplier.anomalyFlags && supplier.anomalyFlags.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                          {supplier.anomalyFlags.map((flag, idx) => (
                            <div key={idx} style={{ color: '#8e1e1e', lineHeight: '16px' }}>
                              {flag}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ color: '#8a929e' }}>None.</div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Supplier Detail Modal */}
      {selectedSupplier && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(18, 22, 28, 0.4)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
          }}
          data-testid="supplier-detail-modal"
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '8px',
              maxWidth: '560px',
              width: '100%',
              boxShadow: '0 10px 25px rgba(0,0,0,0.15)',
              overflow: 'hidden',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            {/* Modal Header */}
            <div
              style={{
                padding: '16px 20px',
                borderBottom: '0.667px solid #e4e7ec',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Building2 size={18} color="#3b45ad" />
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#12161c' }}>
                  Hồ sơ nhà cung cấp (Supplier Detail)
                </h3>
              </div>
              <button
                onClick={() => setSelectedSupplier(null)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#8a929e' }}
                data-testid="close-supplier-detail-btn"
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '20px' }}>
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '18px', fontWeight: 700, color: '#12161c', marginBottom: '4px' }}>
                  {selectedSupplier.name}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#5a6472' }}>
                  <span style={{ fontWeight: 600, color: '#3b45ad' }}>Mã đối tác: {selectedSupplier.id}</span>
                  {selectedSupplier.taxCode && <span>· MST: {selectedSupplier.taxCode}</span>}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', backgroundColor: '#f8fafc', padding: '14px', borderRadius: '6px', marginBottom: '16px' }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#8a929e' }}>Quốc gia</div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>{selectedSupplier.country || 'Việt Nam'}</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#8a929e' }}>Điều khoản thanh toán</div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>{selectedSupplier.terms || 'Net 30'}</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#8a929e' }}>Điểm tín nhiệm (Rating)</div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>{selectedSupplier.rating || 4.5} / 5.0</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#8a929e' }}>Tỷ lệ giao đúng hạn</div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: '#12161c' }}>{selectedSupplier.onTime || '95%'}</div>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#5a6472', marginBottom: '4px' }}>
                  Thông tin liên hệ &amp; ghi chú
                </div>
                <div style={{ fontSize: '13px', color: '#12161c' }}>
                  {selectedSupplier.contact || selectedSupplier.notes || 'Chưa có ghi chú liên hệ bổ sung.'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#5a6472', marginBottom: '4px' }}>
                  Số báo giá đã ghi nhận
                </div>
                <div style={{ fontSize: '13px', color: '#12161c' }}>
                  {selectedSupplier.quotationsOnFile ? selectedSupplier.quotationsOnFile.length : 0} báo giá trong hệ thống
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div
              style={{
                padding: '12px 20px',
                borderTop: '0.667px solid #e4e7ec',
                display: 'flex',
                justifyContent: 'flex-end',
                backgroundColor: '#fafbfc',
              }}
            >
              <button
                onClick={() => setSelectedSupplier(null)}
                style={{
                  padding: '7px 16px',
                  backgroundColor: '#3b45ad',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#ffffff',
                  cursor: 'pointer',
                }}
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
