import React, { useState } from "react";
import { HiMenuAlt2 } from "react-icons/hi";
import { Link, Outlet } from "react-router-dom";
import { MdHistory } from "react-icons/md";
import { FaRegNewspaper } from "react-icons/fa6";
import { RiAccountCircleLine } from "react-icons/ri";
import { PiCardsThreeBold } from "react-icons/pi";
import { motion } from "motion/react"
import { easeInOut } from "motion";
const Home = () => {
  const menus = [
    { name: "LoginPage", link: "/LoginPage", icon: RiAccountCircleLine },
    { name: "User history", link: "/history", icon: MdHistory },
    { name: "Generate flashcards", link: "/generate_flashcard", icon: PiCardsThreeBold },
    { name: "Generate quiz", link: "/Quizz", icon: FaRegNewspaper },
  ];

  const [open, setOpen] = useState(false);

  return (
    
    <div className="flex w-full h-auto bg-white">
      <motion.div
          whileHover={{ scale: 1. }}
          whileTap={{ scale: 1.05}}
        className={`slidebar ${
          open ? "w-72" : "w-20"
        } duration-500 bg-zinc-900 rounded-3xl px-4 space-y-10 h-[45.25vw]  m-1 fixed z-10`}
      >
        <div className="py-3 flex justify-end">
          <HiMenuAlt2
            size={30}
            className="cursor-pointer text-zinc-300 m-2 hover:bg-zinc-700 rounded-3xl"
            onClick={() => setOpen(!open)}
          />
        </div>
        <div className="flex flex-col mt-4 gap-4 relative py-6">
          {menus.map((menu, i) => (
            <Link
              to={menu.link}
              key={i}
              className="flex items-center gap-5 font-medium p-2 text-sm hover:bg-zinc-700 rounded-3xl"
            >
              <motion.div
               whileHover={{ scale: 1. }}
               whileTap={{ scale: 0.85}}
            
              className="text-zinc-300 flex gap-6">
                {React.createElement(menu.icon, { size: "35" })}
          
              <h2
                className={`text-zinc-300 text-2xl ${!open && "hidden"}`}
              >
                {menu.name}
              </h2>
              </motion.div>
            </Link>
          ))}
        </div>
      </motion.div>
      <div className="ml-20 w-full h-full">
        <Outlet />
      </div>
    </div>
  );
};

export default Home;
