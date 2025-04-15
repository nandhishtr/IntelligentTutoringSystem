import React from "react";
import { motion } from "framer-motion";
const Loader = () => {
  const LoaderVarients = {
    animateOne: {
      X: [-20, 20],
      Y: [0, -30],
      transition: {
        X: {
          yoyo: Infinity,
          duration :0.5
        },
        Y: {
            yoyo: Infinity,
            duration :0.25
          },
      },
    },
  };
  return (
  <>
  <motion.div className="loader">  
   Variants = {LoaderVarients}
   animate ={"animateOne"}
  </motion.div>
  </>
  )
};

export default Loader;
