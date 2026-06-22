// Minimal placeholder for the AQF demo UI.
// Replace with a React app or wire to your existing React hierarchy.
export function render() {
  const root = document.getElementById('root');
  if (root) {
    root.innerHTML = `
      <div style="font-family: Arial; padding: 24px;">
        <h1>AQF Demo Starter</h1>
        <p>Backend and runtime scaffold created.</p>
        <ol>
          <li>Load dataset</li>
          <li>Generate AQF</li>
          <li>Build query</li>
          <li>Explain AQL</li>
        </ol>
      </div>
    `;
  }
}
