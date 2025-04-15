import React, { createContext, useContext } from "react";
import { ProductContext } from "./Product_context";



const ProductList = () => {
  const { product } = useContext(ProductContext); // Extract product data from context

  return (
    
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
      {product.length === 0 ? (
        <p>Loading products...</p>
      ) : (
        product.map(({ id, price, description, Question , Choices ,CorrectAnswer , Difficulty ,Topic, LearningObjective}) => (
          <div
            key={id}
            className="border border-gray-300 rounded-lg p-4 shadow-lg"
          >
           
            <h2 className="text-lg font-bold">{Question}</h2>
            
            <ul>
                {Choices.map((item, index) => (
                    <li key={index}>{item}</li> // Dynamically render each item in a list
                ))}
            </ul>
          </div>
        ))
      )}
    </div>
  );
};

export default ProductList;
