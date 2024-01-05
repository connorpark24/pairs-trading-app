import React, { useState } from "react";
import axios from "axios";

function App() {
  const [ticker1, setTicker1] = useState("");
  const [ticker2, setTicker2] = useState("");
  const [plots, setPlots] = useState({});
  const [loading, setLoading] = useState(false);

  const plotTitles = {
    heatmap: "Correlation Matrix Heatmap",
    spread: "Stock Price Spread",
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
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            value={ticker1}
            onChange={(e) => setTicker1(e.target.value)}
            placeholder="AAPL"
            className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          <input
            type="text"
            value={ticker2}
            onChange={(e) => setTicker2(e.target.value)}
            placeholder="MSFT"
            className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <button
          type="submit"
          className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          Get Graph
        </button>
      </form>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          {Object.keys(plots).map((key) => (
            <div key={key} className="flex flex-col items-center gap-2 mb-8">
              <h3 className="text-2xl font-bold">{plotTitles[key]}</h3>
              <img
                src={`data:image/png;base64,${plots[key]}`}
                alt={plotTitles[key]}
                className="max-w-full"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
