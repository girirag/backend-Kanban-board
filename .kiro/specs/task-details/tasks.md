# Implementation Plan: Task Details

## Overview

Extend the Kanban board with per-task detail editing. Implementation covers three layers: TypeScript interfaces in `api.ts`, a new `TaskDetailModal.svelte` component with indicator markup in `+page.svelte`, and Python/Pydantic model + handler changes in `backend/main.py`.

## Tasks

- [x] 1. Extend data model interfaces
  - Add `description?: string` and `assignees?: string[]` to the `Task` interface in `src/lib/api.ts`
  - Add `description?: string` and `assignees?: string[]` to the `TaskUpdate` interface in `src/lib/api.ts`
  - _Requirements: 4.4_

- [x] 2. Extend backend Pydantic models and PUT handler
  - [x] 2.1 Update `Task` and `TaskUpdate` Pydantic models in `backend/main.py` to include optional `description` and `assignees` fields
    - `description: Optional[str] = None`
    - `assignees: Optional[List[str]] = []`
    - _Requirements: 4.4_
  - [x] 2.2 Update `PUT /tasks/{task_id}` handler to apply `description` and `assignees` when present, mirroring the existing `text`/`column` pattern
    - Persist updated fields to Firebase and file backup
    - _Requirements: 4.1, 4.4_
  - [ ]* 2.3 Write property test for API optional fields (Property 10)
    - **Property 10: API accepts optional detail fields**
    - **Validates: Requirements 4.4, 4.1**
    - Use Hypothesis in `backend/test_task_details_properties.py`
    - For any update payload with `description`/`assignees` present, assert 200 response body reflects submitted values
    - For any payload without those fields, assert existing values are preserved

- [ ] 3. Checkpoint — ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement pure logic helpers for task details
  - [x] 4.1 Create `src/lib/taskDetailsUtils.ts` with pure functions:
    - `addAssignee(list: string[], value: string): { list: string[] } | { error: string }`
    - `removeAssignee(list: string[], index: number): string[]`
    - `validateDescription(text: string): boolean` (true if length ≤ 500)
    - _Requirements: 2.2, 3.2, 3.3, 3.4, 3.5_
  - [ ]* 4.2 Write property test for `addAssignee` — grows list (Property 7)
    - **Property 7: Add assignee grows list**
    - **Validates: Requirements 3.2**
    - Use fast-check in `src/lib/__tests__/taskDetails.property.test.ts`
  - [ ]* 4.3 Write property test for `addAssignee` — duplicate rejected (Property 8)
    - **Property 8: Duplicate assignee rejected**
    - **Validates: Requirements 3.3**
  - [ ]* 4.4 Write property test for `removeAssignee` — shrinks list (Property 9)
    - **Property 9: Remove assignee shrinks list**
    - **Validates: Requirements 3.5**
  - [ ]* 4.5 Write property test for `validateDescription` — length constraint (Property 4)
    - **Property 4: Description length constraint**
    - **Validates: Requirements 2.2, 2.3**

- [x] 5. Build `TaskDetailModal.svelte` component
  - [x] 5.1 Create `src/lib/components/TaskDetailModal.svelte` with props `task: Task` and `open: boolean`
    - Internal draft state: `draftDescription`, `draftAssignees`, `assigneeInput`, `assigneeError`, `saveError`, `saving`
    - Textarea with `maxlength="500"` and live character counter
    - Assignee input with Enter/Add button, inline duplicate error, remove buttons per assignee
    - Save button that dispatches `save` event with updated task; Close/Escape/backdrop dispatches `close`
    - Inline error banner on API failure; retain draft on error
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 4.5_
  - [ ]* 5.2 Write property test — modal displays task data (Property 2)
    - **Property 2: Modal displays task data**
    - **Validates: Requirements 1.2, 2.1, 3.1**
    - Use fast-check in `src/lib/__tests__/taskDetails.property.test.ts`
  - [ ]* 5.3 Write property test — close discards draft (Property 3)
    - **Property 3: Close discards draft**
    - **Validates: Requirements 1.4, 1.5**

- [x] 6. Wire `TaskDetailModal` into `+page.svelte`
  - [x] 6.1 Import `TaskDetailModal` and add `let selectedTask: Task | null = null` reactive variable
    - Task card `on:click` sets `selectedTask = task` with `stopPropagation` to block DnD
    - Handle `save` event: call `apiService.updateTask`, update board state, save to localStorage; fall back to localStorage on API error
    - Handle `close` event: set `selectedTask = null`
    - _Requirements: 1.1, 1.3, 4.1, 4.2_
  - [ ]* 6.2 Write property test — clicking a task opens the modal for that task (Property 1)
    - **Property 1: Clicking a task opens the modal for that task**
    - **Validates: Requirements 1.1**
    - Use fast-check in `src/lib/__tests__/taskDetails.property.test.ts`
  - [ ]* 6.3 Write property test — save round-trip (Property 5)
    - **Property 5: Save round-trip**
    - **Validates: Requirements 2.4, 3.6, 4.1**

- [x] 7. Add task card detail indicators in `+page.svelte`
  - Inside the `.task` markup, below `.task-meta`, add an indicator area:
    - Description icon (e.g. 📝) rendered only when `task.description` is non-empty
    - Assignee badges (initials or count) rendered only when `task.assignees?.length > 0`
    - No indicator area rendered when both fields are absent
    - Use colours consistent with the existing red theme
    - _Requirements: 2.5, 3.7, 5.1, 5.2, 5.3, 5.4_
  - [ ]* 7.1 Write property test — task card indicators reflect task data (Property 6)
    - **Property 6: Task card indicators reflect task data**
    - **Validates: Requirements 2.5, 3.7, 5.1, 5.2, 5.3**
    - Use fast-check in `src/lib/__tests__/taskDetails.property.test.ts`

- [ ] 8. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use fast-check (frontend) and Hypothesis (backend)
- Unit tests validate specific examples and edge cases; property tests validate universal correctness
