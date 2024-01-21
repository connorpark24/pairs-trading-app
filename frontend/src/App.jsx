import { useState } from "react";
import axios from "axios";
import { BarLoader } from "react-spinners";

function App() {
  const [ticker1, setTicker1] = useState("");
  const [ticker2, setTicker2] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [std, setStd] = useState("");
  const [movingAverageLength, setMovingAverageLength] = useState("");
  const [plots, setPlots] = useState({});
  const [testResults, setTestResults] = useState({
    coint_p: null,
    adf_p: null,
  });
  const [requestMade, setRequestMade] = useState(false);
  const [loading, setLoading] = useState(false);

  const plotTitles = {
    prices: "Prices",
    static: "Stock Price Ratio",
    bands: "Upper and Lower Bands",
    static_returns: "Cumulative Returns",
    bands_returns: "Cumulative Returns",
    prices_signals: "Prices with Signals",
  };

  function formatDate(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const day = date.getDate().toString().padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  const today = new Date();
  const lastYear = new Date(
    today.getFullYear() - 1,
    today.getMonth(),
    today.getDate()
  );

  const defaultStartDate = formatDate(lastYear);
  const defaultEndDate = formatDate(today);

  // const validateInputs = () => {
  //   let isValid = true;
  //   const errors = {};

  //   // Validate ticker symbols
  //   if (!ticker1.trim()) {
  //     isValid = false;
  //     errors.ticker1 = "Ticker 1 is required.";
  //   }

  //   if (!ticker2.trim()) {
  //     isValid = false;
  //     errors.ticker2 = "Ticker 2 is required.";
  //   }

  //   // Validate start and end date format (YYYY-MM-DD)
  //   const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  //   if (!dateRegex.test(startDate)) {
  //     isValid = false;
  //     errors.startDate = "Invalid start date format (YYYY-MM-DD).";
  //   }

  //   if (!dateRegex.test(endDate)) {
  //     isValid = false;
  //     errors.endDate = "Invalid end date format (YYYY-MM-DD).";
  //   }

  //   // Validate numerical inputs
  //   if (isNaN(std)) {
  //     isValid = false;
  //     errors.std = "Invalid standard deviation input.";
  //   }

  //   if (isNaN(movingAverageLength)) {
  //     isValid = false;
  //     errors.movingAverageLength = "Invalid moving average length input.";
  //   }

  //   // Display error messages if validation fails
  //   if (!isValid) {
  //     console.error("Input validation failed:", errors);
  //     // You can set error messages in state and display them to the user
  //     return false;
  //   }

  //   return true;
  // };

  const handleSubmit = async (event) => {
    setLoading(true);
    event.preventDefault();

    // if (!validateInputs()) {
    //   setLoading(false);
    //   return;
    // }

    try {
      const response = await axios.get("http://localhost:8000/", {
        ticker1,
        ticker2,
        startDate,
        endDate,
        std: parseFloat(std),
        window: parseInt(movingAverageLength),
      });
      setPlots(response.data);
      setTestResults({
        coint_p: response.data.coint_p,
        adf_p: response.data.adf_p,
      });
      setRequestMade(true);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-2 mx-auto p-4">
      <h1 className="text-4xl text-center">Pairs Trading Algorithm</h1>
      <h1 className="text-sm text-center lg:w-3/5 my-2">
        Pairs trading algorithm implemented using two different strategies. Uses
        Yahoo Finance to fetch stock data, numpy and pandas to process and
        prepare data, and matplotlib to display results. Frontend built using
        React and data processing done via Django backend.
      </h1>
      <form
        onSubmit={handleSubmit}
        className="flex flex-col items-center gap-4 mx-auto"
      >
        <div className="grid sm:grid-cols-2 lg:grid-cols-6 flex-wrap gap-4">
          <div className="flex flex-col">
            <label className="text-base text-gray-700">Ticker 1</label>
            <input
              type="text"
              value={ticker1}
              onChange={(e) => setTicker1(e.target.value)}
              placeholder="AAPL"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-base text-gray-700">Ticker 2</label>
            <input
              type="text"
              value={ticker2}
              onChange={(e) => setTicker2(e.target.value)}
              placeholder="MSFT"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-base text-gray-700">
              Start Date (YYYY-MM-DD)
            </label>
            <input
              type="text"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              placeholder={defaultStartDate}
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-base text-gray-700">
              End Date (YYYY-MM-DD)
            </label>
            <input
              type="text"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              placeholder={defaultEndDate}
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-base text-gray-700">
              Standard Deviation
            </label>
            <input
              type="number"
              value={std}
              onChange={(e) => setStd(e.target.value)}
              placeholder="1.50"
              step="0.05"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-base text-gray-700">MA Window</label>
            <input
              type="number"
              value={movingAverageLength}
              onChange={(e) => setMovingAverageLength(e.target.value)}
              placeholder="20"
              className="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        <button
          type="submit"
          className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 w-56 lg:w-96"
        >
          Get Graphs
        </button>
      </form>
      {loading ? (
        <div className="mt-20">
          <BarLoader color={"#3b82f6"} width={150} loading={loading} />
        </div>
      ) : requestMade ? (
        <div className="grid grid-cols-1 lg:grid-cols-2">
          <div className="lg:col-span-2 text-xl mt-4 text-center">
            <p>Cointegration Test P-Value: {testResults.coint_p.toFixed(4)}</p>
            <p>ADF Test P-Value: {testResults.adf_p.toFixed(4)}</p>
          </div>
          <img
            src={`data:image/png;base64,${plots.prices}`}
            alt={plotTitles.prices}
            className="lg:col-span-2 lg:w-3/5 mx-auto"
          />

          {["static", "bands", "static_returns", "bands_returns"].map((key) => (
            <div key={key} className="flex flex-col items-center">
              <img
                src={`data:image/png;base64,${plots[key]}`}
                alt={plotTitles[key]}
                className="max-w-full"
                style={{ width: "100%" }}
              />
            </div>
          ))}

          <img
            src={`data:image/png;base64,${plots.prices_signals}`}
            alt={plotTitles.prices_signals}
            className="lg:col-span-2 lg:w-3/5 mx-auto"
          />
        </div>
      ) : (
        <div></div>
      )}
    </div>
  );
}

export default App;
