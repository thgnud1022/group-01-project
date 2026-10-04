import React, { useState, useMemo } from 'react';
import { 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Check, 
  RotateCw,
  Loader2
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface LineItem {
  id: string;
  itemName: string;
  quantity: number;
  estimatedUnitPrice: number;
}

interface EditAfterRevisionViewProps {
  pr: any;
  user: AuthenticatedUser | null;
  onBack: () => void;
  onResubmitSuccess: (updatedPr: any) => void;
  onSaveSuccess: (updatedPr: any) => void;
}

export const EditAfterRevisionView: React.FC<EditAfterRevisionViewProps> = ({
  pr,
  user,
  onBack,
  onResubmitSuccess,
  onSaveSuccess,
}) => {
  const prId = pr?.id || 'PR-2026-037';
  const approverComment = pr?.approverComments || pr?.revisionFeedback || 'Split into two phases and name the twelve recipients before resubmitting.';
  const approverInfo = pr?.approverName ? `${pr.approverName} · 19 Aug 2026 · 09:00` : 'Hoàng Nhật Nam (People Manager) · 19 Aug 2026 · 09:00';

  // Form fields
  const [title, setTitle] = useState(pr.title || 'Standing desk converters (12 units)');
  const [category, setCategory] = useState(pr.category || 'Facilities');
  const [department, setDepartment] = useState(pr.departmentName || pr.deptId || 'People');
  const [costCentre, setCostCentre] = useState(pr.costCentre || 'CC-PPL-1400');
  const [requiredBy, setRequiredBy] = useState(pr.requiredBy || '01 Oct 2026');
  const [deliveryLocation, setDeliveryLocation] = useState(pr.deliveryLocation || 'HQ Hanoi · Floor 2 · Reception');
  const [justification, setJustification] = useState(pr.justification || 'Requested through the wellbeing survey.');

  // Line items
  const [items, setItems] = useState<LineItem[]>(
    pr.items && pr.items.length > 0
      ? pr.items.map((it: any, idx: number) => ({
          id: String(it.id || idx + 1),
          itemName: it.itemName,
          quantity: Number(it.quantity) || 1,
          estimatedUnitPrice: Number(it.estimatedUnitPrice) || 0,
        }))
      : [{ id: '1', itemName: 'Sit-stand desk converter', quantity: 12, estimatedUnitPrice: 3100000 }]
  );

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const estimatedTotal = useMemo(() => {
    return items.reduce((sum, it) => sum + (Number(it.quantity) || 0) * (Number(it.estimatedUnitPrice) || 0), 0);
  }, [items]);

  const formatVND = (num: number) => {
    return Number(num || 0).toLocaleString('vi-VN') + ' ₫';
  };

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

  const handleUpdateItem = (id: string, field: keyof LineItem, val: any) => {
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, [field]: val } : it))
    );
  };

  // Calculate changes on this edit dynamically
  const changes = useMemo(() => {
    const list: string[] = [];
    if (pr.title && title.trim() !== pr.title.trim()) {
      list.push(`Title changed: "${pr.title}" → "${title.trim()}"`);
    }
    const origEstimated = Number(pr.estimatedValue || 0);
    if (origEstimated > 0 && Math.abs(origEstimated - estimatedTotal) > 0.01) {
      list.push(`Estimated total: ${formatVND(origEstimated)} → ${formatVND(estimatedTotal)}`);
    }
    const origItemsCount = (pr.items || []).length;
    if (origItemsCount > 0 && origItemsCount !== items.length) {
      list.push(`Line items count: ${origItemsCount} → ${items.length}`);
    }
    return list;
  }, [pr, title, estimatedTotal, items]);

  const handleResubmit = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const res = await api.resubmitPR(pr.id, {
        title: title.trim(),
        description: justification.trim(),
        items: items.map((it) => ({
          itemName: it.itemName.trim(),
          quantity: it.quantity,
          estimatedUnitPrice: it.estimatedUnitPrice,
        })),
        comments: changes.length > 0 ? changes.join('; ') : 'Resubmitted after revision review',
      });
      onResubmitSuccess(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Lỗi khi gửi lại yêu cầu');
    } finally {
      setIsSubmitting(false);
    }
  };


  const handleSave = () => {
    const updated = {
      ...pr,
      title,
      category,
      departmentName: department,
      costCentre,
      requiredBy,
      deliveryLocation,
      justification,
      items,
      estimatedValue: estimatedTotal,
    };
    onSaveSuccess(updated);
  };

  return (
    <div 
      style={{ maxWidth: '860.67px', margin: '0 auto', fontFamily: 'Inter, sans-serif' }}
      data-node-id="9:3179"
      data-testid="edit-after-revision-view"
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
          data-testid="back-link"
        >
          <ArrowLeft size={14} />
          <span>{prId}</span>
        </button>
      </div>

      {/* Header bar: Badge + ID */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <span
          style={{
            backgroundColor: '#fdf4e3',
            border: '0.667px solid #f2ddad',
            borderRadius: '4px',
            padding: '2.5px 8px',
            fontSize: '12px',
            fontWeight: 500,
            color: '#7a5209',
            lineHeight: '16px',
          }}
        >
          Revision required
        </span>
        <span style={{ fontSize: '12px', color: '#8a929e', lineHeight: '16px' }}>
          {prId}
        </span>
      </div>

      {/* Main Title & Subtitle */}
      <h1
        style={{
          fontSize: '24px',
          fontWeight: 600,
          color: '#12161c',
          margin: '0 0 8px 0',
          letterSpacing: '-0.6px',
          lineHeight: '32px',
        }}
      >
        Edit purchase request
      </h1>
      <p
        style={{
          fontSize: '14px',
          color: '#5a6472',
          margin: '0 0 24px 0',
          lineHeight: '20px',
        }}
      >
        Make the changes the approver asked for. Resubmitting sends it back to the same approver with a note on what moved.
      </p>

      {errorMsg && (
        <div style={{ backgroundColor: '#fdecec', border: '1px solid #f4c2c2', color: '#8e1e1e', padding: '12px', borderRadius: '6px', marginBottom: '16px', fontSize: '13px' }}>
          {errorMsg}
        </div>
      )}

      {/* Two-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '516.67px 320px', gap: '24px', alignItems: 'flex-start' }}>
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Yellow Box: What the approver asked for */}
          <div
            style={{
              backgroundColor: '#fdf4e3',
              border: '0.667px solid #f2ddad',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <RotateCw size={16} color="#7a5209" />
              <h2
                style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  color: '#7a5209',
                  margin: 0,
                  lineHeight: '20px',
                }}
              >
                What the approver asked for
              </h2>
            </div>
            <p
              style={{
                fontSize: '14px',
                color: '#12161c',
                margin: '0 0 8px 0',
                lineHeight: '22.75px',
              }}
            >
              {approverComment}
            </p>
            <div style={{ fontSize: '12px', color: '#5a6472', lineHeight: '16px' }}>
              {approverInfo}
            </div>
          </div>

          {/* Request details Card */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
            }}
          >
            <h2
              style={{
                fontSize: '14px',
                fontWeight: 600,
                color: '#12161c',
                margin: '0 0 16px 0',
                lineHeight: '20px',
              }}
            >
              Request details
            </h2>

            {/* Request Title */}
            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                Request title <span style={{ color: '#b32626' }}>*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                style={{
                  width: '100%',
                  height: '37px',
                  padding: '8px 11px',
                  border: '0.667px solid #e4e7ec',
                  borderRadius: '4px',
                  fontSize: '14px',
                  color: '#12161c',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            {/* Category & Department */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  Category <span style={{ color: '#b32626' }}>*</span>
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  style={{
                    width: '100%',
                    height: '37px',
                    padding: '8px 11px',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    backgroundColor: '#ffffff',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                >
                  <option value="IT Equipment">IT Equipment</option>
                  <option value="Office Supplies">Office Supplies</option>
                  <option value="Facilities">Facilities</option>
                  <option value="Software & Licences">Software & Licences</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  Department <span style={{ color: '#b32626' }}>*</span>
                </label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  style={{
                    width: '100%',
                    height: '37px',
                    padding: '8px 11px',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    backgroundColor: '#ffffff',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                >
                  <option value="Engineering">Engineering</option>
                  <option value="Operations">Operations</option>
                  <option value="People">People</option>
                  <option value="Finance">Finance</option>
                </select>
              </div>
            </div>

            {/* Cost Centre & Required by */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  Cost centre <span style={{ color: '#b32626' }}>*</span>
                </label>
                <input
                  type="text"
                  value={costCentre}
                  onChange={(e) => setCostCentre(e.target.value)}
                  style={{
                    width: '100%',
                    height: '37px',
                    padding: '8px 11px',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                  Required by <span style={{ color: '#b32626' }}>*</span>
                </label>
                <input
                  type="text"
                  value={requiredBy}
                  onChange={(e) => setRequiredBy(e.target.value)}
                  style={{
                    width: '100%',
                    height: '37px',
                    padding: '8px 11px',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            {/* Delivery Location */}
            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                Delivery location <span style={{ color: '#b32626' }}>*</span>
              </label>
              <input
                type="text"
                value={deliveryLocation}
                onChange={(e) => setDeliveryLocation(e.target.value)}
                style={{
                  width: '100%',
                  height: '37px',
                  padding: '8px 11px',
                  border: '0.667px solid #e4e7ec',
                  borderRadius: '4px',
                  fontSize: '14px',
                  color: '#12161c',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            {/* Business Justification */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600, color: '#12161c' }}>
                  Business justification <span style={{ color: '#b32626' }}>*</span>
                </label>
                <span style={{ fontSize: '11px', color: '#8a929e' }}>Approvers read this first</span>
              </div>
              <textarea
                value={justification}
                onChange={(e) => setJustification(e.target.value)}
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
                  resize: 'vertical',
                }}
              />
            </div>
          </div>

          {/* Line items Card */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', margin: 0 }}>
                Line items
              </h2>
              <button
                onClick={handleAddItem}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  backgroundColor: '#ffffff',
                  border: '0.667px solid #e4e7ec',
                  borderRadius: '4px',
                  padding: '4px 10px',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#12161c',
                  cursor: 'pointer',
                }}
              >
                <Plus size={14} />
                <span>Add item</span>
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
              {items.map((it, idx) => (
                <div key={it.id} style={{ display: 'grid', gridTemplateColumns: '220px 70px 130px 32px', gap: '8px', alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder={`Item ${idx + 1} description`}
                    value={it.itemName}
                    onChange={(e) => handleUpdateItem(it.id, 'itemName', e.target.value)}
                    style={{
                      height: '35px',
                      padding: '6px 10px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '13px',
                      color: '#12161c',
                      outline: 'none',
                    }}
                  />
                  <input
                    type="number"
                    min="1"
                    value={it.quantity}
                    onChange={(e) => handleUpdateItem(it.id, 'quantity', parseInt(e.target.value) || 1)}
                    style={{
                      height: '35px',
                      padding: '6px 8px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '13px',
                      color: '#12161c',
                      textAlign: 'center',
                      outline: 'none',
                    }}
                  />
                  <input
                    type="number"
                    min="0"
                    step="1000"
                    placeholder="Est. unit price"
                    value={it.estimatedUnitPrice || ''}
                    onChange={(e) => handleUpdateItem(it.id, 'estimatedUnitPrice', parseFloat(e.target.value) || 0)}
                    style={{
                      height: '35px',
                      padding: '6px 10px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '13px',
                      color: '#12161c',
                      textAlign: 'right',
                      outline: 'none',
                    }}
                  />
                  <button
                    onClick={() => handleRemoveItem(it.id)}
                    style={{
                      backgroundColor: 'transparent',
                      border: 'none',
                      color: '#8a929e',
                      cursor: 'pointer',
                      padding: 0,
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '0.667px solid #e4e7ec', paddingTop: '14px' }}>
              <span style={{ fontSize: '13px', color: '#5a6472' }}>Estimated total</span>
              <span style={{ fontSize: '18px', fontWeight: 600, color: '#12161c' }}>
                {formatVND(estimatedTotal)}
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Checklist & Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Before you submit */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
            }}
          >
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', margin: '0 0 14px 0' }}>
              Before you submit
            </h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                { label: 'Request title', ok: checklist.title },
                { label: 'Category', ok: checklist.category },
                { label: 'Department', ok: checklist.department },
                { label: 'Cost centre', ok: checklist.costCentre },
                { label: 'Required-by date', ok: checklist.requiredBy },
                { label: 'Delivery location', ok: checklist.deliveryLocation },
                { label: 'Business justification', ok: checklist.justification },
                { label: 'Line items priced', ok: checklist.lineItemsPriced },
              ].map((c) => (
                <li key={c.label} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: c.ok ? '#16603b' : '#8a929e' }}>
                  <Check size={14} color={c.ok ? '#16603b' : '#8a929e'} />
                  <span>{c.label}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Changes on this edit */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
            }}
          >
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#12161c', margin: '0 0 6px 0' }}>
              Changes on this edit
            </h4>
            {changes.length > 0 ? (
              <ul style={{ paddingLeft: '16px', margin: '0 0 8px 0', fontSize: '12px', color: '#12161c', lineHeight: '18px' }} data-testid="changes-list">
                {changes.map((c, idx) => (
                  <li key={idx}>{c}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '12px', color: '#8a929e', margin: '0 0 6px 0' }}>
                Nothing changed yet.
              </p>
            )}
            <p style={{ fontSize: '11px', color: '#8a929e', margin: 0 }}>
              This list is recorded on the request so the approver can see what moved.
            </p>
          </div>


          {/* Budget check preview */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
            }}
          >
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#12161c', margin: '0 0 10px 0' }}>
              Budget check preview
            </h4>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#5a6472', marginBottom: '6px' }}>
              <span>Facilities available</span>
              <span style={{ fontWeight: 600, color: '#12161c' }}>186,000,000 ₫</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#5a6472' }}>
              <span>This request</span>
              <span style={{ fontWeight: 600, color: '#12161c' }}>{formatVND(estimatedTotal)}</span>
            </div>
          </div>

          {/* Action buttons */}
          <button
            onClick={handleResubmit}
            disabled={isSubmitting}
            style={{
              width: '100%',
              height: '37px',
              backgroundColor: '#4a56d2',
              color: '#ffffff',
              border: 'none',
              borderRadius: '4px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
            }}
            data-testid="resubmit-btn"
          >
            {isSubmitting ? <Loader2 size={16} className="animate-spin" /> : <span>Resubmit for approval</span>}
          </button>

          <button
            onClick={handleSave}
            style={{
              width: '100%',
              height: '37px',
              backgroundColor: '#ffffff',
              color: '#5a6472',
              border: '0.667px solid #e4e7ec',
              borderRadius: '4px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
            data-testid="save-changes-btn"
          >
            Save changes
          </button>

          <button
            onClick={onBack}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: '#5a6472',
              fontSize: '12px',
              cursor: 'pointer',
              textAlign: 'center',
              marginTop: '4px',
            }}
          >
            Cancel and go back
          </button>
        </div>
      </div>
    </div>
  );
};
