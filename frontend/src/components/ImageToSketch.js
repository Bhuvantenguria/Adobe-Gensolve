import React, { useState, useRef } from 'react';
import { Stage, Layer, Image, Line } from 'react-konva';
import axios from 'axios';
import { FiUpload, FiDownload, FiShare2, FiSettings, FiRotateCw, FiZoomIn, FiZoomOut } from 'react-icons/fi';
import toast from 'react-hot-toast';

const ImageToSketch = () => {
    const [originalImage, setOriginalImage] = useState(null);
    const [sketchImage, setSketchImage] = useState(null);
    const [outlineImage, setOutlineImage] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [drawingMode, setDrawingMode] = useState('draw');
    const [brushSize, setBrushSize] = useState(5);
    const [brushColor, setBrushColor] = useState('#000000');
    const [lines, setLines] = useState([]);
    const [svgPaths, setSvgPaths] = useState([]);
    const [sketchStyle, setSketchStyle] = useState('pencil');
    const [zoom, setZoom] = useState(1);
    
    const stageRef = useRef();
    const isDrawing = useRef(false);
    const fileInputRef = useRef();

    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsProcessing(true);
        toast.loading('Processing image...');
        
        const formData = new FormData();
        formData.append('image', file);
        formData.append('style', sketchStyle);

        try {
            const response = await axios.post('/api/v1/upload-image', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                setOriginalImage(response.data.files.original_image.url);
                setSketchImage(response.data.files.sketch_image.url);
                setOutlineImage(response.data.files.outline_image.url);
                toast.success('Image processed successfully!');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            toast.error('Image upload failed. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleMouseDown = (e) => {
        isDrawing.current = true;
        const pos = e.target.getStage().getPointerPosition();
        setLines([...lines, { points: [pos.x, pos.y], mode: drawingMode, color: brushColor, size: brushSize }]);
    };

    const handleMouseMove = (e) => {
        if (!isDrawing.current) return;

        const stage = e.target.getStage();
        const point = stage.getPointerPosition();
        let lastLine = lines[lines.length - 1];
        lastLine.points = lastLine.points.concat([point.x, point.y]);
        
        lines.splice(lines.length - 1, 1, lastLine);
        setLines([...lines]);
    };

    const handleMouseUp = () => {
        isDrawing.current = false;
    };

    const clearCanvas = () => {
        setLines([]);
        toast.success('Canvas cleared!');
    };

    const undoLastLine = () => {
        setLines(lines.slice(0, -1));
        toast.success('Undone!');
    };

    const saveSketch = async () => {
        try {
            const stage = stageRef.current;
            const dataURL = stage.toDataURL();
            
            const response = await axios.post('/api/v1/drawing/save', {
                drawingData: dataURL,
                title: 'Sketch from Image',
                description: 'Generated sketch with edits',
                userId: 'user123'
            });

            if (response.data.success) {
                const link = document.createElement('a');
                link.href = response.data.file_url;
                link.download = 'sketch.png';
                link.click();
                toast.success('Sketch saved successfully!');
            }
        } catch (error) {
            console.error('Save failed:', error);
            toast.error('Failed to save sketch. Please try again.');
        }
    };

    const shareSketch = async () => {
        try {
            const stage = stageRef.current;
            const dataURL = stage.toDataURL();
            
            if (navigator.share) {
                await navigator.share({
                    title: 'My Sketch',
                    text: 'Check out my sketch!',
                    url: dataURL
                });
            } else {
                navigator.clipboard.writeText(dataURL);
                toast.success('Sketch URL copied to clipboard!');
            }
        } catch (error) {
            console.error('Share failed:', error);
            toast.error('Share failed. Please try again.');
        }
    };

    const handleZoomIn = () => {
        setZoom(prev => Math.min(prev + 0.1, 3));
    };

    const handleZoomOut = () => {
        setZoom(prev => Math.max(prev - 0.1, 0.1));
    };

    const resetZoom = () => {
        setZoom(1);
    };

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Image to Sketch Converter
                    </h1>
                    <p className="text-lg text-gray-600">
                        Upload an image and convert it to a sketch, then edit it with our drawing tools
                    </p>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <div className="flex flex-wrap gap-4 items-center justify-center mb-6">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            disabled={isProcessing}
                            className="hidden"
                        />
                        <button
                            onClick={() => fileInputRef.current.click()}
                            disabled={isProcessing}
                            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            <FiUpload />
                            {isProcessing ? 'Processing...' : 'Upload Image'}
                        </button>

                        <select
                            value={sketchStyle}
                            onChange={(e) => setSketchStyle(e.target.value)}
                            className="px-4 py-2 border border-gray-300 rounded-lg"
                        >
                            <option value="pencil">Pencil Sketch</option>
                            <option value="pen">Pen Sketch</option>
                            <option value="charcoal">Charcoal Sketch</option>
                        </select>
                    </div>

                    {isProcessing && (
                        <div className="text-center py-4">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                            <p className="mt-2 text-gray-600">Processing your image...</p>
                        </div>
                    )}
                </div>

                {sketchImage && (
                    <div className="bg-white rounded-lg shadow-lg p-6">
                        <div className="flex flex-wrap gap-4 items-center justify-between mb-6">
                            <div className="flex flex-wrap gap-2">
                                <button
                                    onClick={() => setDrawingMode('draw')}
                                    className={`px-4 py-2 rounded-lg ${
                                        drawingMode === 'draw' 
                                            ? 'bg-blue-600 text-white' 
                                            : 'bg-gray-200 text-gray-700'
                                    }`}
                                >
                                    Draw
                                </button>
                                <button
                                    onClick={() => setDrawingMode('erase')}
                                    className={`px-4 py-2 rounded-lg ${
                                        drawingMode === 'erase' 
                                            ? 'bg-red-600 text-white' 
                                            : 'bg-gray-200 text-gray-700'
                                    }`}
                                >
                                    Erase
                                </button>
                            </div>

                            <div className="flex items-center gap-4">
                                <input
                                    type="color"
                                    value={brushColor}
                                    onChange={(e) => setBrushColor(e.target.value)}
                                    className="w-10 h-10 border border-gray-300 rounded-lg cursor-pointer"
                                />
                                <input
                                    type="range"
                                    min="1"
                                    max="20"
                                    value={brushSize}
                                    onChange={(e) => setBrushSize(parseInt(e.target.value))}
                                    className="w-24"
                                />
                                <span className="text-sm text-gray-600">{brushSize}px</span>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={handleZoomOut}
                                    className="p-2 bg-gray-200 rounded-lg hover:bg-gray-300"
                                >
                                    <FiZoomOut />
                                </button>
                                <button
                                    onClick={resetZoom}
                                    className="px-3 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 text-sm"
                                >
                                    {Math.round(zoom * 100)}%
                                </button>
                                <button
                                    onClick={handleZoomIn}
                                    className="p-2 bg-gray-200 rounded-lg hover:bg-gray-300"
                                >
                                    <FiZoomIn />
                                </button>
                            </div>
                        </div>

                        <div className="flex flex-wrap gap-4 mb-6">
                            <button
                                onClick={undoLastLine}
                                disabled={lines.length === 0}
                                className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
                            >
                                <FiRotateCw />
                                Undo
                            </button>
                            <button
                                onClick={clearCanvas}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                            >
                                Clear
                            </button>
                            <button
                                onClick={saveSketch}
                                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                            >
                                <FiDownload />
                                Save
                            </button>
                            <button
                                onClick={shareSketch}
                                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                            >
                                <FiShare2 />
                                Share
                            </button>
                        </div>

                        <div className="border border-gray-300 rounded-lg overflow-hidden">
                            <Stage
                                ref={stageRef}
                                width={800}
                                height={600}
                                onMouseDown={handleMouseDown}
                                onMousemove={handleMouseMove}
                                onMouseup={handleMouseUp}
                                scaleX={zoom}
                                scaleY={zoom}
                            >
                                <Layer>
                                    {/* Background sketch image */}
                                    {sketchImage && (
                                        <Image
                                            image={new window.Image()}
                                            src={sketchImage}
                                            opacity={0.3}
                                        />
                                    )}
                                    
                                    {/* User drawings */}
                                    {lines.map((line, i) => (
                                        <Line
                                            key={i}
                                            points={line.points}
                                            stroke={line.color}
                                            strokeWidth={line.size}
                                            tension={0.5}
                                            lineCap="round"
                                            lineJoin="round"
                                            globalCompositeOperation={
                                                line.mode === 'erase' ? 'destination-out' : 'source-over'
                                            }
                                        />
                                    ))}
                                </Layer>
                            </Stage>
                        </div>

                        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                            {originalImage && (
                                <div className="text-center">
                                    <h3 className="font-semibold mb-2">Original Image</h3>
                                    <img 
                                        src={originalImage} 
                                        alt="Original" 
                                        className="w-full h-32 object-cover rounded-lg border"
                                    />
                                </div>
                            )}
                            {sketchImage && (
                                <div className="text-center">
                                    <h3 className="font-semibold mb-2">Sketch</h3>
                                    <img 
                                        src={sketchImage} 
                                        alt="Sketch" 
                                        className="w-full h-32 object-cover rounded-lg border"
                                    />
                                </div>
                            )}
                            {outlineImage && (
                                <div className="text-center">
                                    <h3 className="font-semibold mb-2">Outlines</h3>
                                    <img 
                                        src={outlineImage} 
                                        alt="Outlines" 
                                        className="w-full h-32 object-cover rounded-lg border"
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ImageToSketch; 