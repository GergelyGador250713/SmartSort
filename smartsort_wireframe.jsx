import { useState, useRef } from "react";

const RECYCLABLE_MAP = {
  "Plastic Bottle": { bin: "Plastic", category: "Hard Plastic", recyclable: true, tip: "Rinse before recycling. Remove cap if possible." },
  "Glass Jar": { bin: "Glass", category: "Glass", recyclable: true, tip: "Remove lid and rinse. Labels are fine to leave on." },
  "Cardboard Box": { bin: "Paper", category: "Paper / Cardboard", recyclable: true, tip: "Flatten to save space. Remove tape if possible." },
  "Food Waste": { bin: "General Waste", category: "Organic", recyclable: false, tip: "Consider composting! Not suitable for recycling bins." },
  "Aluminium Can": { bin: "Metal", category: "Metal", recyclable: true, tip: "Rinse cans. Crush them to save space." },
  "Plastic Bag": { bin: "General Waste", category: "Soft Plastic", recyclable: false, tip: "Some supermarkets accept soft plastics. Never put in kerbside bins." },
};

const SAMPLE_ITEMS = Object.keys(RECYCLABLE_MAP);

const HISTORY = [
  { item: "Plastic Bottle", date: "Today, 09:14", recyclable: true, bin: "Plastic" },
  { item: "Cardboard Box", date: "Today, 08:52", recyclable: true, bin: "Paper" },
  { item: "Food Waste", date: "Yesterday, 19:30", recyclable: false, bin: "General Waste" },
  { item: "Aluminium Can", date: "Yesterday, 13:11", recyclable: true, bin: "Metal" },
  { item: "Glass Jar", date: "Mon, 10:05", recyclable: true, bin: "Glass" },
  { item: "Plastic Bag", date: "Mon, 09:47", recyclable: false, bin: "General Waste" },
];

const BIN_COLORS = {
  "Plastic": "#F5C518",
  "Paper": "#2196F3",
  "Glass": "#4CAF50",
  "Metal": "#FF9800",
  "General Waste": "#9E9E9E",
};

const STATS = {
  total: 47,
  recyclable: 34,
  nonRecyclable: 13,
  bins: { "Plastic": 16, "Paper": 10, "Glass": 6, "Metal": 2, "General Waste": 13 },
};

export default function App() {
  const [page, setPage] = useState(1); // 0=result, 1=camera, 2=profile
  const [scanning, setScanning] = useState(false);
  const [scanComplete, setScanComplete] = useState(false);
  const [currentResult, setCurrentResult] = useState(null);
  const [loggedIn, setLoggedIn] = useState(true);
  const [dragStart, setDragStart] = useState(null);
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const handleSimulateScan = () => {
    setScanning(true);
    setScanComplete(false);
    setTimeout(() => {
      const randomItem = SAMPLE_ITEMS[Math.floor(Math.random() * SAMPLE_ITEMS.length)];
      setCurrentResult({ item: randomItem, ...RECYCLABLE_MAP[randomItem] });
      setScanning(false);
      setScanComplete(true);
      setTimeout(() => {
        setScanComplete(false);
        setPage(0);
      }, 800);
    }, 2000);
  };

  const handleDragStart = (e) => {
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    setDragStart(clientX);
    setIsDragging(true);
  };

  const handleDragMove = (e) => {
    if (!isDragging || dragStart === null) return;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    setDragOffset(clientX - dragStart);
  };

  const handleDragEnd = () => {
    if (Math.abs(dragOffset) > 60) {
      if (dragOffset < 0 && page < 2) setPage(page + 1);
      if (dragOffset > 0 && page > 0) setPage(page - 1);
    }
    setDragOffset(0);
    setDragStart(null);
    setIsDragging(false);
  };

  const recyclePct = Math.round((STATS.recyclable / STATS.total) * 100);

  return (
    <div style={{
      fontFamily: "'DM Sans', sans-serif",
      background: "#0f0f0f",
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "20px",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { display: none; }

        @keyframes scanLine {
          0% { top: 15%; opacity: 1; }
          100% { top: 75%; opacity: 0.3; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(0.97); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes checkPop {
          0% { transform: scale(0); opacity: 0; }
          60% { transform: scale(1.2); }
          100% { transform: scale(1); opacity: 1; }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        .fade-in { animation: fadeIn 0.4s ease forwards; }
        .check-pop { animation: checkPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
      `}</style>

      {/* Device shell */}
      <div style={{
        width: 375,
        height: 720,
        background: "#111",
        borderRadius: 44,
        overflow: "hidden",
        boxShadow: "0 40px 80px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.08)",
        position: "relative",
        display: "flex",
        flexDirection: "column",
      }}>
        {/* Status bar */}
        <div style={{
          height: 44,
          background: "rgba(0,0,0,0.6)",
          backdropFilter: "blur(10px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          position: "absolute",
          top: 0, left: 0, right: 0,
          zIndex: 100,
        }}>
          <span style={{ color: "#fff", fontSize: 13, fontWeight: 600, fontFamily: "'Space Mono'" }}>9:41</span>
          <div style={{ display: "flex", gap: 5, alignItems: "center" }}>
            {["▋▋▋", "wifi", "🔋"].map((_, i) => (
              <div key={i} style={{ width: i === 2 ? 22 : 16, height: 10, background: "rgba(255,255,255,0.6)", borderRadius: 2 }} />
            ))}
          </div>
        </div>

        {/* Slide container */}
        <div
          style={{
            display: "flex",
            width: "300%",
            height: "100%",
            transform: `translateX(calc(${-page * (100/3)}% + ${dragOffset / 3}px))`,
            transition: isDragging ? "none" : "transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
          }}
          onMouseDown={handleDragStart}
          onMouseMove={handleDragMove}
          onMouseUp={handleDragEnd}
          onMouseLeave={handleDragEnd}
          onTouchStart={handleDragStart}
          onTouchMove={handleDragMove}
          onTouchEnd={handleDragEnd}
        >
          {/* PAGE 0: RESULT */}
          <ResultPage result={currentResult} onBack={() => setPage(1)} />

          {/* PAGE 1: CAMERA */}
          <CameraPage
            scanning={scanning}
            scanComplete={scanComplete}
            onScan={handleSimulateScan}
            onGoResult={() => setPage(0)}
            onGoProfile={() => setPage(2)}
            currentPage={page}
          />

          {/* PAGE 2: PROFILE */}
          <ProfilePage
            loggedIn={loggedIn}
            setLoggedIn={setLoggedIn}
            history={HISTORY}
            stats={STATS}
            recyclePct={recyclePct}
          />
        </div>

        {/* Page indicator dots */}
        <div style={{
          position: "absolute",
          bottom: 20,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          gap: 6,
          zIndex: 200,
          pointerEvents: "none",
        }}>
          {[0, 1, 2].map(i => (
            <div key={i} style={{
              width: page === i ? 20 : 6,
              height: 6,
              borderRadius: 3,
              background: page === i ? "#7ED957" : "rgba(255,255,255,0.3)",
              transition: "all 0.3s ease",
            }} />
          ))}
        </div>
      </div>

        {/* Label hints */}
        <div style={{
          position: "absolute",
          bottom: 6,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "space-between",
          padding: "0 18px",
          color: "rgba(255,255,255,0.25)",
          fontSize: 9,
          fontFamily: "'Space Mono'",
          letterSpacing: 1,
          pointerEvents: "none",
          zIndex: 200,
        }}>
          <span>← RESULT</span>
          <span>CAMERA</span>
          <span>PROFILE →</span>
        </div>
      </div>
  );
}

function ResultPage({ result, onBack }) {
  if (!result) return (
    <div style={{
      width: "33.33%",
      height: "100%",
      background: "linear-gradient(160deg, #0d1a0d 0%, #111 100%)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "60px 28px 80px",
      gap: 16,
    }}>
      <div style={{ fontSize: 48, marginBottom: 8 }}>📸</div>
      <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 14, textAlign: "center", lineHeight: 1.7 }}>
        Take a photo in the camera to see your classification result here.
      </div>
    </div>
  );

  const binColor = BIN_COLORS[result.bin] || "#7ED957";

  return (
    <div className="fade-in" style={{
      width: "33.33%",
      height: "100%",
      background: "linear-gradient(160deg, #0d1a0d 0%, #111 100%)",
      display: "flex",
      flexDirection: "column",
      padding: "60px 0 80px",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{ padding: "0 24px 24px", borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
        <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, fontFamily: "'Space Mono'", letterSpacing: 2, marginBottom: 6 }}>
          CLASSIFICATION RESULT
        </div>
        <div style={{ color: "#fff", fontSize: 22, fontWeight: 700 }}>{result.item}</div>
      </div>

      {/* Big verdict */}
      <div style={{
        margin: "24px",
        borderRadius: 20,
        padding: "28px 24px",
        background: result.recyclable
          ? "linear-gradient(135deg, rgba(126,217,87,0.15), rgba(126,217,87,0.05))"
          : "linear-gradient(135deg, rgba(255,80,80,0.15), rgba(255,80,80,0.05))",
        border: `1px solid ${result.recyclable ? "rgba(126,217,87,0.3)" : "rgba(255,80,80,0.3)"}`,
        display: "flex",
        alignItems: "center",
        gap: 18,
      }}>
        <div style={{
          width: 56,
          height: 56,
          borderRadius: 28,
          background: result.recyclable ? "#7ED957" : "#FF5050",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 26,
          flexShrink: 0,
        }}>
          {result.recyclable ? "♻️" : "🚫"}
        </div>
        <div>
          <div style={{
            color: result.recyclable ? "#7ED957" : "#FF5050",
            fontSize: 18,
            fontWeight: 700,
            marginBottom: 4,
          }}>
            {result.recyclable ? "Recyclable!" : "Not Recyclable"}
          </div>
          <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 13 }}>{result.category}</div>
        </div>
      </div>

      {/* Bin instruction */}
      <div style={{ padding: "0 24px", marginBottom: 16 }}>
        <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, fontFamily: "'Space Mono'", letterSpacing: 2, marginBottom: 10 }}>
          WHERE TO THROW IT
        </div>
        <div style={{
          background: "rgba(255,255,255,0.05)",
          borderRadius: 16,
          padding: "16px 20px",
          display: "flex",
          alignItems: "center",
          gap: 14,
          border: `1px solid ${binColor}30`,
        }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: binColor,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 22,
            flexShrink: 0,
          }}>
            🗑️
          </div>
          <div>
            <div style={{ color: "#fff", fontWeight: 600, fontSize: 16 }}>{result.bin}</div>
            <div style={{ color: binColor, fontSize: 12, marginTop: 2 }}>Tap to see bin locations nearby</div>
          </div>
        </div>
      </div>

      {/* Tip */}
      <div style={{ padding: "0 24px" }}>
        <div style={{
          background: "rgba(255,255,255,0.04)",
          borderRadius: 16,
          padding: "16px 20px",
          border: "1px solid rgba(255,255,255,0.07)",
        }}>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, fontFamily: "'Space Mono'", letterSpacing: 2, marginBottom: 8 }}>
            💡 TIP
          </div>
          <div style={{ color: "rgba(255,255,255,0.75)", fontSize: 13, lineHeight: 1.6 }}>{result.tip}</div>
        </div>
      </div>

      {/* CTA */}
      <div style={{ padding: "16px 24px 0", marginTop: "auto" }}>
        <div style={{
          background: "rgba(126,217,87,0.1)",
          border: "1px solid rgba(126,217,87,0.25)",
          borderRadius: 14,
          padding: "14px",
          textAlign: "center",
          color: "#7ED957",
          fontSize: 13,
          fontWeight: 600,
        }}>
          Swipe right → to scan another item
        </div>
      </div>
    </div>
  );
}

function CameraPage({ scanning, scanComplete, onScan, currentPage }) {
  return (
    <div style={{
      width: "33.33%",
      height: "100%",
      background: "#000",
      position: "relative",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "flex-end",
    }}>
      {/* Fake camera viewfinder */}
      <div style={{
        position: "absolute",
        inset: 0,
        background: scanning
          ? "linear-gradient(160deg, #0a1a0a, #0d2010, #0a1a0a)"
          : "linear-gradient(160deg, #0a120a, #111a0f, #090f09)",
        transition: "background 0.5s",
      }}>
        {/* Grid overlay */}
        <div style={{
          position: "absolute",
          inset: 0,
          backgroundImage: "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }} />

        {/* Subject area */}
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -60%)",
          width: 180,
          height: 180,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: scanning ? 80 : 72,
          animation: scanning ? "pulse 0.8s ease-in-out infinite" : "none",
          transition: "font-size 0.3s",
          filter: scanning ? "saturate(2) brightness(1.3)" : "none",
        }}>
          {scanComplete ? "✅" : "🥤"}
        </div>

        {/* Corner brackets */}
        {[
          { top: "22%", left: "10%", borderTop: "2.5px solid #7ED957", borderLeft: "2.5px solid #7ED957" },
          { top: "22%", right: "10%", borderTop: "2.5px solid #7ED957", borderRight: "2.5px solid #7ED957" },
          { bottom: "38%", left: "10%", borderBottom: "2.5px solid #7ED957", borderLeft: "2.5px solid #7ED957" },
          { bottom: "38%", right: "10%", borderBottom: "2.5px solid #7ED957", borderRight: "2.5px solid #7ED957" },
        ].map((style, i) => (
          <div key={i} style={{ position: "absolute", width: 24, height: 24, ...style }} />
        ))}

        {/* Scan line */}
        {scanning && (
          <div style={{
            position: "absolute",
            left: "10%",
            right: "10%",
            height: 2,
            background: "linear-gradient(90deg, transparent, #7ED957, transparent)",
            boxShadow: "0 0 8px #7ED957",
            animation: "scanLine 1s ease-in-out infinite",
            top: "22%",
          }} />
        )}

        {/* Top label */}
        <div style={{
          position: "absolute",
          top: 60,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "0 20px",
        }}>
          <div style={{
            background: "rgba(0,0,0,0.5)",
            borderRadius: 20,
            padding: "5px 12px",
            color: "#7ED957",
            fontSize: 11,
            fontFamily: "'Space Mono'",
            letterSpacing: 1,
          }}>
            SMART SORT
          </div>
          <div style={{
            background: "rgba(0,0,0,0.5)",
            borderRadius: 20,
            padding: "5px 12px",
            color: "rgba(255,255,255,0.5)",
            fontSize: 11,
          }}>
            {scanning ? "⚡ SCANNING..." : "📍 Breda, NL"}
          </div>
        </div>

        {/* Swipe hints */}
        <div style={{
          position: "absolute",
          top: "50%",
          left: 0,
          right: 0,
          transform: "translateY(-50%)",
          display: "flex",
          justifyContent: "space-between",
          padding: "0 8px",
          pointerEvents: "none",
        }}>
          <div style={{
            color: "rgba(255,255,255,0.2)",
            fontSize: 11,
            fontFamily: "'Space Mono'",
            transform: "rotate(-90deg)",
            letterSpacing: 1,
          }}>← RESULT</div>
          <div style={{
            color: "rgba(255,255,255,0.2)",
            fontSize: 11,
            fontFamily: "'Space Mono'",
            transform: "rotate(90deg)",
            letterSpacing: 1,
          }}>PROFILE →</div>
        </div>
      </div>

      {/* Bottom controls */}
      <div style={{
        position: "relative",
        zIndex: 10,
        width: "100%",
        padding: "24px 28px 80px",
        background: "linear-gradient(to top, rgba(0,0,0,0.95) 0%, transparent 100%)",
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 28 }}>
          {/* Gallery button */}
          <button style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: "rgba(255,255,255,0.1)",
            border: "1px solid rgba(255,255,255,0.15)",
            color: "#fff",
            fontSize: 18,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>🖼</button>

          {/* Shutter */}
          <button
            onClick={!scanning ? onScan : undefined}
            style={{
              width: 76,
              height: 76,
              borderRadius: "50%",
              background: scanning
                ? "rgba(126,217,87,0.3)"
                : "rgba(255,255,255,0.95)",
              border: scanning
                ? "3px solid #7ED957"
                : "4px solid rgba(255,255,255,0.4)",
              cursor: scanning ? "default" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.3s",
              boxShadow: scanning ? "0 0 24px rgba(126,217,87,0.5)" : "none",
              animation: scanning ? "pulse 0.8s ease-in-out infinite" : "none",
            }}
          >
            {scanning
              ? <span style={{ fontSize: 24 }}>♻️</span>
              : <div style={{ width: 56, height: 56, borderRadius: "50%", background: "#111" }} />
            }
          </button>

          {/* Flash */}
          <button style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: "rgba(255,255,255,0.1)",
            border: "1px solid rgba(255,255,255,0.15)",
            color: "#fff",
            fontSize: 18,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>⚡</button>
        </div>

        {!scanning && (
          <div style={{
            textAlign: "center",
            marginTop: 16,
            color: "rgba(255,255,255,0.4)",
            fontSize: 12,
            fontFamily: "'Space Mono'",
            letterSpacing: 1,
          }}>
            TAP TO CLASSIFY
          </div>
        )}
      </div>
    </div>
  );
}

function ProfilePage({ loggedIn, setLoggedIn, history, stats, recyclePct }) {
  return (
    <div style={{
      width: "33.33%",
      height: "100%",
      background: "linear-gradient(160deg, #0a0d1a 0%, #111 100%)",
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        padding: "60px 24px 20px",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, fontFamily: "'Space Mono'", letterSpacing: 2, marginBottom: 4 }}>
              PROFILE
            </div>
            <div style={{ color: "#fff", fontSize: 20, fontWeight: 700 }}>
              {loggedIn ? "Gergely K." : "Guest"}
            </div>
            {loggedIn && (
              <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, marginTop: 2 }}>
                ✅ Syncing across devices
              </div>
            )}
          </div>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 24,
            background: loggedIn
              ? "linear-gradient(135deg, #7ED957, #4CAF50)"
              : "rgba(255,255,255,0.1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 22,
          }}>
            {loggedIn ? "👤" : "👻"}
          </div>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "0 24px 80px" }}>
        {/* Stats card */}
        <div style={{
          marginTop: 20,
          background: "rgba(255,255,255,0.04)",
          borderRadius: 20,
          padding: "20px",
          border: "1px solid rgba(255,255,255,0.08)",
          marginBottom: 20,
        }}>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, fontFamily: "'Space Mono'", letterSpacing: 2, marginBottom: 16 }}>
            THIS MONTH
          </div>

          {/* Big stat */}
          <div style={{ display: "flex", gap: 16, marginBottom: 16 }}>
            <div style={{
              flex: 1,
              background: "rgba(126,217,87,0.1)",
              borderRadius: 14,
              padding: "14px",
              border: "1px solid rgba(126,217,87,0.2)",
            }}>
              <div style={{ color: "#7ED957", fontSize: 28, fontWeight: 700, fontFamily: "'Space Mono'" }}>{recyclePct}%</div>
              <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 11, marginTop: 2 }}>Recycled correctly</div>
            </div>
            <div style={{
              flex: 1,
              background: "rgba(255,255,255,0.04)",
              borderRadius: 14,
              padding: "14px",
              border: "1px solid rgba(255,255,255,0.07)",
            }}>
              <div style={{ color: "#fff", fontSize: 28, fontWeight: 700, fontFamily: "'Space Mono'" }}>{stats.total}</div>
              <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 11, marginTop: 2 }}>Items scanned</div>
            </div>
          </div>

          {/* Progress bar */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
              <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 11 }}>Recycling rate</span>
              <span style={{ color: "#7ED957", fontSize: 11, fontFamily: "'Space Mono'" }}>{stats.recyclable}/{stats.total}</span>
            </div>
            <div style={{ height: 8, background: "rgba(255,255,255,0.08)", borderRadius: 4 }}>
              <div style={{
                height: "100%",
                width: `${recyclePct}%`,
                background: "linear-gradient(90deg, #7ED957, #4CAF50)",
                borderRadius: 4,
                transition: "width 1s ease",
              }} />
            </div>
          </div>

          {/* Per-bin breakdown */}
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, fontFamily: "'Space Mono'", letterSpacing: 2, marginBottom: 10 }}>
            BY BIN
          </div>
          {Object.entries(stats.bins).map(([bin, count]) => (
            <div key={bin} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div style={{
                width: 10,
                height: 10,
                borderRadius: 5,
                background: BIN_COLORS[bin],
                flexShrink: 0,
              }} />
              <div style={{ color: "rgba(255,255,255,0.6)", fontSize: 12, flex: 1 }}>{bin}</div>
              <div style={{ color: "#fff", fontSize: 12, fontFamily: "'Space Mono'" }}>{count}</div>
              <div style={{
                height: 4,
                width: `${(count / stats.total) * 80}px`,
                background: BIN_COLORS[bin],
                borderRadius: 2,
                opacity: 0.7,
              }} />
            </div>
          ))}
        </div>

        {/* History */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 11, fontFamily: "'Space Mono'", letterSpacing: 2, marginBottom: 12 }}>
            RECENT SCANS
          </div>
          {history.map((item, i) => (
            <div key={i} style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "12px 0",
              borderBottom: i < history.length - 1 ? "1px solid rgba(255,255,255,0.05)" : "none",
            }}>
              <div style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: item.recyclable ? "rgba(126,217,87,0.15)" : "rgba(255,80,80,0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 16,
                flexShrink: 0,
              }}>
                {item.recyclable ? "♻️" : "🚫"}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ color: "#fff", fontSize: 13, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {item.item}
                </div>
                <div style={{ color: "rgba(255,255,255,0.35)", fontSize: 11 }}>{item.date}</div>
              </div>
              <div style={{
                padding: "3px 8px",
                borderRadius: 6,
                background: `${BIN_COLORS[item.bin]}20`,
                border: `1px solid ${BIN_COLORS[item.bin]}40`,
                color: BIN_COLORS[item.bin],
                fontSize: 10,
                fontFamily: "'Space Mono'",
                whiteSpace: "nowrap",
              }}>
                {item.bin}
              </div>
            </div>
          ))}
        </div>

        {/* Sign in/out */}
        <button
          onClick={() => setLoggedIn(!loggedIn)}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: 14,
            background: loggedIn ? "rgba(255,80,80,0.1)" : "rgba(126,217,87,0.1)",
            border: `1px solid ${loggedIn ? "rgba(255,80,80,0.25)" : "rgba(126,217,87,0.25)"}`,
            color: loggedIn ? "#FF6060" : "#7ED957",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
            fontFamily: "'DM Sans', sans-serif",
          }}
        >
          {loggedIn ? "Sign Out" : "Sign In / Create Account"}
        </button>
      </div>
    </div>
  );
}
