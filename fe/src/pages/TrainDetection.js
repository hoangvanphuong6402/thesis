import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import Dropdown from "react-dropdown";
import "react-dropdown/style.css";
import {
  Button,
  Typography,
  Box,
  CircularProgress,
  IconButton,
} from "@mui/material";
import { HelpOutline } from "@mui/icons-material";

const TrainDetection = () => {
  const [file, setFile] = useState();
  const [uploadedFile, setUploadedFile] = useState();
  const [error, setError] = useState();
  const [message, setMessage] = useState();
  const [fraction, setFraction] = useState(0.8);
  const [numEpochs, setNumEpochs] = useState(2);
  const [batchSize, setBatchSize] = useState(16);
  const [imageSize, setImageSize] = useState(224);
  const [loading, setLoading] = useState(false);
  const [precision, setPrecision] = useState();
  const [recall, setRecall] = useState();
  const [map, setMAP] = useState();
  const [showHelp, setShowHelp] = useState(false);
  const [filename, setFilename] = useState("abc.pt");
  const [modelOptions, setModelOptions] = useState([
    "yolo11n.pt",
    "yolo11s.pt",
    "yolo11m.pt",
    "yolo11l.pt",
    "yolo11x.pt",
  ]);
  const [dropdownOption1, setDropdownOption1] = useState(modelOptions[0]);

  function handleChange(event) {
    setFile(event.target.files[0]);
  }

  function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    const url = "http://localhost:8887/train_detection";
    const formData = new FormData();
    if (!file) {
      toast.error("Please select a file");
      setLoading(false);
      return;
    }
    formData.append("file", file);
    formData.append("fileName", file.name);
    formData.append("model", dropdownOption1);
    formData.append("num_epochs", numEpochs);
    formData.append("batch_size", batchSize);
    formData.append("image_size", imageSize);
    formData.append("fraction", fraction);
    formData.append("filename", filename);
    const token = localStorage.getItem("token");
    const config = {
      headers: {
        "content-type": "multipart/form-data",
        Authorization: `${token}`,
      },
    };
    axios
      .post(url, formData, config)
      .then((response) => {
        setUploadedFile(response.data.file);
        setPrecision(response.data.precision);
        setRecall(response.data.recall);
        setMAP(response.data.mAP);
        setLoading(false);
      })
      .catch((error, response) => {
        setLoading(false);
        toast.error(error.response.data.message);
      });
  }

  return (
    <>
      <div className="bg-gray-50 flex justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-xl">
          <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
            Train Detection Model
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Upload Dataset
              </label>
              <input
                type="file"
                onChange={handleChange}
                className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fraction of Dataset
              </label>
              <input
                type="text"
                placeholder="0.8"
                value={fraction}
                onChange={(e) => setFraction(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of epochs
              </label>
              <input
                type="text"
                placeholder="2"
                value={numEpochs}
                onChange={(e) => setNumEpochs(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Batch size
              </label>
              <input
                type="text"
                placeholder="16"
                value={batchSize}
                onChange={(e) => setBatchSize(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Image size
              </label>
              <input
                type="text"
                placeholder="224"
                value={imageSize}
                onChange={(e) => setImageSize(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model Type
                </label>
                <Dropdown
                  options={modelOptions}
                  onChange={(e) => setDropdownOption1(e.value)}
                  value={dropdownOption1}
                  placeholder="Select a model"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model filename
                </label>
                <input
                  type="text"
                  placeholder="2"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="contained"
              color="primary"
              className="w-full"
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : "Train"}
            </Button>
          </form>

          {precision && (
            <Box className="mt-6">
              <Typography variant="h6" className="text-center">
                Training Result:
              </Typography>
              <Typography className="mt-2 text-center">
                <strong>Precision:</strong> {precision}
              </Typography>
              <Typography className="mt-2 text-center">
                <strong>Recall:</strong> {recall}
              </Typography>
              <Typography className="mt-2 text-center">
                <strong>mAP:</strong> {map}
              </Typography>
            </Box>
          )}
        </div>
        <div className="relative">
          {/* Added relative class for positioning the icon */}
          <IconButton
            className="absolute left-0 mt-4 bg-gray-100 p-4 rounded shadow-lg z-30" // Positioned top-left with z-index for visibility
            onClick={() => setShowHelp(!showHelp)}
          >
            <HelpOutline />
          </IconButton>
          {showHelp && (
            <div className="absolute left-0 mt-4 bg-gray-100 p-4 rounded shadow-lg z-30">
              <img
                src="https://github.com/ultralytics/docs/releases/download/0/two-persons-tie.avif"
                alt="Dataset Structure Example"
                className="mb-4 w-full"
                style={{ height: "200px", width: "auto" }}
              />
              <img
                src="https://github.com/ultralytics/docs/releases/download/0/two-persons-tie-1.avif"
                alt="Dataset Structure Example"
                className="mb-4 w-full"
                style={{ height: "200px", width: "auto" }}
              />
              <Typography variant="body2">
                <pre>Structure of dataset for detection:</pre>
                <pre>train</pre>
                <pre>├── images</pre>
                <pre>├──── image1.jpg</pre>
                <pre>├──── image2.jpg</pre>
                <pre>└──── ...</pre>
                <pre>├── labels</pre>
                <pre>├──── image1.txt</pre>
                <pre>├──── image2.txt</pre>
                <pre>└──── ...</pre>
                <pre>val</pre>
                <pre>├── images</pre>
                <pre>├──── image1.jpg</pre>
                <pre>├──── image2.jpg</pre>
                <pre>└──── ...</pre>
                <pre>├── labels</pre>
                <pre>├──── image1.txt</pre>
                <pre>├──── image2.txt</pre>
                <pre>└──── ...</pre>
                <pre>test</pre>
                <pre>├── images</pre>
                <pre>├──── image1.jpg</pre>
                <pre>├──── image2.jpg</pre>
                <pre>└──── ...</pre>
                <pre>├── labels</pre>
                <pre>├──── image1.txt</pre>
                <pre>├──── image2.txt</pre>
                <pre>└──── ...</pre>
              </Typography>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default TrainDetection;
