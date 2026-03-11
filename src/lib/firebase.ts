import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBgYiAy5D-r55RfSz-4j23TCyONDW-zCXs",
  authDomain: "firstapp-ddec4.firebaseapp.com",
  projectId: "firstapp-ddec4",
  storageBucket: "firstapp-ddec4.firebasestorage.app",
  messagingSenderId: "947799663684",
  appId: "1:947799663684:web:4dae79009d9fe9d7d08811"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();