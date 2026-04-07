import { auth, googleProvider, db } from './firebase';
import { signInWithPopup, signOut, onAuthStateChanged, type User } from 'firebase/auth';
import { doc, setDoc, serverTimestamp, collection, query, where, getDocs, writeBatch } from 'firebase/firestore';

export async function registerUserAndResolveInvites(user: User): Promise<void> {
  const { uid, email, displayName } = user;
  try {
    // Upsert user record
    await setDoc(
      doc(db, 'users', uid),
      { uid, email, displayName, updatedAt: serverTimestamp() },
      { merge: true }
    );
    // Resolve any pending collaboration invites for this email
    if (email) {
      const collabRef = collection(db, 'collaborations');
      const pendingQuery = query(
        collabRef,
        where('collaboratorEmail', '==', email),
        where('pending', '==', true)
      );
      const snapshot = await getDocs(pendingQuery);
      if (!snapshot.empty) {
        const batch = writeBatch(db);
        snapshot.forEach(docSnap => {
          batch.update(docSnap.ref, { collaboratorUid: uid, pending: false });
        });
        await batch.commit();
        console.log(`Resolved ${snapshot.size} pending invite(s) for ${email}`);
      }
    }
  } catch (err) {
    console.error('Error registering user or resolving invites:', err);
  }
}

export async function signInWithGoogle(): Promise<User> {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    // Await registration + invite resolution so board switcher loads correctly
    await registerUserAndResolveInvites(result.user);
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
