import React from "react";
import { TbCards } from "react-icons/tb";
import { GiCardPick } from "react-icons/gi";

const History = () => {
  return (
    <div className="w-full h-auto">
      {/*Flashcards Section*/}
      <div className="flex">
        <h1 className="text-[2vw] mt-[1vw] p-10">Flashcards</h1>
        <div className="text-[2.5vw] mt-[3.5vw]">
          <TbCards />
        </div>
      </div>

      <div className="flex">
        <div className="main-group flex flex-col ml-[4.5vw]">
          <div className="group w-[20vw] h-[25vw] [perspective:1000px]">
            <div className="card relative w-full h-full transition-all duration-500 font-['Founders_Grotesk'] cursor-pointer [transform-style:preserve-3d] group-hover:[transform:rotateY(180deg)]">
              {/* Front Side */}
              <div className="front absolute w-full h-full bg-[#18181B]  rounded-2xl shadow-xl p-5 text-[1.5vw] [backface-visibility:hidden]">
                <h1 className="font-semibold font-['Founders_Grotesk'] ml-[4vw]">
                  
              
                </h1>
                <div className="flex justify-center items-center text-[#D4D4D8]">
                5. Which word is used to ask for information about when something happened in German?
                </div>
              </div>
              {/* Back Side */}
              <div className="back absolute w-full h-full bg-[#18181B] rounded-2xl shadow-xl p-5 text-[1.5vw] [transform:rotateY(180deg)] [backface-visibility:hidden]">
                <div className="py-[9vw] px-[4vw] text-[#D4D4D8]">Answer to the question: <br />was</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quizzes Section */}
      <div className="flex">
        <h1 className="text-[2vw] p-10 mt-[6vw]">Quizzes</h1>
        <div className="text-[3vw] mt-[8vw]">
          <GiCardPick />
        </div>
      </div>

      {/* Quiz Cards */}
      <div className="flex">
        <div className="cards w-[20vw] h-[15vw] bg-[#18181B] ml-10 rounded-2xl shadow-xl"></div>
        <div className="cards w-[20vw] h-[15vw] bg-[#18181B] ml-10 rounded-2xl shadow-xl"></div>
        <div className="cards w-[20vw] h-[15vw] bg-[#18181B] ml-10 rounded-2xl shadow-xl"></div>
      </div>
    </div>
  );
};

export default History;
