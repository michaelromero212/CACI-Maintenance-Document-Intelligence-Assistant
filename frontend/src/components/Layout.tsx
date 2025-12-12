import { Outlet, NavLink } from 'react-router-dom';

export default function Layout() {
    return (
        <div className="app-layout">
            {/* Classification Banner - Demo Only */}
            <div className="classification-banner">
                UNCLASSIFIED // FOR OFFICIAL USE ONLY - DEMONSTRATION SYSTEM
            </div>

            <nav className="nav" role="navigation" aria-label="Main navigation">
                <div className="nav-container">
                    <NavLink to="/" className="nav-brand">
                        {/* Shield/Document Icon */}
                        <svg
                            width="36"
                            height="36"
                            viewBox="0 0 36 36"
                            fill="none"
                            aria-hidden="true"
                        >
                            <path
                                d="M18 3L4 9v9c0 8.28 5.98 16.02 14 18 8.02-1.98 14-9.72 14-18V9L18 3z"
                                fill="#14919b"
                                stroke="white"
                                strokeWidth="1.5"
                            />
                            <rect x="11" y="12" width="14" height="2" rx="1" fill="white" />
                            <rect x="11" y="16" width="10" height="2" rx="1" fill="white" />
                            <rect x="11" y="20" width="12" height="2" rx="1" fill="white" />
                            <rect x="11" y="24" width="8" height="2" rx="1" fill="white" />
                        </svg>
                        <div className="nav-brand-text">
                            <span className="nav-brand-title">MDIA</span>
                            <span className="nav-brand-subtitle">Maintenance Document Intelligence</span>
                        </div>
                    </NavLink>

                    <ul className="nav-links">
                        <li>
                            <NavLink
                                to="/"
                                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                                end
                            >
                                Dashboard
                            </NavLink>
                        </li>
                        <li>
                            <NavLink
                                to="/upload"
                                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                            >
                                Upload
                            </NavLink>
                        </li>
                        <li>
                            <NavLink
                                to="/status-board"
                                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                            >
                                Status Board
                            </NavLink>
                        </li>
                    </ul>
                </div>
            </nav>

            <main className="container" style={{ padding: 'var(--spacing-4) var(--spacing-6)' }}>
                <Outlet />
            </main>

            <footer className="app-footer">
                <p>
                    Maintenance Document Intelligence Assistant v1.0.0 |
                    MSC N7 Modernization Program |
                    CACI International
                </p>
            </footer>
        </div>
    );
}
