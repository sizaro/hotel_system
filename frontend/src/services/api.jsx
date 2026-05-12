import { createContext, useState } from "react";
import api from "../services/api";

export const DataContext = createContext();

export function DataProvider({ children }) {

  // =========================
  // STATES
  // =========================

  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(false);

  // =========================
  // GET ALL ROOMS
  // =========================

  const getRooms = async () => {

    try {

      setLoading(true);

      const response = await api.get("/api/rooms/");

      setRooms(response.data);

    } catch (error) {

      console.log(error);

    } finally {

      setLoading(false);

    }
  };

  // =========================
  // CREATE ROOM
  // =========================

  const createRoom = async (roomData) => {

    try {

      const response = await api.post(
        "/api/rooms/",
        roomData
      );

      await getRooms();

      return response.data;

    } catch (error) {

      console.log(error);

    }
  };

  // =========================
  // UPDATE ROOM
  // =========================

  const updateRoom = async (id, roomData) => {

    try {

      const response = await api.put(
        `/api/rooms/${id}/`,
        roomData
      );

      await getRooms();

      return response.data;

    } catch (error) {

      console.log(error);

    }
  };

  // =========================
  // DELETE ROOM
  // =========================

  const deleteRoom = async (id) => {

    try {

      await api.delete(`/api/rooms/${id}/`);

      await getRooms();

    } catch (error) {

      console.log(error);

    }
  };

  return (

    <DataContext.Provider
      value={{

        // STATES
        rooms,
        loading,

        // FUNCTIONS
        getRooms,
        createRoom,
        updateRoom,
        deleteRoom,

      }}
    >

      {children}

    </DataContext.Provider>

  );
}