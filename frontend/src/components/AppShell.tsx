import React from 'react';
import { 
  FileText, 
  PlusCircle, 
  CheckSquare, 
  BarChart3, 
  Search, 
  Building2, 
  Package, 
  ShieldCheck, 
  LogOut,
  User as UserIcon,
  AlertTriangle
} from 'lucide-react';
import { AuthenticatedUser } from '../api/client';

export type NavItemKey = 
  | 'purchase-requests' 
  | 'new-request' 
  | 'approvals' 
  | 'budget-review' 
  | 'sourcing' 
  | 'suppliers' 
  | 'purchase-orders' 
  | 'audit-trail';

/** Roles that are permitted to see/use a given nav item */
export type UserRole = 'EMPLOYEE' | 'MANAGER' | 'PROCUREMENT' | 'FINANCE' | 'ADMIN';

/** Returns true when the current user role is allowed to access the given nav key */
export function canAccessTab(role: UserRole | undefined, tab: NavItemKey): boolean {
  if (!role) return false;
  if (role === 'ADMIN') return true;
  const matrix: Record<NavItemKey, UserRole[]> = {
    'purchase-requests': ['EMPLOYEE', 'MANAGER', 'PROCUREMENT', 'FINANCE'],
    'new-request':       ['EMPLOYEE'],
    'approvals':         ['MANAGER'],
    'budget-review':     ['FINANCE'],
    'sourcing':          ['PROCUREMENT', 'FINANCE', 'MANAGER', 'EMPLOYEE'],
    'suppliers':         ['PROCUREMENT'],
    'purchase-orders':   ['EMPLOYEE', 'MANAGER', 'PROCUREMENT', 'FINANCE'],
    'audit-trail':       ['EMPLOYEE', 'MANAGER', 'PROCUREMENT', 'FINANCE'],
  };
  return matrix[tab]?.includes(role) ?? false;
}

/** Sidebar menu items visible per role (maintains clean, role-tailored sidebar menu) */
const sidebarVisibilityMatrix: Record<NavItemKey, UserRole[]> = {
  'purchase-requests': ['EMPLOYEE', 'MANAGER', 'PROCUREMENT', 'FINANCE'],
  'new-request':       ['EMPLOYEE'],
  'approvals':         ['MANAGER'],
  'budget-review':     ['FINANCE'],
  'sourcing':          ['PROCUREMENT'],
  'suppliers':         ['PROCUREMENT'],
  'purchase-orders':   ['EMPLOYEE', 'MANAGER', 'PROCUREMENT', 'FINANCE'],
  'audit-trail':       ['EMPLOYEE', 'MANAGER', 'PROCUREMENT', 'FINANCE'],
};

interface AppShellProps {
  currentTab: NavItemKey;
  onNavigate: (tab: NavItemKey) => void;
  user: AuthenticatedUser | null;
  onLogout: () => void;
  children: React.ReactNode;
  counts?: {
    prs?: number;
    approvals?: number;
    budget?: number;
    sourcing?: number;
    pos?: number;
  };
}

export const AppShell: React.FC<AppShellProps> = ({
  currentTab,
  onNavigate,
  user,
  onLogout,
  children,
  counts = { prs: 3, approvals: 1, budget: 1, sourcing: 3, pos: 1 }
}) => {
  const allNavItems = [
    {
      key: 'purchase-requests' as NavItemKey,
      label: 'Purchase requests',
      icon: FileText,
      count: counts.prs,
    },
    {
      key: 'new-request' as NavItemKey,
      label: 'New request',
      icon: PlusCircle,
    },
    {
      key: 'approvals' as NavItemKey,
      label: 'Approvals',
      icon: CheckSquare,
      count: counts.approvals,
    },
    {
      key: 'budget-review' as NavItemKey,
      label: 'Budget review',
      icon: BarChart3,
      count: counts.budget,
    },
    {
      key: 'sourcing' as NavItemKey,
      label: 'Sourcing',
      icon: Search,
      count: counts.sourcing,
    },
    {
      key: 'suppliers' as NavItemKey,
      label: 'Suppliers',
      icon: Building2,
    },
    {
      key: 'purchase-orders' as NavItemKey,
      label: 'Purchase orders',
      icon: Package,
      count: counts.pos,
    },
    {
      key: 'audit-trail' as NavItemKey,
      label: 'Audit Trail',
      icon: ShieldCheck,
    },
  ];

  // Filter nav items to only show menu items intended for current role in the sidebar
  const navItems = allNavItems.filter((item) => {
    if (!user?.role || user.role === 'ADMIN') return true;
    return sidebarVisibilityMatrix[item.key]?.includes(user.role as UserRole) ?? false;
  });

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f5f6f8' }} data-testid="app-shell">
      {/* 256px Fixed Sidebar matching Figma spec */}
      <aside
        style={{
          width: '256px',
          minWidth: '256px',
          backgroundColor: '#ffffff',
          borderRight: '0.667px solid #e4e7ec',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '16px 8px 16px 8px',
          position: 'sticky',
          top: 0,
          height: '100vh',
          boxSizing: 'border-box',
          overflowY: 'auto',
          zIndex: 10,
        }}
        data-testid="sidebar"
      >
        <div>
          {/* Brand Header */}
          <div style={{ padding: '0 8px 16px 8px', borderBottom: '0.667px solid #f0f2f5' }}>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#12161c', letterSpacing: '-0.3px' }}>
              Procure
            </div>
            <div style={{ fontSize: '11px', color: '#8a929e', marginTop: '2px' }}>
              Request &amp; approval
            </div>
          </div>

          {/* Navigation Menu List */}
          <nav style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {navItems.map((item) => {
              const isActive = currentTab === item.key;
              const IconComponent = item.icon;
              return (
                <button
                  key={item.key}
                  onClick={() => onNavigate(item.key)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    width: '100%',
                    height: '36px',
                    padding: '0 10px',
                    borderRadius: '4px',
                    border: 'none',
                    backgroundColor: isActive ? '#eef1ff' : 'transparent',
                    color: isActive ? '#2f3789' : '#5a6472',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontFamily: 'inherit',
                    fontSize: '13px',
                    fontWeight: isActive ? 600 : 500,
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = '#f8fafc';
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  data-testid={`nav-${item.key}`}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <IconComponent size={16} color={isActive ? '#2f3789' : '#5a6472'} style={{ flexShrink: 0 }} />
                    <span style={{ whiteSpace: 'nowrap' }}>
                      {item.label}
                    </span>
                  </div>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
                    {item.count !== undefined && item.count > 0 && (
                      <span
                        style={{
                          backgroundColor: isActive ? '#ffffff' : '#f5f6f8',
                          color: '#5a6472',
                          fontSize: '11px',
                          fontWeight: 600,
                          minWidth: '18px',
                          height: '16px',
                          borderRadius: '4px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: '0 4px',
                        }}
                      >
                        {item.count}
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer: Prototype Notes + User Profile */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Prototype assumptions card from Figma frame 9:642 */}
          <div
            style={{
              backgroundColor: '#fbfcfd',
              border: '0.667px solid #e4e7ec',
              borderRadius: '4px',
              padding: '12px',
              fontSize: '11px',
            }}
          >
            <div
              style={{
                fontSize: '11px',
                fontWeight: 600,
                color: '#8a929e',
                letterSpacing: '0.275px',
                marginBottom: '4px',
                textTransform: 'uppercase',
              }}
            >
              Prototype
            </div>
            <p style={{ margin: 0, color: '#5a6472', fontSize: '11px', lineHeight: '16px' }}>
              Sample data only. The assistant never approves a request or selects a supplier — it produces recommendations that a person accepts or overrides.
            </p>
          </div>

          {/* User Session Profile & Logout */}
          <div
            style={{
              borderTop: '0.667px solid #e4e7ec',
              paddingTop: '12px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: '#eef1ff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#2f3789',
                  fontWeight: 600,
                  fontSize: '13px',
                }}
              >
                {user?.name ? user.name.charAt(0) : <UserIcon size={16} />}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: '#12161c',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {user?.name || 'Khách'}
                </div>
                <div
                  style={{
                    fontSize: '11px',
                    color: '#8a929e',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {user?.email || 'Chưa đăng nhập'}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '4px' }}>
              <span className={`badge ${user?.role === 'ADMIN' ? 'badge-error' : user?.role === 'MANAGER' ? 'badge-warning' : 'badge-pending'}`}>
                {user?.role || 'GUEST'}
              </span>
              <button
                onClick={onLogout}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '12px',
                  color: '#8a929e',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px 6px',
                  borderRadius: '4px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#8e1e1e';
                  e.currentTarget.style.backgroundColor = '#fdecec';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#8a929e';
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
                title="Đăng xuất"
                data-testid="logout-button"
              >
                <LogOut size={14} />
                <span>Đăng xuất</span>
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main
        style={{
          flex: 1,
          padding: '32px',
          boxSizing: 'border-box',
          minWidth: 0,
          maxWidth: '1200px',
        }}
        data-testid="main-content"
      >
        {children}
      </main>
    </div>
  );
};
