import axios from 'axios';
import './App.css';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from './pages/Login';
import Register from './pages/Register';
import Predict from './pages/Predict';
import Images from './pages/Images';
import TrainClassification from './pages/TrainClassification';
import TrainDetection from './pages/TrainDetection';
import { ToastContainer } from 'react-toastify';
import Layout
 from './components/Layout';
 import { UserProvider } from "./providers/UserContext";
axios.default.baseURL = "http://localhost:4000";
function App() {
  return (
    <BrowserRouter>
      <ToastContainer />
      <UserProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Predict />} />
            <Route path="/login" element={<Login />}/>
            <Route path="/register" element={<Register />}/>
            <Route path="/predict" element={<Predict />}/>
            <Route path="/train_classification" element={<TrainClassification />}/>
            <Route path="/train_detection" element={<TrainDetection />}/>
            <Route path="/images" element={<Images />}/>
          </Route>
        </Routes>
      </UserProvider>  
    </BrowserRouter>
  );
}

export default App;
