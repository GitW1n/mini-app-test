import React, { useState, useEffect } from "react";

const App = () => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <header className="header">
        <button onClick={() => console.log("Настройки")}>⚙️</button>
        <div className="clock">{time.toLocaleTimeString()}</div>
      </header>
      <div className="content">Добро пожаловать!</div>
    </div>
  );
};

export default App;
