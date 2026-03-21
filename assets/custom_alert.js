// Custom Alert Module

function getCustomAlertHTML() {
  return `
    <div id="customAlertOverlay" class="custom-alert-overlay">
      <div class="custom-alert-box">
        <div id="customAlertIcon" class="custom-alert-icon"></div>
        <div id="customAlertMessage" class="custom-alert-message"></div>
        <button id="customAlertConfirmBtn" class="custom-alert-btn">OK</button>
      </div>
    </div>
  `;
}

function initCustomAlert() {
  if (!document.getElementById("customAlertOverlay")) {
    document.body.insertAdjacentHTML('beforeend', getCustomAlertHTML());
  }
}

// Global Override for alert
window.originalAlert = window.alert;

// showCustomAlert returns a promise allowing you to await it.
function showCustomAlert(message) {
  return new Promise((resolve) => {
    initCustomAlert();

    // Check if the message contains typical error keywords
    const isError = /error|invalid|denied|failed|wrong|match|not found/i.test(message);

    const iconDiv = document.getElementById('customAlertIcon');
    iconDiv.innerHTML = isError ? '&#10006;' : '&#10004;';
    iconDiv.className = isError ? 'custom-alert-icon error' : 'custom-alert-icon success';

    document.getElementById('customAlertMessage').innerText = message;
    
    const overlay = document.getElementById('customAlertOverlay');
    const btn = document.getElementById('customAlertConfirmBtn');

    // Force reflow for animation reset if needed
    overlay.style.display = 'block';

    btn.onclick = function() {
      overlay.style.display = 'none';
      resolve();
    };
  });
}

// Optional: override default alert to map to showCustomAlert
// We do not await this, so execution will continue immediately if they just call alert().
window.alert = function(message) {
  showCustomAlert(message);
};

window.addEventListener("DOMContentLoaded", initCustomAlert);
