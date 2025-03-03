import {createContext, useEffect, useState} from "react";
import axios from "axios";
import { getItemFromLocalStorage, removeItemFromLocalStorage } from '../utils';

export const UserContext = createContext({});

export function UserProvider({children}) {
  const [user,setUser] = useState(null);
  useEffect(() => {
    if (!user) {
      const token = getItemFromLocalStorage('token');
      console.log(token);
      
      if (token) {
        axios
          .get('http://127.0.0.1:8887/user', {
            headers: {
                'content-type': 'multipart/form-data',
                'Authorization': `${token}`
                },
          })
          .then(({ data }) => {
            setUser(data);
          })
          .catch((error) => {
            if(error.response.data.error.name === "TokenExpiredError") {
              removeItemFromLocalStorage('token');
            } else {
              console.log(error);
            };
          });
      }
    }
  }, [user]);

  return (
    <UserContext.Provider value={{user,setUser}}>
      {children}
    </UserContext.Provider>
  );
}