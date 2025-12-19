// Translation dictionaries
const translations = {
  en: {
    "school-name": "Mergington High School",
    "page-title": "Extracurricular Activities",
    "available-activities": "Available Activities",
    "signup-title": "Sign Up for an Activity",
    "email-label": "Student Email:",
    "email-placeholder": "your-email@mergington.edu",
    "activity-label": "Select Activity:",
    "select-activity": "-- Select an activity --",
    "signup-button": "Sign Up",
    "loading": "Loading activities...",
    "footer-text": "© 2023 Mergington High School",
    "schedule": "Schedule:",
    "availability": "Availability:",
    "spots-left": "spots left",
    "current-participants": "Current Participants:",
    "no-participants": "No participants yet. Be the first to sign up!",
    "delete-button": "Delete",
    "confirm-unregister": "Are you sure you want to unregister {email} from {activity}?",
    "error-load-activities": "Failed to load activities. Please try again later.",
    "error-generic": "An error occurred",
    "error-signup": "Failed to sign up. Please try again.",
    "error-unregister-participant": "Failed to unregister participant",
    "error-unregister": "Failed to unregister. Please try again."
  },
  hu: {
    "school-name": "Mergington Középiskola",
    "page-title": "Tanórán Kívüli Tevékenységek",
    "available-activities": "Elérhető Tevékenységek",
    "signup-title": "Jelentkezés Tevékenységre",
    "email-label": "Diák Email címe:",
    "email-placeholder": "email-cimed@mergington.edu",
    "activity-label": "Válassz Tevékenységet:",
    "select-activity": "-- Válassz egy tevékenységet --",
    "signup-button": "Jelentkezés",
    "loading": "Tevékenységek betöltése...",
    "footer-text": "© 2023 Mergington Középiskola",
    "schedule": "Időpont:",
    "availability": "Elérhetőség:",
    "spots-left": "hely maradt",
    "current-participants": "Jelenlegi Résztvevők:",
    "no-participants": "Még nincsenek résztvevők. Légy te az első!",
    "delete-button": "Törlés",
    "confirm-unregister": "Biztosan ki szeretnéd jelenteni {email}-t a(z) {activity} tevékenységből?",
    "error-load-activities": "Nem sikerült betölteni a tevékenységeket. Kérlek próbáld újra később.",
    "error-generic": "Hiba történt",
    "error-signup": "Nem sikerült a jelentkezés. Kérlek próbáld újra.",
    "error-unregister-participant": "Nem sikerült kijelentkeztetni a résztvevőt",
    "error-unregister": "Nem sikerült a kijelentkezés. Kérlek próbáld újra."
  }
};

// Current language
let currentLang = localStorage.getItem("lang") || "en";

// Function to translate text on the page
function translatePage(lang) {
  currentLang = lang;
  localStorage.setItem("lang", lang);
  document.documentElement.lang = lang;

  // Translate all elements with data-i18n attribute
  document.querySelectorAll("[data-i18n]").forEach(element => {
    const key = element.getAttribute("data-i18n");
    if (translations[lang] && translations[lang][key]) {
      if (element.tagName === "INPUT" && element.type === "submit") {
        element.value = translations[lang][key];
      } else {
        element.textContent = translations[lang][key];
      }
    }
  });

  // Translate placeholder attributes
  document.querySelectorAll("[data-i18n-placeholder]").forEach(element => {
    const key = element.getAttribute("data-i18n-placeholder");
    if (translations[lang] && translations[lang][key]) {
      element.placeholder = translations[lang][key];
    }
  });

  // Update flag button active state
  document.querySelectorAll(".flag-btn").forEach(btn => {
    if (btn.dataset.lang === lang) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });
}

// Function to get translated text
function t(key, replacements = {}) {
  let text = translations[currentLang][key] || key;
  Object.keys(replacements).forEach(replaceKey => {
    text = text.replace(`{${replaceKey}}`, replacements[replaceKey]);
  });
  return text;
}

document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Initialize language on page load
  translatePage(currentLang);

  // Handle language switcher clicks
  document.querySelectorAll(".flag-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const selectedLang = btn.dataset.lang;
      // Skip if same language is already selected
      if (selectedLang === currentLang) {
        return;
      }
      translatePage(selectedLang);
      fetchActivities();
    });
  });

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch(`/activities?lang=${currentLang}`);
      const activities = await response.json();

      // Clear loading message and select options
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = `<option value="" data-i18n="select-activity">${t("select-activity")}</option>`;

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsList = details.participants.length > 0
          ? `<ul class="participants-list" data-activity="${name}">
              ${details.participants.map(email => `
                <li>
                  <span>${email}</span>
                  <button class="delete-btn" data-email="${email}" data-activity="${name}" aria-label="Remove ${email} from ${name}">${t("delete-button")}</button>
                </li>
              `).join('')}
             </ul>`
          : `<p class="no-participants">${t("no-participants")}</p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>${t("schedule")}</strong> ${details.schedule}</p>
          <p><strong>${t("availability")}</strong> ${spotsLeft} ${t("spots-left")}</p>
          <div class="participants-section">
            <p class="participants-header"><strong>${t("current-participants")}</strong></p>
            ${participantsList}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = `<p>${t("error-load-activities")}</p>`;
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?lang=${currentLang}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email: email })
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities list
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || t("error-generic");
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = t("error-signup");
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle delete button clicks using event delegation
  activitiesList.addEventListener('click', async (event) => {
    if (event.target.classList.contains('delete-btn')) {
      const email = event.target.dataset.email;
      const activity = event.target.dataset.activity;

      if (!confirm(t("confirm-unregister", { email, activity }))) {
        return;
      }

      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activity)}/unregister?lang=${currentLang}`,
          {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
          }
        );

        const result = await response.json();

        if (response.ok) {
          messageDiv.textContent = result.message;
          messageDiv.className = 'success';
          messageDiv.classList.remove('hidden');

          // Refresh activities list
          await fetchActivities();

          // Hide message after 5 seconds
          setTimeout(() => {
            messageDiv.classList.add('hidden');
          }, 5000);
        } else {
          messageDiv.textContent = result.detail || t("error-unregister-participant");
          messageDiv.className = 'error';
          messageDiv.classList.remove('hidden');
        }
      } catch (error) {
        messageDiv.textContent = t("error-unregister");
        messageDiv.className = 'error';
        messageDiv.classList.remove('hidden');
        console.error('Error unregistering:', error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
