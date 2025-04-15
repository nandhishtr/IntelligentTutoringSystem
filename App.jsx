import React, { useEffect } from "react";
import { createBrowserRouter, RouterProvider, useLocation } from "react-router-dom";
import Home from "./components/home";
import GenerateFlashcard from "./components/generate_flashcard";
import History from "./components/history";
import Quizz from "./components/Quizz";
import { motion } from "motion/react"
import { AnimatePresence } from "motion/react";
import ProductProvider  from "./components/Product_context";
import LoginPage from "./components/LoginPage";

const App = () => {
 
  const router = createBrowserRouter([
    {
      path: "/",
      element: <Home />,
      children: [
        { path: "/history", element: <History /> },
        { path: "/generate_flashcard", element: <GenerateFlashcard /> },
         { path: "/LoginPage", element: <LoginPage/> },
        { path: "/quizz", element: <Quizz /> },
      ],
    },
  ]);

  return (
  
    <ProductProvider>
      <AnimatePresence mode="wait">
      <RouterProvider router={router} />
      </AnimatePresence>
      </ProductProvider>
    
  );
};

export default App;
