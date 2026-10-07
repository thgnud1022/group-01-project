import React, { useState, useMemo, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  Plus, 
  Trash2, 
  Check, 
  X, 
  AlertCircle,
  Settings,
  ArrowRight,
  RefreshCw,
  Sliders
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface LineItem {
  id: string;
  itemName: string;
  quantity: number;
  estimatedUnitPrice: number;
}

interface NewRequestViewProps {
  user: AuthenticatedUser | null;
  onSuccess: (createdPr: any) => void;
  onSaveDraft?: (draftPr: any) => void;
  onErrorState?: (errorInfo: any) => void;
  onCancel?: () => void;
}

export const NewRequestView: React.FC<NewRequestViewProps> = ({
  user,
  onSuccess,
  onSaveDraft,
  onErrorState,
  onCancel,
}) => {
  // AI Note state
  const [noteText, setNoteText] = useState(
    'e.g. need 15 laptops 32gb ram at 18.5m each for eng onboarding, plus 15 usb-c docks at 1.5m'
  );
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  // Form Fields (Figma 9:645)
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [department, setDepartment] = useState(user?.departmentId ? (user.departmentId.includes('IT') ? 'Engineering' : 'People') : '');
  const [costCentre, setCostCentre] = useState('');
  const [requiredBy, setRequiredBy] = useState('');
  const [deliveryLocation, setDeliveryLocation] = useState('');
  const [justification, setJustification] = useState('');

  // Calendar popup state
  const [showCalendar, setShowCalendar] = useState(false);
  const [calViewYear, setCalViewYear] = useState(() => new Date().getFullYear());
  const [calViewMonth, setCalViewMonth] = useState(() => new Date().getMonth());
  const calendarRef = useRef<HTMLDivElement>(null);

  // Close calendar when clicking outside
  useEffect(() => {
    if (!showCalendar) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (calendarRef.current && !calendarRef.current.contains(e.target as Node)) {
        setShowCalendar(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showCalendar]);

  const handleCalendarSelect = (day: number) => {
    const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    setRequiredBy(`${day} ${monthNames[calViewMonth]} ${calViewYear}`);
    setShowCalendar(false);
  };

  const getCalendarDays = (year: number, month: number) => {
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();
    const days: { day: number; type: 'prev' | 'current' | 'next' }[] = [];
    for (let i = firstDay - 1; i >= 0; i--) days.push({ day: daysInPrevMonth - i, type: 'prev' });
    for (let i = 1; i <= daysInMonth; i++) days.push({ day: i, type: 'current' });
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) days.push({ day: i, type: 'next' });
    return days;
  };

  // Line Items state
  const [items, setItems] = useState<LineItem[]>([
    { id: '1', itemName: '', quantity: 1, estimatedUnitPrice: 0 },
  ]);

  // Advisory suggestions dismissal
  const [costCentreDismissed, setCostCentreDismissed] = useState(false);
  const [locationDismissed, setLocationDismissed] = useState(false);

  // Submitting state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Calculate estimated total
  const estimatedTotal = useMemo(() => {
    return items.reduce((sum, it) => sum + (Number(it.quantity) || 0) * (Number(it.estimatedUnitPrice) || 0), 0);
  }, [items]);

  // Checklist verification
  const checklist = {
    title: !!title.trim(),
    category: !!category.trim(),
    department: !!department.trim(),
    costCentre: !!costCentre.trim(),
    requiredBy: !!requiredBy.trim(),
    deliveryLocation: !!deliveryLocation.trim(),
    justification: !!justification.trim(),
    lineItemsPriced: items.length > 0 && items.every((it) => it.itemName.trim() && it.quantity > 0 && it.estimatedUnitPrice > 0),
  };

  const missingFieldsCount = Object.values(checklist).filter((v) => !v).length;

  // AI Structure this note — step 1: only show preview, do NOT touch form yet
  const [aiPreview, setAiPreview] = useState<any | null>(null);

  const handleStructureNote = async () => {
    const defaultQuery = 'Cần 15 laptop Dell XPS 15 32GB RAM cho nhân viên mới Engineering và 15 dock chuyển đổi USB-C';
    if (!noteText.trim() || noteText.startsWith('e.g.')) {
      setNoteText(defaultQuery);
    }
    const query = (!noteText.trim() || noteText.startsWith('e.g.')) ? defaultQuery : noteText;

    setIsAiLoading(true);
    setAiError(null);
    setAiPreview(null);
    try {
      const result = await api.standardizePR(query);
      // Store preview but do NOT apply to form yet
      setAiPreview({
        title: result.title || '',
        category: result.category || 'not determined',
        items: result.items && result.items.length > 0
          ? result.items.map((it: any, idx: number) => ({
              id: String(idx + 1),
              itemName: it.itemName,
              quantity: Number(it.quantity) || 1,
              estimatedUnitPrice: Number(it.estimatedUnitPrice) || 0,
            }))
          : [],
        warnings: result.warnings || [],
      });
    } catch (err: any) {
      setAiError(err.message || 'Không thể chuẩn hóa ghi chú.');
    } finally {
      setIsAiLoading(false);
    }
  };

  // AI step 2: apply preview to form fields
  const handleApplyToForm = () => {
    if (!aiPreview) return;
    if (aiPreview.title) setTitle(aiPreview.title);
    if (!category) setCategory('IT Equipment');
    if (!department) setDepartment('Engineering');
    if (aiPreview.items && aiPreview.items.length > 0) {
      setItems(aiPreview.items);
    }
    setAiPreview(null);
  };

  const handleDiscardPreview = () => setAiPreview(null);

  const handleAddItem = () => {
    setItems((prev) => [
      ...prev,
      { id: String(Date.now()), itemName: '', quantity: 1, estimatedUnitPrice: 0 },
    ]);
  };

  const handleRemoveItem = (id: string) => {
    if (items.length <= 1) return;
    setItems((prev) => prev.filter((it) => it.id !== id));
  };

  const handleUpdateItem = (id: string, field: keyof LineItem, value: any) => {
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, [field]: value } : it))
    );
  };

  // Submit to real backend
  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    // Map department to departmentId
    let deptId = 'DEPT-IT';
    if (department === 'People' || department === 'Operations') {
      deptId = 'DEPT-HR';
    }

    try {
      const response = await api.createPR({
        departmentId: deptId,
        title: title || 'Laptops for engineering onboarding',
        items: items.map((it) => ({
          itemName: it.itemName || 'Thiết bị tiêu chuẩn',
          quantity: Number(it.quantity) || 1,
          estimatedUnitPrice: Number(it.estimatedUnitPrice) || 1000000,
        })),
      });

      onSuccess(response);
    } catch (err: any) {
      setSubmitError(err.message || 'Submission failed');
      if (onErrorState) {
        onErrorState({
          id: 'PR-2026-034',
          title: title || 'Server rack rails and cable management',
          creatorName: user?.name || 'Trương Bảo Long',
          departmentName: department || 'Engineering',
          category: category || 'IT Equipment',
          costCentre: costCentre || 'CC-ENG-2200',
          requiredBy: requiredBy || '25 Sept 2026',
          deliveryLocation: deliveryLocation || 'HQ Hanoi · Floor 6 · Goods-in',
          justification: justification || 'Required for the rack consolidation in September.',
          items: items,
          estimatedTotal: estimatedTotal || 14400000,
          errorMessage: err.message,
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Save as draft handler
  const handleSaveDraft = () => {
    const draftPr = {
      id: 'PR-2026-035',
      title: title || 'Whiteboard markers and erasers',
      status: 'DRAFT',
      creatorName: user?.name || 'Đặng Khánh Vy',
      departmentName: department || 'People',
      category: category || 'Office Supplies',
      costCentre: costCentre || null,
      requiredBy: requiredBy || null,
      deliveryLocation: deliveryLocation || null,
      justification: justification || 'Meeting rooms are out of markers.',
      createdAt: '25 Aug 2026 · 15:30',
      lastUpdated: '25 Aug 2026 · 15:30',
      items: items.length > 0 && items[0].itemName ? items : [
        { id: '1', itemName: 'Whiteboard marker, assorted', quantity: 60, estimatedUnitPrice: 28000 }
      ],
      estimatedValue: estimatedTotal > 0 ? estimatedTotal : 1680000,
    };
    if (onSaveDraft) {
      onSaveDraft(draftPr);
    }
  };

  return (
    <div style={{ maxWidth: '860px', margin: '0 auto' }} data-node-id="9:645" data-testid="new-request-view">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
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
          Employee · Flow A
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
          New purchase request
        </h1>
        <p style={{ margin: 0, fontSize: '14px', color: '#5a6472', lineHeight: '20px' }}>
          Describe what you need. The assistant can restructure your note and offer values for missing fields — you decide what goes on the request.
        </p>
      </div>

      {submitError && (
        <div
          style={{
            marginBottom: '16px',
            padding: '12px 16px',
            borderRadius: '6px',
            backgroundColor: '#fdecec',
            border: '0.667px solid #f4c2c2',
            color: '#8e1e1e',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
          data-testid="new-request-error-banner"
        >
          <AlertCircle size={16} />
          <span>{submitError}</span>
        </div>
      )}

      {/* Main 2-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '516px 320px', gap: '24px', alignItems: 'start' }}>
        {/* Left Column (516px) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Card 1: Start from a note (AI Advisory) */}
          <div
            style={{
              backgroundColor: 'rgba(238, 241, 255, 0.5)',
              border: '0.667px solid #c3ccff',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:656"
          >
            {/* Header */}
            <div
              style={{
                borderBottom: '0.667px solid #c3ccff',
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <div
                  style={{
                    backgroundColor: '#4a56d2',
                    borderRadius: '4px',
                    width: '24px',
                    height: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    marginTop: '2px',
                  }}
                >
                  <Sparkles size={14} color="#ffffff" />
                </div>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#2f3789', lineHeight: '20px' }}>
                    Start from a note
                  </div>
                  <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '16px', marginTop: '2px' }}>
                    Paste what you would have written in an email. Nothing is added that is not in your note.
                  </div>
                </div>
              </div>
              <span
                style={{
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #c3ccff',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#2f3789',
                  letterSpacing: '0.275px',
                }}
              >
                Advisory
              </span>
            </div>

            {/* Textarea + Action */}
            <div style={{ padding: '12px 16px' }}>
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                rows={3}
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #c3ccff',
                  borderRadius: '4px',
                  fontSize: '14px',
                  lineHeight: '22px',
                  color: '#12161c',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                  resize: 'none',
                  outline: 'none',
                }}
                data-testid="ai-note-input"
              />
              <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  type="button"
                  onClick={handleStructureNote}
                  disabled={isAiLoading}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    backgroundColor: '#4a56d2',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    height: '28px',
                    padding: '0 12px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: isAiLoading ? 'wait' : 'pointer',
                    boxShadow: '0 1px 2px rgba(74, 86, 210, 0.2)',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseOver={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#3b46b8'; }}
                  onMouseOut={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#4a56d2'; }}
                  data-testid="structure-note-btn"
                >
                  {isAiLoading ? <RefreshCw size={14} className="animate-spin" /> : <Sparkles size={14} />}
                  <span>Structure this note</span>
                </button>
                {aiError && <span style={{ fontSize: '11px', color: '#b32626' }}>{aiError}</span>}
              </div>

              {/* Proposed Structure Preview */}
              {aiPreview && (
                <div style={{
                  marginTop: '12px',
                  border: '0.667px solid #c3ccff',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  backgroundColor: '#ffffff',
                }}>
                  {/* Preview Header */}
                  <div style={{
                    padding: '8px 14px',
                    borderBottom: '0.667px solid #e4e7ec',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.5px',
                    color: '#5a6472',
                    textTransform: 'uppercase',
                  }}>Proposed structure</div>

                  {/* Preview Body */}
                  <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: '4px', fontSize: '13px' }}>
                      <span style={{ color: '#5a6472', fontWeight: 500 }}>Title</span>
                      <span style={{ color: '#12161c' }}>{aiPreview.title || '—'}</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: '4px', fontSize: '13px' }}>
                      <span style={{ color: '#5a6472', fontWeight: 500 }}>Category</span>
                      <span style={{ color: aiPreview.category === 'not determined' ? '#8a929e' : '#12161c' }}>
                        {aiPreview.category}
                      </span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: '4px', fontSize: '13px', alignItems: 'start' }}>
                      <span style={{ color: '#5a6472', fontWeight: 500 }}>Items</span>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        {aiPreview.items.length === 0 && (
                          <span style={{ color: '#b32626' }}>— price missing</span>
                        )}
                        {aiPreview.items.map((item: any, i: number) => (
                          <span key={i} style={{ color: '#12161c' }}>
                            {item.quantity} unit · {item.itemName}
                            {item.estimatedUnitPrice > 0
                              ? ` · ${item.estimatedUnitPrice.toLocaleString('vi-VN')}₫`
                              : <span style={{ color: '#b32626' }}> · price missing</span>
                            }
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Warnings */}
                    {aiPreview.items.some((it: any) => it.estimatedUnitPrice === 0) && (
                      <div style={{ marginTop: '4px', fontSize: '12px', color: '#b32626' }}>
                        ! Still needed from you: Estimated unit price for missing items
                      </div>
                    )}
                    {aiPreview.category === 'not determined' && (
                      <div style={{ fontSize: '12px', color: '#b32626' }}>
                        ! Still needed from you: Category — no recognised keyword in the note
                      </div>
                    )}
                  </div>

                  {/* Preview Actions */}
                  <div style={{
                    padding: '10px 14px',
                    borderTop: '0.667px solid #e4e7ec',
                    display: 'flex',
                    gap: '8px',
                    alignItems: 'center',
                  }}>
                    <button
                      type="button"
                      onClick={handleApplyToForm}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        backgroundColor: '#4a56d2',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '4px',
                        height: '28px',
                        padding: '0 12px',
                        fontSize: '12px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                      data-testid="apply-to-form-btn"
                    >
                      <Check size={13} />
                      Apply to form
                    </button>
                    <button
                      type="button"
                      onClick={handleDiscardPreview}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#5a6472',
                        fontSize: '12px',
                        fontWeight: 500,
                        cursor: 'pointer',
                        padding: '0 4px',
                      }}
                      data-testid="discard-preview-btn"
                    >Discard</button>
                  </div>
                </div>
              )}
            </div>

            {/* Disclaimer Footer */}
            <div
              style={{
                borderTop: '0.667px solid #c3ccff',
                padding: '10px 16px',
                fontSize: '12px',
                color: '#5a6472',
                lineHeight: '16px',
              }}
            >
              The assistant only restructures your own words. It never fills in prices, dates or approvers on its own.
            </div>
          </div>

          {/* Card 2: Request details */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:683"
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '16px' }}>
              Request details
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Request title * */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                  Request title <span style={{ color: '#b32626' }}>*</span>
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Laptops for engineering onboarding"
                  style={{
                    width: '100%',
                    height: '37px',
                    padding: '0 10px',
                    backgroundColor: '#ffffff',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    boxSizing: 'border-box',
                    outline: 'none',
                  }}
                  data-testid="input-request-title"
                />
              </div>

              {/* Category * and Department * in 2 columns */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Category <span style={{ color: '#b32626' }}>*</span>
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    style={{
                      width: '100%',
                      height: '37px',
                      padding: '0 10px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: category ? '#12161c' : '#8a929e',
                      boxSizing: 'border-box',
                      outline: 'none',
                    }}
                    data-testid="select-category"
                  >
                    <option value="">Select…</option>
                    <option value="IT Equipment">IT Equipment</option>
                    <option value="Office Supplies">Office Supplies</option>
                    <option value="Facilities">Facilities</option>
                    <option value="Software & Licences">Software &amp; Licences</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Department <span style={{ color: '#b32626' }}>*</span>
                  </label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    style={{
                      width: '100%',
                      height: '37px',
                      padding: '0 10px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: department ? '#12161c' : '#8a929e',
                      boxSizing: 'border-box',
                      outline: 'none',
                    }}
                    data-testid="select-department"
                  >
                    <option value="">Select…</option>
                    <option value="Engineering">Engineering</option>
                    <option value="Operations">Operations</option>
                    <option value="Finance">Finance</option>
                    <option value="People">People</option>
                  </select>
                </div>
              </div>

              {/* Cost centre * and Required by * in 2 columns */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Cost centre <span style={{ color: '#b32626' }}>*</span>
                  </label>
                  <input
                    type="text"
                    value={costCentre}
                    onChange={(e) => setCostCentre(e.target.value)}
                    placeholder="CC-ENG-2200"
                    style={{
                      width: '100%',
                      height: '37px',
                      padding: '0 10px',
                      backgroundColor: '#ffffff',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: '#12161c',
                      boxSizing: 'border-box',
                      outline: 'none',
                    }}
                    data-testid="input-cost-centre"
                  />
                </div>

                <div ref={calendarRef} style={{ position: 'relative' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Required by <span style={{ color: '#b32626' }}>*</span>
                  </label>
                  <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                    <input
                      type="text"
                      value={requiredBy}
                      onChange={(e) => setRequiredBy(e.target.value)}
                      placeholder="15 Oct 2026"
                      style={{
                        width: '100%',
                        height: '37px',
                        padding: '0 36px 0 10px',
                        backgroundColor: '#ffffff',
                        border: showCalendar ? '0.667px solid #3b5bdb' : '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        fontSize: '14px',
                        color: '#12161c',
                        boxSizing: 'border-box',
                        outline: 'none',
                        transition: 'border-color 0.15s',
                      }}
                      data-testid="input-required-by"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        if (!showCalendar) {
                          const now = new Date();
                          setCalViewYear(now.getFullYear());
                          setCalViewMonth(now.getMonth());
                        }
                        setShowCalendar(prev => !prev);
                      }}
                      style={{
                        position: 'absolute',
                        right: '8px',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '0',
                        display: 'flex',
                        alignItems: 'center',
                        color: showCalendar ? '#3b5bdb' : '#6b7280',
                        transition: 'color 0.15s',
                      }}
                      title="Pick a date"
                      data-testid="btn-required-by-calendar"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                        <line x1="16" y1="2" x2="16" y2="6"/>
                        <line x1="8" y1="2" x2="8" y2="6"/>
                        <line x1="3" y1="10" x2="21" y2="10"/>
                      </svg>
                    </button>
                  </div>

                  {/* Custom Calendar Popup */}
                  {showCalendar && (() => {
                    const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
                    const days = getCalendarDays(calViewYear, calViewMonth);
                    const today = new Date();
                    const todayStr = `${today.getDate()}-${today.getMonth()}-${today.getFullYear()}`;
                    return (
                      <div style={{
                        position: 'absolute',
                        top: 'calc(100% + 6px)',
                        left: 0,
                        zIndex: 9999,
                        background: '#ffffff',
                        border: '1px solid #e4e7ec',
                        borderRadius: '12px',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)',
                        padding: '16px',
                        width: '280px',
                        userSelect: 'none',
                      }}>
                        {/* Header: Month nav */}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                          <button
                            type="button"
                            onClick={() => {
                              if (calViewMonth === 0) { setCalViewMonth(11); setCalViewYear(y => y - 1); }
                              else setCalViewMonth(m => m - 1);
                            }}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px 8px', borderRadius: '6px', color: '#6b7280', fontSize: '16px', lineHeight: 1, display: 'flex', alignItems: 'center' }}
                          >&#8249;</button>
                          <span style={{ fontSize: '13px', fontWeight: 600, color: '#12161c' }}>
                            {monthNames[calViewMonth]} {calViewYear}
                          </span>
                          <button
                            type="button"
                            onClick={() => {
                              if (calViewMonth === 11) { setCalViewMonth(0); setCalViewYear(y => y + 1); }
                              else setCalViewMonth(m => m + 1);
                            }}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px 8px', borderRadius: '6px', color: '#6b7280', fontSize: '16px', lineHeight: 1, display: 'flex', alignItems: 'center' }}
                          >&#8250;</button>
                        </div>
                        {/* Weekday headers */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px', marginBottom: '6px' }}>
                          {['Su','Mo','Tu','We','Th','Fr','Sa'].map(d => (
                            <div key={d} style={{ textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#9ca3af', padding: '2px 0' }}>{d}</div>
                          ))}
                        </div>
                        {/* Day grid */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px' }}>
                          {days.map((item, idx) => {
                            const isToday = item.type === 'current' && `${item.day}-${calViewMonth}-${calViewYear}` === todayStr;
                            return (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => item.type === 'current' && handleCalendarSelect(item.day)}
                                style={{
                                  border: 'none',
                                  background: isToday ? '#3b5bdb' : 'none',
                                  color: item.type !== 'current' ? '#d1d5db' : isToday ? '#ffffff' : '#12161c',
                                  borderRadius: '6px',
                                  padding: '5px 0',
                                  fontSize: '12px',
                                  fontWeight: isToday ? 700 : 400,
                                  cursor: item.type === 'current' ? 'pointer' : 'default',
                                  textAlign: 'center',
                                  transition: 'background 0.1s, color 0.1s',
                                }}
                                onMouseEnter={e => { if (item.type === 'current' && !isToday) (e.currentTarget as HTMLButtonElement).style.background = '#f1f3f9'; }}
                                onMouseLeave={e => { if (item.type === 'current' && !isToday) (e.currentTarget as HTMLButtonElement).style.background = 'none'; }}
                              >
                                {item.day}
                              </button>
                            );
                          })}
                        </div>
                        {/* Footer: Today shortcut */}
                        <div style={{ marginTop: '10px', borderTop: '1px solid #f3f4f6', paddingTop: '10px', textAlign: 'center' }}>
                          <button
                            type="button"
                            onClick={() => {
                              const now = new Date();
                              handleCalendarSelect(now.getDate());
                              setCalViewYear(now.getFullYear());
                              setCalViewMonth(now.getMonth());
                            }}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '12px', color: '#3b5bdb', fontWeight: 500, padding: '2px 8px', borderRadius: '4px' }}
                          >Today</button>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>

              {/* Delivery location * */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                  Delivery location <span style={{ color: '#b32626' }}>*</span>
                </label>
                <input
                  type="text"
                  value={deliveryLocation}
                  onChange={(e) => setDeliveryLocation(e.target.value)}
                  placeholder="HQ Hanoi · Floor 6 · Goods-in"
                  style={{
                    width: '100%',
                    height: '37px',
                    padding: '0 10px',
                    backgroundColor: '#ffffff',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    boxSizing: 'border-box',
                    outline: 'none',
                  }}
                  data-testid="input-delivery-location"
                />
              </div>

              {/* Business justification * */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: '#12161c' }}>
                    Business justification <span style={{ color: '#b32626' }}>*</span>
                  </label>
                  <span style={{ fontSize: '11px', color: '#8a929e' }}>
                    Approvers read this first
                  </span>
                </div>
                <textarea
                  value={justification}
                  onChange={(e) => setJustification(e.target.value)}
                  rows={3}
                  placeholder="Why this is needed, and what happens if it is not bought."
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    backgroundColor: '#ffffff',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    lineHeight: '22px',
                    color: '#12161c',
                    fontFamily: 'inherit',
                    boxSizing: 'border-box',
                    resize: 'none',
                    outline: 'none',
                  }}
                  data-testid="textarea-justification"
                />
              </div>
            </div>
          </div>

          {/* Card 3: Line items */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:760"
          >
            <div
              style={{
                borderBottom: '0.667px solid #e4e7ec',
                padding: '14px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ fontSize: '14px', fontWeight: 600, color: '#12161c' }}>
                Line items
              </span>
              <button
                type="button"
                onClick={handleAddItem}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #e4e7ec',
                  borderRadius: '4px',
                  height: '26px',
                  padding: '0 10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#5a6472',
                  cursor: 'pointer',
                }}
                data-testid="add-line-item-btn"
              >
                <Plus size={14} />
                <span>Add item</span>
              </button>
            </div>

            <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {items.map((it, idx) => (
                <div
                  key={it.id}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 70px 120px 34px',
                    gap: '12px',
                    alignItems: 'flex-end',
                  }}
                  data-testid={`line-item-row-${idx}`}
                >
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Item {idx + 1} description
                    </label>
                    <input
                      type="text"
                      value={it.itemName}
                      onChange={(e) => handleUpdateItem(it.id, 'itemName', e.target.value)}
                      placeholder="e.g. Dell XPS 15 32GB"
                      style={{
                        width: '100%',
                        height: '37px',
                        padding: '0 10px',
                        backgroundColor: '#ffffff',
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        fontSize: '14px',
                        color: '#12161c',
                        boxSizing: 'border-box',
                        outline: 'none',
                      }}
                      data-testid={`item-desc-${idx}`}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Qty
                    </label>
                    <input
                      type="number"
                      min={1}
                      value={it.quantity}
                      onChange={(e) => handleUpdateItem(it.id, 'quantity', Number(e.target.value))}
                      style={{
                        width: '100%',
                        height: '37px',
                        padding: '0 8px',
                        backgroundColor: '#ffffff',
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        fontSize: '14px',
                        color: '#12161c',
                        boxSizing: 'border-box',
                        outline: 'none',
                      }}
                      data-testid={`item-qty-${idx}`}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Est. unit price (₫)
                    </label>
                    <input
                      type="text"
                      inputMode="numeric"
                      value={it.estimatedUnitPrice === 0 ? '' : String(it.estimatedUnitPrice)}
                      onChange={(e) => {
                        // Strip all non-digit characters, then remove leading zeros
                        const raw = e.target.value.replace(/\D/g, '');
                        const num = raw === '' ? 0 : parseInt(raw, 10);
                        handleUpdateItem(it.id, 'estimatedUnitPrice', num);
                      }}
                      placeholder="0"
                      style={{
                        width: '100%',
                        height: '37px',
                        padding: '0 8px',
                        backgroundColor: '#ffffff',
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        fontSize: '14px',
                        color: '#12161c',
                        boxSizing: 'border-box',
                        outline: 'none',
                      }}
                      data-testid={`item-price-${idx}`}
                    />
                  </div>

                  <div>
                    <button
                      type="button"
                      disabled={items.length <= 1}
                      onClick={() => handleRemoveItem(it.id)}
                      style={{
                        width: '34px',
                        height: '37px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: '#ffffff',
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        color: items.length <= 1 ? '#cdd2da' : '#8a929e',
                        cursor: items.length <= 1 ? 'not-allowed' : 'pointer',
                      }}
                      data-testid={`item-remove-${idx}`}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Total Footer */}
            <div
              style={{
                borderTop: '0.667px solid #e4e7ec',
                padding: '14px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ fontSize: '14px', color: '#5a6472' }}>
                Estimated total
              </span>
              <span style={{ fontSize: '18px', fontWeight: 600, color: '#12161c' }} data-testid="new-request-total">
                {estimatedTotal.toLocaleString()} ₫
              </span>
            </div>
          </div>
        </div>

        {/* Right Column (320px) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Card 1: Before you submit */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:797"
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '12px' }}>
              Before you submit
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.title ? '#12161c' : '#5a6472' }}>
                {checklist.title ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Request title</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.category ? '#12161c' : '#5a6472' }}>
                {checklist.category ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Category</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.department ? '#12161c' : '#5a6472' }}>
                {checklist.department ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Department</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.costCentre ? '#12161c' : '#5a6472' }}>
                {checklist.costCentre ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Cost centre</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.requiredBy ? '#12161c' : '#5a6472' }}>
                {checklist.requiredBy ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Required-by date</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.deliveryLocation ? '#12161c' : '#5a6472' }}>
                {checklist.deliveryLocation ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Delivery location</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.justification ? '#12161c' : '#5a6472' }}>
                {checklist.justification ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Business justification</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: checklist.lineItemsPriced ? '#12161c' : '#5a6472' }}>
                {checklist.lineItemsPriced ? <Check size={14} color="#16603b" /> : <X size={14} color="#8a929e" />}
                <span>Line items priced</span>
              </div>
            </div>
          </div>

          {/* Card 2: Missing information (Advisory) */}
          <div
            style={{
              backgroundColor: 'rgba(238, 241, 255, 0.5)',
              border: '0.667px solid #c3ccff',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
            data-node-id="9:839"
          >
            {/* Header */}
            <div
              style={{
                borderBottom: '0.667px solid #c3ccff',
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <div
                  style={{
                    backgroundColor: '#4a56d2',
                    borderRadius: '4px',
                    width: '24px',
                    height: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    marginTop: '2px',
                  }}
                >
                  <Sparkles size={14} color="#ffffff" />
                </div>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#2f3789', lineHeight: '20px' }}>
                    Missing information
                  </div>
                  <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '16px', marginTop: '2px' }}>
                    {missingFieldsCount > 0 ? `${missingFieldsCount} required fields still empty.` : 'All required fields filled!'}
                  </div>
                </div>
              </div>
              <span
                style={{
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #c3ccff',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#2f3789',
                  letterSpacing: '0.275px',
                }}
              >
                Advisory
              </span>
            </div>

            {/* Suggestions list */}
            <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* Suggestion 1: Cost centre */}
              {!costCentreDismissed && !costCentre && (
                <div
                  style={{
                    backgroundColor: '#ffffff',
                    border: '0.667px solid #c3ccff',
                    borderRadius: '4px',
                    padding: '10px',
                  }}
                >
                  <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', letterSpacing: '0.275px', marginBottom: '2px' }}>
                    Cost centre
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c', marginBottom: '4px' }}>
                    CC-ENG-2200
                  </div>
                  <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '16px', marginBottom: '10px' }}>
                    Used on 14 of the last 15 Engineering requests.
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      type="button"
                      onClick={() => setCostCentre('CC-ENG-2200')}
                      style={{
                        backgroundColor: '#4a56d2',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '4px',
                        padding: '4px 10px',
                        fontSize: '11px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                      data-testid="use-suggestion-costcentre"
                    >
                      Use this
                    </button>
                    <button
                      type="button"
                      onClick={() => setCostCentreDismissed(true)}
                      style={{
                        backgroundColor: '#ffffff',
                        border: '0.667px solid #e4e7ec',
                        color: '#5a6472',
                        borderRadius: '4px',
                        padding: '4px 10px',
                        fontSize: '11px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              )}

              {/* Suggestion 2: Delivery location */}
              {!locationDismissed && !deliveryLocation && (
                <div
                  style={{
                    backgroundColor: '#ffffff',
                    border: '0.667px solid #c3ccff',
                    borderRadius: '4px',
                    padding: '10px',
                  }}
                >
                  <div style={{ fontSize: '11px', fontWeight: 600, color: '#8a929e', letterSpacing: '0.275px', marginBottom: '2px' }}>
                    Delivery location
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c', marginBottom: '4px' }}>
                    HQ Hanoi · Floor 6 · Goods-in
                  </div>
                  <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '16px', marginBottom: '10px' }}>
                    Standing delivery point for Engineering hardware.
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      type="button"
                      onClick={() => setDeliveryLocation('HQ Hanoi · Floor 6 · Goods-in')}
                      style={{
                        backgroundColor: '#4a56d2',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '4px',
                        padding: '4px 10px',
                        fontSize: '11px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                      data-testid="use-suggestion-location"
                    >
                      Use this
                    </button>
                    <button
                      type="button"
                      onClick={() => setLocationDismissed(true)}
                      style={{
                        backgroundColor: '#ffffff',
                        border: '0.667px solid #e4e7ec',
                        color: '#5a6472',
                        borderRadius: '4px',
                        padding: '4px 10px',
                        fontSize: '11px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              )}

              {/* Unassisted fields */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', paddingTop: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                  <Settings size={13} color="#8a929e" />
                  <span style={{ fontWeight: 600, color: '#12161c' }}>Request title</span>
                  <span style={{ color: '#5a6472' }}>— no suggestion. Only you can decide this.</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                  <Settings size={13} color="#8a929e" />
                  <span style={{ fontWeight: 600, color: '#12161c' }}>Category</span>
                  <span style={{ color: '#5a6472' }}>— no suggestion. Only you can decide this.</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                  <Settings size={13} color="#8a929e" />
                  <span style={{ fontWeight: 600, color: '#12161c' }}>Required-by date</span>
                  <span style={{ color: '#5a6472' }}>— no suggestion. Only you can decide this.</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                  <Settings size={13} color="#8a929e" />
                  <span style={{ fontWeight: 600, color: '#12161c' }}>Business justification</span>
                  <span style={{ color: '#5a6472' }}>— no suggestion. Only you can decide this.</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting}
              style={{
                width: '100%',
                height: '36px',
                backgroundColor: '#4a56d2',
                color: '#ffffff',
                border: 'none',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: isSubmitting ? 'wait' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'background-color 0.15s ease',
              }}
              data-testid="submit-for-approval-btn"
            >
              {isSubmitting && <RefreshCw size={16} className="animate-spin" />}
              <span>Submit for approval</span>
            </button>

            <button
              type="button"
              onClick={handleSaveDraft}
              style={{
                width: '100%',
                height: '36px',
                backgroundColor: '#ffffff',
                border: '0.667px solid #e4e7ec',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: 600,
                color: '#5a6472',
                cursor: 'pointer',
              }}
              data-testid="save-as-draft-btn"
            >
              Save as draft
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
