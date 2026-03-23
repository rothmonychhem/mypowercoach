const views = document.querySelectorAll(".view");
const viewButtons = document.querySelectorAll("[data-view-target]");
const authModeButtons = document.querySelectorAll(".auth-mode-button");
const authForm = document.getElementById("auth-form");
const authTitle = document.getElementById("auth-title");
const authCopy = document.getElementById("auth-copy");
const authSubmit = document.getElementById("auth-submit");
const workspaceAthleteName = document.getElementById("workspace-athlete-name");
const workspaceAthleteCopy = document.getElementById("workspace-athlete-copy");
const profileStatus = document.getElementById("profile-status");
const navButtons = document.querySelectorAll(".nav-link");
const workspacePanels = document.querySelectorAll(".workspace-panel");
const profileForm = document.getElementById("profile-form");
const dailyCheckinForm = document.getElementById("daily-checkin-form");
const dailyStatus = document.getElementById("daily-status");
const chatForm = document.getElementById("chat-form");
const chatThread = document.getElementById("chat-thread");
const chatInput = document.getElementById("chat-input");
const signOutButton = document.querySelector("[data-signout]");
const workoutFeedbackPanel = document.getElementById("lifts-panel");
const exerciseSelectorList = document.getElementById("exercise-selector-list");
const selectedExerciseTitle = document.getElementById("selected-exercise-title");
const selectedExercisePlan = document.getElementById("selected-exercise-plan");
const selectedExerciseProgress = document.getElementById("selected-exercise-progress");
const selectedSetList = document.getElementById("selected-set-list");
const exerciseSliderPrev = document.getElementById("exercise-slider-prev");
const exerciseSliderNext = document.getElementById("exercise-slider-next");
const blockWeekGrid = document.getElementById("block-week-grid");
const prevWeekButton = document.getElementById("prev-week-button");
const nextWeekButton = document.getElementById("next-week-button");
const currentWeekBadge = document.getElementById("current-week-badge");
const selectedWeekLabel = document.getElementById("selected-week-label");
const selectedWeekTitle = document.getElementById("selected-week-title");
const selectedWeekDescription = document.getElementById("selected-week-description");
const programSheetHead = document.getElementById("program-sheet-head");
const programSheetBody = document.getElementById("program-sheet-body");
const newBlockStatus = document.getElementById("new-block-status");
const newBlockGate = document.getElementById("new-block-gate");
const newBlockForm = document.getElementById("new-block-form");
const createBlockButton = document.getElementById("create-block-button");

let authMode = "create";
let selectedExerciseIndex = 0;
let currentProgramWeek = 2;
let athleteProfile = {
    name: "Maya Torres",
    heightCm: "168",
    age: "28",
    sex: "Female",
    bodyweightKg: "84",
    trainingAgeYears: "3",
    trainingDaysPerWeek: "4",
    equipment: "Raw",
    primaryGoal: "Build a stronger competition total with better squat carryover",
    squatKg: "182.5",
    benchKg: "110",
    deadliftKg: "215",
    constraints: "Deadlift fatigue can stack fast, weekdays are time-limited",
    notes: "Bench responds well to higher frequency. Squat needs more force out of the bottom."
};
let workoutPlan = [
    {
        name: "Competition bench",
        summary: "Primary bench exposure for the day.",
        sets: [
            { plannedReps: 5, plannedWeight: 82.5, plannedRpe: 7.5, completedReps: 5, completedWeight: 82.5, completedRpe: 7.5, done: false, videoName: "" },
            { plannedReps: 5, plannedWeight: 82.5, plannedRpe: 7.5, completedReps: 5, completedWeight: 82.5, completedRpe: 7.5, done: false, videoName: "" },
            { plannedReps: 5, plannedWeight: 82.5, plannedRpe: 8, completedReps: 5, completedWeight: 82.5, completedRpe: 8, done: false, videoName: "" },
            { plannedReps: 5, plannedWeight: 82.5, plannedRpe: 8, completedReps: 5, completedWeight: 82.5, completedRpe: 8, done: false, videoName: "" },
            { plannedReps: 5, plannedWeight: 82.5, plannedRpe: 8.5, completedReps: 5, completedWeight: 82.5, completedRpe: 8.5, done: false, videoName: "" }
        ]
    },
    {
        name: "Close-grip bench",
        summary: "Accessory press to build triceps and bench carryover.",
        sets: [
            { plannedReps: 6, plannedWeight: 72.5, plannedRpe: 7.5, completedReps: 6, completedWeight: 72.5, completedRpe: 7.5, done: false, videoName: "" },
            { plannedReps: 6, plannedWeight: 72.5, plannedRpe: 8, completedReps: 6, completedWeight: 72.5, completedRpe: 8, done: false, videoName: "" },
            { plannedReps: 6, plannedWeight: 72.5, plannedRpe: 8, completedReps: 6, completedWeight: 72.5, completedRpe: 8, done: false, videoName: "" }
        ]
    },
    {
        name: "Chest-supported row",
        summary: "Upper-back support without extra low-back fatigue.",
        sets: [
            { plannedReps: 10, plannedWeight: 55, plannedRpe: 7, completedReps: 10, completedWeight: 55, completedRpe: 7, done: false, videoName: "" },
            { plannedReps: 10, plannedWeight: 55, plannedRpe: 7.5, completedReps: 10, completedWeight: 55, completedRpe: 7.5, done: false, videoName: "" },
            { plannedReps: 10, plannedWeight: 55, plannedRpe: 8, completedReps: 10, completedWeight: 55, completedRpe: 8, done: false, videoName: "" },
            { plannedReps: 10, plannedWeight: 55, plannedRpe: 8, completedReps: 10, completedWeight: 55, completedRpe: 8, done: false, videoName: "" }
        ]
    }
];
const blockWeeks = [
    {
        label: "Week 1",
        title: "Volume base",
        description: "Establish technical volume, rebuild work capacity, and accumulate useful squat and bench practice.",
        days: [
            {
                label: "Day 1",
                title: "Squat focus",
                description: "Volume base for squat pattern and quad drive.",
                exercises: [
                    { name: "Competition squat", prescription: "1 top set + 4 x 5 @ 72%" },
                    { name: "Paused squat", prescription: "3 x 4 @ 66%" },
                    { name: "Romanian deadlift", prescription: "3 x 8 moderate" },
                    { name: "Leg press", prescription: "3 x 12 hard but smooth" }
                ]
            },
            {
                label: "Day 2",
                title: "Bench volume",
                description: "Stable pressing positions and base volume.",
                exercises: [
                    { name: "Competition bench", prescription: "5 x 5 @ 75%" },
                    { name: "Close-grip bench", prescription: "3 x 6 @ 70%" },
                    { name: "Chest-supported row", prescription: "4 x 10" },
                    { name: "Cable fly", prescription: "3 x 15" }
                ]
            },
            {
                label: "Day 3",
                title: "Deadlift exposure",
                description: "Pulling practice without burying recovery.",
                exercises: [
                    { name: "Competition deadlift", prescription: "1 top set + 3 x 4 @ 70%" },
                    { name: "Front squat", prescription: "3 x 5 moderate" },
                    { name: "Lat pulldown", prescription: "3 x 12" },
                    { name: "Back extension", prescription: "3 x 15" }
                ]
            },
            {
                label: "Day 4",
                title: "Bench technique",
                description: "Extra bench frequency and upper-back support.",
                exercises: [
                    { name: "Tempo bench", prescription: "4 x 4 @ 68%" },
                    { name: "Pin press", prescription: "3 x 5" },
                    { name: "Seated cable row", prescription: "4 x 12" },
                    { name: "Lateral raise", prescription: "3 x 18" }
                ]
            }
        ]
    },
    {
        label: "Week 2",
        title: "Load progression",
        description: "Push load gradually while keeping extra bench exposure and targeted quad work in place.",
        days: [
            {
                label: "Day 1",
                title: "Squat intensity build",
                description: "Slightly heavier top exposure with paused support sets.",
                exercises: [
                    { name: "Competition squat", prescription: "1 top single + 4 x 4 @ 76%" },
                    { name: "Paused squat", prescription: "3 x 3 @ 70%" },
                    { name: "Romanian deadlift", prescription: "3 x 7" },
                    { name: "Hack squat", prescription: "3 x 10" }
                ]
            },
            {
                label: "Day 2",
                title: "Bench progression",
                description: "Load builds while volume stays useful.",
                exercises: [
                    { name: "Competition bench", prescription: "5 x 4 @ 78%" },
                    { name: "Close-grip bench", prescription: "3 x 5 @ 72%" },
                    { name: "Chest-supported row", prescription: "4 x 8 heavier" },
                    { name: "Dip variation", prescription: "3 x 10" }
                ]
            },
            {
                label: "Day 3",
                title: "Deadlift single",
                description: "More specific pulling without unnecessary spillover fatigue.",
                exercises: [
                    { name: "Competition deadlift", prescription: "1 top single + 3 x 3 @ 74%" },
                    { name: "Front squat", prescription: "3 x 4" },
                    { name: "Single-leg leg press", prescription: "3 x 10 each" },
                    { name: "Weighted plank", prescription: "3 x 40 sec" }
                ]
            },
            {
                label: "Day 4",
                title: "Bench technique",
                description: "Keep skill high and elbows healthy while pressing volume rises.",
                exercises: [
                    { name: "Tempo bench", prescription: "4 x 4 @ 70%" },
                    { name: "Spoto press", prescription: "3 x 5" },
                    { name: "Seated cable row", prescription: "4 x 10" },
                    { name: "Triceps pressdown", prescription: "3 x 15" }
                ]
            }
        ]
    },
    {
        label: "Week 3",
        title: "Highest stress week",
        description: "Top-set expression appears, fatigue is watched closely, and the athlete gets more meaningful benchmark sessions.",
        days: [
            {
                label: "Day 1",
                title: "High-stress squat",
                description: "Highest-stress squat day with clear positional carryover work.",
                exercises: [
                    { name: "Competition squat", prescription: "1 top single + 4 x 3 @ 80%" },
                    { name: "Paused squat", prescription: "3 x 3 @ 72%" },
                    { name: "Romanian deadlift", prescription: "3 x 6" },
                    { name: "Leg extension", prescription: "3 x 15" }
                ]
            },
            {
                label: "Day 2",
                title: "Bench benchmark",
                description: "Main bench benchmark day for the block.",
                exercises: [
                    { name: "Competition bench", prescription: "5 x 3 @ 82.5%" },
                    { name: "Close-grip bench", prescription: "3 x 5 @ 74%" },
                    { name: "Chest-supported row", prescription: "4 x 8" },
                    { name: "Cable fly", prescription: "3 x 12" }
                ]
            },
            {
                label: "Day 3",
                title: "Controlled deadlift stress",
                description: "Heavy enough to keep skill, light enough to stop fatigue drift.",
                exercises: [
                    { name: "Competition deadlift", prescription: "1 top single + 3 x 3 @ 77%" },
                    { name: "Front squat", prescription: "3 x 4" },
                    { name: "Lat pulldown", prescription: "4 x 10" },
                    { name: "Weighted plank", prescription: "3 x 45 sec" }
                ]
            },
            {
                label: "Day 4",
                title: "Extra bench exposure",
                description: "An added exposure slot to keep bench progress moving.",
                exercises: [
                    { name: "Tempo bench", prescription: "4 x 3 @ 72%" },
                    { name: "Pin press", prescription: "3 x 4" },
                    { name: "Seated cable row", prescription: "4 x 10" },
                    { name: "Rear delt fly", prescription: "3 x 18" }
                ]
            }
        ]
    },
    {
        label: "Week 4",
        title: "Pivot and recover",
        description: "Drop the least useful fatigue, protect movement quality, and set up the next block to start strong.",
        days: [
            {
                label: "Day 1",
                title: "Squat pivot",
                description: "Reduce fatigue while keeping squat pattern quality high.",
                exercises: [
                    { name: "Competition squat", prescription: "3 x 4 @ 67%" },
                    { name: "Paused squat", prescription: "2 x 3 @ 60%" },
                    { name: "Leg press", prescription: "2 x 10" }
                ]
            },
            {
                label: "Day 2",
                title: "Bench maintenance",
                description: "Enough work to keep momentum without overstaying fatigue.",
                exercises: [
                    { name: "Competition bench", prescription: "4 x 4 @ 70%" },
                    { name: "Close-grip bench", prescription: "2 x 5 @ 65%" },
                    { name: "Chest-supported row", prescription: "3 x 10" }
                ]
            },
            {
                label: "Day 3",
                title: "Deadlift recovery",
                description: "Fast pulls and low-cost accessories only.",
                exercises: [
                    { name: "Competition deadlift", prescription: "4 x 2 @ 65%" },
                    { name: "Front squat", prescription: "2 x 4 light" },
                    { name: "Back extension", prescription: "2 x 15" }
                ]
            },
            {
                label: "Day 4",
                title: "Upper back and tempo bench",
                description: "Low-fatigue work that sets up the next block cleanly.",
                exercises: [
                    { name: "Tempo bench", prescription: "3 x 4 @ 65%" },
                    { name: "Seated cable row", prescription: "3 x 12" },
                    { name: "Lateral raise", prescription: "3 x 15" }
                ]
            }
        ]
    }
];

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
    if (name) {
        athleteProfile.name = name;
    }
    renderProfile();
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

function getWorkoutEntries() {
    return workoutPlan.map((exercise) => ({
        name: exercise.name,
        plannedSets: exercise.sets.length,
        plannedReps: exercise.sets[0]?.plannedReps ?? 0,
        plannedWeight: exercise.sets[0]?.plannedWeight ?? 0,
        plannedRpe: exercise.sets[0]?.plannedRpe ?? 0,
        completedSets: exercise.sets.filter((set) => set.done).length,
        completedReps: exercise.sets.reduce((sum, set) => sum + set.completedReps, 0),
        completedWeight:
            exercise.sets.reduce((sum, set) => sum + set.completedWeight, 0) / Math.max(exercise.sets.length, 1),
        completedRpe: exercise.sets.reduce((sum, set) => sum + set.completedRpe, 0) / Math.max(exercise.sets.length, 1),
        sets: exercise.sets.map((set, index) => ({
            setNumber: index + 1,
            plannedReps: set.plannedReps,
            plannedWeight: set.plannedWeight,
            plannedRpe: set.plannedRpe,
            completedReps: set.completedReps,
            completedWeight: set.completedWeight,
            completedRpe: set.completedRpe,
            done: set.done,
            videoName: set.videoName
        }))
    }));
}

function buildExerciseSummary(exercises) {
    return exercises
        .map((exercise) => {
            const changedSets = exercise.sets.filter(
                (set) =>
                    set.completedWeight !== set.plannedWeight ||
                    set.completedReps !== set.plannedReps ||
                    set.completedRpe !== set.plannedRpe
            ).length;
            const feedback =
                changedSets === 0
                    ? "all sets matched the plan."
                    : `${changedSets} set${changedSets > 1 ? "s" : ""} changed from the plan.`;

            return `<li><strong>${exercise.name}</strong> ${feedback}</li>`;
        })
        .join("");
}

function updateWorkoutFeedbackPanel(summary, cues, improvements, videoText) {
    workoutFeedbackPanel.innerHTML = `
        <div class="panel-header">
            <div>
                <p class="eyebrow">Workout Feedback</p>
                <h3>Overview feedback on your workout</h3>
            </div>
            <span class="panel-badge">Session review</span>
        </div>

        <div class="lifts-grid">
            <article class="panel-card">
                <p class="card-label">What can be better</p>
                <h4>${summary}</h4>
                <p>${videoText}</p>
            </article>

            <article class="panel-card">
                <p class="card-label">Cues for next time</p>
                <ul class="clean-list">${cues.map((cue) => `<li>${cue}</li>`).join("")}</ul>
            </article>

            <article class="panel-card accent-card">
                <p class="card-label">What to improve next</p>
                <ul class="clean-list">${improvements.map((item) => `<li>${item}</li>`).join("")}</ul>
            </article>
        </div>
    `;
}

function renderProgramWeek() {
    const selectedWeek = blockWeeks[currentProgramWeek];
    currentWeekBadge.textContent = `${selectedWeek.label} of 4`;
    selectedWeekLabel.textContent = selectedWeek.label;
    selectedWeekTitle.textContent = selectedWeek.title;
    selectedWeekDescription.textContent = selectedWeek.description;

    blockWeekGrid.innerHTML = blockWeeks
        .map(
            (week, index) => `
                <button class="exercise-selector-button ${index === currentProgramWeek ? "is-selected" : ""}" type="button" data-week-index="${index}">
                    <strong>${week.label}</strong>
                    <span>${week.title}</span>
                    <div class="exercise-meta">
                        <span>${week.days.length} planned days</span>
                        <span>${index === currentProgramWeek ? "Selected" : "Open"}</span>
                    </div>
                </button>
            `
        )
        .join("");

    const maxSlots = Math.max(...selectedWeek.days.map((day) => day.exercises.length));

    programSheetHead.innerHTML = `
        <tr>
            <th class="program-sheet-slot">Slot</th>
            ${selectedWeek.days
                .map(
                    (day) => `
                        <th>
                            <div class="program-sheet-day">
                                <strong>${day.label}</strong>
                                <span>${day.title}</span>
                            </div>
                        </th>
                    `
                )
                .join("")}
        </tr>
    `;

    programSheetBody.innerHTML = Array.from({ length: maxSlots }, (_, slotIndex) => {
        const rowNumber = slotIndex + 1;
        const cells = selectedWeek.days
            .map((day) => {
                const exercise = day.exercises[slotIndex];

                if (!exercise) {
                    return `<td><div class="program-sheet-cell program-sheet-empty">Open slot</div></td>`;
                }

                return `
                    <td>
                        <div class="program-sheet-cell">
                            <div class="program-sheet-exercise">
                                <strong>${exercise.name}</strong>
                                <span>${exercise.prescription}</span>
                            </div>
                        </div>
                    </td>
                `;
            })
            .join("");

        return `
            <tr>
                <th class="program-sheet-slot">Exercise ${rowNumber}</th>
                ${cells}
            </tr>
        `;
    }).join("");

    prevWeekButton.disabled = currentProgramWeek === 0;
    nextWeekButton.disabled = currentProgramWeek === blockWeeks.length - 1;

    const unlocked = currentProgramWeek === blockWeeks.length - 1;
    newBlockStatus.textContent = unlocked ? "Ready to create" : "Available after week 4";
    newBlockGate.textContent = unlocked
        ? "Week 4 is selected. The next block can now pull forward the previous block's results and ask a few handoff questions before generating the next one."
        : "Complete week 4 first. Then this section should unlock, pull in data from the previous block, ask a few basic questions, and build the next block.";
    newBlockForm.classList.toggle("is-disabled", !unlocked);
    createBlockButton.disabled = !unlocked;
}

function renderWorkoutPlanner() {
    const exercise = workoutPlan[selectedExerciseIndex];
    const doneCount = exercise.sets.filter((set) => set.done).length;

    exerciseSelectorList.innerHTML = `
        <button class="exercise-selector-button is-selected" type="button">
            <strong>${exercise.name}</strong>
            <div class="exercise-meta">
                <span>${exercise.sets.length} sets planned</span>
                <span>${doneCount}/${exercise.sets.length} done</span>
            </div>
        </button>
    `;

    exerciseSliderPrev.disabled = selectedExerciseIndex === 0;
    exerciseSliderNext.disabled = selectedExerciseIndex === workoutPlan.length - 1;

    renderSelectedExercise();
}

function renderSelectedExercise() {
    const exercise = workoutPlan[selectedExerciseIndex];
    if (!exercise) {
        return;
    }

    const doneCount = exercise.sets.filter((set) => set.done).length;
    selectedExerciseTitle.textContent = exercise.name;
    selectedExercisePlan.textContent = `${exercise.summary} ${exercise.sets.length} planned sets.`;
    selectedExerciseProgress.textContent = `${doneCount} of ${exercise.sets.length} sets done`;

    selectedSetList.innerHTML = exercise.sets
        .map(
            (set, index) => `
                <div class="set-log-row ${set.done ? "is-done" : ""}" data-set-index="${index}">
                    <label class="set-check">
                        <input type="checkbox" data-field="done" ${set.done ? "checked" : ""} aria-label="${exercise.name} set ${index + 1} done">
                    </label>
                    <span class="set-label">Set ${index + 1}</span>
                    <span class="planned-chip">Planned ${set.plannedReps} @ ${set.plannedWeight} kg, RPE ${set.plannedRpe}</span>
                    <input type="number" min="0" max="30" value="${set.completedReps}" data-field="reps" aria-label="${exercise.name} set ${index + 1} reps">
                    <input type="number" min="0" max="400" step="0.5" value="${set.completedWeight}" data-field="weight" aria-label="${exercise.name} set ${index + 1} weight">
                    <input type="number" min="5" max="10" step="0.5" value="${set.completedRpe}" data-field="rpe" aria-label="${exercise.name} set ${index + 1} rpe">
                    <div>
                        <input class="set-video-input" type="file" accept="video/*" data-field="video" aria-label="${exercise.name} set ${index + 1} video">
                        <div class="planned-chip">${set.videoName || "No set video yet"}</div>
                    </div>
                </div>
            `
        )
        .join("");
}

function renderProfile() {
    workspaceAthleteName.textContent = athleteProfile.name;
    workspaceAthleteCopy.textContent = `${athleteProfile.bodyweightKg} kg, ${athleteProfile.sex.toLowerCase()}, ${athleteProfile.trainingDaysPerWeek} training days, PRs ${athleteProfile.squatKg}/${athleteProfile.benchKg}/${athleteProfile.deadliftKg} kg.`;

    document.getElementById("profile-name").value = athleteProfile.name;
    document.getElementById("profile-height").value = athleteProfile.heightCm;
    document.getElementById("profile-age").value = athleteProfile.age;
    document.getElementById("profile-sex").value = athleteProfile.sex;
    document.getElementById("profile-bodyweight").value = athleteProfile.bodyweightKg;
    document.getElementById("profile-training-age").value = athleteProfile.trainingAgeYears;
    document.getElementById("profile-training-days").value = athleteProfile.trainingDaysPerWeek;
    document.getElementById("profile-equipment").value = athleteProfile.equipment;
    document.getElementById("profile-goal").value = athleteProfile.primaryGoal;
    document.getElementById("profile-squat").value = athleteProfile.squatKg;
    document.getElementById("profile-bench").value = athleteProfile.benchKg;
    document.getElementById("profile-deadlift").value = athleteProfile.deadliftKg;
    document.getElementById("profile-constraints").value = athleteProfile.constraints;
    document.getElementById("profile-notes").value = athleteProfile.notes;
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
    setActivePanel(authMode === "create" ? "profile-panel" : "today-panel");
});

navButtons.forEach((button) => {
    button.addEventListener("click", () => {
        setActivePanel(button.dataset.panel);
    });
});

blockWeekGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-week-index]");
    if (!button) {
        return;
    }

    currentProgramWeek = Number(button.dataset.weekIndex);
    renderProgramWeek();
});

prevWeekButton.addEventListener("click", () => {
    if (currentProgramWeek > 0) {
        currentProgramWeek -= 1;
        renderProgramWeek();
    }
});

nextWeekButton.addEventListener("click", () => {
    if (currentProgramWeek < blockWeeks.length - 1) {
        currentProgramWeek += 1;
        renderProgramWeek();
    }
});

createBlockButton.addEventListener("click", () => {
    if (createBlockButton.disabled) {
        return;
    }

    newBlockStatus.textContent = "Next block drafted";
    newBlockGate.textContent = "The next block would now use the previous block data plus your recovery and priority answers to build a new cycle.";
});

exerciseSliderPrev.addEventListener("click", () => {
    if (selectedExerciseIndex > 0) {
        selectedExerciseIndex -= 1;
        renderWorkoutPlanner();
    }
});

exerciseSliderNext.addEventListener("click", () => {
    if (selectedExerciseIndex < workoutPlan.length - 1) {
        selectedExerciseIndex += 1;
        renderWorkoutPlanner();
    }
});

selectedSetList.addEventListener("change", (event) => {
    const row = event.target.closest("[data-set-index]");
    if (!row) {
        return;
    }

    const setIndex = Number(row.dataset.setIndex);
    const exercise = workoutPlan[selectedExerciseIndex];
    const target = event.target;

    if (target.dataset.field === "done") {
        exercise.sets[setIndex].done = target.checked;
    }

    if (target.dataset.field === "reps") {
        exercise.sets[setIndex].completedReps = Number(target.value);
    }

    if (target.dataset.field === "weight") {
        exercise.sets[setIndex].completedWeight = Number(target.value);
    }

    if (target.dataset.field === "rpe") {
        exercise.sets[setIndex].completedRpe = Number(target.value);
    }

    if (target.dataset.field === "video") {
        exercise.sets[setIndex].videoName = target.files.length > 0 ? target.files[0].name : "";
    }

    renderWorkoutPlanner();
});

profileForm.addEventListener("submit", (event) => {
    event.preventDefault();

    athleteProfile = {
        name: document.getElementById("profile-name").value.trim(),
        heightCm: document.getElementById("profile-height").value.trim(),
        age: document.getElementById("profile-age").value.trim(),
        sex: document.getElementById("profile-sex").value,
        bodyweightKg: document.getElementById("profile-bodyweight").value.trim(),
        trainingAgeYears: document.getElementById("profile-training-age").value.trim(),
        trainingDaysPerWeek: document.getElementById("profile-training-days").value.trim(),
        equipment: document.getElementById("profile-equipment").value,
        primaryGoal: document.getElementById("profile-goal").value.trim(),
        squatKg: document.getElementById("profile-squat").value.trim(),
        benchKg: document.getElementById("profile-bench").value.trim(),
        deadliftKg: document.getElementById("profile-deadlift").value.trim(),
        constraints: document.getElementById("profile-constraints").value.trim(),
        notes: document.getElementById("profile-notes").value.trim()
    };

    renderProfile();
    profileStatus.textContent = "Profile saved locally";
});

dailyCheckinForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const sessionQuality = document.getElementById("session-quality").value;
    const fatigueLevel = document.getElementById("fatigue-level").value;
    const notes = document.getElementById("daily-notes").value.trim();
    const exercises = getWorkoutEntries();
    const setVideos = exercises.flatMap((exercise) =>
        exercise.sets.filter((set) => set.videoName).map((set) => `${exercise.name} set ${set.setNumber}: ${set.videoName}`)
    );

    let summary = "";
    let status = "";
    let cues = [];
    let improvements = [];

    if (sessionQuality === "great" && fatigueLevel !== "high") {
        status = "Progression supported";
        summary = "Today's session was productive. The main lifts looked ready to keep moving, and the workout review supports continued progression.";
        cues = [
            "Keep competition bench positions consistent as load rises.",
            "Let accessories support the goal instead of turning into random fatigue."
        ];
        improvements = [
            "Keep logging exact reps, sets, and load so next-week adjustments stay precise.",
            "Use the video review to confirm that faster work is still technically clean."
        ];
    } else if (fatigueLevel === "high" || sessionQuality === "rough") {
        status = "Watch fatigue closely";
        summary = "Today's workout suggests recovery is getting tighter. The next useful move is protecting the following sessions instead of forcing more stress into the block.";
        cues = [
            "Stay patient in the setup instead of rushing reps when tired.",
            "Protect bar path and position before chasing heavier load."
        ];
        improvements = [
            "Cut the least useful fatigue first, especially if accessories are drifting sloppy.",
            "Use video to see whether the miss was technical or simply fatigue-related."
        ];
    } else {
        status = "Readiness stable";
        summary = "Today's workout was solid overall. The block can likely stay on course while the coach watches for repeated fatigue or underperformance patterns.";
        cues = [
            "Keep execution repeatable across all work sets.",
            "Use the planned workout as the baseline before making emotional load jumps."
        ];
        improvements = [
            "Look for small technique wins, not a full rewrite of the workout.",
            "Track where reps slow down so the next cue is more specific."
        ];
    }

    if (notes) {
        summary += ` Your note was: "${notes}"`;
    }

    const videoText = setVideos.length > 0
        ? `Set videos attached: ${setVideos.join(" | ")}. Use them to compare different sets, not just the whole exercise.`
        : "No set videos attached today. Add one on any set when you want feedback on the exact rep quality or load change.";

    dailyStatus.textContent = status;
    updateWorkoutFeedbackPanel(summary, cues, improvements, videoText);
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
renderProfile();
renderWorkoutPlanner();
renderProgramWeek();
setActivePanel("profile-panel");
