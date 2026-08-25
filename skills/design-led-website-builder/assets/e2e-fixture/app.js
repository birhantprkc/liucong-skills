document.documentElement.dataset.enhanced = "";

const navToggle = document.querySelector(".nav-toggle");
const primaryNavigation = document.querySelector(".primary-nav");

if (navToggle && primaryNavigation) {
  navToggle.addEventListener("click", () => {
    const open = navToggle.getAttribute("aria-expanded") !== "true";
    navToggle.setAttribute("aria-expanded", String(open));
    primaryNavigation.toggleAttribute("data-open", open);
  });

  primaryNavigation.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      navToggle.setAttribute("aria-expanded", "false");
      primaryNavigation.removeAttribute("data-open");
    }
  });
}

const tabs = [...document.querySelectorAll('[role="tab"]')];
const panels = [...document.querySelectorAll('[role="tabpanel"]')];

function selectTab(nextTab, moveFocus = false) {
  tabs.forEach((tab) => {
    const selected = tab === nextTab;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
  });

  panels.forEach((panel) => {
    const selected = panel.id === nextTab.getAttribute("aria-controls");
    panel.classList.toggle("is-hidden", !selected);
    panel.setAttribute("aria-hidden", String(!selected));
  });

  if (moveFocus) nextTab.focus();
}

if (tabs.length && panels.length) {
  selectTab(tabs.find((tab) => tab.getAttribute("aria-selected") === "true") || tabs[0]);

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => selectTab(tab));
    tab.addEventListener("keydown", (event) => {
      let nextIndex = index;
      if (["ArrowRight", "ArrowDown"].includes(event.key)) nextIndex = (index + 1) % tabs.length;
      if (["ArrowLeft", "ArrowUp"].includes(event.key)) nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") nextIndex = 0;
      if (event.key === "End") nextIndex = tabs.length - 1;
      if (nextIndex !== index) {
        event.preventDefault();
        selectTab(tabs[nextIndex], true);
      }
    });
  });
}

const form = document.querySelector(".evaluation-form");

if (form) {
  const status = form.querySelector(".form-status");
  const fields = [...form.querySelectorAll("input, textarea")];

  const messages = {
    name: "Add a name for this fixture request.",
    email: "Enter a valid work email.",
    team: "Describe what the evaluation should prove.",
  };

  function validateField(field) {
    const valid = field.checkValidity();
    field.setAttribute("aria-invalid", String(!valid));
    const error = document.getElementById(`${field.id}-error`);
    if (error) error.textContent = valid ? "" : messages[field.id];
    return valid;
  }

  fields.forEach((field) => {
    field.addEventListener("blur", () => validateField(field));
    field.addEventListener("input", () => {
      if (field.getAttribute("aria-invalid") === "true") validateField(field);
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const firstInvalid = fields.find((field) => !validateField(field));
    if (firstInvalid) {
      status.textContent = "Review the marked fields. Nothing has been submitted.";
      status.dataset.state = "error";
      firstInvalid.focus();
      return;
    }

    status.textContent = "Fixture validated locally. No request or personal data was sent.";
    status.dataset.state = "success";
    status.focus();
  });
}
