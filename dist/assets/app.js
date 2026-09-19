// Planetarium Events App Logic
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");
  const areaChips = document.querySelectorAll("[data-filter-area]");
  const statusChips = document.querySelectorAll("[data-filter-status]");
  const bookmarkToggleBtn = document.getElementById("bookmark-toggle-btn");
  const resultCountEl = document.getElementById("result-count");
  const cards = document.querySelectorAll(".event-card");
  const emptyState = document.getElementById("empty-state");

  let currentArea = "all";
  let currentStatus = "all";
  let searchQuery = "";
  let showOnlyBookmarked = false;

  // LocalStorage for bookmarks
  const STORAGE_KEY = "planetarium_bookmarked_ids";
  let bookmarkedIds = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"));

  // Update Bookmark icons
  function updateBookmarkIcons() {
    cards.forEach(card => {
      const id = card.dataset.id;
      const btn = card.querySelector(".bookmark-btn");
      if (btn) {
        if (bookmarkedIds.has(id)) {
          btn.classList.add("bookmarked");
          btn.innerHTML = "★";
          btn.setAttribute("title", "お気に入りから削除");
        } else {
          btn.classList.remove("bookmarked");
          btn.innerHTML = "☆";
          btn.setAttribute("title", "お気に入りに追加");
        }
      }
    });

    const bookmarkCount = bookmarkedIds.size;
    const bookmarkCountSpan = document.getElementById("bookmark-count-badge");
    if (bookmarkCountSpan) {
      bookmarkCountSpan.textContent = bookmarkCount;
    }
  }

  // Toggle bookmark for single card
  window.toggleBookmark = function(id, event) {
    if (event) event.stopPropagation();
    if (bookmarkedIds.has(id)) {
      bookmarkedIds.delete(id);
    } else {
      bookmarkedIds.add(id);
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...bookmarkedIds]));
    updateBookmarkIcons();
    filterEvents();
  };

  // Filter function
  function filterEvents() {
    let visibleCount = 0;
    const query = searchQuery.toLowerCase().trim();

    cards.forEach(card => {
      const id = card.dataset.id;
      const title = (card.dataset.title || "").toLowerCase();
      const venue = (card.dataset.venue || "").toLowerCase();
      const area = (card.dataset.area || "").toLowerCase();
      const status = (card.dataset.status || "").toLowerCase();
      const desc = (card.dataset.desc || "").toLowerCase();

      // Bookmark filter
      if (showOnlyBookmarked && !bookmarkedIds.has(id)) {
        card.style.display = "none";
        return;
      }

      // Search match
      const matchesSearch = !query || 
        title.includes(query) || 
        venue.includes(query) || 
        area.includes(query) || 
        desc.includes(query);

      // Area match
      let matchesArea = true;
      if (currentArea !== "all") {
        if (currentArea === "kanto") {
          matchesArea = area.includes("東京") || area.includes("神奈川") || area.includes("千葉") || area.includes("埼玉") || area.includes("関東") || area.includes("茨城") || area.includes("群馬") || area.includes("栃木");
        } else if (currentArea === "tokyo") {
          matchesArea = area.includes("東京");
        } else if (currentArea === "kansai") {
          matchesArea = area.includes("大阪") || area.includes("京都") || area.includes("兵庫") || area.includes("近畿") || area.includes("滋賀") || area.includes("奈良");
        } else if (currentArea === "chubu") {
          matchesArea = area.includes("愛知") || area.includes("名古屋") || area.includes("岐阜") || area.includes("静岡") || area.includes("中部");
        } else if (currentArea === "other") {
          const isMajor = area.includes("東京") || area.includes("神奈川") || area.includes("埼玉") || area.includes("千葉") || area.includes("愛知") || area.includes("大阪");
          matchesArea = !isMajor;
        }
      }

      // Status match
      let matchesStatus = true;
      if (currentStatus !== "all") {
        if (currentStatus === "open") {
          matchesStatus = status.includes("開催中") || status.includes("上映中");
        } else if (currentStatus === "hot") {
          matchesStatus = status.includes("注目") || status.includes("new");
        }
      }

      if (matchesSearch && matchesArea && matchesStatus) {
        card.style.display = "flex";
        visibleCount++;
      } else {
        card.style.display = "none";
      }
    });

    if (resultCountEl) {
      resultCountEl.textContent = visibleCount;
    }

    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? "block" : "none";
    }
  }

  // Search input event
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value;
      filterEvents();
    });
  }

  // Area chips
  areaChips.forEach(chip => {
    chip.addEventListener("click", () => {
      areaChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentArea = chip.dataset.filterArea;
      filterEvents();
    });
  });

  // Status chips
  statusChips.forEach(chip => {
    chip.addEventListener("click", () => {
      statusChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentStatus = chip.dataset.filterStatus;
      filterEvents();
    });
  });

  // Bookmark toggle button
  if (bookmarkToggleBtn) {
    bookmarkToggleBtn.addEventListener("click", () => {
      showOnlyBookmarked = !showOnlyBookmarked;
      bookmarkToggleBtn.classList.toggle("active", showOnlyBookmarked);
      filterEvents();
    });
  }

  // Image error handling fallback
  document.querySelectorAll(".card-img").forEach(img => {
    img.addEventListener("error", function() {
      const parent = this.parentElement;
      if (parent) {
        this.style.display = "none";
        const placeholder = document.createElement("div");
        placeholder.className = "placeholder-img";
        placeholder.innerHTML = `
          <div class="placeholder-icon">✦</div>
          <span style="font-size:0.75rem; color:#94a3b8;">PLANETARIUM</span>
        `;
        parent.appendChild(placeholder);
      }
    });
  });

  // Initial call
  updateBookmarkIcons();
  filterEvents();
});
