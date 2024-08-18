import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Stage, Layer, Line } from "react-konva";
import { FaPencilAlt } from "react-icons/fa";

const DrawingApp = () => {
  const [lines, setLines] = useState([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [inputImageUrl, setInputImageUrl] = useState("");
  const [outputImageUrl, setOutputImageUrl] = useState("");
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const lastPosRef = useRef(null);
  const fileInputRef = useRef(null);

  const DRAWING_WIDTH = 800;
  const DRAWING_HEIGHT = 550;

  const handleMouseDown = (e) => {
    if (isLoading) return;
    const pos = e.target.getStage().getPointerPosition();
    lastPosRef.current = pos;
    setIsDrawing(true);
    setLines([
      ...lines,
      { points: [{ x: pos.x, y: pos.y }] },
    ]);
  };

  const handleMouseMove = (e) => {
    if (!isDrawing || isLoading) return;

    const stage = e.target.getStage();
    const pos = stage.getPointerPosition();
    // const lastPos = lastPosRef.current;

    const newLines = [...lines];
    const lastLine = newLines[newLines.length - 1];
    lastLine.points = [...lastLine.points, { x: pos.x, y: pos.y }];
    newLines[newLines.length - 1] = lastLine;
    setLines(newLines);

    lastPosRef.current = pos;
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
  };

  const generateCSVData = () => {
    let csvContent = "";

    lines.forEach((line, polylineIndex) => {
      line.points.forEach((point) => {
        csvContent += `${polylineIndex},0,${point.x},${point.y}\n`;
      });
    });

    return csvContent;
  };

  const downloadResults = async () => {
    setIsLoading(true);
    setRefreshTrigger(prev => prev + 1);
    const csvData = generateCSVData();
    const blob = new Blob([csvData], { type: "text/csv" });
    const formData = new FormData();
    formData.append("file", blob, "polylines.csv");

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/upload-csv`,
        formData,
        {
          responseType: "blob",
        }
      );

      const zipBlob = new Blob([response.data], { type: "application/zip" });
      const url = window.URL.createObjectURL(zipBlob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "results.zip";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);

      
    } catch (error) {
      console.error("Error during file download:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const processCSV = async (file) => {
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/upload-csv`,
        formData,
        {
          responseType: "blob",
        }
      );

      const zipBlob = new Blob([response.data], { type: "application/zip" });
      const url = window.URL.createObjectURL(zipBlob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "results.zip";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);

      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
      console.error("Error during file download:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProcessCSVClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      processCSV(file);
    }
  };

  useEffect(() => {
    setInputImageUrl(`https://firebasestorage.googleapis.com/v0/b/adobe-gensolve.appspot.com/o/images%2Finput_image.png?alt=media&refresh=${refreshTrigger}`);
    setOutputImageUrl(`https://firebasestorage.googleapis.com/v0/b/adobe-gensolve.appspot.com/o/images%2Foutput_image.png?alt=media&refresh=${refreshTrigger}`);
  }, [refreshTrigger]);


  return (
    <div>
      <div
        style={{
          position: "fixed",
          top: "20px",
          left: "50%",
          transform: "translateX(-50%)",
          color: "#007bff",
          fontSize: "24px",
          zIndex: 999,
          display: "flex",
          alignItems: "center",
          padding: "10px 20px",
          backgroundColor: "white",
          borderRadius: "8px",
          border: "2px solid #007bff",
        }}
      >
        <FaPencilAlt style={{ marginRight: "10px" }} />
        Adobe-Gensolve
      </div>
      <div
  style={{
    border: "10px solid #fff",
    backgroundColor: "#494848",
    marginTop: "80px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
    position: "relative",
    padding: "10px",
    display: "flex",
    flexDirection: "row",
    alignItems: "flex-start",
    gap: "20px",
    overflowX: "auto",
    paddingBottom: "20px",
    // background: rgb(57, 53, 0),
    backgroundSize: "40px 40px"
  }}
>
  <Stage
    width={DRAWING_WIDTH}
    height={DRAWING_HEIGHT}
    onMouseDown={handleMouseDown}
    onMouseMove={handleMouseMove}
    onMouseUp={handleMouseUp}
    style={{
      backgroundColor: "transparent",
      borderRadius: "8px",
      boxShadow: "inset 0 0 10px rgba(0, 0, 0, 0.5)",
      flexShrink: 0
    }}
  >
    <Layer>
      {lines.map((line, i) => (
        <Line
          key={i}
          points={line.points.flatMap((p) => [p.x, p.y])}
          stroke="yellow"
          strokeWidth={2}
          tension={0.5}
          lineCap="round"
          globalCompositeOperation="source-over"
        />
      ))}
    </Layer>
  </Stage>
  
  {inputImageUrl && (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <p style={{ color: "white",fontWeight : "bold" , marginBottom: "10px" }}>Input Image</p>
      <img
        src={inputImageUrl}
        alt="Input"
        style={{
          marginTop: "0px",
          width: "325px",
          height: "370px",
          borderRadius: "8px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
          transition: "opacity 0.3s ease",
          opacity: inputImageUrl ? 1 : 0,
        }}
      />
    </div>
  )}

  {outputImageUrl && (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <p style={{ color: "white",fontWeight : "bold", marginBottom: "10px" }}>Output Image</p>
      <img
        src={outputImageUrl}
        alt="Output"
        style={{
          marginTop: "0px",
          width: "325px",
          height: "370px",
          borderRadius: "8px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
          transition: "opacity 0.3s ease",
          opacity: outputImageUrl ? 1 : 0,
        }}
      />
    </div>
  )}
</div>

      
      <div style={{display:"flex", marginTop: "20px", justifyContent: "center", gap: "20px"}}>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        <button
          onClick={handleProcessCSVClick}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            color: "#fff",
            backgroundColor: "#007bff",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
            transition: "background-color 0.3s ease",
          }}
        >
          Process CSV
        </button>
        <button
          onClick={downloadResults}
          disabled={isLoading}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            color: "#fff",
            backgroundColor: isLoading ? "#ccc" : "#28a745",
            border: "none",
            borderRadius: "8px",
            cursor: isLoading ? "not-allowed" : "pointer",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
            transition: "background-color 0.3s ease",
          }}
        >
          {isLoading ? "Processing..." : "Download Results"}
        </button>
        
      </div>
    </div>
  );
};

export default DrawingApp;
