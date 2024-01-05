import React, { useState } from "react";
import axios from "axios";

function App() {
  const [ticker1, setTicker1] = useState("");
  const [ticker2, setTicker2] = useState("");
  const [plots, setPlots] = useState({});
  const [loading, setLoading] = useState(false);

  const plotTitles = {
    prices: "Prices",
    spread: "Stock Price Spread",
    ratio: "Stock Price Ratio",
    bands: "Upper and Lower Bands",
    returns: "Cumulative Returns",
  };

  const handleSubmit = async (event) => {
    setLoading(true);
    event.preventDefault();

    try {
      const response = await axios.post("http://localhost:8000/api/stocks/", {
        ticker1,
        ticker2,
      });
      setPlots(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  return (
    <div className="App container mx-auto p-4">
      <form onSubmit={handleSubmit} className="mb-8">
        {/* ... (your form code) */}
      </form>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {Object.keys(plots).map((key) => (
            <div key={key} className="flex flex-col items-center gap-2 mb-8">
              <h3 className="text-2xl font-bold">{plotTitles[key]}</h3>
              <img
                src={`data:image/png;base64,${plots[key]}`}
                alt={plotTitles[key]}
                className="max-w-full"
                style={{ width: "100%" }} // Automatically fit images
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
