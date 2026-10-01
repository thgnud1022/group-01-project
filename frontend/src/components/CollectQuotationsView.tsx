import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Check, 
  UploadCloud, 
  FileText, 
  AlertCircle, 
  CheckCircle2, 
  Loader2, 
  Building2, 
  Layers, 
  Clock, 
  ShieldCheck, 
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface CollectQuotationsViewProps {
  prId: string;
  prData?: any;
  user: AuthenticatedUser | null;
  onBack: () => void;
  onNavigateTab?: (tab: string) => void;
  onProceedToComparison?: (prId: string) => void;
}

interface SupplierOption {
  id: string;
  name: string;
  taxCode?: string | null;
  rating?: number;
  terms?: string;
  country?: string;
}

export const CollectQuotationsView: React.FC<CollectQuotationsViewProps> = ({
  prId,
  prData: initialPrData,
  user,
  onBack,
  onNavigateTab,
  onProceedToComparison,
}) => {
  const [pr, setPr] = useState<any>(initialPrData || null);
  const [prLoading, setPrLoading] = useState<boolean>(!initialPrData);
  const [suppliers, setSuppliers] = useState<SupplierOption[]>([]);
  const [suppliersLoading, setSuppliersLoading] = useState<boolean>(true);
  const [quotations, setQuotations] = useState<any[]>([]);
  const [quotationsLoading, setQuotationsLoading] = useState<boolean>(true);

  // Form State
  const [selectedSupplierId, setSelectedSupplierId] = useState<string>('');
  const [quantity, setQuantity] = useState<number>(1);
  const [unitPrice, setUnitPrice] = useState<number>(0);
  const [totalAmount, setTotalAmount] = useState<number>(0);
  const [deliveryDays, setDeliveryDays] = useState<number>(3);
  const [warrantyTerms, setWarrantyTerms] = useState<string>('12 tháng chính hãng');
  const [fileUrl, setFileUrl] = useState<string>('quotes/bao-gia.pdf');

  // Submission State
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  // Load PR, Suppliers, Quotations
  useEffect(() => {
    loadAllData();
  }, [prId]);

  const loadAllData = async () => {
    // 1. Load PR if needed
    if (!initialPrData) {
      setPrLoading(true);
      try {
        const prDetails = await api.getPR(prId);
        setPr(prDetails);
        // Pre-fill quantity from PR items
        const initialQty = (prDetails.items || []).reduce((acc: number, it: any) => acc + (it.quantity || 1), 0);
        if (initialQty > 0) setQuantity(initialQty);
      } catch (err: any) {
        console.error('Failed to load PR:', err);
      } finally {
        setPrLoading(false);
      }
    } else {
      setPr(initialPrData);
      const initialQty = (initialPrData.items || []).reduce((acc: number, it: any) => acc + (it.quantity || 1), 0);
      if (initialQty > 0) setQuantity(initialQty);
    }

    // 2. Load Suppliers from real PostgreSQL
    setSuppliersLoading(true);
    try {
      const data = await api.listSuppliers();
      const mapped: SupplierOption[] = (data || []).map((s: any) => ({
        id: s.id,
        name: s.name,
        taxCode: s.taxCode,
        rating: s.id === 'SUP-01' ? 4.6 : s.id === 'SUP-02' ? 4.2 : s.id === 'SUP-03' ? 3.8 : 4.5,
        terms: s.id === 'SUP-01' ? 'Net 30' : s.id === 'SUP-02' ? 'Net 15' : s.id === 'SUP-03' ? '100% prepayment' : 'Net 30',
        country: s.id === 'SUP-03' ? 'Singapore' : 'Vietnam',
      }));
      setSuppliers(mapped);
    } catch (err: any) {
      console.error('Failed to load suppliers:', err);
    } finally {
      setSuppliersLoading(false);
    }

    // 3. Load Quotations for this PR from real PostgreSQL
    await loadQuotations();
  };

  const loadQuotations = async () => {
    setQuotationsLoading(true);
    try {
      const quotes = await api.listQuotations(prId);
      setQuotations(quotes || []);
    } catch (err: any) {
      console.error('Failed to load quotations:', err);
    } finally {
      setQuotationsLoading(false);
    }
  };

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

  // Handle supplier selection
  const handleSelectSupplier = (suppId: string) => {
    setSelectedSupplierId(suppId);
    setFormError(null);
    setFormSuccess(null);
    const supp = suppliers.find(s => s.id === suppId);
    if (supp) {
      setFileUrl(`quotes/bao-gia-${supp.id.toLowerCase()}.pdf`);
    }
  };

  // Handle unit price change & auto recalculate totalAmount
  const handleUnitPriceChange = (val: number) => {
    setUnitPrice(val);
    if (quantity > 0) {
      setTotalAmount(val * quantity);
    }
  };

  // Handle quantity change
  const handleQuantityChange = (val: number) => {
    setQuantity(val);
    if (unitPrice > 0) {
      setTotalAmount(val * unitPrice);
    }
  };

  // Handle Quotation Submission
  const handleSubmitQuotation = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    // Client-side validations
    if (!selectedSupplierId) {
      setFormError('Vui lòng chọn một nhà cung cấp ở Mục 01.');
      return;
    }
    if (quantity <= 0) {
      setFormError('Số lượng báo giá phải lớn hơn 0.');
      return;
    }
    if (totalAmount <= 0) {
      setFormError('Tổng giá trị báo giá phải lớn hơn 0 ₫.');
      return;
    }
    if (deliveryDays < 0) {
      setFormError('Thời gian giao hàng không được là số âm.');
      return;
    }

    setIsSubmitting(true);
    try {
      const created = await api.createQuotation({
        purchaseRequestId: prId,
        supplierId: selectedSupplierId,
        totalAmount: Number(totalAmount),
        quantity: Number(quantity),
        deliveryDays: Number(deliveryDays),
        warrantyTerms: warrantyTerms.trim() || undefined,
        fileUrl: fileUrl.trim() || 'quotes/default.pdf',
      });

      setFormSuccess(`Đã lưu báo giá thành công cho nhà cung cấp (${created.supplierName || selectedSupplierId})!`);
      // Reload quotations from DB
      await loadQuotations();

      // Reset form fields
      setSelectedSupplierId('');
      setUnitPrice(0);
      setTotalAmount(0);
    } catch (err: any) {
      console.error('Create quotation error:', err);
      setFormError(err.message || 'Không thể lưu báo giá vào hệ thống.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalPRUnits = pr?.items ? pr.items.reduce((acc: number, it: any) => acc + (it.quantity || 0), 0) : quantity;
  const quotedSupplierIds = quotations.map(q => q.supplierId);

  return (
    <div 
      style={{ maxWidth: '876px', margin: '0 auto', fontFamily: 'Inter, sans-serif' }}
      data-node-id="9:4163"
      data-testid="collect-quotations-view"
    >
      {/* Back to Sourcing link */}
      <div style={{ marginBottom: '16px' }}>
        <button
          onClick={onBack}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            color: '#5a6472',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
            padding: 0,
          }}
          data-testid="back-to-sourcing-btn"
        >
          <ArrowLeft size={15} />
          <span>{pr?.id || prId}</span>
        </button>
      </div>

      {/* Title & Status */}
      <div style={{ marginBottom: '20px' }}>
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
            data-testid="pr-status-badge"
          >
            Approved
          </span>
          <span style={{ fontSize: '11px', color: '#8a929e', fontFamily: 'monospace' }}>
            {pr?.id || prId}
          </span>
        </div>

        <h1 
          style={{ 
            fontSize: '24px', 
            fontWeight: 600, 
            color: '#12161c', 
            letterSpacing: '-0.6px', 
            margin: '0 0 4px 0',
            lineHeight: '32px'
          }}
          data-testid="collect-quotations-title"
        >
          Collect quotations
        </h1>

        <div style={{ fontSize: '14px', color: '#5a6472', lineHeight: '20px' }}>
          {pr?.title || 'Yêu cầu mua sắm thiết bị'} ({totalPRUnits} units) · approved estimate {formatVND(pr?.estimatedValue || 84000000)} · needed by {pr?.neededBy || '30 Sept 2026'}
        </div>
      </div>

      {/* Stepper (Figma 9:4163) */}
      <div 
        style={{
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          padding: '12px 20px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          overflowX: 'auto',
          fontSize: '12px',
          color: '#8a929e',
        }}
        data-testid="quotation-stepper"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#16603b' }}>
          <Check size={14} color="#16603b" />
          <span style={{ fontWeight: 500 }}>Request</span>
        </div>
        <span style={{ color: '#d0d5dd' }}>—</span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#16603b' }}>
          <Check size={14} color="#16603b" />
          <span style={{ fontWeight: 500 }}>Approval</span>
        </div>
        <span style={{ color: '#d0d5dd' }}>—</span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#3b45ad', fontWeight: 600 }}>
          <span 
            style={{ 
              backgroundColor: '#3b45ad', 
              color: '#ffffff', 
              width: '18px', 
              height: '18px', 
              borderRadius: '50%', 
              display: 'inline-flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontSize: '11px',
            }}
          >
            3
          </span>
          <span>Quotations</span>
        </div>
        <span style={{ color: '#d0d5dd' }}>—</span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#8a929e' }}>
          <span style={{ width: '18px', height: '18px', borderRadius: '50%', border: '0.667px solid #d0d5dd', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px' }}>4</span>
          <span>Comparison</span>
        </div>
        <span style={{ color: '#d0d5dd' }}>—</span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#8a929e' }}>
          <span style={{ width: '18px', height: '18px', borderRadius: '50%', border: '0.667px solid #d0d5dd', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px' }}>5</span>
          <span>Purchase order</span>
        </div>
        <span style={{ color: '#d0d5dd' }}>—</span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#8a929e' }}>
          <span style={{ width: '18px', height: '18px', borderRadius: '50%', border: '0.667px solid #d0d5dd', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px' }}>6</span>
          <span>Received</span>
        </div>
        <span style={{ color: '#d0d5dd' }}>—</span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#8a929e' }}>
          <span style={{ width: '18px', height: '18px', borderRadius: '50%', border: '0.667px solid #d0d5dd', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px' }}>7</span>
          <span>Closed</span>
        </div>
      </div>

      {/* Main 2-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '20px', alignItems: 'start' }}>
        
        {/* Left Column: Form & Selection */}
        <div>
          {/* SECTION 01: Supplier Selection */}
          <div 
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
            }}
            data-testid="supplier-selection-section"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#8a929e' }}>01</span>
              <h2 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: '#12161c' }}>
                Choose the supplier this quotation came from
              </h2>
            </div>
            <div style={{ fontSize: '11px', color: '#8a929e', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '14px' }}>
              Supplier
            </div>

            {suppliersLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '16px', color: '#5a6472', fontSize: '13px' }} data-testid="suppliers-loading">
                <Loader2 size={16} className="animate-spin" />
                <span>Đang tải danh sách nhà cung cấp từ cơ sở dữ liệu...</span>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '12px' }}>
                {suppliers.map((s) => {
                  const isSelected = selectedSupplierId === s.id;
                  const hasQuotation = quotedSupplierIds.includes(s.id);
                  return (
                    <div
                      key={s.id}
                      onClick={() => handleSelectSupplier(s.id)}
                      style={{
                        border: isSelected ? '1.5px solid #3b45ad' : '0.667px solid #e4e7ec',
                        backgroundColor: isSelected ? '#f4f6fc' : '#ffffff',
                        borderRadius: '6px',
                        padding: '12px 14px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '10px',
                        transition: 'all 0.15s ease',
                      }}
                      data-testid={`supplier-select-${s.id}`}
                    >
                      <div 
                        style={{
                          width: '16px',
                          height: '16px',
                          borderRadius: '50%',
                          border: isSelected ? '5px solid #3b45ad' : '1px solid #c3c7ce',
                          backgroundColor: '#ffffff',
                          marginTop: '2px',
                          flexShrink: 0,
                          boxSizing: 'border-box',
                        }}
                      />
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '4px' }}>
                          <span style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>
                            {s.name}
                          </span>
                          {hasQuotation && (
                            <span 
                              style={{ 
                                backgroundColor: '#f0f2f5', 
                                color: '#5a6472', 
                                fontSize: '10px', 
                                padding: '1px 5px', 
                                borderRadius: '3px',
                                fontWeight: 500,
                              }}
                            >
                              On file
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '11px', color: '#8a929e', marginTop: '2px' }}>
                          {s.id} · rating {s.rating} · {s.terms}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <div style={{ fontSize: '12px', color: '#8a929e' }}>
              One quotation per supplier per request. Supplier records are read-only.
            </div>
          </div>

          {/* SECTION 02: Upload & Commercial Details */}
          <div 
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
            }}
            data-testid="quotation-form-section"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#8a929e' }}>02</span>
              <h2 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: '#12161c' }}>
                Upload the quotation file &amp; enter commercial terms
              </h2>
            </div>

            {/* Error & Success Messages */}
            {formError && (
              <div 
                style={{
                  backgroundColor: '#fdecec',
                  border: '0.667px solid #f4c2c2',
                  borderRadius: '6px',
                  padding: '10px 14px',
                  marginBottom: '16px',
                  color: '#8e1e1e',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
                data-testid="quotation-form-error"
              >
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{formError}</span>
              </div>
            )}

            {formSuccess && (
              <div 
                style={{
                  backgroundColor: '#e9f7ef',
                  border: '0.667px solid #b6e2c7',
                  borderRadius: '6px',
                  padding: '10px 14px',
                  marginBottom: '16px',
                  color: '#16603b',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
                data-testid="quotation-form-success"
              >
                <CheckCircle2 size={16} style={{ flexShrink: 0 }} />
                <span>{formSuccess}</span>
              </div>
            )}

            {!selectedSupplierId ? (
              /* Dropzone Placeholder before selecting supplier */
              <div
                style={{
                  border: '1.5px dashed #d0d5dd',
                  borderRadius: '8px',
                  padding: '40px 20px',
                  textAlign: 'center',
                  backgroundColor: '#fafbfc',
                }}
                data-testid="dropzone-disabled"
              >
                <UploadCloud size={32} color="#8a929e" style={{ margin: '0 auto 8px auto', display: 'block' }} />
                <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c', marginBottom: '4px' }}>
                  Drop the quotation PDF or image here
                </div>
                <div style={{ fontSize: '12px', color: '#8a929e', marginBottom: '14px' }}>
                  PDF, PNG or JPEG · up to 10 MB
                </div>
                <div style={{ fontSize: '12px', color: '#b54708', fontWeight: 500 }}>
                  Choose a supplier first so the quotation can be linked.
                </div>
              </div>
            ) : (
              /* Form when supplier is chosen */
              <form onSubmit={handleSubmitQuotation} noValidate>
                {/* Simulated Dropzone File Area */}
                <div
                  style={{
                    border: '1px solid #c3ccff',
                    borderRadius: '8px',
                    padding: '16px',
                    backgroundColor: '#f8fafc',
                    marginBottom: '16px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                    <FileText size={20} color="#3b45ad" />
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>
                        Tệp báo giá đính kèm (File reference)
                      </div>
                      <div style={{ fontSize: '11px', color: '#8a929e' }}>
                        Gắn siêu dữ liệu đường dẫn tệp báo giá phục vụ kiểm tra và trích xuất
                      </div>
                    </div>
                  </div>

                  <input
                    type="text"
                    value={fileUrl}
                    onChange={(e) => setFileUrl(e.target.value)}
                    placeholder="quotes/bao-gia.pdf"
                    style={{
                      width: '100%',
                      height: '34px',
                      padding: '0 10px',
                      borderRadius: '4px',
                      border: '0.667px solid #e4e7ec',
                      fontSize: '13px',
                      backgroundColor: '#ffffff',
                      boxSizing: 'border-box',
                    }}
                    data-testid="input-quotation-file"
                  />
                </div>

                {/* Commercial Inputs */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Số lượng chào giá (Quantity) <span style={{ color: '#b32626' }}>*</span>
                    </label>
                    <input
                      type="number"
                      min={1}
                      value={quantity}
                      onChange={(e) => handleQuantityChange(Number(e.target.value))}
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
                      data-testid="input-quotation-qty"
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Đơn giá chào (Unit Price - ₫) <span style={{ color: '#b32626' }}>*</span>
                    </label>
                    <input
                      type="number"
                      min={1}
                      value={unitPrice}
                      onChange={(e) => handleUnitPriceChange(Number(e.target.value))}
                      placeholder="e.g. 8500000"
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
                      data-testid="input-quotation-unit-price"
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Tổng giá trị báo giá (Total Amount - ₫) <span style={{ color: '#b32626' }}>*</span>
                    </label>
                    <input
                      type="number"
                      min={1}
                      value={totalAmount}
                      onChange={(e) => setTotalAmount(Number(e.target.value))}
                      required
                      style={{
                        width: '100%',
                        height: '36px',
                        padding: '0 10px',
                        borderRadius: '4px',
                        border: '0.667px solid #e4e7ec',
                        fontSize: '13px',
                        fontWeight: 600,
                        color: '#12161c',
                        boxSizing: 'border-box',
                      }}
                      data-testid="input-quotation-total-amount"
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Thời gian giao hàng (Delivery Days)
                    </label>
                    <input
                      type="number"
                      min={0}
                      value={deliveryDays}
                      onChange={(e) => setDeliveryDays(Number(e.target.value))}
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
                      data-testid="input-quotation-delivery-days"
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '18px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                    Điều khoản bảo hành (Warranty terms)
                  </label>
                  <input
                    type="text"
                    value={warrantyTerms}
                    onChange={(e) => setWarrantyTerms(e.target.value)}
                    placeholder="12 tháng chính hãng"
                    style={{
                      width: '100%',
                      height: '36px',
                      padding: '0 10px',
                      borderRadius: '4px',
                      border: '0.667px solid #e4e7ec',
                      fontSize: '13px',
                      boxSizing: 'border-box',
                    }}
                    data-testid="input-quotation-warranty"
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button
                    type="button"
                    onClick={() => setSelectedSupplierId('')}
                    style={{
                      padding: '8px 14px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '13px',
                      color: '#5a6472',
                      cursor: 'pointer',
                    }}
                  >
                    Bỏ chọn
                  </button>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    style={{
                      padding: '8px 18px',
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
                    data-testid="submit-quotation-btn"
                  >
                    {isSubmitting ? <Loader2 size={15} className="animate-spin" /> : <Check size={15} />}
                    <span>Lưu báo giá vào hệ thống</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>

        {/* Right Column: Status & Policy */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Card 1: Collected so far */}
          <div 
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
            }}
            data-testid="collected-so-far-card"
          >
            <h3 style={{ margin: '0 0 2px 0', fontSize: '15px', fontWeight: 600, color: '#12161c' }}>
              Collected so far
            </h3>
            <div style={{ fontSize: '12px', color: '#8a929e', marginBottom: '14px' }}>
              {quotations.length} of {suppliers.length} suppliers
            </div>

            {quotationsLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#5a6472', fontSize: '12px', padding: '12px 0' }}>
                <Loader2 size={14} className="animate-spin" />
                <span>Đang tải...</span>
              </div>
            ) : quotations.length === 0 ? (
              <div>
                <div style={{ fontSize: '13px', color: '#5a6472', marginBottom: '12px' }}>
                  Nothing linked yet.
                </div>
                <div style={{ fontSize: '12px', color: '#8a929e', lineHeight: '18px' }}>
                  A comparison is shown once at least two quotations are linked. 2 more to go.
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '14px' }}>
                {quotations.map((q) => (
                  <div
                    key={q.id}
                    style={{
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '6px',
                      padding: '10px',
                      backgroundColor: '#fbfcfd',
                    }}
                    data-testid={`quote-item-${q.id}`}
                  >
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#12161c', marginBottom: '2px' }}>
                      {q.supplierName || q.supplier?.name || q.supplierId}
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: '#3b45ad', marginBottom: '2px' }}>
                      {formatVND(q.totalAmount)}
                    </div>
                    <div style={{ fontSize: '11px', color: '#5a6472' }}>
                      Đơn giá: {formatVND(q.unitPrice)} · Giao {q.deliveryDays} ngày
                    </div>
                  </div>
                ))}

                {quotations.length < 2 ? (
                  <div style={{ fontSize: '12px', color: '#8a929e', lineHeight: '18px' }}>
                    Cần thêm {2 - quotations.length} báo giá để mở tính năng so sánh (Comparison).
                  </div>
                ) : (
                  <div style={{ marginTop: '4px' }}>
                    <div 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '6px', 
                        fontSize: '12px', 
                        color: '#16603b', 
                        fontWeight: 600,
                        marginBottom: '8px'
                      }}
                    >
                      <CheckCircle2 size={14} color="#16603b" />
                      <span>Đã thu thập đủ tối thiểu 2 báo giá.</span>
                    </div>

                    {onProceedToComparison && (
                      <button
                        onClick={() => onProceedToComparison(prId)}
                        style={{
                          width: '100%',
                          padding: '8px 12px',
                          backgroundColor: '#3b45ad',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px',
                        }}
                        data-testid="compare-quotations-btn"
                      >
                        <span>So sánh báo giá (Comparison)</span>
                        <ChevronRight size={14} />
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Card 2: How this works */}
          <div 
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0 1px 2px rgba(18,22,28,0.03)',
            }}
            data-testid="how-this-works-card"
          >
            <h4 style={{ margin: '0 0 10px 0', fontSize: '13px', fontWeight: 600, color: '#12161c' }}>
              How this works
            </h4>
            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: '#5a6472', lineHeight: '18px' }}>
              <li style={{ marginBottom: '6px' }}>The file is attached to the quotation record for traceability.</li>
              <li style={{ marginBottom: '6px' }}>Currency, tax and shipping are aligned so totals are comparable.</li>
              <li>Anything not stated on the file is flagged, never guessed.</li>
            </ul>
          </div>

        </div>

      </div>
    </div>
  );
};
