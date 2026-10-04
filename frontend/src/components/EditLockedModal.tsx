import React from 'react';
import { Lock } from 'lucide-react';

interface EditLockedModalProps {
  pr: any;
  onBack: () => void;
}

export const EditLockedModal: React.FC<EditLockedModalProps> = ({ pr, onBack }) => {
  const prId = pr?.id || 'PR-2026-041';

  return (
    <div 
      style={{ 
        maxWidth: '860px', 
        margin: '0 auto', 
        paddingTop: '32px',
        display: 'flex',
        justifyContent: 'center',
        fontFamily: 'Inter, sans-serif'
      }}
      data-node-id="9:2321"
      data-testid="edit-locked-view"
    >
      <div
        style={{
          width: '672px',
          backgroundColor: '#ffffff',
          border: '0.667px solid #e4e7ec',
          borderRadius: '8px',
          padding: '32px 32px 28px 32px',
          boxShadow: '0px 1px 0.5px rgba(18,22,28,0.03), 0px 1px 1px rgba(18,22,28,0.04)',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Lock Icon */}
        <div style={{ color: '#12161c', marginBottom: '12px' }}>
          <Lock size={20} strokeWidth={1.75} />
        </div>

        {/* Title */}
        <h2
          style={{
            fontSize: '18px',
            fontWeight: 600,
            color: '#12161c',
            margin: '0 0 12px 0',
            lineHeight: '28px',
          }}
        >
          This request is locked
        </h2>

        {/* Explanation */}
        <p
          style={{
            fontSize: '14px',
            color: '#5a6472',
            lineHeight: '22.75px',
            maxWidth: '448px',
            margin: '0 0 24px 0',
          }}
        >
          <span style={{ color: '#5a6472' }}>{prId}</span> is{' '}
          <strong style={{ fontWeight: 500, color: '#12161c' }}>pending approval</strong>
          . A request can only be edited while it is a draft, after a revision is requested, or after a failed submission — so that what an approver reviewed cannot change underneath them.
        </p>

        {/* Action Button */}
        <button
          onClick={onBack}
          style={{
            backgroundColor: '#ffffff',
            border: '0.667px solid #e4e7ec',
            borderRadius: '4px',
            padding: '8px 24px',
            fontSize: '14px',
            fontWeight: 600,
            color: '#5a6472',
            cursor: 'pointer',
            lineHeight: '20px',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f9fafb')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
          data-testid="back-to-request-btn"
        >
          Back to the request
        </button>
      </div>
    </div>
  );
};
