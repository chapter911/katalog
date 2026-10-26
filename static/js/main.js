/**
 * Main Frontend Script for Laboratorium Peralatan Diagnostik
 * Includes Notification Anti-Duplication, Gallery Interactions, and Dynamic Image Upload
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Notification System with Strict Anti-Duplication
  initNotifications();

  // 2. Initialize Catalog Detail Image Gallery
  initDetailGallery();

  // 3. Initialize Interactive Image Uploader (Min 1, Max 5 with Thumbnail Picker)
  initKatalogImageUploader();

  // 4. Initialize Clickable Catalog Cards
  initClickableCards();

  // 5. Initialize User Navigation Dropdown
  initUserDropdown();
});

/* ===================================================================
   User Navigation Dropdown (Ubah Sandi & Logout)
   =================================================================== */
function initUserDropdown() {
  const toggle = document.getElementById('userDropdownToggle');
  const menu = document.getElementById('userDropdownMenu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = menu.classList.toggle('show');
    toggle.classList.toggle('active', isOpen);
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('show');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      menu.classList.remove('show');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
}

/* ===================================================================
   Clickable Catalog Cards
   =================================================================== */
function initClickableCards() {
  const cards = document.querySelectorAll('.katalog-card[data-href]');
  cards.forEach(card => {
    card.addEventListener('click', (e) => {
      // Ignore click if originating from action buttons or forms
      if (e.target.closest('a, button, form, input')) {
        return;
      }
      const href = card.getAttribute('data-href');
      if (href) {
        window.location.href = href;
      }
    });

    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        if (e.target.closest('a, button, form, input')) {
          return;
        }
        const href = card.getAttribute('data-href');
        if (href) {
          window.location.href = href;
        }
      }
    });
  });
}

/* ===================================================================
   1. Notification System (Anti-Duplication Enforcement - Rule #1)
   =================================================================== */
function initNotifications() {
  const container = document.getElementById('notification-wrapper');
  if (!container) return;

  const seenMessages = new Set();
  const alerts = container.querySelectorAll('.toast-alert');

  alerts.forEach(alert => {
    const text = alert.querySelector('.toast-content')?.innerText.trim() || alert.innerText.trim();
    
    // Check for duplicate message
    if (seenMessages.has(text)) {
      alert.remove(); // Prevent double notification!
      return;
    }
    seenMessages.add(text);

    // Auto-dismiss after 5 seconds
    const timer = setTimeout(() => {
      dismissAlert(alert);
    }, 5000);

    // Close button handler
    const closeBtn = alert.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        clearTimeout(timer);
        dismissAlert(alert);
      });
    }
  });
}

function dismissAlert(alertElement) {
  if (!alertElement) return;
  alertElement.classList.add('fade-out');
  setTimeout(() => {
    alertElement.remove();
  }, 300);
}

/* ===================================================================
   2. Detail Page Gallery Preview & Fullscreen Image Zoom (Lightbox)
   =================================================================== */
function initDetailGallery() {
  const mainPreview = document.getElementById('mainPreviewContainer');
  const mainImg = document.getElementById('mainGalleryImage');
  const thumbs = Array.from(document.querySelectorAll('.gallery-thumb-item'));
  const lightbox = document.getElementById('imageLightboxModal');
  const lightboxImg = document.getElementById('lightboxImage');
  const lightboxCounter = document.getElementById('lightboxCounter');
  const closeBtn = document.getElementById('lightboxCloseBtn');
  const prevBtn = document.getElementById('lightboxPrevBtn');
  const nextBtn = document.getElementById('lightboxNextBtn');
  const backdrop = document.getElementById('lightboxBackdrop');

  if (!mainImg) return;

  // Build image list
  let imageList = [];
  if (thumbs.length > 0) {
    imageList = thumbs.map(t => t.getAttribute('data-full-src'));
  } else if (mainImg.src) {
    imageList = [mainImg.src];
  }

  let currentIndex = 0;

  // Switch image on thumbnail click
  thumbs.forEach((thumb, idx) => {
    thumb.addEventListener('click', () => {
      setActiveImage(idx);
    });
  });

  function setActiveImage(index) {
    if (index < 0 || index >= imageList.length) return;
    currentIndex = index;

    thumbs.forEach((t, i) => {
      t.classList.toggle('active', i === currentIndex);
    });

    const fullSrc = imageList[currentIndex];
    if (fullSrc && mainImg.src !== fullSrc) {
      mainImg.style.opacity = '0.3';
      setTimeout(() => {
        mainImg.src = fullSrc;
        mainImg.style.opacity = '1';
      }, 120);
    }

    // Sync lightbox if currently open
    if (lightbox && lightbox.classList.contains('show')) {
      updateLightboxDisplay();
    }
  }

  // Lightbox Zoom Handling
  if (lightbox && mainPreview) {
    mainPreview.addEventListener('click', () => {
      if (imageList.length > 0) {
        openLightbox();
      }
    });

    function openLightbox() {
      updateLightboxDisplay();
      lightbox.classList.add('show');
      document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
      lightbox.classList.remove('show');
      document.body.style.overflow = '';
    }

    function updateLightboxDisplay() {
      if (lightboxImg && imageList[currentIndex]) {
        lightboxImg.src = imageList[currentIndex];
      }
      if (lightboxCounter) {
        lightboxCounter.textContent = `${currentIndex + 1} / ${imageList.length}`;
      }
    }

    function showPrev() {
      const prevIdx = (currentIndex - 1 + imageList.length) % imageList.length;
      setActiveImage(prevIdx);
    }

    function showNext() {
      const nextIdx = (currentIndex + 1) % imageList.length;
      setActiveImage(nextIdx);
    }

    if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
    if (backdrop) backdrop.addEventListener('click', closeLightbox);
    if (prevBtn) prevBtn.addEventListener('click', (e) => { e.stopPropagation(); showPrev(); });
    if (nextBtn) nextBtn.addEventListener('click', (e) => { e.stopPropagation(); showNext(); });

    // Keyboard support for Lightbox
    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('show')) return;
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowLeft' && imageList.length > 1) showPrev();
      if (e.key === 'ArrowRight' && imageList.length > 1) showNext();
    });
  }
}

/* ===================================================================
   3. Interactive Catalog Image Uploader (Min 1, Max 5, Thumbnail Selector)
   =================================================================== */
function initKatalogImageUploader() {
  const fileInput = document.getElementById('katalogFileInput');
  const dropzone = document.getElementById('uploadDropzone');
  const previewContainer = document.getElementById('imagePreviews');
  const thumbnailInput = document.getElementById('chosenThumbnailInput');
  const countIndicator = document.getElementById('imageCountIndicator');

  if (!previewContainer) return;

  // Track state
  // For Create mode: files array in DataTransfer
  let dt = new DataTransfer();
  let selectedThumbIndex = 0;

  if (dropzone && fileInput) {
    // Click on dropzone to trigger file dialog
    dropzone.addEventListener('click', (e) => {
      if (e.target !== fileInput) {
        fileInput.click();
      }
    });

    // Drag & drop support
    ['dragenter', 'dragover'].forEach(event => {
      dropzone.addEventListener(event, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(event => {
      dropzone.addEventListener(event, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files) {
        handleFilesSelected(e.dataTransfer.files);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files) {
        handleFilesSelected(fileInput.files);
      }
    });
  }

  function handleFilesSelected(files) {
    const isEditMode = document.body.dataset.mode === 'edit';
    const existingCount = getRemainingExistingCount();

    const maxAllowedNew = 5 - (isEditMode ? existingCount : 0);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (!file.type.startsWith('image/')) continue;

      if (dt.items.length >= maxAllowedNew) {
        alert(`Maksimal total 5 gambar yang diizinkan.`);
        break;
      }
      dt.items.add(file);
    }

    if (fileInput) {
      fileInput.files = dt.files;
    }
    renderUploadPreviews();
  }

  function getRemainingExistingCount() {
    const existingCards = document.querySelectorAll('.preview-card[data-type="existing"]:not(.marked-delete)');
    return existingCards.length;
  }

  function renderUploadPreviews() {
    // Remove previous new file previews
    const newPreviews = previewContainer.querySelectorAll('.preview-card[data-type="new"]');
    newPreviews.forEach(el => el.remove());

    const isEditMode = document.body.dataset.mode === 'edit';

    // Render newly selected files
    for (let i = 0; i < dt.files.length; i++) {
      const file = dt.files[i];
      const card = document.createElement('div');
      card.className = 'preview-card';
      card.dataset.type = 'new';
      card.dataset.index = i;

      const isCurrentThumb = (!isEditMode && selectedThumbIndex === i) || 
                             (thumbnailInput && thumbnailInput.value === `new_${i}`);
      if (isCurrentThumb) {
        card.classList.add('is-thumbnail');
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        card.innerHTML = `
          <button type="button" class="btn-remove-preview" title="Hapus gambar">&times;</button>
          <div class="preview-img-wrap">
            <img src="${e.target.result}" alt="Preview ${i + 1}">
          </div>
          <div class="preview-actions">
            <button type="button" class="btn-set-thumb" data-thumb-target="${isEditMode ? 'new_' + i : i}">
              ${isCurrentThumb ? '⭐ Thumbnail Utama' : 'Jadikan Thumbnail'}
            </button>
          </div>
        `;

        // Remove button
        card.querySelector('.btn-remove-preview').addEventListener('click', (ev) => {
          ev.stopPropagation();
          removeNewFile(i);
        });

        // Set thumbnail button
        card.querySelector('.btn-set-thumb').addEventListener('click', (ev) => {
          ev.stopPropagation();
          setChosenThumbnail(isEditMode ? `new_${i}` : i);
        });
      };
      reader.readAsDataURL(file);
      previewContainer.appendChild(card);
    }

    updateCountStatus();
  }

  function removeNewFile(index) {
    const newDt = new DataTransfer();
    for (let i = 0; i < dt.files.length; i++) {
      if (i !== index) {
        newDt.items.add(dt.files[i]);
      }
    }
    dt = newDt;
    if (fileInput) fileInput.files = dt.files;

    if (selectedThumbIndex >= dt.files.length) {
      selectedThumbIndex = 0;
    }
    renderUploadPreviews();
  }

  function setChosenThumbnail(thumbKey) {
    const isEditMode = document.body.dataset.mode === 'edit';
    if (!isEditMode) {
      selectedThumbIndex = parseInt(thumbKey, 10) || 0;
      if (thumbnailInput) thumbnailInput.value = selectedThumbIndex;
    } else {
      if (thumbnailInput) thumbnailInput.value = thumbKey;
    }

    // Update visuals across all cards
    const allCards = previewContainer.querySelectorAll('.preview-card');
    allCards.forEach(card => {
      const type = card.dataset.type;
      const key = type === 'existing' ? `existing_${card.dataset.id}` : (isEditMode ? `new_${card.dataset.index}` : parseInt(card.dataset.index, 10));
      
      const isMatch = (!isEditMode && key === selectedThumbIndex) || (isEditMode && key === thumbKey);
      if (isMatch) {
        card.classList.add('is-thumbnail');
        const btn = card.querySelector('.btn-set-thumb');
        if (btn) btn.innerHTML = '⭐ Thumbnail Utama';
      } else {
        card.classList.remove('is-thumbnail');
        const btn = card.querySelector('.btn-set-thumb');
        if (btn) btn.innerHTML = 'Jadikan Thumbnail';
      }
    });
  }

  // Hook up existing cards in Edit Mode
  const existingCards = previewContainer.querySelectorAll('.preview-card[data-type="existing"]');
  existingCards.forEach(card => {
    const imgId = card.dataset.id;
    const deleteBtn = card.querySelector('.btn-remove-preview');
    const setThumbBtn = card.querySelector('.btn-set-thumb');

    if (deleteBtn) {
      deleteBtn.addEventListener('click', () => {
        // Toggle deletion mark
        const isMarked = card.classList.toggle('marked-delete');
        let hiddenInput = card.querySelector(`input[name="delete_image_ids"][value="${imgId}"]`);
        
        if (isMarked) {
          card.style.opacity = '0.35';
          deleteBtn.innerHTML = '&#x21bb;'; // Undo icon
          deleteBtn.title = 'Batalkan hapus';
          if (!hiddenInput) {
            hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'delete_image_ids';
            hiddenInput.value = imgId;
            card.appendChild(hiddenInput);
          }
        } else {
          card.style.opacity = '1';
          deleteBtn.innerHTML = '&times;';
          deleteBtn.title = 'Hapus gambar';
          if (hiddenInput) hiddenInput.remove();
        }
        updateCountStatus();
      });
    }

    if (setThumbBtn) {
      setThumbBtn.addEventListener('click', () => {
        if (!card.classList.contains('marked-delete')) {
          setChosenThumbnail(`existing_${imgId}`);
        }
      });
    }
  });

  function updateCountStatus() {
    if (!countIndicator) return;
    const existing = getRemainingExistingCount();
    const newFilesCount = dt.files.length;
    const total = existing + newFilesCount;

    countIndicator.innerText = `Total Gambar: ${total} / 5 (Min 1, Maks 5)`;
    if (total < 1 || total > 5) {
      countIndicator.style.color = '#ef4444';
    } else {
      countIndicator.style.color = '#10b981';
    }
  }

  // Initial count update
  updateCountStatus();
}
