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
const dailyWorkoutContext = document.getElementById("daily-workout-context");
const publishedWorkoutTitle = document.getElementById("published-workout-title");
const publishedWorkoutCopy = document.getElementById("published-workout-copy");
const weekProgressTitle = document.getElementById("week-progress-title");
const weekProgressCopy = document.getElementById("week-progress-copy");
const blockProgressTitle = document.getElementById("block-progress-title");
const blockProgressCopy = document.getElementById("block-progress-copy");
const dailyWorkflowMessage = document.getElementById("daily-workflow-message");
const mainLiftCuesTitle = document.getElementById("main-lift-cues-title");
const mainLiftCuesWhy = document.getElementById("main-lift-cues-why");
const mainLiftCuesList = document.getElementById("main-lift-cues-list");
const chatForm = document.getElementById("chat-form");
const chatThread = document.getElementById("chat-thread");
const chatInput = document.getElementById("chat-input");
const chatSuggestions = document.getElementById("chat-suggestions");
const signOutButton = document.querySelector("[data-signout]");
const weightUnitToggle = document.getElementById("weight-unit-toggle");
const weightUnitButtons = document.querySelectorAll("[data-weight-unit]");
const bodyweightUnitLabel = document.getElementById("bodyweight-unit-label");
const strengthUnitLabels = document.querySelectorAll(".strength-unit-label");
const setWeightUnitLabel = document.getElementById("set-weight-unit-label");
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
const programCurrentMarker = document.getElementById("program-current-marker");
const programCurrentCopy = document.getElementById("program-current-copy");
const programWeeklyRecapTitle = document.getElementById("program-weekly-recap-title");
const programWeeklyRecapCopy = document.getElementById("program-weekly-recap-copy");
const programBlockRecapTitle = document.getElementById("program-block-recap-title");
const programBlockRecapCopy = document.getElementById("program-block-recap-copy");
const newBlockStatus = document.getElementById("new-block-status");
const newBlockGate = document.getElementById("new-block-gate");
const newBlockForm = document.getElementById("new-block-form");
const createBlockButton = document.getElementById("create-block-button");

const KG_TO_LB = 2.20462;
const appStorageKey = "mypowercoach-prototype-state";

let authMode = "create";
let selectedExerciseIndex = 0;
let currentProgramWeek = 0;
let weightUnit = "kg";
let workflowNotice = "Save a day when you are really finished with the published workout. The next session should only publish after that confirmation.";
let activePanelId = "profile-panel";

const defaultChatGreeting = "Ask about today's focus, your squat cues, your bench setup, deadlift execution, fatigue, or why the next workout changed.";

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

const workoutTemplateByDay = buildWorkoutTemplates(blockWeeks);
let trainingState = createTrainingState();
let workoutPlan = [];
let lastWorkoutReview = {
    summary: "Complete a workout day and the review will summarize how the session compared to the plan.",
    cues: [
        "Use the planned session as the baseline before changing load emotionally.",
        "Attach a set video when you want the review tied to one specific rep or position."
    ],
    improvements: [
        "Daily reviews should feed the weekly and block recap automatically.",
        "The next workout should publish only after the current day is saved."
    ],
    videoText: "No completed workout review yet."
};

function buildWorkoutTemplates(weeks) {
    const templates = {};

    weeks.forEach((week, weekIndex) => {
        week.days.forEach((day, dayIndex) => {
            templates[getDayKey(weekIndex, dayIndex)] = day.exercises.map((exercise) =>
                createExerciseTemplate(exercise.name, exercise.prescription, week.title, day.title)
            );
        });
    });

    return templates;
}

function createExerciseTemplate(name, prescription, weekTitle, dayTitle) {
    const parsed = parsePrescription(prescription);
    return {
        name,
        summary: `${dayTitle} in ${weekTitle}. ${prescription}`,
        prescription,
        sets: Array.from({ length: parsed.sets }, (_, index) => {
            const targetRpe = parsed.rpeStart + (index >= Math.max(parsed.sets - 2, 0) ? 0.5 : 0);
            return {
                plannedReps: parsed.reps,
                plannedWeight: parsed.weightKg,
                plannedRpe: targetRpe,
                completedReps: parsed.reps,
                completedWeight: parsed.weightKg,
                completedRpe: targetRpe,
                done: false,
                videoName: ""
            };
        })
    };
}

function parsePrescription(prescription) {
    const normalized = prescription.toLowerCase();
    const setMatch = normalized.match(/(\d+)\s*x\s*(\d+)/);
    const percentMatch = normalized.match(/(\d+(?:\.\d+)?)\s*%/);
    const sets = setMatch ? Number(setMatch[1]) : 3;
    const reps = setMatch ? Number(setMatch[2]) : 8;

    if (percentMatch) {
        const percent = Number(percentMatch[1]);
        return {
            sets,
            reps,
            weightKg: percent,
            rpeStart: percentToRpe(percent)
        };
    }

    if (normalized.includes("light")) {
        return { sets, reps, weightKg: 40, rpeStart: 6 };
    }
    if (normalized.includes("moderate")) {
        return { sets, reps, weightKg: 55, rpeStart: 7 };
    }
    if (normalized.includes("hard")) {
        return { sets, reps, weightKg: 60, rpeStart: 8 };
    }

    return { sets, reps, weightKg: 50, rpeStart: 7 };
}

function percentToRpe(percent) {
    if (percent >= 82.5) {
        return 8.5;
    }
    if (percent >= 75) {
        return 8;
    }
    if (percent >= 70) {
        return 7.5;
    }
    if (percent >= 65) {
        return 7;
    }
    return 6.5;
}

function createTrainingState() {
    return {
        currentWeekIndex: 0,
        currentDayIndex: 0,
        completedDays: {},
        workoutHistory: [],
        workflowNotice
    };
}

function getDayKey(weekIndex, dayIndex) {
    return `w${weekIndex}-d${dayIndex}`;
}

function getCurrentTrainingPointer() {
    return {
        weekIndex: trainingState.currentWeekIndex,
        dayIndex: trainingState.currentDayIndex,
        dayKey: getDayKey(trainingState.currentWeekIndex, trainingState.currentDayIndex)
    };
}

function cloneWorkoutTemplate(dayKey) {
    const template = workoutTemplateByDay[dayKey] ?? [];
    return JSON.parse(JSON.stringify(template));
}

function isBlockComplete() {
    const lastWeekIndex = blockWeeks.length - 1;
    const lastDayIndex = blockWeeks[lastWeekIndex].days.length - 1;
    return Boolean(trainingState.completedDays[getDayKey(lastWeekIndex, lastDayIndex)]);
}

function getCurrentDayDefinition() {
    const pointer = getCurrentTrainingPointer();
    const week = blockWeeks[pointer.weekIndex];
    const day = week.days[pointer.dayIndex];
    return {
        week,
        day,
        weekIndex: pointer.weekIndex,
        dayIndex: pointer.dayIndex,
        dayKey: pointer.dayKey
    };
}

function getDayStatus(weekIndex, dayIndex) {
    const dayKey = getDayKey(weekIndex, dayIndex);
    if (trainingState.completedDays[dayKey]) {
        return "done";
    }

    if (isBlockComplete()) {
        return "upcoming";
    }

    const pointer = getCurrentTrainingPointer();
    if (pointer.weekIndex === weekIndex && pointer.dayIndex === dayIndex) {
        return "current";
    }
    if (weekIndex < pointer.weekIndex || (weekIndex === pointer.weekIndex && dayIndex < pointer.dayIndex)) {
        return "passed";
    }
    return "upcoming";
}

function countCompletedDaysForWeek(weekIndex) {
    return blockWeeks[weekIndex].days.filter((_, dayIndex) => getDayStatus(weekIndex, dayIndex) === "done").length;
}

function countCompletedDaysForBlock() {
    return Object.keys(trainingState.completedDays).length;
}

function getTotalDaysInBlock() {
    return blockWeeks.reduce((sum, week) => sum + week.days.length, 0);
}

function getWeekHistory(weekIndex) {
    return trainingState.workoutHistory.filter((entry) => entry.weekIndex === weekIndex);
}

function getBlockHistory() {
    return trainingState.workoutHistory;
}

function averageFromHistory(entries, field) {
    if (!entries.length) {
        return 0;
    }
    return entries.reduce((sum, entry) => sum + (entry[field] ?? 0), 0) / entries.length;
}

function loadWorkoutPlanForCurrentDay() {
    const pointer = getCurrentTrainingPointer();
    const saved = trainingState.completedDays[pointer.dayKey];
    workoutPlan = saved?.exercises ? JSON.parse(JSON.stringify(saved.exercises)) : cloneWorkoutTemplate(pointer.dayKey);
    selectedExerciseIndex = Math.min(selectedExerciseIndex, Math.max(workoutPlan.length - 1, 0));
}

function qualityToScore(value) {
    if (value === "great") {
        return 3;
    }
    if (value === "solid") {
        return 2;
    }
    return 1;
}

function fatigueToScore(value) {
    if (value === "low") {
        return 1;
    }
    if (value === "moderate") {
        return 2;
    }
    return 3;
}

function buildDayCompletionSummary(exercises) {
    const totalSets = exercises.reduce((sum, exercise) => sum + exercise.sets.length, 0);
    const doneSets = exercises.reduce((sum, exercise) => sum + exercise.sets.filter((set) => set.done).length, 0);
    const attachedVideos = exercises.reduce((sum, exercise) => sum + exercise.sets.filter((set) => set.videoName).length, 0);
    return { totalSets, doneSets, attachedVideos };
}

function buildWorkoutConfirmationMessage(currentDay, completionSummary) {
    const incompleteSets = completionSummary.totalSets - completionSummary.doneSets;
    const completionLine = `${completionSummary.doneSets}/${completionSummary.totalSets} sets are marked done.`;
    const incompleteLine = incompleteSets > 0
        ? ` ${incompleteSets} set${incompleteSets === 1 ? "" : "s"} are still unchecked.`
        : "";

    return `Are you sure you're done with ${currentDay.week.label} ${currentDay.day.label}? ${completionLine}${incompleteLine} Saving this will publish the next workout.`;
}

function buildWorkflowNoticeAfterSave(savedDay, nextPointer, weekWasCompleted) {
    if (isBlockComplete()) {
        return `${savedDay.week.label} ${savedDay.day.label} is saved. Week 4 is complete and the full block is now complete.`;
    }

    const nextWeek = blockWeeks[nextPointer.weekIndex];
    const nextDay = nextWeek.days[nextPointer.dayIndex];
    if (weekWasCompleted) {
        return `${savedDay.week.label} is complete. ${nextWeek.label} ${nextDay.label} is now published in daily feedback.`;
    }

    return `${savedDay.week.label} ${savedDay.day.label} is saved. ${nextWeek.label} ${nextDay.label} is now published in daily feedback.`;
}

function getMainLiftCuePack(day, athlete) {
    const primaryExercise = day.exercises[0];
    const primaryName = primaryExercise?.name ?? "Main lift";
    const notes = `${athlete.notes ?? ""} ${athlete.constraints ?? ""}`.toLowerCase();

    if (primaryName.toLowerCase().includes("bench")) {
        const cues = [
            "Pull the shoulder blades down and back before the handoff so the chest stays high and the touch point stays repeatable.",
            "Press your feet into the floor before the bar leaves the chest so leg drive transfers into the bar instead of arriving late.",
            "Keep the forearms stacked under the bar so the press stays efficient through the sticking point."
        ];

        if (notes.includes("leg drive")) {
            cues[1] = "Start leg drive before the press, not after it, so the bar leaves the chest with the whole body working together.";
        }
        if (notes.includes("off the chest") || notes.includes("off chest")) {
            cues[2] = "Stay patient at the touch and keep the bar path tight so the first inches off the chest do not leak force.";
        }

        return {
            title: `${primaryName} cues`,
            why: "These cues matter because bench usually improves when setup, touch position, and pressure transfer are cleaner, not when you just force more effort into a messy rep.",
            cues
        };
    }

    if (primaryName.toLowerCase().includes("squat")) {
        const cues = [
            "Brace before the descent and keep pressure through the full foot so the bar stays over the mid-foot.",
            "Let the knees and hips break together so you do not dump forward out of the bottom.",
            "Drive the upper back into the bar as you come up so the torso rises with the hips."
        ];

        if (notes.includes("knee") || notes.includes("knee cave")) {
            cues[1] = "Keep the knees tracking over the foot on the way down and out of the hole so position does not collapse under load.";
        }
        if (notes.includes("hips shoot") || notes.includes("out of the hole")) {
            cues[2] = "Push evenly through the floor out of the hole so the chest and hips rise together instead of the hips shooting up first.";
        }

        return {
            title: `${primaryName} cues`,
            why: "These cues matter because squat execution is mostly about staying balanced and keeping the bar over a strong position through the hardest range.",
            cues
        };
    }

    if (primaryName.toLowerCase().includes("deadlift")) {
        const cues = [
            "Set the lats before the pull so the bar stays close instead of drifting away from you.",
            "Push the floor away at the start instead of yanking the bar with loose position.",
            "Stay over the bar long enough that the knees clear and the lockout finishes with the whole posterior chain."
        ];

        if (notes.includes("off the floor") || notes.includes("wedge")) {
            cues[1] = "Build the wedge first and then push the floor away so the bar breaks from the floor without losing position.";
        }
        if (notes.includes("lockout") || notes.includes("at the knee")) {
            cues[2] = "Keep the bar pinned to you past the knee so the finish is a strong lockout, not a chase forward.";
        }

        return {
            title: `${primaryName} cues`,
            why: "These cues matter because deadlift execution gets better when the bar stays close, the start is patient, and the hard range is attacked from a stable position.",
            cues
        };
    }

    return {
        title: `${primaryName} cues`,
        why: "These pointers should make the main work more repeatable and technically useful instead of just making the session feel harder.",
        cues: [
            "Use the first working sets to lock in the same setup every time.",
            "Keep the bar path and body position as repeatable as possible.",
            "Let execution quality decide whether load should move up today."
        ]
    };
}

function renderMainLiftCues() {
    const currentDay = getCurrentDayDefinition();
    const cuePack = getMainLiftCuePack(currentDay.day, athleteProfile);
    mainLiftCuesTitle.textContent = cuePack.title;
    mainLiftCuesWhy.textContent = cuePack.why;
    mainLiftCuesList.innerHTML = cuePack.cues.map((cue) => `<li>${cue}</li>`).join("");
}

function advanceTrainingPointer() {
    if (isBlockComplete()) {
        return;
    }

    const pointer = getCurrentTrainingPointer();
    const week = blockWeeks[pointer.weekIndex];

    if (pointer.dayIndex < week.days.length - 1) {
        trainingState.currentDayIndex += 1;
        return;
    }

    if (pointer.weekIndex < blockWeeks.length - 1) {
        trainingState.currentWeekIndex += 1;
        trainingState.currentDayIndex = 0;
    }
}

function savePrototypeState() {
    trainingState.workflowNotice = workflowNotice;
    const payload = {
        athleteProfile,
        trainingState,
        weightUnit,
        currentProgramWeek,
        lastWorkoutReview,
        workflowNotice
    };
    window.localStorage.setItem(appStorageKey, JSON.stringify(payload));
}

function loadPrototypeState() {
    const raw = window.localStorage.getItem(appStorageKey);
    if (!raw) {
        loadWorkoutPlanForCurrentDay();
        return;
    }

    try {
        const parsed = JSON.parse(raw);
        athleteProfile = parsed.athleteProfile ?? athleteProfile;
        trainingState = parsed.trainingState ?? trainingState;
        weightUnit = parsed.weightUnit ?? weightUnit;
        currentProgramWeek = parsed.currentProgramWeek ?? currentProgramWeek;
        lastWorkoutReview = parsed.lastWorkoutReview ?? lastWorkoutReview;
        workflowNotice = parsed.workflowNotice ?? parsed.trainingState?.workflowNotice ?? workflowNotice;
    } catch (error) {
        trainingState = createTrainingState();
    }

    currentProgramWeek = Math.min(currentProgramWeek, blockWeeks.length - 1);
    trainingState.workflowNotice = workflowNotice;
    loadWorkoutPlanForCurrentDay();
}

function convertWeightForDisplay(weightKg) {
    const numericWeight = Number(weightKg);
    if (Number.isNaN(numericWeight)) {
        return 0;
    }
    return weightUnit === "kg" ? numericWeight : numericWeight * KG_TO_LB;
}

function convertWeightFromDisplay(weightValue) {
    const numericWeight = Number(weightValue);
    if (Number.isNaN(numericWeight)) {
        return 0;
    }
    return weightUnit === "kg" ? numericWeight : numericWeight / KG_TO_LB;
}

function formatWeight(weightKg) {
    const convertedWeight = convertWeightForDisplay(weightKg);
    const rounded = convertedWeight >= 100 ? convertedWeight.toFixed(0) : convertedWeight.toFixed(1);
    return `${rounded} ${weightUnit}`;
}

function renderWeightUnit() {
    weightUnitButtons.forEach((button) => {
        button.classList.toggle("is-active", button.dataset.weightUnit === weightUnit);
    });
    bodyweightUnitLabel.textContent = weightUnit;
    strengthUnitLabels.forEach((label) => {
        label.textContent = weightUnit;
    });
    setWeightUnitLabel.textContent = weightUnit;
}

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
    renderWorkoutPlanner();
    renderProgramWeek();
    renderWorkoutFeedback();
    showView("app-view");
}

function setActivePanel(panelId) {
    if (activePanelId === "chat-panel" && panelId !== "chat-panel") {
        resetChatThread();
    }

    navButtons.forEach((button) => {
        button.classList.toggle("is-active", button.dataset.panel === panelId);
    });

    workspacePanels.forEach((panel) => {
        panel.classList.toggle("is-hidden", panel.id !== panelId);
        panel.classList.toggle("is-active", panel.id === panelId);
    });

    activePanelId = panelId;

    if (panelId === "chat-panel" && !chatThread.children.length) {
        resetChatThread();
    }
}

function appendChatMessage(role, text) {
    const bubble = document.createElement("article");
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;
    chatThread.appendChild(bubble);
    chatThread.scrollTop = chatThread.scrollHeight;
}

function resetChatThread() {
    chatThread.innerHTML = "";
    chatInput.value = "";
    appendChatMessage("coach", defaultChatGreeting);
    renderChatSuggestions();
}

function getLatestHistoryEntry() {
    return trainingState.workoutHistory.at(-1) ?? null;
}

function normalizeChatText(message) {
    return message.toLowerCase().replace(/\s+/g, " ").trim();
}

function chatMatches(text, keywords) {
    return keywords.some((keyword) => text.includes(keyword));
}

function inferPriorityLift() {
    const notes = `${athleteProfile.primaryGoal} ${athleteProfile.notes} ${athleteProfile.constraints}`.toLowerCase();
    const squat = Number(athleteProfile.squatKg);
    const bench = Number(athleteProfile.benchKg);
    const deadlift = Number(athleteProfile.deadliftKg);

    if (chatMatches(notes, ["bench", "leg drive", "off chest", "pause"])) {
        return "bench";
    }
    if (chatMatches(notes, ["squat", "out of the bottom", "out of the hole", "quad", "knee"])) {
        return "squat";
    }
    if (chatMatches(notes, ["deadlift", "back fatigue", "hinge", "off the floor"])) {
        return "deadlift";
    }
    if (squat > 0 && bench / squat < 0.58) {
        return "bench";
    }
    if (deadlift > 0 && squat / deadlift < 0.78) {
        return "squat";
    }
    return "deadlift";
}

function getPrimaryFocusCue() {
    const priority = inferPriorityLift();
    if (priority === "bench") {
        return "Bench is the live priority, so the best carryover usually comes from repeated quality exposures, stable setup, and force transfer that stays clean before load jumps.";
    }
    if (priority === "squat") {
        return "Squat is the live priority, so the useful question is whether the block is improving positions and force out of the bottom, not whether one top set felt hard.";
    }
    return "Deadlift is the live priority, so the coaching goal is to keep meaningful pulling exposures while managing the fatigue cost across the whole week.";
}

function inferChatLift(text) {
    if (chatMatches(text, ["bench", "press", "pause", "leg drive"])) {
        return "bench";
    }
    if (chatMatches(text, ["squat", "hole", "brace", "knee", "quad"])) {
        return "squat";
    }
    if (chatMatches(text, ["deadlift", "pull", "hinge", "lockout", "wedge"])) {
        return "deadlift";
    }
    return inferPriorityLift();
}

function buildLiftCueAnswer(liftName) {
    const cuePack = getMainLiftCuePack(
        {
            exercises: [{ name: liftName === "bench" ? "Competition bench press" : liftName === "squat" ? "Competition squat" : "Competition deadlift" }]
        },
        athleteProfile
    );
    const liftLabel = liftName.charAt(0).toUpperCase() + liftName.slice(1);
    return `${liftLabel} cues should stay specific to the lift you asked about. Focus on this today: ${cuePack.cues.join(" ")} Why it matters: ${cuePack.why}`;
}

function summarizeCurrentWorkout() {
    const currentDay = getCurrentDayDefinition();
    const topExercises = workoutPlan.slice(0, 3).map((exercise) => exercise.name).join(", ");
    return `${currentDay.week.label} ${currentDay.day.label} is ${currentDay.day.title.toLowerCase()}, and the main work today is ${topExercises}.`;
}

function summarizeWeekState() {
    const currentDay = getCurrentDayDefinition();
    const weekHistory = getWeekHistory(trainingState.currentWeekIndex);
    const weekDone = countCompletedDaysForWeek(trainingState.currentWeekIndex);
    const weekTotal = currentDay.week.days.length;

    if (!weekHistory.length) {
        return `${currentDay.week.label} is still empty, so the recap does not have enough data yet.`;
    }

    return `${currentDay.week.label} is ${weekDone}/${weekTotal} days complete with average session quality ${averageFromHistory(weekHistory, "sessionQualityScore").toFixed(1)}/3 and average fatigue ${averageFromHistory(weekHistory, "fatigueScore").toFixed(1)}/3.`;
}

function summarizeBlockState() {
    const blockDone = countCompletedDaysForBlock();
    const blockTotal = getTotalDaysInBlock();
    if (blockDone === 0) {
        return "The block has not started yet.";
    }
    return `The block is ${blockDone}/${blockTotal} days complete, so the next change should come from the trend of the block, not one emotional reaction.`;
}

function explainNextWorkout() {
    const currentDay = getCurrentDayDefinition();
    return `The next workout only changes when the current day is saved because the sheet, daily feedback, and recaps all share the same training state. That keeps ${currentDay.week.label} aligned with the actual block flow instead of letting the chat drift away from the program.`;
}

function buildSuggestedQuestions() {
    const currentDay = getCurrentDayDefinition();
    const priority = inferPriorityLift();
    const liftQuestion = priority === "bench"
        ? "How is my bench progressing?"
        : priority === "squat"
            ? "How is my squat progressing?"
            : "How is my deadlift progressing?";
    const cueQuestion = priority === "bench"
        ? "What are my bench cues today?"
        : priority === "squat"
            ? "What are my squat cues today?"
            : "What are my deadlift cues today?";

    return [
        `What should I focus on in ${currentDay.day.title.toLowerCase()}?`,
        cueQuestion,
        liftQuestion,
        "Why did the next workout change?"
    ];
}

function renderChatSuggestions(questions = buildSuggestedQuestions()) {
    chatSuggestions.innerHTML = questions
        .map(
            (question) => `
                <button class="chat-suggestion" type="button" data-chat-question="${question}">
                    ${question}
                </button>
            `
        )
        .join("");
}

function buildCoachReply(message) {
    const text = normalizeChatText(message);
    const currentDay = getCurrentDayDefinition();
    const latestHistory = getLatestHistoryEntry();
    let answer = "";

    if (chatMatches(text, ["cue", "cues", "pointer", "pointers", "technique"])) {
        answer = buildLiftCueAnswer(inferChatLift(text));
    } else if (chatMatches(text, ["block", "next workout", "next day", "change", "why"])) {
        answer = `${summarizeBlockState()} ${explainNextWorkout()}`;
    } else if (chatMatches(text, ["today", "focus", currentDay.day.title.toLowerCase(), "session"])) {
        answer = `${summarizeCurrentWorkout()} ${getPrimaryFocusCue()} The best coaching move today is to finish the planned work cleanly enough that the next published day still fits the block.`;
    } else if (chatMatches(text, ["bench", "leg drive", "off chest", "pause"])) {
        answer = `${getPrimaryFocusCue()} ${latestHistory ? `Your last saved day finished with ${latestHistory.completionPercent}% completion and session quality ${latestHistory.sessionQualityScore}/3, so bench decisions should come from repeated clean exposures, not one hard set.` : "Once a few days are logged, the weekly recap will tell us whether the bench work is actually carrying over."}`;
    } else if (chatMatches(text, ["squat", "hole", "quad", "brace", "knee"])) {
        answer = `Squat should be judged across the block, not in isolation. ${summarizeWeekState()} That recap should tell us whether the squat-focused work is improving bottom-end positions or only creating fatigue.`;
    } else if (chatMatches(text, ["deadlift", "pull", "hinge", "back fatigue"])) {
        answer = `Deadlift is usually the biggest weekly fatigue lever. ${summarizeWeekState()} If the recap starts showing high fatigue with dropping completion, the right move is to trim the least useful pulling stress first.`;
    } else if (chatMatches(text, ["week", "recap"])) {
        answer = `${summarizeWeekState()} The weekly recap should drive the next adjustment more than any one set.`;
    } else if (chatMatches(text, ["fatigue", "tired", "recovery", "beat up"])) {
        answer = latestHistory
            ? `Your latest logged day carried fatigue ${latestHistory.fatigueScore}/3. If that keeps stacking in the weekly recap, the smart move is to reduce the fatigue that is paying the least rent instead of rewriting the whole block. ${summarizeWeekState()}`
            : "Fatigue should be judged as a pattern across the week, not just a feeling from one workout. Once more days are logged, the chatbot can answer from the recap instead of guessing.";
    } else if (chatMatches(text, ["weak", "weakness", "sticking point", "limiter"])) {
        answer = `${getPrimaryFocusCue()} The block should attack the weak point with enough specific work to matter, but not so much that it destroys the rest of the week. That balance is what the recap is supposed to protect.`;
    } else {
        answer = `${summarizeCurrentWorkout()} ${summarizeWeekState()} ${getPrimaryFocusCue()} Ask about today's focus, your priority lift, fatigue, the weekly recap, or why the next workout changed and I can answer from the actual training state.`;
    }

    return {
        answer,
        suggestedQuestions: buildSuggestedQuestions()
    };
}

function submitChatMessage(message) {
    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
        return;
    }

    appendChatMessage("user", trimmedMessage);
    const reply = buildCoachReply(trimmedMessage);
    appendChatMessage("coach", reply.answer);
    renderChatSuggestions(reply.suggestedQuestions);
}

function getWorkoutEntries() {
    return workoutPlan.map((exercise) => ({
        exercise_name: exercise.name,
        sets: exercise.sets.map((set, index) => ({
            set_number: index + 1,
            planned_reps: set.plannedReps,
            planned_weight_kg: set.plannedWeight,
            completed_reps: set.completedReps,
            completed_weight_kg: set.completedWeight,
            completed_rpe: set.completedRpe,
            done: set.done,
            video_name: set.videoName
        }))
    }));
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

function renderWorkoutFeedback() {
    updateWorkoutFeedbackPanel(
        lastWorkoutReview.summary,
        lastWorkoutReview.cues,
        lastWorkoutReview.improvements,
        lastWorkoutReview.videoText
    );
}

function renderProgressSummaries() {
    const pointer = getCurrentTrainingPointer();
    const week = blockWeeks[pointer.weekIndex];
    const day = week.days[pointer.dayIndex];
    const weekDone = countCompletedDaysForWeek(pointer.weekIndex);
    const weekTotal = week.days.length;
    const blockDone = countCompletedDaysForBlock();
    const blockTotal = getTotalDaysInBlock();
    const weekHistory = getWeekHistory(pointer.weekIndex);
    const blockHistory = getBlockHistory();
    const lastLog = blockHistory.at(-1);

    if (isBlockComplete()) {
        dailyWorkoutContext.textContent = "The current block is complete. Review the recap and generate the next block.";
        publishedWorkoutTitle.textContent = "Block complete";
        publishedWorkoutCopy.textContent = "All planned days in the current block have been logged.";
    } else {
        dailyWorkoutContext.textContent = `${week.label}, ${day.label} is published for today.`;
        publishedWorkoutTitle.textContent = `${week.label} / ${day.label}`;
        publishedWorkoutCopy.textContent = `${day.title}: ${day.description}`;
    }

    weekProgressTitle.textContent = `${weekDone} of ${weekTotal} days done`;
    weekProgressCopy.textContent = weekHistory.length === 0
        ? "No days are complete yet in the current week."
        : `Average completion ${Math.round(averageFromHistory(weekHistory, "completionPercent"))}% and fatigue ${averageFromHistory(weekHistory, "fatigueScore").toFixed(1)}/3 so far.`;

    blockProgressTitle.textContent = `${blockDone} of ${blockTotal} days done`;
    blockProgressCopy.textContent = blockDone === 0
        ? "The block has not started yet."
        : `${Math.round((blockDone / blockTotal) * 100)}% of the block is complete. ${blockHistory.filter((entry) => entry.videosAttached > 0).length} logged day${blockHistory.filter((entry) => entry.videosAttached > 0).length === 1 ? "" : "s"} included video.`;

    programCurrentMarker.textContent = isBlockComplete() ? "Block complete" : `${week.label} / ${day.label}`;
    programCurrentCopy.textContent = isBlockComplete()
        ? "All planned training days are complete. Use the recap and handoff questions to build the next block."
        : `${day.title} is the published workout and should stay highlighted in the sheet until you save it.`;

    programWeeklyRecapTitle.textContent = weekHistory.length === weekTotal ? `${week.label} recap ready` : `${week.label} still in progress`;
    programWeeklyRecapCopy.textContent = weekHistory.length === 0
        ? "Daily reviews will roll up here once sessions are logged."
        : `Completed ${weekHistory.length}/${weekTotal} days. Average session quality ${averageFromHistory(weekHistory, "sessionQualityScore").toFixed(1)}/3.`;

    programBlockRecapTitle.textContent = blockDone === blockTotal ? "Block recap ready" : "Block still in progress";
    programBlockRecapCopy.textContent = blockHistory.length === 0
        ? "Block recap will summarize compliance, fatigue, and session quality as training logs come in."
        : `Logged ${blockHistory.length} day${blockHistory.length === 1 ? "" : "s"}. Last saved session: ${lastLog.weekLabel} ${lastLog.dayLabel}.`;

    dailyWorkflowMessage.textContent = workflowNotice;
}

function renderProgramWeek() {
    const selectedWeek = blockWeeks[currentProgramWeek];
    currentWeekBadge.textContent = `${selectedWeek.label} of 4`;
    selectedWeekLabel.textContent = selectedWeek.label;
    selectedWeekTitle.textContent = selectedWeek.title;
    selectedWeekDescription.textContent = selectedWeek.description;

    blockWeekGrid.innerHTML = blockWeeks
        .map((week, index) => {
            const doneCount = countCompletedDaysForWeek(index);
            const weekStatus = index < trainingState.currentWeekIndex ? "Done" : index === trainingState.currentWeekIndex ? "Current" : "Upcoming";
            return `
                <button class="exercise-selector-button ${index === currentProgramWeek ? "is-selected" : ""}" type="button" data-week-index="${index}">
                    <strong>${week.label}</strong>
                    <span>${week.title}</span>
                    <div class="exercise-meta">
                        <span>${doneCount}/${week.days.length} done</span>
                        <span>${index === currentProgramWeek ? "Selected" : weekStatus}</span>
                    </div>
                </button>
            `;
        })
        .join("");

    const maxSlots = Math.max(...selectedWeek.days.map((day) => day.exercises.length));

    programSheetHead.innerHTML = `
        <tr>
            <th class="program-sheet-slot">Slot</th>
            ${selectedWeek.days
                .map((day, dayIndex) => {
                    const status = getDayStatus(currentProgramWeek, dayIndex);
                    const statusLabel = status === "done" ? "Done" : status === "current" ? "Live" : status === "passed" ? "Passed" : "Upcoming";
                    return `
                        <th>
                            <div class="program-sheet-day ${status}">
                                <strong>${day.label}</strong>
                                <span>${day.title}</span>
                                <small class="program-day-status ${status}">${statusLabel}</small>
                            </div>
                        </th>
                    `;
                })
                .join("")}
        </tr>
    `;

    programSheetBody.innerHTML = Array.from({ length: maxSlots }, (_, slotIndex) => {
        const cells = selectedWeek.days
            .map((day, dayIndex) => {
                const exercise = day.exercises[slotIndex];
                const status = getDayStatus(currentProgramWeek, dayIndex);

                if (!exercise) {
                    return `<td><div class="program-sheet-cell program-sheet-empty">Open slot</div></td>`;
                }

                return `
                    <td class="program-day-cell ${status}">
                        <div class="program-sheet-cell ${status}">
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
                <th class="program-sheet-slot">Exercise ${slotIndex + 1}</th>
                ${cells}
            </tr>
        `;
    }).join("");

    prevWeekButton.disabled = currentProgramWeek === 0;
    nextWeekButton.disabled = currentProgramWeek === blockWeeks.length - 1;

    const lastWeekIndex = blockWeeks.length - 1;
    const unlocked = currentProgramWeek === lastWeekIndex && countCompletedDaysForWeek(lastWeekIndex) === blockWeeks[lastWeekIndex].days.length;
    newBlockStatus.textContent = unlocked ? "Ready to create" : "Available after week 4";
    newBlockGate.textContent = unlocked
        ? "Week 4 is complete. The next block can now use the previous block recap, ask a few handoff questions, and generate the next cycle."
        : "Complete all of week 4 first. Then this section should unlock, pull in the recap from the previous block, ask a few basic questions, and build the next one.";
    newBlockForm.classList.toggle("is-disabled", !unlocked);
    createBlockButton.disabled = !unlocked;

    renderProgressSummaries();
}

function renderWorkoutPlanner() {
    const currentDay = getCurrentDayDefinition();
    const exercise = workoutPlan[selectedExerciseIndex];

    if (!exercise) {
        exerciseSelectorList.innerHTML = `
            <button class="exercise-selector-button is-selected" type="button">
                <strong>Block complete</strong>
                <div class="exercise-meta">
                    <span>No active workout</span>
                    <span>Review recap</span>
                </div>
            </button>
        `;
        selectedExerciseTitle.textContent = "No workout published";
        selectedExercisePlan.textContent = "Finish the recap and create the next block to publish another day here.";
        selectedExerciseProgress.textContent = "0 active sets";
        selectedSetList.innerHTML = "";
        dailyStatus.textContent = "Block complete";
        return;
    }

    const exerciseDoneCount = workoutPlan.filter((plannedExercise) => plannedExercise.sets.every((set) => set.done)).length;
    const doneCount = exercise.sets.filter((set) => set.done).length;
    const allDone = workoutPlan.every((plannedExercise) => plannedExercise.sets.every((set) => set.done));
    dailyStatus.textContent = allDone ? "Ready to save day" : `Logging ${currentDay.day.label}`;

    exerciseSelectorList.innerHTML = `
        <button class="exercise-selector-button is-selected" type="button">
            <strong>${exercise.name}</strong>
            <div class="exercise-meta">
                <span>${currentDay.week.label} / ${currentDay.day.label}</span>
                <span>${exerciseDoneCount}/${workoutPlan.length} exercises fully done</span>
            </div>
        </button>
    `;

    exerciseSliderPrev.disabled = selectedExerciseIndex === 0;
    exerciseSliderNext.disabled = selectedExerciseIndex === workoutPlan.length - 1;

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
                    <span class="planned-chip">Planned ${set.plannedReps} @ ${formatWeight(set.plannedWeight)}, RPE ${set.plannedRpe}</span>
                    <input type="number" min="0" max="30" value="${set.completedReps}" data-field="reps" aria-label="${exercise.name} set ${index + 1} reps">
                    <input type="number" min="0" max="1000" step="0.5" value="${convertWeightForDisplay(set.completedWeight).toFixed(1)}" data-field="weight" aria-label="${exercise.name} set ${index + 1} weight">
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
    workspaceAthleteCopy.textContent = `${formatWeight(athleteProfile.bodyweightKg)}, ${athleteProfile.sex.toLowerCase()}, ${athleteProfile.trainingDaysPerWeek} training days, PRs ${formatWeight(athleteProfile.squatKg)} / ${formatWeight(athleteProfile.benchKg)} / ${formatWeight(athleteProfile.deadliftKg)}.`;

    document.getElementById("profile-name").value = athleteProfile.name;
    document.getElementById("profile-height").value = athleteProfile.heightCm;
    document.getElementById("profile-age").value = athleteProfile.age;
    document.getElementById("profile-sex").value = athleteProfile.sex;
    document.getElementById("profile-bodyweight").value = convertWeightForDisplay(athleteProfile.bodyweightKg).toFixed(1);
    document.getElementById("profile-training-age").value = athleteProfile.trainingAgeYears;
    document.getElementById("profile-training-days").value = athleteProfile.trainingDaysPerWeek;
    document.getElementById("profile-equipment").value = athleteProfile.equipment;
    document.getElementById("profile-goal").value = athleteProfile.primaryGoal;
    document.getElementById("profile-squat").value = convertWeightForDisplay(athleteProfile.squatKg).toFixed(1);
    document.getElementById("profile-bench").value = convertWeightForDisplay(athleteProfile.benchKg).toFixed(1);
    document.getElementById("profile-deadlift").value = convertWeightForDisplay(athleteProfile.deadliftKg).toFixed(1);
    document.getElementById("profile-constraints").value = athleteProfile.constraints;
    document.getElementById("profile-notes").value = athleteProfile.notes;
    renderWeightUnit();
}

function refreshWorkspaceState() {
    loadWorkoutPlanForCurrentDay();
    currentProgramWeek = trainingState.currentWeekIndex;
    renderProfile();
    renderMainLiftCues();
    renderWorkoutPlanner();
    renderProgramWeek();
    renderWorkoutFeedback();
    renderChatSuggestions();
    savePrototypeState();
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
    savePrototypeState();
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
    savePrototypeState();
});

prevWeekButton.addEventListener("click", () => {
    if (currentProgramWeek > 0) {
        currentProgramWeek -= 1;
        renderProgramWeek();
        savePrototypeState();
    }
});

nextWeekButton.addEventListener("click", () => {
    if (currentProgramWeek < blockWeeks.length - 1) {
        currentProgramWeek += 1;
        renderProgramWeek();
        savePrototypeState();
    }
});

createBlockButton.addEventListener("click", () => {
    if (createBlockButton.disabled) {
        return;
    }

    newBlockStatus.textContent = "Next block drafted";
    newBlockGate.textContent = "The next block would now use the previous block recap, your recovery answers, and your next priority to build a new cycle.";
});

weightUnitToggle.addEventListener("click", (event) => {
    const button = event.target.closest("[data-weight-unit]");
    if (!button) {
        return;
    }

    weightUnit = button.dataset.weightUnit;
    renderProfile();
    renderWorkoutPlanner();
    renderProgramWeek();
    savePrototypeState();
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
        exercise.sets[setIndex].completedWeight = convertWeightFromDisplay(target.value);
    }
    if (target.dataset.field === "rpe") {
        exercise.sets[setIndex].completedRpe = Number(target.value);
    }
    if (target.dataset.field === "video") {
        exercise.sets[setIndex].videoName = target.files.length > 0 ? target.files[0].name : "";
    }

    renderWorkoutPlanner();
    savePrototypeState();
});

profileForm.addEventListener("submit", (event) => {
    event.preventDefault();

    athleteProfile = {
        name: document.getElementById("profile-name").value.trim(),
        heightCm: document.getElementById("profile-height").value.trim(),
        age: document.getElementById("profile-age").value.trim(),
        sex: document.getElementById("profile-sex").value,
        bodyweightKg: convertWeightFromDisplay(document.getElementById("profile-bodyweight").value.trim()).toFixed(1),
        trainingAgeYears: document.getElementById("profile-training-age").value.trim(),
        trainingDaysPerWeek: document.getElementById("profile-training-days").value.trim(),
        equipment: document.getElementById("profile-equipment").value,
        primaryGoal: document.getElementById("profile-goal").value.trim(),
        squatKg: convertWeightFromDisplay(document.getElementById("profile-squat").value.trim()).toFixed(1),
        benchKg: convertWeightFromDisplay(document.getElementById("profile-bench").value.trim()).toFixed(1),
        deadliftKg: convertWeightFromDisplay(document.getElementById("profile-deadlift").value.trim()).toFixed(1),
        constraints: document.getElementById("profile-constraints").value.trim(),
        notes: document.getElementById("profile-notes").value.trim()
    };

    renderProfile();
    profileStatus.textContent = "Profile saved locally";
    savePrototypeState();
});

dailyCheckinForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!workoutPlan.length) {
        return;
    }

    const sessionQuality = document.getElementById("session-quality").value;
    const fatigueLevel = document.getElementById("fatigue-level").value;
    const notes = document.getElementById("daily-notes").value.trim();
    const exercises = getWorkoutEntries();
    const setVideos = exercises.flatMap((exercise) =>
        exercise.sets.filter((set) => set.video_name).map((set) => `${exercise.exercise_name} set ${set.set_number}: ${set.video_name}`)
    );
    const currentDay = getCurrentDayDefinition();
    const completionSummary = buildDayCompletionSummary(workoutPlan);
    const completionPercent = completionSummary.totalSets === 0 ? 0 : Math.round((completionSummary.doneSets / completionSummary.totalSets) * 100);
    const saveConfirmed = window.confirm(buildWorkoutConfirmationMessage(currentDay, completionSummary));

    if (!saveConfirmed) {
        workflowNotice = `${currentDay.week.label} ${currentDay.day.label} is still open. Save it only when you are sure today's workout is done.`;
        renderProgressSummaries();
        savePrototypeState();
        return;
    }

    let summary = "";
    let status = "";
    let cues = [];
    let improvements = [];

    if (sessionQuality === "great" && fatigueLevel !== "high") {
        status = "Progression supported";
        summary = "Today's session was productive. The plan and the logged work are still aligned well enough to keep progressing.";
        cues = [
            "Keep the same setup quality as load rises.",
            "Let the next session build from this one instead of making random jumps."
        ];
        improvements = [
            "Use the weekly recap to confirm that good days are repeating, not just appearing once.",
            "Keep attaching set videos when a rep slows down or feels different."
        ];
    } else if (fatigueLevel === "high" || sessionQuality === "rough") {
        status = "Watch fatigue closely";
        summary = "Today's workout suggests recovery is tighter. The next useful move is to protect the rest of the week, not force more stress into it.";
        cues = [
            "Keep positions patient when fatigue starts pulling the rep apart.",
            "Prioritize repeatable execution before chasing extra load."
        ];
        improvements = [
            "Let the weekly recap decide whether fatigue is a pattern or just one hard day.",
            "Use block recap trends before making a full rewrite of the next cycle."
        ];
    } else {
        status = "Readiness stable";
        summary = "Today's workout was solid overall. The current block can stay on course while the recap watches for repeated changes in execution or fatigue.";
        cues = [
            "Keep day-to-day execution repeatable.",
            "Use the planned workout as the baseline before adjusting."
        ];
        improvements = [
            "Look for small technique wins that carry into the weekly recap.",
            "Track where reps slow down so the next cue can be more specific."
        ];
    }

    if (notes) {
        summary += ` Your note was: "${notes}"`;
    }

    const videoText = setVideos.length > 0
        ? `Set videos attached: ${setVideos.join(" | ")}. Those should feed into daily, weekly, and block recap notes without cluttering the main table.`
        : "No set videos attached today. Add one when you want a specific set reviewed more closely.";

    trainingState.completedDays[currentDay.dayKey] = {
        weekIndex: currentDay.weekIndex,
        dayIndex: currentDay.dayIndex,
        weekLabel: currentDay.week.label,
        dayLabel: currentDay.day.label,
        dayTitle: currentDay.day.title,
        completionPercent,
        sessionQuality,
        fatigueLevel,
        notes,
        videosAttached: completionSummary.attachedVideos,
        exercises: JSON.parse(JSON.stringify(workoutPlan))
    };

    trainingState.workoutHistory = trainingState.workoutHistory.filter((entry) => entry.dayKey !== currentDay.dayKey);
    trainingState.workoutHistory.push({
        dayKey: currentDay.dayKey,
        weekIndex: currentDay.weekIndex,
        dayIndex: currentDay.dayIndex,
        weekLabel: currentDay.week.label,
        dayLabel: currentDay.day.label,
        completionPercent,
        sessionQualityScore: qualityToScore(sessionQuality),
        fatigueScore: fatigueToScore(fatigueLevel),
        videosAttached: completionSummary.attachedVideos
    });

    const weekWasCompleted = countCompletedDaysForWeek(currentDay.weekIndex) === blockWeeks[currentDay.weekIndex].days.length;

    lastWorkoutReview = { summary, cues, improvements, videoText };
    dailyStatus.textContent = status;
    updateWorkoutFeedbackPanel(summary, cues, improvements, videoText);

    advanceTrainingPointer();
    workflowNotice = buildWorkflowNoticeAfterSave(currentDay, getCurrentTrainingPointer(), weekWasCompleted);
    trainingState.workflowNotice = workflowNotice;
    document.getElementById("daily-notes").value = "";
    refreshWorkspaceState();
});

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitChatMessage(chatInput.value);
    chatInput.value = "";
});

chatSuggestions.addEventListener("click", (event) => {
    const button = event.target.closest("[data-chat-question]");
    if (!button) {
        return;
    }

    const question = button.dataset.chatQuestion ?? "";
    chatInput.value = question;
    submitChatMessage(question);
    chatInput.value = "";
});

signOutButton.addEventListener("click", () => {
    showView("landing-view");
});

loadPrototypeState();
setAuthMode("create");
renderProfile();
renderMainLiftCues();
renderWorkoutPlanner();
renderProgramWeek();
renderWorkoutFeedback();
renderChatSuggestions();
setActivePanel("profile-panel");
