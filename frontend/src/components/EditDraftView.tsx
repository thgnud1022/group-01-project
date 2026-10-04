import React, { useState, useMemo } from 'react';
import { 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Check, 
  X, 
  Sparkles,
  Settings,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface LineItem {
  id: string;
  itemName: string;
  quantity: number;
  estimatedUnitPrice: number;
}

interface EditDraftViewProps {
  pr: any;
  user: AuthenticatedUser | null;
  onBack: () => void;
  onSubmitSuccess: (updatedPr: any) => void;
  onSaveSuccess: (updatedPr: any) => void;
}

export const EditDraftView: React.FC<EditDraftViewProps> = ({
  pr,
  user,
  onBack,
  onSubmitSuccess,
  onSaveSuccess,
}) => {
  // Form fields initialized from draft PR
  const [title, setTitle] = useState(pr.title || 'Whiteboard markers and erasers');
  const [category, setCategory] = useState(pr.category || 'Office Supplies');
  const [department, setDepartment] = useState(pr.departmentName || pr.deptId || 'People');
  const [costCentre, setCostCentre] = useState(pr.costCentre || '');
  const [requiredBy, setRequiredBy] = useState(pr.requiredBy || '');
  const [deliveryLocation, setDeliveryLocation] = useState(pr.deliveryLocation || '');
  const [justification, setJustification] = useState(pr.justification || 'Meeting rooms are out of markers.');

  // Line items
  const [items, setItems] = useState<LineItem[]>(
    pr.items && pr.items.length > 0
      ? pr.items.map((it: any, idx: number) => ({
          id: String(it.id || idx + 1),
          itemName: it.itemName,
          quantity: Number(it.quantity) || 1,
          estimatedUnitPrice: Number(it.estimatedUnitPrice) || 0,
        }))
      : [{ id: '1', itemName: 'Whiteboard marker, assorted', quantity: 60, estimatedUnitPrice: 28000 }]
  );

  const [costCentreDismissed, setCostCentreDismissed] = useState(false);
  const [locationDismissed, setLocationDismissed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const estimatedTotal = useMemo(() => {
    return items.reduce((sum, it) => sum + (Number(it.quantity) || 0) * (Number(it.estimatedUnitPrice) || 0), 0);
  }, [items]);

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

  const missingCount = Object.values(checklist).filter((v) => !v).length;

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

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const result = await api.createPR({
        departmentId: department === 'People' ? 'DEPT-HR' : 'DEPT-IT',
        title: title || 'Whiteboard markers and erasers',
        items: items.map((it) => ({
          itemName: it.itemName,
          quantity: it.quantity,
          estimatedUnitPrice: it.estimatedUnitPrice,
        })),
      });
      onSubmitSuccess(result);
    } catch (err: any) {
      setErrorMsg(err.message || 'Lỗi khi gửi yêu cầu mua sắm');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSave = () => {
    const updatedPr = {
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
      lastUpdated: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) + ' · 16:00',
    };
    onSaveSuccess(updatedPr);
  };

  return (
    <div style={{ maxWidth: '860px', margin: '0 auto' }} data-node-id="9:1237" data-testid="edit-draft-view">
      {/* Back button */}
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
          data-testid="back-to-draft-detail"
        >
          <ArrowLeft size={14} />
          <span>{pr.id || 'PR-2026-035'}</span>
        </button>
      </div>

      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
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
          <span style={{ fontSize: '12px', color: '#8a929e' }}>
            {pr.id || 'PR-2026-035'}
          </span>
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
          Edit purchase request
        </h1>
        <p style={{ margin: 0, fontSize: '14px', color: '#5a6472', lineHeight: '20px' }}>
          Keep working on this draft. Nobody sees it until you submit.
        </p>
      </div>

      {errorMsg && (
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
        >
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* 2-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '516px 320px', gap: '24px', alignItems: 'start' }}>
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Card 1: Request Details */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '16px' }}>
              Request details
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                  Request title <span style={{ color: '#b32626' }}>*</span>
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  style={{
                    width: '100%',
                    height: '37px',
                    padding: '0 10px',
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    boxSizing: 'border-box',
                    outline: 'none',
                  }}
                  data-testid="edit-title-input"
                />
              </div>

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
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: '#12161c',
                      boxSizing: 'border-box',
                      outline: 'none',
                    }}
                  >
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
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: '#12161c',
                      boxSizing: 'border-box',
                      outline: 'none',
                    }}
                  >
                    <option value="Engineering">Engineering</option>
                    <option value="Operations">Operations</option>
                    <option value="Finance">Finance</option>
                    <option value="People">People</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Cost centre <span style={{ color: '#b32626' }}>*</span>
                  </label>
                  <input
                    type="text"
                    value={costCentre}
                    onChange={(e) => setCostCentre(e.target.value)}
                    placeholder="CC-..."
                    style={{
                      width: '100%',
                      height: '37px',
                      padding: '0 10px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: '#12161c',
                      boxSizing: 'border-box',
                      outline: 'none',
                    }}
                    data-testid="edit-costcentre-input"
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '6px' }}>
                    Required by <span style={{ color: '#b32626' }}>*</span>
                  </label>
                  <input
                    type="text"
                    value={requiredBy}
                    onChange={(e) => setRequiredBy(e.target.value)}
                    placeholder="DD/MM/YYYY"
                    style={{
                      width: '100%',
                      height: '37px',
                      padding: '0 10px',
                      border: '0.667px solid #e4e7ec',
                      borderRadius: '4px',
                      fontSize: '14px',
                      color: '#12161c',
                      boxSizing: 'border-box',
                      outline: 'none',
                    }}
                  />
                </div>
              </div>

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
                    border: '0.667px solid #e4e7ec',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#12161c',
                    boxSizing: 'border-box',
                    outline: 'none',
                  }}
                  data-testid="edit-location-input"
                />
              </div>

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
                  style={{
                    width: '100%',
                    padding: '8px 10px',
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
                />
              </div>
            </div>
          </div>

          {/* Card 2: Line items */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
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
                >
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Item {idx + 1} description
                    </label>
                    <input
                      type="text"
                      value={it.itemName}
                      onChange={(e) => handleUpdateItem(it.id, 'itemName', e.target.value)}
                      style={{
                        width: '100%',
                        height: '37px',
                        padding: '0 10px',
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        fontSize: '14px',
                        color: '#12161c',
                        boxSizing: 'border-box',
                        outline: 'none',
                      }}
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
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        fontSize: '14px',
                        color: '#12161c',
                        boxSizing: 'border-box',
                        outline: 'none',
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#12161c', marginBottom: '4px' }}>
                      Est. unit price (₫)
                    </label>
                    <input
                      type="number"
                      value={it.estimatedUnitPrice}
                      onChange={(e) => handleUpdateItem(it.id, 'estimatedUnitPrice', Number(e.target.value))}
                      style={{
                        width: '100%',
                        height: '37px',
                        padding: '0 8px',
                        border: '0.667px solid #e4e7ec',
                        borderRadius: '4px',
                        fontSize: '14px',
                        color: '#12161c',
                        boxSizing: 'border-box',
                        outline: 'none',
                      }}
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
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div
              style={{
                borderTop: '0.667px solid #e4e7ec',
                padding: '14px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ fontSize: '14px', color: '#5a6472' }}>Estimated total</span>
              <span style={{ fontSize: '18px', fontWeight: 600, color: '#12161c' }}>
                {estimatedTotal.toLocaleString()} ₫
              </span>
            </div>
          </div>
        </div>

        {/* Right Column */}
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

          {/* Card 2: Changes on this edit (Figma 9:1237) */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '8px' }}>
              Changes on this edit
            </div>
            <p style={{ margin: '0 0 6px 0', fontSize: '13px', color: '#5a6472' }}>
              Nothing changed yet.
            </p>
            <p style={{ margin: 0, fontSize: '11px', color: '#8a929e', lineHeight: '16px' }}>
              This list is recorded on the request so the approver can see what moved.
            </p>
          </div>

          {/* Card 3: Missing information */}
          {missingCount > 0 && (
            <div
              style={{
                backgroundColor: 'rgba(238, 241, 255, 0.5)',
                border: '0.667px solid #c3ccff',
                borderRadius: '8px',
                overflow: 'hidden',
                boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
              }}
            >
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
                    }}
                  >
                    <Sparkles size={14} color="#ffffff" />
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 600, color: '#2f3789' }}>
                      Missing information
                    </div>
                    <div style={{ fontSize: '12px', color: '#5a6472' }}>
                      {missingCount} required fields still empty.
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
                  }}
                >
                  Advisory
                </span>
              </div>

              <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {!costCentreDismissed && !costCentre && (
                  <div style={{ backgroundColor: '#ffffff', border: '0.667px solid #c3ccff', borderRadius: '4px', padding: '10px' }}>
                    <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>Cost centre</div>
                    <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c', marginBottom: '4px' }}>CC-PPL-1400</div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginBottom: '8px' }}>Default People cost centre.</div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        type="button"
                        onClick={() => setCostCentre('CC-PPL-1400')}
                        style={{ backgroundColor: '#4a56d2', color: '#ffffff', border: 'none', borderRadius: '4px', padding: '4px 10px', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                      >
                        Use this
                      </button>
                      <button
                        type="button"
                        onClick={() => setCostCentreDismissed(true)}
                        style={{ backgroundColor: '#ffffff', border: '0.667px solid #e4e7ec', color: '#5a6472', borderRadius: '4px', padding: '4px 10px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                )}

                {!locationDismissed && !deliveryLocation && (
                  <div style={{ backgroundColor: '#ffffff', border: '0.667px solid #c3ccff', borderRadius: '4px', padding: '10px' }}>
                    <div style={{ fontSize: '11px', color: '#8a929e', marginBottom: '2px' }}>Delivery location</div>
                    <div style={{ fontSize: '14px', fontWeight: 500, color: '#12161c', marginBottom: '4px' }}>HQ Hanoi · Floor 2 · Reception</div>
                    <div style={{ fontSize: '12px', color: '#5a6472', marginBottom: '8px' }}>Standing delivery point for People.</div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        type="button"
                        onClick={() => setDeliveryLocation('HQ Hanoi · Floor 2 · Reception')}
                        style={{ backgroundColor: '#4a56d2', color: '#ffffff', border: 'none', borderRadius: '4px', padding: '4px 10px', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                      >
                        Use this
                      </button>
                      <button
                        type="button"
                        onClick={() => setLocationDismissed(true)}
                        style={{ backgroundColor: '#ffffff', border: '0.667px solid #e4e7ec', color: '#5a6472', borderRadius: '4px', padding: '4px 10px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                )}

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                  <Settings size={13} color="#8a929e" />
                  <span style={{ fontWeight: 600, color: '#12161c' }}>Required-by date</span>
                  <span style={{ color: '#5a6472' }}>Only you can decide this.</span>
                </div>
              </div>
            </div>
          )}

          {/* Card 4: Budget check preview (Figma 9:1237) */}
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '0.667px solid #e4e7ec',
              borderRadius: '8px',
              padding: '16px',
              boxShadow: '0px 1px 1px rgba(18, 22, 28, 0.04)',
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#12161c', marginBottom: '12px' }}>
              Budget check preview
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', fontSize: '13px' }}>
              <span style={{ color: '#5a6472' }}>Office Supplies available</span>
              <span style={{ fontWeight: 600, color: '#12161c' }}>50,500,000 ₫</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px' }}>
              <span style={{ color: '#5a6472' }}>This request</span>
              <span style={{ fontWeight: 600, color: '#12161c' }}>{estimatedTotal.toLocaleString()} ₫</span>
            </div>
          </div>

          {/* Actions */}
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
              }}
              data-testid="edit-submit-btn"
            >
              {isSubmitting && <RefreshCw size={16} className="animate-spin" />}
              <span>Submit for approval</span>
            </button>

            <button
              type="button"
              onClick={handleSave}
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
              data-testid="edit-save-changes-btn"
            >
              Save changes
            </button>

            <button
              type="button"
              onClick={onBack}
              style={{
                width: '100%',
                height: '30px',
                backgroundColor: 'transparent',
                border: 'none',
                color: '#5a6472',
                fontSize: '13px',
                cursor: 'pointer',
                textAlign: 'center',
              }}
              data-testid="edit-cancel-btn"
            >
              Cancel and go back
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
