import React, { useContext } from "react"; // Import React and useContext hook
import { IoIosAttach } from "react-icons/io"; // Import the attach icon
import { motion } from "motion/react"; // Import motion for animations
import { MdOutlineArrowForward } from "react-icons/md"; // Import forward arrow icon
import { ProductContext } from "./Product_context"; // Import ProductContext to access product data


const GenerateFlashcard = () => {
  // Consume product data from ProductContext
  const { product } = useContext(ProductContext);

  return (
    <div className="w-full h-auto flex items-center justify-center flex-wrap gap-8 p-8">
      {/* Check if product array is empty; if yes, show loading message, otherwise render flashcards */}
      {product.length === 0 ? (
        <p>Loading flashcards...</p> // Display loading message if data hasn't been fetched yet
      ) : (
        product.map(({ id, Question}) => (
          // Map through product array and generate a flashcard for each product
          <div
            key={id} // Use product ID as a unique key for each flashcard
            className="flashcard flex flex-col items-center"
          >
            <div className="main-group flex flex-col">
              <div className="group w-[20vw] h-[25vw] [perspective:1000px]">
                {/* Flashcard container with 3D perspective for flip effect */}
                <div className="card relative w-full h-full transition-all duration-500 font-['Founders_Grotesk'] cursor-pointer [transform-style:preserve-3d] group-hover:[transform:rotateY(180deg)]">
                  {/* Front side of the flashcard */}
                  <div className="front absolute w-full h-full bg-[#18181B] rounded-2xl shadow-xl p-5 text-[1.5vw] [backface-visibility:hidden]">
                    <h1 className="font-semibold font-['Founders_Grotesk'] text-center">
                      {title} {/* Display product title as the flashcard question */}
                    </h1>
                    <div className="flex justify-center items-center text-[#D4D4D8] mt-4">
                      {description.slice(0, 5)}... {/* Display first 50 characters of the product description */}
                    </div>
                  </div>

                  {/* Back side of the flashcard */}
                  <div className="back absolute w-full h-full bg-[#18181B] rounded-2xl shadow-xl p-5 text-[1.5vw] [transform:rotateY(180deg)] [backface-visibility:hidden]">
                    <div className="py-[9vw] px-[4vw] text-[#D4D4D8] text-center">
                      Full description: {title} {/* Display full product description */}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))
      )}

      {/* Section for attaching files */}
      <div className="type_and_attach flex flex-col items-center mt-8">
        <motion.div
          className="gap-4 flex attach p-4 hover:bg-zinc-700 bg-zinc-900 text-white rounded-full w-[15vw] cursor-pointer"
          whileHover={{ scale: 1.1 }} // Slightly scale up the button on hover
          whileTap={{ scale: 0.98 }} // Slightly scale down the button on tap
          onClick={() => document.getElementById("hiddenFileInput").click()} // Trigger hidden file input on click
        >
          <button>
            <IoIosAttach size={35} /> {/* Render the attach icon */}
          </button>
          <div className="text-2xl">
            <h4> Attach a PDF</h4> {/* Display button text */}
          </div>
        </motion.div>
        <input
          type="file" // Input type for file upload
          id="hiddenFileInput" // ID for referencing this input programmatically
          style={{ display: "none" }} // Hide the file input from view
          accept="application/pdf" // Restrict file input to PDF files only
        />
      </div>
 
    </div>
  );
};

export default GenerateFlashcard; // Export the GenerateFlashcard component for use in other parts of the app
