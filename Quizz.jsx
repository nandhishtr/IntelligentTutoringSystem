import React, { useContext, useState } from "react";
import { IoIosAttach } from "react-icons/io";
import { motion } from "framer-motion";
import { ProductContext } from "./Product_context";
import { FaCircleCheck } from "react-icons/fa6";
import { Link } from "react-router-dom";
const Quizz = () => {
  const { product } = useContext(ProductContext); // Extract product data from the ProductContext
  const [fileName, setFileName] = useState(""); // State to store the name of the uploaded file
  const [isUploading, setIsUploading] = useState(false); // Track file uploading status
  const [isGenerating, setIsGenerating] = useState(false); // Track quiz generation status
  const [currentCard, setCurrentCard] = useState(0); // Track the current quiz card index
  const [quizCompleted, setQuizCompleted] = useState(false); // Track quiz completion
  const [answers, setAnswers] = useState({}); // Store selected answers

  // Handle file upload event
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setIsUploading(true);
      setTimeout(() => {
        setFileName(file.name);
        setIsUploading(false);
        setIsGenerating(true);
        setTimeout(() => {
          setIsGenerating(false);
        }, 2000);
      }, 2000);
    } else {
      alert("Please upload a valid PDF file.");
    }
  };

  // Handle moving to the next card or completing the quiz
  const handleNext = () => {
    if (currentCard < product.length - 1) {
      setCurrentCard((prev) => prev + 1);
    } else {
      setQuizCompleted(true); // Mark quiz as completed
      console.log("Selected Answers:", answers); // Log answers on completion
    }
  };

  // Handle moving to the previous card
  const handlePrevious = () => {
    if (currentCard > 0) {
      setCurrentCard((prev) => prev - 1);
    }
  };

  // Handle option selection
  const handleOptionSelect = (questionIndex, choice) => {
    setAnswers((prev) => ({ ...prev, [questionIndex]: choice }));
    console.log(`Question ${questionIndex + 1}: Selected ${choice}`); // Log selected choice immediately
  };

  // Animation variants for card transitions
  const cardVariants = {
    hidden: (direction) => ({
      x: direction > 60 ? 0 : -60,
      opacity: 0,
    }),
    visible: {
      x: 0,
      opacity: 1,
      transition: { duration: 0.25 },
    },
    exit: (direction) => ({
      x: direction < 0 ? 300 : -300,
      opacity: 0,
      transition: { duration: 0.5 },
    }),
  };

  return (
    <div className="w-full h-screen flex flex-col font-['Neue_Montreal'] gap-5 text-3xl items-center justify-center">
      <div className="flex flex-col items-center gap-6">
        {!isUploading && !fileName && (
          <div className="border-2 border-zinc-300 p-[7.5vw] bg-zinc-50 rounded-3xl  flex flex-col items-center gap-4">
            <h1 className="text-zinc-700">Attach a PDF to generate a Quiz</h1>
            <motion.div
              className="gap-4 flex items-center p-4 hover:bg-zinc-200 text-zinc-900 bg-[#F2F2F2] border-2 border-zinc-300 rounded-full w-[15vw] cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 1 }}
              onClick={() => document.getElementById("hiddenFileInput").click()}
            >
              <button>
                <IoIosAttach size={35} />
              </button>
              <div className="text-2xl text-zinc-700">
                <h5>Attach a PDF</h5>
              </div>
            </motion.div>
          </div>
        )}
        {isUploading ? (
          <div className="w-auto p-2 h-auto flex hover:bg-zinc-200 text-zinc-900 bg-[#F2F2F2] border-2 border-zinc-300 rounded-full gap-4">
            <div className="loader text-3xl w-10 h-10 border-4 border-t-transparent border-zinc-900 rounded-full animate-spin"></div>
            <h1 className="">Uploading...</h1>
          </div>
        ) : isGenerating ? (
          <div className="w-auto p-2 h-auto flex hover:bg-zinc-200 text-zinc-900 bg-[#F2F2F2] border-2 border-zinc-300 rounded-full gap-4">
            <div className="loader text-3xl w-10 h-10 border-4 border-t-transparent border-zinc-900 rounded-full animate-spin"></div>
            <h1 className="">Generating Quiz...</h1>
          </div>
        ) : null}

        <input
          type="file"
          id="hiddenFileInput"
          style={{ display: "none" }}
          onChange={handleFileUpload}
          accept="application/pdf"
        />

        {fileName && (
          <div className="rounded-3xl text-xl overflow-hidden text-zinc-900 bg-[#F2F2F2] border-2 border-zinc-300 p-3">
            <u>Attached File:</u> {fileName}
          </div>
        )}

        {fileName && !isGenerating && product.length > 0 && (
          <div className="font-['Neue_Montreal'] flex flex-col relative w-[50vw] h-[40vw] overflow-hidden">
            {!quizCompleted ? (
              <motion.div
                key={currentCard}
                custom={currentCard}
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                className="absolute top-0 left-0 w-full h-full flex flex-col items-start justify-start text-zinc-900 p-4 rounded-lg shadow-md gap-[5vw]"
              >
                <div className="bg-zinc-50 border-2 border-zinc-200 absolute rounded-2xl p-[2vw] m-2 w-[45vw] h-[34vw] flex flex-col gap-8">
                  <h1 className="text-zinc-700 text-3xl mb-3">
                    {currentCard + 1}. {product[currentCard]?.Question}
                  </h1>
                  <div className="text-[1.5vw] gap-5">
                    <div className="flex text-zinc-600 flex-col gap-[.5vw]">
                      {product[currentCard]?.Choices.map((choice, index) => (
                        <label
                          className="w-auto h-auto border-2 text-[1.25vw] border-zinc-300 hover:bg-zinc-300 duration-700 cursor-pointer bg-zinc-100 rounded-2xl p-3 text-zinc-900 flex gap-4"
                          key={index}
                        >
                          <input
                            type="radio"
                            name={`question-${currentCard}`}
                            value={choice}
                            className="accent-zinc-500 scale-150"
                            onChange={() => handleOptionSelect(currentCard, choice)}
                          />
                          {choice}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : (
              <div className="flex items-center justify-center text-center text-2xl w-[50vw] h-[35vw] bg-zinc-100 border-2 border-zinc-300 rounded-3xl text-zinc-600">
              <h2 className="absolute top-0 p-[5vw] text-[2vw] font-light ">
                Quiz Completed!
               
              </h2>
              <div className="text-[7vw] text-zinc-400 absolute top-[10vw]">
              <FaCircleCheck />
              </div>
              <div className="mt-[4vw]">Your Final score is 3/5(60%)</div>
             <motion.button      
               whileHover={{ scale: 1.05 }}
              whileTap={{ scale: .5 }} 
              className="absolute bottom-60 w-auto h-auto hover:bg-zinc-300 duration-300 p-3 border-2 border-zinc-400 rounded-full text-2xl">Restart</motion.button>
              </div>
            )}
            <div className="absolute w-auto h-auto bottom-0 text-zinc-900 left-0 right-0 flex justify-between text-[1.5vw] p-1">
              <button onClick={handlePrevious}></button>
              {!quizCompleted && (
                <button
                  className="border-2 border-zinc-300 bg-[#F2F2F2] hover:bg-zinc-200 p-4 rounded-full"
                  onClick={handleNext}
                >
                  {currentCard === product.length - 1 ? "End" : "Next"}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Quizz;
