import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDrhDmkKxKpYIrMO84B3QAth70x3FXzW18",
  authDomain: "proyectoiot-177e9.firebaseapp.com",
  projectId: "proyectoiot-177e9",
  storageBucket: "proyectoiot-177e9.appspot.com", // 🔹 Aquí estaba mal antes
  messagingSenderId: "610387539253",
  appId: "1:610387539253:web:59b06576fc212f9c92087c",
  measurementId: "G-Y07NYQGF67",
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };
