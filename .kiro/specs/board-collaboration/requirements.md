# Requirements Document

## Introduction

This feature adds real-time board collaboration to the Kanban application. A board owner can invite other registered users (identified by email) to collaborate on their board. Collaborators can view, add, move, and edit tasks on the owner's board. Each user retains their own personal board. When a collaborator logs in, they can switch between their own board and any boards they have been invited to. The board header clearly identifies whose board is currently being viewed.

## Glossary

- **Board**: The Kanban board belonging to a specific user, identified by that user's `userId`. Tasks are stored under the owner's `userId`.
- **Board_Owner**: The authenticated user who created and owns a Board.
- **Collaborator**: An authenticated user who has been granted access to a Board_Owner's Board.
- **Collaboration_Invite**: A record that associates a Collaborator's email with a Board_Owner's `userId`, granting access.
- **Collaborator_Panel**: The modal/panel UI opened by the "Collaborate" button, used to manage Collaborators.
- **Board_Switcher**: The UI control that allows a Collaborator to switch between their own Board and Boards they have been invited to.
- **Active_Board**: The Board currently being viewed and interacted with by the logged-in user.
- **User_Registry**: The Firestore collection (`users`) that stores a record for every user who has signed in with Google at least once, keyed by `uid` and indexed by `email`.
- **API**: The Python FastAPI backend that persists tasks and collaboration data.
- **Storage**: Firebase Firestore when connected, or localStorage when offline.
- **System**: The Kanban board application as a whole (frontend + backend).

---

## Requirements

### Requirement 1: Collaborate Button and Panel

**User Story:** As a board owner, I want a "Collaborate" button in the board header, so that I can open a panel to manage who has access to my board.

#### Acceptance Criteria

1. THE Board SHALL display a "Collaborate" button in the top-right area of the board header, positioned below the Firebase connection status indicator.
2. WHEN a Board_Owner clicks the "Collaborate" button, THE System SHALL open the Collaborator_Panel.
3. WHEN the Collaborator_Panel is open, THE System SHALL display the current list of Collaborators for the Active_Board.
4. WHEN a user clicks outside the Collaborator_Panel or presses the Escape key, THE Collaborator_Panel SHALL close.
5. WHILE a user is viewing a Board they do not own (i.e., they are a Collaborator), THE Board SHALL hide the "Collaborate" button.

---

### Requirement 2: Invite Collaborator by Email

**User Story:** As a board owner, I want to invite a collaborator by entering their email address, so that I can grant them access to my board.

#### Acceptance Criteria

1. WHEN the Collaborator_Panel is open, THE Collaborator_Panel SHALL display an email input field and an "Add" button for inviting new Collaborators.
2. WHEN a Board_Owner submits a valid email address, THE System SHALL check whether a user with that email exists in the User_Registry.
3. IF the submitted email does not correspond to any user in the User_Registry, THEN THE Collaborator_Panel SHALL display an error message stating the user was not found.
4. IF the submitted email corresponds to the Board_Owner's own account, THEN THE Collaborator_Panel SHALL display an error message stating the owner cannot invite themselves.
5. IF the submitted email is already in the Collaborator list for the Active_Board, THEN THE Collaborator_Panel SHALL display an error message stating the user is already a collaborator.
6. WHEN a valid, non-duplicate, non-self email is submitted, THE System SHALL create a Collaboration_Invite record in Storage linking the Collaborator's `uid` and email to the Board_Owner's `userId`.
7. WHEN a Collaboration_Invite is successfully created, THE Collaborator_Panel SHALL add the new Collaborator to the displayed list immediately.
8. IF the email input field is empty when the "Add" button is clicked, THEN THE Collaborator_Panel SHALL ignore the submission without displaying an error.

---

### Requirement 3: User Registry

**User Story:** As the system, I need to know which users have registered, so that board owners can only invite existing users.

#### Acceptance Criteria

1. WHEN a user signs in with Google for the first time, THE System SHALL write a record to the User_Registry containing the user's `uid`, `email`, and `displayName`.
2. WHEN a user signs in with Google on a subsequent visit, THE System SHALL update the User_Registry record for that user with the latest `displayName`.
3. THE User_Registry SHALL be queryable by email address to support the invite lookup in Requirement 2.
4. THE System SHALL store User_Registry records in the Firestore `users` collection.

---

### Requirement 4: Remove Collaborator

**User Story:** As a board owner, I want to remove a collaborator at any time, so that I can revoke access to my board.

#### Acceptance Criteria

1. WHEN the Collaborator_Panel is open, THE Collaborator_Panel SHALL display a "Remove" button next to each Collaborator in the list.
2. WHEN a Board_Owner clicks the "Remove" button for a Collaborator, THE System SHALL delete the corresponding Collaboration_Invite record from Storage.
3. WHEN a Collaboration_Invite is deleted, THE Collaborator_Panel SHALL remove the Collaborator from the displayed list immediately.
4. WHEN a Collaboration_Invite is deleted, THE former Collaborator SHALL no longer be able to view or interact with the Board_Owner's Board.

---

### Requirement 5: Collaborator Board Access

**User Story:** As a collaborator, I want to view and interact with the boards I've been invited to, so that I can contribute to those projects.

#### Acceptance Criteria

1. WHEN a Collaborator logs in, THE System SHALL load the list of Boards the Collaborator has been invited to.
2. WHEN a Collaborator has one or more active invitations, THE Board SHALL display a Board_Switcher control listing the Collaborator's own board and each Board they have been invited to.
3. WHEN a Collaborator selects a Board from the Board_Switcher, THE System SHALL load and display the tasks belonging to that Board's owner.
4. WHILE a Collaborator is viewing an owner's Board, THE Collaborator SHALL be able to add tasks, move tasks between columns, and edit task details on that Board.
5. WHILE a Collaborator is viewing an owner's Board, THE System SHALL store any new or modified tasks under the Board_Owner's `userId`, not the Collaborator's `userId`.
6. WHILE a Collaborator is viewing an owner's Board, THE Collaborator SHALL NOT be able to delete tasks from that Board.

---

### Requirement 6: Board Identity Label

**User Story:** As a user, I want the board header to clearly show whose board I am viewing, so that I always know which board is active.

#### Acceptance Criteria

1. WHILE a user is viewing their own Board, THE Board SHALL display the label "My Board" in the board header.
2. WHILE a Collaborator is viewing another user's Board, THE Board SHALL display the label "[Owner's first name]'s Board" in the board header (e.g., "John's Board").
3. THE board identity label SHALL be visually prominent and consistent with the existing red theme of the Board.

---

### Requirement 7: Backend Collaboration Endpoints

**User Story:** As the system, I need API endpoints to manage collaboration invites, so that the frontend can create, list, and delete them reliably.

#### Acceptance Criteria

1. THE API SHALL expose a `POST /collaborations` endpoint that accepts a `ownerUserId` and a `collaboratorEmail`, validates the collaborator exists in the User_Registry, and creates a Collaboration_Invite record.
2. THE API SHALL expose a `GET /collaborations` endpoint that accepts an `ownerUserId` query parameter and returns the list of Collaborators for that board.
3. THE API SHALL expose a `DELETE /collaborations/{invite_id}` endpoint that removes a Collaboration_Invite record.
4. THE API SHALL expose a `GET /collaborations/invited` endpoint that accepts a `collaboratorUid` query parameter and returns the list of Boards the user has been invited to.
5. WHEN a `POST /collaborations` request is made with an email that does not exist in the User_Registry, THE API SHALL return a 404 response with a descriptive error message.
6. WHEN a `POST /collaborations` request is made with an email that is already a collaborator on the specified board, THE API SHALL return a 409 response.
7. THE API SHALL store Collaboration_Invite records in the Firestore `collaborations` collection with fields: `ownerUserId`, `collaboratorUid`, `collaboratorEmail`, and `createdAt`.

---

### Requirement 8: Firestore Security Rules

**User Story:** As the system, I need Firestore security rules to protect collaboration data, so that users can only access data they are authorised to see.

#### Acceptance Criteria

1. THE System SHALL allow a Board_Owner to read and write Collaboration_Invite records where the `ownerUserId` matches the authenticated user's `uid`.
2. THE System SHALL allow a Collaborator to read Collaboration_Invite records where the `collaboratorUid` matches the authenticated user's `uid`.
3. THE System SHALL allow any authenticated user to read User_Registry records (to support email lookup).
4. THE System SHALL allow an authenticated user to write only their own User_Registry record (where the document id matches their `uid`).
5. THE System SHALL allow a Collaborator to read and write tasks in the `kanban-tasks` collection where the task's `userId` matches a Board they have been invited to.
