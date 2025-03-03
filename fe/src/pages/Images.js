
import axios from 'axios';
import { useEffect, useContext, useState } from 'react';
import { UserContext } from '../providers/UserContext';

const Images = () => {
  const { user } = useContext(UserContext);
  const [listImages, setListImages] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [imageToDelete, setImageToDelete] = useState(null); // Store imageId of the image to delete

  useEffect(() => {
    if (!user) {
      return;
    }

    axios
      .get(`http://127.0.0.1:8887/${user._id}/images`)
      .then((res) => {
        console.log(res.data);
        setListImages(res.data);
      })
      .catch((e) => {
        console.log(e.message);
      });
  }, [user]);

  const handleDeleteImage = (imageId) => {
    setShowModal(true); // Show the confirmation modal
    setImageToDelete(imageId); // Set the imageId to be deleted
  };

  const confirmDelete = () => {
    axios
      .delete(`http://127.0.0.1:8887/${imageToDelete}`)
      .then((res) => {
        console.log('Image deleted successfully');
        setListImages(listImages.filter((image) => image._id !== imageToDelete)); // Remove the image from the list
        setShowModal(false); // Close the modal after deletion
      })
      .catch((e) => {
        console.log(e.message);
        setShowModal(false); // Close the modal if there's an error
      });
  };

  const cancelDelete = () => {
    setShowModal(false); // Close the modal without deleting the image
  };

  return (
    <div className="flex justify-center">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {listImages.map((image, index) => (
          <div
            key={index}
            className="relative flex flex-col items-center bg-white p-4 rounded-lg shadow-md hover:shadow-lg"
          >
            <button
              onClick={() => handleDeleteImage(image._id)}
              className="absolute top-2 right-2 text-red-500 hover:text-red-700"
            >
              x
            </button>
            <img
              src={`data:image/jpeg;base64,${image.data}`}
              alt="cassava"
              className="h-40 w-full object-cover rounded-md"
            />
            <p className="mt-2 text-sm font-semibold text-gray-700">{image.label}</p>
          </div>
        ))}
      </div>

      {/* Modal for delete confirmation */}
      {showModal && (
        <div className="fixed inset-0 flex justify-center items-center bg-gray-500 bg-opacity-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-fit">
            <h3 className="text-lg font-semibold mb-4">Are you sure you want to delete this image?</h3>
            <div className="flex justify-center space-x-2"> {/* Reduced space between buttons */}
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-700"
              >
                Yes
              </button>
              <button
                onClick={cancelDelete}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-700"
              >
                No
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Images;
