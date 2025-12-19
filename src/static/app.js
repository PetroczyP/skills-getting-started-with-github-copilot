document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create title
        const title = document.createElement("h4");
        title.textContent = name;
        activityCard.appendChild(title);

        // Create description
        const description = document.createElement("p");
        description.textContent = details.description;
        activityCard.appendChild(description);

        // Create schedule
        const schedule = document.createElement("p");
        const scheduleLabel = document.createElement("strong");
        scheduleLabel.textContent = "Schedule:";
        schedule.appendChild(scheduleLabel);
        schedule.appendChild(document.createTextNode(` ${details.schedule}`));
        activityCard.appendChild(schedule);

        // Create availability
        const availability = document.createElement("p");
        const availabilityLabel = document.createElement("strong");
        availabilityLabel.textContent = "Availability:";
        availability.appendChild(availabilityLabel);
        availability.appendChild(document.createTextNode(` ${spotsLeft} spots left`));
        activityCard.appendChild(availability);

        // Create participants section
        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        const participantsHeader = document.createElement("p");
        participantsHeader.className = "participants-header";
        const participantsHeaderLabel = document.createElement("strong");
        participantsHeaderLabel.textContent = "Current Participants:";
        participantsHeader.appendChild(participantsHeaderLabel);
        participantsSection.appendChild(participantsHeader);

        // Create participants list or no participants message
        if (details.participants.length > 0) {
          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";
          participantsList.dataset.activity = name;

          details.participants.forEach(email => {
            const listItem = document.createElement("li");
            
            const emailSpan = document.createElement("span");
            emailSpan.textContent = email;
            listItem.appendChild(emailSpan);

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.textContent = "Delete";
            deleteBtn.dataset.email = email;
            deleteBtn.dataset.activity = name;
            listItem.appendChild(deleteBtn);

            participantsList.appendChild(listItem);
          });

          participantsSection.appendChild(participantsList);
        } else {
          const noParticipants = document.createElement("p");
          noParticipants.className = "no-participants";
          noParticipants.textContent = "No participants yet. Be the first to sign up!";
          participantsSection.appendChild(noParticipants);
        }

        activityCard.appendChild(participantsSection);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.textContent = "";
      const errorMessage = document.createElement("p");
      errorMessage.textContent = "Failed to load activities. Please try again later.";
      activitiesList.appendChild(errorMessage);
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
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
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

      if (!confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) {
        return;
      }

      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
          {
            method: 'DELETE',
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
          messageDiv.textContent = result.detail || 'Failed to unregister participant';
          messageDiv.className = 'error';
          messageDiv.classList.remove('hidden');
        }
      } catch (error) {
        messageDiv.textContent = 'Failed to unregister. Please try again.';
        messageDiv.className = 'error';
        messageDiv.classList.remove('hidden');
        console.error('Error unregistering:', error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
