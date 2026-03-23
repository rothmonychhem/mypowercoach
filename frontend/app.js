const views = document.querySelectorAll(".view");
const viewButtons = document.querySelectorAll("[data-view-target]");
const authModeButtons = document.querySelectorAll(".auth-mode-button");
const authForm = document.getElementById("auth-form");
const demoEntryButton = document.getElementById("demo-entry");
const authTitle = document.getElementById("auth-title");
const authCopy = document.getElementById("auth-copy");
const authSubmit = document.getElementById("auth-submit");
const workspaceAthleteName = document.getElementById("workspace-athlete-name");
const workspaceAthleteCopy = document.getElementById("workspace-athlete-copy");
const navButtons = document.querySelectorAll(".nav-link");
const workspacePanels = document.querySelectorAll(".workspace-panel");
const dailyCheckinForm = document.getElementById("daily-checkin-form");
const dailyStatus = document.getElementById("daily-status");
const dailyResponse = document.getElementById("daily-response");
const chatForm = document.getElementById("chat-form");
const chatThread = document.getElementById("chat-thread");
const chatInput = document.getElementById("chat-input");
const signOutButton = document.querySelector("[data-signout]");

let authMode = "create";

function showView(viewId) {
    views.forEach((view) => {
        view.classList.toggle("is-hidden", view.id !== viewId);
        view.classList.toggle("is-active", view.id === viewId);
    });
}

function setAuthMode(mode) {
    authMode = mode;

    authModeButtons.forEach((button) => {
        button.classList.toggle("is-selected", button.dataset.authMode === mode);
    });

    const isCreate = mode === "create";
    authTitle.textContent = isCreate ? "Create your coaching account" : "Sign in to your coaching account";
    authCopy.textContent = isCreate
        ? "Start with a profile that captures your goals, recovery context, and lifting background so the program is built around the athlete, not around a template."
        : "Jump back into your workspace to review your program, log feedback on your day, and ask the coach how training is going.";
    authSubmit.textContent = isCreate ? "Create account" : "Sign in";
}

function openWorkspace(name) {
    workspaceAthleteName.textContent = name || "Maya Torres";
    workspaceAthleteCopy.textContent = "84 kg class, intermediate, 4 training days, personalized programming with daily feedback and lift guidance.";
    showView("app-view");
}

function setActivePanel(panelId) {
    navButtons.forEach((button) => {
        button.classList.toggle("is-active", button.dataset.panel === panelId);
    });

    workspacePanels.forEach((panel) => {
        panel.classList.toggle("is-hidden", panel.id !== panelId);
        panel.classList.toggle("is-active", panel.id === panelId);
    });
}

function getCoachReply(message) {
    const text = message.toLowerCase();

    if (text.includes("bench")) {
        return "Your bench is responding well right now. Volume is paying off, recovery looks good, and the next useful move is more exposure before a bigger jump in intensity.";
    }

    if (text.includes("squat")) {
        return "Your squat feedback points more toward force production out of the bottom than a major technical breakdown. That is why the plan keeps paused squat work in the rotation.";
    }

    if (text.includes("deadlift") || text.includes("pull")) {
        return "Deadlift is the lift most likely to drag down readiness at the moment. The coaching logic would keep a meaningful heavy exposure while trimming the fatigue that is not paying rent.";
    }

    if (text.includes("tired") || text.includes("fatigue") || text.includes("recovery")) {
        return "If fatigue is stacking faster than performance is improving, the app should protect momentum by reducing the stress that is least useful first, not by panicking and changing everything.";
    }

    return "Training is going best when the app can connect three things clearly: how the day felt, what your program is doing, and why the next adjustment makes sense for you.";
}

function appendChatMessage(role, text) {
    const bubble = document.createElement("article");
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;
    chatThread.appendChild(bubble);
    chatThread.scrollTop = chatThread.scrollHeight;
}

viewButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const target = button.dataset.viewTarget;
        const mode = button.dataset.authMode;

        if (mode) {
            setAuthMode(mode);
        }

        if (target) {
            showView(target);
        }
    });
});

authModeButtons.forEach((button) => {
    button.addEventListener("click", () => {
        setAuthMode(button.dataset.authMode);
    });
});

authForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const enteredEmail = document.getElementById("email").value.trim();
    const derivedName = enteredEmail ? enteredEmail.split("@")[0].replace(/[._-]+/g, " ") : "athlete";
    const displayName = derivedName
        .split(" ")
        .filter(Boolean)
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");

    openWorkspace(displayName || "Athlete");
    setActivePanel("today-panel");
});

demoEntryButton.addEventListener("click", () => {
    openWorkspace("Demo Athlete");
    setActivePanel("today-panel");
});

navButtons.forEach((button) => {
    button.addEventListener("click", () => {
        setActivePanel(button.dataset.panel);
    });
});

dailyCheckinForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const sessionQuality = document.getElementById("session-quality").value;
    const fatigueLevel = document.getElementById("fatigue-level").value;
    const notes = document.getElementById("daily-notes").value.trim();

    let summary = "";
    let status = "";

    if (sessionQuality === "great" && fatigueLevel !== "high") {
        status = "Progression supported";
        summary = "Today looked productive. The session quality was high and fatigue stayed manageable, so the coaching system would usually keep progression moving forward.";
    } else if (fatigueLevel === "high" || sessionQuality === "rough") {
        status = "Watch fatigue closely";
        summary = "Today suggests the plan may be spending a little too much recovery. The coaching response would likely protect the next few sessions instead of forcing more stress.";
    } else {
        status = "Readiness stable";
        summary = "Today was solid overall. The plan can probably stay on course, with only small adjustments if this pattern repeats across the week.";
    }

    if (notes) {
        summary += ` Your note was: "${notes}"`;
    }

    dailyStatus.textContent = status;
    dailyResponse.innerHTML = `
        <p class="card-label">Coach response</p>
        <p>${summary}</p>
    `;
});

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const message = chatInput.value.trim();
    if (!message) {
        return;
    }

    appendChatMessage("user", message);
    appendChatMessage("coach", getCoachReply(message));
    chatInput.value = "";
});

signOutButton.addEventListener("click", () => {
    showView("landing-view");
});

setAuthMode("create");
setActivePanel("today-panel");
