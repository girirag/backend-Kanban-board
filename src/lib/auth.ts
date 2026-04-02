import { auth, googleProvider, db } from './firebase';
import { signInWithPopup, signOut, onAuthStateChanged, type User } from 'firebase/auth';
import { doc, setDoc, serverTimestamp, collection, query, where, getDocs, writeBatch } from 'firebase/firestore';

export async function signInWithGoogle(): Promise<User> {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const { uid, email, displayName } = result.user;

    // Non-blocking upsert — best-effort, does not delay sign-in return
    setDoc(
      doc(db, 'users', uid),
      { uid, email, displayName, updatedAt: serverTimestamp() },
      { merge: true }
    ).then(async () => {
      // Resolve any pending collaboration invites for this email
      if (email) {
        try {
          const collabRef = collection(db, 'collaborations');
          const pendingQuery = query(collabRef, where('collaboratorEmail', '==', email), where('pending', '==', true));
          const snapshot = await getDocs(pendingQuery);
          if (!snapshot.empty) {
            const batch = writeBatch(db);
            snapshot.forEach(docSnap => {
              batch.update(docSnap.ref, { collaboratorUid: uid, pending: false });
            });
            await batch.commit();
          }
        } catch (err) {
          console.error('Error resolving pending invites:', err);
        }
      }
    }).catch((err) => console.error('Error writing user record:', err));

    return result.user;
  } catch (error) {
    console.error('Error signing in with Google:', error);
    throw error;
  }
}

export async function logout(): Promise<void> {
  try {
    await signOut(auth);
  } catch (error) {
    console.error('Error signing out:', error);
    throw error;
  }
}

export function onAuthChange(callback: (user: User | null) => void) {
  return onAuthStateChanged(auth, callback);
}
