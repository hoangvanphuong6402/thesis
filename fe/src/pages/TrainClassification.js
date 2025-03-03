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

const TrainClassification = () => {
  const [file, setFile] = useState();
  const [uploadedFile, setUploadedFile] = useState();
  const [error, setError] = useState();
  const [fraction, setFraction] = useState(0.8);
  const [numEpochs, setNumEpochs] = useState(2);
  const [learningRate, setLearningRate] = useState(0.1);
  const [loading, setLoading] = useState(false);
  const [valLoss, setValLoss] = useState();
  const [valAcc, setValAcc] = useState();
  const [filename, setFilename] = useState("abc.pth");
  const [modelOptions, setModelOptions] = useState([
    "hf_hub:timm/vit_large_patch16_224.augreg_in21k_ft_in1k",
    "hf_hub:timm/vit_base_patch16_224.augreg_in21k_ft_in1k",
    "hf_hub:timm/vit_small_patch16_224.augreg_in21k_ft_in1k",
    "VGG16",
  ]);
  const [dropdownOption1, setDropdownOption1] = useState(modelOptions[0]);
  const optimizerList = ["SGD", "Adam"];
  const [dropdownOption2, setDropdownOption2] = useState(optimizerList[0]);
  const lossFunctionList = ["Cross Entropy", "MSE"];
  const [dropdownOption3, setDropdownOption3] = useState(lossFunctionList[0]);
  const [showHelp, setShowHelp] = useState(false);

  function handleChange(event) {
    setFile(event.target.files[0]);
  }

  function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    const url = "http://localhost:8887/train_classification";
    const formData = new FormData();
    if (!file) {
      toast.error("Please select a file");
      setLoading(false);
      return;
    }
    formData.append("file", file);
    formData.append("fileName", file.name);
    formData.append("net", dropdownOption1);
    formData.append("optimizer", dropdownOption2);
    formData.append("criterior", dropdownOption3);
    formData.append("num_epochs", numEpochs);
    formData.append("learning_rate", learningRate);
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
        setValLoss(response.data.loss);
        setValAcc(response.data.accuracy);
        setLoading(false);
      })
      .catch((error) => {
        setLoading(false);
        toast.error(error.response.data.message);
        setError(error);
      });
  }

  return (
    <div className="bg-gray-50 flex justify-center relative">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-xl relative">
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
          Train Classification Model
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
              Classification Model Type
            </label>
            <Dropdown
              options={modelOptions}
              onChange={(e) => setDropdownOption1(e.value)}
              value={dropdownOption1}
              placeholder="Select a model"
              className="w-full"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                Optimizer
              </label>
              <Dropdown
                options={optimizerList}
                onChange={(e) => setDropdownOption2(e.value)}
                value={dropdownOption2}
                placeholder="Select an optimizer"
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loss Function
              </label>
              <Dropdown
                options={lossFunctionList}
                onChange={(e) => setDropdownOption3(e.value)}
                value={dropdownOption3}
                placeholder="Select an option"
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Learning rate
              </label>
              <input
                type="text"
                placeholder="0.1"
                value={learningRate}
                onChange={(e) => setLearningRate(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Model filename
              </label>
              <input
                type="text"
                placeholder="filename.pth"
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

        {valLoss && (
          <Box className="mt-6">
            <Typography variant="h6" className="text-center">
              Training Result:
            </Typography>
            <Typography className="mt-2 text-center">
              <strong>Val loss:</strong> {valLoss}
            </Typography>
            <Typography className="mt-2 text-center">
              <strong>Val accuracy:</strong> {valAcc}
            </Typography>
          </Box>
        )}
      </div>
      <div className="relative">
        <IconButton
          className="absolute left-0 mt-4 bg-gray-100 p-4 rounded shadow-lg z-30"
          onClick={() => setShowHelp(!showHelp)}
        >
          <HelpOutline />
        </IconButton>
        {showHelp && (
          <div className="absolute left-0 mt-4 bg-gray-100 p-4 rounded shadow-lg z-30">
            <Typography variant="body2">
              <pre>Structure of dataset for classification:</pre>
              <pre>label1</pre>
              <pre>├── image1.jpg</pre>
              <pre>├── image2.jpg</pre>
              <pre>└── ...</pre>
              <pre>label2</pre>
              <pre>├── image3.jpg</pre>
              <pre>├── image4.jpg</pre>
              <pre>└── ...</pre>
            </Typography>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainClassification;
