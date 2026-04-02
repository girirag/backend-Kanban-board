/**
 * Pure logic helpers for task details.
 * Feature: task-details
 */

/**
 * Adds a value to the assignee list if it is non-empty and not already present.
 * Returns the updated list on success, or an error string on failure.
 */
export function addAssignee(
  list: string[],
  value: string
): { list: string[] } | { error: string } {
  const trimmed = value.trim();
  if (trimmed === '') {
    return { error: 'Assignee name cannot be empty.' };
  }
  if (list.includes(trimmed)) {
    return { error: 'Assignee already added.' };
  }
  return { list: [...list, trimmed] };
}

/**
 * Removes the entry at the given index from the assignee list.
 * Returns a new list without that entry.
 */
export function removeAssignee(list: string[], index: number): string[] {
  return list.filter((_, i) => i !== index);
}

/**
 * Returns true if the description text is within the 500-character limit.
 */
export function validateDescription(text: string): boolean {
  return text.length <= 500;
}
