(function () {
    function persistTheme(theme) {
        document.documentElement.dataset.theme = theme;
        fetch("/settings/appearance", {
            method: "POST",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            body: new URLSearchParams({ theme })
        }).catch(function (error) {
            console.error("Could not save theme preference:", error);
        });
    }

    function setupThemeButtons() {
        const light = document.querySelector(".theme-light-btn");
        const dark = document.querySelector(".theme-dark-btn");
        if (light) light.addEventListener("click", () => persistTheme("light"));
        if (dark) dark.addEventListener("click", () => persistTheme("dark"));
    }

    function setupSidebar() {
        const frame = document.querySelector(".app-frame");
        const sidebar = document.querySelector(".sidebar");
        const collapseButton = document.querySelector(".sidebar-collapse");
        const mobileButton = document.getElementById("mobileSidebarToggle");
        const overlay = document.getElementById("sidebarOverlay");
        if (!frame || !sidebar || !collapseButton) return;

        const key = "school-sidebar-collapsed";

        function isMobile() {
            return window.innerWidth <= 820;
        }

        function setMobileOpen(open) {
            if (!isMobile()) {
                sidebar.classList.remove("open");
                if (mobileButton) mobileButton.setAttribute("aria-expanded", "false");
                if (overlay) overlay.classList.remove("open");
                return;
            }
            sidebar.classList.toggle("open", open);
            if (overlay) {
                overlay.classList.toggle("open", open);
                overlay.setAttribute("aria-hidden", open ? "false" : "true");
            }
            if (mobileButton) {
                mobileButton.setAttribute("aria-expanded", open ? "true" : "false");
                mobileButton.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
                mobileButton.innerHTML = '<i class="ti ' + (open ? 'ti-x' : 'ti-menu-2') + '"></i>';
            }
        }

        if (!isMobile() && localStorage.getItem(key) === "1") {
            document.body.classList.add("sidebar-collapsed");
        }

        collapseButton.addEventListener("click", function () {
            if (isMobile()) {
                setMobileOpen(false);
                return;
            }
            document.body.classList.toggle("sidebar-collapsed");
            localStorage.setItem(key, document.body.classList.contains("sidebar-collapsed") ? "1" : "0");
        });

        if (mobileButton) {
            mobileButton.addEventListener("click", function () {
                setMobileOpen(!sidebar.classList.contains("open"));
            });
        }

        if (overlay) {
            overlay.addEventListener("click", function () {
                setMobileOpen(false);
            });
        }

        sidebar.querySelectorAll(".side-nav-link").forEach(function (link) {
            link.addEventListener("click", function () {
                if (isMobile()) setMobileOpen(false);
            });
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && isMobile()) setMobileOpen(false);
        });

        window.addEventListener("resize", function () {
            if (!isMobile()) setMobileOpen(false);
        });
    }

    function setupGlobalSearch() {
        const input = document.getElementById("globalSearchInput");
        const results = document.getElementById("globalSearchResults");
        if (!input || !results) return;
        let timer = null;

        function close() { results.classList.remove("open"); }
        function render(items) {
            if (!items.length) {
                results.innerHTML = '<div class="global-search-empty">No class or student found.</div>';
                results.classList.add("open");
                return;
            }
            results.innerHTML = items.map(function (item) {
                const icon = item.type === "class" ? "ti-school" : "ti-user";
                return '<a class="global-search-result" href="' + item.url + '"><i class="ti ' + icon + '"></i><div><strong>' + escapeHtml(item.label) + '</strong><span>' + escapeHtml(item.subtitle) + '</span></div></a>';
            }).join("");
            results.classList.add("open");
        }
        function escapeHtml(value) {
            return String(value).replace(/[&<>\"]/g, function (c) { return ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]; });
        }
        async function search() {
            const q = input.value.trim();
            if (q.length < 2) { close(); return; }
            try {
                const response = await fetch("/global-search?q=" + encodeURIComponent(q), { headers: { "X-Requested-With": "XMLHttpRequest" } });
                if (!response.ok) return;
                const data = await response.json();
                render(data.results || []);
            } catch (error) { console.error("Global search failed:", error); }
        }
        input.addEventListener("input", function () {
            clearTimeout(timer);
            timer = setTimeout(search, 180);
        });
        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                const first = results.querySelector("a");
                if (first) first.click();
                else search();
            }
            if (event.key === "Escape") close();
        });
        document.addEventListener("click", function (event) {
            if (!event.target.closest("#globalSearchWrap")) close();
        });
    }

    function setupFlashDismiss() {
        document.querySelectorAll(".flash-stack .flash").forEach(function (el) {
            el.addEventListener("animationend", function (event) {
                if (event.animationName === "flash-out") el.remove();
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        setupThemeButtons();
        setupSidebar();
        setupGlobalSearch();
        setupFlashDismiss();
    });
})();