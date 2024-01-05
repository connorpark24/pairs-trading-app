import React, { useState } from "react";
import axios from "axios";

function App() {
  const [ticker1, setTicker1] = useState("");
  const [ticker2, setTicker2] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [std, setStd] = useState(1.5);
  const [movingAverageLength, setMovingAverageLength] = useState("");
  const [plots, setPlots] = useState({});
  const [loading, setLoading] = useState(false);

  const plotTitles = {
    prices: "Prices",
    static: "Stock Price Ratio",
    bands: "Upper and Lower Bands",
    static_returns: "Cumulative Returns",
    bands_returns: "Cumulative Returns",
  };

  const handleSubmit = async (event) => {
    setLoading(true);
    event.preventDefault();

    try {
      const response = await axios.post("http://localhost:8000/api/stocks/", {
        ticker1,
        ticker2,
        startDate,
        endDate,
        std: parseFloat(std),
        window: parseInt(movingAverageLength),
      });
      setPlots(response.data);
      console.log(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-2 container mx-auto p-4">
      <h1 className="text-4xl text-center">Pairs Trading Algorithm</h1>
      <h1 className="text-xl text-center">Description</h1>
      <form
        onSubmit={handleSubmit}
        className="flex flex-col items-center gap-4 mx-auto"
      >
        <div className="flex gap-4">
          <div className="flex flex-col">
            <label htmlFor="ticker1" className="text-lg text-gray-700">
              Ticker 1
            </label>
            <input
              type="text"
              id="ticker1"
              value={ticker1}
              onChange={(e) => setTicker1(e.target.value)}
              placeholder="AAPL"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label htmlFor="ticker2" className="text-lg text-gray-700">
              Ticker 2
            </label>
            <input
              type="text"
              id="ticker2"
              value={ticker2}
              onChange={(e) => setTicker2(e.target.value)}
              placeholder="MSFT"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label htmlFor="startDate" className="text-lg text-gray-700">
              Start Date
            </label>
            <input
              type="text"
              id="startDate"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              placeholder="YYYY-MM-DD"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label htmlFor="endDate" className="text-lg text-gray-700">
              End Date
            </label>
            <input
              type="text"
              id="endDate"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              placeholder="YYYY-MM-DD"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label htmlFor="std" className="text-lg text-gray-700">
              Standard Deviation
            </label>
            <input
              type="number"
              id="std"
              value={std}
              onChange={(e) => setStd(e.target.value)}
              placeholder="2"
              step="0.1"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label
              htmlFor="movingAverageLength"
              className="text-lg text-gray-700"
            >
              Moving Average Length
            </label>
            <input
              type="number"
              id="movingAverageLength"
              value={movingAverageLength}
              onChange={(e) => setMovingAverageLength(e.target.value)}
              placeholder="20"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        <button
          type="submit"
          className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 w-2/5"
        >
          Get Graph
        </button>
      </form>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="flex flex-col">
          <div className="flex w-full">
            <img
              src={`data:image/png;base64,${plots.prices}`}
              alt={plotTitles.prices}
              className="w-3/5 mx-auto"
            />
          </div>
          <div className="grid grid-cols-2">
            {["static", "bands", "static_returns", "bands_returns"].map(
              (key) => (
                <div key={key} className="flex flex-col items-center mb-8">
                  <img
                    src={`data:image/png;base64,${plots[key]}`}
                    alt={plotTitles[key]}
                    className="max-w-full"
                    style={{ width: "100%" }}
                  />
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
