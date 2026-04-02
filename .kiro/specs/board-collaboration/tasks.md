# Implementation Plan: Board Collaboration

## Overview

Implement real-time board collaboration across four layers: Firestore data model + security rules, FastAPI backend endpoints, frontend lib updates, and new/updated Svelte UI components.

## Tasks

- [x] 1. Add collaboration types and API methods to `src/lib/api.ts`
  - Add `Collaborator`, `InvitedBoard`, and `CollaborationCreate` TypeScript interfaces
  - Add `getCollaborators(ownerUserId)`, `addCollaborator(payload)`, `removeCollaborator(inviteId)`, and `getInvitedBoards(collaboratorUid)` methods to `ApiService`
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 2. Update `src/lib/auth.ts` to write to the User Registry on sign-in
  - Import Firestore client and write/upsert a `UserRecord` (`uid`, `email`, `displayName`, `updatedAt`) to the `users` collection on every successful Google sign-in
  - Use `setDoc` with `merge: true` so subsequent sign-ins update `displayName` without overwriting other fields
  - _Requirements: 3.1, 3.2, 3.4_

  - [ ]* 2.1 Write property test for user registry upsert idempotency
    - **Property 6: User registry upsert is idempotent**
    - **Validates: Requirements 3.1, 3.2**

- [x] 3. Add collaboration endpoints to `backend/main.py`
  - [x] 3.1 Add `CollaborationCreate` and `CollaborationRecord` Pydantic models
    - _Requirements: 7.7_

  - [x] 3.2 Implement `POST /collaborations`
    - Look up `collaboratorEmail` in the `users` Firestore collection
    - Return 404 if not found, 409 if already a collaborator
    - Write to `collaborations` collection with `ownerUserId`, `collaboratorUid`, `collaboratorEmail`, `createdAt`
    - _Requirements: 7.1, 7.5, 7.6, 7.7_

  - [ ]* 3.3 Write property test for `POST /collaborations` — unknown email returns 404
    - **Property 3: Unknown email invite is rejected**
    - **Validates: Requirements 2.3, 7.5**

  - [ ]* 3.4 Write property test for `POST /collaborations` — duplicate email returns 409
    - **Property 4: Duplicate email invite is rejected**
    - **Validates: Requirements 2.5, 7.6**

  - [x] 3.5 Implement `GET /collaborations?ownerUserId=...`
    - Query `collaborations` collection filtered by `ownerUserId`, return list of `CollaborationRecord`
    - _Requirements: 7.2_

  - [ ]* 3.6 Write property test for collaboration round-trip
    - **Property 12: API collaboration round-trip**
    - **Validates: Requirements 7.7**

  - [ ]* 3.7 Write property test for valid invite creates a retrievable record
    - **Property 5: Valid invite creates a retrievable record**
    - **Validates: Requirements 2.6, 2.7**

  - [x] 3.8 Implement `DELETE /collaborations/{invite_id}`
    - Return 404 if document not found, otherwise delete and return success
    - _Requirements: 7.3_

  - [x] 3.9 Implement `GET /collaborations/invited?collaboratorUid=...`
    - Query `collaborations` by `collaboratorUid`, join with `users` to get owner name/email, return list of `InvitedBoard`
    - _Requirements: 7.4_

  - [ ]* 3.10 Write property test for invite deletion removes access
    - **Property 8: Invite deletion removes access**
    - **Validates: Requirements 4.2, 4.3, 4.4**

  - [ ]* 3.11 Write property test for board switch loads owner's tasks
    - **Property 9: Board switch loads owner's tasks**
    - **Validates: Requirements 5.3, 5.5**

- [ ] 4. Checkpoint — Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create `src/lib/components/CollaboratePanel.svelte`
  - Accept props: `ownerUserId: string`, `currentUserEmail: string`, `open: boolean`
  - On open, fetch collaborators via `getCollaborators(ownerUserId)` and display the list
  - Render email input + "Add" button; on submit validate non-empty, non-self, then call `addCollaborator`
  - Show inline error for self-invite (Requirements 2.4), unknown user (Requirements 2.3), duplicate (Requirements 2.5), and API errors
  - Render "Remove" button per collaborator; on click call `removeCollaborator(invite.id)` and splice from local list
  - Close on Escape keydown or backdrop click; dispatch `close` and `collaboratorsChanged` events
  - _Requirements: 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 4.1, 4.2, 4.3_

  - [ ]* 5.1 Write property test for collaborator panel renders all entries with remove buttons
    - **Property 2: Collaborator panel renders all collaborators with remove buttons**
    - **Validates: Requirements 1.3, 4.1**

  - [ ]* 5.2 Write property test for unknown email invite is rejected in UI
    - **Property 3: Unknown email invite is rejected**
    - **Validates: Requirements 2.3, 7.5**

- [x] 6. Create `src/lib/components/BoardSwitcher.svelte`
  - Accept props: `ownBoard: { userId: string; label: string }`, `invitedBoards: InvitedBoard[]`, `activeUserId: string`
  - Render a `<select>` listing "My Board" first, then each invited board as "{ownerName}'s Board"
  - Dispatch `switch` event with `{ userId, ownerName }` on change
  - Do not render (or render nothing) when `invitedBoards` is empty
  - _Requirements: 5.1, 5.2, 5.3, 6.2_

- [x] 7. Update `src/routes/+page.svelte` to wire collaboration state and components
  - [x] 7.1 Add reactive state: `activeBoardOwnerId`, `activeBoardOwnerName`, `invitedBoards`, `showCollaboratePanel`
    - After login, call `getInvitedBoards(currentUser.uid)` and populate `invitedBoards`
    - _Requirements: 5.1, 5.2_

  - [x] 7.2 Replace hardcoded `currentUser.uid` with `activeBoardOwnerId` in all `getTasks`, `createTask`, and `updateTask` calls
    - New tasks must be stored under `activeBoardOwnerId` (Requirements 5.5)
    - _Requirements: 5.3, 5.5_

  - [x] 7.3 Add board identity label logic and display it in the board header
    - `boardLabel = activeBoardOwnerId === currentUser?.uid ? 'My Board' : \`${activeBoardOwnerName.split(' ')[0]}'s Board\``
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 7.4 Write property test for board identity label correctness
    - **Property 11: Board identity label correctness**
    - **Validates: Requirements 6.1, 6.2**

  - [x] 7.5 Render `<BoardSwitcher>` in the board header when `invitedBoards.length > 0`; handle `switch` event to update `activeBoardOwnerId` / `activeBoardOwnerName` and reload tasks
    - _Requirements: 5.2, 5.3_

  - [x] 7.6 Render "Collaborate" button in the board header; show only when `activeBoardOwnerId === currentUser.uid`; on click set `showCollaboratePanel = true`
    - _Requirements: 1.1, 1.5_

  - [ ]* 7.7 Write property test for collaborate button visibility is owner-only
    - **Property 1: Collaborate button visibility is owner-only**
    - **Validates: Requirements 1.5**

  - [x] 7.8 Render `<CollaboratePanel>` bound to `showCollaboratePanel`; handle `close` event
    - _Requirements: 1.2, 1.4_

  - [x] 7.9 Hide the delete button on tasks when `activeBoardOwnerId !== currentUser.uid`
    - _Requirements: 5.6_

  - [ ]* 7.10 Write property test for collaborator cannot delete tasks on foreign boards
    - **Property 10: Collaborator cannot delete tasks on foreign boards**
    - **Validates: Requirements 5.6**

- [x] 8. Update `firestore.rules` to add security rules for `users` and `collaborations` collections
  - Allow authenticated users to read any `users` doc; allow write only to own doc (where `uid == request.auth.uid`)
  - Allow board owner to read/write `collaborations` where `ownerUserId == request.auth.uid`
  - Allow collaborator to read `collaborations` where `collaboratorUid == request.auth.uid`
  - Allow collaborator to read/write `kanban-tasks` where the task's `userId` matches an owned collaboration invite
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 9. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Property tests use [fast-check](https://github.com/dubzzz/fast-check) for TypeScript and [Hypothesis](https://hypothesis.readthedocs.io/) for Python
- Each property test must include a comment: `// Feature: board-collaboration, Property N: <property_text>`
- All task API calls must use `activeBoardOwnerId` (not `currentUser.uid`) once board switching is wired up
