import { useNavigate } from "react-router-dom";
import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import Dropdown from "react-dropdown";
import "react-dropdown/style.css";
import { UserContext } from "../providers/UserContext";
import {
  Button,
  Typography,
  Paper,
  Box,
  CircularProgress,
} from "@mui/material";

const Predict = () => {
  const navigate = useNavigate();
  const { user } = useContext(UserContext);
  const [file, setFile] = useState();
  const [uploadedFile, setUploadedFile] = useState();
  const [error, setError] = useState();
  const [prediction, setPrediction] = useState();
  const [imageData, setImageData] = useState();
  const [advice, setAdvice] = useState();
  const [prob, setProb] = useState();
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState([
    "hf_hub:timm/vit_large_patch16_224.augreg_in21k_ft_in1k",
    "hf_hub:timm/vit_base_patch16_224.augreg_in21k_ft_in1k",
    "hf_hub:timm/vit_small_patch16_224.augreg_in21k_ft_in1k",
    "VGG16",
  ]);
  const [dropdownOption, setDropdownOption] = useState(options[0]);
    const [detectionModelOptions, setDetectionModelOptions] = useState([
      "default",
    ]);
    const [dropdownOption2, setDropdownOption2] = useState(detectionModelOptions[0]);

  useEffect(() => {
    if (!user) {
      return;
    }

    axios
      .get(`http://127.0.0.1:8887/${user._id}/models`)
      .then((res) => {
        setOptions((prevOptions) => {
          const newOptions = Array.from(
            new Set([
              ...prevOptions,
              ...res.data
                .filter((item) => item.task === "classification")
                .map((item) => item["model name"]), // Extract model names
            ])
          );
          return newOptions;
        });
      })
      .catch((e) => {
        console.log(e.message);
      });

      axios
      .get(`http://127.0.0.1:8887/${user._id}/models`)
      .then((res) => {
        setDetectionModelOptions((prevOptions) => {
          const newOptions = Array.from(
            new Set([
              ...prevOptions,
              ...res.data
                .filter((item) => item.task === "detection")
                .map((item) => item["model name"]), // Extract model names
            ])
          );
          return newOptions;
        });
      })
      .catch((e) => {
        console.log(e.message);
      });
  }, [user]);

  const navigateToTrainClassification = () => {
    navigate("/train_classification");
  };
  const navigateToTrainDetection = () => {
    navigate("/train_detection");
  };

  function handleChange(event) {
    setFile(event.target.files[0]);
  }

  function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    const url = "http://localhost:8887/predict";
    const formData = new FormData();

    if (!file) {
      toast.error("Please select a file");
      setLoading(false);
      return;
    }

    formData.append("file", file);
    formData.append("fileName", file.name);
    formData.append("net", dropdownOption);
    formData.append("detection", dropdownOption2);

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
        setPrediction(response.data.label);
        setAdvice(response.data.advice);
        setProb(response.data.probability);
        setImageData(response.data.data);
        setLoading(false);
      })
      .catch((error) => {
        setLoading(false);
        toast.error(error.response.data.message);
        setError(error);
      });
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-6">
      <Paper elevation={3} className="p-6 w-full max-w-lg">
        <Typography variant="h4" className="text-center mb-4">
          Predict Cassava Leaf Diseases
        </Typography>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="file"
            onChange={handleChange}
            className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select detection model
            </label>
            <Dropdown
              options={detectionModelOptions}
              onChange={(e) => setDropdownOption2(e.value)}
              value={dropdownOption2}
              placeholder="Select a model"
              className="w-full"
            />
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Select classification model
          </label>
          <Dropdown
            options={options}
            onChange={(e) => setDropdownOption(e.value)}
            value={dropdownOption}
            placeholder="Select a model"
            className="w-full"
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            className="w-full"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Predict"}
          </Button>
        </form>

        {uploadedFile && (
          <Box className="mt-6">
            <Typography variant="h6" className="text-center">
              Uploaded Image:
            </Typography>
            <img
              src={uploadedFile}
              alt="Uploaded content"
              className="mx-auto mt-2 max-h-64 rounded-lg shadow-md"
            />
          </Box>
        )}

        {imageData && (
          <Box className="mt-6">
            <Typography variant="h6" className="text-center">
              Prediction Result:
            </Typography>
            <img
              src={`data:image/jpeg;base64,${imageData}`}
              alt="Cassava leaves"
              className="mx-auto mt-2 max-h-64 rounded-lg shadow-md"
            />
            <Typography className="mt-2 text-center">
              <strong>Disease:</strong> {prediction}
            </Typography>
            <Typography className="mt-2 text-center">
              <strong>Probability:</strong> {prob}
            </Typography>
            <Typography className="mt-1 text-center">
              <strong>Advice:</strong> {advice}
            </Typography>
          </Box>
        )}

        {error && (
          <Typography color="error" className="mt-4 text-center">
            Error uploading file: {error.message}
          </Typography>
        )}

        <Box className="flex space-x-4 mt-6">
          <Button
            variant="contained"
            color="secondary"
            onClick={navigateToTrainClassification}
            className="flex-1"
          >
            Train Classification Model
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={navigateToTrainDetection}
            className="flex-1"
          >
            Train Detection Model
          </Button>
        </Box>
      </Paper>
    </div>
  );
};

export default Predict;
