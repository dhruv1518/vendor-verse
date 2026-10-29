/**
 * Vendora Admin Console — In-App Modal & Interactive UX System
 * Replaces browser Chrome popups (window.open) with seamless in-app modals.
 */

(function () {
    'use strict';

    // --- State & DOM References ---
    let modalBackdrop = null;
    let modalDialog = null;
    let modalIframe = null;
    let modalSpinner = null;
    let modalTitle = null;
    let toastContainer = null;
    let activeTriggerLink = null;

    // --- Pure Light Theme Enforcement ---
    function initTheme() {
        try {
            localStorage.removeItem('vv_admin_theme');
        } catch (e) {}
        document.documentElement.setAttribute('data-theme', 'light');
        if (document.body) {
            document.body.classList.remove('theme-dark');
            document.body.setAttribute('data-theme', 'light');
        }
    }

    // --- In-App Toast Notification System ---
    function ensureToastContainer() {
        if (!toastContainer) {
            toastContainer = document.getElementById('vv-toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'vv-toast-container';
                document.body.appendChild(toastContainer);
            }
        }
    }

    function showToast(message, type = 'success') {
        ensureToastContainer();
        const toast = document.createElement('div');
        toast.className = 'vv-toast';

        let iconSvg = '';
        if (type === 'success') {
            iconSvg = '<svg class="vv-app-svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>';
        } else if (type === 'warning') {
            iconSvg = '<svg class="vv-app-svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" /></svg>';
        } else if (type === 'error') {
            iconSvg = '<svg class="vv-app-svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>';
        } else {
            iconSvg = '<svg class="vv-app-svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" /></svg>';
        }

        toast.innerHTML = `
            <div class="vv-toast-icon ${type}">${iconSvg}</div>
            <div class="vv-toast-msg">${message}</div>
        `;
        toastContainer.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('is-visible');
        });

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('is-visible');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3500);
    }
    window.showAdminToast = showToast;

    // --- In-App Modal Creation ---
    function ensureModal() {
        if (modalBackdrop) return;

        modalBackdrop = document.createElement('div');
        modalBackdrop.id = 'vv-modal-backdrop';

        modalBackdrop.innerHTML = `
            <div id="vv-modal-dialog" role="dialog" aria-modal="true">
                <div id="vv-modal-header">
                    <div class="vv-modal-title-wrap">
                        <div class="vv-modal-icon">
                            <svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                            </svg>
                        </div>
                        <h3 class="vv-modal-title" id="vv-modal-title-text">Vendora Object Manager</h3>
                    </div>
                    <div class="vv-modal-actions">
                        <button type="button" class="vv-modal-btn" id="vv-modal-expand-btn" title="Toggle Fullscreen">
                            <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
                            </svg>
                        </button>
                        <button type="button" class="vv-modal-btn close" id="vv-modal-close-btn" title="Close (Esc)">
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="vv-modal-body">
                    <div id="vv-modal-spinner">
                        <div class="vv-spinner-ring"></div>
                        <span style="font-size: 13px; font-weight: 600; color: var(--body-quiet-color);">Loading workspace...</span>
                    </div>
                    <iframe id="vv-modal-iframe" name="vv-modal-frame" src="about:blank"></iframe>
                </div>
            </div>
        `;

        document.body.appendChild(modalBackdrop);

        modalDialog = document.getElementById('vv-modal-dialog');
        modalIframe = document.getElementById('vv-modal-iframe');
        modalSpinner = document.getElementById('vv-modal-spinner');
        modalTitle = document.getElementById('vv-modal-title-text');

        // Close button
        document.getElementById('vv-modal-close-btn').addEventListener('click', closeModal);

        // Click outside on backdrop closes
        modalBackdrop.addEventListener('click', (e) => {
            if (e.target === modalBackdrop) {
                closeModal();
            }
        });

        // Expand / Toggle Fullscreen button
        document.getElementById('vv-modal-expand-btn').addEventListener('click', () => {
            const isFull = modalDialog.style.width === '98%';
            if (isFull) {
                modalDialog.style.width = '90%';
                modalDialog.style.maxWidth = '980px';
                modalDialog.style.height = '85vh';
            } else {
                modalDialog.style.width = '98%';
                modalDialog.style.maxWidth = '98vw';
                modalDialog.style.height = '96vh';
            }
        });

        // Iframe load listener
        modalIframe.addEventListener('load', () => {
            modalSpinner.classList.add('is-hidden');
            try {
                // Attach parent opener reference so child window JavaScript works identically
                if (modalIframe.contentWindow) {
                    modalIframe.contentWindow.opener = window;
                }
                // Try grabbing title from child document
                if (modalIframe.contentDocument && modalIframe.contentDocument.title) {
                    const docTitle = modalIframe.contentDocument.title.split('|')[0].trim();
                    if (docTitle) {
                        modalTitle.textContent = docTitle;
                    }
                }
            } catch (err) {
                // Cross-origin restriction fallback
            }
        });

        // Esc key closes modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modalBackdrop.classList.contains('is-open')) {
                closeModal();
            }
        });
    }

    function openInAppModal(url, title = 'Manage Object', triggerLink = null) {
        ensureModal();
        activeTriggerLink = triggerLink;

        // Ensure _popup=1 is in the URL
        let targetUrl = url;
        if (targetUrl.indexOf('?') === -1) {
            targetUrl += '?_popup=1';
        } else if (!targetUrl.includes('_popup=1')) {
            targetUrl += '&_popup=1';
        }

        modalTitle.textContent = title;
        modalSpinner.classList.remove('is-hidden');
        modalIframe.src = targetUrl;
        modalBackdrop.classList.add('is-open');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        if (!modalBackdrop) return;
        modalBackdrop.classList.remove('is-open');
        document.body.style.overflow = '';
        setTimeout(() => {
            if (modalIframe) {
                modalIframe.src = 'about:blank';
            }
            activeTriggerLink = null;
        }, 250);
    }

    // --- Monkey-patch Django Admin Popup Callbacks ---
    // Django uses these global functions to close popups and update related fields
    const originalDismissAdd = window.dismissAddRelatedObjectPopup;
    const originalDismissChange = window.dismissChangeRelatedObjectPopup;
    const originalDismissDelete = window.dismissDeleteRelatedObjectPopup;

    window.dismissAddRelatedObjectPopup = function (win, newId, newRepr) {
        if (originalDismissAdd) {
            try { originalDismissAdd(win, newId, newRepr); } catch (e) { console.warn(e); }
        }
        closeModal();
        showToast(`Successfully added: "${newRepr || newId}"`, 'success');
    };

    window.dismissChangeRelatedObjectPopup = function (win, objId, newRepr, newId) {
        if (originalDismissChange) {
            try { originalDismissChange(win, objId, newRepr, newId); } catch (e) { consolewarn(e); }
        }
        closeModal();
        showToast(`Successfully updated: "${newRepr || objId}"`, 'success');
    };

    window.dismissDeleteRelatedObjectPopup = function (win, objId) {
        if (originalDismissDelete) {
            try { originalDismissDelete(win, objId); } catch (e) { console.warn(e); }
        }
        closeModal();
        showToast('Item deleted successfully', 'warning');
    };

    // --- Intercept Related Object Popup Links ---
    function interceptPopupTriggers() {
        document.addEventListener('click', function (e) {
            // Only intercept actual Django ForeignKey popup buttons (inside .related-widget-wrapper or with data-modal)
            const link = e.target.closest('.related-widget-wrapper a.related-widget-wrapper-link, .related-widget-wrapper a.add-related, .related-widget-wrapper a.change-related, .related-widget-wrapper a.delete-related, .related-widget-wrapper a.view-related, a[data-modal="true"]');
            if (link && link.href) {
                e.preventDefault();
                e.stopPropagation();

                let title = 'Manage Object';
                if (link.classList.contains('add-related')) {
                    title = 'Add New Item';
                } else if (link.classList.contains('change-related')) {
                    title = 'Change Item';
                } else if (link.classList.contains('delete-related')) {
                    title = 'Delete Item';
                } else if (link.classList.contains('view-related')) {
                    title = 'View Item Details';
                }

                openInAppModal(link.href, title, link);
                return false;
            }
        }, true);
    }

    // --- Intercept window.open for any _popup=1 calls ---
    const originalWindowOpen = window.open;
    window.open = function (url, name, specs) {
        if (url && typeof url === 'string' && url.includes('_popup=1')) {
            openInAppModal(url, 'Manage Object');
            // Return dummy object with focus/close methods so Django popup scripts don't throw error
            return {
                focus: function () {},
                close: function () { closeModal(); },
                closed: false
            };
        }
        return originalWindowOpen.apply(window, arguments);
    };

    function initMobileMenu() {
        const toggleBtn = document.getElementById('vv-menu-toggle');
        const sidebar = document.getElementById('vv-sidebar');
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('is-open');
            });
        }
    }

    // --- Modernize & Polish Admin Interface Elements ---
    function enhanceAdminUI() {
        // 1. Clean up duplicate object tools in content-main
        try {
            const bannerTools = document.querySelector('.vv-page-title-banner .object-tools');
            const mainTools = document.querySelectorAll('#content-main > .object-tools, #content-main > ul.object-tools');
            if (bannerTools && mainTools.length > 0) {
                mainTools.forEach(el => el.remove());
            }
        } catch (e) {}

        // 2. Set modern placeholder on changelist search bar
        const searchbar = document.getElementById('searchbar');
        if (searchbar && (!searchbar.placeholder || searchbar.placeholder === '')) {
            searchbar.placeholder = 'Search records (name, sku, vendor, keywords)...';
        }

        // 3. Beautify changelist main heading
        const mainTitle = document.querySelector('.vv-main-title');
        if (mainTitle && mainTitle.textContent) {
            const text = mainTitle.textContent.trim();
            // E.g., "Select product to change" -> "Products Directory"
            const selectMatch = text.match(/^Select\s+(.+?)\s+to\s+change$/i);
            if (selectMatch && selectMatch[1]) {
                const modelName = selectMatch[1].charAt(0).toUpperCase() + selectMatch[1].slice(1);
                mainTitle.textContent = `${modelName} Directory`;
            }
        }

        // 4. Transform plain-text status table cells into modern status pills
        const statusMap = {
            success: ['active', 'published', 'completed', 'delivered', 'paid', 'approved', 'verified', 'yes'],
            warning: ['draft', 'pending', 'processing', 'unpaid', 'in review', 'in_review', 'low stock'],
            danger: ['archived', 'cancelled', 'refunded', 'failed', 'rejected', 'inactive', 'no', 'out of stock']
        };

        const resultRows = document.querySelectorAll('#result_list tbody tr');
        resultRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach(cell => {
                // Skip if cell contains form elements or links
                if (cell.querySelector('input, select, textarea, a, button, img, svg')) return;
                const rawText = cell.textContent.trim().toLowerCase();
                if (!rawText || rawText.length > 25) return;

                let category = null;
                if (statusMap.success.includes(rawText)) {
                    category = 'success';
                } else if (statusMap.warning.includes(rawText)) {
                    category = 'warning';
                } else if (statusMap.danger.includes(rawText)) {
                    category = 'danger';
                }

                if (category) {
                    const displayLabel = cell.textContent.trim();
                    cell.innerHTML = `<span class="vv-badge-status ${category}"><span class="vv-badge-dot"></span>${displayLabel}</span>`;
                }
            });
        });

        // 5. Enhance Filter sidebar with badge counts if available
        const filterItems = document.querySelectorAll('#changelist-filter li.selected a');
        filterItems.forEach(item => {
            if (!item.querySelector('.vv-filter-active-tag')) {
                const checkTag = document.createElement('span');
                checkTag.className = 'vv-filter-active-tag';
                checkTag.style.cssText = 'font-size: 11px; font-weight: 800; color: #4f46e5; margin-left: auto;';
                item.appendChild(checkTag);
            }
        });
    }

    // --- Dashboard Live Search & Command Palette ---
    function initDashboardToolbar() {
        const searchInput = document.getElementById('vv-dash-quick-filter');
        const clearBtn = document.getElementById('vv-dash-search-clear');
        const dropdown = document.getElementById('vv-dash-search-dropdown');
        const noModulesBox = document.getElementById('vv-dash-no-modules');
        const emptyQueryEl = document.getElementById('vv-empty-query');
        const emptyEqTexts = document.querySelectorAll('.vv-eq-text');
        const emptyProdLink = document.getElementById('vv-empty-prod-link');
        const emptyOrderLink = document.getElementById('vv-empty-order-link');
        const emptyUserLink = document.getElementById('vv-empty-user-link');
        const tabBtns = document.querySelectorAll('.vv-cat-tab');
        const appCards = document.querySelectorAll('.vv-app-card');

        if (!searchInput && tabBtns.length === 0) return;

        let activeCategory = 'all';

        function renderDropdown(query) {
            if (!dropdown) return;
            if (!query) {
                dropdown.style.display = 'none';
                dropdown.innerHTML = '';
                return;
            }

            const enc = encodeURIComponent(query);
            const safeQuery = query.replace(/[<>&"]/g, '');

            // 1. Gather any matching dashboard module links
            const matchingModels = [];
            const allModelLinks = document.querySelectorAll('.vv-model-item');
            allModelLinks.forEach(item => {
                const name = (item.getAttribute('data-model-name') || '').toLowerCase();
                if (name && name.includes(query.toLowerCase())) {
                    const link = item.querySelector('a.vv-model-tile-link');
                    if (link) {
                        matchingModels.push({
                            title: item.querySelector('.vv-model-title')?.textContent?.trim() || name,
                            url: link.href
                        });
                    }
                }
            });

            let html = `
                <div class="vv-dropdown-section-title">Search Marketplace Records</div>
                <a href="/admin/products/product/?q=${enc}" class="vv-dropdown-item primary">
                    <span class="vv-dd-icon">🛍️</span>
                    <span class="vv-dd-text">Search <strong>Products</strong> for &ldquo;${safeQuery}&rdquo;</span>
                    <span class="vv-dd-arrow">&rarr;</span>
                </a>
                <a href="/admin/orders/order/?q=${enc}" class="vv-dropdown-item">
                    <span class="vv-dd-icon">📦</span>
                    <span class="vv-dd-text">Search <strong>Orders</strong> for &ldquo;${safeQuery}&rdquo;</span>
                    <span class="vv-dd-arrow">&rarr;</span>
                </a>
                <a href="/admin/accounts/user/?q=${enc}" class="vv-dropdown-item">
                    <span class="vv-dd-icon">👥</span>
                    <span class="vv-dd-text">Search <strong>Customers &amp; Users</strong> for &ldquo;${safeQuery}&rdquo;</span>
                    <span class="vv-dd-arrow">&rarr;</span>
                </a>
                <a href="/admin/vendors/vendor/?q=${enc}" class="vv-dropdown-item">
                    <span class="vv-dd-icon">🏪</span>
                    <span class="vv-dd-text">Search <strong>Vendors</strong> for &ldquo;${safeQuery}&rdquo;</span>
                    <span class="vv-dd-arrow">&rarr;</span>
                </a>
            `;

            if (matchingModels.length > 0) {
                html += `<div class="vv-dropdown-section-title" style="margin-top: 6px;">Matching Admin Modules (${matchingModels.length})</div>`;
                matchingModels.slice(0, 5).forEach(m => {
                    html += `
                        <a href="${m.url}" class="vv-dropdown-item">
                            <span class="vv-dd-icon">📂</span>
                            <span class="vv-dd-text">${m.title}</span>
                            <span class="vv-dd-arrow">&rarr;</span>
                        </a>
                    `;
                });
            }

            dropdown.innerHTML = html;
            dropdown.style.display = 'block';
        }

        function filterDashboard() {
            const query = searchInput ? searchInput.value.trim().toLowerCase() : '';

            // Toggle clear button
            if (clearBtn) {
                clearBtn.style.display = query ? 'flex' : 'none';
            }

            // Update empty state text & links
            if (query) {
                if (emptyQueryEl) emptyQueryEl.textContent = query;
                emptyEqTexts.forEach(el => el.textContent = query);
                if (emptyProdLink) emptyProdLink.href = `/admin/products/product/?q=${encodeURIComponent(query)}`;
                if (emptyOrderLink) emptyOrderLink.href = `/admin/orders/order/?q=${encodeURIComponent(query)}`;
                if (emptyUserLink) emptyUserLink.href = `/admin/accounts/user/?q=${encodeURIComponent(query)}`;
            }

            renderDropdown(query);

            let visibleCards = 0;
            appCards.forEach(card => {
                const cardCat = card.getAttribute('data-category') || 'other';
                const cardName = card.getAttribute('data-app-name') || '';
                const models = card.querySelectorAll('.vv-model-item');

                let catMatch = (activeCategory === 'all' || cardCat === activeCategory);
                let modelMatchCount = 0;

                models.forEach(model => {
                    const modelName = model.getAttribute('data-model-name') || '';
                    if (!query || modelName.includes(query) || cardName.includes(query)) {
                        model.style.display = '';
                        modelMatchCount++;
                    } else {
                        model.style.display = 'none';
                    }
                });

                if (catMatch && (!query || modelMatchCount > 0 || cardName.includes(query))) {
                    card.style.display = '';
                    visibleCards++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (noModulesBox) {
                if (query && visibleCards === 0) {
                    noModulesBox.style.display = 'block';
                } else {
                    noModulesBox.style.display = 'none';
                }
            }
        }

        if (searchInput) {
            searchInput.addEventListener('input', filterDashboard);
            searchInput.addEventListener('focus', () => {
                if (searchInput.value.trim()) {
                    renderDropdown(searchInput.value.trim().toLowerCase());
                }
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (searchInput) {
                    searchInput.value = '';
                    filterDashboard();
                    searchInput.focus();
                }
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (dropdown && !e.target.closest('#vv-dash-search-form')) {
                dropdown.style.display = 'none';
            }
        });

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeCategory = btn.getAttribute('data-cat') || 'all';
                filterDashboard();
            });
        });
    }

    // --- Initialize on DOMContentLoaded ---
    function init() {
        initTheme();
        interceptPopupTriggers();
        initMobileMenu();
        enhanceAdminUI();
        initDashboardToolbar();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

