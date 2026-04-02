# Requirements Document

## Introduction

This feature adds detail editing capabilities to task cards on the Kanban board. Users can click on any task card to open a modal panel where they can add or edit a short description and a list of people involved (assignees). The new fields are persisted alongside existing task data in Firebase/localStorage and synced through the FastAPI backend. The UI follows the existing red theme of the SvelteKit frontend.

## Glossary

- **Task**: An item on the Kanban board with an id, text, column, and userId. Extended by this feature to include description and assignees.
- **Task_Card**: The visual representation of a Task rendered inside a Kanban column.
- **Task_Detail_Modal**: The overlay panel that opens when a user clicks a Task_Card, allowing editing of task details.
- **Description**: A short free-text field (up to 500 characters) summarising the task.
- **Assignee**: A person associated with a task, identified by a display name or email address.
- **Assignee_List**: The ordered collection of Assignees attached to a single Task.
- **Board**: The full Kanban board page rendered by the SvelteKit frontend.
- **API**: The Python FastAPI backend that persists tasks.
- **Storage**: Firebase Firestore when connected, or localStorage when offline.

---

## Requirements

### Requirement 1: Open Task Detail Modal

**User Story:** As a board user, I want to click on a task card to open a detail panel, so that I can view and edit the task's description and assignees without leaving the board.

#### Acceptance Criteria

1. WHEN a user clicks on a Task_Card, THE Board SHALL open the Task_Detail_Modal for that task.
2. WHEN the Task_Detail_Modal is open, THE Task_Detail_Modal SHALL display the task's current text, description, and Assignee_List.
3. WHEN the Task_Detail_Modal is open, THE Board SHALL prevent the click from triggering a drag-and-drop action.
4. WHEN a user presses the Escape key while the Task_Detail_Modal is open, THE Task_Detail_Modal SHALL close without saving unsaved changes.
5. WHEN a user clicks outside the Task_Detail_Modal while it is open, THE Task_Detail_Modal SHALL close without saving unsaved changes.

---

### Requirement 2: Edit Task Description

**User Story:** As a board user, I want to add or edit a short description for a task, so that I can provide context about what the task involves.

#### Acceptance Criteria

1. WHEN the Task_Detail_Modal is open, THE Task_Detail_Modal SHALL display a text area pre-filled with the task's existing description, or empty if none exists.
2. THE Task_Detail_Modal SHALL accept a description of up to 500 characters.
3. IF a user enters more than 500 characters in the description field, THEN THE Task_Detail_Modal SHALL prevent input beyond 500 characters and display the remaining character count.
4. WHEN a user clicks the Save button, THE Task_Detail_Modal SHALL persist the description to Storage.
5. WHEN a description has been saved, THE Task_Card SHALL display a visual indicator (e.g., a description icon) to signal that a description exists.

---

### Requirement 3: Manage Assignees

**User Story:** As a board user, I want to add and remove people involved in a task, so that the team knows who is responsible for or contributing to each task.

#### Acceptance Criteria

1. WHEN the Task_Detail_Modal is open, THE Task_Detail_Modal SHALL display the current Assignee_List for the task.
2. WHEN a user types a name or email address into the assignee input field and presses Enter or clicks the Add button, THE Task_Detail_Modal SHALL add the entry to the Assignee_List.
3. IF a user submits an assignee entry that is already present in the Assignee_List, THEN THE Task_Detail_Modal SHALL reject the duplicate and display an inline error message.
4. IF a user submits an empty assignee input field, THEN THE Task_Detail_Modal SHALL ignore the submission without displaying an error.
5. WHEN a user clicks the remove button next to an Assignee, THE Task_Detail_Modal SHALL remove that Assignee from the Assignee_List immediately.
6. WHEN a user clicks the Save button, THE Task_Detail_Modal SHALL persist the updated Assignee_List to Storage.
7. WHEN at least one Assignee exists on a task, THE Task_Card SHALL display the assignee count or avatar initials as a visual indicator.

---

### Requirement 4: Persist Task Details to Backend

**User Story:** As a board user, I want task details to be saved to the backend, so that description and assignees are available across sessions and devices.

#### Acceptance Criteria

1. WHEN a user saves task details and the API is connected, THE API SHALL update the task record with the new description and Assignee_List.
2. WHEN a user saves task details and the API is not connected, THE Board SHALL persist the details to localStorage and display an offline indicator.
3. WHEN the API reconnects after an offline session, THE Board SHALL sync locally stored task details to the API.
4. THE API SHALL accept description as an optional string field and assignees as an optional list of strings on the task update endpoint.
5. WHEN the API returns an error during save, THE Task_Detail_Modal SHALL display an error message and retain the unsaved changes so the user can retry.

---

### Requirement 5: Display Task Detail Indicators on Task Cards

**User Story:** As a board user, I want to see at a glance which tasks have descriptions or assignees, so that I can quickly identify tasks that need attention or have context.

#### Acceptance Criteria

1. WHEN a Task has a non-empty description, THE Task_Card SHALL display a description icon below the task text.
2. WHEN a Task has one or more Assignees, THE Task_Card SHALL display the count of Assignees or up to three initials badges below the task text.
3. WHEN a Task has neither a description nor any Assignees, THE Task_Card SHALL not display any detail indicators.
4. THE Task_Card detail indicators SHALL use colours consistent with the existing red theme of the Board.
