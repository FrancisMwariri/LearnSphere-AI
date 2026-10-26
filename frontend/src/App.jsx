import './App.css'

function App() {
  return (
    <main className="page">
      <header className="topbar">
        <a className="brand" href="/" aria-label="LearnSphere AI home">
          <span className="brand-mark" aria-hidden="true">L</span>
          <span>LearnSphere <span className="brand-accent">AI</span></span>
        </a>
        <span className="status"><span className="status-dot" /> Your learning space</span>
      </header>

      <section className="welcome" aria-labelledby="welcome-title">
        <p className="eyebrow">A new way to learn</p>
        <h1 id="welcome-title">Curiosity has a place to grow.</h1>
        <p className="intro">
          LearnSphere is your future home for thoughtful, interactive lessons
          with an AI-powered virtual teacher.
        </p>
        <div className="coming-soon">
          <span className="sparkle" aria-hidden="true">✦</span>
          <div>
            <h2>Your classroom is taking shape</h2>
            <p>We’re building a more personal way to explore what you love.</p>
          </div>
        </div>
      </section>

      <footer className="footer">
        <span>Learn at your pace. Go further every day.</span>
        <span>Made for curious minds</span>
      </footer>
    </main>
  )
}

export default App
